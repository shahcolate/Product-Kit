# Contributing to ProductKit

Thanks for wanting to make this better. ProductKit gets sharper when people who build real products contribute to it — PMs, designers, engineers, researchers, data scientists, founders.

There are three ways to contribute, from lightweight to ambitious:

1. **Improve an existing plugin** — add a framework, fix a misapplication, add an edge case
2. **Report an issue** — Claude did something wrong with a plugin installed? Tell us.
3. **Propose and build a new plugin** — have a workflow for your discipline that would benefit others? Build it.

---

## 1. Improving an Existing Plugin

This is the most common and most valuable contribution.

### What makes a good improvement

- **New frameworks** that are battle-tested, not theoretical. If you've only read about it but never applied it in real product work, it's not ready.
- **Edge case protocols** for scenarios the plugin doesn't cover yet. Format: "If [situation], then [what Claude should do]."
- **Anti-patterns** you've seen in the wild. Real failure modes you've witnessed or committed yourself.
- **Cross-discipline additions** — PM plugins that help PMs collaborate better with designers, design plugins that account for engineering constraints, etc.
- **AI-specific additions** — this space moves fast. AI playbooks should stay current.
- **Bug fixes** — if Claude misapplies a framework or triggers at the wrong time, fix the instruction.
- **Clarity improvements** — if a section is ambiguous and Claude interprets it inconsistently, tighten the language.

### What we'll push back on

- Generic advice that anyone could find with a quick search
- Frameworks without clear application instructions — Claude needs to know *when* to apply it, *how* to apply it, and *what the output looks like*, not just *what* the framework is
- Additions that duplicate existing coverage
- Content that inflates the plugin without adding signal (plugins have a practical length limit — every line needs to earn its place)
- Prescriptive tone policing — each plugin's communication style is intentional
- Promotional content or links to paid products

### How to submit

1. **Fork** this repo
2. **Create a branch** with a descriptive name (`git checkout -b add-wardley-mapping-protocol`)
3. **Edit the SKILL.md** for the relevant plugin (e.g., `plugins/strategic-pm/skills/strategic-pm/SKILL.md`)
4. **Update CHANGELOG.md** with a brief description under an `[Unreleased]` section
5. **Submit a PR** with:
   - **What you changed** — the specific section added or modified
   - **Why it matters** — what scenario this addresses
   - **How you've used it** — even a sentence about real-world application helps reviewers
   - **Testing notes** — if you tested the change with Claude, share what you asked and what Claude did differently

### Style guide for skill instructions

Skills are read by Claude, not by humans (though humans review them). Write accordingly:

- **Use imperative form.** "Reframe every feature as a job" not "Features should be reframed as jobs."
- **Explain why, not just what.** Claude follows instructions better when it understands the reasoning. "Flag survivorship bias because the analysis only captures users who stayed — the ones who left might tell a different story" is better than "Flag survivorship bias."
- **Be specific about triggers.** "When the user presents a roadmap without stated capacity assumptions" is better than "When relevant."
- **Include examples when the concept is subtle.** Especially for anti-patterns and edge cases — show Claude what the bad version looks like and what the good version looks like.
- **Don't over-specify tone.** Each plugin has a communication style section. New sections should inherit from it, not override it.
- **Keep tables for reference, prose for logic.** Tables are good for lookup (metric definitions, model comparisons). Prose is better for decision logic and protocols.

### Structural conventions

- Use `###` headers for major sections, `####` for subsections
- Framework names get **bold** on first mention within a section
- Anti-patterns follow the format: **Name** — one-line description of the failure mode
- Edge case protocols follow: **If [condition]**: [what Claude should do]
- Confidence labels use the standard emoji: 🟢 High, 🟡 Medium, 🔴 Low

---

## 2. Reporting Issues

If Claude does something wrong with a plugin installed, that's a bug.

### What counts as a bug

- Claude **ignores a protocol** — e.g., writes a PRD without running the Reverse Brief
- Claude **misapplies a framework** — e.g., uses RICE when ICE would be more appropriate
- Claude **triggers on the wrong task** — e.g., runs the Devil's Advocate Protocol on a simple factual question
- Claude **doesn't trigger when it should** — e.g., doesn't use the AI Playbook when the user is clearly speccing an AI feature
- Claude **produces output that contradicts the plugin's instructions** — e.g., hides uncertainty despite the Confidence Label law

### How to report

[Open an issue](../../issues) with:

1. **What you asked Claude** — the prompt or conversation context
2. **What Claude did** — paste the relevant output
3. **What you expected** — which part of the plugin should have applied
4. **Your setup** — Claude Code plugin, Claude.ai upload, or API

