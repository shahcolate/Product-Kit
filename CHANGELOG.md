# Changelog

All notable changes to ProductKit will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.2.0] - 2026-03-08

### Added — Behavioral Eval Harness
- LLM-as-judge eval harness for automated behavioral verification of plugin skills
- Two-call architecture: subject call (skill as system prompt) + grader call (per-criterion scoring)
- `evals/strategic-pm/cases.json` — 7 behavioral eval cases covering reverse-brief, anti-pattern detection, devil's advocate, who-loses rule, JTBD reframing, confidence labeling, and AI uncertainty stack
- `evals/product-writing-studio/cases.json` — 7 behavioral eval cases covering audience-first, buried lede detection, jargon flagging, SCQA structure, so-what on data, missing ask detection, and reading time mismatch
- `scripts/run_evals.py` — eval runner with `--plugin`, `--output json`, and `--model` flags; exits 1 on any case below 75% weighted threshold
- `.github/workflows/eval.yml` — manual-trigger CI workflow writing results to GitHub Actions Job Summary
- `evals/README.md` — full methodology doc: architecture, schema reference, how to run, how to add cases, cost, limitations
- Version drift warning: runner prints a warning when `cases.json` version doesn't match `plugin.json` version

### Changed — README
- Rewritten hero to lead with eval-driven differentiation: "Most AI plugins hope they work. ProductKit proves it."
- New "What Sets This Apart" section above the fold explaining the two-call LLM-as-judge architecture
- Behavioral Evals badge updated to show passing case count
- Repo structure diagram updated to include `evals/` and `scripts/` directories

## [1.1.0] - 2026-03-08

### Added — Product Writing Studio Plugin
- New plugin: Product Writing Studio — expert product communicator for Claude
- Audience-First Protocol: identifies reader, context level, and decision/feeling goal before writing
- Pyramid Principle enforcement: recommendation leads, support follows; buried ledes flagged and restructured
- SCQA Structure (Situation → Complication → Question → Answer) for all strategic writing
- Five Clarity Laws: jargon check, passive voice check, sentence length check, reading time estimate, "So What?" on data
- Anti-Pattern Detection: buried lede, walls of text, false urgency, defensive hedging, jargon overuse, metric theater, accomplishment lists, missing asks
- Document Type Intelligence for 8 formats: exec updates, strategy memos, board deck narratives, stakeholder emails, product announcements, one-pagers, design briefs, launch comms
- Draft review mode: structural critique + tracked rewrites with reasoning
- `plugins/product-writing-studio/README.md` — full plugin deep-dive and install guide

### Changed — README restructure
- Root README.md slimmed to a clean marketplace index
- Strategic PM and Product Writing Studio plugin deep-dives moved to per-plugin READMEs
- `plugins/strategic-pm/README.md` created — full plugin detail, standalone readable
- Repo structure diagram updated to reflect per-plugin README pattern
- Available Plugins table and Marketplace Roadmap updated with links and new statuses
- Version badge updated to 1.1.0

## [1.0.0] - 2026-02-26

### Added — Strategic PM Plugin
- Initial release of the Strategic PM plugin
- Core PM frameworks: JTBD, Opportunity Solution Trees, Assumption Mapping, RICE/ICE prioritization
- The Five Laws: So What filter, Who Loses rule, Why Now pressure test, Confidence Labels, Second-Order Consequence Scan
- Devil's Advocate Protocol for stress-testing strategies and major decisions
- Decision Journal for institutional memory with review triggers
- PM Maturity Adapter that auto-adjusts to junior, mid, and senior PM experience levels
- Reverse Brief protocol for faster context-gathering
- Anti-Pattern Detection Engine (feature factories, vanity metrics, roadmap theater, and 9 more)
- User Research Synthesis Engine (interviews, surveys, support tickets, competitive reviews)
- Business Model Literacy (unit economics, monetization models, pricing strategy)
- Growth & Retention Models (acquisition loops, 3 retention horizons)
- Go-to-Market Playbook with launch tiering and rollout sequencing
- Technical Collaboration Framework (spec calibration, Why Stack, tech debt translation)
- Product Health Diagnostics (5-Layer Audit)
- Stakeholder Chessboard with "When the CEO Wants a Feature" protocol
- Competitive Intelligence (signal classification, response protocol, honest market sizing)
- PM Operating Rhythm (weekly priorities, OKR standards)
- **AI Product Management Playbook**:
  - AI Uncertainty Stack (capability, evaluation, behavior uncertainty)
  - AI Feature Spec additions (failure mode taxonomy, confidence UX, human-in-the-loop, eval rubrics, model dependency docs)
  - AI-specific metrics (task completion, edit/override rate, automation trust curve, fallback rate, false confidence rate)
  - Build vs. Buy vs. Wrap decision matrix for AI
  - AI Ethics Checklist
  - AI roadmap dynamics (capability cliffs, good-enough thresholds, prompt engineering as product work, eval-driven development, compounding data advantages)
  - AI competitive analysis framework
- Document output standards for PRDs, roadmaps, strategy memos, experiment designs, and exec updates
- Edge case protocols for 11 common PM scenarios

### Added — ProductKit Marketplace
- Marketplace structure supporting multiple independent plugins
- CONTRIBUTING.md with full guide for improvements, bug reports, and new plugin proposals
- Plugin development guide with templates and quality bar
- Claude Code auto-update support via plugin marketplace
- Pre-built ZIP releases for Claude.ai manual upload
