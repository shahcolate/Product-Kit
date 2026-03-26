# QA Tester -- Autonomous Browser-Based QA Agent

Claude becomes a QA engineer who opens the browser, navigates your web app like a real user, tries to break things, and files bugs with full reproduction steps.

## What it does

1. **Discovery** -- Asks about the app, what changed, what to test, where to file bugs
2. **Test plan** -- Builds a structured plan using real testing methodology (boundary analysis, state transitions, error paths, exploratory testing). You confirm before it starts.
3. **Execution** -- Opens the browser, navigates, clicks, fills forms, screenshots everything
4. **Bug filing** -- Files each bug in Linear or JIRA with steps, screenshots, severity, and environment details
5. **Report** -- Summarizes results with a ship/no-ship recommendation

## Testing methodologies used

- Equivalence partitioning
- Boundary value analysis
- State transition testing
- Error path testing
- Exploratory testing (time-boxed, charter-based)
- Security spot checks (XSS, IDOR, auth bypass)
- Accessibility spot checks (focus order, labels, contrast)

## Modes

| Command | What happens |
|---------|-------------|
| "Smoke test [url]" | Quick P0-only check of core flows |
| "Regression test [url]" | Focused testing around recent changes |
| "Full QA [url]" | Comprehensive pass across all methodologies |
| "Pre-launch check [url]" | Ship/no-ship assessment of a release candidate |

## Bug tracker integration

Supports Linear and JIRA. Configure during the discovery phase:

- **Linear**: Specify team/project and labels. Bugs filed via Linear MCP or CLI.
- **JIRA**: Specify project key and issue type. Bugs filed via JIRA MCP or CLI.
- **No tracker**: Bugs reported inline in the conversation.

## Requirements

- **Claude Cowork** (or any Claude environment with browser/computer use)
- Linear or JIRA MCP integration (optional, for automatic bug filing)

## Install

### Claude Code
```bash
/plugin add qa-tester
```

### Claude.ai
Upload the plugin ZIP via Settings > Capabilities > Skills.

## Example

```
User: Smoke test https://staging.myapp.com -- we just deployed a new checkout flow.
      Login is test@example.com / password123. File bugs in Linear, team "Engineering".

Claude: [asks follow-up questions if needed]
Claude: [builds test plan, presents for confirmation]
User: Looks good, go.
Claude: [opens browser, executes tests, files bugs as found]
Claude: [presents summary report]
```
