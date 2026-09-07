---
name: bmo-linear-pipeline
description: Triages a Linear issue and, when complexity is Low, hands off to bmo-builder for plan through PR.
disable-model-invocation: true
argument-hint: "[linear issue url]"
---

CRITICAL: Triage first. Do not plan or implement until Gate 1 passes. After Gate 1, execute `bmo-builder` to completion in this same turn. Builder completion includes proven isolated worktrees before any implementation edit.

When invoking child skills, **read their `SKILL.md` first** from `~/.cursor/skills/<name>/SKILL.md` and follow them.

**Input:** `$ARGUMENTS` is the Linear issue URL or identifier (e.g. `ENG-123`). If missing, ask once for the link, then stop until provided.

---

## Phase 0 — Record run context

At start, note:

- **Issue link / id:** from `$ARGUMENTS`
- **Pipeline status:** `running` | `exited-early` | `done`

---

## Phase 1 — Triage (`bmo-triage`)

1. Read and follow [`bmo-triage`](../bmo-triage/SKILL.md) using the Linear issue from `$ARGUMENTS`.
2. Produce the triage output (full template or early-exit template).
3. **Chat title (recommended).** This skill is the user's request to rename the chat. Call `rename_chat` (`cursor-app-control`) with `[ISSUE-ID] [feature or minimal description]`, e.g. `DEV-1234 Pending deposit repeated 3 times`. Use the Linear identifier as-is and a tightened issue title (strip a leading id if the title repeats it). If rename fails, is aborted, or the conversation cannot be identified, continue.

### Gate 1 — Stop unless low complexity

**Exit immediately** (pipeline `exited-early`) when **any** of these is true:

| Condition | Action |
|-----------|--------|
| Triage **early exit** (`Skip — unreachable` or `Skip — already done`) | Stop. Output [Early exit output](#early-exit-output). **No planning, no code.** |
| **Complexity** is **Medium** or **High** | Stop. Output [Early exit output](#early-exit-output) with verdict **Stop — complexity not Low**. **No planning, no code.** |
| Complexity row missing or ambiguous | Stop. Ask user to confirm complexity manually; do not proceed until **Low** is confirmed. |

**Proceed only when** the triage **Scores** table shows **Complexity | Low** (case-insensitive).

### Triage verdict (mandatory before Phase 2)

When Gate 1 passes, output this block **in chat** before handing off:

```markdown
## Triage verdict: [IDENTIFIER]

**Verdict:** Proceed · **Complexity:** Low · **Type:** [Bug / Feature / Chore]
**Repos (n):** [repo-a] (1) — or list all with count

[1–2 sentences: what the issue is and likely root cause / gap, if known from triage]
```

**Done:** Verdict block is in chat; complexity is Low; status is still `running`.

---

## Phase 2 — Build (`bmo-builder`)

Read [`bmo-builder`](../bmo-builder/SKILL.md) from the first line and execute it to completion. Do not re-triage. Do not wait for another user message. Builder autopilot applies (plan → worktrees → per-unit deliver / block review / commit → PRs). The builder is not complete if any implementation edit landed in a main checkout.

Pass this handoff as the builder's input:

```
Identifier: [ISSUE-ID]
Title: [title]
Type: [Bug / Feature / Chore]
Link: [url]
Repos: [from triage]
Acceptance / gaps:
[AC and gaps from triage]

Triage: Proceed · Complexity: Low
```

When the builder finishes, set pipeline status to `done`.

**Done:** `bmo-builder` has run to `done` (or stopped with a reported reason); this pipeline's status matches.

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

## What this pipeline does **not** do

- Pick up **Medium** or **High** complexity issues
- Plan, deliver, or open PRs itself (that is `/bmo-builder`)
- Force-push to shared branches
- Replace human review for large or ambiguous work

---

## Quick invoke

```
/bmo-linear-pipeline https://linear.app/team/issue/ENG-123
```
