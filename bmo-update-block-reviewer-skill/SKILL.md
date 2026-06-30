---
name: bmo-update-block-reviewer-skill
description: >-
  Processes pending session captures from bmo-respond-pr-review in
  inbox/pending/, distills them into abstract guidelines, dedupes against the
  learnings catalog, promotes durable rules into bmo-block-reviewer when warranted,
  and moves captures to inbox/actioned/. Use when the user invokes
  /bmo-update-block-reviewer-skill or asks to improve the block reviewer from
  accumulated PR feedback.
disable-model-invocation: true
argument-hint: "[optional session id or filename fragment; default all pending]"
---

# Update block reviewer from PR feedback

Turn **pending inbox captures** into abstract guidelines for [`bmo-block-reviewer`](../bmo-block-reviewer/SKILL.md). Keep this skill thin. Store durable rules in [learnings/catalog.md](learnings/catalog.md).

**Typical trigger:** run in a **separate session** after one or more [`bmo-respond-pr-review`](../bmo-respond-pr-review/SKILL.md) runs. Each respond session writes to [inbox/pending/](inbox/pending/).

**Input:** `$ARGUMENTS` is an optional session `id` or filename fragment. If omitted, process **all** files in `inbox/pending/`.

**No GitHub fetch in the default path.** Source material is the captured session files.

---

## Data shapes

### Session capture (`inbox/pending/*.md`)

Written by respond-pr-review. See [references/session-capture.md](references/session-capture.md).

| Field | Notes |
|-------|-------|
| `id` | Filename stem |
| `status` | `pending` until this skill runs |
| `capturedAt` | When respond-pr-review finished |
| `actionedAt` | Set when this skill finishes processing |
| `pr` | `owner/repo#number` |
| `threads[]` | Verbatim reviewer comment + resolution per thread |

### Learning (catalog output)

| Field | Type | Notes |
|-------|------|-------|
| `id` | slug | kebab-case, stable across sessions |
| `category` | enum | `typing` \| `tests` \| `architecture` \| `patterns` \| `style` \| `performance` \| `other` |
| `guideline` | string | One imperative rule. No paths, no PR comment quotes |
| `rationale` | string | Why the rule matters (1–2 sentences) |
| `sources` | string[] | `owner/repo#number` only |
| `promoted` | boolean | `true` when copied into `bmo-block-reviewer/SKILL.md` |

---

## Order of operations

```
1. List pending session captures
2. Load selected captures
3. Extract abstract learnings (all threads, all sessions)
4. Dedupe across sessions and against catalog
5. Append net-new learnings to catalog
6. Promote to block-reviewer (only when warranted)
7. Mark captures actioned (move pending → actioned)
8. Report back in chat
```

---

## 1. List pending captures

```bash
ls ~/.cursor/skills/bmo-update-block-reviewer-skill/inbox/pending/*.md 2>/dev/null
```

If `$ARGUMENTS` is set, filter to matching `id` or filename fragment.

If none match, report "no pending captures" and stop.

---

## 2. Load captures

Read every selected file in full. Collect all threads across sessions into one working set. Note each thread's source `pr` and session `id` for traceability.

---

## 3. Extract abstract learnings

Read [references/extraction-rules.md](references/extraction-rules.md) before extracting.

For each thread across **all** pending sessions:

1. Read reviewer comment and resolution from the capture file.
2. Ask: **what general rule would have caught or prevented this feedback?**
3. Write one `guideline` — team-wide, not a description of the fix.
4. Drop thread-specific detail.

Process **dismissed** threads when they encode a standing preference.

---

## 4. Dedupe

Read [learnings/catalog.md](learnings/catalog.md).

Dedupe in two passes:

1. **Within the batch** — merge threads from different sessions that express the same rule into one learning before writing.
2. **Against catalog** — merge when `id` or intent matches an existing entry; append `owner/repo#number` to `sources`.

Repeated feedback across sessions strengthens a rule but must not duplicate catalog rows.

---

## 5. Append to catalog

Add only net-new learnings. Use [templates/learning-entry.md](templates/learning-entry.md).

Group by `category`. The catalog may grow; `bmo-block-reviewer/SKILL.md` must not.

---

## 6. Promote to block-reviewer

Read [references/promotion-rules.md](references/promotion-rules.md).

Promotion is **rare**. Cross-session repetition (same rule from 2+ `sources`) is a promotion signal per promotion rules.

When promoting, add one bullet under the matching section in `bmo-block-reviewer/SKILL.md` and set `promoted: true` on the catalog entry.

---

## 7. Mark captures actioned

For **each** processed session file:

1. Set frontmatter `status: actioned` and `actionedAt` to current UTC ISO8601.
2. **Move** the file from `inbox/pending/` to `inbox/actioned/` (same filename).

Do not delete captures. `inbox/actioned/` is the audit trail.

If extraction fails for one file, leave it in `pending/` and report which file was skipped.

---

## 8. Chat report

- Pending captures processed (ids)
- Sessions actioned (moved to `inbox/actioned/`)
- Thread count across sessions
- New catalog learnings (id + one-line guideline)
- Merged into existing entries (id + new sources)
- Cross-session dedupes (same rule from N sessions)
- Promoted to block-reviewer (if any)
- Skipped threads (too local or already covered)
- Left in pending (if any failed)

---

## Checklist

```
- [ ] Pending captures listed
- [ ] All selected captures loaded
- [ ] Extraction rules applied (abstract guidelines only)
- [ ] Batch + catalog dedupe done
- [ ] Catalog updated
- [ ] Block reviewer touched only per promotion rules
- [ ] Every processed capture marked actioned and moved
- [ ] Chat report posted
```

---

## Additional reference

- Session capture format: [references/session-capture.md](references/session-capture.md)
- Extraction: [references/extraction-rules.md](references/extraction-rules.md)
- Promotion: [references/promotion-rules.md](references/promotion-rules.md)
- Catalog: [learnings/catalog.md](learnings/catalog.md)
- Recovery fetch (only if a capture is missing): [references/fetch-pr-feedback.md](references/fetch-pr-feedback.md)
