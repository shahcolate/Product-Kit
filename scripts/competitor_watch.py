#!/usr/bin/env python3
from __future__ import annotations

"""
ProductKit Competitive Screenshot Monitor
Captures competitor web pages, detects semantic changes vs. previous captures using Claude vision.

Usage:
  python scripts/competitor_watch.py --config competitors.json
  python scripts/competitor_watch.py --url "https://competitor.com/pricing" --name "Competitor X" --diff
  python scripts/competitor_watch.py --config competitors.json --output markdown --save

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
# Config loading
# ---------------------------------------------------------------------------

def load_config(config_path: str) -> list[dict]:
    """Load competitor config from JSON file."""
    with open(config_path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict) and "competitors" in data:
        entries = data["competitors"]
    else:
        entries = [data]

    for entry in entries:
        if "url" not in entry or "name" not in entry:
            print("ERROR: Each competitor entry must have 'url' and 'name' fields.", file=sys.stderr)
            sys.exit(1)
    return entries


# ---------------------------------------------------------------------------
# Screenshot capture
# ---------------------------------------------------------------------------

async def capture_screenshot(
    url: str, slug: str, viewport: str, output_dir: Path,
) -> Path:
    """Capture a full-page screenshot of a URL using Playwright."""
    width, height = (int(x) for x in viewport.split("x"))
    screenshot_path = output_dir / f"{slug}.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={"width": width, "height": height})
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)  # Extra settle time
            await page.screenshot(path=str(screenshot_path), full_page=True)
        except Exception as e:
            print(f"    WARNING: Could not capture {url}: {e}", file=sys.stderr)
            await browser.close()
            return None
        await browser.close()

    return screenshot_path


def find_previous_capture(slug: str, current_date: str) -> Path | None:
    """Find the most recent previous capture for a competitor."""
    watch_dir = repo_root() / "competitor-watch"
    if not watch_dir.exists():
        return None

    candidates = []
    for date_dir in sorted(watch_dir.iterdir(), reverse=True):
        if not date_dir.is_dir() or date_dir.name == current_date:
            continue
        candidate = date_dir / f"{slug}.png"
        if candidate.exists():
            candidates.append(candidate)

    return candidates[0] if candidates else None


# ---------------------------------------------------------------------------
# AI analysis
# ---------------------------------------------------------------------------

BASELINE_PROMPT = """You are a competitive intelligence analyst. Analyze this screenshot of a competitor's web page.

COMPETITOR: {name}
URL: {url}
{category_line}

Provide:
1. **Page purpose** — what is this page trying to do?
2. **Key messaging** — main value propositions, headlines, and positioning
3. **Pricing/packaging** (if visible) — tiers, prices, feature gates
4. **Social proof** — logos, testimonials, case studies, metrics
5. **CTAs** — what actions are they driving?
6. **Notable design choices** — anything unusual or strategic about the layout/design

Be specific. Reference actual text and elements you can see."""

DIFF_PROMPT = """You are a competitive intelligence analyst. Compare these two screenshots of the same competitor page, captured at different times.

COMPETITOR: {name}
URL: {url}
{category_line}

The FIRST image is the PREVIOUS capture. The SECOND image is the CURRENT capture.

Provide:
1. **Changes detected** — list every meaningful change you can identify
2. **Significance** — rate as: cosmetic (visual tweaks only), minor (messaging/layout changes), or major (pricing, positioning, or feature changes)
3. **Strategic implication** — what does this change suggest about their strategy?
4. **Competitive response** — should we care? What, if anything, should we do?

Focus on SEMANTIC changes (what the content means), not pixel-level differences. If the pages look identical, say so."""

SYNTHESIS_PROMPT = """You are a competitive intelligence analyst. You just analyzed {num_competitors} competitor pages. Now synthesize the findings.

INDIVIDUAL ANALYSES:
{analyses}

Provide:
1. **Cross-competitor patterns** — what trends or shared moves do you see?
2. **Strategic moves** — any competitor making a notable shift?
3. **Market signals** — what does this collectively suggest about the market?
4. **Recommended actions** — top 3 things the product team should know or do based on these findings

Be direct and strategic. Focus on what's actionable."""


async def analyze_single(
    client, model: str, entry: dict, screenshot_path: Path, previous_path: Path | None,
    do_diff: bool,
) -> dict:
    """Analyze a single competitor screenshot, optionally diffing against previous."""
    name = entry["name"]
    url = entry["url"]
    category_line = f"CATEGORY: {entry['category']}" if entry.get("category") else ""

    if do_diff and previous_path:
        prompt = DIFF_PROMPT.format(name=name, url=url, category_line=category_line)
        analysis = await async_vision_call(
            client, model,
            "You are a competitive intelligence analyst.",
            prompt,
            [previous_path, screenshot_path],
        )
        mode = "diff"
    else:
        prompt = BASELINE_PROMPT.format(name=name, url=url, category_line=category_line)
        analysis = await async_vision_call(
            client, model,
            "You are a competitive intelligence analyst.",
            prompt,
            [screenshot_path],
        )
        mode = "baseline"

    return {"name": name, "url": url, "analysis": analysis, "mode": mode}


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_terminal(results: list[dict], model: str, synthesis: str | None) -> str:
    """Format results for terminal display."""
    lines = []
    lines.append(box_header(
        "COMPETITIVE WATCH",
        f"Competitors: {len(results)} | Model: {model}",
    ))
    lines.append("")

    for r in results:
        mode_label = "(diff vs previous)" if r["mode"] == "diff" else "(baseline)"
        lines.append(section_rule(f"{r['name']} {mode_label}"))
        lines.append(f"  URL: {r['url']}")
        lines.append("")
        lines.append(r["analysis"].strip())
        lines.append("")

    if synthesis:
        lines.append(section_rule("CROSS-COMPETITOR SYNTHESIS"))
        lines.append("")
        lines.append(synthesis.strip())
        lines.append("")

    lines.append(footer_line())
    lines.append("Generated by ProductKit · github.com/shahcolate/Product-Kit")
    lines.append("")
    return "\n".join(lines)


