---
name: bmo-linear-pipeline
description: Autonomous Linear-issue pipeline for low-complexity work only — triage, plan, isolated worktrees per affected repo (same branch), deliver each U* unit, parallel block review, fix, commit, open PRs via bmo-pr, done summary. Use when the user invokes /bmo-linear-pipeline or passes a Linear issue URL for hands-off pickup of small issues.
disable-model-invocation: true
argument-hint: "[linear issue url]"
---

CRITICAL: Execute every phase below **in order**. Do not implement code before triage passes and a written plan exists. Do not skip block review or commit between units unless the pipeline explicitly exits early.

When invoking child skills, **read their `SKILL.md` first** from `~/.cursor/skills/<name>/SKILL.md` and follow them — except where this pipeline **overrides** pacing (autopilot `continue` between units; see [Overrides](#overrides-to-child-skills)).

**Input:** `$ARGUMENTS` is the Linear issue URL or identifier (e.g. `ENG-123`). If missing, ask once for the link, then stop until provided.

---

## Phase 0 — Record run context

At start, note:

- **Issue link / id:** from `$ARGUMENTS`
- **Branch name:** `feature/[issue-id]-[slug]` (filled in Phase 2.5)
- **WORKTREE_ID:** shared id for this run (filled in Phase 2.5)
- **Worktrees:** `REPO_ROOT → WORKTREE_PATH` per affected repo (filled in Phase 2.5)
- **Plan file path:** (filled in Phase 2)
- **Repos (n):** from triage / plan (filled in Phase 1–2)
- **Current unit:** (filled in Phase 3 loop)
- **Pipeline status:** `running` | `exited-early` | `done`

---

## Phase 1 — Triage (`bmo-triage`)

1. Read and follow [`bmo-triage`](../bmo-triage/SKILL.md) using the Linear issue from `$ARGUMENTS`.
2. Produce the triage output (full template or early-exit template).

### Gate 1 — Stop unless low complexity

**Exit immediately** (pipeline `exited-early`) when **any** of these is true:

| Condition | Action |
|-----------|--------|
| Triage **early exit** (`Skip — unreachable` or `Skip — already done`) | Stop. Output [Early exit output](#early-exit-output). **No planning, no code.** |
| **Complexity** is **Medium** or **High** | Stop. Output [Early exit output](#early-exit-output) with verdict **Stop — complexity not Low**. **No planning, no code.** |
| Complexity row missing or ambiguous | Stop. Ask user to confirm complexity manually; do not proceed until **Low** is confirmed. |

**Proceed only when** the triage **Scores** table shows **Complexity | Low** (case-insensitive).

### Triage verdict (mandatory before Phase 2)

When Gate 1 passes, output this block **in chat** before planning:

```markdown
## Triage verdict: [IDENTIFIER]

**Verdict:** Proceed · **Complexity:** Low · **Type:** [Bug / Feature / Chore]
**Repos (n):** [repo-a] (1) — or list all with count

[1–2 sentences: what the issue is and likely root cause / gap, if known from triage]
```

Record repos count in run context. Then continue to Phase 2.

---

## Phase 2 — Plan (`bmo-step-planner`)

Planning only, no implementation — **do not** call `SwitchMode` or block on mode changes.

1. Read and follow [`bmo-step-planner`](../bmo-step-planner/SKILL.md) using triage context (issue title, AC, repos, gaps).
2. Write the plan file per that skill (`U1`, `U2`, … mandatory when 2+ units).

### Gate 2 — Plan must exist

- **Stop** if no plan file was written.
- **Record** the absolute path to the plan file in run context.
- Parse the list of implementation units (`U1`, `U2`, …) in order from the plan.

If the plan has **Open questions (blocked)** with no `defaults: yes` from the user, **stop** and list blockers — do not implement.

---

## Phase 2.5 — Worktrees (mandatory before deliver)

All implementation happens in **isolated worktrees** — never edit the user's main checkout for an affected repo.

**Affected repos** = union of git roots named in the plan (all units). One worktree per repo, **same branch name** in each.

### Branch name

`feature/[issue-id-lowercase]-[slug-from-title]` — e.g. `feature/dev-3311-pending-deposit-repeated-3-times`.

If the user passed `/worktree branch=…` or an existing feature branch is linked to the issue, use that name instead.

### Setup

1. Pick one **WORKTREE_ID** for the run: `[issue-id]-$(openssl rand -hex 4)` (e.g. `dev3311-a1b2c3d4`).
2. For **each** affected `REPO_ROOT`, create a worktree under `~/.cursor/worktrees/$WORKTREE_ID/`:
   - Prefer Cursor **`/worktree`** when available (same `WORKTREE_ID` + branch for every repo).
   - Else use the multi-repo create block from successful runs (detach from `main` or existing remote branch, then `git checkout -B "$BRANCH"`).
3. Run each repo's `.cursor/worktrees.json` setup once if present.
4. Record `REPO_ROOT → WORKTREE_PATH` in run context.

### Rules

- **Reads, edits, shell, verify, commit** for a repo → use that repo's **WORKTREE_PATH** only.
- Do **not** switch branches or commit in the main workspace for affected repos.
- Reuse an existing chat worktree mapping when the user already ran `/worktree` for this issue — do not create duplicates.

**Gate:** If any required worktree is missing, stop before Phase 3.

Report once:

```markdown
## Worktrees: [IDENTIFIER]

**Branch:** `feature/…` · **WORKTREE_ID:** `dev3311-…`

| Repo | Path |
|------|------|
| roxtopia | `~/.cursor/worktrees/…/roxtopia-…` |
| roxtarsverse | `~/.cursor/worktrees/…/roxtarsverse-…` |
```

Merge back with `/apply-worktree`; cleanup with `/delete-worktree`.

---

## Phase 3 — Per-unit delivery loop

Repeat for **each** unit `U1`, `U2`, … in plan order until all units are done.

For the current unit `Un`:

### 3a — Deliver one unit (`bmo-step-deliver`)

1. Read [`bmo-step-deliver`](../bmo-step-deliver/SKILL.md).
2. Implement **exactly `Un`** only (sliced mode, one unit) — in each repo's **WORKTREE_PATH** from Phase 2.5.
3. Verify per that skill (correct worktree, narrowest proof).
4. Produce **How to run** and the mandatory **`## Review digest`** with blocks **Block A**, **Block B**, …

**Do not** wait for the user to type `continue` before the review sub-phase — this pipeline supplies autopilot `continue` (see [Overrides](#overrides-to-child-skills)).

### 3b — Parallel block review (one subagent per block)

From the **Review digest**, identify each `### Block X — …` section (A, B, C, …).

For **each block**, spawn **one** background subagent in parallel using the host `Task` tool:

- **subagent_type:** `generalPurpose`
- **readonly:** `true`
- **run_in_background:** `true`
- **Prompt:** use [references/block-reviewer-subagent.md](references/block-reviewer-subagent.md) — pass block name, block text, file paths, git root, and issue id.

Each subagent must read and follow [`bmo-block-reviewer`](../bmo-block-reviewer/SKILL.md) and inspect the **actual diff** for files in that block.

**Await** all subagent results before continuing.

### 3c — Apply review fixes

1. Merge findings from all block reviewers.
2. **Fix** every actionable finding (typing, duplication, test style, etc.) in the orchestrator — same unit scope only.
3. Re-run the **narrowest verification** from the plan/deliver step if fixes touched behavior.
4. If a reviewer reported **no issues**, note it and continue.

Do **not** commit before fixes are applied.

### 3d — Commit unit (`bmo-commit`)

1. Read [`bmo-commit`](../bmo-commit/SKILL.md).
2. Stage **only** files changed for **`Un`** in the correct git root (`git add <paths>` — this pipeline **explicitly authorizes** staging for the completed unit).
3. Run `/bmo-commit` workflow on the staged index. If index empty after staging, stop and report — do not skip commit silently.

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
3. Fix every actionable finding, re-run the narrowest affected verification, and commit the final quality fixes before moving on.

This pass exists to catch issues that slip past per-block review, especially repeated PR comments from the learnings catalog.

### 4b — Pull requests (`bmo-pr`)

After the final quality check is green:

1. Read [`bmo-pr`](../bmo-pr/SKILL.md).
2. **Per affected repo** (each `WORKTREE_PATH`): push branch, create or update PR (default base `main`). Reuse Phase 4c problem/fix/verification in the body; footer `Refs [ISSUE-ID]`. **Label `agent-built`** on every PR (`--label agent-built` on create; `--add-label agent-built` when updating).
3. Record PR URL per repo in run context.

If push or `gh` fails for a repo, report it in the summary — do not fail silently.

### 4c — Summary

Output:

```markdown
# Pipeline complete: [ISSUE-ID]

**Issue:** [title](link) · **Type:** [Bug / Feature / Chore]
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
[Command(s) run and result.]

## Triage (reference)
Proceed · Complexity: Low · Repos (n): [same as above]
```

Set pipeline status to `done`.

---

## Early exit output

When Gate 1 stops the pipeline, output:

```markdown
# Pipeline stopped: [IDENTIFIER]

**Verdict:** [Skip — unreachable | Skip — already done | Stop — complexity not Low]
**Link:** [url]

## Findings
[2–4 sentences: status seen, why no work, root cause if investigated, repos touched if any]

## Linear comment
[Copy-paste block for the issue — concise, professional, no agent jargon]

---
_Complexity / ROI from triage if applicable._
```

Set pipeline status to `exited-early`.

---

## Overrides to child skills

| Child skill | Normal behavior | Under this pipeline |
|-------------|-----------------|---------------------|
| `bmo-step-deliver` | Pause after each unit; wait for user `continue` | **Autopilot:** after 3b–3d, immediately start next unit — no user message required |
| `bmo-step-deliver` | Commit only on explicit user ask or `continue` | **Autopilot:** 3d commits each completed unit after review fixes |
| `bmo-commit` | Default: commit staged only; no `git add` | **Autopilot:** orchestrator may `git add` paths for the current unit before commit |
| `bmo-triage` | Planning only | Unchanged — still no code in Phase 1 |
| `bmo-step-planner` | Planning only | Unchanged — still no code in Phase 2 |
| `bmo-pr` | User invokes separately | **Autopilot:** Phase 4b push + PR per affected repo worktree |

Single-unit plans: still run **3b → 3c → 3d** once, then Phase 4.

Multi-repo plans: commit **per git root** per unit; never commit repo B because repo A was committed in the same unit unless both were in scope for `Un`.

---

## Failure handling

| Situation | Action |
|-----------|--------|
| Worktree setup fails for a required repo | Stop before Phase 3; report which repo failed |
| Verification fails after deliver or fixes | Fix within unit if small; otherwise stop with smallest next action |
| Subagent unavailable / Task tool missing | Review blocks **sequentially** in the orchestrator using `bmo-block-reviewer` — do not skip review |
| Plan revision needed mid-flight | Update plan file **Revision** section per `bmo-step-deliver`, restate scope, then continue current or next unit |
| User interrupts with "stop" / "abort" | Halt pipeline; summarize done vs remaining units |
| Final quality check finds issues | Fix, verify, and commit before Phase 4b PR creation |
| PR push or `gh` fails | Report in 4b summary; other repos' PRs still proceed |

---

## What this pipeline does **not** do

- Pick up **Medium** or **High** complexity issues
- Force-push to shared branches
- Replace human review for large or ambiguous work

---

## Quick invoke

```
/bmo-linear-pipeline https://linear.app/team/issue/ENG-123
```
