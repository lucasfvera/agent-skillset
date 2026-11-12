# Sprint Track (`01-interview-sprint-3h` or single-track root)

Hands-on onboarding (~2–3 hours across 4–6 modules) taking the learner from their stated baseline to writing real code and answering technical interview questions.

## Directory shape

```text
01-interview-sprint-3h/
├── README.md              # Progressive modules (concept -> native CLI -> red stub)
├── CHEATSHEET.md          # Syntax, CLI commands, and decision tables
├── INTERVIEW_QA.md        # 15–25 foundational-to-production interview Q&As
├── src/
│   ├── exercises/         # Red stubs implemented by the learner (01..0N)
│   ├── checkers/          # Automated verifiers per module (check:1..check:N)
│   └── examples/          # Runnable parallel-domain scripts (example:1..example:N)
└── ...                    # Schema/config/SQL/fixtures as needed by the stack
```

## Module loop (repeat per module)

1. **Concept + `parallel domain` snippet + `doc pointer`**: Teach 2–4 cohesive building blocks in one consistent `parallel domain` shared across `README.md` and `src/examples/`.
2. **`Native CLI` step (~3–5 min)**: Provide a script alias (e.g., `npm run psql`, `make cli`) into the default namespace plus 2–3 concrete inspection or query tasks so the learner observes physical tables, plans, keys, or frames directly.
3. **`Red stub` exercise (~15–25 min)**: Have the learner write across the stack's real surfaces (e.g., schema model/index + raw query file + 2–3 typed functions in `src/exercises/0N-<topic>.<ext>` stubbed with `throw new Error('TODO: ...')`).
4. **Module checker (`check:1` .. `check:N` + `check:all`)**: Seed state deterministically, run assertions against the live local stack, and print per-check results. Re-throw `TODO:` errors before any expected-error or rollback `catch` block so untouched stubs stay `red`.

## Module arc

1. **Core mental model & basic operations** (baseline equivalent $\rightarrow$ typed client/SDK read/write, projection, sensitive-field omission).
2. **Relationships, composition, or state modeling** (links across entities, atomic nested writes, race-safe upserts).
3. **Performance & scaling mechanics** (indexes/data structures, `EXPLAIN`/profiling, N+1 or batching fixes, cursor/streaming pagination).
4. **Concurrency, atomicity & escape hatches** (transactions, simultaneous-request race conditions, locking/conditional writes, typed raw queries).
5. **Lifecycle, extensibility & legacy codebases** (migrations/rollouts, client extensions/hooks, and a concise field guide to older major-version patterns learners will encounter in existing repos).

## Companion files

- **`CHEATSHEET.md`**: 5-minute pre-interview reference with `native CLI` commands, syntax snippets, `A vs. B` decision tables, and `doc pointer` links.
- **`INTERVIEW_QA.md`**: 15–25 realistic engineering interview questions ordered foundational $\rightarrow$ modeling $\rightarrow$ performance $\rightarrow$ concurrency/production, with concrete answers explaining underlying mechanics and tradeoffs.

**Completion criterion:** All 4–6 modules in `README.md` use a `parallel domain` distinct from `src/exercises/`, include `native CLI` tasks and `doc pointer` signposts, pair each `red stub` exercise with a stub-safe `check:N` verifier and a working `example:N` script, and ship `CHEATSHEET.md` and `INTERVIEW_QA.md`.
