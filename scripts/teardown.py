#!/usr/bin/env python3
from __future__ import annotations

"""
ProductKit AI Product Teardown Tool
Runs any product through Strategic PM's full framework battery and produces a structured report.

Usage:
  python scripts/teardown.py "Notion"
  python scripts/teardown.py "Notion" --context "workspace productivity tool for teams"
  python scripts/teardown.py "Linear" --model claude-sonnet-4-6
  python scripts/teardown.py "Slack" --output markdown --save
  python scripts/teardown.py "Notion" --vs "Coda"
  python scripts/teardown.py "Notion" --output social

Requires: ANTHROPIC_API_KEY env var, pip install anthropic
"""

import argparse
import asyncio
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import anthropic


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def repo_root() -> Path:
    """Return the repo root (parent of scripts/)."""
    return Path(__file__).parent.parent


def load_skill() -> str:
    """Load Strategic PM skill text from SKILL.md."""
    skill_path = repo_root() / "plugins" / "strategic-pm" / "skills" / "strategic-pm" / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"No SKILL.md found at {skill_path}")
    return skill_path.read_text()


def slugify(name: str) -> str:
    """Convert product name to a filename-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------

DIMENSIONS = [
    {
        "num": 1,
        "title": "JOBS TO BE DONE",
        "prompt": """Analyze {product} through the JTBD and "What Would Have to Be True?" frameworks.

{context_line}

Provide a structured analysis with these exact sections:

**Primary Job:** The core job users hire {product} to do (JTBD framing — not a feature description).
**Secondary Jobs:** 2-3 additional jobs served.
**Aha Moment:** The specific moment a new user first experiences core value.
**Value Prop Clarity:** Rate as 🟢 High / 🟡 Medium / 🔴 Low — can a new user explain what this does within 60 seconds?
**"What Would Have to Be True?":** 3-4 conditions that must hold for {product}'s value prop to succeed. Rank by uncertainty.

Be opinionated. Use specific evidence. Keep it concise — no filler.""",
    },
    {
        "num": 2,
        "title": "COMPETITIVE MOAT",
        "prompt": """Analyze {product}'s competitive moat using the 7 Powers framework, Wardley Mapping lens, and Competitive Threat Taxonomy.

{context_line}

Provide a structured analysis with these exact sections:

**7 Powers Assessment:**
For each power, state whether {product} HAS it, is BUILDING it, or LACKS it, with one-line evidence:
- Scale Economies:
- Network Effects:
- Counter-Positioning:
- Switching Costs:
- Branding:
- Cornered Resource:
- Process Power:

**Wardley Position:** Where does {product}'s core capability sit on the evolution axis (genesis → custom → product → commodity)? What does this mean for defensibility?

**Competitive Threats:**
- Direct competitors:
- Substitute behaviors:
- Platform risks:

**Biggest Threat:** The single most dangerous competitive threat and why.

Be opinionated. Use specific evidence. Keep it concise.""",
    },
    {
        "num": 3,
        "title": "GROWTH MODEL",
        "prompt": """Analyze {product}'s growth and retention model using Acquisition Loop Typing and the 3 Retention Horizons.

{context_line}

Provide a structured analysis with these exact sections:

**Acquisition Loop Type:** Viral / Content / Paid / Sales — which is primary, and what's the mechanism?
**Loop Accelerator:** The single highest-leverage variable in their growth loop right now.
**Loop Breaker:** What would break this loop?

**Retention Horizons:**
- **H1 — Activation (Day 1-7):** What's the activation moment? How quickly do users hit core value?
- **H2 — Habit (Week 2-8):** What return behavior are they building? What's the trigger?
- **H3 — Deep (Month 3+):** What creates deep retention — habit, switching costs, or network effects?

**Retention Risk:** The biggest gap in their retention architecture.

Be opinionated. Use specific evidence. Keep it concise.""",
    },
    {
        "num": 4,
        "title": "ANTI-PATTERN FLAGS",
        "prompt": """Scan {product} for all 13 anti-patterns from the Anti-Pattern Detection Engine.

{context_line}

For EACH of the following anti-patterns, state whether it is DETECTED (⚠) or NOT DETECTED (✓), with brief evidence:

