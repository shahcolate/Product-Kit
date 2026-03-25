# MVC Ownership -- RACI Table

Every MVC section has a clear owner. This table defines who is Responsible (does the work), Accountable (owns the decision), Consulted (provides input), and Informed (notified after).

## Roles

| Abbr | Role |
|------|------|
| PM   | Product Manager |
| Des  | Designer |
| Eng  | Engineering Lead |

## RACI Matrix

| Activity | PM | Des | Eng |
|---|---|---|---|
| Write objective statement | A/R | C | C |
| Define non-goals | A/R | C | C |
| Set success criteria and targets | A/R | C | C |
| Identify compliance constraints | A | I | R |
| Set performance constraints (latency, cost) | C | I | A/R |
| Define data restrictions | A | I | R |
| Map allowed data sources | C | I | A/R |
| Map forbidden data sources | A | I | R |
| Define fallback behavior | A | R | R |
| Write acceptance tests (functional) | R | C | A/R |
| Write acceptance tests (experience) | C | A/R | I |
| Write acceptance tests (performance) | I | I | A/R |
| Create canonical examples | R | C | R |

## How to read this

- **R** -- Does the work.
- **A** -- Owns the decision. Signs off. One A per row.
- **C** -- Consulted before the decision.
- **I** -- Informed after.

## When there's no designer

Common for backend features, internal tools, and infra work. When there's no designer:

- PM absorbs the Des column. The PM owns fallback behavior and experience tests.
- Experience acceptance tests can be omitted if the feature has no user-facing output.
- See [when-no-designer.md](when-no-designer.md) for detailed guidance.
- See `templates/mvc-example-backend-migration.yaml` for a worked example with no designer.
