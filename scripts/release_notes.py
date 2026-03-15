#!/usr/bin/env python3
from __future__ import annotations

"""
ProductKit Release Notes Generator
Reads git log, classifies changes, and generates polished audience-appropriate release notes.
Produces internal (eng-facing) and external (customer-facing) versions.

Usage:
  python scripts/release_notes.py --repo . --since v2.3.0 --audience external
  python scripts/release_notes.py --repo . --range v2.3.0..v2.4.0 --output markdown --save
  python scripts/release_notes.py --since "2026-03-01" --product-name "ProductKit"

Requires: ANTHROPIC_API_KEY env var, pip install anthropic, git CLI
"""

import argparse
import asyncio
import subprocess
import sys
from pathlib import Path

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
# Git log extraction
# ---------------------------------------------------------------------------

def get_git_log(repo: str, since: str | None, range_spec: str | None) -> list[dict]:
    """Extract structured commit list from git log."""
    # Build git log command
    fmt = "%H%n%h%n%an%n%s%n%b%n---END---"
    cmd = ["git", "-C", repo, "log", f"--pretty=format:{fmt}"]

    if range_spec:
        cmd.append(range_spec)
    elif since:
        # Try as tag first, then as date
        tag_check = subprocess.run(
            ["git", "-C", repo, "rev-parse", f"{since}^{{}}"],
            capture_output=True, text=True,
        )
        if tag_check.returncode == 0:
            cmd.append(f"{since}..HEAD")
        else:
            cmd.extend(["--since", since])
    else:
        # Default: last 50 commits
        cmd.extend(["-n", "50"])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: git log failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    raw = result.stdout.strip()
    if not raw:
        print("ERROR: No commits found in the specified range.", file=sys.stderr)
        sys.exit(1)

    commits = []
    for block in raw.split("---END---"):
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        if len(lines) < 4:
            continue
        commits.append({
            "hash": lines[0],
            "short_hash": lines[1],
            "author": lines[2],
            "subject": lines[3],
            "body": "\n".join(lines[4:]).strip(),
        })

    return commits


def get_diff_stats(repo: str, since: str | None, range_spec: str | None) -> str:
    """Get diffstat summary for the range."""
    cmd = ["git", "-C", repo, "diff", "--stat"]
    if range_spec:
        cmd.append(range_spec)
    elif since:
        tag_check = subprocess.run(
            ["git", "-C", repo, "rev-parse", f"{since}^{{}}"],
            capture_output=True, text=True,
        )
        if tag_check.returncode == 0:
            cmd.append(f"{since}..HEAD")
        else:
            # Fall back to empty — diffstat with dates is tricky
            return ""
    else:
        cmd.append("HEAD~50..HEAD")

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


# ---------------------------------------------------------------------------
# AI classification and generation
# ---------------------------------------------------------------------------

CLASSIFY_PROMPT = """You are a release notes writer. Classify and rewrite these git commits for release notes.

COMMITS:
{commits_block}

For each commit, return:
- **Category**: one of: Feature, Improvement, Bug Fix, Performance, Documentation, Infrastructure, Breaking Change
- **Internal summary** (eng-facing): technical, references specific components, keeps jargon
- **External summary** (customer-facing): benefit-focused, no internal jargon, describes user impact
- **Impact score** (1-5): how much does this matter to users? 5 = major new capability, 1 = internal cleanup

Format as a structured list. Group related commits together when they're part of the same logical change.
Skip merge commits and trivial changes (formatting, typos) — note them as "Skipped: N trivial changes" at the end."""

ASSEMBLE_INTERNAL_PROMPT = """You are writing **internal release notes** for the engineering team.

PRODUCT: {product_name}
CLASSIFIED CHANGES:
{classified}

DIFF STATS:
{diff_stats}

Write release notes with:
1. **Summary** (2-3 sentences) — what shipped and why it matters
2. **Changes by category** — group by Feature, Improvement, Bug Fix, etc. Use bullet points.
3. **Breaking changes** (if any) — call out explicitly with migration notes
4. **Stats** — files changed, commits included
5. **Contributors** — list authors

Keep it technical. Reference specific files, functions, and systems. Engineers should know exactly what changed."""

ASSEMBLE_EXTERNAL_PROMPT = """You are writing **customer-facing release notes** for a product update.

PRODUCT: {product_name}
CLASSIFIED CHANGES:
{classified}

Write release notes with:
1. **Headline** — one sentence capturing the most exciting change
2. **What's new** — feature additions, benefit-focused language
3. **What's improved** — enhancements to existing functionality
4. **What's fixed** — bug fixes, described by the user-facing symptom that's now resolved
5. **Coming soon** (optional) — only if there are clear signals in the commits

Rules:
- No commit hashes, file paths, or internal jargon
- Lead each item with the user benefit, not the technical change
- Skip infrastructure/internal changes entirely
- Keep it scannable — short bullets, bold key phrases"""