1. **Feature factory output** — specs/features without a linked outcome
2. **Vanity metrics** — reliance on pageviews, downloads, MAU without retention context
3. **Roadmap theater** — items without a credible delivery path
4. **Consensus-driven prioritization** — averaging opinions instead of finding highest-leverage outcomes
5. **Solution-first thinking** — jumping to solutions before defining problems
6. **Premature scaling** — designing for scale before validation
7. **Metric-less launches** — shipping without pre-defined success metrics
8. **HiPPO decisions** — executive preference as substitute for evidence
9. **False urgency** — everything framed as critical to avoid trade-offs
10. **Post-launch abandonment** — shipping and moving on without learning
11. **Duct-tape roadmaps** — unrelated features without a coherent thesis
12. **Backfill analytics** — manufacturing data to justify decisions already made
13. **Democracy of ideas** — treating all ideas as equally worthy

Count the total detected at the end. Be direct — if there's evidence of an anti-pattern, flag it. If there isn't, say so cleanly.""",
    },
    {
        "num": 5,
        "title": "MONETIZATION",
        "prompt": """Analyze {product}'s monetization strategy using Unit Economics, Pricing Strategy, and Monetization Model frameworks.

{context_line}

Provide a structured analysis with these exact sections:

**Monetization Model:** Which type — Usage-based / Seat-based SaaS / Transactional / Marketplace / Freemium / Enterprise license? What's the primary lever?

**Pricing Alignment:**
- What's the value metric? Does pricing scale with what the customer gets?
- Is the packaging designed for the decision, or the feature list?
- Score alignment as 🟢 Strong / 🟡 Moderate / 🔴 Weak

**Upgrade Trigger:** What specific user behavior or moment triggers the free→paid or tier upgrade?

**Unit Economics Assessment:**
- Likely CAC channels (paid, organic, referral)
- LTV drivers — what extends lifetime value?
- LTV:CAC health signal: 🟢 Healthy / 🟡 Caution / 🔴 Warning

**Monetization Risk:** The single biggest risk to their revenue model.

Be opinionated. Use specific evidence. Keep it concise.""",
    },
    {
        "num": 6,
        "title": "STRATEGIC VERDICT",
        "prompt": """Deliver a strategic verdict on {product} using the Devil's Advocate Protocol and Second-Order Consequence thinking.

{context_line}

Provide a structured analysis with these exact sections:

**Steelman:** The strongest possible case for {product}'s strategy — stated as a smart bull would frame it.

**Top 3 Risks:**
For each, include the second-order consequence:
1. [Risk] → Second-order: [consequence]
2. [Risk] → Second-order: [consequence]
3. [Risk] → Second-order: [consequence]

**If I Were PM, I'd Change:** The single highest-leverage change you'd make to {product}'s strategy. Be specific and actionable.

**Escape Hatch:** For the #1 risk above, what's the early warning signal and kill criterion?

**Confidence:** Rate your overall analysis as 🟢 High / 🟡 Medium / 🔴 Low, and explain why.

Be opinionated, direct, and concise. Take a position.""",
    },
]

COMPARISON_DIMENSION = {
    "num": 7,
    "title": "HEAD-TO-HEAD VERDICT",
    "prompt": """You just completed a full 6-dimension teardown of both {product_a} and {product_b}. Now deliver the head-to-head verdict.

{context_line}

Provide a structured comparison with these exact sections:

**Dimension Scorecard:**
For each of the 6 dimensions, declare a winner (or tie) with a one-line justification:
1. Jobs to Be Done: {product_a} / {product_b} / Tie — [why]
2. Competitive Moat: {product_a} / {product_b} / Tie — [why]
3. Growth Model: {product_a} / {product_b} / Tie — [why]
4. Anti-Pattern Flags: {product_a} / {product_b} / Tie — [why] (fewer flags = better)
5. Monetization: {product_a} / {product_b} / Tie — [why]
6. Strategic Verdict: {product_a} / {product_b} / Tie — [why]

**Overall Winner:** {product_a} or {product_b} — and the single most important reason why.

**Where the Loser Wins:** The one dimension or area where the losing product is genuinely stronger.

**If They Merged:** The single most powerful product that could be built by combining the best of both.

Be opinionated, direct, and decisive. Pick a winner — don't hedge.""",
}

SOCIAL_SUMMARY_PROMPT = """You just completed a full 6-dimension teardown of {product}. Now distill it into a social-ready summary.

{context_line}

Create a social media thread summary with these exact sections:

**Hook:** A single provocative sentence (under 280 characters) that captures the most surprising or contrarian finding. Make it quotable.

**5 Bullet Verdicts:** One per line, each under 60 characters, each starting with an emoji verdict:
- 🟢 = strength
- 🟡 = mixed/watch
- 🔴 = weakness
Format: [emoji] [Dimension]: [one-line verdict]

**Bottom Line:** One sentence — would you bet on this product? Why or why not?

**Tag:** "Full teardown: github.com/shahcolate/Product-Kit"

Be punchy, opinionated, and shareable. No hedging."""


