#!/usr/bin/env python3
"""
ProductKit AI Product Teardown Tool
Runs any product through Strategic PM's full framework battery and produces a structured report.

Usage:
  python scripts/teardown.py "Notion"
  python scripts/teardown.py "Notion" --context "workspace productivity tool for teams"
  python scripts/teardown.py "Linear" --model claude-sonnet-4-6
  python scripts/teardown.py "Slack" --output markdown --save

Requires: ANTHROPIC_API_KEY env var, pip install anthropic
"""

import argparse
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


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------

def build_dimension_prompt(product: str, context: str | None, dimension: dict) -> str:
    """Build the user message for a single dimension."""
    context_line = f"Context: {context}" if context else f"Analyze based on publicly known information about {product}."
    return dimension["prompt"].format(product=product, context_line=context_line)


def call_dimension(client: anthropic.Anthropic, model: str, skill_text: str, prompt: str) -> str:
    """Make a single API call for one teardown dimension."""
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        temperature=0.3,
        system=skill_text,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Output formatting
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Product Teardown — run any product through Strategic PM's framework battery"
    )
    parser.add_argument("product", help="Product name to analyze")
    parser.add_argument("--context", type=str, default=None, help="One-liner about the product (helps if obscure)")
    parser.add_argument("--model", type=str, default="claude-sonnet-4-6", help="Claude model to use (default: claude-sonnet-4-6)")
    parser.add_argument("--output", choices=["terminal", "markdown"], default="terminal", help="Output format")
    parser.add_argument("--save", action="store_true", help="Save output to teardowns/<product-slug>-<date>.md")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Load Strategic PM skill
    try:
        skill_text = load_skill()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    product = args.product
    print(f"\n🔍 Running teardown: {product}")
    if args.context:
        print(f"   Context: {args.context}")
    print(f"   Model: {args.model}")
    print(f"   Dimensions: {len(DIMENSIONS)}")
    print()

    # Run each dimension
    results: list[tuple[dict, str]] = []
    for dim in DIMENSIONS:
        print(f"  [{dim['num']}/6] {dim['title']}...", end=" ", flush=True)
        prompt = build_dimension_prompt(product, args.context, dim)
        try:
            content = call_dimension(client, args.model, skill_text, prompt)
            results.append((dim, content))
            print("done")
        except Exception as e:
            print(f"ERROR: {e}")
            results.append((dim, f"*Analysis failed: {e}*"))

    print()

    # Format output
    if args.output == "markdown":
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

        # Always save as markdown when saving to file
        md_output = format_markdown(product, args.model, results)
        filepath.write_text(md_output)
        print(f"💾 Saved to {filepath}")


if __name__ == "__main__":
    main()
