#!/usr/bin/env python3
from __future__ import annotations

"""
ProductKit Tutorial Creator
Takes a URL + goal, launches headless browser, AI-plans navigation steps,
captures screenshots, and generates annotated step-by-step tutorial.

Usage:
  python scripts/tutorial.py "https://app.linear.dev" --goal "Create a new project and add a task"
  python scripts/tutorial.py "https://notion.so" --steps steps.json --auth-cookie cookie.txt
  python scripts/tutorial.py "https://example.com" --goal "Find the main content" --output markdown --save

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
# Step planning
# ---------------------------------------------------------------------------

PLAN_STEPS_PROMPT = """You are a tutorial writer planning browser actions to accomplish a goal.

URL: {url}
GOAL: {goal}

Looking at this screenshot, plan the sequence of browser actions to accomplish the goal.

Return ONLY valid JSON (no markdown fences):
{{
  "steps": [
    {{
      "action": "click" | "type" | "navigate" | "scroll",
      "selector": "CSS selector for the element",
      "value": "text to type (for 'type' action) or URL (for 'navigate')",
      "description": "human-readable description of this step"
    }}
  ]
}}

Rules:
- Use specific, robust CSS selectors (prefer [data-testid], [aria-label], or role-based selectors)
- Include 'scroll' actions when content is below the fold
- Keep steps granular — one action per step
- Plan a realistic path a user would take
- Limit to {max_steps} steps maximum"""

RETRY_SELECTOR_PROMPT = """The CSS selector "{selector}" failed on this page. Looking at the current screenshot, suggest an alternative selector for the element described as: "{description}"

Return ONLY valid JSON (no markdown fences):
{{
  "selector": "new CSS selector",
  "reasoning": "why this selector should work"
}}"""

ANNOTATE_STEP_PROMPT = """You are writing a step in a product tutorial. Looking at this screenshot:

STEP NUMBER: {step_num}
ACTION TAKEN: {description}
URL: {url}

Write the tutorial annotation for this step:

Return ONLY valid JSON (no markdown fences):
{{
  "step_title": "Short, imperative title for this step (e.g., 'Click the Create button')",
  "instruction_text": "1-2 sentence instruction telling the user exactly what to do and where to find it",
  "callout_text": "Optional tip, note, or context about this step (null if not needed)"
}}"""

ASSEMBLE_TUTORIAL_PROMPT = """You are assembling a complete tutorial from annotated steps.

PRODUCT URL: {url}
GOAL: {goal}
TOTAL STEPS: {total_steps}

ANNOTATED STEPS:
{annotated_steps}

Write the tutorial wrapper:

1. **Title**: A clear, action-oriented tutorial title
2. **Introduction**: 2-3 sentences explaining what the user will accomplish and why
3. **Prerequisites**: Bullet list of what the user needs before starting (account, permissions, etc.)
4. **Summary**: 2-3 sentences recapping what was accomplished

Do NOT repeat the individual steps — just provide the wrapper content.

