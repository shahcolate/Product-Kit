# When There's No Designer

Not every AI feature has a designer. Backend migrations, data pipelines, internal tools, and infra features ship with a PM and engineers. MVC still works. You adapt a few sections and skip the ones that don't apply.

## What changes

### Objective + Non-Goals
No change. Every feature has an objective and non-goals, whether it's user-facing or not. Your persona might be "on-call SRE" or "data pipeline downstream consumer" instead of an end user.

### Constraints
No change. Technical features often have stricter constraints than user-facing ones. A payment migration has PCI DSS, backward compatibility, and rollback SLAs. Fill this section thoroughly.

### Acceptance Tests
Drop the `experience` category. Keep `functional` and `performance`. For technical features, your acceptance tests are usually: regression suite passes, parity check passes, rollback within SLA.

### Tools and Boundaries
No change. If anything, this section matters more for technical features because the blast radius of accessing the wrong data source is larger (production databases, payment systems).

### Canonical Examples
Still valuable, but the examples are API calls and system states instead of user scenarios. Show: normal operation, dual-write parity, and rollback.

### Fallback Behavior
Without a designer, nobody is thinking about graceful degradation UX. For technical features, the fallback is usually: revert to the previous system. Be explicit about the trigger, the mechanism, and the SLA.

## Summary

| Section | With Designer | Without Designer |
|---|---|---|
| Objective + Non-Goals | Full | Full |
| Constraints | Full | Full (often stricter) |
| Acceptance Tests | Functional + Performance + Experience | Functional + Performance only |
| Tools and Boundaries | Full | Full |
| Canonical Examples | User scenarios | System states and API calls |
| Fallback | UX degradation path | System revert path |

## Reference

See `templates/mvc-example-backend-migration.yaml` for a complete example. The persona is an internal engineering team. There are no experience tests. The fallback is automatic traffic rerouting. The canonical examples are API requests and rollback scenarios.
