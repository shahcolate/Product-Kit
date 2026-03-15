# Changelog

All notable changes to ProductKit will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.5.0] - 2026-03-15

### Added — Functional Tools

ProductKit expands beyond behavioral plugins into standalone CLI tools that do real work for product teams.

- **Feedback Synthesizer** (`scripts/feedback_synth.py`) — ingest user feedback from CSV/JSON, cluster by theme using multi-phase AI pipeline (extract → merge → assess), produce structured synthesis with quotes, sentiment, urgency, and actionability assessment
- **Release Notes Generator** (`scripts/release_notes.py`) — read git log (commit range, tag range, or date range), AI-classify changes, generate polished internal (eng-facing) and external (customer-facing) release notes with audience-appropriate language
- **Competitive Screenshot Monitor** (`scripts/competitor_watch.py`) — capture competitor pages via headless Playwright browser, use Claude vision for semantic diff vs. previous captures ("they removed the free tier" not "7 pixels moved"), cross-competitor synthesis for strategic patterns
- **Onboarding Flow Auditor** (`scripts/onboarding_audit.py`) — auto-navigate signup/onboarding flows via AI-driven CTA detection, capture each screen, produce per-screen friction scoring and full-flow synthesis with A-F grade
- **Tutorial Creator** (`scripts/tutorial.py`) — take a URL + natural language goal, AI-plan navigation steps, execute in headless browser with screenshot capture, annotate each step, assemble into a complete tutorial with `index.md` + `screenshots/` directory

### Added — Shared Infrastructure

- `scripts/_common.py` — extracted shared utilities: `repo_root()`, `slugify()`, terminal box-drawing helpers, Anthropic client initialization, common argparse setup (`--model`, `--output`, `--save`), async text and vision API call helpers
- `requirements.txt` — base dependencies (`anthropic`)
- `requirements-browser.txt` — browser tool dependencies (`playwright`, `Pillow`), includes base requirements

### Changed — README

- New "Functional Tools" section with usage examples for all 5 tools
- Repo structure diagram updated with new scripts, requirements files, and output directories
- Version badge updated to 1.5.0

## [1.4.0] - 2026-03-15

### Added — PM Interview Prep Plugin
- New plugin: PM Interview Prep — senior PM interview coach for Claude
- 321-line SKILL.md covering product sense (JTBD-framed), execution, estimation (structured decomposition), and behavioral (STAR format) question coaching
- Mock interview mode: Claude plays interviewer, asks follow-ups, then scores on 4-dimension rubric
- Anti-pattern detection for 6 common interview answer failures (too broad, no metrics, no tradeoffs, solution-first, no user empathy, rambling)
- Company-type calibration for FAANG, growth-stage, enterprise, and consumer interviews
- `evals/pm-interview-prep/cases.json` — 6 behavioral eval cases
- `plugins/pm-interview-prep/README.md` — plugin deep-dive and install guide
- Added to `marketplace.json` and `.claude-plugin/marketplace.json`

### Added — Teardown Enhancements
- `--vs` comparison mode: head-to-head product analysis across 6 dimensions + 7th "Head-to-Head Verdict" (e.g., `python scripts/teardown.py "Notion" --vs "Coda"`)
- `--output social` format: thread-ready summary with hook, 5 bullet verdicts, and bottom line
- Async parallel API calls via `asyncio` + `anthropic.AsyncAnthropic` — ~4x faster teardowns
- 4 example teardowns in `examples/teardowns/`: Notion, Linear, Figma, ChatGPT

### Added — Eval Enhancements
- `--baseline` flag for `run_evals.py`: runs each case with and without the skill, shows per-case and overall behavioral lift scores
- 5 new strategic-pm eval cases (spm-008 through spm-012): Why Now pressure test, second-order consequence identification, Decision Journal generation, PM Maturity Adapter detection, GTM launch tiering
- 5 new product-writing-studio eval cases (pws-008 through pws-012): passive voice detection, board deck narrative structure, stakeholder email format, one-pager length enforcement, wall-of-text anti-pattern
- Total eval coverage: 30 cases across 3 plugins (was 14 across 2)

### Added — Community Loop
- GitHub Action: teardown-on-issue (`teardown.yml`) — label an issue `teardown`, get results as a comment
- Issue template: `teardown_request.md` for zero-barrier teardown requests
- 5/day rate limit to manage API costs

### Changed — README
- New "Example Teardowns" section with links to 4 product teardowns
- PM Interview Prep listed as ✅ Live in Available Plugins and Marketplace Roadmap
- Teardown Tool section updated with `--vs`, `--output social` docs
- Eval Harness section updated with `--baseline` mode docs
- New "Teardown-on-Issue" section
- Repo structure diagram updated
- Eval badge updated to 30 cases
- Version badge updated to 1.4.0

## [1.3.0] - 2026-03-08

### Added — AI Product Teardown Tool
- `scripts/teardown.py` — CLI tool that runs any product through Strategic PM's full framework battery
- 6-dimension analysis: JTBD & Value Prop, Competitive Moat (7 Powers), Growth Model, Anti-Pattern Scan (all 13), Monetization, Strategic Verdict
- Multi-call architecture: each dimension gets its own focused API call with Strategic PM as system prompt for higher-quality output
- Terminal output with box-drawing formatting (screenshot-ready) and Markdown output for sharing
- `--save` flag writes reports to `teardowns/` directory
- `--context` flag for adding product context (helps with obscure products)
- `--model` flag for model selection (defaults to claude-sonnet-4-6)
- `teardowns/` directory with `.gitkeep`; generated reports gitignored

### Changed — README
- Added AI Product Teardown Tool section with usage examples
- Repo structure diagram updated to include `teardown.py` and `teardowns/`
- Version badge updated to 1.3.0

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
