---
name: bmo-triage
description: Triages a Linear issue into complexity, Kano user value, importance, and ROI. Blocks when acceptance criteria are not explicit or derivable; skips unreachable or already-closed issues.
disable-model-invocation: true
argument-hint: "[linear issue url]"
---

# Triage (bmo)

Triage output only: fetch the Linear issue, score it, emit the template.

## Workflow

### 1) Resolve the issue

1. Extract identifier from the link (`ENG-123`, `ROX-456`, etc.) or use the identifier directly.
2. Fetch issue data via **Linear MCP** (preferred). If tools are missing or auth fails, call `mcp_auth` once and retry. Fallback: `gh` if the issue is linked to GitHub, or ask the user to paste title + description.
3. Read at minimum: **title**, **description**, **status**, **priority**, **labels**, **comments** (recent), **linked PRs**, **project/team**, **acceptance criteria** (dedicated field, checklist, or description).

**Done:** identifier resolved and those fields read, or fetch failed (then step 2).

### 2) Early exit (mandatory)

Stop and emit only the **Early exit** template when **any** of these is true:

| Condition | Verdict |
|-----------|---------|
| Issue not found, private without access, or fetch failed | `Skip — unreachable` |
| Status is terminal / no work expected | `Skip — already done` |

Treat as **terminal** when Linear `statusType` is `completed` or `canceled`, or the status name matches (case-insensitive): `Done`, `Completed`, `Ready for release`, `Canceled`, `Cancelled`, `Duplicate`, `Won't fix`, `Wont fix`, `Archived`, `Released`, `Deployed` (when clearly shipped).

If status is ambiguous (e.g. `In Review` with open PR), continue triage and note the status.

**Done:** Skip template emitted, or neither skip condition holds.

### 3) Analyze

Fill every Findings row from the issue. Missing detail goes under **Gaps** (no invented facts). If a bug's **Reproducible** is `No`, list the missing steps there.

| Dimension | What to judge |
|-----------|----------------|
| **Type** | Feature, Bug, Chore, or Unknown |
| **Clarity** | Is the problem/ask understandable? **Clear** / **Partial** / **Unclear** |
| **Acceptance criteria** | **Explicit** / **Derived** / **Unclear** — see AC below |
| **Reproducible** (bugs only) | **Yes** / **Maybe** / **No** / **N/A** (features/chores) — steps, env, account state, screenshots, logs |
| **Stack** | **Frontend** / **Backend** / **Fullstack** / **Unknown** |
| **Repos** | Git remotes (not packages/apps in a monorepo). Names and count from labels, paths, linked PRs, or at most two workspace searches. Mark **certain** / **inferred**. Count is a finding, not a band. |

#### Acceptance criteria (blocker)

A testable done-when, from either source:

- **Explicit** — checklist, dedicated AC field, or numbered done-when in the issue.
- **Derived** — no AC field, but the description still yields a testable done-when. Quote that done-when in the Findings one-liner.
- **Unclear** — cannot name a testable done-when. **Blocker.** Verdict `Block — AC unclear`. Suggested next step: get a testable done-when. Still score the issue.

**Done:** every Findings row filled; AC is Explicit, Derived (with quoted done-when), or Unclear.

#### Complexity (`Low` | `Medium` | `High`)

Implementation effort, not user impact. **Highest matching band wins.** **Low** only when every Low condition holds and no Medium or High bullet matches. Git-repo count does not set the band: two remotes can still be Low when the change is the same localized pattern in each.

**Low** — all of:

- Change is nameable (clear fix)
- Localized to one area, or the same pattern in a second git repo
- Existing pattern
- No new contract, migration, or schema churn

**Medium** — any of:

- Distinct layers that both must change (e.g. UI + existing API) without new contracts
- A **bounded unknown**: plausible mechanism named, but which of a few call sites is unconfirmed

**High** — any of:

- New contracts, migrations, or schema churn
- Cross-cutting (shared kernel, many independent call sites)
- No plausible mechanism (symptom only)
- High regression surface: auth, **money movement** (balances, submit, fee math), infra — not display-only denomination or copy

**Done:** one band, from the tie-break above.

#### User value (`Low` | `Medium` | `High`)

Kano: end-user reaction if shipped (not team urgency).

| Kano | Score | Signals |
|------|-------|---------|
| **Must-be** broken, or **performance** for core / revenue / many users | High | core flow blocked, trust/money, strong product signal |
| **Performance** or must-be pain for a subset | Medium | meaningful improvement, painful for some |
| **Delighter** | Low | polish, internal-only, edge, nice-to-have |

**Done:** one Kano category named and mapped to the score.

#### Importance (`Low` | `Medium` | `High`)

Team urgency (Linear priority, dates, incidents) — not Kano.

- **High** — Urgent, incident, SLA, explicit blocking, overdue
- **Medium** — High priority, or due this cycle
- **Low** — Medium / Low / None, no date pressure

#### ROI (`Low` | `Medium` | `High`)

Value relative to complexity:

| User value ↓ / Complexity → | Low | Medium | High |
|------------------------------|-----|--------|------|
| **High** | High | High | Low |
| **Medium** | High | Medium | Low |
| **Low** | Medium | Low | Low |

Override the matrix in one sentence when context demands (e.g. compliance must-fix despite high complexity → **Low ROI**, **High importance**).

**Pickup** (pipeline Gate 1): Complexity **Low**, or Complexity **Medium** and ROI **High**. High complexity is never pickup.

### 4) Output

Emit the full template. Short: bullets over paragraphs. Scores are recommendations the user can override.

| AC | Verdict |
|----|---------|
| Explicit or Derived | `Proceed` |
| Unclear | `Block — AC unclear` |

Suggested next step is **Pick up now** when Verdict is Proceed and **Pickup** holds; otherwise spike/defer (or get a testable done-when if AC Unclear).

**Done:** matching template emitted; Verdict follows the AC table; suggested next step follows Pickup.

## Output template — full triage

```markdown
# Triage: [IDENTIFIER] [title]

**Link:** [url]
**Status:** [status] · **Priority:** [priority or —]
**Verdict:** [Proceed | Block — AC unclear]

## Summary
[2–3 sentences: what it is, whether it is ready to pick up, main risk.]

## Findings

| | |
|---|---|
| Type | Feature / Bug / Chore / Unknown |
| Clarity | Clear / Partial / Unclear — [one line why] |
| Acceptance criteria | Explicit / Derived / Unclear — [quote done-when, or what is missing] |
| Reproducible | Yes / Maybe / No / N/A — [one line] |
| Stack | Frontend / Backend / Fullstack / Unknown |
| Repos (n) | [repo-a, repo-b] (2) — [certain / inferred] |

## Scores

| | |
|---|---|
| User value | Low / Medium / High ([must-be / performance / delighter]) |
| Complexity | Low / Medium / High |
| Importance | Low / Medium / High |
| **ROI** | **Low / Medium / High** |
| Pickup | Yes / No |

**ROI note:** [one sentence tying value to effort]

## Gaps
- [missing repro, AC, owner, design, etc. — or "None"]

## Suggested next step
[Pick up now / get a testable done-when / spike / defer — one line]
```

## Output template — early exit

```markdown
# Triage: [IDENTIFIER or "unreachable"]

**Link:** [url or —]
**Verdict:** Skip — [unreachable | already done]

**Reason:** [one sentence]

**Status seen:** [status or error]
```
