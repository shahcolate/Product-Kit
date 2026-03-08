# Pull Request

## Summary

What does this PR change, and why?

## Type of change

- [ ] Improving an existing plugin (new framework, edge case, anti-pattern, fix)
- [ ] New plugin
- [ ] Documentation fix
- [ ] Infrastructure / tooling

---

## Checklist

### All PRs
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] No broken links in any modified `.md` files

### Plugin changes (new or updated)
- [ ] `plugin.json` updated (version bumped if this is a content change)
- [ ] `SKILL.md` instructions are in imperative form ("Do X", not "You should X")
- [ ] Each new framework includes: when to apply it, what it produces, an example
- [ ] Anti-patterns covered for any new framework
- [ ] Confidence labels (`🟢 High / 🟡 Medium / 🔴 Low`) used where appropriate

### New plugins only
- [ ] `.claude-plugin/plugin.json` created with correct `name`, `version`, `description`, `skills`
- [ ] `SKILL.md` file exists at the path referenced in `plugin.json`
- [ ] Example conversations included (before/after the skill is installed)
- [ ] Plugin listed in root `marketplace.json`

### Test conversations
Paste 1–2 example prompts and Claude's response with this skill active. This is the quality bar — if you can't show it working well, it's not ready.

**Prompt 1:**
> [your test prompt]

**Response:**
> [Claude's actual output]

---

## Breaking changes

Does this change alter existing behavior? If yes, describe what changes and why it's worth the disruption.
