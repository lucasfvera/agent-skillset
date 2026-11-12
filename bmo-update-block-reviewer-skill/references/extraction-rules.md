# Extraction rules — PR feedback to domain & tier rules

## Goal

Distill raw PR review threads into **one-line, positive-target rules** classified by **domain** (`core | frontend | backend | database | testing`) and **tier** (`issue | style`).

## 1. Domain routing (`domain`)

Pick the narrowest file layer the rule governs:

| Domain | Target file in `bmo-block-reviewer` | Triggers / scope |
|--------|-------------------------------------|------------------|
| `core` | `SKILL.md` | Universal TypeScript typing, strict equality, error narrowing, decimal math, secret logging, general DRY/helper/comment hygiene |
| `frontend` | `references/frontend.md` | UI components, client hooks, form/view state, event handlers vs effects, DOM structure, CSS/design tokens |
| `backend` | `references/backend.md` | HTTP/gRPC/message handlers, routes, middleware, service boundaries, HTTP/auth status mapping, wire schemas/protos, codegen |
| `database` | `references/database.md` | SQL queries, repositories/stores, DB transactions/locks, `CHECK` constraints, migrations |
| `testing` | `references/testing.md` | Unit, component, and integration specs (`*.test.*`, `*.spec.*`), fixtures, mocks, query priority, suite harnesses/ports |

## 2. Severity tier (`tier`)

| Tier | Meaning | Examples |
|------|---------|----------|
| `issue` | Violating the rule causes wrong runtime output, broken wire/DB contracts, wrong HTTP/auth status codes, leaked secrets or raw DB errors, held DB transactions/locks, hot-path latency, parallel test port races, or vacuous/flaky tests | `auth-identity-is-401`, `validate-before-transaction`, `log-presence-not-secrets`, `test-unit-owned-contract`, `no-settimeout-sleeps` |
| `style` | Code runs accurately and performs fine; the rule encodes structure, file layout, helper granularity, DRY conventions, comments, or test readability | `single-return-formatters`, `avoid-thin-wrappers`, `one-handler-per-file`, `test-aaa-pattern`, `prefer-design-tokens` |

## 3. Wording rules

1. **Prompt the positive target first:** Lead with what to write (`Compare values with strict equality...`), pairing a brief `never`/`rather than` clause only as a guardrail.
2. **One line (`rule`):** `<Positive imperative>; <one-clause why or contrast>.`
3. **No file paths or verbatim PR quotes:** Keep rules portable across repositories.
4. **Dismissed threads count when they encode a standing rule:** A `Keeping as-is` resolution that states a repeatable boundary preference ("Keep pure internal mappers free of try/catch; handle errors at the I/O boundary") yields a valid rule.

## 4. When to skip

- One-off factual fixes (typos, wrong enum literal in one feature).
- Feedback tied to a temporary feature flag or a single file's legacy quirk.
- Rules already covered by an existing ID in [`ledger.md`](../ledger.md) (append the PR to `sources` instead).

## Examples

### Example A — `tier: issue`, `domain: database`

> Reviewer: "Don't open `db.transaction` before checking if the request body is valid."
> Resolution: Valid. Moved validation above `db.transaction`.

```yaml
id: validate-before-transaction
domain: database
tier: issue
rule: Run format and precondition validation before opening a database transaction so invalid requests never acquire or hold scarce connections.
sources: [acme/payments#104]
status: promoted
```

### Example B — `tier: style`, `domain: core`

> Reviewer: "Can we assign the result in each branch and have a single `return` at the bottom of this formatter?"
> Resolution: Valid. Refactored to single return.

```yaml
id: single-return-formatters
domain: core
tier: style
rule: Structure pure formatter functions around one assignment path and a single return at the end.
sources: [acme/web#412]
status: candidate
```
