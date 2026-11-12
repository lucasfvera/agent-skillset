---
name: bmo-stack-prs
description: Infers stacked branch order from git history, pushes out-of-sync stack heads, and creates missing stacked GitHub PRs.
disable-model-invocation: true
---

# Stack PRs

## When to use

Apply this skill when opening **multiple PRs** where each PR targets the **previous branch** (or `main` for the first), and the order must match **real git history**, not branch-name sorting.

## Preconditions

- `gh` installed and authenticated (`gh auth status`).
- Remote is `origin` unless the user specifies otherwise.
- Default integration branch is usually `main`; use the repo default if different.

## Minimum input and automation

**The user should not have to list which branches to push or which PRs to create.** Derive everything from git + GitHub as follows.

**Required input (at most):**

1. **Stack tip** — The newest branch in the stack (contains all work to ship). If the user does not name one, use the **current branch** (`git branch --show-current`).
2. **Default base name** for GitHub (e.g. `main`) — Infer from `gh repo view --json defaultBranchRef` when not specified.

**Optional override:** an explicit ordered branch list (§1). Use only when the user provides it; do not reorder by name.

**Automatic outputs (do not ask the user to enumerate these):**

| Output | Rule |
|--------|------|
| **Ordered stack branches** | From §1 discovery along `ROOT..TIP`, or the explicit list. |
| **Planned PR slices** | Consecutive pairs `(base_i, head_i)` from default branch through the tip. |
| **Branches to push** | Every branch name that appears as a **stack head** (`head_i`) where **either** `origin/<name>` does not exist **or** `git rev-parse <name> != git rev-parse origin/<name>` (local tip differs from remote). This keeps the remote chain consistent for downstream PRs without the user naming branches. |
| **PRs to create** | Only **gaps** from §3 (no open PR for `head_i`, or open PR with wrong base—see confirmation). |

Then execute §2 → §3 → push the computed push-set → §5–§6 for gap heads only.

**When to confirm with the user (stop automation until resolved):**

- **Ancestry check (§2) fails** — non-stackable history; do not push or create until fixed or the user overrides with a corrected explicit list.
- **Not a single line** from `ROOT` to `TIP` (merges, multiple parents) — ask how to slice or which first-parent line to use.
- **Open PR base mismatch (§3)** for a `head_i` — report PR number and bases; suggest `gh pr edit`; do not create a second PR without user direction.
- **Diverged branch** (local and `origin/<name>` both have unique commits, not fast-forward) — do not `--force` push; ask how to reconcile.
- **Ambiguous tip** — e.g. current branch not on the intended line, or discovery includes branches the user did not expect: show the **computed ordered list** and one-line rationale (tips on `ROOT..TIP`); ask only if something is off or unusually broad.

**When not to ask:** If §2 passes, §3 is only satisfied rows + plain gaps, and push-set is straightforward, **proceed** with push + `gh pr create` for gaps and report what happened.

## 1. Define the stack (history-first)

**Inputs:** stack **tip** branch (newest work; default **current branch**), default base name for GitHub (e.g. `main`), optional explicit ordered list of branch names.

**If the user gave an explicit list:** validate it in step 2. Do not reorder by name.

**If discovering branches:**

1. `git fetch origin` (or the relevant remote).
2. Let `ROOT` = remote default tip, e.g. `origin/main` (resolve with `gh repo view --json defaultBranchRef` if unsure).
3. Let `TIP` = the stack tip branch.
4. List commits on the path: `git log --reverse --oneline "$ROOT..$TIP"` (must be a **single line** of history for a simple stack; if not, stop and ask how to handle merges).
5. Map **local** branch tips to commits on that line (`git rev-parse branch` for each candidate). Include only branches whose tip SHA appears on that path.
6. Sort those branches **chronologically** along `ROOT..TIP` (order of first appearance of each tip commit in the reversed log, or equivalently increasing ancestry depth from `ROOT`).

**Include** intermediate branches (e.g. `chore/*`, `refactor/*`) if their tips sit on the path—**do not** skip from `feat/n` to `tip` if named branches exist between them.

## 2. Verify ancestry (required)

For each consecutive pair `(base_ref, head_ref)`:

- PR1: `base_ref = main` (GitHub base name), `head_ref` = first branch. For **local** checks use `origin/main` if local `main` may diverge: `git merge-base --is-ancestor origin/main "$head_ref"`.
- PRi (i>1): `base_ref` = previous **head** branch name, `head_ref` = current branch.

Run:

```bash
git merge-base --is-ancestor "$base_ref" "$head_ref"
```

for each pair using the **local ref** that matches what will be pushed (e.g. use `origin/main` only when comparing into `main` for correctness). If any check fails, **stop** and report which pair breaks; do not open PRs until the stack is fixed.

**Common mistake:** assuming lexical order of branch names equals stack order. **History** decides (e.g. a `chore/*` or `refactor/*` branch may be the base for a later `feat/*` if the feat tip is a descendant of that tip).

## 3. Compare plan to GitHub (incremental / existing stack)

Before pushing or creating anything, **reconcile** the ordered stack from §1 with **open** PRs in this repo.

