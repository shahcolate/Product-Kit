# ProductKit — Verified Claude Plugins for Product Teams

**Most AI plugins hope they work. ProductKit proves it.**

Opinionated Claude plugins for PMs, designers, engineers, and researchers — built with the same eval-driven development practices used by serious AI product teams. Each plugin ships with a behavioral eval harness: an LLM-as-judge test suite that verifies the skill actually changes Claude's behavior, not just that the file parses.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Plugin](https://img.shields.io/badge/Claude-Plugin_Marketplace-blueviolet)](https://claude.com/blog/skills)
[![Version](https://img.shields.io/badge/version-1.3.0-green.svg)](CHANGELOG.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Behavioral Evals](https://img.shields.io/badge/evals-14%20cases%20passing-brightgreen)](evals/README.md)

---

## What Sets This Apart

Most Claude plugin repos have zero behavioral testing. Their CI proves files parse. That's it.

ProductKit ships a **two-call LLM-as-judge eval harness**: every plugin has a test suite of behavioral cases. A subject call loads the skill and generates a response. A grader call scores the response against falsifiable criteria — "did Claude refuse to write the PRD before asking clarifying questions?" "did it flag the vanity metric?" Each case gets a weighted pass/fail score with a 75% threshold.

14 cases across 2 plugins. Every case you can read, run, and extend.

→ **[How the eval harness works](evals/README.md)**

---

## Available Plugins

| Plugin | For | Description | Status |
|---|---|---|---|
| **[Strategic PM](plugins/strategic-pm/README.md)** | Product Managers | PRDs, roadmaps, competitive analysis, user research, AI product playbook | ✅ Live |
| **[Product Writing Studio](plugins/product-writing-studio/README.md)** | All roles | Exec comms, strategy memos, board decks, stakeholder emails | ✅ Live |
| **UX Strategy** | Designers | UX heuristics, design system thinking, usability audits, interaction patterns | 🔜 Coming soon |
| **PM Interview Prep** | PMs (job seekers) | Case study practice, structured answer coaching, mock product sense questions | 🔜 Coming soon |
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

## 🧠 Strategic PM

**Turn Claude from a template-filler into an opinionated PM co-pilot.**

500+ lines of product strategy instruction: the Five Laws, Devil's Advocate Protocol, Decision Journal, PM Maturity Adapter, AI Product Management Playbook, and anti-pattern detection for 13 common PM failure modes.

→ [Full details and install guide](plugins/strategic-pm/README.md)

---

## ✍️ Product Writing Studio

**Claude becomes an expert product communicator — not a generic writer.**

Audience-First Protocol, Pyramid Principle enforcement, SCQA structuring, Clarity Laws, and document type intelligence for exec updates, strategy memos, board decks, stakeholder emails, product announcements, one-pagers, design briefs, and launch comms.

→ [Full details and install guide](plugins/product-writing-studio/README.md)

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
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/run_evals.py
# or: --plugin strategic-pm  --output json  --model claude-haiku-4-5-20251001
```

**Run in CI:** Actions → Behavioral Eval → Run workflow (manual trigger — ~$1–2/run at Opus pricing).

→ [Full methodology, schema, and how to add cases](evals/README.md)

---

## AI Product Teardown Tool

Run any product through Strategic PM's full framework battery and get a structured teardown across 6 dimensions: JTBD & Value Prop, Competitive Moat (7 Powers), Growth Model, Anti-Pattern Scan (all 13), Monetization, and Strategic Verdict.

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/teardown.py "Notion"
python scripts/teardown.py "Linear" --output markdown --save
```

Each dimension gets its own focused API call with Strategic PM as the system prompt — producing higher-quality, framework-specific analysis than a single massive prompt. Outputs are screenshot-ready for sharing.

---

## Repo Structure

```
productkit/
├── README.md                              # You're here
├── CONTRIBUTING.md                        # How to contribute plugins and skills
├── CHANGELOG.md                           # Version history
├── LICENSE                                # MIT
├── marketplace.json                       # Plugin marketplace catalog
├── .claude-plugin/
│   └── marketplace.json                   # Marketplace marker
├── plugins/
│   ├── strategic-pm/                      # ✅ Live
│   │   ├── README.md                      # Plugin deep-dive and install guide
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   │       └── strategic-pm/
│   │           └── SKILL.md
│   └── product-writing-studio/            # ✅ Live
│       ├── README.md                      # Plugin deep-dive and install guide
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── product-writing-studio/
│               └── SKILL.md
├── evals/
│   ├── README.md                          # Eval methodology and how to run
│   ├── strategic-pm/
│   │   └── cases.json                     # 7 behavioral eval cases
│   └── product-writing-studio/
│       └── cases.json                     # 7 behavioral eval cases
├── scripts/
│   ├── run_evals.py                       # Eval runner (LLM-as-judge harness)
│   └── teardown.py                        # AI Product Teardown CLI tool
├── teardowns/                             # Saved teardown reports (gitignored)
└── releases/
    ├── strategic-pm-v1.0.0.zip            # For Claude.ai manual upload
    └── product-writing-studio-v1.1.0.zip  # For Claude.ai manual upload
```

Each plugin is self-contained under `plugins/`. Each has its own README with full details.

---

## Marketplace Roadmap

| Status | Plugin | Audience | Description |
|---|---|---|---|
| ✅ Live | **[Strategic PM](plugins/strategic-pm/README.md)** | PMs | Full-stack PM co-pilot with AI Playbook |
| ✅ Live | **[Product Writing Studio](plugins/product-writing-studio/README.md)** | All roles | Exec comms, strategy memos, board decks, stakeholder emails |
| 🔜 Next | **UX Strategy** | Designers | Heuristics, usability audits, design system thinking |
| 🔜 Next | **PM Interview Prep** | PMs | Case study practice, structured answer coaching |
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