def format_markdown(results: list[dict], model: str, synthesis: str | None) -> str:
    """Format results as Markdown."""
    now = datetime.now().strftime("%B %d, %Y")
    lines = []
    lines.append("# Competitive Watch Report")
    lines.append(f"*{len(results)} competitors | Model: {model} | {now}*")
    lines.append("")

    for r in results:
        mode_label = "(diff vs previous)" if r["mode"] == "diff" else "(baseline)"
        lines.append(f"## {r['name']} {mode_label}")
        lines.append(f"URL: {r['url']}")
        lines.append("")
        lines.append(r["analysis"].strip())
        lines.append("")

    if synthesis:
        lines.append("## Cross-Competitor Synthesis")
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
        description="Competitive Screenshot Monitor — capture and analyze competitor pages"
    )
    parser.add_argument("--config", type=str, default=None,
                        help="JSON config file with competitor URLs")
    parser.add_argument("--url", type=str, default=None,
                        help="Single URL to monitor")
    parser.add_argument("--name", type=str, default=None,
                        help="Competitor name (for single URL mode)")
    parser.add_argument("--category", type=str, default=None,
                        help="Category label (e.g., 'pricing', 'features')")
    parser.add_argument("--diff", action="store_true",
                        help="Compare vs last capture (default when previous exists)")
    parser.add_argument("--capture-only", action="store_true",
                        help="Capture screenshots without AI analysis")
    parser.add_argument("--viewport", type=str, default="1280x800",
                        help="Browser viewport size (default: 1280x800)")
    add_common_args(parser)
    args = parser.parse_args()

    if not args.config and not args.url:
        print("ERROR: Provide either --config or --url.", file=sys.stderr)
        sys.exit(1)

    if args.url and not args.name:
        print("ERROR: --name is required with --url.", file=sys.stderr)
        sys.exit(1)

    if not args.capture_only:
        require_api_key()

    # Build entries list
    if args.config:
        entries = load_config(args.config)
    else:
        entries = [{"name": args.name, "url": args.url, "category": args.category}]

    # Set up output directory
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = repo_root() / "competitor-watch" / date_str
    output_dir.mkdir(parents=True, exist_ok=True)

    async def _run():
        # Phase 1: Capture screenshots
        print(f"\nCapturing {len(entries)} page(s)...")
        captures = []
        for entry in entries:
            slug = slugify(entry["name"])
            print(f"  Capturing {entry['name']}...", end=" ", flush=True)
            path = await capture_screenshot(entry["url"], slug, args.viewport, output_dir)
            if path:
                print(f"saved to {path}")
                previous = find_previous_capture(slug, date_str)
                captures.append((entry, path, previous))
            else:
                print("FAILED")

        if not captures:
            print("ERROR: No screenshots captured.", file=sys.stderr)
            sys.exit(1)

        if args.capture_only:
            print(f"\nScreenshots saved to {output_dir}")
            return

        # Phase 2: Analyze each competitor
        client = make_async_client()
        print(f"\nAnalyzing {len(captures)} page(s)...")

        async def _analyze(entry, path, previous):
            do_diff = args.diff or previous is not None
            if do_diff and previous:
                print(f"  Analyzing {entry['name']} (diff vs {previous.parent.name})...", end=" ", flush=True)
            else:
                print(f"  Analyzing {entry['name']} (baseline)...", end=" ", flush=True)
            result = await analyze_single(client, args.model, entry, path, previous, do_diff)
            print("done")
            return result

        results = await asyncio.gather(*[
            _analyze(entry, path, previous) for entry, path, previous in captures
        ])

        # Phase 3: Cross-competitor synthesis (if multiple)
        synthesis = None
        if len(results) > 1:
            print(f"\nSynthesizing across {len(results)} competitors...", end=" ", flush=True)
            analyses_block = "\n\n---\n\n".join(
                f"**{r['name']}** ({r['url']}):\n{r['analysis']}" for r in results
            )
            synthesis = await async_text_call(
                client, args.model,
                "You are a competitive intelligence analyst.",
                SYNTHESIS_PROMPT.format(num_competitors=len(results), analyses=analyses_block),
            )
            print("done")

        print()

        # Format output
        results_list = list(results)
        if args.output == "markdown":
            output = format_markdown(results_list, args.model, synthesis)
        else:
            output = format_terminal(results_list, args.model, synthesis)

        print(output)

        # Save if requested
        if args.save:
            slug = dated_slug("competitor-watch")
            md_output = format_markdown(results_list, args.model, synthesis)
            filepath = save_output(md_output, "competitor-watch", f"{slug}-report.md")
            print(f"Saved to {filepath}")

    asyncio.run(_run())


if __name__ == "__main__":
    main()
