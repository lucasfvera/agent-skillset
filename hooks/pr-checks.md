# Pre-PR checks (`pr-checks`)

**Checks** are the repository's `lint`, `typecheck`, and `test` commands for the git root (or isolated worktree) being opened. Run and pass them before `gh pr create` whether or not a local shell hook also enforces them.

## 1. Discover required check families

Record one command per present family. Prefer the commands called by the repository's PR workflow (`.github/workflows/`); when the workflow omits a family and a package script exists, include the first matching script name:

| Family | Package scripts (first match) | Non-Node fallbacks |
|--------|-------------------------------|--------------------|
| `lint` | `lint`, `lint:check`, `eslint` | `Makefile` `lint`, `golangci-lint run`, `cargo clippy -- -D warnings`, `ruff check` |
| `typecheck` | `type-check`, `typecheck`, `tsc`, `types` | `Makefile` `typecheck` / `type-check` |
| `test` | `test`, `test:unit`, `test:ci`, `test:all` | `Makefile` `test`, `go test ./...`, `cargo test`, `pytest` |

Skip mutating, watch, coverage, or full-browser E2E scripts (`lint:fix`, `test:watch`, `test:e2e`, `test:coverage`).

## 2. Run on the committed `HEAD`

1. Record every discovered check command for the target git root / `WORKTREE_PATH`.
2. Run each command in that exact git root (for a stacked branch line, running on the committed stack tip satisfies downstream `gh pr create` calls from that worktree). **Green** = exit code `0`.
3. **If `HEAD` or working-tree state changes** (new commit, amend, rebase), every check becomes un-green and must re-run on the new `HEAD`.

When the `pr-checks.py` shell hook is active locally, it stamps green check runs per `(git_root, HEAD, status)` and mechanically blocks `gh pr create` until every discovered family is green. Without the hook, these steps are the gate.

**Done:** Every recorded check exited `0` on the current committed `HEAD` of the target git root.
