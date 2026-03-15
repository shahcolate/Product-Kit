"""
ProductKit shared utilities for CLI tools.

Common helpers used across teardown.py, run_evals.py, and functional tools.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import anthropic


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def repo_root() -> Path:
    """Return the repo root (parent of scripts/)."""
    return Path(__file__).parent.parent


def slugify(name: str) -> str:
    """Convert a name to a filename-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def dated_slug(name: str) -> str:
    """Return a slug with today's date appended."""
    return f"{slugify(name)}-{datetime.now().strftime('%Y-%m-%d')}"


# ---------------------------------------------------------------------------
# Terminal formatting
# ---------------------------------------------------------------------------

def box_header(title: str, subtitle: str = "", width: int = 62) -> str:
    """Return a box-drawn header string."""
    title_line = f"  {title}"
    sub_line = f"  {subtitle}" if subtitle else ""
    width = max(width, len(title_line) + 4, len(sub_line) + 4 if subtitle else 0)
    border_top = "\u2550" * width
    border_bot = "\u2550" * width
    lines = [f"\u2554{border_top}\u2557"]
    lines.append(f"\u2551{title_line:<{width}}\u2551")
    if subtitle:
        lines.append(f"\u2551{sub_line:<{width}}\u2551")
    lines.append(f"\u255a{border_bot}\u255d")
    return "\n".join(lines)


def section_rule(title: str, width: int = 64) -> str:
    """Return a section separator like: ━━━ 1. TITLE ━━━━━━━━━━━"""
    line = f"\u2501\u2501\u2501 {title} "
    line += "\u2501" * max(0, width - len(line))
    return line


def footer_line(width: int = 64) -> str:
    """Return a footer rule."""
    return "\u2501" * width


# ---------------------------------------------------------------------------
# Anthropic client
# ---------------------------------------------------------------------------

def require_api_key() -> str:
    """Return the Anthropic API key or exit with an error."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    return api_key


def make_client() -> anthropic.Anthropic:
    """Create a sync Anthropic client."""
    return anthropic.Anthropic(api_key=require_api_key())


def make_async_client() -> anthropic.AsyncAnthropic:
    """Create an async Anthropic client."""
    return anthropic.AsyncAnthropic(api_key=require_api_key())


# ---------------------------------------------------------------------------
# Common argparse setup
# ---------------------------------------------------------------------------

def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add --model, --output, and --save flags shared across tools."""
    parser.add_argument(
        "--model", type=str, default="claude-sonnet-4-6",
        help="Claude model to use (default: claude-sonnet-4-6)",
    )
    parser.add_argument(
        "--output", choices=["terminal", "markdown"], default="terminal",
        help="Output format",
    )
    parser.add_argument(
        "--save", action="store_true",
        help="Save output to a file",
    )


# ---------------------------------------------------------------------------
# Async API helpers
# ---------------------------------------------------------------------------

async def async_text_call(
    client: anthropic.AsyncAnthropic,
    model: str,
    system: str,
    user_message: str,
    max_tokens: int = 4096,
    temperature: float = 0.3,
) -> str:
    """Make a single async text API call and return the text content."""
    message = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


async def async_vision_call(
    client: anthropic.AsyncAnthropic,
    model: str,
    system: str,
    user_text: str,
    image_paths: list[Path],
    max_tokens: int = 4096,
    temperature: float = 0.3,
) -> str:
    """Make an async vision API call with one or more images."""
    content: list[dict] = []
    for img_path in image_paths:
        data = img_path.read_bytes()
        b64 = base64.b64encode(data).decode("utf-8")
        suffix = img_path.suffix.lower()
        media_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }.get(suffix, "image/png")
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": b64},
        })
    content.append({"type": "text", "text": user_text})

    message = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": content}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Save helper
# ---------------------------------------------------------------------------

def save_output(content: str, directory: str, filename: str) -> Path:
    """Save content to repo_root()/directory/filename and return the path."""
    out_dir = repo_root() / directory
    out_dir.mkdir(parents=True, exist_ok=True)
    filepath = out_dir / filename
    filepath.write_text(content)
    return filepath