Screenshots or full conversation exports are especially helpful.

---

## 3. Proposing a New Plugin

We want ProductKit to grow across product disciplines. If you have a workflow — for design, engineering, research, data, ops, or anything else involved in building products — that would benefit from a dedicated Claude plugin, propose it.

### Before you propose

Check the [Marketplace Roadmap](README.md#marketplace-roadmap) in the README. Your idea might already be planned. If it is, open an issue to express interest and share your perspective — it helps us prioritize.

### Plugin proposal process

1. **Open an issue** with the title: `[Plugin Proposal] Your Plugin Name`
2. Include:
   - **What the plugin does** — one paragraph
   - **Who it's for** — which role(s) and what workflow
   - **Why it's separate** — why this shouldn't be folded into an existing plugin
   - **3 example prompts** — what would a user say to trigger this?
   - **Key behaviors** — how should Claude act differently with this plugin installed?
3. **Discussion** — we'll ask questions, suggest scope changes, and decide whether to greenlight
4. **Build** — once approved, follow the development guide below

### Plugin ideas we'd love to see

These are starting points, not prescriptions. Surprise us.

- **UX Strategy** — heuristics evaluation, cognitive load analysis, interaction pattern selection, accessibility audits, design system constraints
- **Research Ops** — interview guide generation, synthesis protocols, survey design, participant screening criteria
- **Engineering Collaboration** — technical spec reviews, architecture decision records, API design principles, tech debt prioritization
- **Data & Experimentation** — experiment design rigor, statistical significance checks, metric definition standards, dashboard critique
- **Product Marketing** — positioning frameworks, messaging hierarchies, competitive messaging, launch narratives
- **Product Ops** — process audits, ceremony design, tooling evaluation, cross-team coordination protocols

### Plugin development guide

Every plugin follows the same structure:

```
plugins/
└── your-plugin-name/
    ├── .claude-plugin/
    │   └── plugin.json          # Plugin manifest
    └── skills/
        └── your-plugin-name/
            └── SKILL.md         # The actual skill instructions
```

#### plugin.json template

```json
{
  "name": "your-plugin-name",
  "description": "One-line description of what the plugin does and when to trigger it.",
  "version": "1.0.0",
  "skills": ["./skills/your-plugin-name"]
}
```

#### SKILL.md requirements

Your SKILL.md must include YAML frontmatter:

```yaml
---
name: your-plugin-name
description: >
  Detailed description including trigger conditions. Be specific about when
  Claude should load this skill. Include keywords and phrases users might
  say. Err on the side of "pushy" — undertriggering is more common than
  overtriggering.
---
```

After the frontmatter, write the skill instructions in Markdown. Refer to the Strategic PM plugin (`plugins/strategic-pm/skills/strategic-pm/SKILL.md`) as an example of structure and style.

#### Quality bar for new plugins

- **Minimum 100 lines of instruction.** Anything shorter probably belongs as a section in an existing plugin.
- **At least 3 distinct behavioral changes.** A plugin should change how Claude acts in multiple ways — not just apply a single framework.
- **Clear trigger boundaries.** The skill description must make it obvious when this plugin activates vs. when other ProductKit plugins handle it.
- **No overlap with existing plugins.** If your plugin covers territory another plugin already handles, propose it as an improvement instead.
- **Tested with Claude.** Before submitting, use your plugin with Claude on at least 3 real tasks. Include the test results in your PR.

#### Submitting a new plugin

1. Fork the repo
2. Create your plugin directory under `plugins/`
3. Add your plugin to `marketplace.json` in the `plugins` array
4. Add a section to CHANGELOG.md
5. Submit a PR with:
   - Link to the approved proposal issue
   - The 3+ test conversations you ran with Claude
   - A brief entry for the README's plugin table

---

## Review Process

- **Small improvements** (typo fixes, clarity edits, minor additions): reviewed within a few days
- **New frameworks or sections**: reviewed within a week. May request changes.
- **New plugins**: reviewed within two weeks. Expect 1-2 rounds of feedback.

All PRs need at least one approval before merging. For new plugins, we'll test with Claude ourselves before approving.

---

## Code of Conduct

Be constructive. Disagree with reasoning, not with people. We're all here to build better tools for product teams.

If a PR gets rejected, it's not personal — it means the contribution didn't meet the bar for this specific project. The feedback should help you understand why and what would need to change.

---

## Recognition

Contributors are recognized in:
- The CHANGELOG.md for their specific contribution
- The repo's GitHub contributors list
- Shoutouts in release announcements for significant additions

---

## Questions?

Open an issue tagged `question` or start a discussion. We're friendly.
