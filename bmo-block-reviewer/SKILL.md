---
name: bmo-block-reviewer
description: Two-pass findings-first diff review separating strict correctness issues from coding style across domain catalogs.
disable-model-invocation: true
---

# Block reviewer (bmo)

Review the changed files in two ordered passes: **Pass 1 (`[issue]`)** catches correctness, contract, security, performance, and false-test defects; **Pass 2 (`[style]`)** aligns structure, conventions, and readability to the author's style without crowding out strict issues.

This skill covers a delivery-digest block, a PR-fix slice, or a domain slice of a branch diff. Parent skills (`bmo-builder`, `bmo-respond-pr-review`) own subagent orchestration.

## Review procedure

1. **Inspect the diff:** Read the actual changed files and `git diff` (plus one sibling file when checking pattern consistency). Use handoff text (digest, verification notes, PR comment) as supporting context only; if the diff is unavailable, state that the review is limited by missing code context. Treat work explicitly marked for a later unit as **Deferred (out of scope)**, not a finding.
2. **Load matching domain catalogs:** Always apply the **Core** rules below, plus only the domain files triggered by the changed paths:
   - **Frontend** ([`references/frontend.md`](references/frontend.md)) — UI components, client hooks, form or view state, templates, CSS/design tokens.
   - **Backend** ([`references/backend.md`](references/backend.md)) — HTTP/gRPC/message handlers, routes, middleware, services, wire schemas/protos, generated clients.
   - **Database** ([`references/database.md`](references/database.md)) — SQL queries, repositories/stores, DB transactions, schema constraints, migrations.
   - **Testing** ([`references/testing.md`](references/testing.md)) — Unit, component, and integration specs (`*.test.*`, `*.spec.*`), fixtures, mocks, test harnesses.
3. **Pass 1 — Strict issues (`[issue]`):** Check **Core → Strict issues** and each loaded domain's **Strict issues** section first. Trace failure paths, boundary validation, status codes, resource locks, and whether tests can pass when production is broken.
4. **Pass 2 — Style & conventions (`[style]`):** Check **Core → Style & conventions** and each loaded domain's **Style & conventions** section second. Skip generic security hunts, invented edge cases, and long summaries.

**Done:** Every domain file matching the changed paths was read; Pass 1 (`[issue]`) was evaluated before Pass 2 (`[style]`); every triggered rule cites its `[rule-id]`.

---

## Core — Strict issues (`[issue]`)

Apply on every diff during Pass 1.

- **[no-any]** Type every value, parameter, and return path explicitly; replace `any` with the concrete contract type or `unknown` narrowed by a guard.
- **[catch-unknown-not-any]** Bind `catch (err: unknown)` and narrow with `instanceof Error` or a typed guard before reading error properties.
- **[strict-equality]** Compare values with strict equality (`===`, `!==`) so type coercion never masks `null`, `undefined`, or numeric mismatches.
- **[use-decimal-helpers]** Compute money, rate, and FX math through shared decimal helpers rather than native floating-point division or multiplication.
- **[log-presence-not-secrets]** Log boolean presence flags (`Boolean(secret)`) for credentials and tokens; never log secret values.
- **[no-empty-string-as-undefined]** Validate required strings before helper calls and treat only `undefined` as omitted; never coerce `""` to `undefined` via truthiness (`val || undefined`).
- **[keep-canonical-separate-from-display]** Persist and pass canonical raw values; apply display masks or formatting only on the read/render path and never derive originals from formatted strings.
- **[hot-path-latency]** Keep hot execution paths free of avoidable sequential awaits, redundant allocations, or repeated lookups inside loops.

## Core — Style & conventions (`[style]`)

Apply on every diff during Pass 2.

