---
name: bmo-commit
description: Creates a conventional commit from the index only—default is staged changes only; aborts with no commit if nothing is staged. Never auto-stages unstaged work, edits files, or runs formatters. Stages paths only when the user explicitly asks to stage. Detects workspace scope from paths in Yarn/Nx/Turborepo-style monorepos (apps/*, packages/*). Use when the user says commit, commit this, /bmo-commit, save changes with a message, or attaches this skill. Do not infer permission to commit a second git root because a prior message committed another repo—confirm intent matches staged paths (see bmo-step-deliver).
disable-model-invocation: true
---

# Commit (conventional)

## Default behavior (hard gate)

Unless the user **explicitly** asked you to stage paths first (see [Staging](#staging)):

1. **Commit only what is already staged** — use `git diff --cached` as the sole source of truth for the commit contents.
2. **Do not run `git add`** — not `git add .`, not `git add -A`, not path inference from unstaged diffs or “commit everything” wording alone.
3. **Abort if the index is empty** — after `git diff --cached --stat` (or equivalent) shows no staged files, **stop without `git commit`**. Tell the user nothing was committed because nothing is staged, and that they should stage files locally (e.g. `git add <path>`) or ask you to stage named paths, then run the skill again.

Unstaged or untracked changes stay out of the commit by default; mention them only in post-commit status if a commit succeeded.

## Immutable commit boundary (hard gate)

This skill is **commit-only**. It must **not** change any file that will end up in the commit (staged or unstaged).

**Never do while running this skill:**

- Edit, create, delete, or rename source, config, test, or generated files
- Run formatters, linters with auto-fix, `yarn normalize` / `yarn beautify`, `prettier --write`, `eslint --fix`, or similar tools that rewrite the tree
- “Fix” hook failures, type errors, or test failures before committing—report them and stop
- Stage or unstage paths unless the user **explicitly** asked to stage (see [Staging](#staging) below)—including auto-staging “all changes”, unstaged files, or paths implied only by branch or scope

**Allowed git operations:** read-only inspection (`git status`, `git diff`, `git diff --cached`, `git log`, …), **`git add`** only when staging was requested, and **`git commit`** on the index as it exists after any user-requested staging.

If a pre-commit hook modifies files and the commit fails or needs a follow-up, **do not** patch files in this skill—tell the user what the hook changed and let them decide (re-stage, fix, or amend per their repo rules).

## Staging

**Default:** no staging step — commit the index as-is or abort if empty.

| User said | Action |
|-----------|--------|
| “commit” / `/bmo-commit` / “commit this” (no staging instruction) | **Do not** run `git add`. If the index is empty, **abort** (see [Default behavior](#default-behavior-hard-gate)). Otherwise commit **only** staged paths. |
| “stage X and commit” / “add these files and commit” / scoped “commit **packages/ws**” with unstaged changes in that scope | Run **`git add`** only for the paths they named (or the named workspace scope). Do not `git add -A` unless they asked for all changes. If staging still leaves an empty index, **abort**. |
| **`continue`** per **bmo-step-deliver** | Stage **only** that slice’s files in **that** repo if the step-deliver flow says to stage before commit; still **no** file edits. If nothing ends up staged, **abort**. |

After any `git add`, re-run `git diff --cached` and confirm the index is non-empty and matches intent before committing.

## Workflow

1. **Confirm intent:** Only run when the user asked to **create a commit** (or used `/bmo-commit` / `continue` per **bmo-step-deliver** for the **same** repo’s completed slice). If they asked to commit **only** a named part of the monorepo or a **different** git root, ensure staged files match that scope—**do not** stage or commit other repos by inference. See **bmo-step-deliver** (Git commits: explicit approval per repository).
2. **Stage (only if requested):** If the user asked to stage specific paths or a scope, run `git add` for those paths only. Otherwise **skip staging entirely** — do not compensate for an empty index by adding files.
3. **Index check (required):** Run `git diff --cached --stat`. If empty, **abort**: do not run `git commit`. Tell the user no commit was created, that only staged changes are committed by default, and they should stage files (or ask you to stage named paths) and retry.
4. Inspect staged changes: `git diff --cached`, names, and rough intent (feat/fix/test/chore/etc.)—**read-only**; do not “improve” the diff.
5. **Infer `<type>`** from branch name when it matches `feat/`, `fix/`, `chore/`, etc.; otherwise choose from the list below from the actual diff.
6. **Infer `<scope>`** using [Monorepo scope](#monorepo-scope) rules when paths clearly belong to one workspace; omit scope when unclear or overly broad.
7. Compose the message per [Format](#format), then run `git commit` with that message.

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

After the message is ready, create the commit (`git commit -m` for single-line or `-m` pairs / here-doc for body+footer) **only when the index was non-empty in step 3**. Do not commit if the user only asked for message text without committing.

**Post-commit:** Run `git status` to confirm success. If the working tree still has unstaged or unrelated changes, mention them briefly—do **not** edit or stage them unless the user asks in a follow-up.

**Aborted (empty index):** Do not run `git commit`. State clearly that the command was aborted because nothing was staged.
