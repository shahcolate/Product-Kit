#!/usr/bin/env python3
from __future__ import annotations

"""
ProductKit Feedback Synthesizer
Ingests user feedback from CSV/JSON, clusters by theme, and produces structured synthesis
with quotes, sentiment, urgency, and recommended actions.

Usage:
  python scripts/feedback_synth.py feedback.csv --text-column "comment" --source "NPS Q1 2026"
  python scripts/feedback_synth.py reviews.json --format json --text-field "body" --max-themes 8
  python scripts/feedback_synth.py feedback.csv --output markdown --save

Requires: ANTHROPIC_API_KEY env var, pip install anthropic
"""

import argparse
import asyncio
import csv
import json
import sys
from pathlib import Path

# Allow running from repo root or scripts/
sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    add_common_args,
    async_text_call,
    box_header,
    dated_slug,
    footer_line,
    make_async_client,
    require_api_key,
    save_output,
    section_rule,
)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_feedback(filepath: Path, fmt: str, text_field: str) -> list[str]:
    """Load feedback items from CSV or JSON, returning a list of text strings."""
    if fmt == "auto":
        fmt = "json" if filepath.suffix.lower() == ".json" else "csv"

    if fmt == "csv":
        items = []
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if text_field not in (reader.fieldnames or []):
                available = ", ".join(reader.fieldnames or [])
                print(f"ERROR: Column '{text_field}' not found. Available: {available}", file=sys.stderr)
                sys.exit(1)
            for row in reader:
                val = (row.get(text_field) or "").strip()
                if val:
                    items.append(val)
        return items

    elif fmt == "json":
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            # Try common wrapper keys
            for key in ("data", "results", "items", "reviews", "feedback"):
                if key in data and isinstance(data[key], list):
                    entries = data[key]
                    break
            else:
                print("ERROR: JSON must be an array or contain a recognized array key (data, results, items, reviews, feedback).", file=sys.stderr)
                sys.exit(1)

        items = []
        for entry in entries:
            if isinstance(entry, str):
                val = entry.strip()
            elif isinstance(entry, dict):
                val = (entry.get(text_field) or "").strip()
                if not val:
                    print(f"ERROR: Field '{text_field}' not found in JSON objects. Available: {', '.join(entry.keys())}", file=sys.stderr)
                    sys.exit(1)
            else:
                continue
            if val:
                items.append(val)
        return items

    else:
        print(f"ERROR: Unknown format '{fmt}'.", file=sys.stderr)
        sys.exit(1)


def dedup_and_sample(items: list[str], max_items: int) -> list[str]:
    """Deduplicate and apply sample limit."""
    seen = set()
    unique = []
    for item in items:
        normalized = item.lower().strip()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(item)
    if len(unique) > max_items:
        # Take evenly spaced samples to preserve distribution
        step = len(unique) / max_items
        unique = [unique[int(i * step)] for i in range(max_items)]
    return unique


# ---------------------------------------------------------------------------
# AI synthesis pipeline
# ---------------------------------------------------------------------------

THEME_EXTRACTION_PROMPT = """You are a product research analyst. Analyze this batch of user feedback and extract themes.

For each theme, provide:
- **Theme name** (short, descriptive)
- **Sentiment** (positive / negative / mixed)
- **Frequency** (how many items in this batch relate to this theme)
- **Representative quotes** (2-3 verbatim quotes from the feedback, as blockquotes)
- **Urgency** (high / medium / low — based on user frustration/impact signals)

FEEDBACK BATCH:
{feedback_block}

Return your analysis as structured text with clear section headers per theme. Be specific — use the actual language from the feedback."""

MERGE_PROMPT = """You are a product research analyst. You have extracted themes from {num_batches} batches of user feedback. Now consolidate them into a unified synthesis.

BATCH RESULTS:
{batch_results}

INSTRUCTIONS:
1. Merge duplicate/overlapping themes into a single theme with the combined evidence
2. Rank themes by frequency (most common first), then by urgency
3. Limit to the top {max_themes} themes
4. For each final theme, provide:
   - **Theme name**
   - **Sentiment** (positive / negative / mixed)
   - **Frequency signal** (e.g., "mentioned in 40% of feedback")
   - **Urgency** (high / medium / low)
   - **Representative quotes** (3-5 best, as blockquotes)
   - **Summary** (2-3 sentences capturing the core insight)

Be precise. Preserve the original user language in quotes."""

ACTIONABILITY_PROMPT = """You are a product manager assessing feedback themes for actionability.

SOURCE: {source}
TOTAL FEEDBACK ITEMS ANALYZED: {total_items}

SYNTHESIZED THEMES:
{themes}

For each theme, assess:
1. **Actionability**: one of:
   - **Actionable now** — clear next step the team can take
   - **Needs investigation** — signal is real but root cause unclear
   - **Known limitation** — team is aware, no near-term fix
   - **Feature request** — users want something new
2. **Recommended action** — one specific, concrete next step (not generic)
3. **Impact if ignored** — what happens if the team does nothing

Then provide:
- **Top 3 priorities** — the three themes the team should address first, with reasoning
- **Overall health signal** — is this feedback base mostly happy, mostly frustrated, or split?

Be direct and specific. Recommendations should be actionable by a PM this week."""