- **[real-contract-types]** Type values with the producing module's contract type directly; reserve `as` assertions for boundaries where narrowing is impossible.
- **[schema-narrow-types]** Use schema-defined narrow types at validated boundaries rather than wide unions that upstream validation already constrained.
- **[shared-constants-not-magic]** Import numeric defaults, limits, and timeouts from shared schemas or constants packages instead of hardcoding literals.
- **[consume-original-shared-exports]** Import canonical lists, constants, and paths directly from their original shared module without local array copies or renaming re-exports.
- **[colocate-related-code]** Keep types, helpers, and wiring that change together in the same module or folder.
- **[extract-for-testability]** Extract pure branching or transformation logic into a dedicated helper when direct unit testing is simpler than driving the full caller.
- **[avoid-thin-wrappers]** Inline single-expression checks at the call site when a wrapper function adds indirection without reuse or testability gain.
- **[no-forced-shared-helpers]** Keep similar functions separate when their contracts, return shapes, or domain branches diverge enough that sharing requires mode flags or indirection.
- **[single-return-formatters]** Structure pure formatter functions around one assignment path and a single `return` at the end.
- **[extract-nullish-chains]** Assign multi-step `??` fallback chains to a named intermediate variable or helper so precedence is explicit.
- **[extract-named-predicates]** Extract multi-clause `&&` / `||` domain conditions into a named boolean helper that states the domain question.
- **[no-over-defensive-checks]** Trust invariants enforced earlier on the call path; omit guards for states that cannot occur there.
- **[type-appropriate-operations]** Run string cleanup like `.trim()` only on branches where the value is not already validated as a non-padded type.
- **[remove-redundant-type-checks]** Collapse redundant `typeof` branches when a single coercion handles every input case equivalently.
- **[no-redundant-membership-guards]** Rely on the callback's declared type when iterating items produced from a canonical list; omit secondary `.includes()` checks.
- **[remove-refactor-leftovers]** Delete unused parameters, dead wiring, and leftover inline objects after changing an implementation approach.
- **[preserve-helpful-comments]** Keep comments that explain non-obvious domain invariants, contract quirks, or why an approach was chosen.
- **[helper-docstrings]** Add a concise what-and-why docstring on helpers and public components whose purpose or variant options are not obvious from the signature alone.
- **[precise-docstrings]** Name the exact producing service and data shape in docstrings rather than vague labels.
- **[comment-regex-patterns]** Add a brief comment on each regex stating what pattern it matches and which contract it enforces.

---

## Output

Keep the response short and findings-first. List all `[issue]` findings before `[style]` findings.

```markdown
- [issue] [<rule-id>] <what is wrong, why it matters here, what to change>
- [style] [<rule-id>] <what is wrong, why it matters here, what to change>

Catalog: core[, frontend, backend, database, testing] — <triggered rule-ids or none>

What is fine:
- <one or two notably solid points only if worth saying>

Verdict: <ship | fix style before ship | block — fix issues>
```

**Done:** Output matches this shape; `[issue]` findings precede `[style]` findings; `Catalog:` lists every domain catalog read plus triggered rule IDs (or `none`); `Verdict` is `ship` only when there are zero `[issue]` and zero actionable `[style]` findings.

## Finding style

Each finding states: (1) what is wrong, (2) why it matters in this codebase, and (3) what to change.

- `- [issue] [no-any] Uses \`any\` on the response mapper input. Callers lose compile-time contract checks when the schema changes. Type the parameter with \`OrderResponse\`.`
- `- [issue] [validate-before-transaction] Opens \`db.transaction\` before checking the request payload. Invalid requests hold a pooled connection unnecessarily. Move the schema check above \`db.transaction\`.`
- `- [style] [no-over-defensive-checks] Checks \`if (!user)\` after \`requireAuth\` already guaranteed the session. Remove the redundant guard to keep the main path direct.`
- `- [style] [accessible-query-priority] Queries the submit button with \`getByTestId('submit-btn')\` even though it exposes a button role and label. Use \`getByRole('button', { name: /submit/i })\`.`
