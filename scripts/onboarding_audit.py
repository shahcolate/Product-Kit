#!/usr/bin/env python3
from __future__ import annotations

"""
ProductKit Onboarding Flow Auditor
Navigates a signup/onboarding flow via headless browser, captures each screen,
and produces a structured UX audit with friction scoring and recommendations.

Usage:
  python scripts/onboarding_audit.py "https://app.example.com/signup" --product "Example App"
  python scripts/onboarding_audit.py "https://linear.app/signup" --max-steps 15 --output markdown --save

Requires: ANTHROPIC_API_KEY env var, pip install anthropic playwright
          One-time setup: python -m playwright install chromium
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    add_common_args,
    async_text_call,
    async_vision_call,
    box_header,
    dated_slug,
    footer_line,
    make_async_client,
    repo_root,
    require_api_key,
    save_output,
    section_rule,
    slugify,
)

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("ERROR: playwright is required. Install with: pip install playwright && python -m playwright install chromium", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Flow navigation
# ---------------------------------------------------------------------------

DETECT_CTA_PROMPT = """You are a UX analyst examining a screenshot of a web application's onboarding/signup flow.

PRODUCT: {product}
CATEGORY: {category}
STEP: {step_num} of max {max_steps}
CURRENT URL: {url}

Identify the primary call-to-action (CTA) on this screen — the button, link, or input field that advances the user through the onboarding flow.

Return ONLY valid JSON (no markdown fences):
{{
  "cta_type": "button" | "link" | "input" | "none",
  "cta_text": "the visible text on the CTA",
  "cta_selector": "a CSS selector to find this element",
  "input_value": "if cta_type is input, what to type (use realistic test data)",
  "is_end_of_flow": true/false,
  "reasoning": "why this is the primary CTA"
}}

If the page appears to be the end of the onboarding flow (dashboard, success screen, etc.), set is_end_of_flow to true.
If there's no clear CTA or the page is an error, set cta_type to "none"."""

SCREEN_AUDIT_PROMPT = """You are a UX expert auditing a single screen in an onboarding flow.

PRODUCT: {product}
CATEGORY: {category}
STEP: {step_num}
URL: {url}

Score this screen on each dimension (1 = poor, 5 = excellent):

1. **Clarity** (1-5): Is the purpose of this screen immediately obvious?
2. **Cognitive load** (1-5): How much mental effort does this screen require? (5 = minimal effort)
3. **Friction** (1-5): How easy is it to complete the action? (5 = effortless)
4. **Progress indication**: Is there a progress bar or step indicator? (yes/no)
5. **Social proof**: Any trust signals, testimonials, or logos? (yes/no)
6. **CTA clarity**: Is the primary action obvious and compelling? (yes/no)

Then provide:
- **What works well**: 1-2 specific positives
- **Friction points**: 1-2 specific issues that could cause drop-off
- **Recommendation**: One specific, actionable improvement

Be concise and specific. Reference actual UI elements you can see."""

SYNTHESIS_PROMPT = """You are a senior UX strategist delivering a comprehensive onboarding audit.

PRODUCT: {product}
CATEGORY: {category}
TOTAL STEPS: {total_steps}

PER-SCREEN AUDITS:
{screen_audits}

Deliver the full-flow synthesis:

1. **Time-to-value assessment**: How many steps before the user experiences core value? Is this acceptable for a {category} product?

2. **Highest drop-off risk screen**: Which screen is most likely to cause abandonment and why?

3. **Flow friction map**: Rate overall friction as Low / Medium / High with evidence

4. **Top 3 recommendations**: Specific, actionable changes ranked by impact. For each:
   - What to change
   - Why it matters (reference specific screen)
   - Expected impact

5. **Overall grade**: A through F, with one-sentence justification
   - A: Best-in-class onboarding
   - B: Solid with minor friction
   - C: Functional but significant friction
   - D: Multiple serious friction points
   - F: Likely to lose most users

6. **Benchmark comparison**: How does this compare to best-in-class onboarding in {category}?

Be opinionated. Name specific screens and specific problems. Don't hedge."""


