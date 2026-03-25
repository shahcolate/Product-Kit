# MVC Demo

Validates two mock agents against a single MVC spec. GoodAgent follows the contract. BadAgent violates it. The test runner shows exactly which clauses break.

## Prerequisites

- Python 3.9+
- PyYAML: `pip install pyyaml`

## Run it

```bash
cd productkit/demo
python mvc_test_runner.py
```

Point at a different MVC file:

```bash
python mvc_test_runner.py --mvc /path/to/your/mvc.yaml
```

## What happens

The runner loads `context/mvc.yaml` and runs each agent through three test suites:

1. **Contract tests** -- Does the output match the MVC output format? Right number of items, required keys, valid score ranges, no PII leakage.
2. **Boundary tests** -- Does the agent stay within limits? Latency budget, no forbidden data in response.
3. **Behavioral tests** -- Does the agent handle key scenarios? Happy path, cold start, malformed input.

GoodAgent passes all tests. BadAgent fails on: item count (3 instead of 5), confidence score range (1.5, -0.2), PII leakage (email field), latency (>200ms), and no fallback on bad input.

## Files

```
demo/
  mvc_test_runner.py     Test runner
  agent/mock_agent.py    GoodAgent + BadAgent implementations
  context/mvc.yaml       MVC spec under test
```

## Further reading

- [The New PRD: Minimal Viable Context for AI Features](https://shahai.substack.com/p/the-new-prd)
- [ProductKit repo](https://github.com/shahcolate/Product-Kit)
- [Full article series](https://shahai.substack.com/)
