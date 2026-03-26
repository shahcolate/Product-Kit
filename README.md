# ProductKit — Verified Claude Plugins for Product Teams

**Most AI plugins hope they work. ProductKit proves it.**

Opinionated Claude plugins for PMs, designers, engineers, and researchers — built with the same eval-driven development practices used by serious AI product teams. Each plugin ships with a behavioral eval harness: an LLM-as-judge test suite that verifies the skill actually changes Claude's behavior, not just that the file parses.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Plugin](https://img.shields.io/badge/Claude-Plugin_Marketplace-blueviolet)](https://claude.com/blog/skills)
[![Version](https://img.shields.io/badge/version-1.5.0-green.svg)](CHANGELOG.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Behavioral Evals](https://img.shields.io/badge/evals-31%20cases%20passing-brightgreen)](evals/README.md)

---

## What Sets This Apart

Most Claude plugin repos have zero behavioral testing. Their CI proves files parse. That's it.

ProductKit ships a **two-call LLM-as-judge eval harness**: every plugin has a test suite of behavioral cases. A subject call loads the skill and generates a response. A grader call scores the response against falsifiable criteria — "did Claude refuse to write the PRD before asking clarifying questions?" "did it flag the vanity metric?" Each case gets a weighted pass/fail score with a 75% threshold.

31 cases across 3 plugins. Every case you can read, run, and extend.

> **[How the eval harness works](evals/README.md)**

---

## Available Plugins

| Plugin | For | Description | Status |
|---|---|---|---|
| **[Strategic PM](plugins/strategic-pm/README.md)** | Product Managers | PRDs, roadmaps, competitive analysis, user research, AI product playbook | ✅ Live |
| **[Product Writing Studio](plugins/product-writing-studio/README.md)** | All roles | Exec comms, strategy memos, board decks, stakeholder emails | ✅ Live |
| **[PM Interview Prep](plugins/pm-interview-prep/README.md)** | PMs (job seekers) | Mock interviews, structured answer coaching, product sense & execution questions | ✅ Live |
| **[QA Tester](plugins/qa-tester/README.md)** | QA, Eng, PM | Autonomous browser-based QA — navigates, clicks, breaks things, files bugs in Linear/JIRA | ✅ Live |
| **UX Strategy** | Designers | UX heuristics, design system thinking, usability audits, interaction patterns | 🔜 Coming soon |
| **Metrics & Analytics** | PMs, Data, Eng | Dashboard design, metric trees, experiment analysis, statistical rigor checks | 📋 Planned |

> **Want to build a plugin?** See [CONTRIBUTING.md](CONTRIBUTING.md) — we're actively looking for contributors across product, design, engineering, and research.

---

## Quick Start

### Claude Code (recommended — auto-updates when we ship improvements)

Open your terminal and run these commands inside Claude Code:

**Step 1: Add the marketplace**
```bash
/plugin marketplace add shahcolate/Product-Kit
```
This clones the repo locally. You only do this once.

**Step 2: Install the plugin**
```bash
/plugin add strategic-pm
```
When prompted, choose your scope:
- **User scope** — available across all your projects
- **Project scope** — only available in the current project

**Step 3: Enable auto-updates (recommended)**
When prompted during install, select **auto-update**. New versions will sync automatically every time Claude Code starts.

To update manually at any time:
```bash
/plugin marketplace update
```

That's it. Claude will automatically load Strategic PM whenever you're doing product work. No extra commands needed — just start working.

### Claude.ai (manual upload)

1. Download the latest ZIP from the [Releases page](https://github.com/shahcolate/Product-Kit/releases)
2. Go to **Settings → Capabilities → Skills**
3. Click **"Upload skill"** and upload the ZIP
4. Claude auto-loads it whenever the relevant work is detected

> Claude.ai doesn't support auto-updates yet. ⭐ Star this repo and watch releases to get notified when new versions ship.

### Team & Enterprise (org-wide deployment)

Organization Owners can provision plugins centrally from admin settings. Admin-provisioned skills are enabled by default for all users — one upload covers your entire product team.

### Claude API

Skills are supported via the `/v1/skills` API endpoint. See [Anthropic's Skills documentation](https://platform.claude.com/docs/en/skills) for integration details.

---

## Plugins

### 🧠 Strategic PM

**Turn Claude from a template-filler into an opinionated PM co-pilot.**

500+ lines of product strategy instruction: the Five Laws, Devil's Advocate Protocol, Decision Journal, PM Maturity Adapter, AI Product Management Playbook, and anti-pattern detection for 13 common PM failure modes.

> [Full details and install guide](plugins/strategic-pm/README.md)

### ✍️ Product Writing Studio

**Claude becomes an expert product communicator — not a generic writer.**

Audience-First Protocol, Pyramid Principle enforcement, SCQA structuring, Clarity Laws, and document type intelligence for exec updates, strategy memos, board decks, stakeholder emails, product announcements, one-pagers, design briefs, and launch comms.

> [Full details and install guide](plugins/product-writing-studio/README.md)

### 🎯 PM Interview Prep

**Your personal PM interview coach — not a flashcard app.**

Mock interview mode with scoring rubrics, JTBD-framed product sense coaching, structured decomposition for estimation questions, STAR format behavioral coaching, and anti-pattern detection for common interview mistakes. Calibrated for FAANG, growth-stage, enterprise, and consumer companies.

> [Full details and install guide](plugins/pm-interview-prep/README.md)

### 🧪 QA Tester

**Claude opens the browser and tests your app like a real QA engineer.**

Discovery phase (asks about docs, recent changes, test scope), structured test plan with real methodology (boundary analysis, state transitions, error paths, exploratory testing), browser-based execution with screenshots, and automatic bug filing in Linear or JIRA with full reproduction steps. Runs in Claude Cowork.

> [Full details and install guide](plugins/qa-tester/README.md)

---

## Example Teardowns

See what ProductKit produces before installing it. These teardowns were generated by the AI Product Teardown Tool using Strategic PM as the system prompt.

| Product | Category | Key Finding |
|---|---|---|
| **[Notion](examples/teardowns/notion.md)** | Productivity | Strong switching costs, but "everything tool" positioning creates value prop clarity risk |
| **[Linear](examples/teardowns/linear.md)** | Dev Tools | Counter-positioning against Jira works — but narrow ICP limits TAM |
| **[Figma](examples/teardowns/figma.md)** | Design | Network effects + multiplayer = strongest moat in the set, post-Adobe risk resolved |
| **[ChatGPT](examples/teardowns/chatgpt.md)** | AI | Fastest adoption in history, but retention architecture is the weakest dimension |

> **[Browse all teardowns →](examples/teardowns/)**

---

## AI Product Teardown Tool

Run any product through Strategic PM's full framework battery and get a structured teardown across 6 dimensions: JTBD & Value Prop, Competitive Moat (7 Powers), Growth Model, Anti-Pattern Scan (all 13), Monetization, and Strategic Verdict.

This is a standalone CLI tool that calls the Anthropic API directly — not a Claude plugin. Clone the repo and run it with your own API key:

```bash
git clone https://github.com/shahcolate/Product-Kit.git
cd Product-Kit
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/teardown.py "Notion"
python scripts/teardown.py "Linear" --output markdown --save
```

### Comparison Mode

Compare two products head-to-head across all 6 dimensions plus a 7th "Head-to-Head Verdict":

```bash
python scripts/teardown.py "Notion" --vs "Coda"
python scripts/teardown.py "Figma" --vs "Canva" --output markdown --save
```

### Social Export

Generate a thread-ready summary — a punchy hook, 5 bullet verdicts, and a bottom line:

```bash
python scripts/teardown.py "Notion" --output social
```

All dimensions run in parallel via async API calls (~15s vs ~60s sequential).

---

## Functional Tools

Standalone CLI tools that do real work for product teams. Each calls the Anthropic API directly — clone the repo, set your API key, and run.

### Feedback Synthesizer

Ingest user feedback from CSV/JSON, cluster by theme, and produce structured synthesis with quotes, sentiment, urgency, and recommended actions. Multi-phase pipeline: extract themes per batch, merge across batches, assess actionability.

```bash
pip install -r requirements.txt
python scripts/feedback_synth.py feedback.csv --text-column "comment" --source "NPS Q1 2026"
python scripts/feedback_synth.py reviews.json --format json --text-field "body" --max-themes 8 --output markdown --save
```

### Release Notes Generator

Read git log (commit range, tag range, or date range), classify changes, and generate polished release notes. Produces internal (eng-facing) and external (customer-facing) versions — or both.

```bash
python scripts/release_notes.py --repo . --since v2.3.0 --audience external
python scripts/release_notes.py --repo . --range v2.3.0..v2.4.0 --output markdown --save
```

### Competitive Screenshot Monitor

Capture competitor pages via headless browser, then use Claude vision to detect and summarize semantic changes vs. previous captures. Run weekly/monthly via cron. Semantic diff ("they removed the free tier") not pixel diff.

```bash
pip install -r requirements-browser.txt && python -m playwright install chromium
python scripts/competitor_watch.py --url "https://competitor.com/pricing" --name "Competitor X"
python scripts/competitor_watch.py --config competitors.json --output markdown --save
```

### Onboarding Flow Auditor

Navigate a signup/onboarding flow via headless browser, capture each screen, and produce a structured UX audit: friction scoring per screen, time-to-value assessment, drop-off risk identification, and overall A-F grade.

```bash
python scripts/onboarding_audit.py "https://app.example.com/signup" --product "Example App" --category "B2B SaaS"
python scripts/onboarding_audit.py "https://linear.app/signup" --max-steps 15 --output markdown --save
```

### Tutorial Creator

Take a URL + natural language goal, AI-plan navigation steps, capture screenshots at each step, and generate an annotated step-by-step tutorial. Supports pre-defined steps JSON and cookie-based auth for authenticated flows.

```bash
python scripts/tutorial.py "https://app.linear.dev" --goal "Create a new project and add a task"
python scripts/tutorial.py "https://notion.so" --steps steps.json --auth-cookie cookie.txt --output markdown --save
```

---

## Minimal Viable Context (MVC)

PRDs were designed for deterministic software. AI agents need something different — a spec that captures what the agent does, what it must never do, how much each call can cost, and how to detect when it drifts out of spec.

**MVC is the smallest set of product decisions an AI agent needs before it can act on behalf of a user.** It's a structured YAML template covering five components: objective + non-goals, constraints, acceptance tests, tools & boundaries, and canonical examples. One file, testable in CI, readable by humans.

The [`mvc/`](mvc/) directory contains everything you need to adopt MVC:

- **Blank template** — copy [`templates/mvc-template.yaml`](mvc/templates/mvc-template.yaml) and fill it in
- **Worked examples** — [AI recommendations](mvc/templates/mvc-example-recommendations.yaml) (full MVC) and [payment migration](mvc/templates/mvc-example-backend-migration.yaml) (stripped-down, no designer)
- **Demo** — test runner that validates mock agents against an MVC spec ([run it](mvc/demo/))
- **Test patterns** — contract, behavioral, boundary, and drift detection specs
- **CI workflows** — GitHub Actions for PR tests and weekly drift detection
- **Docs** — [4-week onboarding guide](mvc/docs/getting-started.md), [RACI table](mvc/docs/raci.md), [solo builder guidance](mvc/docs/when-no-designer.md)

> **[Read the original article: The New PRD](https://shahai.substack.com/p/the-new-prd)**

---

## Behavioral Eval Harness

The existing CI (`validate.yml`) proves plugin files parse and exist. That's table stakes. The eval harness answers the harder question: **does loading this skill actually change what Claude does?**

Each plugin ships with an `evals/<plugin>/cases.json` — a suite of behavioral test cases with falsifiable criteria. The runner makes two API calls per case:

1. **Subject call** — Claude responds with the skill as its system prompt, simulating a real user interaction
2. **Grader call** — a separate Claude call scores the response against each criterion and returns structured JSON

Example criteria from `strategic-pm`:
- *"Response does NOT immediately begin writing a PRD"* — passes if the behavior is absent
- *"Response asks about the underlying problem, user need, or metric"* — passes if the behavior is present
- *"Questions are batched rather than asked one at a time"* — weighted 2, critical criteria weighted 3

**Run locally:**
```bash
git clone https://github.com/shahcolate/Product-Kit.git
cd Product-Kit
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/run_evals.py
# or: --plugin strategic-pm  --output json  --model claude-haiku-4-5-20251001
```

### Baseline Mode (Skill vs Vanilla Claude)

Prove the skill actually matters. Run every eval case twice — with the skill and without — and see the behavioral lift:

```bash
python scripts/run_evals.py --plugin strategic-pm --baseline
```

```
spm-001 · Reverse Brief trigger on PRD request
  WITH skill:    10/10 (100%) ✅
  WITHOUT skill:  3/10 (30%)  ❌
  Skill lift: +70 points
```

**Run in CI:** Actions → Behavioral Eval → Run workflow (manual trigger — ~$1–2/run at Opus pricing).

> [Full methodology, schema, and how to add cases](evals/README.md)

---

## Teardown-on-Issue

Want a teardown without cloning the repo? Open a GitHub issue using the **Product Teardown Request** template, and a GitHub Action will run the teardown and post results as a comment.

1. Go to [Issues → New Issue](https://github.com/shahcolate/Product-Kit/issues/new/choose)
2. Select **Product Teardown Request**
3. Enter the product name in the title: `Teardown: Stripe`
4. Optionally add context in the body
5. Results appear as a comment within ~2 minutes

Rate-limited to 5 teardowns/day to manage API costs.

---

## Repo Structure

```
Product-Kit/
├── README.md                              # You're here
├── mvc/                                   # MVC templates, demo, tests, and docs
├── CONTRIBUTING.md                        # How to contribute plugins and skills
├── CHANGELOG.md                           # Version history
├── LICENSE                                # MIT
├── marketplace.json                       # Plugin marketplace catalog
├── .claude-plugin/
│   └── marketplace.json                   # Marketplace marker
├── plugins/
│   ├── strategic-pm/                      # ✅ Live
│   │   ├── README.md
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/strategic-pm/SKILL.md
│   ├── product-writing-studio/            # ✅ Live
│   │   ├── README.md
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/product-writing-studio/SKILL.md
│   ├── pm-interview-prep/                 # ✅ Live
│   │   ├── README.md
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/pm-interview-prep/SKILL.md
│   └── qa-tester/                         # ✅ Live
│       ├── README.md
│       ├── .claude-plugin/plugin.json
│       └── skills/qa-tester/SKILL.md
├── evals/
│   ├── README.md                          # Eval methodology and how to run
│   ├── strategic-pm/cases.json            # 12 behavioral eval cases
│   ├── product-writing-studio/cases.json  # 13 behavioral eval cases
│   └── pm-interview-prep/cases.json       # 6 behavioral eval cases
├── examples/
│   └── teardowns/                         # Example teardown outputs
│       ├── notion.md
│       ├── linear.md
│       ├── figma.md
│       └── chatgpt.md
├── scripts/
│   ├── _common.py                         # Shared utilities across CLI tools
│   ├── feedback_synth.py                  # Feedback Synthesizer (CSV/JSON → themed synthesis)
│   ├── release_notes.py                   # Release Notes Generator (git log → polished notes)
│   ├── competitor_watch.py                # Competitive Screenshot Monitor (Playwright + vision)
│   ├── onboarding_audit.py                # Onboarding Flow Auditor (Playwright + vision)
│   ├── tutorial.py                        # Tutorial Creator (Playwright + vision + annotation)
│   ├── run_evals.py                       # Eval runner (--baseline for skill vs vanilla)
│   └── teardown.py                        # Teardown CLI (--vs, --output social, async)
├── requirements.txt                       # Base deps (anthropic)
├── requirements-browser.txt               # Browser tool deps (playwright, Pillow)
├── .github/
│   ├── workflows/teardown.yml             # Teardown-on-issue Action
│   └── ISSUE_TEMPLATE/teardown_request.md
├── teardowns/                             # Saved teardown reports (gitignored)
├── feedback-synthesis/                    # Saved feedback synthesis reports (gitignored)
├── release-notes/                         # Saved release notes (gitignored)
├── competitor-watch/                      # Competitor screenshots and reports (gitignored)
├── onboarding-audits/                     # Onboarding audit reports (gitignored)
└── tutorials/                             # Generated tutorials with screenshots (gitignored)
```

---

## Marketplace Roadmap

| Status | Plugin | Audience | Description |
|---|---|---|---|
| ✅ Live | **[Strategic PM](plugins/strategic-pm/README.md)** | PMs | Full-stack PM co-pilot with AI Playbook |
| ✅ Live | **[Product Writing Studio](plugins/product-writing-studio/README.md)** | All roles | Exec comms, strategy memos, board decks, stakeholder emails |
| ✅ Live | **[PM Interview Prep](plugins/pm-interview-prep/README.md)** | PMs | Mock interviews, structured answer coaching |
| ✅ Live | **[QA Tester](plugins/qa-tester/README.md)** | QA, Eng, PM | Browser-based QA agent, files bugs in Linear/JIRA |
| 🔜 Next | **UX Strategy** | Designers | Heuristics, usability audits, design system thinking |
| 📋 Planned | **Metrics & Analytics** | PMs, Data, Eng | Metric trees, experiment analysis, dashboard design |
| 💡 Exploring | **Research Ops** | Researchers, PMs | Automated user research synthesis with web search |
| 💡 Exploring | **Jira/Linear Bridge** | PMs, Eng | Roadmap-to-ticket workflows via MCP |

Have a plugin idea? [Open an issue](https://github.com/shahcolate/Product-Kit/issues) or read [CONTRIBUTING.md](CONTRIBUTING.md) to propose one.

---

## Contributing

ProductKit gets better when people who build real products contribute to it. We're looking for PMs, designers, engineers, researchers — anyone who's shipped and learned from it.

- **Improve existing plugins** — add frameworks, edge cases, anti-patterns
- **Build new plugins** — bring your discipline's expertise
- **Report bugs** — when Claude misapplies something, tell us

**Read the full guide → [CONTRIBUTING.md](CONTRIBUTING.md)**

---

## FAQ

**Q: Does this work on the free Claude plan?**
A: Yes. Skills are available on free, Pro, Max, Team, and Enterprise plans. Code execution must be enabled.

**Q: How do I get updates automatically?**
A: Claude Code users can enable auto-update during install — new versions sync at startup. Or run `/plugin marketplace update` manually. Claude.ai users re-download from Releases.

**Q: Will Claude always use this skill?**
A: Claude auto-detects when the skill is relevant based on your task. Any matching work should trigger it automatically.

**Q: Can I use multiple plugins at once?**
A: Yes. Claude loads multiple skills simultaneously. ProductKit plugins are designed to compose well with each other and with third-party skills.

**Q: I'm on a Team/Enterprise plan. Can I deploy this org-wide?**
A: Yes. Organization Owners can provision skills centrally. One upload covers your entire team.

**Q: I want to add a plugin for my discipline (design, engineering, research). Can I?**
A: Yes — that's the point. See [CONTRIBUTING.md](CONTRIBUTING.md) for the plugin proposal process.

**Q: Something isn't working right.**
A: [Open an issue](https://github.com/shahcolate/Product-Kit/issues) with what you asked Claude and what went wrong. Include the output if possible.

---

## License

[MIT](LICENSE) — use it, fork it, improve it, share it.

---

<p align="center">
  <strong>Thinking partners for the people who build products.</strong>
  <br><br>
  ⭐ Star this repo if it makes your work sharper. It helps others find it.
</p>