async def navigate_and_capture(
    url: str, product: str, category: str, max_steps: int, viewport: str,
    client, model: str,
) -> list[dict]:
    """Navigate through onboarding flow, capturing screenshots at each step."""
    width, height = (int(x) for x in viewport.split("x"))
    slug = slugify(product)
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = repo_root() / "onboarding-audits" / f"{slug}-{date_str}"
    output_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)

    steps = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={"width": width, "height": height})
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"  ERROR: Could not load {url}: {e}", file=sys.stderr)
            await browser.close()
            return steps

        for step_num in range(1, max_steps + 1):
            current_url = page.url
            print(f"  Step {step_num}: {current_url}")

            # Capture screenshot
            screenshot_path = screenshots_dir / f"step-{step_num:02d}.png"
            await page.screenshot(path=str(screenshot_path), full_page=False)

            steps.append({
                "step_num": step_num,
                "url": current_url,
                "screenshot": screenshot_path,
            })

            # Ask Claude to detect CTA
            detect_prompt = DETECT_CTA_PROMPT.format(
                product=product, category=category,
                step_num=step_num, max_steps=max_steps, url=current_url,
            )
            cta_response = await async_vision_call(
                client, model,
                "You are a UX analyst.",
                detect_prompt,
                [screenshot_path],
                max_tokens=512,
            )

            # Parse CTA response
            try:
                # Strip markdown fences if present
                cleaned = cta_response.strip()
                if cleaned.startswith("```"):
                    lines = cleaned.split("\n")
                    cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
                cta = json.loads(cleaned.strip())
            except json.JSONDecodeError:
                print(f"    Could not parse CTA response, stopping flow")
                break

            if cta.get("is_end_of_flow"):
                print(f"    End of flow detected")
                break

            if cta.get("cta_type") == "none":
                print(f"    No CTA detected, stopping flow")
                break

            # Execute the action
            try:
                selector = cta.get("cta_selector", "")
                if cta["cta_type"] == "input":
                    await page.fill(selector, cta.get("input_value", "test@example.com"))
                    print(f"    Typed into: {selector}")
                    # Look for a submit button after filling input
                    await page.wait_for_timeout(500)
                elif cta["cta_type"] in ("button", "link"):
                    await page.click(selector, timeout=5000)
                    print(f"    Clicked: {cta.get('cta_text', selector)}")

                # Wait for navigation/network
                await page.wait_for_timeout(2000)
                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    pass  # Page may not have navigated

            except Exception as e:
                print(f"    Action failed: {e}")
                # Try one more time with a broader selector
                try:
                    fallback_text = cta.get("cta_text", "")
                    if fallback_text:
                        await page.get_by_text(fallback_text, exact=False).first.click(timeout=5000)
                        print(f"    Fallback click on text: {fallback_text}")
                        await page.wait_for_timeout(2000)
                except Exception:
                    print(f"    Fallback also failed, stopping flow")
                    break

        await browser.close()

    return steps


# ---------------------------------------------------------------------------
# AI audit pipeline
# ---------------------------------------------------------------------------

async def audit_screens(
    client, model: str, product: str, category: str, steps: list[dict],
) -> tuple[list[str], str]:
    """Audit each screen and produce synthesis."""
    # Per-screen audits (parallel)
    print(f"\nAuditing {len(steps)} screens...")

    async def _audit_one(step):
        prompt = SCREEN_AUDIT_PROMPT.format(
            product=product, category=category,
            step_num=step["step_num"], url=step["url"],
        )
        print(f"  Auditing step {step['step_num']}...", end=" ", flush=True)
        result = await async_vision_call(
            client, model,
            "You are a UX expert.",
            prompt,
            [step["screenshot"]],
        )
        print("done")
        return result

    screen_audits = await asyncio.gather(*[_audit_one(s) for s in steps])

    # Full-flow synthesis
    print(f"\nGenerating flow synthesis...", end=" ", flush=True)
    audits_block = "\n\n---\n\n".join(
        f"**Step {steps[i]['step_num']}** ({steps[i]['url']}):\n{audit}"
        for i, audit in enumerate(screen_audits)
    )
    synthesis = await async_text_call(
        client, model,
        "You are a senior UX strategist.",
        SYNTHESIS_PROMPT.format(
            product=product, category=category,
            total_steps=len(steps), screen_audits=audits_block,
        ),
    )
    print("done")

    return list(screen_audits), synthesis


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_terminal(
    product: str, model: str, steps: list[dict],
    screen_audits: list[str], synthesis: str,
) -> str:
    """Format audit results for terminal display."""
    lines = []
    lines.append(box_header(
        f"ONBOARDING AUDIT: {product}",
        f"Steps: {len(steps)} | Model: {model}",
    ))
    lines.append("")

    for i, (step, audit) in enumerate(zip(steps, screen_audits)):
        lines.append(section_rule(f"Step {step['step_num']}: {step['url']}"))
        lines.append("")
        lines.append(audit.strip())
        lines.append("")

    lines.append(section_rule("FULL-FLOW SYNTHESIS"))
    lines.append("")
    lines.append(synthesis.strip())
    lines.append("")
    lines.append(footer_line())
    lines.append("Generated by ProductKit · github.com/shahcolate/Product-Kit")
    lines.append("")
    return "\n".join(lines)


