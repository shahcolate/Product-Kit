# PM Interview Prep — Plugin for ProductKit

**Turn Claude from a generic Q&A bot into a senior PM interview coach who actually gets you hired.**

200+ lines of interview coaching instruction. Structured answer frameworks, mock interview mode, calibrated scoring rubrics, and anti-pattern detection tuned to how real interviewers evaluate.

<- [Back to ProductKit marketplace](../../README.md)

---

## The Problem

Claude can answer PM interview questions. It can even give you frameworks. But it can't tell you that your answer — while technically correct — would get you a "Lean No Hire" at Google because you skipped metrics, rambled for 8 minutes, and never named a single tradeoff.

Generic interview prep produces generic candidates. And generic candidates don't get offers.

## The Fix

PM Interview Prep rewires Claude into a coach who has seen 500+ mock interviews and knows exactly what separates a "Hire" from a "No Hire" on a real scorecard.

**Before installing:**
> "Here are some frameworks for product sense questions: consider the user, think about solutions, and define metrics."

**After installing:**
> "You jumped to a solution in your first sentence. That's the #1 product sense killer. Let me hear the user problem first — who has this problem, when do they have it, and how are they solving it today? Also, your answer would take 8 minutes. You have 5. Cut the Situation to 15 seconds and get to the Action."

---

## What Makes This Different

### Four Question Types, Four Answer Structures
Product sense, execution, estimation, and behavioral questions each require a distinct structure. Mixing them is a silent failure mode this skill catches and corrects.

### Mock Interview Mode
Claude plays the interviewer. Asks real questions, probes with follow-ups, then debriefs with a calibrated rubric — structure, insight depth, tradeoff awareness, and communication clarity. Each answer gets a weighted score and a hire/no-hire verdict.

### Anti-Pattern Detection
Six answer killers that get candidates rejected even when the content is correct:
- Too broad (no specificity)
- No metrics (can't quantify impact)
- No tradeoffs (everything is positive)
- Solution-first (skips problem framing)
- No user empathy (talks about product, not people)
- Rambling (no structure)

### Company-Type Calibration
The same answer scores differently at Google vs. a Series C startup vs. Salesforce vs. Spotify. This skill calibrates feedback to the company type: FAANG, growth-stage, enterprise, or consumer.

### The Feedback Protocol
Every answer gets scored on 4 dimensions (structure, insight, tradeoffs, clarity) with a weighted score mapped to a verdict: Strong Hire through No Hire. Plus the strongest moment, biggest gap, and a rewritten model answer.

---

## Usage Examples

Once installed, just practice. The skill triggers automatically:

**Run a mock interview:**
> "Give me a mock PM interview for Google. Product sense focus."

**Practice a product sense question:**
> "How would you improve Instagram Stories?"

**Get feedback on an answer:**
> "Here's how I'd answer 'design a product for elderly users' — can you score it?"

**Practice estimation:**
> "How many Uber rides happen in NYC per day?"

**Work on behavioral answers:**
> "Tell me about a time you had to influence without authority — here's my answer..."

**Calibrate for a company:**
> "I'm interviewing at Stripe. What should I focus on?"

---

## Install

### Claude Code (recommended — auto-updates)

```bash
# Add the marketplace (one-time)
/plugin marketplace add shahcolate/product-kit

# Install this plugin
/plugin add pm-interview-prep
```

Enable auto-update when prompted. New versions — new question banks, refined rubrics, expanded company calibrations — sync automatically. No re-downloading.

### Claude.ai (manual upload)

1. Download `pm-interview-prep-v1.0.0.zip` from the [Releases page](../../releases)
2. Go to **Settings -> Capabilities -> Skills**
3. Click **"Upload skill"** and upload the ZIP

### Team & Enterprise

Organization Owners can provision this plugin centrally from admin settings. One upload covers your entire product team.

---

## What's in this plugin

```
plugins/pm-interview-prep/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
└── skills/
    └── pm-interview-prep/
        └── SKILL.md             # 200+ lines of interview coaching instruction
```

---

<p align="center">
  <strong>Stop practicing with generic feedback. Start training with a coach.</strong>
</p>