**Expected stacked PR:** For each slice `i`, you have an expected pair `(base_i, head_i)` where `base_1` is the default branch name (e.g. `main`) and `head_i` is branch `i` on the stack; for `i>1`, `base_i` is the **previous stack branch name** (same string you will pass to `gh pr create --base`).

**Fetch GitHub state** (after `git fetch origin`):

```bash
gh pr list --state open --limit 200 --json number,url,baseRefName,headRefName
```

(Adjust `--limit` if the repo has many open PRs; filter client-side by `headRefName` in the planned stack.)

**For each planned `(base_i, head_i)`:**

| Condition | Action |
|-----------|--------|
| Open PR exists with `headRefName == head_i` **and** `baseRefName == base_i` | **Satisfied.** Do not create a duplicate. Optionally mention PR number/URL in the summary. |
| Open PR exists for `head_i` but `baseRefName != base_i` | **Mismatch.** Stop creating for that head; report the conflict (wrong base vs stacked expectation). Suggest fixing with `gh pr edit <n> --base <base_i>` after user confirms, or ask how to proceed—do not open a second PR for the same head. |
| No open PR for `head_i` | **Gap.** This slice needs push (§4), then body/title (§5), then `gh pr create` (§6). |

**Merged-only or absent:** If there is **no open** PR for `head_i`, treat the slice as **missing** and create it (unless the user said “do not recreate closed PRs”). Do not assume an old merged PR means the branch is “done” for a new stacking run—only **open** PRs satisfy the stack for automation.

**Summary for the user:** List (a) slices already satisfied on GitHub, (b) slices with base mismatch, (c) branches that still need **push**, (d) slices that need **PR create**. This is the answer to “what already exists vs what we need to do.”

## 4. Verify pre-PR checks and push branches (automatic set)

Before pushing and calling `gh pr create`, ensure the repository's `lint`, `typecheck`, and `test` checks are green on the committed stack tip per [`../hooks/pr-checks.md`](../hooks/pr-checks.md) (skip re-running only if `bmo-builder` Phase 4b just passed on this exact `HEAD`).

Use the **push set** from **Minimum input and automation** (every stack `head_i` where local ref differs from `origin/<head_i>` or remote branch missing). Do **not** wait for the user to name these branches.

For each branch in that set:

```bash
git push -u origin "<branch>"
```

If local is **strictly ahead** (fast-forward), push is safe. If **not** fast-forward (diverged), stop and follow the diverged rule in **When to confirm**.

Do **not** use `--force` unless the user explicitly requests it.

**Incremental example:** Stack is `main <- feat-1 <- feat-2 <- feat-3`. Open PRs already exist for `feat-1` and `feat-2` with matching bases. **Create:** only `feat-3` (gap). **Push:** any of `feat-1`, `feat-2`, `feat-3` whose local SHA differs from `origin/<name>` (e.g. new work on `feat-3` only → usually push just `feat-3`).

## 5. PR body and title

Follow [`bmo-pr/SKILL.md`](../bmo-pr/SKILL.md) (`## 4. Title` and `## 5. Body (preventing cognitive surrender)`) as the single source of truth for every slice's title and PR body:

- **Scope & self-containment:** Each stacked PR represents one significant, domain-focused vertical slice (~100 LOC target / ~200 LOC production-code soft ceiling, excluding tests, lockfiles, snapshots, and generated code) **with its unit/integration tests included in the same PR**.
- **`## Intent & stack position`:**
  - Set **Stack position** to `Part i of k — stacked on #<prev-pr-or-branch>: <1-line role of this slice in the stack>` (or `Part 1 of k — base: <default-branch>` for PR1).
  - Include a fenced commit block for the slice's unique range (`git log --oneline <base_i>..<head_i>`, using `origin/<default-branch>..<head_1>` for PR1).
- **`## Decisions, trade-offs & backing docs`**, **`## Failure modes & boundary risks`**, **`## How to review (product & decision focus)`**, and **`## Verification & unverified gaps`:** Populate for **this slice only**, stating what later PRs in the stack add under **Out of scope**.
- **`## Screenshots`:** Follow [`../bmo-pr/screenshots.md`](../bmo-pr/screenshots.md) (release-free `--attach` or `gh image`, skipping cleanly without creating GitHub releases if tooling is unavailable) when the slice changes visual UI or UI copy/constants, or write `N/A — non-visual change`.

## 6. Create PRs with GitHub CLI (gaps only)

In stack order, run **`gh pr create` only for slices marked as gaps** in §3 (missing open PR with correct base).

```bash
gh pr create --base <base> --head <head> --title "..." --body-file <file> --assignee <github_login>
```

- PR1: `--base main` (or repo default).
- Later PRs: `--base` = previous branch name **as it exists on the remote**.

**Assignee:** Use the user’s GitHub login (e.g. from `gh auth status`) unless they specify another.

**Do not** create a new PR for a `head` that already has an open PR with the **matching** `base` (§3).

## 7. After creation

Tell the user the **merge order** (PR1 → `main`, then PR2, …), which PRs were **already present**, which were **created**, and that each merge or rebase may require updating downstream PR bases if GitHub does not auto-retarget.

## Reference

For a worked ordering table, incremental example, and command snippets, see [reference.md](reference.md).
