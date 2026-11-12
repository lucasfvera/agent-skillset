# Block reviewer learnings ledger

Updater-only state for [`bmo-update-block-reviewer-skill`](SKILL.md). **Reviewers (`bmo-block-reviewer`) never read this file**; active rules live in [`../bmo-block-reviewer/SKILL.md`](../bmo-block-reviewer/SKILL.md) (`core`) and [`../bmo-block-reviewer/references/`](../bmo-block-reviewer/references/) (`frontend`, `backend`, `database`, `testing`).

## Promotion thresholds

- **`tier: issue`** (correctness, contracts, security, performance, test validity): promotes to the target domain's `## 1. Strict issues ([issue])` section on **1+ PR source** when durable and repo-general.
- **`tier: style`** (structure, conventions, readability, test ergonomics): stays in **Candidates** below on its first PR and promotes to the target domain's `## 2. Style & conventions ([style])` section once it reaches **2+ PR sources** (or when explicitly promoted by the user).

---

## Candidates (1 PR source, `tier: style` — not yet active in reviewer)

| ID | Domain | Tier | Sources | Candidate rule |
|----|--------|------|---------|----------------|
| _(none pending)_ | — | — | — | — |

---

## Active promoted rules (indexed by domain & tier)

| ID | Domain | Tier | Sources | Target file |
|----|--------|------|---------|-------------|
| `no-any` | `core` | `issue` | baseline | `bmo-block-reviewer/SKILL.md` |
| `catch-unknown-not-any` | `core` | `issue` | 1+ | `bmo-block-reviewer/SKILL.md` |
| `strict-equality` | `core` | `issue` | 4 | `bmo-block-reviewer/SKILL.md` |
| `use-decimal-helpers` | `core` | `issue` | 1+ | `bmo-block-reviewer/SKILL.md` |
| `log-presence-not-secrets` | `core` | `issue` | 1+ | `bmo-block-reviewer/SKILL.md` |
| `no-empty-string-as-undefined` | `core` | `issue` | 1+ | `bmo-block-reviewer/SKILL.md` |
| `keep-canonical-separate-from-display` | `core` | `issue` | 2 | `bmo-block-reviewer/SKILL.md` |
| `hot-path-latency` | `core` | `issue` | baseline | `bmo-block-reviewer/SKILL.md` |
| `real-contract-types` | `core` | `style` | baseline | `bmo-block-reviewer/SKILL.md` |
| `schema-narrow-types` | `core` | `style` | seeded | `bmo-block-reviewer/SKILL.md` |
| `shared-constants-not-magic` | `core` | `style` | 2 | `bmo-block-reviewer/SKILL.md` |
| `consume-original-shared-exports` | `core` | `style` | 2 | `bmo-block-reviewer/SKILL.md` |
| `colocate-related-code` | `core` | `style` | baseline | `bmo-block-reviewer/SKILL.md` |
| `extract-for-testability` | `core` | `style` | baseline | `bmo-block-reviewer/SKILL.md` |
| `avoid-thin-wrappers` | `core` | `style` | 3 | `bmo-block-reviewer/SKILL.md` |
| `no-forced-shared-helpers` | `core` | `style` | 2 | `bmo-block-reviewer/SKILL.md` |
| `single-return-formatters` | `core` | `style` | seeded | `bmo-block-reviewer/SKILL.md` |
| `extract-nullish-chains` | `core` | `style` | seeded | `bmo-block-reviewer/SKILL.md` |
| `extract-named-predicates` | `core` | `style` | seeded | `bmo-block-reviewer/SKILL.md` |
| `no-over-defensive-checks` | `core` | `style` | baseline | `bmo-block-reviewer/SKILL.md` |
| `type-appropriate-operations` | `core` | `style` | seeded | `bmo-block-reviewer/SKILL.md` |
| `remove-redundant-type-checks` | `core` | `style` | seeded | `bmo-block-reviewer/SKILL.md` |
| `no-redundant-membership-guards` | `core` | `style` | seeded | `bmo-block-reviewer/SKILL.md` |
| `remove-refactor-leftovers` | `core` | `style` | seeded | `bmo-block-reviewer/SKILL.md` |
| `preserve-helpful-comments` | `core` | `style` | baseline | `bmo-block-reviewer/SKILL.md` |
| `helper-docstrings` | `core` | `style` | 2 | `bmo-block-reviewer/SKILL.md` |
| `precise-docstrings` | `core` | `style` | seeded | `bmo-block-reviewer/SKILL.md` |
| `comment-regex-patterns` | `core` | `style` | seeded | `bmo-block-reviewer/SKILL.md` |
| `concurrent-submit-guard` | `frontend` | `issue` | baseline | `bmo-block-reviewer/references/frontend.md` |
| `no-fallback-unproduced-states` | `frontend` | `issue` | 2 | `bmo-block-reviewer/references/frontend.md` |
| `suppress-unresolved-display` | `frontend` | `issue` | 1+ | `bmo-block-reviewer/references/frontend.md` |
| `verify-domain-guards` | `frontend` | `issue` | 1+ | `bmo-block-reviewer/references/frontend.md` |
| `single-dom-across-viewports` | `frontend` | `style` | baseline | `bmo-block-reviewer/references/frontend.md` |
| `match-sibling-ui-patterns` | `frontend` | `style` | 2 | `bmo-block-reviewer/references/frontend.md` |
| `avoid-useeffect-derived-state` | `frontend` | `style` | seeded | `bmo-block-reviewer/references/frontend.md` |
| `validate-from-handlers-not-effects` | `frontend` | `style` | seeded | `bmo-block-reviewer/references/frontend.md` |
| `reuse-existing-state` | `frontend` | `style` | seeded | `bmo-block-reviewer/references/frontend.md` |
| `extend-via-optional-props` | `frontend` | `style` | seeded | `bmo-block-reviewer/references/frontend.md` |
| `one-shared-hook-not-domain-copy` | `frontend` | `style` | seeded | `bmo-block-reviewer/references/frontend.md` |
| `single-loading-skeleton` | `frontend` | `style` | seeded | `bmo-block-reviewer/references/frontend.md` |
| `prefer-design-tokens` | `frontend` | `style` | seeded | `bmo-block-reviewer/references/frontend.md` |
| `validate-inbound-ids-at-handler` | `backend` | `issue` | 3 | `bmo-block-reviewer/references/backend.md` |
| `generic-errors-to-callers` | `backend` | `issue` | 3 | `bmo-block-reviewer/references/backend.md` |
| `map-upstream-errors-to-http` | `backend` | `issue` | 1+ | `bmo-block-reviewer/references/backend.md` |
| `auth-identity-is-401` | `backend` | `issue` | 1+ | `bmo-block-reviewer/references/backend.md` |
| `keep-proto-success-envelopes` | `backend` | `issue` | 1+ | `bmo-block-reviewer/references/backend.md` |
| `reproducible-codegen-config` | `backend` | `issue` | 2 | `bmo-block-reviewer/references/backend.md` |
| `dispatch-by-sent-field` | `backend` | `issue` | 1+ | `bmo-block-reviewer/references/backend.md` |
| `shared-error-constants` | `backend` | `issue` | 1+ | `bmo-block-reviewer/references/backend.md` |
| `match-sibling-route-registration` | `backend` | `style` | 2 | `bmo-block-reviewer/references/backend.md` |
| `one-handler-per-file` | `backend` | `style` | seeded | `bmo-block-reviewer/references/backend.md` |
| `colocate-handler-schemas` | `backend` | `style` | seeded | `bmo-block-reviewer/references/backend.md` |
| `match-generated-client-calls` | `backend` | `style` | seeded | `bmo-block-reviewer/references/backend.md` |
| `derive-http-types-from-domain` | `backend` | `style` | seeded | `bmo-block-reviewer/references/backend.md` |
| `zod-parse-contract-payload` | `backend` | `style` | seeded | `bmo-block-reviewer/references/backend.md` |
| `no-wire-type-paths` | `backend` | `style` | seeded | `bmo-block-reviewer/references/backend.md` |
| `validate-before-transaction` | `database` | `issue` | 1+ | `bmo-block-reviewer/references/database.md` |
| `no-transaction-for-single-read` | `database` | `issue` | 1+ | `bmo-block-reviewer/references/database.md` |
| `db-constraint-matches-service-rule` | `database` | `issue` | 1+ | `bmo-block-reviewer/references/database.md` |
| `sql-alias-instead-of-row-map` | `database` | `issue` | 1+ | `bmo-block-reviewer/references/database.md` |
| `skip-empty-table-backfill` | `database` | `style` | seeded | `bmo-block-reviewer/references/database.md` |
| `single-use-vendor-error-codes` | `database` | `style` | seeded | `bmo-block-reviewer/references/database.md` |
| `no-custom-uuid-guards` | `database` | `style` | seeded | `bmo-block-reviewer/references/database.md` |
| `no-settimeout-sleeps` | `testing` | `issue` | baseline | `bmo-block-reviewer/references/testing.md` |
| `test-contract-types` | `testing` | `issue` | 3 | `bmo-block-reviewer/references/testing.md` |
| `integration-tests-match-production` | `testing` | `issue` | 3 | `bmo-block-reviewer/references/testing.md` |
| `shared-test-config-ports` | `testing` | `issue` | 3 | `bmo-block-reviewer/references/testing.md` |
| `test-unit-owned-contract` | `testing` | `issue` | 1+ | `bmo-block-reviewer/references/testing.md` |
| `no-self-asserting-constants` | `testing` | `issue` | 2 | `bmo-block-reviewer/references/testing.md` |
| `no-unproven-indirect-assertions` | `testing` | `issue` | 1+ | `bmo-block-reviewer/references/testing.md` |
| `test-live-export-not-leftover` | `testing` | `issue` | 1+ | `bmo-block-reviewer/references/testing.md` |
| `test-canonical-urls` | `testing` | `issue` | 1+ | `bmo-block-reviewer/references/testing.md` |
| `test-unauthenticated-when-middleware-allows` | `testing` | `issue` | 1+ | `bmo-block-reviewer/references/testing.md` |
| `accessible-query-priority` | `testing` | `style` | baseline | `bmo-block-reviewer/references/testing.md` |
| `no-locator-type-assertions` | `testing` | `style` | 1+ | `bmo-block-reviewer/references/testing.md` |
| `test-user-event` | `testing` | `style` | 1+ | `bmo-block-reviewer/references/testing.md` |
| `separate-queries-from-assertions` | `testing` | `style` | baseline | `bmo-block-reviewer/references/testing.md` |
| `test-aaa-pattern` | `testing` | `style` | seeded | `bmo-block-reviewer/references/testing.md` |
| `behavior-not-implementation` | `testing` | `style` | baseline | `bmo-block-reviewer/references/testing.md` |
| `assert-mock-presence-or-transformed-props` | `testing` | `style` | baseline | `bmo-block-reviewer/references/testing.md` |
| `no-css-class-assertions` | `testing` | `style` | 2 | `bmo-block-reviewer/references/testing.md` |
| `test-realistic-fixtures` | `testing` | `style` | 3 | `bmo-block-reviewer/references/testing.md` |
| `reuse-shared-test-mocks` | `testing` | `style` | 3 | `bmo-block-reviewer/references/testing.md` |
| `test-real-logger-off` | `testing` | `style` | seeded | `bmo-block-reviewer/references/testing.md` |
| `no-non-contract-negative-tests` | `testing` | `style` | 3 | `bmo-block-reviewer/references/testing.md` |
| `no-overlapping-method-tests` | `testing` | `style` | 2 | `bmo-block-reviewer/references/testing.md` |
| `test-names-describe-behavior` | `testing` | `style` | 2 | `bmo-block-reviewer/references/testing.md` |
