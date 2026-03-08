#!/usr/bin/env python3
"""
ProductKit Behavioral Eval Harness
Two-call LLM-as-judge: subject call (skill as system prompt) + grader call (criterion scoring)

Usage:
  python scripts/run_evals.py
  python scripts/run_evals.py --plugin strategic-pm
  python scripts/run_evals.py --output json
  python scripts/run_evals.py --model claude-haiku-4-5-20251001

Requires: ANTHROPIC_API_KEY env var, pip install anthropic
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import anthropic


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Criterion:
    id: str
    description: str
    should_pass: bool
    weight: int


@dataclass
class EvalCase:
    id: str
    name: str
    category: str
    user_message: str
    context: Optional[str]
    criteria: list[Criterion]


@dataclass
class CriterionResult:
    criterion_id: str
    passed: bool
    reasoning: str
    weight: int


@dataclass
class CaseResult:
    case_id: str
    case_name: str
    category: str
    subject_response: str
    criterion_results: list[CriterionResult]
    weighted_score: float
    passed: bool


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def repo_root() -> Path:
    """Return the repo root (parent of scripts/)."""
    return Path(__file__).parent.parent


def load_cases(plugin: str) -> tuple[list[EvalCase], dict]:
    """Load eval cases from evals/<plugin>/cases.json."""
    cases_path = repo_root() / "evals" / plugin / "cases.json"
    if not cases_path.exists():
        raise FileNotFoundError(f"No cases.json found at {cases_path}")

    with open(cases_path) as f:
        data = json.load(f)

    cases = []
    for c in data["cases"]:
        criteria = [
            Criterion(
                id=cr["id"],
                description=cr["description"],
                should_pass=cr["should_pass"],
                weight=cr["weight"],
            )
            for cr in c["criteria"]
        ]
        cases.append(
            EvalCase(
                id=c["id"],
                name=c["name"],
                category=c["category"],
                user_message=c["user_message"],
                context=c.get("context"),
                criteria=criteria,
            )
        )

    return cases, data


def load_skill(plugin: str) -> str:
    """Load skill text from plugins/<plugin>/skills/<plugin>/SKILL.md."""
    skill_path = repo_root() / "plugins" / plugin / "skills" / plugin / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"No SKILL.md found at {skill_path}")
    return skill_path.read_text()


def load_plugin_version(plugin: str) -> Optional[str]:
    """Load plugin version from plugin.json, if present."""
    plugin_json_path = repo_root() / "plugins" / plugin / ".claude-plugin" / "plugin.json"
    if not plugin_json_path.exists():
        return None
    with open(plugin_json_path) as f:
        data = json.load(f)
    return data.get("version")


def check_version_drift(plugin: str, cases_data: dict) -> None:
    """Warn if cases.json version doesn't match plugin.json version."""
    cases_version = cases_data.get("version")
    plugin_version = load_plugin_version(plugin)
    if cases_version and plugin_version and cases_version != plugin_version:
        print(
            f"  ⚠️  VERSION DRIFT WARNING: cases.json version={cases_version} "
            f"but plugin.json version={plugin_version}. "
            f"Consider updating evals when bumping plugin version."
        )


# ---------------------------------------------------------------------------
# Subject call
# ---------------------------------------------------------------------------

def call_subject(client: anthropic.Anthropic, model: str, skill_text: str, case: EvalCase) -> str:
    """Call Claude with the skill as system prompt and the case message as user turn."""
    user_content = case.user_message
    if case.context:
        user_content = f"{case.context}\n\n{user_content}"

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        temperature=0,
        system=skill_text,
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Grader call
# ---------------------------------------------------------------------------

def build_grader_prompt(case: EvalCase, subject_response: str) -> str:
    """Build the grader prompt with per-criterion pass/fail instructions."""
    criteria_lines = []
    for c in case.criteria:
        if c.should_pass:
            direction = "This criterion PASSES if the behavior IS present in the response."
        else:
            direction = "This criterion PASSES if the behavior is NOT present in the response."
        criteria_lines.append(
            f'- id: "{c.id}"\n  description: "{c.description}"\n  {direction}'
        )

    criteria_block = "\n\n".join(criteria_lines)

    user_context = case.user_message
    if case.context:
        user_context = f"[CONTEXT PROVIDED TO MODEL]\n{case.context}\n\n[USER MESSAGE]\n{case.user_message}"

    return f"""You are evaluating a Claude model's response to a user message. The model was loaded with a specific behavioral skill. Your job is to assess whether the response honors specific behavioral criteria.

---

ORIGINAL USER INPUT:
{user_context}

---

MODEL RESPONSE:
{subject_response}

---

CRITERIA TO EVALUATE:

{criteria_block}

---

INSTRUCTIONS:
- Evaluate each criterion independently based only on the model response above.
- Be precise and evidence-based. Quote or reference specific parts of the response in your reasoning.
- Each criterion has clear pass/fail logic stated above — follow it exactly.
- Return ONLY raw JSON. No markdown, no code fences, no explanation outside the JSON.

OUTPUT FORMAT:
{{"criteria": [{{"id": "...", "passed": true/false, "reasoning": "..."}}]}}"""


