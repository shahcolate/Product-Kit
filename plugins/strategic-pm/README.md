# 🧠 Strategic PM — Plugin for ProductKit

**Turn Claude from a template-filler into an opinionated PM co-pilot.**

500+ lines of product strategy instruction. Frameworks, decision protocols, anti-pattern detection, and the first AI Product Management Playbook built into a Claude skill.

← [Back to ProductKit marketplace](../../README.md)

---

## The Problem

Claude is a brilliant writer. Ask it for a PRD and you'll get a beautiful document — with no problem statement, no success metrics, and no acknowledgment that shipping this feature kills another team's roadmap.

It produces professional-looking PM output with no strategic thinking underneath. That's not a tool. That's a liability.

## The Fix

Strategic PM rewires how Claude approaches product work. It doesn't fill templates — it thinks.

**Before installing:**
> "Here's your PRD with 12 user stories and a scope section."

**After installing:**
> "Before I write this — what user problem are we solving, and how will we know it worked? Your draft implies a dashboard feature, but the real job seems to be 'know if things are on track without asking someone.' That changes the solution space. Also, shipping this means the integrations team loses 3 weeks of capacity in Q2. Is that an accepted trade-off?"

---

## What Makes This Different

Most PM prompts are framework checklists. This skill changes Claude's **behavior**.

### 🔴 The Five Laws
Non-negotiable checks that run on every output:

| Law | What It Does |
|---|---|
| **The "So What?" Filter** | Blocks output that can't connect to a business or user outcome |
| **The "Who Loses?" Rule** | Names the losers in every product decision before producing anything |
| **The "Why Now?" Pressure Test** | Forces timing justification for strategy and roadmap work |
| **Confidence Labels** | Tags every recommendation as 🟢 High, 🟡 Medium, or 🔴 Low confidence |
| **Second-Order Consequence Scan** | Identifies downstream effects most PMs miss |

### 😈 Devil's Advocate Protocol
On major decisions, Claude automatically:
1. **Steelmans your plan** — states the strongest version of what you're proposing
2. **Attacks it** — presents the 2-3 most dangerous failure modes
3. **Offers escape hatches** — mitigations, early warning signals, or kill criteria

The pre-mortem that prevents the post-mortem. Skip with "skip devil's advocate" — but it runs by default on high-stakes decisions.

### 📓 Decision Journal
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

### 🎯 PM Maturity Adapter
Claude silently reads your experience level and adjusts:

- **Early-career PM** → Teaches frameworks as it applies them
- **Mid-career PM** → Focuses on blind spots and pressure-testing
- **Senior/Exec PM** → Sparring partner mode. Challenges directly.

Recalibrates as the conversation evolves.

### ⚡ Reverse Brief
Instead of asking 15 clarifying questions one by one, Claude batches them, states its own best-guess answers, and asks you to correct what's wrong. 10x faster than the usual back-and-forth.

### 🚨 Anti-Pattern Detection
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

## 🤖 AI Product Management Playbook

This section doesn't exist in any other PM skill. If you're building AI-powered products, traditional PM frameworks break in specific ways. This playbook addresses them.

### AI Uncertainty Stack
Traditional products have uncertain demand. AI products have uncertain demand **AND uncertain capability**. Before any AI feature spec, classify:

- **Capability uncertainty** — Can the model do this reliably? 95% accuracy is amazing for suggestions and catastrophic for medical diagnoses.
- **Evaluation uncertainty** — Can you even tell if it's working? If you can't evaluate, you can't iterate.
- **Behavior uncertainty** — Models update. Your feature changes without you shipping code.

### AI Feature Spec Additions
Every AI feature spec gets these sections automatically:

- **Failure Mode Taxonomy** — graceful, silent, and catastrophic failures, each with required UX responses
- **Confidence UX Decision** — when to show uncertainty to users (product decision, not engineering default)
- **Human-in-the-Loop Design** — review points, cost of review, removal thresholds
- **Evaluation Rubric** — concrete rated examples defining "good enough" before engineering starts
- **Model Dependency Documentation** — version, deprecation plan, migration path

### AI-Specific Metrics

| Metric | What It Captures |
|---|---|
| **Task completion rate** | Did the AI actually solve the problem? |
| **Edit/override rate** | Is this a starting point or a solution? |
| **Automation trust curve** | Is user reliance growing over time? |
| **Fallback rate** | How often do users abandon AI and do it manually? |
| **False confidence rate** | How often is the AI wrong but appears confident? |

### Also includes:
- **Build vs. Buy vs. Wrap** decision matrix for AI with defensibility pressure-testing
- **AI Ethics Checklist** — bias audits, transparency, data usage, failure impact, reversibility
- **AI Roadmap Dynamics** — capability cliffs, "good enough" thresholds, prompt engineering as product work, eval-driven development, compounding data advantages
- **AI Competitive Analysis** — data moats, model strategy, eval rigor, integration depth, trust signals

---

## Full Framework Coverage

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

## Usage Examples

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

## Install

### Claude Code (recommended — auto-updates)

```bash
# Add the marketplace (one-time)
/plugin marketplace add shahcolate/product-kit

# Install this plugin
/plugin add strategic-pm
```

Enable auto-update when prompted. New versions — new frameworks, better anti-pattern detection, expanded AI playbook — sync automatically. No re-downloading.

### Claude.ai (manual upload)

1. Download `strategic-pm-v1.0.0.zip` from the [Releases page](../../releases)
2. Go to **Settings → Capabilities → Skills**
3. Click **"Upload skill"** and upload the ZIP

### Team & Enterprise

Organization Owners can provision this plugin centrally from admin settings. One upload covers your entire product team.

---

## What's in this plugin

```
plugins/strategic-pm/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
└── skills/
    └── strategic-pm/
        └── SKILL.md         # 500+ lines of PM instruction
```

---

<p align="center">
  <strong>Stop filling templates. Start thinking.</strong>
</p>
