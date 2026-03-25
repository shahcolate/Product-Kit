# Getting Started -- 4-Week MVC Onboarding

Adopt MVC incrementally. One section per week. By week 4 you have a testable spec running in CI.

## Week 1: Objective + Non-Goals

Write only the `objective` section of your MVC file.

1. Copy `templates/mvc-template.yaml` into your project.
2. Write a one-sentence objective. Be specific: include a number and a timeframe.
3. List 3-5 non-goals. These matter more than you think -- they prevent the agent from hallucinating scope.
4. Get one stakeholder to review. Ask: "Is there anything on the non-goals list that should actually be a goal?"

Bad: "Improve recommendations."
Good: "Surface 5 relevant items per session to increase add-to-cart by 15% in 90 days."

Deliverable: MVC file with `objective` section complete.

## Week 2: Acceptance Tests

Write 3 acceptance tests. Start simple.

1. **Happy path** -- the primary use case works as intended.
2. **Cold start** -- what happens when the agent has no data to work with.
3. **Edge case** -- pick the scariest scenario (privacy constraint, malformed input, empty catalog).

Use given/when/then format. Each test must be falsifiable -- a pass or fail, not a judgment call.

Deliverable: 3 test cases in the `acceptance_tests` section.

## Week 3: Constraints + Tools and Boundaries

Add the guardrails.

1. List compliance requirements (GDPR, CCPA, PCI, SOC 2 -- whatever applies).
2. Set performance limits: latency SLA, cost ceiling, throughput floor.
3. Map allowed data sources with freshness requirements.
4. List forbidden data sources with reasons. This prevents future creep.
5. Define fallback behavior. Every agent fails eventually. Decide what happens before it does.

Review with engineering: Are these data sources actually available at the freshness you need?

Deliverable: `constraints` and `tools_and_boundaries` sections complete.

## Week 4: Run It

Wire up the MVC to a real (or mock) agent and compare outputs to your tests.

1. Implement or mock the agent to match `objective.statement`.
2. Run the test runner: `python demo/mvc_test_runner.py --mvc your-mvc.yaml`
3. Compare agent output to each acceptance test. Fix the spec or the agent -- usually both need adjustment.
4. Copy `.github/workflows/mvc-tests.yml` into your repo. Tests run on every PR.
5. Add canonical examples to anchor the agent's behavior and prevent drift.

Deliverable: Passing CI pipeline. MVC is now a living document.

## After Week 4

- Add drift detection (weekly eval against golden dataset).
- Update the MVC when scope changes. It's a living document, not a launch artifact.
- Use the MVC as the starting point for sprint planning and design reviews.
- Record architectural decisions in `decision_records` so future readers know why the spec looks the way it does.
