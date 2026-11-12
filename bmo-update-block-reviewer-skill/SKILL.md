---
name: bmo-update-block-reviewer-skill
description: Distills pending PR review captures into domain- and tier-classified rules for bmo-block-reviewer.
disable-model-invocation: true
argument-hint: "[optional session id or filename fragment; default all pending]"
---

# Update block reviewer from PR feedback

Turn **pending inbox captures** from [`bmo-respond-pr-review`](../bmo-respond-pr-review/SKILL.md) into deduplicated review rules for [`bmo-block-reviewer`](../bmo-block-reviewer/SKILL.md) and its domain catalogs (`frontend`, `backend`, `database`, `testing`). Audit state and unpromoted 1-source style candidates live in [`ledger.md`](ledger.md), never in the reviewer's context.

**Input:** `$ARGUMENTS` is an optional session `id` or filename fragment. If omitted, process **all** files in `inbox/pending/`.

**Default source:** local files in `inbox/pending/*.md` (see [references/session-capture.md](references/session-capture.md)). Use [references/fetch-pr-feedback.md](references/fetch-pr-feedback.md) only when recovering a missing capture.

---

## Learning shape

| Field | Type | Notes |
|-------|------|-------|
| `id` | slug | kebab-case, stable across sessions |
| `domain` | enum | `core` \| `frontend` \| `backend` \| `database` \| `testing` |
| `tier` | enum | `issue` (correctness, contract, security, perf, false/flaky test) \| `style` (structure, conventions, readability, test ergonomics) |
| `rule` | string | One-line positive-target rule + brief why (`- **[id]** <what to write>; <why/guardrail>.`). No file paths or verbatim PR quotes |
| `sources` | string[] | `owner/repo#number` list stored only in [`ledger.md`](ledger.md) |
| `status` | enum | `candidate` (1-source `style` rule waiting in `ledger.md`) \| `promoted` (active in `bmo-block-reviewer`) |

---

## Procedure

### 1. List and load pending captures

```bash
ls "$SKILL_DIR"/inbox/pending/*.md 2>/dev/null
```

Filter by `$ARGUMENTS` when provided. If no files match, report "no pending captures" and stop. Read every selected file in full and collect all threads with their `pr` (`owner/repo#number`) and session `id`.

**Done:** Every matching capture in `inbox/pending/` is loaded into memory.

### 2. Extract abstract rules (`domain` + `tier`)

Read [references/extraction-rules.md](references/extraction-rules.md). For each thread:

1. Ask: **what general rule would have caught or prevented this feedback?**
2. Classify **`domain`** (`core`, `frontend`, `backend`, `database`, `testing`) by the file layer the rule governs.
3. Classify **`tier`**:
   - **`issue`** when violating the rule causes wrong runtime behavior, broken contracts/status codes, security/error leaks, DB connection/lock waste, hot-path latency, or flaky/vacuous tests.
   - **`style`** when the code works and performs fine, and the rule encodes structural, layout, DRY, naming, or test-readability taste.
4. Phrase the rule positively (state what to write first). Skip one-off typos or purely local fixes.

**Done:** Every extractable thread is mapped to `{ id, domain, tier, rule, source }`.

### 3. Dedupe against batch and `ledger.md`

Read [`ledger.md`](ledger.md) and the target domain files in [`../bmo-block-reviewer/`](../bmo-block-reviewer/SKILL.md).

1. **Within the batch:** Merge threads from different sessions that express the same rule and combine their `sources`.
2. **Against `ledger.md`:** When `id` or intent matches an existing row (candidate or promoted), append the new `owner/repo#number` to `sources` instead of creating a second ID.

**Done:** Zero duplicate rule intents exist across the batch, `ledger.md`, and `bmo-block-reviewer`.

### 4. Promote or stage (`references/promotion-rules.md`)

Read [references/promotion-rules.md](references/promotion-rules.md) and apply the tier threshold:

- **`tier: issue` (1+ PR source, durable & actionable):**
  1. Append `- **[id]** <rule>` under `## 1. Strict issues ([issue])` (or `## Core — Strict issues ([issue])` in `SKILL.md`) in the matching domain file:
     - `core` → [`../bmo-block-reviewer/SKILL.md`](../bmo-block-reviewer/SKILL.md)
     - `frontend` → [`../bmo-block-reviewer/references/frontend.md`](../bmo-block-reviewer/references/frontend.md)
     - `backend` → [`../bmo-block-reviewer/references/backend.md`](../bmo-block-reviewer/references/backend.md)
     - `database` → [`../bmo-block-reviewer/references/database.md`](../bmo-block-reviewer/references/database.md)
     - `testing` → [`../bmo-block-reviewer/references/testing.md`](../bmo-block-reviewer/references/testing.md)
  2. Record the rule under **Active promoted rules** in [`ledger.md`](ledger.md).
- **`tier: style` with 1 PR source:**
  1. Add the row under **Candidates** in [`ledger.md`](ledger.md) using [templates/learning-entry.md](templates/learning-entry.md). Leave `bmo-block-reviewer` files untouched.
- **`tier: style` reaching 2+ PR sources (newly merged candidate or multi-PR batch, or explicit user request):**
  1. Remove the row from **Candidates** in [`ledger.md`](ledger.md) and add it to **Active promoted rules**.
  2. Append `- **[id]** <rule>` under `## 2. Style & conventions ([style])` (or `## Core — Style & conventions ([style])` in `SKILL.md`) in the matching domain file.

**Done:** Every qualifying `issue` (1+ source) and recurring `style` rule (2+ sources) is written to its single domain file and indexed as promoted in `ledger.md`; every 1-source `style` rule sits only in `ledger.md` Candidates.

### 5. Mark captures actioned and report

For each processed capture file, set frontmatter `status: actioned` and `actionedAt` to current UTC ISO8601, then move the file from `inbox/pending/` to `inbox/actioned/`.

Report in chat:
- Captures actioned (IDs and thread count)
- Newly promoted rules (`[tier] [domain] [id]` + target file)
- New or updated `style` candidates staged in `ledger.md` (`[domain] [id]` + source count)
- Skipped threads (too local or already covered)

**Done:** All processed captures are in `inbox/actioned/` with `status: actioned`, and the summary report is posted.
