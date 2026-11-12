# Katas Track (`03-code-katas` or single-track root)

5–8 progressive, test-driven `Red -> Green -> Refactor` challenges that build muscle memory against live automated test suites.

## Directory shape

```text
03-code-katas/
├── README.md                  # Red -> Green -> Refactor workflow + kata index table
├── katas/
│   ├── 01-<slug>/
│   │   ├── README.md          # Objectives, brief mental model + doc pointer, task spec
│   │   ├── challenge.<ext>    # Red stub edited by the learner
│   │   ├── solution.<ext>     # Idiomatic reference implementation
│   │   └── challenge.test.<ext>
│   └── ...
└── ...                        # Shared client/harness + test config with solution swap
```

## Per-kata structure

Order katas from single-entity basics through relations/composition, atomic transactions, pagination/performance, raw/low-level escape hatches, and extensibility. Every kata folder contains:

1. **`README.md` (self-contained brief)**:
   - **Objectives**: 2–3 concrete skills tested by the kata.
   - **Mental model + `doc pointer`**: Compact explanation (plus a Mermaid diagram or `parallel domain` snippet where helpful) paired with `doc pointer` links so the kata is solvable standalone using official docs.
   - **Task spec**: Exact function signatures and behaviors to implement in `challenge.<ext>`, plus single-kata test and watch commands.
2. **`challenge.<ext>` (`red stub`)**: Exported signatures with static types, behavioral docstrings, and `throw new Error('Not implemented')` bodies.
3. **`solution.<ext>`**: Idiomatic implementation for the pinned tool versions exporting the identical contract as `challenge.<ext>`.
4. **`challenge.test.<ext>`**: Resets state in `beforeEach` for repeatable watch-mode runs and asserts both return values and real side effects (persisted rows, rollback on mid-flight error, omitted fields, deterministic cursors).

## Zero-edit solution swap (`test:solutions`)

Configure the test runner (via module resolver alias, fixture switch, or `TEST_SOLUTIONS=1` environment flag) to swap `challenge` imports to `solution` across all katas:

- Default test command (`test katas/01`) imports `challenge.<ext>` and fails `red` (`Not implemented`).
- `test:solutions` imports `solution.<ext>` across every kata and exits `green` (`0`) without touching `challenge.<ext>` on disk.

**Completion criterion:** Every kata directory contains a self-contained `README.md` (with mental model and `doc pointer`), `challenge` (`red stub`), `solution`, and deterministic `challenge.test`; default tests fail `red` on untouched stubs and `test:solutions` passes `green` across all katas with zero file edits.
