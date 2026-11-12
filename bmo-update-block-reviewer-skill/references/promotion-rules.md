# Promotion rules — `ledger.md` → `bmo-block-reviewer`

## Single source of truth

- **Active rules** live in exactly **one** reviewer file based on `domain`:
  - `core` → [`bmo-block-reviewer/SKILL.md`](../../bmo-block-reviewer/SKILL.md)
  - `frontend` → [`bmo-block-reviewer/references/frontend.md`](../../bmo-block-reviewer/references/frontend.md)
  - `backend` → [`bmo-block-reviewer/references/backend.md`](../../bmo-block-reviewer/references/backend.md)
  - `database` → [`bmo-block-reviewer/references/database.md`](../../bmo-block-reviewer/references/database.md)
  - `testing` → [`bmo-block-reviewer/references/testing.md`](../../bmo-block-reviewer/references/testing.md)
- **Audit metadata & unpromoted candidates** live in [`ledger.md`](../ledger.md). Reviewers never read `ledger.md`, and rules are never duplicated across multiple reviewer files.

## Promotion bar by tier

Every promoted rule must be **durable** (applies across repos/features), **actionable** (verifiable from a diff and sibling file), and **net-new** (not already covered in the target domain file).

| Tier | When to promote | Where it lands |
|------|-----------------|----------------|
| **`tier: issue`** (strict correctness, contract, security, perf, false/flaky test) | **1+ PR source** (promote immediately on first qualifying capture) | `## 1. Strict issues ([issue])` in `references/<domain>.md` (or `## Core — Strict issues ([issue])` in `SKILL.md`) |
| **`tier: style`** (structure, conventions, layout, readability, test ergonomics) | **2+ distinct PR sources** (or explicit user instruction in chat) | **1 source:** add to `## Candidates` in [`ledger.md`](../ledger.md) only.<br>**2+ sources:** move to `## Active promoted rules` in `ledger.md` and append to `## 2. Style & conventions ([style])` in `references/<domain>.md` (or `## Core — Style & conventions ([style])` in `SKILL.md`) |

## Bullet format in reviewer files

Append one line under the matching section:

```markdown
- **[<id>]** <Positive-target imperative>; <one-clause why or guardrail>.
```
