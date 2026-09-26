---
name: bmo-builder
description: Builds a feature or bug end to end: plan, isolated worktrees, per-unit deliver with block review, commit, green checks, then PRs.
disable-model-invocation: true
argument-hint: "[feature or bug]"
---

CRITICAL: Execute every phase below **in order**. Do not implement code before a written plan exists **and** Phase 2 isolation is proven. Do not skip block review or commit between units.

Start at planning. Do not run `bmo-triage` or stop because the work looks medium or high.

When invoking child skills, **read their `SKILL.md` first** from `~/.cursor/skills/<name>/SKILL.md` and follow them, except where this builder **overrides** pacing (autopilot `continue` between units; see [Overrides](#overrides-to-child-skills)).

**Input:** `$ARGUMENTS` is the work to build: a feature or bug in the user's words, a spec, an existing `.plan.md` path, or a handoff from `bmo-linear-pipeline` (identifier, title, type, AC, repos, gaps). If missing, ask once for the work, then stop until provided.

---

## Phase 0 — Record run context

Derive and note:

- **Identifier:** first issue key in the input (`[A-Z]{2,10}-\d+`, case-insensitive, e.g. `DEV-3311`). Else a kebab slug from the title / first line (lowercase, non-alphanumerics to hyphens, ≤48 chars, trim on a hyphen).
- **Title:** from the handoff, or the first line / sentence of `$ARGUMENTS`.
- **Type:** from the handoff, or `Bug` if the user said bug/fix, `Chore` if they said chore, else `Feature`.
- **Link:** URL in the input if present, else none.
- **Work statement:** 1–2 sentences of what to build (from the input; do not invent scope).
- **Branch name:** (filled in Phase 2)
- **WORKTREE_ID:** (filled in Phase 2)
- **Worktrees:** `REPO_ROOT → WORKTREE_PATH` per affected repo (filled in Phase 2)
- **Plan file path:** (filled in Phase 1)
- **Repos (n):** from the plan (filled in Phase 1)
- **Current unit:** (filled in Phase 3 loop)
- **Run status:** `running` | `stopped` | `done`

**Done:** Identifier, title, type, and work statement are recorded; status is `running`.

---

## Phase 1 — Plan (`bmo-step-planner`)

Planning only, no implementation. Do not call `SwitchMode` or block on mode changes.

**Existing plan.** If `$ARGUMENTS` names a `.plan.md` that exists on disk, skip authoring, record that path, and parse its `U1`, `U2`, … units in order.

**Otherwise:**

1. Read and follow [`bmo-step-planner`](../bmo-step-planner/SKILL.md) using the work statement (title, AC, repos, gaps when the handoff has them).
2. Write the plan file per that skill (`U1`, `U2`, … mandatory when 2+ units).

### Gate — Plan must exist

- **Stop** if no plan file was written (or the named file is missing). Status `stopped`.
- **Record** the absolute path to the plan file.
- Parse the list of implementation units (`U1`, `U2`, …) in order from the plan.
- Record **Repos (n)** from the git roots named in the plan.

If the plan has **Open questions (blocked)** with no `defaults: yes` from the user, **stop** and list blockers. Do not implement. Status `stopped`.

**Done:** Plan file exists on disk, every `U*` is listed in order, repos count is recorded, and there are no unresolved blocked questions.

---

## Phase 2 — Worktrees (mandatory before deliver)

All implementation happens in **isolated worktrees**. Phase 3 does not start on a recorded path that is the user's main checkout.

**Affected repos** = union of git roots named in the plan (all units). One worktree per repo, **same branch name** in each.

### Branch name

- Issue key identifier: `feature/[id-lowercase]-[slug-from-title]`, e.g. `feature/dev-3311-pending-deposit-repeated-3-times`.
- Slug-only identifier: `feature/[slug]`.

If the user passed `/worktree branch=…` or this chat already has a worktree for this identifier, reuse that **WORKTREE_PATH** (still run Proof). A feature branch checked out in `REPO_ROOT` is not a worktree. Use the same branch name, in a worktree.

### Setup

1. Pick one **WORKTREE_ID** for the run: `[compact-id]-$(openssl rand -hex 4)` where compact-id is the identifier with hyphens stripped (e.g. `dev3311-a1b2c3d4`).
2. For **each** affected `REPO_ROOT`, add a worktree under `~/.cursor/worktrees/$WORKTREE_ID/` (prefer Cursor **`/worktree`** with the same `WORKTREE_ID` + branch for every repo). If creating by hand: `git -C "$REPO_ROOT" worktree add "$WORKTREE_PATH" -b "$BRANCH"` from `main` or the existing remote branch. Do not `git checkout` that branch in `REPO_ROOT`.
3. Run each repo's `.cursor/worktrees.json` setup once if present.
4. Record `REPO_ROOT → WORKTREE_PATH`.

Do **not** call `move_agent_to_root` (or `move_agent_to_cloned_root`). That tool fetches `origin/<branch>` and fails or prompts-to-abort on a freshly created local branch, which is the usual case after `worktree add -b`. Isolation is the path, not a workspace move.

### Isolation (holds through Phase 4)

For each affected repo, every Write, StrReplace, Shell cwd, `git add` / `commit` / `push`, and verify command targets that repo's `WORKTREE_PATH`. Reviewer `GIT_ROOT` is `WORKTREE_PATH`. Child skills (`bmo-step-deliver`, `bmo-commit`, `bmo-pr`) inherit this: their git root is the worktree, not `REPO_ROOT`.

### Proof (gate)

Run for **every** affected repo. Stop before Phase 3 (status `stopped`) if any check fails:

```bash
test "$(realpath "$WORKTREE_PATH")" != "$(realpath "$REPO_ROOT")"
test -d "$WORKTREE_PATH"
test "$(realpath "$(git -C "$WORKTREE_PATH" rev-parse --show-toplevel)")" = "$(realpath "$WORKTREE_PATH")"
git -C "$REPO_ROOT" worktree list --porcelain | grep -F "$(realpath "$WORKTREE_PATH")"
```

Then print the table:

```markdown
## Worktrees: [IDENTIFIER]

**Branch:** `feature/…` · **WORKTREE_ID:** `dev3311-…`

| Repo | Path |
|------|------|
| roxtopia | `~/.cursor/worktrees/…/roxtopia-…` |
| roxtarsverse | `~/.cursor/worktrees/…/roxtarsverse-…` |
```

Merge back with `/apply-worktree`; cleanup with `/delete-worktree`.

**Done:** Every Proof check passed; the worktrees table was printed. The agent root may still be `REPO_ROOT`.

---

## Phase 3 — Per-unit delivery loop

Repeat for **each** unit `U1`, `U2`, … in plan order until all units are done.

For the current unit `Un`:

### 3a — Deliver one unit (`bmo-step-deliver`)

1. Read [`bmo-step-deliver`](../bmo-step-deliver/SKILL.md).
2. Implement **exactly `Un`** only (sliced mode, one unit) in each repo's **WORKTREE_PATH** from Phase 2.
3. Verify per that skill (correct worktree, narrowest proof).
4. Produce **How to run** and the mandatory **`## Review digest`** with blocks **Block A**, **Block B**, …

Do not wait for the user to type `continue` before the review sub-phase. This builder supplies autopilot `continue` (see [Overrides](#overrides-to-child-skills)).

**Done for 3a:** The review digest lists every changed file in some block; every digest path is under a recorded `WORKTREE_PATH`; `git -C "$REPO_ROOT" diff --name-only` and `git -C "$REPO_ROOT" diff --cached --name-only` show no implementation files; verification ran.

### 3b — Parallel block review (one subagent per block)

From the **Review digest**, identify each `### Block X — …` section (A, B, C, …).

For **each block**, spawn **one** background subagent in parallel using the host `Task` tool:

- **subagent_type:** `generalPurpose`
- **readonly:** `true`
- **run_in_background:** `true`
- **Prompt:** use [references/block-reviewer-subagent.md](references/block-reviewer-subagent.md). Pass block name, block text, file paths, work id, and `GIT_ROOT` = that repo's `WORKTREE_PATH` (never `REPO_ROOT`).

Each subagent must read and follow [`bmo-block-reviewer`](../bmo-block-reviewer/SKILL.md) and inspect the **actual diff** for files in that block.

**Await** all subagent results before continuing.

**Done for 3b:** Every digest block has a reviewer verdict.

### 3c — Apply review fixes

1. Merge findings from all block reviewers.
2. **Fix** every actionable finding (typing, duplication, test style, etc.) in the orchestrator, same unit scope, only under `WORKTREE_PATH`.
3. Re-run the **narrowest verification** from the plan/deliver step if fixes touched behavior.
4. If a reviewer reported **no issues**, note it and continue.

Do **not** commit before fixes are applied.

**Done for 3c:** Every actionable finding is fixed or explicitly deferred with a reason; fixes landed only under `WORKTREE_PATH`; verification re-ran if behavior changed.

### 3d — Commit unit (`bmo-commit`)

1. Read [`bmo-commit`](../bmo-commit/SKILL.md).
2. Stage **only** files changed for **`Un`** in that repo's **WORKTREE_PATH** (`git -C "$WORKTREE_PATH" add <paths>` or Shell cwd = `WORKTREE_PATH`). This builder **explicitly authorizes** staging for the completed unit.
3. Run `/bmo-commit` on that worktree's index. If the index is empty after staging, stop and report. Do not skip commit silently. Status `stopped`.

**Done for 3d:** Each worktree in scope for `Un` has a new commit (hash from `git -C "$WORKTREE_PATH" log -1`); no commit was created in any `REPO_ROOT`. Or this run stopped because the index was empty.

### 3e — Advance

- Mark `Un` complete in run context.
- If more units remain → next iteration at **3a** for `Un+1`.
- If `Un` was the last unit → go to [Phase 4](#phase-4--done).

**Hard rule:** Never start `Un+1` in the same deliver sub-step as `Un` without completing **3b → 3c → 3d** for `Un` first.

---

## Phase 4 — Done

### 4a — Final quality check

After all units are committed, run one more **repo-wide** review pass before any PR:

1. For **each affected repo** (`WORKTREE_PATH`), spawn one readonly reviewer using the same [block reviewer subagent prompt](references/block-reviewer-subagent.md), but with a synthetic block like `Final diff — whole repo`.
2. Pass the full branch diff for that repo (`origin/main...HEAD` or the chosen base), not a per-block slice.
3. Fix every actionable finding **in that `WORKTREE_PATH`**, re-run the narrowest affected verification, and commit the final quality fixes in that worktree before moving on.

This pass exists to catch issues that slip past per-block review, especially repeated PR comments from the learnings catalog.

**Done for 4a:** Every affected repo has a final-diff verdict; actionable findings are fixed and committed.

### 4b — Checks (gate before any PR)

Run this after 4a. [4c](#4c--pull-requests-bmo-pr) starts only when the done line below is met. No `git push` and no `gh pr create` in this step.

For **each** affected repo, in that `WORKTREE_PATH`:

1. Read the PR workflow and the package scripts it calls. The **checks** are the test, typecheck, and lint commands that workflow runs. When the workflow does not run one of those and the package script exists, include that script. Record every command.
2. Run every recorded check in that worktree. A check is **green** when the command exits 0.

When every recorded check is green on the committed `HEAD` of every affected worktree, go to 4c.

When any check is red, the red set from this pass is the next implementation unit:

1. Append `Un+1` to the plan file, using the plan's existing unit headings. **Scope in** is every check that exited non-zero on this pass, including the command output. **Verification (narrowest)** is those same commands, in the worktree they failed in, each exiting 0.
2. Run [Phase 3](#phase-3--per-unit-delivery-loop) for that unit only: **3a → 3b → 3c → 3d**. Autopilot applies. Isolation still holds.
3. Re-run each command that was red this pass on the new `HEAD`. All exit 0 → run this step again from the top (full check set). Any of them still red with the same test name or error → status `stopped`. Report the command and output. Leave that failure without another unit, and leave the PR unopened. A new test name or error is the next pass.

**Done for 4b:** Every recorded check exited 0 on the committed `HEAD` of each affected `WORKTREE_PATH`. No PR exists yet for this run.

### 4c — Pull requests (`bmo-pr`)

After 4b is green:

1. Read [`bmo-pr`](../bmo-pr/SKILL.md).
2. **Per affected repo** (each `WORKTREE_PATH`): push branch, create or update PR (default base `main`). Use the Problem, Fix, and Verification sections in the body. Footer `Refs [IDENTIFIER]` only when the identifier is an issue key. **Label `agent-built`** on every PR (`--label agent-built` on create; `--add-label agent-built` when updating).
3. Record PR URL per repo in run context.

If push or `gh` fails for a repo, report it in the summary. Do not fail silently.

**Done for 4c:** Every affected repo has a PR URL or a recorded failure reason. 4b was already green on the `HEAD` that was pushed.

### 4d — Summary

Output:

```markdown
# Builder complete: [IDENTIFIER]

**Work:** [title](link-or-plain) · **Type:** [Bug / Feature / Chore]
**Branch:** `feature/…` · **WORKTREE_ID:** `…`
**Repos (n):** [repo → what changed, one line each]
**Worktrees:** [repo → path]
**Plan:** [absolute path]
**Units delivered:** U1 … Un
**Commits:** [hash + subject per repo]
**PRs:** [repo → url, or "failed: …"]

## Problem
[Bug: what was broken and why. Non-bug: what was missing / requested.]

## Fix
[What we changed and why it resolves the problem. 2–4 bullets max.]

## Verification
[4b check commands and exit codes, per repo.]
```

If the handoff included a triage verdict, append:

```markdown
## Triage (reference)
Proceed · Pickup: Yes · Complexity: [Low / Medium] · Repos (n): [same as above]
```

Set run status to `done`.

**Done:** The summary is in chat; status is `done`.

---

## Overrides to child skills

| Child skill | Normal behavior | Under this builder |
|-------------|-----------------|---------------------|
| `bmo-step-deliver` | Pause after each unit; wait for user `continue` | **Autopilot:** after 3b–3d, immediately start next unit. No user message required. |
| `bmo-step-deliver` | Commit only on explicit user ask or `continue` | **Autopilot:** 3d commits each completed unit after review fixes |
| `bmo-commit` | Default: commit staged only; no `git add` | **Autopilot:** orchestrator may `git add` paths for the current unit before commit |
| `bmo-step-planner` | Planning only | Unchanged. Still no code in Phase 1. |
| `bmo-pr` | User invokes separately | **Autopilot:** Phase 4c push + PR per affected repo worktree, only after 4b is green |

Single-unit plans: still run **3b → 3c → 3d** once, then Phase 4.

Multi-repo plans: commit **per git root** per unit; never commit repo B because repo A was committed in the same unit unless both were in scope for `Un`.

---

## Failure handling

| Situation | Action |
|-----------|--------|
| Worktree setup fails for a required repo | Stop before Phase 3; report which repo failed |
| Verification fails after deliver or fixes | Fix within unit if small; otherwise stop with smallest next action |
| Subagent unavailable / Task tool missing | Review blocks **sequentially** in the orchestrator using `bmo-block-reviewer`. Do not skip review. |
| Plan revision needed mid-flight | Update plan file **Revision** section per `bmo-step-deliver`, restate scope, then continue current or next unit |
| User interrupts with "stop" / "abort" | Halt; summarize done vs remaining units. Status `stopped` |
| Final quality check finds issues | Fix, verify, and commit before the 4b checks |
| A 4b check is red | Append one plan unit for the red set and run Phase 3 (3a–3d), then re-run 4b. Open the PR only after every recorded check exits 0 |
| The same check failure remains after that unit's commit | Stop. Status `stopped`. Report the command and output. Leave the PR unopened |
| PR push or `gh` fails | Report in the 4d summary; other repos' PRs still proceed |

---

## What this builder does **not** do

- Triage Linear issues or refuse work by complexity (`/bmo-linear-pipeline`, `/bmo-triage`)
- Force-push to shared branches
- Replace human review for large or ambiguous work

---

## Quick invoke

```
/bmo-builder Fix duplicate pending-deposit notifications when the user retries
```
