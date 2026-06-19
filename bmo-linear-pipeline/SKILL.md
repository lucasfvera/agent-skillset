---
name: bmo-linear-pipeline
description: Autonomous Linear-issue pipeline for low-complexity work only — triage (bmo-triage), plan (bmo-step-planner in plan mode), deliver each U* unit (bmo-step-deliver), parallel block review subagents (bmo-block-reviewer), fix findings, commit (bmo-commit), repeat until the plan is done. Use when the user invokes /bmo-linear-pipeline or passes a Linear issue URL for hands-off pickup of small issues.
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
- **Plan file path:** (filled in Phase 2)
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
| Triage **early exit** (`Skip — unreachable` or `Skip — already done`) | Stop. Output early-exit summary only. **No planning, no code.** |
| **Complexity** is **Medium** or **High** | Stop. Output triage summary + one line: **"Complexity is not Low — pipeline stopped."** **No planning, no code.** |
| Complexity row missing or ambiguous | Stop. Ask user to confirm complexity manually; do not proceed until **Low** is confirmed. |

**Proceed only when** the triage **Scores** table shows **Complexity | Low** (case-insensitive).

Record the triage summary in chat (short); keep going to Phase 2.

---

## Phase 2 — Plan (`bmo-step-planner`, plan mode)

1. **Switch to plan mode** using the host `SwitchMode` tool (`target_mode_id: plan`) so planning stays read-only. If switch is unavailable, state that and still follow `bmo-step-planner` rules (planning only, no implementation).
2. Read and follow [`bmo-step-planner`](../bmo-step-planner/SKILL.md) using triage context (issue title, AC, repos, gaps).
3. Write the plan file per that skill (`U1`, `U2`, … mandatory when 2+ units).
4. **Switch back to agent mode** (`SwitchMode` → `agent`) before any implementation.

### Gate 2 — Plan must exist

- **Stop** if no plan file was written.
- **Record** the absolute path to the plan file in run context.
- Parse the list of implementation units (`U1`, `U2`, …) in order from the plan.

If the plan has **Open questions (blocked)** with no `defaults: yes` from the user, **stop** and list blockers — do not implement.

---

## Phase 3 — Per-unit delivery loop

Repeat for **each** unit `U1`, `U2`, … in plan order until all units are done.

For the current unit `Un`:

### 3a — Deliver one unit (`bmo-step-deliver`)

1. Read [`bmo-step-deliver`](../bmo-step-deliver/SKILL.md).
2. Implement **exactly `Un`** only (sliced mode, one unit).
3. Verify per that skill (correct workspace, narrowest proof).
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

Output:

```markdown
# Pipeline complete: [ISSUE-ID]

**Plan:** [absolute path to plan file]
**Units delivered:** U1 … Un (all)
**Commits:** [short list per repo / unit if helpful]

## Summary
[2–4 sentences: what shipped, verification run, anything deferred]

## Triage (reference)
Complexity: Low · [link]
```

Set pipeline status to `done`.

---

## Overrides to child skills

| Child skill | Normal behavior | Under this pipeline |
|-------------|-----------------|---------------------|
| `bmo-step-deliver` | Pause after each unit; wait for user `continue` | **Autopilot:** after 3b–3d, immediately start next unit — no user message required |
| `bmo-step-deliver` | Commit only on explicit user ask or `continue` | **Autopilot:** 3d commits each completed unit after review fixes |
| `bmo-commit` | Default: commit staged only; no `git add` | **Autopilot:** orchestrator may `git add` paths for the current unit before commit |
| `bmo-triage` | Planning only | Unchanged — still no code in Phase 1 |
| `bmo-step-planner` | Planning only | Unchanged — still no code in Phase 2 |

Single-unit plans: still run **3b → 3c → 3d** once, then Phase 4.

Multi-repo plans: commit **per git root** per unit; never commit repo B because repo A was committed in the same unit unless both were in scope for `Un`.

---

## Failure handling

| Situation | Action |
|-----------|--------|
| Verification fails after deliver or fixes | Fix within unit if small; otherwise stop with smallest next action |
| Subagent unavailable / Task tool missing | Review blocks **sequentially** in the orchestrator using `bmo-block-reviewer` — do not skip review |
| Plan revision needed mid-flight | Update plan file **Revision** section per `bmo-step-deliver`, restate scope, then continue current or next unit |
| User interrupts with "stop" / "abort" | Halt pipeline; summarize done vs remaining units |

---

## What this pipeline does **not** do

- Pick up **Medium** or **High** complexity issues
- Open PRs (use `/bmo-pr` separately if needed)
- Push to remote unless the user asks later
- Replace human review for large or ambiguous work

---

## Quick invoke

```
/bmo-linear-pipeline https://linear.app/team/issue/ENG-123
```
