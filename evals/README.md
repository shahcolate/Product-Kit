# ProductKit Behavioral Eval Harness

## What This Is

A **LLM-as-judge** behavioral verification system for ProductKit plugins. Not syntax checking — actual behavioral testing.

The existing CI (`validate.yml`) proves plugin files parse and exist. This eval harness proves that loading a skill *actually changes Claude's behavior* in the ways the skill claims to. Two different problems; two different systems.

---

## The Problem It Solves

A plugin's `SKILL.md` might say "always run the Reverse Brief protocol before writing a PRD." The validate workflow can't test that. It only knows the file exists. This harness sends a real message to Claude with the skill loaded and judges whether Claude actually ran the Reverse Brief.

**What passes CI ≠ what works.** This closes that gap.

---

## Architecture: Two-Call LLM-as-Judge

```
User message
     │
     ▼
[Subject Call] ──── system: SKILL.md content ──────► Claude response
                                                            │
                                                            ▼
                                          [Grader Call] ─── system: "You are an expert evaluator..."
                                                            │    user: original message + response + criteria list
                                                            ▼
                                                    JSON: per-criterion pass/fail + reasoning
                                                            │
                                                            ▼
                                                    Weighted score per case → summary report
```

**Subject call:** Claude responds with the skill as its system prompt — simulating a real user interaction with the plugin loaded.

**Grader call:** A separate Claude call evaluates the subject's response against a specific list of behavioral criteria. The grader has no access to the skill text — it only sees the original message, the response, and the criteria. This eliminates confirmation bias.

**Key design:** `should_pass: false` criteria (anti-pattern tests like "does NOT immediately write a PRD") are handled at grader-prompt construction time. The prompt explicitly states "this criterion PASSES if the behavior is NOT present." The runner uses `grader.passed` directly with no inversion logic, eliminating double-negative bugs.

---

## How to Run Locally

**Prerequisites:**
```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

**Run all plugins:**
```bash
python scripts/run_evals.py
```

**Run one plugin:**
```bash
python scripts/run_evals.py --plugin strategic-pm
python scripts/run_evals.py --plugin product-writing-studio
python scripts/run_evals.py --plugin pm-interview-prep
```

**Options:**
```bash
python scripts/run_evals.py --output json          # JSON output instead of terminal
python scripts/run_evals.py --model claude-haiku-4-5-20251001  # Cheaper model for iteration
python scripts/run_evals.py --plugin strategic-pm --output json
```

**Baseline mode (skill vs vanilla Claude):**
```bash
python scripts/run_evals.py --plugin strategic-pm --baseline
```

Baseline mode runs every eval case twice — once with the skill as system prompt, once with an empty system prompt (vanilla Claude). It shows per-case and overall behavioral lift:

```
spm-001 · Reverse Brief trigger on PRD request
  WITH skill:    10/10 (100%) ✅
  WITHOUT skill:  3/10 (30%)  ❌
  Skill lift: +70 points
