# ✍️ Product Writing Studio — Plugin for ProductKit

**Claude becomes an expert product communicator — not a generic writer.**

It knows the structure, audience, and purpose of every product writing format. It refuses to produce output that buries the recommendation, uses jargon without justification, or mistakes a data dump for a narrative.

← [Back to ProductKit marketplace](../../README.md)

---

## The Problem

Claude is a capable writer. Ask it for a strategy memo and you'll get a well-formatted document — with the recommendation buried in paragraph 4, a subject line that says "Q3 Planning" instead of "Decision needed: headcount by Friday," and at least three instances of "leverage" used as a verb.

It produces professional-looking product writing with no structural thinking underneath.

## The Fix

Product Writing Studio rewires how Claude approaches written communication. It doesn't clean up prose — it interrogates structure, challenges audience assumptions, and refuses to let you ship writing that fails at its actual job.

**Before installing:**
> "Here's a strategy memo summarizing the options you outlined."

**After installing:**
> "Before I write this — who's the primary reader and what do you need them to decide or feel? Your draft buries the recommendation in paragraph 4. I'll lead with it. Also, 'leverage synergistic alignment' is doing no work here — I'll replace it with what you actually mean."

---

## What Makes This Different

### 👥 Audience-First Protocol
Before writing anything, Claude identifies the reader, their context level, and their decision or feeling goal. Every structural choice traces back to what that specific reader needs.

### 🔺 Pyramid Principle (Non-Negotiable)
Recommendation leads. Support follows. Claude will always restructure documents where the point is buried — and explain why.

### 📐 SCQA Structure
Situation → Complication → Question → Answer. Claude applies this to all strategic writing at the document level and section level.

### ✂️ Clarity Laws
Five checks run on every output:
- **Jargon check** — every piece of jargon must do work that a plain word cannot
- **Passive voice check** — passive voice that hides the agent gets rewritten
- **Sentence length check** — anything over 35 words is a split candidate
- **Reading time estimate** — stated for every document; mismatches flagged
- **"So What?" on data** — every data point must connect to an implication

### 📄 Document Type Intelligence
Claude knows the specific structure, audience, and purpose of each format — not just how to write, but what each document is *for*.

### 🚨 Anti-Pattern Detection
Claude flags and refuses to enable:
- Buried ledes (recommendation not in the first sentence)
- Walls of text (no structure, no visual breaks)
- False urgency (unsubstantiated "critical" and "urgent")
- Defensive hedging (softening claims until they mean nothing)
- Jargon overuse (hiding behind vocabulary)
- Metric theater (quoting numbers without implications)
- The accomplishment list (listing what was done, not why it mattered)
- The missing ask (no clear next action at the end)

---

## Document Types Covered

| Document | Target | Key Requirement |
|---|---|---|
| **Executive updates** | 90-second read | Max 3 key messages, status + risk + ask |
| **Strategy memos** | Decision-ready | SCQA + steelman + decision details |
| **Board deck narratives** | Context-rich | Headline = implication, not topic label |
| **Stakeholder emails** | Specific ask | Ask in first sentence, detail matched to audience |
| **Product announcements** | Benefit-led | Plain language, one action, no hype superlatives |
| **One-pagers** | Single recommendation | Literally one page, 2-4 sentences per section |
| **Design briefs** | Problem framing | Problem + constraints + success criteria |
| **Launch comms** | Internal + external | Right detail for each audience, what-if contingencies |

---

## Usage Examples

Once installed, Claude handles product writing automatically:

**Review a draft:**
> "Here's my exec update for the leadership sync — can you review it?"

**Write from scratch:**
> "I need a strategy memo recommending we move to usage-based pricing. The primary reader is the CFO."

**Improve a stakeholder email:**
> "Help me write an email to Engineering leadership asking for 2 extra weeks on the deadline."

**Structure a board narrative:**
> "I need to write the product section of our board deck. We're showing Q3 results and introducing our AI roadmap."

**Draft an announcement:**
> "Write a product announcement for our new collaboration feature — audience is existing customers."

---

## Behavioral Examples

**Before (no skill):**
> "Here's your strategy memo with an overview of options and considerations."

**After (with skill):**
> "Your current draft has the recommendation in paragraph 4. The CFO reading this cold won't get there — I'm leading with it. I've also replaced 'leverage cross-functional alignment' with 'get engineering and design working from the same spec by EOQ' because that's what you actually mean. Reading time is now 4 minutes, down from 9."

---

**Before (no skill):**
> "Subject: Q3 Update — here's a summary of what the team shipped this quarter."

**After (with skill):**
> "Subject line rewritten to 'Q3: On track on revenue, one retention risk to flag.' Your body currently lists 7 things the team did. I've compressed that to 3 things that matter to this audience and added the 'so what' for each one. I've also added a clear ask in the last paragraph — you need a decision on Q4 headcount by Friday and the current draft doesn't say that."

---

## Install

### Claude Code (recommended — auto-updates)

```bash
# Add the marketplace (one-time)
/plugin marketplace add shahcolate/product-kit

# Install this plugin
/plugin add product-writing-studio
```

Enable auto-update when prompted. Improvements sync automatically.

### Claude.ai (manual upload)

1. Download `product-writing-studio-v1.1.0.zip` from the [Releases page](../../releases)
2. Go to **Settings → Capabilities → Skills**
3. Click **"Upload skill"** and upload the ZIP

### Team & Enterprise

Organization Owners can provision this plugin centrally. One upload covers every PM, designer, or leader on your team who sends stakeholder emails, writes memos, or presents to the board.

---

## What's in this plugin

```
plugins/product-writing-studio/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
└── skills/
    └── product-writing-studio/
        └── SKILL.md         # Full writing instruction set
```

---

<p align="center">
  <strong>Stop writing documents. Start moving readers.</strong>
</p>
