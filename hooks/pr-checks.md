# Checks (before `gh pr create`)

**checks** are the lint, typecheck, and test commands for this git root. Record and run them here whether a Cursor hook will also stamp them.

Record one command per family. Prefer the PR workflow. When the workflow omits a family and a package script exists, that script is the check. First matching script name:

| Family | Scripts |
|--------|---------|
| lint | `lint`, `lint:check`, `eslint` |
| typecheck | `type-check`, `typecheck`, `tsc`, `types` |
| test | `test`, `test:unit`, `test:ci`, `test:all` |

Skip `lint:fix`, `test:watch`, `test:e2e`, `test:coverage`. No matching scripts: Makefile `lint` / `typecheck` / `test`, else `go test ./...` / `cargo test` / `pytest` when those manifests exist.

1. Record every check for this git root.
2. Run each one in the same root (or worktree) you will open. Green = exit 0.
3. If `HEAD` moves, every check is un-green.

A local Cursor hook stamps those green Shell commands and blocks `gh pr create` until this `HEAD` is green. Cloud has no hook: these steps are the gate.

**Done:** every recorded check exited 0 on the current committed `HEAD`.