def call_grader(client: anthropic.Anthropic, model: str, grader_prompt: str, case: EvalCase) -> list[CriterionResult]:
    """Call the grader and parse per-criterion results."""
    system = "You are an expert evaluator of AI behavioral compliance. Be precise and evidence-based."

    def _parse_grader_json(text: str) -> list[CriterionResult]:
        # Strip markdown fences if present
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        text = text.strip()
        data = json.loads(text)
        results = []
        for item in data["criteria"]:
            results.append(
                CriterionResult(
                    criterion_id=item["id"],
                    passed=item["passed"],
                    reasoning=item["reasoning"],
                    weight=next(c.weight for c in case.criteria if c.id == item["id"]),
                )
            )
        return results

    # First attempt
    message = client.messages.create(
        model=model,
        max_tokens=2048,
        temperature=0,
        system=system,
        messages=[{"role": "user", "content": grader_prompt}],
    )
    raw = message.content[0].text

    try:
        return _parse_grader_json(raw)
    except (json.JSONDecodeError, KeyError):
        # Retry once with explicit instruction
        retry_messages = [
            {"role": "user", "content": grader_prompt},
            {"role": "assistant", "content": raw},
            {"role": "user", "content": 'Return only raw JSON matching the format {"criteria": [{"id": "...", "passed": true/false, "reasoning": "..."}]}. No markdown, no code fences.'},
        ]
        retry_message = client.messages.create(
            model=model,
            max_tokens=2048,
            temperature=0,
            system=system,
            messages=retry_messages,
        )
        raw2 = retry_message.content[0].text
        try:
            return _parse_grader_json(raw2)
        except (json.JSONDecodeError, KeyError):
            # Second failure — mark all criteria as failed with error note
            return [
                CriterionResult(
                    criterion_id=c.id,
                    passed=False,
                    reasoning="grader parse error",
                    weight=c.weight,
                )
                for c in case.criteria
            ]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

PASS_THRESHOLD = 0.75


def score_case(case: EvalCase, criterion_results: list[CriterionResult], subject_response: str) -> CaseResult:
    """Compute weighted score and determine pass/fail for a case."""
    total_weight = sum(r.weight for r in criterion_results)
    passing_weight = sum(r.weight for r in criterion_results if r.passed)
    weighted_score = passing_weight / total_weight if total_weight > 0 else 0.0
    passed = weighted_score >= PASS_THRESHOLD

    return CaseResult(
        case_id=case.id,
        case_name=case.name,
        category=case.category,
        subject_response=subject_response,
        criterion_results=criterion_results,
        weighted_score=weighted_score,
        passed=passed,
    )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_terminal_results(plugin: str, results: list[CaseResult], model: str) -> None:
    """Print formatted terminal output."""
    print()
    print("=" * 60)
    print(f"BEHAVIORAL EVAL RESULTS — {plugin}")
    print(f"Model: {model} | Cases: {len(results)}")
    print("=" * 60)
    print()

    for result in results:
        total_weight = sum(r.weight for r in result.criterion_results)
        passing_weight = sum(r.weight for r in result.criterion_results if r.passed)
        status = "PASS" if result.passed else "FAIL"
        pct = int(result.weighted_score * 100)
        print(f"[{status}] {result.case_id} · {result.case_name:<44} {passing_weight}/{total_weight} ({pct}%)")
        for cr in result.criterion_results:
            symbol = "✓" if cr.passed else "✗"
            print(f"  {symbol} {cr.criterion_id} (w:{cr.weight}) {cr.reasoning[:80]}")
        print()

    passing = sum(1 for r in results if r.passed)
    total = len(results)
    pct = int(passing / total * 100) if total > 0 else 0
    total_w = sum(r.weighted_score * sum(c.weight for c in []) for r in results)
    # Weighted across all cases
    all_cr = [cr for r in results for cr in r.criterion_results]
    all_w = sum(c.weight for c in all_cr)
    pass_w = sum(c.weight for c in all_cr if c.passed)
    overall_pct = int(pass_w / all_w * 100) if all_w > 0 else 0
    print(f"PLUGIN SUMMARY: {plugin:<30} {passing}/{total} passing ({overall_pct}% weighted)")
    print()


