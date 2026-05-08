---
name: commit
description: Writes conventional commit messages from staged diffs and creates the commit. Detects workspace scope from paths in Yarn/Nx/Turborepo-style monorepos (apps/*, packages/*). Use when the user says commit, commit this, save changes with a message, or attaches this skill for a conventional commit.
disable-model-invocation: true
---

# Commit (conventional)

## Workflow

1. If nothing is staged (`git diff --cached --stat` empty), stop and tell the user to stage files first.
2. Inspect staged changes: `git diff --cached`, names, and rough intent (feat/fix/test/chore/etc.).
3. **Infer `<type>`** from branch name when it matches `feat/`, `fix/`, `chore/`, etc.; otherwise choose from the list below from the actual diff.
4. **Infer `<scope>`** using [Monorepo scope](#monorepo-scope) rules when paths clearly belong to one workspace; omit scope when unclear or overly broad.
5. Compose the message per [Format](#format), then run `git commit` with that message.

## Monorepo scope

Conventional commits allow an optional scope: `type(scope): subject`

**Goal:** The scope should identify *which package or app* users blame or changelog generators group by—not every folder touched.

### Detect scope from staged paths

Use path prefixes relative to the repository root (works for Yarn workspaces, Nx, Turborepo, and similar layouts):

| Staged path pattern | Scope (examples) |
|---------------------|------------------|
| `apps/<name>/...` | `<name>` (e.g. `activity`, `eventrox`, `tx`) |
| `packages/<name>/...` | `<name>` |
| `libs/<name>/...` or `libraries/<name>/...` | `<name>` |
| `services/<name>/...` | `<name>` |
| `tools/<name>/...` | `<name>` |
| Only root files (`package.json`, `turbo.json`, `.github/`, `yarn.lock`) | Prefer short repo or tooling label if the team uses one (e.g. `repo`, `ci`); otherwise **omit scope** |

If the repo uses a different top-level convention, map the **first directory after the workspace root** that names an installable unit (matches `workspaces` globs or an app folder) to that unit’s short name.

### Multiple workspaces in one commit

- **One dominant workspace:** ≥ ~70% of staged files under one `apps/*` or `packages/*` tree → use that scope; mention other areas in the body if relevant.
- **Two or more equally important workspaces:** Either **omit scope** or use the **shortest shared parent** only if your team uses that convention (e.g. `apps`); do not invent ambiguous scopes like `multiple`.
- **Shared infrastructure** (only root config, CI, lockfile): scope `ci`, `build`, or omit—match the `<type>` (e.g. `ci:` for workflow-only changes).

### Confirm with package name (optional)

If unsure between folder name and `package.json` `name` (e.g. `@org/foo` → scope `foo` or `org-foo`), prefer the **directory name** under `apps/` or `packages/` for brevity unless the repo consistently uses the npm scope in commits.

## Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

- **Subject line:** imperative, present tense, capital start, no trailing period; **≤ 50 characters** (including `(scope)` if present).
- **Body:** wrap at **72** chars; two short paragraphs—**why** first, **what** second; no implementation trivia.
- **Footer:** issue/PR reference from branch name if present (`Closes #123`, `Refs #456`); else omit. **BREAKING CHANGE:** in footer when applicable.

`<type>` (if not taken from branch):

- feat — feature
- fix — bug fix
- chore — chore
- refactor — refactor without feat/fix
- docs — documentation
- style — formatting, no logic change
- test — tests only
- perf — performance
- build — build system or externals
- ci — CI config
- revert — revert
- security — security fix

## Examples

**Single app:**

```
fix(activity): Align Jest config with workspace TS paths

Tests failed under the activity app after TS path changes.
We align Jest and tsconfig so tests resolve modules consistently.

Refs #DEV-123
```

**Root-only CI:**

```
ci: Pin Node version in release workflow

Release jobs behaved differently across runners.
We pin the Node version used in the release workflow.

```

**No scope (touches several apps equally):**

```
chore: Update shared lint rules across workspaces

Lint drift was causing noisy CI failures.
We apply the same ESLint overrides wherever the shared config is consumed.

```

## Finish

After the message is ready, create the commit (`git commit -m` for single-line or `-m` pairs / here-doc for body+footer). Do not commit if the user only asked for message text without committing.