async def extract_themes_batch(
    client, model: str, feedback_items: list[str], batch_num: int, total_batches: int,
) -> str:
    """Extract themes from a single batch of feedback items."""
    feedback_block = "\n".join(f"- {item}" for item in feedback_items)
    prompt = THEME_EXTRACTION_PROMPT.format(feedback_block=feedback_block)
    print(f"  [{batch_num}/{total_batches}] Extracting themes from {len(feedback_items)} items...", end=" ", flush=True)
    result = await async_text_call(client, model, "You are a product research analyst.", prompt)
    print("done")
    return result


async def run_synthesis(
    client, model: str, items: list[str], source: str, max_themes: int,
) -> tuple[str, str]:
    """Run the full 3-phase synthesis pipeline. Returns (themes, assessment)."""
    # Phase 1: Batch theme extraction
    batch_size = 100
    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    total_batches = len(batches)

    print(f"\nPhase 1: Theme extraction ({total_batches} batch{'es' if total_batches != 1 else ''})")
    tasks = [
        extract_themes_batch(client, model, batch, i + 1, total_batches)
        for i, batch in enumerate(batches)
    ]
    batch_results = await asyncio.gather(*tasks)

    # Phase 2: Cross-batch merge
    print(f"\nPhase 2: Cross-batch merge and ranking...", end=" ", flush=True)
    combined_results = "\n\n---\n\n".join(
        f"BATCH {i + 1}:\n{result}" for i, result in enumerate(batch_results)
    )
    merge_prompt = MERGE_PROMPT.format(
        num_batches=total_batches,
        batch_results=combined_results,
        max_themes=max_themes,
    )
    themes = await async_text_call(client, model, "You are a product research analyst.", merge_prompt)
    print("done")

    # Phase 3: Actionability assessment
    print(f"Phase 3: Actionability assessment...", end=" ", flush=True)
    action_prompt = ACTIONABILITY_PROMPT.format(
        source=source or "User feedback",
        total_items=len(items),
        themes=themes,
    )
    assessment = await async_text_call(client, model, "You are a senior product manager.", action_prompt)
    print("done")

    return themes, assessment


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_terminal(source: str, total: int, model: str, themes: str, assessment: str) -> str:
    """Format results for terminal display."""
    lines = []
    lines.append(box_header(
        f"FEEDBACK SYNTHESIS: {source or 'User Feedback'}",
        f"Items: {total} | Model: {model}",
    ))
    lines.append("")
    lines.append(section_rule("THEMES"))
    lines.append("")
    lines.append(themes.strip())
    lines.append("")
    lines.append(section_rule("ACTIONABILITY ASSESSMENT"))
    lines.append("")
    lines.append(assessment.strip())
    lines.append("")
    lines.append(footer_line())
    lines.append("Generated by ProductKit · github.com/shahcolate/Product-Kit")
    lines.append("")
    return "\n".join(lines)


def format_markdown(source: str, total: int, model: str, themes: str, assessment: str) -> str:
    """Format results as Markdown."""
    from datetime import datetime
    now = datetime.now().strftime("%B %d, %Y")
    lines = []
    lines.append(f"# Feedback Synthesis: {source or 'User Feedback'}")
    lines.append(f"*{total} items analyzed | Model: {model} | {now}*")
    lines.append("")
    lines.append("## Themes")
    lines.append("")
    lines.append(themes.strip())
    lines.append("")
    lines.append("## Actionability Assessment")
    lines.append("")
    lines.append(assessment.strip())
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
        description="Feedback Synthesizer — cluster user feedback into themes with actionability assessment"
    )
    parser.add_argument("file", help="Path to CSV or JSON feedback file")
    parser.add_argument("--text-column", dest="text_field", default="comment",
                        help="Column name (CSV) or field name (JSON) containing feedback text (default: comment)")
    parser.add_argument("--text-field", dest="text_field_json",
                        help="Alias for --text-column (for JSON files)")
    parser.add_argument("--format", choices=["csv", "json", "auto"], default="auto",
                        help="Input format (default: auto-detected from extension)")
    parser.add_argument("--source", type=str, default=None,
                        help="Label for the feedback source (e.g., 'NPS Q1 2026')")
    parser.add_argument("--max-themes", type=int, default=10,
                        help="Maximum number of themes to surface (default: 10)")
    parser.add_argument("--sample", type=int, default=500,
                        help="Maximum feedback items to analyze (default: 500)")
    add_common_args(parser)
    args = parser.parse_args()

    # Resolve text field
    text_field = args.text_field_json or args.text_field

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    require_api_key()

    # Load and prepare data
    print(f"\nLoading feedback from {filepath}...")
    items = load_feedback(filepath, args.format, text_field)
    if not items:
        print("ERROR: No feedback items found.", file=sys.stderr)
        sys.exit(1)

    original_count = len(items)
    items = dedup_and_sample(items, args.sample)
    print(f"  {original_count} items loaded, {len(items)} after dedup/sampling")

    # Run synthesis
    client = make_async_client()
    source = args.source or filepath.stem
    themes, assessment = asyncio.run(
        run_synthesis(client, args.model, items, source, args.max_themes)
    )
    print()

    # Format output
    if args.output == "markdown":
        output = format_markdown(source, len(items), args.model, themes, assessment)
    else:
        output = format_terminal(source, len(items), args.model, themes, assessment)

    print(output)

    # Save if requested
    if args.save:
        slug = dated_slug(source)
        md_output = format_markdown(source, len(items), args.model, themes, assessment)
        filepath = save_output(md_output, "feedback-synthesis", f"{slug}.md")
        print(f"Saved to {filepath}")


if __name__ == "__main__":
    main()