Return ONLY valid JSON (no markdown fences):
{{
  "title": "Tutorial title",
  "introduction": "Intro paragraph",
  "prerequisites": ["prerequisite 1", "prerequisite 2"],
  "summary": "Summary paragraph"
}}"""


async def plan_steps(client, model: str, url: str, goal: str, screenshot: Path, max_steps: int) -> list[dict]:
    """Use Claude vision to plan navigation steps from the initial screenshot."""
    prompt = PLAN_STEPS_PROMPT.format(url=url, goal=goal, max_steps=max_steps)
    response = await async_vision_call(
        client, model,
        "You are an expert tutorial writer.",
        prompt,
        [screenshot],
        max_tokens=2048,
    )

    # Parse response
    cleaned = response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        data = json.loads(cleaned.strip())
        return data["steps"]
    except (json.JSONDecodeError, KeyError):
        print(f"  WARNING: Could not parse step plan, using empty plan", file=sys.stderr)
        return []


def load_steps_file(steps_file: str) -> list[dict]:
    """Load pre-defined steps from a JSON file."""
    with open(steps_file, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    elif "steps" in data:
        return data["steps"]
    else:
        print("ERROR: Steps file must be a JSON array or contain a 'steps' key.", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Browser execution
# ---------------------------------------------------------------------------

async def execute_steps(
    url: str, steps: list[dict], viewport: str, wait_ms: int,
    output_dir: Path, client, model: str,
    auth_cookie_file: str | None = None,
) -> list[dict]:
    """Execute planned steps in the browser, capturing screenshots."""
    width, height = (int(x) for x in viewport.split("x"))
    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    captured_steps = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={"width": width, "height": height})

        # Load auth cookies if provided
        if auth_cookie_file:
            cookie_path = Path(auth_cookie_file)
            if cookie_path.exists():
                with open(cookie_path) as f:
                    cookies = json.load(f)
                if isinstance(cookies, list):
                    await context.add_cookies(cookies)
                print(f"  Loaded auth cookies from {auth_cookie_file}")

        page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"  ERROR: Could not load {url}: {e}", file=sys.stderr)
            await browser.close()
            return captured_steps

        await page.wait_for_timeout(wait_ms)

        for i, step in enumerate(steps):
            step_num = i + 1
            action = step.get("action", "click")
            selector = step.get("selector", "")
            value = step.get("value", "")
            description = step.get("description", f"Step {step_num}")

            print(f"  Step {step_num}/{len(steps)}: {description}")

            # Capture before screenshot
            screenshot_path = screenshots_dir / f"step-{step_num:02d}.png"
            await page.screenshot(path=str(screenshot_path), full_page=False)

            # Execute the action
            success = False
            try:
                if action == "click":
                    await page.click(selector, timeout=5000)
                    success = True
                elif action == "type":
                    await page.fill(selector, value)
                    success = True
                elif action == "navigate":
                    await page.goto(value, wait_until="networkidle", timeout=30000)
                    success = True
                elif action == "scroll":
                    await page.evaluate("window.scrollBy(0, 400)")
                    success = True
            except Exception as e:
                print(f"    Action failed: {e}")
                # Retry: ask Claude for alternative selector
                try:
                    retry_prompt = RETRY_SELECTOR_PROMPT.format(
                        selector=selector, description=description,
                    )
                    retry_response = await async_vision_call(
                        client, model,
                        "You are a web automation expert.",
                        retry_prompt,
                        [screenshot_path],
                        max_tokens=256,
                    )
                    cleaned = retry_response.strip()
                    if cleaned.startswith("```"):
                        lines_list = cleaned.split("\n")
                        cleaned = "\n".join(lines_list[1:-1] if lines_list[-1].strip() == "```" else lines_list[1:])
                    retry_data = json.loads(cleaned.strip())
                    new_selector = retry_data["selector"]
                    print(f"    Retrying with: {new_selector}")

                    if action == "click":
                        await page.click(new_selector, timeout=5000)
                        success = True
                    elif action == "type":
                        await page.fill(new_selector, value)
                        success = True
                except Exception as e2:
                    print(f"    Retry also failed: {e2}")

            # Wait for page to settle
            await page.wait_for_timeout(wait_ms)
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass

            captured_steps.append({
                "step_num": step_num,
                "action": action,
                "description": description,
                "url": page.url,
                "screenshot": screenshot_path,
                "success": success,
            })

            if not success:
                print(f"    Continuing despite failure...")

        # Capture final state
        final_path = screenshots_dir / f"step-{len(steps) + 1:02d}-final.png"
        await page.screenshot(path=str(final_path), full_page=False)
        captured_steps.append({
            "step_num": len(steps) + 1,
            "action": "final",
            "description": "Final state",
            "url": page.url,
            "screenshot": final_path,
            "success": True,
        })

        await browser.close()

    return captured_steps


# ---------------------------------------------------------------------------
# AI annotation
# ---------------------------------------------------------------------------

async def annotate_steps(
    client, model: str, url: str, goal: str, captured_steps: list[dict],
) -> tuple[list[dict], dict]:
    """Annotate each screenshot and assemble the tutorial."""
    print(f"\nAnnotating {len(captured_steps)} screenshots...")

    async def _annotate_one(step):
        if step["action"] == "final":
            return {
                "step_title": "Tutorial complete",
                "instruction_text": "You have completed all the steps.",
                "callout_text": None,
            }
        prompt = ANNOTATE_STEP_PROMPT.format(
            step_num=step["step_num"],
            description=step["description"],
            url=step["url"],
        )
        print(f"  Annotating step {step['step_num']}...", end=" ", flush=True)
        response = await async_vision_call(
            client, model,
            "You are a tutorial writer.",
            prompt,
            [step["screenshot"]],
            max_tokens=512,
        )
        print("done")
        cleaned = response.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            return {
                "step_title": step["description"],
                "instruction_text": step["description"],
                "callout_text": None,
            }

    annotations = await asyncio.gather(*[_annotate_one(s) for s in captured_steps])

    # Assemble tutorial wrapper
    print(f"\nAssembling tutorial...", end=" ", flush=True)
    annotated_block = "\n\n".join(
        f"Step {captured_steps[i]['step_num']}: {ann.get('step_title', '')}\n"
        f"Instruction: {ann.get('instruction_text', '')}\n"
        f"Callout: {ann.get('callout_text', 'none')}"
        for i, ann in enumerate(annotations)
    )
    wrapper_response = await async_text_call(
        client, model,
        "You are a technical writer.",
        ASSEMBLE_TUTORIAL_PROMPT.format(
            url=url, goal=goal, total_steps=len(captured_steps),
            annotated_steps=annotated_block,
        ),
    )
    print("done")

    cleaned = wrapper_response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        wrapper = json.loads(cleaned.strip())
    except json.JSONDecodeError:
        wrapper = {
            "title": f"How to: {goal}",
            "introduction": f"This tutorial walks you through how to {goal.lower()}.",
            "prerequisites": ["An account on the platform", "A modern web browser"],
            "summary": "You have completed all the steps in this tutorial.",
        }

    return list(annotations), wrapper


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_terminal(
    wrapper: dict, captured_steps: list[dict], annotations: list[dict], model: str,
) -> str:
    """Format tutorial for terminal display."""
    lines = []
    lines.append(box_header(
        wrapper.get("title", "Tutorial"),
        f"Steps: {len(captured_steps)} | Model: {model}",
    ))
    lines.append("")
    lines.append(wrapper.get("introduction", ""))
    lines.append("")

    prereqs = wrapper.get("prerequisites", [])
    if prereqs:
        lines.append("Prerequisites:")
        for p in prereqs:
            lines.append(f"  - {p}")
        lines.append("")

    for step, ann in zip(captured_steps, annotations):
        if step["action"] == "final":
            lines.append(section_rule("DONE"))
        else:
            lines.append(section_rule(f"Step {step['step_num']}: {ann.get('step_title', '')}"))
        lines.append("")
        lines.append(ann.get("instruction_text", ""))
        if ann.get("callout_text"):
            lines.append(f"\n  TIP: {ann['callout_text']}")
        status = "OK" if step.get("success") else "FAILED"
        lines.append(f"  [{status}] Screenshot: {step['screenshot']}")
        lines.append("")

    lines.append(section_rule("SUMMARY"))
    lines.append("")
    lines.append(wrapper.get("summary", ""))
    lines.append("")
    lines.append(footer_line())
    lines.append("Generated by ProductKit · github.com/shahcolate/Product-Kit")
    lines.append("")
    return "\n".join(lines)


def format_markdown(
    wrapper: dict, captured_steps: list[dict], annotations: list[dict], model: str,
) -> str:
    """Format tutorial as Markdown with embedded screenshot references."""
    now = datetime.now().strftime("%B %d, %Y")
    lines = []
    lines.append(f"# {wrapper.get('title', 'Tutorial')}")
    lines.append(f"*{len(captured_steps)} steps | Model: {model} | {now}*")
    lines.append("")
    lines.append(wrapper.get("introduction", ""))
    lines.append("")

    prereqs = wrapper.get("prerequisites", [])
    if prereqs:
        lines.append("## Prerequisites")
        lines.append("")
        for p in prereqs:
            lines.append(f"- {p}")
        lines.append("")

    lines.append("## Steps")
    lines.append("")

    for step, ann in zip(captured_steps, annotations):
        if step["action"] == "final":
            continue
        lines.append(f"### Step {step['step_num']}: {ann.get('step_title', '')}")
        lines.append("")
        lines.append(ann.get("instruction_text", ""))
        lines.append("")
        lines.append(f"![Step {step['step_num']}](screenshots/step-{step['step_num']:02d}.png)")
        lines.append("")
        if ann.get("callout_text"):
            lines.append(f"> **Tip:** {ann['callout_text']}")
            lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(wrapper.get("summary", ""))
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
        description="Tutorial Creator — AI-powered step-by-step tutorial generator"
    )
    parser.add_argument("url", help="URL to create a tutorial for")
    parser.add_argument("--goal", type=str, default=None,
                        help="Natural language goal (AI plans the steps)")
    parser.add_argument("--steps", type=str, default=None,
                        help="Pre-defined steps JSON file (overrides --goal)")
    parser.add_argument("--auth-cookie", type=str, default=None,
                        help="Cookie file for authenticated sessions (JSON format)")
    parser.add_argument("--viewport", type=str, default="1280x800",
                        help="Browser viewport size (default: 1280x800)")
    parser.add_argument("--wait", type=int, default=2000,
                        help="Milliseconds to wait after each action (default: 2000)")
    parser.add_argument("--max-steps", type=int, default=20,
                        help="Maximum steps for AI-planned tutorials (default: 20)")
    add_common_args(parser)
    args = parser.parse_args()

    if not args.goal and not args.steps:
        print("ERROR: Provide either --goal or --steps.", file=sys.stderr)
        sys.exit(1)

    require_api_key()
    client = make_async_client()

    # Set up output directory
    url_slug = slugify(args.url.split("//")[-1].split("/")[0].replace("www.", ""))
    date_str = datetime.now().strftime("%Y-%m-%d")
    goal_slug = slugify(args.goal[:40]) if args.goal else "manual"
    output_dir = repo_root() / "tutorials" / f"{url_slug}-{goal_slug}-{date_str}"
    output_dir.mkdir(parents=True, exist_ok=True)

    async def _run():
        # Phase 1: Plan steps (or load from file)
        if args.steps:
            print(f"\nLoading steps from {args.steps}...")
            steps = load_steps_file(args.steps)
            print(f"  {len(steps)} steps loaded")
        else:
            print(f"\nPlanning tutorial for: {args.goal}")
            print(f"URL: {args.url}\n")

            # Take initial screenshot for planning
            width, height = (int(x) for x in args.viewport.split("x"))
            async with async_playwright() as pw:
                browser = await pw.chromium.launch()
                ctx = await browser.new_context(viewport={"width": width, "height": height})
                page = await ctx.new_page()
                await page.goto(args.url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)
                initial_screenshot = output_dir / "screenshots" / "initial.png"
                initial_screenshot.parent.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=str(initial_screenshot), full_page=False)
                await browser.close()

            print("  Planning steps...", end=" ", flush=True)
            steps = await plan_steps(
                client, args.model, args.url, args.goal, initial_screenshot, args.max_steps,
            )
            print(f"done ({len(steps)} steps planned)")

            if not steps:
                print("ERROR: Could not plan any steps.", file=sys.stderr)
                sys.exit(1)

            for i, step in enumerate(steps):
                print(f"    {i + 1}. [{step.get('action')}] {step.get('description')}")

        # Phase 2: Execute steps in browser
        print(f"\nExecuting {len(steps)} steps...")
        captured_steps = await execute_steps(
            args.url, steps, args.viewport, args.wait,
            output_dir, client, args.model,
            auth_cookie_file=args.auth_cookie,
        )

        if not captured_steps:
            print("ERROR: No steps executed.", file=sys.stderr)
            sys.exit(1)

        # Phase 3: Annotate screenshots
        goal_text = args.goal or "Complete the tutorial"
        annotations, wrapper = await annotate_steps(
            client, args.model, args.url, goal_text, captured_steps,
        )

        print()

        # Format output
        if args.output == "markdown":
            output = format_markdown(wrapper, captured_steps, annotations, args.model)
        else:
            output = format_terminal(wrapper, captured_steps, annotations, args.model)

        print(output)

        # Save (always save markdown + screenshots for tutorials)
        if args.save:
            md_output = format_markdown(wrapper, captured_steps, annotations, args.model)
            index_path = output_dir / "index.md"
            index_path.write_text(md_output)
            print(f"Saved to {output_dir}/")
            print(f"  index.md + {len(captured_steps)} screenshots")

    asyncio.run(_run())


if __name__ == "__main__":
    main()
