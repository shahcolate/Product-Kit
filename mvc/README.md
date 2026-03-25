# MVC -- Minimal Viable Context for AI Features

**Minimal Viable Context (MVC)** is the smallest set of product decisions an AI agent needs before it can act on behalf of a user. It replaces the traditional PRD with a structured, testable spec written in YAML. [Read the original article.](https://shahai.substack.com/p/the-new-prd)

## Why PRDs fail for AI agents

PRDs assume deterministic software: write the spec, build the thing, verify it matches. AI agents break every part of that. Their outputs are probabilistic. Their failure modes are invisible -- "it works on my prompt" is the new "it works on my machine." A PRD tells you what to build, but an agent also needs to know what it must never do, how much each call can cost, what to do when it fails, and how to detect when it starts drifting silently out of spec. MVC fills that gap. It's the contract between product intent and agent behavior, written in a format that humans can review and test harnesses can enforce.

## The five MVC components

**1. Objective + Non-Goals** -- What the agent does, and explicitly what it doesn't. The non-goals matter more than the goals. They're what prevent the agent from hallucinating scope.

**2. Constraints** -- Hard limits the agent must never exceed: cost ceiling per request, latency budget, compliance requirements, data it must never access. These aren't aspirational targets. They're circuit breakers.

**3. Acceptance Tests** -- Concrete, falsifiable scenarios the agent must handle. Happy path, cold start, edge cases, privacy-constrained users. If you can't write the test, you haven't defined the feature.

**4. Tools and Boundaries** -- What data sources the agent can access, how fresh they need to be, and what happens when they're unavailable. The fallback behavior is part of the spec, not an afterthought.

**5. Canonical Examples** -- Worked input/output pairs that anchor the agent's behavior. These double as your golden eval dataset and prevent drift over time.

## Quick start

```bash
# Copy the blank template into your project
cp templates/mvc-template.yaml my-feature-mvc.yaml

# Fill in the five components
# (see templates/mvc-example-recommendations.yaml for a worked example)

# Run the demo to see MVC-driven testing in action
cd demo
pip install pyyaml
python mvc_test_runner.py
```

The demo validates two mock agents -- GoodAgent (follows the contract) and BadAgent (violates it) -- against a single MVC spec. GoodAgent passes all tests. BadAgent fails on item count, PII leakage, latency, confidence score range, and fallback handling. You can see exactly which contract clauses each agent breaks.

## Repo layout

```
mvc/
  templates/           Blank MVC template + worked examples
  demo/                Test runner, mock agents, sample MVC
  tests/               Contract, behavioral, boundary, drift test specs
  docs/                Onboarding guide, ownership table, solo builder guide
  .github/workflows/   CI for contract tests and weekly drift detection
```

## Worked examples

- [Recommendations](templates/mvc-example-recommendations.yaml) -- Full MVC for an AI-powered e-commerce recommendation feature. Covers all five components plus telemetry, decision records, and versioning.
- [Backend migration](templates/mvc-example-backend-migration.yaml) -- Stripped-down MVC for a payment processing migration. Shows that the framework scales down for purely technical features with no designer and no experience constraints.

## Further reading

- [The New PRD: Minimal Viable Context for AI Features](https://shahai.substack.com/p/the-new-prd)
- [Full article series on Substack](https://shahai.substack.com/)

## Author

Shah Baig -- Georgetown University

- GitHub: [shahcolate](https://github.com/shahcolate)
- LinkedIn: [shahbaig](https://linkedin.com/in/shahbaig)

## License

[MIT](LICENSE)
