---
name: bmo-triage
description: Triages a Linear issue from a URL into complexity, importance, and ROI (user value vs implementation effort). Exits early when the issue is unreachable or already closed. Use when the user invokes /bmo-triage or passes a Linear issue link for prioritization before planning or implementation.
disable-model-invocation: true
---

# Triage (bmo)

**Planning only** — fetch and analyze the Linear issue; do **not** implement code, never.

## When to use

- User passes a **Linear issue URL** (or identifier like `ENG-123`) and wants a quick **go / no-go** read.
- User asks for **complexity**, **importance**, or **ROI** before picking up work.

## Workflow

### 1) Resolve the issue

1. Extract identifier from the link (`ENG-123`, `ROX-456`, etc.) or use the identifier directly.
2. Fetch issue data via **Linear MCP** (preferred). If tools are missing or auth fails, call `mcp_auth` once and retry. Fallback: `gh` if the issue is linked to GitHub, or ask the user to paste title + description.
3. Read at minimum: **title**, **description**, **status**, **priority**, **labels**, **comments** (recent), **linked PRs**, **project/team**, **acceptance criteria** (if in a dedicated field or checklist).

### 2) Early exit (mandatory)

Stop triage and output only the **Early exit** template when **any** of these is true:

| Condition | Verdict |
|-----------|---------|
| Issue not found, private without access, or fetch failed | `Skip — unreachable` |
| Status is terminal / no work expected | `Skip — already done` |

Treat these statuses as **terminal** (case-insensitive): `Done`, `Completed`, `Canceled`, `Cancelled`, `Duplicate`, `Won't fix`, `Wont fix`, `Archived`, `Released`, `Deployed` (when clearly shipped).

If status is ambiguous (e.g. `In Review` with open PR), **do not** early-exit — note it and continue.

### 3) Analyze

Answer each row honestly from issue content + light codebase search only when repos are unclear.

| Dimension | What to judge |
|-----------|----------------|
| **Type** | Feature, Bug, Chore, or Unknown |
| **Clarity** | Is the problem/ask understandable? **Clear** / **Partial** / **Unclear** |
| **Acceptance criteria** | **Yes** (testable checklist or explicit done-when) / **Partial** / **No** |
| **Reproducible** (bugs only) | **Yes** / **Maybe** / **No** / **N/A** (features/chores) — steps, env, account state, screenshots, logs |
| **Stack** | **Frontend** / **Backend** / **Fullstack** / **Unknown** |
| **Repos** | List likely repos; count them. Infer from labels, paths in description, linked PRs, or a quick search in the open workspace. Mark **uncertain** when guessing. |

**Complexity** (`Low` | `Medium` | `High`) — implementation effort, not user impact:

- **Low** — localized change, known pattern, 1 repo, no migration/schema churn, clear fix.
- **Medium** — multiple files or layers, some unknowns, tests need setup, 2 repos, or moderate integration.
- **High** — cross-cutting, new contracts, migrations, unclear root cause, 3+ repos, or high regression risk.

**User value** (`Low` | `Medium` | `High`) — benefit to end users if shipped. Use the Kano model to determine the user value.

- **High** — blocks core flows, revenue/trust, many users, or strong product signal.
- **Medium** — meaningful improvement or painful bug for a subset.
- **Low** — polish, internal-only, edge case, or nice-to-have.

**Importance** (`Low` | `Medium` | `High`) — urgency / priority for the team (use Linear priority, due date, incident labels, SLA, or explicit “blocking” language; do not conflate with user value).

**ROI** (`Low` | `Medium` | `High`) — value relative to complexity:

| User value ↓ / Complexity → | Low | Medium | High |
|------------------------------|-----|--------|------|
| **High** | High | Medium | Low |
| **Medium** | High | Medium | Low |
| **Low** | Medium | Low | Low |

Override the matrix in one sentence when context demands (e.g. compliance must-fix despite high complexity → note **Low ROI** but **High importance**).

### 4) Output

Use the template below. Keep it **short** — bullets over paragraphs. The user should be able to tweak scores manually.

## Output template — full triage

```markdown
# Triage: [IDENTIFIER] [title]

**Link:** [url]
**Status:** [status] · **Priority:** [priority or —]
**Verdict:** Proceed

## Summary
[2–3 sentences: what it is, whether it is ready to pick up, main risk.]

## Findings

| | |
|---|---|
| Type | Feature / Bug / Chore / Unknown |
| Clarity | Clear / Partial / Unclear — [one line why] |
| Acceptance criteria | Yes / Partial / No — [one line] |
| Reproducible | Yes / Maybe / No / N/A — [one line] |
| Stack | Frontend / Backend / Fullstack / Unknown |
| Repos (n) | [repo-a, repo-b] (2) — [certain / inferred] |

## Scores

| | |
|---|---|
| User value | Low / Medium / High |
| Complexity | Low / Medium / High |
| Importance | Low / Medium / High |
| **ROI** | **Low / Medium / High** |

**ROI note:** [one sentence tying value to effort]

## Gaps
- [missing repro, AC, owner, design, etc. — or "None"]

## Suggested next step
[Pick up now / clarify with PM / spike / defer — one line]
```

## Output template — early exit

```markdown
# Triage: [IDENTIFIER or "unreachable"]

**Link:** [url or —]
**Verdict:** Skip — [unreachable | already done]

**Reason:** [one sentence]

**Status seen:** [status or error]
```

## Rules

1. **No implementation** — triage only.
2. **No invented facts** — if the issue lacks detail, say so under **Gaps**; lower clarity and ROI confidence.
3. **Bugs without repro** — cap complexity confidence; list what is needed to reproduce.
4. **Do not over-search** — repo inference should be fast; 1–2 targeted searches max unless the user asks for deep investigation.
5. **Scores are recommendations** — phrase so the user can override manually.