async def classify_commits(client, model: str, commits: list[dict]) -> str:
    """Classify commits by category and rewrite for audiences."""
    commits_block = "\n".join(
        f"- [{c['short_hash']}] {c['subject']}" + (f"\n  {c['body'][:200]}" if c['body'] else "")
        for c in commits
    )
    print("  Classifying commits...", end=" ", flush=True)
    result = await async_text_call(
        client, model,
        "You are an expert release notes writer.",
        CLASSIFY_PROMPT.format(commits_block=commits_block),
    )
    print("done")
    return result


async def assemble_notes(
    client, model: str, product_name: str, classified: str, diff_stats: str, audience: str,
) -> dict[str, str]:
    """Assemble final release notes for requested audiences."""
    results = {}

    async def _internal():
        print("  Writing internal notes...", end=" ", flush=True)
        r = await async_text_call(
            client, model,
            "You are a technical writer for engineering teams.",
            ASSEMBLE_INTERNAL_PROMPT.format(
                product_name=product_name, classified=classified, diff_stats=diff_stats,
            ),
        )
        print("done")
        return r

    async def _external():
        print("  Writing external notes...", end=" ", flush=True)
        r = await async_text_call(
            client, model,
            "You are a product marketer writing customer-facing updates.",
            ASSEMBLE_EXTERNAL_PROMPT.format(
                product_name=product_name, classified=classified,
            ),
        )
        print("done")
        return r

    if audience == "both":
        internal, external = await asyncio.gather(_internal(), _external())
        results["internal"] = internal
        results["external"] = external
    elif audience == "internal":
        results["internal"] = await _internal()
    else:
        results["external"] = await _external()

    return results


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_terminal(product_name: str, model: str, num_commits: int, notes: dict[str, str]) -> str:
    """Format release notes for terminal display."""
    lines = []
    lines.append(box_header(
        f"RELEASE NOTES: {product_name}",
        f"Commits: {num_commits} | Model: {model}",
    ))
    lines.append("")

    for audience, content in notes.items():
        lines.append(section_rule(f"{audience.upper()} RELEASE NOTES"))
        lines.append("")
        lines.append(content.strip())
        lines.append("")

    lines.append(footer_line())
    lines.append("Generated by ProductKit · github.com/shahcolate/Product-Kit")
    lines.append("")
    return "\n".join(lines)


def format_markdown(product_name: str, model: str, num_commits: int, notes: dict[str, str]) -> str:
    """Format release notes as Markdown."""
    from datetime import datetime
    now = datetime.now().strftime("%B %d, %Y")
    lines = []
    lines.append(f"# Release Notes: {product_name}")
    lines.append(f"*{num_commits} commits | Model: {model} | {now}*")
    lines.append("")

    for audience, content in notes.items():
        if len(notes) > 1:
            lines.append(f"## {audience.title()} Release Notes")
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
        description="Release Notes Generator — AI-powered release notes from git history"
    )
    parser.add_argument("--repo", type=str, default=".",
                        help="Path to git repository (default: current directory)")
    parser.add_argument("--since", type=str, default=None,
                        help="Tag or date to start from (e.g., v2.3.0 or 2026-03-01)")
    parser.add_argument("--range", type=str, default=None,
                        help="Git range (e.g., v2.3.0..v2.4.0)")
    parser.add_argument("--audience", choices=["internal", "external", "both"], default="both",
                        help="Target audience (default: both)")
    parser.add_argument("--product-name", type=str, default=None,
                        help="Product name for the release notes header")
    add_common_args(parser)
    args = parser.parse_args()

    require_api_key()

    repo = args.repo
    product_name = args.product_name or Path(repo).resolve().name

    # Extract commits
    print(f"\nExtracting git log from {repo}...")
    commits = get_git_log(repo, args.since, args.range)
    print(f"  {len(commits)} commits found")

    diff_stats = get_diff_stats(repo, args.since, args.range)

    # Run AI pipeline
    client = make_async_client()

    async def _run():
        classified = await classify_commits(client, args.model, commits)
        notes = await assemble_notes(
            client, args.model, product_name, classified, diff_stats, args.audience,
        )
        return notes

    print()
    notes = asyncio.run(_run())
    print()

    # Format output
    if args.output == "markdown":
        output = format_markdown(product_name, args.model, len(commits), notes)
    else:
        output = format_terminal(product_name, args.model, len(commits), notes)

    print(output)

    # Save if requested
    if args.save:
        slug = dated_slug(f"{product_name}-release-notes")
        md_output = format_markdown(product_name, args.model, len(commits), notes)
        filepath = save_output(md_output, "release-notes", f"{slug}.md")
        print(f"Saved to {filepath}")


if __name__ == "__main__":
    main()
