---
name: bmo-issue-pipeline
description: Triages an issue and, on pickup, hands off to bmo-builder for plan through PR.
disable-model-invocation: true
argument-hint: "[issue url, TEAM-123, or owner/repo#123]"
---

Triage, then Gate 1, then `bmo-builder` in this same turn. Builder starts only after Gate 1 passes. Builder completion includes proven isolated worktrees before any implementation edit.

When invoking child skills, **read their `SKILL.md` first** from the sibling directory (`../<name>/SKILL.md`) and follow them.

**Input:** `$ARGUMENTS` is an issue URL or identifier (e.g. `ENG-123`, `owner/repo#42`, `#42`, or a Linear/GitHub link). If missing, ask once for the issue link or identifier, then stop until provided.

---

## Phase 0 — Record run context

At start, note:

- **Issue link / id:** from `$ARGUMENTS`
- **Pipeline status:** `running` | `exited-early` | `done`

---

## Phase 1 — Triage (`bmo-triage`)

1. Read and follow [`bmo-triage`](../bmo-triage/SKILL.md) using the issue from `$ARGUMENTS`.
2. Produce the triage output (full template or early-exit template).

**Done:** triage template is in chat.

### Gate 1 — Pickup

Read the triage output. Do not re-score. The **Pickup** cell is the gate; its formula lives in `bmo-triage`.

**Pass** when **all** of these hold:

- Verdict is `Proceed` (not Skip, not Block)
- Scores **Pickup** is `Yes` (case-insensitive)

Then output the [Triage verdict](#triage-verdict) block. Status stays `running`.

**Stop** on the first match (status `exited-early`, emit [Early exit output](#early-exit-output), leave `bmo-builder` unread):

| Triage | Pipeline verdict |
|--------|------------------|
| `Skip — unreachable` or `Skip — already done` | same Skip verdict |
| `Block — AC unclear` | `Stop — AC unclear` |
| Pickup `No` | `Stop — not pickup` |
| Full template, Pickup row missing or not Yes/No | Ask once to confirm pickup; stop until the user sets Pickup to Yes |

Block wins over Pickup Yes: unclear AC never starts builder.

**Done:** verdict block in chat and Pickup is Yes, **or** early-exit template in chat and status is `exited-early`.

### Triage verdict

When Gate 1 passes, output this block **in chat** before handing off:

```markdown
## Triage verdict: [IDENTIFIER]

**Verdict:** Proceed · **Pickup:** Yes · **Complexity:** [Low / Medium] · **ROI:** [High / Medium] · **Type:** [Bug / Feature / Chore]
**Repos (n):** [repo-a] (1) — or list all with count

[1–2 sentences: what the issue is and likely root cause / gap, if known from triage]
```

**Done:** Verdict block is in chat; Pickup is Yes; status is still `running`.

---

## Phase 2 — Build (`bmo-builder`)

Read [`bmo-builder`](../bmo-builder/SKILL.md) from the first line and execute it to completion. Do not re-triage. Do not wait for another user message. Builder autopilot applies (plan → worktrees → per-unit deliver / block review / commit → checks green → PRs). The builder is not complete if any implementation edit landed in a main checkout.

Pass this handoff as the builder's input:

```
Identifier: [IDENTIFIER]
Title: [title]
Type: [Bug / Feature / Chore]
Link: [url]
Repos: [from triage]
Acceptance / gaps:
[AC and gaps from triage]

Triage: Proceed · Pickup: Yes · Complexity: [Low / Medium] · ROI: [from triage]
```

When the builder finishes, set pipeline status to `done`.

**Done:** `bmo-builder` has run to `done` (or stopped with a reported reason); this pipeline's status matches.

---

## Early exit output

When Gate 1 stops the pipeline, output:

```markdown
# Pipeline stopped: [IDENTIFIER]

**Verdict:** [Skip — unreachable | Skip — already done | Stop — AC unclear | Stop — not pickup]
**Link:** [url]

## Findings
[2–4 sentences: status seen, why no work, root cause if investigated, repos touched if any]

## Issue comment
[Copy-paste block for the tracker — concise, professional, no agent jargon]

---
_Complexity / ROI from triage if applicable._
```

Set pipeline status to `exited-early`.

---

## Scope

On pickup: run `bmo-builder` to PRs. Otherwise: stop with the early-exit template.
