# Portfolio Track (`02-portfolio-project` or single-track root)

An incremental build-your-own-project guide (1–2 days across 4–6 milestones) where the learner constructs a production-grade domain engine layer by layer from `red stub`s—finishing with a clean codebase they built themselves and can publish directly to their portfolio.

## Directory shape

```text
02-portfolio-project/
├── README.md                  # Domain primer + Milestones 1..N + portfolio publish steps
├── src/                       # Starter wiring + typed red stubs built across Milestones 1..N
├── tests/
│   ├── m1-<layer>.spec.<ext>  # Per-milestone real-stack integration suites (test:m1..test:mN)
│   └── ...
└── reference/                 # Working reference implementation verified via test:reference
```

## Domain primer & milestone progression

1. **Plain-English domain primer**: Pick a domain whose rules naturally stress-test the stack's hardest guarantees (e.g., double-entry ledger for ACID transactions + row locking; durable job orchestrator for queues + retries + dead-lettering; collaborative sync engine for conflict resolution). Open `README.md` by defining every domain noun and invariant in plain English + Mermaid diagrams assuming the domain is new to the reader.
2. **4–6 progressive milestones (`Milestone 1` $\rightarrow$ `Milestone N`)**: Each milestone adds one architectural capability on top of the previous milestone:
   - **M1 — Data/state modeling & pure domain rules** (schema/types, integer/precision math, constraints, indexes + `native CLI` inspection).
   - **M2 — Core atomic operations & auditability** (transactional commands, rollbacks on domain violations, integrity reconciliation).
   - **M3 — Concurrency & contention safety** (reproduce a multi-worker/parallel race in `test:m3` so a naive M2 implementation fails under contention until locking, CAS, or serialization is added).
   - **M4 — Idempotency, retries & failure recovery** (payload hashing, unique-constraint race handling, safe replay).
   - **M5 — Immutability/security boundaries & compensations** (extension hooks/guards, reversals, showcase `demo` script).
3. **Per-milestone teaching loop**:
   - Explain the concept + show structural mechanics in a `parallel domain` paired with `doc pointer` links (keeping the target project's implementation for the learner to write).
   - List exact files, schema models/indexes, and typed method contracts to implement in `src/`.
   - Provide a dedicated milestone test command (`test:m1` .. `test:mN`) plus `native CLI` checks (with pre-configured namespace/search path so CLI inspection works out of the box).

## Starter stubs, `test:reference`, & portfolio handoff

- **Compile-clean `red stub`s**: Provide boilerplate error types, connection scaffolding, `demo`/`seed` runners (calling domain service interfaces rather than raw ORM tables), and typed `red stub` methods so `typecheck` passes at `0` errors before Milestone 1 is even started while `test:m1`..`test:mN` all fail `red`.
- **Non-destructive `test:reference`**: Store a complete working implementation in `reference/` and wire `test:reference` to push/run against an isolated namespace (e.g., `<schema>_ref`) and restore starter generated types in `finally`, proving all `m1`..`mN` tests pass `green` without overwriting or dropping the learner's in-progress database state or `src/` files.
- **Publish-to-portfolio section**: Close `README.md` with exact commands to delete `reference/` and `test:reference` once all milestones and `demo` pass, plus **3–5 extension ideas** so the learner can add original commits before publishing.

**Completion criterion:** `README.md` contains the plain-English domain primer, 4–6 progressive milestones using `parallel domain` snippets and `doc pointer` links, and portfolio cleanup/extension steps; `typecheck` passes on untouched stubs; `test:m1`..`test:mN` fail `red` on untouched stubs; `test:reference` passes `green` across all milestone suites in an isolated namespace without mutating learner files.
