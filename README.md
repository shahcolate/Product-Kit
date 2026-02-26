# 🛠️ ProductKit — Claude Plugins for Product Teams

**Thinking partners for the people who build products.**

A growing collection of Claude plugins for PMs, designers, engineers, and researchers. Not template fillers — opinionated co-pilots that challenge your thinking and make your output sharper.

Install one or all. Each plugin works independently, updates automatically, and gets better with community contributions.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Plugin](https://img.shields.io/badge/Claude-Plugin_Marketplace-blueviolet)](https://claude.com/blog/skills)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](CHANGELOG.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Available Plugins

| Plugin | For | Description | Status |
|---|---|---|---|
| **[Strategic PM](#-strategic-pm)** | Product Managers | PRDs, roadmaps, competitive analysis, user research, AI product playbook | ✅ Live |
| **UX Strategy** | Designers | UX heuristics, design system thinking, usability audits, interaction patterns | 🔜 Coming soon |
| **PM Interview Prep** | PMs (job seekers) | Case study practice, structured answer coaching, mock product sense questions | 🔜 Coming soon |
| **Metrics & Analytics** | PMs, Data, Eng | Dashboard design, metric trees, experiment analysis, statistical rigor checks | 📋 Planned |
| **Product Writing Studio** | All roles | Exec comms, strategy memos, board decks, stakeholder emails | 📋 Planned |

> **Want to build a plugin?** See [CONTRIBUTING.md](CONTRIBUTING.md) — we're actively looking for contributors across product, design, engineering, and research.

---

## Quick Start

### Claude Code (recommended — auto-updates when we ship improvements)

Open your terminal and run these commands inside Claude Code:

**Step 1: Add the marketplace**
```bash
/plugin marketplace add YOUR_GITHUB_USERNAME/productkit
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

1. Download the latest ZIP from the [Releases page](../../releases)
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

500+ lines of product strategy instruction. Frameworks, decision protocols, anti-pattern detection, and the first AI Product Management Playbook built into a Claude skill.

### The Problem

Claude is a brilliant writer. Ask it for a PRD and you'll get a beautiful document — with no problem statement, no success metrics, and no acknowledgment that shipping this feature kills another team's roadmap.

It produces professional-looking PM output with no strategic thinking underneath. That's not a tool. That's a liability.

### The Fix

Strategic PM rewires how Claude approaches product work. It doesn't fill templates — it thinks.

**Before installing:**
> "Here's your PRD with 12 user stories and a scope section."

**After installing:**
> "Before I write this — what user problem are we solving, and how will we know it worked? Your draft implies a dashboard feature, but the real job seems to be 'know if things are on track without asking someone.' That changes the solution space. Also, shipping this means the integrations team loses 3 weeks of capacity in Q2. Is that an accepted trade-off?"

---

### What Makes This Different

Most PM prompts are framework checklists. This skill changes Claude's **behavior**.

#### 🔴 The Five Laws
Non-negotiable checks that run on every output:

| Law | What It Does |
|---|---|
| **The "So What?" Filter** | Blocks output that can't connect to a business or user outcome |
| **The "Who Loses?" Rule** | Names the losers in every product decision before producing anything |
| **The "Why Now?" Pressure Test** | Forces timing justification for strategy and roadmap work |
| **Confidence Labels** | Tags every recommendation as 🟢 High, 🟡 Medium, or 🔴 Low confidence |
| **Second-Order Consequence Scan** | Identifies downstream effects most PMs miss |

#### 😈 Devil's Advocate Protocol
On major decisions, Claude automatically:
1. **Steelmans your plan** — states the strongest version of what you're proposing
2. **Attacks it** — presents the 2-3 most dangerous failure modes
3. **Offers escape hatches** — mitigations, early warning signals, or kill criteria

The pre-mortem that prevents the post-mortem. Skip with "skip devil's advocate" — but it runs by default on high-stakes decisions.

#### 📓 Decision Journal
For major decisions, Claude generates a structured record:

```
DECISION: Ship usage-based pricing for SMB tier
DATE: 2026-02-26
CONTEXT: Seat-based pricing creates friction for small teams (3-5 people)
OPTIONS CONSIDERED: Per-seat discount, freemium tier, usage-based
KEY ASSUMPTION: SMBs will increase usage 40%+ when price friction is removed
REVIEW TRIGGER: If SMB expansion revenue < 15% increase by June 1
CONFIDENCE: 🟡 Medium
```

Most teams forget WHY they made a call. This creates institutional memory.

#### 🎯 PM Maturity Adapter
Claude silently reads your experience level and adjusts:

- **Early-career PM** → Teaches frameworks as it applies them
- **Mid-career PM** → Focuses on blind spots and pressure-testing
- **Senior/Exec PM** → Sparring partner mode. Challenges directly.

Recalibrates as the conversation evolves.

#### ⚡ Reverse Brief
Instead of asking 15 clarifying questions one by one, Claude batches them, states its own best-guess answers, and asks you to correct what's wrong. 10x faster than the usual back-and-forth.

#### 🚨 Anti-Pattern Detection
Claude flags and refuses to enable:

- Feature factory output (specs without linked outcomes)
- Vanity metrics (pageviews without retention context)
- Roadmap theater (Q3 dates with no delivery path)
- Consensus-driven prioritization (averaging opinions instead of finding leverage)
- Solution-first thinking (wireframes before problem definition)
- Premature scaling (designing for 10M users before validating with 1,000)
- Post-launch abandonment (shipping without a learning cycle)
- HiPPO decisions (executive opinion as evidence substitute)
- Backfill analytics (manufacturing data to justify decisions already made)
- ...and 4 more

---

### 🤖 AI Product Management Playbook

This section doesn't exist in any other PM skill. If you're building AI-powered products, traditional PM frameworks break in specific ways. This playbook addresses them.

#### AI Uncertainty Stack
Traditional products have uncertain demand. AI products have uncertain demand **AND uncertain capability**. Before any AI feature spec, classify:

- **Capability uncertainty** — Can the model do this reliably? 95% accuracy is amazing for suggestions and catastrophic for medical diagnoses.
- **Evaluation uncertainty** — Can you even tell if it's working? If you can't evaluate, you can't iterate.
- **Behavior uncertainty** — Models update. Your feature changes without you shipping code.

#### AI Feature Spec Additions
Every AI feature spec gets these sections automatically:

- **Failure Mode Taxonomy** — graceful, silent, and catastrophic failures, each with required UX responses
- **Confidence UX Decision** — when to show uncertainty to users (product decision, not engineering default)
- **Human-in-the-Loop Design** — review points, cost of review, removal thresholds
- **Evaluation Rubric** — concrete rated examples defining "good enough" before engineering starts
- **Model Dependency Documentation** — version, deprecation plan, migration path

#### AI-Specific Metrics

| Metric | What It Captures |
|---|---|
| **Task completion rate** | Did the AI actually solve the problem? |
| **Edit/override rate** | Is this a starting point or a solution? |
| **Automation trust curve** | Is user reliance growing over time? |
| **Fallback rate** | How often do users abandon AI and do it manually? |
| **False confidence rate** | How often is the AI wrong but appears confident? |

#### Also includes:
- **Build vs. Buy vs. Wrap** decision matrix for AI with defensibility pressure-testing
- **AI Ethics Checklist** — bias audits, transparency, data usage, failure impact, reversibility
- **AI Roadmap Dynamics** — capability cliffs, "good enough" thresholds, prompt engineering as product work, eval-driven development, compounding data advantages
- **AI Competitive Analysis** — data moats, model strategy, eval rigor, integration depth, trust signals

---

### Full Framework Coverage

<details>
<summary><strong>Discovery & Problem Framing</strong></summary>

- Jobs-to-be-Done (JTBD) — reframes features as user jobs
- Opportunity Solution Trees — outcome → opportunity → solution mapping
- Assumption Mapping — desirability, viability, feasibility, usability
- JTBD Interview Synthesis — trigger, job, hiring criteria, anxiety, workaround, social dimension
- "What Would Have to Be True?" Analysis (Lafley/Martin)
</details>

<details>
<summary><strong>Prioritization</strong></summary>

- RICE (Reach × Impact × Confidence / Effort)
- ICE (Impact × Confidence × Ease)
- Opportunity Cost Framing
- Dependency Mapping
- Regret Minimization Filter (for irreversible decisions)
</details>

<details>
<summary><strong>Strategy & Positioning</strong></summary>

- 7 Powers Framework (Helmer)
- Crossing the Chasm — beachhead segments
- Competitive Threat Taxonomy
- Wardley Mapping Lens
</details>

<details>
<summary><strong>Metrics & Measurement</strong></summary>

- North Star + Input Metrics Tree
- Guardrail Metrics
- Survivorship Bias Alerts
- Goodhart's Law Checks
</details>

<details>
<summary><strong>Business Model Literacy</strong></summary>

- Unit economics (CAC, LTV, LTV:CAC, payback period)
- Monetization model awareness (usage, seat, transactional, marketplace, freemium, enterprise)
- Pricing strategy principles
</details>

<details>
<summary><strong>Growth & Retention</strong></summary>

- Acquisition loop typing (viral, content, paid, sales)
- 3 Retention Horizons (activation → habit → deep)
</details>

<details>
<summary><strong>Go-to-Market</strong></summary>

- Launch tiering (T1-T4 classification)
- Default rollout sequence (dogfood → alpha → beta → GA)
</details>

<details>
<summary><strong>Stakeholder Navigation</strong></summary>

- Stakeholder Chessboard (influence × alignment)
- "When the CEO Wants a Feature" protocol
- "Saying No Without Saying No" reframes
</details>

<details>
<summary><strong>Competitive Intelligence</strong></summary>

- Signal classification (strategic, product, narrative, customer)
- Competitive response protocol (48-hour rule)
- Honest market sizing (TAM/SAM/SOM)
</details>

<details>
<summary><strong>Document Standards</strong></summary>

- PRDs (JTBD-framed, with anti-scope and post-launch learning plans)
- Roadmaps (Now/Next/Later with confidence bands)
- Strategy Memos (SCQA + steelman of opposing view)
- Experiment Designs (hypothesis format + kill criteria)
- Executive Updates (max 3 key messages)
</details>

<details>
<summary><strong>Edge Case Protocols</strong></summary>

Handles 11 common PM scenarios: no data available, feature requests without outcomes, multiple audiences, political subtext, conflicting research, timelines without estimates, and more.
</details>

---

### Usage Examples

Once installed, just do PM work. The skill triggers automatically:

**Write a PRD:**
> "I need a PRD for adding real-time collaboration to our document editor."

**Stress-test a strategy:**
> "We're planning to move from seat-based to usage-based pricing for our SMB tier."

**Spec an AI feature:**
> "We want to add AI-powered email drafting to our CRM."

**Synthesize user research:**
> "Here are 8 interview transcripts from our onboarding study. What are we missing?"

**Analyze a competitor:**
> "Notion just launched an AI feature that summarizes meeting notes. What should we do?"

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
│   └── config.json                        # Marketplace marker
├── plugins/
│   └── strategic-pm/                      # ✅ Live
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── strategic-pm/
│               └── SKILL.md
└── releases/
    └── strategic-pm-v1.0.0.zip            # For Claude.ai manual upload
```

Future plugins go under `plugins/`. Each is self-contained.

---

## Marketplace Roadmap

| Status | Plugin | Audience | Description |
|---|---|---|---|
| ✅ Live | **Strategic PM** | PMs | Full-stack PM co-pilot with AI Playbook |
| 🔜 Next | **UX Strategy** | Designers | Heuristics, usability audits, design system thinking |
| 🔜 Next | **PM Interview Prep** | PMs | Case study practice, structured answer coaching |
| 📋 Planned | **Metrics & Analytics** | PMs, Data, Eng | Metric trees, experiment analysis, dashboard design |
| 📋 Planned | **Product Writing Studio** | All roles | Exec comms, strategy memos, stakeholder emails |
| 💡 Exploring | **Research Ops** | Researchers, PMs | Automated user research synthesis with web search |
| 💡 Exploring | **Jira/Linear Bridge** | PMs, Eng | Roadmap-to-ticket workflows via MCP |

Have a plugin idea? [Open an issue](../../issues) or read [CONTRIBUTING.md](CONTRIBUTING.md) to propose one.

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
A: [Open an issue](../../issues) with what you asked Claude and what went wrong. Include the output if possible.

---

## License

[MIT](LICENSE) — use it, fork it, improve it, share it.

---

<p align="center">
  <strong>Thinking partners for the people who build products.</strong>
  <br><br>
  ⭐ Star this repo if it makes your work sharper. It helps others find it.
</p>