def print_json_results(results_by_plugin: dict[str, list[CaseResult]]) -> None:
    """Print JSON output."""
    output = {}
    for plugin, results in results_by_plugin.items():
        output[plugin] = [
            {
                "case_id": r.case_id,
                "case_name": r.case_name,
                "category": r.category,
                "passed": r.passed,
                "weighted_score": round(r.weighted_score, 4),
                "criteria": [
                    {
                        "id": cr.criterion_id,
                        "passed": cr.passed,
                        "weight": cr.weight,
                        "reasoning": cr.reasoning,
                    }
                    for cr in r.criterion_results
                ],
            }
            for r in results
        ]
    print(json.dumps(output, indent=2))


def write_github_summary(results_by_plugin: dict[str, list[CaseResult]]) -> None:
    """Write a markdown summary to $GITHUB_STEP_SUMMARY if running in Actions."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    lines = ["# Behavioral Eval Results\n"]

    for plugin, results in results_by_plugin.items():
        passing = sum(1 for r in results if r.passed)
        total = len(results)
        lines.append(f"## {plugin} — {passing}/{total} cases passing\n")
        lines.append("| Case | Score | Status |")
        lines.append("|---|---|---|")
        for r in results:
            pct = int(r.weighted_score * 100)
            status = "✅ PASS" if r.passed else "❌ FAIL"
            lines.append(f"| {r.case_id} · {r.case_name} | {pct}% | {status} |")
        lines.append("")

        # Overall
        all_cr = [cr for r in results for cr in r.criterion_results]
        all_w = sum(c.weight for c in all_cr)
        pass_w = sum(c.weight for c in all_cr if c.passed)
        overall_pct = int(pass_w / all_w * 100) if all_w > 0 else 0
        lines.append(f"**Overall weighted score: {overall_pct}%**\n")

    with open(summary_path, "w") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------------------
# Plugin discovery
# ---------------------------------------------------------------------------

def discover_plugins() -> list[str]:
    """Discover plugins by listing dirs under evals/ that contain cases.json."""
    evals_dir = repo_root() / "evals"
    if not evals_dir.exists():
        return []
    return sorted(
        d.name
        for d in evals_dir.iterdir()
        if d.is_dir() and (d / "cases.json").exists()
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_plugin(client: anthropic.Anthropic, plugin: str, model: str, output_mode: str) -> list[CaseResult]:
    """Run all eval cases for a single plugin."""
    cases, cases_data = load_cases(plugin)
    skill_text = load_skill(plugin)
    check_version_drift(plugin, cases_data)

    results = []
    for case in cases:
        if output_mode == "terminal":
            print(f"  Running {case.id} — {case.name}...")
        subject_response = call_subject(client, model, skill_text, case)
        grader_prompt = build_grader_prompt(case, subject_response)
        criterion_results = call_grader(client, model, grader_prompt, case)
        result = score_case(case, criterion_results, subject_response)
        results.append(result)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="ProductKit Behavioral Eval Harness")
    parser.add_argument("--plugin", type=str, default=None, help="Plugin name to evaluate (default: all)")
    parser.add_argument("--output", choices=["terminal", "json"], default="terminal", help="Output format")
    parser.add_argument("--model", type=str, default="claude-opus-4-6", help="Claude model to use")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Discover plugins
    if args.plugin:
        plugins = [args.plugin]
    else:
        plugins = discover_plugins()
        if not plugins:
            print("No eval cases found under evals/. Nothing to run.", file=sys.stderr)
            sys.exit(0)

    results_by_plugin: dict[str, list[CaseResult]] = {}

    for plugin in plugins:
        if args.output == "terminal":
            print(f"\nLoading plugin: {plugin}")
        try:
            results = run_plugin(client, plugin, args.model, args.output)
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        results_by_plugin[plugin] = results

        if args.output == "terminal":
            print_terminal_results(plugin, results, args.model)

    if args.output == "json":
        print_json_results(results_by_plugin)

    write_github_summary(results_by_plugin)

    # Final summary + exit code
    all_results = [r for results in results_by_plugin.values() for r in results]
    total = len(all_results)
    passing = sum(1 for r in all_results if r.passed)
    any_failed = passing < total

    if args.output == "terminal":
        print("=" * 60)
        if any_failed:
            print(f"OVERALL: {passing}/{total} cases passing — Exit 1")
        else:
            print(f"OVERALL: {total}/{total} cases passing — Exit 0")
        print("=" * 60)
        print()

    sys.exit(1 if any_failed else 0)


if __name__ == "__main__":
    main()