def format_markdown(
    product: str, model: str, steps: list[dict],
    screen_audits: list[str], synthesis: str,
) -> str:
    """Format audit results as Markdown."""
    now = datetime.now().strftime("%B %d, %Y")
    lines = []
    lines.append(f"# Onboarding Audit: {product}")
    lines.append(f"*{len(steps)} steps | Model: {model} | {now}*")
    lines.append("")

    for i, (step, audit) in enumerate(zip(steps, screen_audits)):
        lines.append(f"## Step {step['step_num']}")
        lines.append(f"URL: {step['url']}")
        lines.append(f"![Step {step['step_num']}](screenshots/step-{step['step_num']:02d}.png)")
        lines.append("")
        lines.append(audit.strip())
        lines.append("")

    lines.append("## Full-Flow Synthesis")
    lines.append("")
    lines.append(synthesis.strip())
    lines.append("")
    lines.append("---")
    lines.append("*Generated by [ProductKit](https://github.com/shahcolate/Product-Kit)*")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Onboarding Flow Auditor — automated UX audit of signup/onboarding flows"
    )
    parser.add_argument("url", help="URL of the signup/onboarding page to audit")
    parser.add_argument("--product", type=str, default=None,
                        help="Product name (used in report header)")
    parser.add_argument("--category", type=str, default="B2B SaaS",
                        choices=["B2B SaaS", "consumer", "dev tool"],
                        help="Product category for benchmarking (default: B2B SaaS)")
    parser.add_argument("--max-steps", type=int, default=20,
                        help="Maximum onboarding steps to navigate (default: 20)")
    parser.add_argument("--viewport", type=str, default="1280x800",
                        help="Browser viewport size (default: 1280x800)")
    add_common_args(parser)
    args = parser.parse_args()

    require_api_key()
    product = args.product or args.url.split("//")[-1].split("/")[0].replace("www.", "")

    client = make_async_client()

    async def _run():
        # Phase 1: Navigate and capture
        print(f"\nNavigating onboarding flow: {args.url}")
        print(f"Product: {product} | Category: {args.category} | Max steps: {args.max_steps}\n")
        steps = await navigate_and_capture(
            args.url, product, args.category, args.max_steps, args.viewport,
            client, args.model,
        )

        if not steps:
            print("ERROR: No screens captured.", file=sys.stderr)
            sys.exit(1)

        # Phase 2: AI audit
        screen_audits, synthesis = await audit_screens(
            client, args.model, product, args.category, steps,
        )

        print()

        # Format output
        if args.output == "markdown":
            output = format_markdown(product, args.model, steps, screen_audits, synthesis)
        else:
            output = format_terminal(product, args.model, steps, screen_audits, synthesis)

        print(output)

        # Save if requested
        if args.save:
            slug = dated_slug(f"{product}-onboarding-audit")
            md_output = format_markdown(product, args.model, steps, screen_audits, synthesis)
            filepath = save_output(md_output, f"onboarding-audits/{slugify(product)}-{datetime.now().strftime('%Y-%m-%d')}", "audit.md")
            print(f"Saved to {filepath}")

    asyncio.run(_run())


if __name__ == "__main__":
    main()