```

This is the most powerful proof that a skill changes behavior. If vanilla Claude scores similarly, the skill isn't doing enough.

---

## How to Run in CI

The eval workflow is **manual trigger only** — it costs ~$1–2 per run at Opus pricing and should not run on every push.

1. Go to **Actions → Behavioral Eval → Run workflow**
2. Optionally specify a plugin name (leave blank for all)
3. Optionally specify a model (default: `claude-opus-4-6`)

Results appear in the **Job Summary** of the workflow run — a markdown table with per-case pass/fail and weighted scores.

---

## Eval Case Schema

```json
{
  "plugin": "strategic-pm",
  "skill_path": "plugins/strategic-pm/skills/strategic-pm/SKILL.md",
  "version": "1.0.0",
  "cases": [
    {
      "id": "spm-001",
      "name": "Human-readable case name",
      "category": "category-slug",
      "user_message": "The message sent to the subject model",
      "context": "Optional context prepended to the user turn (or null)",
      "criteria": [
        {
          "id": "spm-001-c1",
          "description": "Observable behavioral criterion, written as a falsifiable statement",
          "should_pass": true,
          "weight": 3
        }
      ]
    }
  ]
}
```

**Field reference:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique case ID. Format: `{plugin-prefix}-{3-digit-number}` |
| `name` | string | Human-readable case name |
| `category` | string | Behavioral category slug (e.g., `reverse-brief`, `anti-pattern`) |
| `user_message` | string | Message sent to the subject Claude call |
| `context` | string \| null | Additional context prepended to the user turn. Use for document reviews, background info, etc. |
| `criteria[].id` | string | Unique criterion ID. Format: `{case-id}-c{n}` |
| `criteria[].description` | string | Observable behavioral statement. Write as: "Response does X" or "Response does NOT do X" |
| `criteria[].should_pass` | boolean | `true` = criterion passes if the behavior IS present. `false` = criterion passes if behavior is NOT present |
| `criteria[].weight` | integer | Relative importance. Range: 1–5. Most criteria are 2–3; critical blockers are 3 |

---

## Interpreting Results

**Weighted score:** Each case score = `sum(weight for passing criteria) / sum(weight for all criteria)`.

**Pass threshold:** A case PASSES if its weighted score is `>= 0.75` (75%).

**Exit code:** Script exits `0` if all cases pass, `1` if any case is below threshold.

Example output:
```
[PASS] spm-001 · Reverse Brief trigger on PRD request     9/9 (100%)
  ✓ c1 (w:3) Did not immediately write a PRD
  ✓ c2 (w:3) Asked about problem/user/metric
  ✓ c3 (w:2) Batched questions together
  ✓ c4 (w:2) Stated assumptions before asking

[FAIL] spm-002 · Vanity metric detection                  4/8 (50%)
  ✗ c1 (w:3) Did not flag downloads as vanity metric
  ✓ c2 (w:3) Proposed outcome metric
  ✗ c3 (w:2) Validated downloads without challenge
```

A failing case means the skill's behavioral claim is not reliably being honored by Claude. The criterion results point directly at which behavior failed.

---

## How to Add Cases

1. Open `evals/<plugin>/cases.json`
2. Add a new object to the `cases` array following the schema above
3. Assign the next sequential ID (e.g., `spm-008`)
4. Write criteria as **observable, falsifiable behavioral statements** — not vague intent
5. For anti-pattern tests (things the skill should NOT do), set `should_pass: false`
6. Run locally to verify your case returns a result without crashing: `python scripts/run_evals.py --plugin <plugin>`

**Writing good criteria:**
- ✅ "Response flags downloads as a vanity metric"
- ✅ "Response does NOT immediately begin writing a PRD"
- ❌ "Response is helpful" (not falsifiable)
- ❌ "Response follows the skill guidelines" (too vague)

---

## Cost

Each eval case makes 2 API calls (subject + grader). Costs depend on response length and may vary, but here are approximate per-run costs for a full 31-case suite:

| Model | Approx. Cost per Run | Use Case |
|---|---|---|
| **Claude Opus** (`claude-opus-4-6`) | **$2–4** | Final quality validation, CI |
| **Claude Sonnet** (`claude-sonnet-4-6`) | **$0.30–0.60** | Development iteration, PR checks |
| **Claude Haiku** (`claude-haiku-4-5-20251001`) | **$0.05–0.10** | Case structure validation, rapid iteration |

Baseline mode (`--baseline`) doubles the cost since each case runs twice (with and without skill).

This is why the eval workflow is `workflow_dispatch` only — not triggered on every push or PR. There's no risk of runaway CI costs.

**Recommended workflow:** Iterate with Haiku to validate case structure, spot-check with Sonnet, run final validation with Opus.

---

## Limitations

- **LLM-as-judge is probabilistic.** The grader may occasionally disagree with a human reviewer. Always run at `temperature=0` to maximize reproducibility.
- **Grader bias.** The grader model is Claude, same as the subject. On some criteria, Claude-as-grader may be lenient toward Claude-as-subject. Where precision matters, manually review the subject response.
- **Not a substitute for human review.** Passing evals mean the behaviors are reliably present *on these specific test cases*. They don't cover every edge case.
- **Version drift.** If `cases.json["version"]` doesn't match the plugin's `plugin.json["version"]`, the runner prints a warning. Update evals when bumping plugin versions.