# ---------------------------------------------------------------------------
# Async API calls
# ---------------------------------------------------------------------------

def build_dimension_prompt(product: str, context: str | None, dimension: dict) -> str:
    """Build the user message for a single dimension."""
    context_line = f"Context: {context}" if context else f"Analyze based on publicly known information about {product}."
    return dimension["prompt"].format(product=product, context_line=context_line)


def build_comparison_prompt(product_a: str, product_b: str, context: str | None) -> str:
    """Build the user message for the head-to-head comparison dimension."""
    context_line = f"Context: {context}" if context else f"Analyze based on publicly known information about {product_a} and {product_b}."
    return COMPARISON_DIMENSION["prompt"].format(
        product_a=product_a, product_b=product_b, context_line=context_line,
    )


def build_social_prompt(product: str, context: str | None) -> str:
    """Build the user message for the social summary."""
    context_line = f"Context: {context}" if context else f"Analyze based on publicly known information about {product}."
    return SOCIAL_SUMMARY_PROMPT.format(product=product, context_line=context_line)


async def call_dimension_async(
    client: anthropic.AsyncAnthropic, model: str, skill_text: str, prompt: str,
) -> str:
    """Make a single async API call for one teardown dimension."""
    message = await client.messages.create(
        model=model,
        max_tokens=1024,
        temperature=0.3,
        system=skill_text,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


async def run_dimensions_async(
    client: anthropic.AsyncAnthropic,
    model: str,
    skill_text: str,
    product: str,
    context: str | None,
    dimensions: list[dict],
    label: str = "",
) -> list[tuple[dict, str]]:
    """Run all dimensions concurrently for a single product."""
    prefix = f"  [{label}] " if label else "  "

    async def _run_one(dim: dict) -> tuple[dict, str]:
        prompt = build_dimension_prompt(product, context, dim)
        try:
            content = await call_dimension_async(client, model, skill_text, prompt)
            print(f"{prefix}[{dim['num']}/6] {dim['title']}... done")
            return (dim, content)
        except Exception as e:
            print(f"{prefix}[{dim['num']}/6] {dim['title']}... ERROR: {e}")
            return (dim, f"*Analysis failed: {e}*")

    tasks = [_run_one(dim) for dim in dimensions]
    results = await asyncio.gather(*tasks)
    # Sort by dimension number to preserve order
    return sorted(results, key=lambda r: r[0]["num"])


# ---------------------------------------------------------------------------
# Output formatting — single product
# ---------------------------------------------------------------------------

def format_terminal(product: str, model: str, results: list[tuple[dict, str]]) -> str:
    """Format results for terminal display with box drawing."""
    now = datetime.now().strftime("%B %Y")
    header_text = f"  PRODUCT TEARDOWN: {product}"
    meta_text = f"  Model: {model} · {now}"
    width = max(62, len(header_text) + 4, len(meta_text) + 4)

    lines = []
    lines.append(f"╔{'═' * width}╗")
    lines.append(f"║{header_text:<{width}}║")
    lines.append(f"║{meta_text:<{width}}║")
    lines.append(f"╚{'═' * width}╝")
    lines.append("")

    for dim, content in results:
        title = f"━━━ {dim['num']}. {dim['title']} "
        title += "━" * max(0, width - len(title))
        lines.append(title)
        lines.append("")
        lines.append(content.strip())
        lines.append("")

    footer = "━" * (width + 2)
    lines.append(footer)
    lines.append("Generated by ProductKit · github.com/shahcolate/Product-Kit")
    lines.append("")

    return "\n".join(lines)


def format_markdown(product: str, model: str, results: list[tuple[dict, str]]) -> str:
    """Format results as shareable Markdown."""
    now = datetime.now().strftime("%B %d, %Y")
    lines = []
    lines.append(f"# Product Teardown: {product}")
    lines.append(f"*Model: {model} · {now}*")
    lines.append("")

    for dim, content in results:
        lines.append(f"## {dim['num']}. {dim['title']}")
        lines.append("")
        lines.append(content.strip())
        lines.append("")

    lines.append("---")
    lines.append("*Generated by [ProductKit](https://github.com/shahcolate/Product-Kit)*")
    lines.append("")

    return "\n".join(lines)


def format_social(product: str, social_content: str) -> str:
    """Format social-ready summary for terminal display."""
    width = 62
    lines = []
    lines.append(f"╔{'═' * width}╗")
    lines.append(f"║{'  SOCIAL TEARDOWN: ' + product:<{width}}║")
    lines.append(f"╚{'═' * width}╝")
    lines.append("")
    lines.append(social_content.strip())
    lines.append("")
    lines.append("━" * (width + 2))
    lines.append("Generated by ProductKit · github.com/shahcolate/Product-Kit")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output formatting — comparison (--vs)
# ---------------------------------------------------------------------------

def format_comparison_terminal(
    product_a: str, product_b: str, model: str,
    results_a: list[tuple[dict, str]],
    results_b: list[tuple[dict, str]],
    verdict: str,
) -> str:
    """Format side-by-side comparison for terminal display."""
    now = datetime.now().strftime("%B %Y")
    header_text = f"  PRODUCT COMPARISON: {product_a} vs {product_b}"
    meta_text = f"  Model: {model} · {now}"
    width = max(62, len(header_text) + 4, len(meta_text) + 4)

    lines = []
    lines.append(f"╔{'═' * width}╗")
    lines.append(f"║{header_text:<{width}}║")
    lines.append(f"║{meta_text:<{width}}║")
    lines.append(f"╚{'═' * width}╝")
    lines.append("")

    for (dim_a, content_a), (dim_b, content_b) in zip(results_a, results_b):
        title = f"━━━ {dim_a['num']}. {dim_a['title']} "
        title += "━" * max(0, width - len(title))
        lines.append(title)
        lines.append("")
        lines.append(f"┌─ {product_a}")
        lines.append("")
        lines.append(content_a.strip())
        lines.append("")
        lines.append(f"├─ {product_b}")
        lines.append("")
        lines.append(content_b.strip())
        lines.append("")

    # Head-to-head verdict
    title = f"━━━ 7. HEAD-TO-HEAD VERDICT "
    title += "━" * max(0, width - len(title))
    lines.append(title)
    lines.append("")
    lines.append(verdict.strip())
    lines.append("")

    footer = "━" * (width + 2)
    lines.append(footer)
    lines.append("Generated by ProductKit · github.com/shahcolate/Product-Kit")
    lines.append("")

    return "\n".join(lines)


def format_comparison_markdown(
    product_a: str, product_b: str, model: str,
    results_a: list[tuple[dict, str]],
    results_b: list[tuple[dict, str]],
    verdict: str,
) -> str:
    """Format side-by-side comparison as Markdown."""
    now = datetime.now().strftime("%B %d, %Y")
    lines = []
    lines.append(f"# Product Comparison: {product_a} vs {product_b}")
    lines.append(f"*Model: {model} · {now}*")
    lines.append("")

    for (dim_a, content_a), (dim_b, content_b) in zip(results_a, results_b):
        lines.append(f"## {dim_a['num']}. {dim_a['title']}")
        lines.append("")
        lines.append(f"### {product_a}")
        lines.append("")
        lines.append(content_a.strip())
        lines.append("")
        lines.append(f"### {product_b}")
        lines.append("")
        lines.append(content_b.strip())
        lines.append("")

    lines.append("## 7. HEAD-TO-HEAD VERDICT")
    lines.append("")
    lines.append(verdict.strip())
    lines.append("")

    lines.append("---")
    lines.append("*Generated by [ProductKit](https://github.com/shahcolate/Product-Kit)*")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def run_single(args, client: anthropic.AsyncAnthropic, skill_text: str) -> None:
    """Run a single-product teardown."""
    product = args.product
    print(f"\n🔍 Running teardown: {product}")
    if args.context:
        print(f"   Context: {args.context}")
    print(f"   Model: {args.model}")
    print(f"   Dimensions: {len(DIMENSIONS)}")
    if args.output == "social":
        print(f"   Output: social (thread-ready summary)")
    print()

    # Run all dimensions concurrently
    results = await run_dimensions_async(
        client, args.model, skill_text, product, args.context, DIMENSIONS,
    )
    print()

    # Social output: run one more call to distill
    if args.output == "social":
        print("  Generating social summary...", end=" ", flush=True)
        social_prompt = build_social_prompt(product, args.context)
        # Include the full teardown as context for the social summary
        full_teardown = "\n\n".join(
            f"## {dim['title']}\n{content}" for dim, content in results
        )
        combined_prompt = f"Here is the full teardown you just completed:\n\n{full_teardown}\n\n---\n\n{social_prompt}"
        social_content = await call_dimension_async(
            client, args.model, skill_text, combined_prompt,
        )
        print("done\n")
        output = format_social(product, social_content)
    elif args.output == "markdown":
        output = format_markdown(product, args.model, results)
    else:
        output = format_terminal(product, args.model, results)

    print(output)

    # Save if requested
    if args.save:
        teardowns_dir = repo_root() / "teardowns"
        teardowns_dir.mkdir(exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        slug = slugify(product)
        filename = f"{slug}-{date_str}.md"
        filepath = teardowns_dir / filename

        if args.output == "social":
            md_output = format_social(product, social_content)
        else:
            md_output = format_markdown(product, args.model, results)
        filepath.write_text(md_output)
        print(f"💾 Saved to {filepath}")


async def run_comparison(args, client: anthropic.AsyncAnthropic, skill_text: str) -> None:
    """Run a --vs comparison teardown of two products."""
    product_a = args.product
    product_b = args.vs
    print(f"\n🔍 Running comparison: {product_a} vs {product_b}")
    if args.context:
        print(f"   Context: {args.context}")
    print(f"   Model: {args.model}")
    print(f"   Dimensions: {len(DIMENSIONS)} × 2 products + head-to-head verdict")
    print()

    # Run both products concurrently
    results_a, results_b = await asyncio.gather(
        run_dimensions_async(
            client, args.model, skill_text, product_a, args.context, DIMENSIONS,
            label=product_a,
        ),
        run_dimensions_async(
            client, args.model, skill_text, product_b, args.context, DIMENSIONS,
            label=product_b,
        ),
    )

    # Run head-to-head verdict with both teardowns as context
    print(f"\n  [7/7] HEAD-TO-HEAD VERDICT...", end=" ", flush=True)
    teardown_a = "\n\n".join(f"## {dim['title']}\n{c}" for dim, c in results_a)
    teardown_b = "\n\n".join(f"## {dim['title']}\n{c}" for dim, c in results_b)
    comparison_prompt = build_comparison_prompt(product_a, product_b, args.context)
    combined = (
        f"Full teardown of {product_a}:\n\n{teardown_a}\n\n---\n\n"
        f"Full teardown of {product_b}:\n\n{teardown_b}\n\n---\n\n"
        f"{comparison_prompt}"
    )
    verdict = await call_dimension_async(client, args.model, skill_text, combined)
    print("done\n")

    # Format output
    if args.output == "markdown":
        output = format_comparison_markdown(
            product_a, product_b, args.model, results_a, results_b, verdict,
        )
    else:
        output = format_comparison_terminal(
            product_a, product_b, args.model, results_a, results_b, verdict,
        )

    print(output)

    # Save if requested
    if args.save:
        teardowns_dir = repo_root() / "teardowns"
        teardowns_dir.mkdir(exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        slug_a = slugify(product_a)
        slug_b = slugify(product_b)
        filename = f"{slug_a}-vs-{slug_b}-{date_str}.md"
        filepath = teardowns_dir / filename

        md_output = format_comparison_markdown(
            product_a, product_b, args.model, results_a, results_b, verdict,
        )
        filepath.write_text(md_output)
        print(f"💾 Saved to {filepath}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Product Teardown — run any product through Strategic PM's framework battery"
    )
    parser.add_argument("product", help="Product name to analyze")
    parser.add_argument("--vs", type=str, default=None, help="Compare against a second product (head-to-head mode)")
    parser.add_argument("--context", type=str, default=None, help="One-liner about the product (helps if obscure)")
    parser.add_argument("--model", type=str, default="claude-sonnet-4-6", help="Claude model to use (default: claude-sonnet-4-6)")
    parser.add_argument("--output", choices=["terminal", "markdown", "social"], default="terminal", help="Output format (social = thread-ready summary)")
    parser.add_argument("--save", action="store_true", help="Save output to teardowns/<product-slug>-<date>.md")
    args = parser.parse_args()

    if args.vs and args.output == "social":
        print("ERROR: --output social is not supported with --vs comparison mode.", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.AsyncAnthropic(api_key=api_key)

    # Load Strategic PM skill
    try:
        skill_text = load_skill()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.vs:
        asyncio.run(run_comparison(args, client, skill_text))
    else:
        asyncio.run(run_single(args, client, skill_text))


if __name__ == "__main__":
    main()
