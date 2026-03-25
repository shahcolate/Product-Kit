#!/usr/bin/env python3
"""
MVC Test Runner — validates agent implementations against an MVC spec.

Usage:
    python mvc_test_runner.py [--mvc context/mvc.yaml]

The runner loads the MVC file and runs each registered agent through:
  1. Contract tests   — does the output match the expected format?
  2. Behavioral tests — does the agent handle key scenarios correctly?
  3. Boundary tests   — does the agent respect hard limits?

Exit code 0 = all tests pass. Non-zero = failures detected.
"""

import argparse
import sys
import time
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_mvc(path: str) -> dict:
    """Load and return the MVC YAML file as a dict."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def print_result(test_name: str, passed: bool, detail: str = ""):
    status = "PASS" if passed else "FAIL"
    icon = "+" if passed else "-"
    line = f"  [{icon}] {test_name}"
    if detail:
        line += f" — {detail}"
    print(line)


# ---------------------------------------------------------------------------
# Test suites
# ---------------------------------------------------------------------------

def run_contract_tests(agent, mvc: dict) -> list[bool]:
    """Verify the agent's output matches the MVC output_format contract."""
    results = []

    # Build a minimal input from context_sources
    sample_input = {
        "user_id": "test-user-001",
        "page_context": "home",
    }

    output = agent.run(sample_input)

    # Test: output is a list
    is_list = isinstance(output, list)
    print_result("Output is a list", is_list)
    results.append(is_list)

    # Test: output has exactly the expected number of items
    expected_count = 5  # from MVC output_format
    correct_count = is_list and len(output) == expected_count
    print_result(
        f"Output contains exactly {expected_count} items",
        correct_count,
        f"got {len(output) if is_list else 'N/A'}",
    )
    results.append(correct_count)

    # Test: each item has required keys
    required_keys = {"product_id", "product_name", "reason", "confidence_score"}
    if is_list:
        for i, item in enumerate(output):
            has_keys = required_keys.issubset(item.keys()) if isinstance(item, dict) else False
            print_result(f"Item {i} has required keys", has_keys)
            results.append(has_keys)

    # Test: confidence_score in valid range
    if is_list:
        for i, item in enumerate(output):
            if isinstance(item, dict) and "confidence_score" in item:
                score = item["confidence_score"]
                in_range = isinstance(score, (int, float)) and 0.0 <= score <= 1.0
                print_result(f"Item {i} confidence_score in [0, 1]", in_range, f"got {score}")
                results.append(in_range)

    return results


def run_boundary_tests(agent, mvc: dict) -> list[bool]:
    """Verify the agent respects boundaries defined in the MVC."""
    results = []
    boundaries = mvc.get("boundaries", {})

    sample_input = {
        "user_id": "test-user-001",
        "page_context": "home",
    }

    # Test: latency budget
    latency_budget_ms = 200  # from MVC
    start = time.perf_counter()
    _ = agent.run(sample_input)
    elapsed_ms = (time.perf_counter() - start) * 1000
    within_budget = elapsed_ms < latency_budget_ms
    print_result(
        f"Latency under {latency_budget_ms}ms",
        within_budget,
        f"{elapsed_ms:.1f}ms",
    )
    results.append(within_budget)

    # Test: no PII in output
    output = agent.run(sample_input)
    pii_fields = {"email", "address", "phone", "ssn", "name"}
    if isinstance(output, list):
        for i, item in enumerate(output):
            if isinstance(item, dict):
                leaked = pii_fields.intersection(item.keys())
                no_pii = len(leaked) == 0
                print_result(f"Item {i} contains no PII fields", no_pii, f"leaked: {leaked}" if leaked else "")
                results.append(no_pii)

    return results


def run_behavioral_tests(agent, mvc: dict) -> list[bool]:
    """Verify agent handles key user scenarios."""
    results = []

    # Happy path — normal user with history
    output = agent.run({"user_id": "returning-user", "page_context": "home"})
    happy = isinstance(output, list) and len(output) > 0
    print_result("Happy path returns recommendations", happy)
    results.append(happy)

    # Cold start — new user with no history
    output = agent.run({"user_id": "brand-new-user", "page_context": "home"})
    cold = isinstance(output, list) and len(output) > 0
    print_result("Cold-start user still gets recommendations", cold)
    results.append(cold)

    # Fallback — agent receives malformed input
    output = agent.run({})
    fallback = isinstance(output, list)
    print_result("Malformed input triggers fallback (returns list)", fallback)
    results.append(fallback)

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="MVC Test Runner")
    parser.add_argument("--mvc", default="context/mvc.yaml", help="Path to MVC YAML file")
    args = parser.parse_args()

    mvc_path = Path(args.mvc)
    if not mvc_path.exists():
        print(f"Error: MVC file not found at {mvc_path}")
        sys.exit(1)

    mvc = load_mvc(str(mvc_path))
    print(f"Loaded MVC: {mvc.get('feature_name', 'unknown')} v{mvc.get('version', '?')}\n")

    # Import agents
    sys.path.insert(0, str(Path(__file__).parent))
    from agent.mock_agent import GoodAgent, BadAgent

    all_results = []

    for agent_cls in [GoodAgent, BadAgent]:
        agent = agent_cls()
        print(f"{'=' * 60}")
        print(f"Testing: {agent.__class__.__name__}")
        print(f"{'=' * 60}")

        print("\n--- Contract Tests ---")
        all_results.extend(run_contract_tests(agent, mvc))

        print("\n--- Boundary Tests ---")
        all_results.extend(run_boundary_tests(agent, mvc))

        print("\n--- Behavioral Tests ---")
        all_results.extend(run_behavioral_tests(agent, mvc))

        print()

    passed = sum(all_results)
    total = len(all_results)
    failed = total - passed
    print(f"{'=' * 60}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    print(f"{'=' * 60}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
