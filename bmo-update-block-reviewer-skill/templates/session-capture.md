---
id: {ISO8601}-{owner}-{repo}-pr{number}
status: pending
capturedAt: {ISO8601}
actionedAt: null
pr: {owner}/{repo}#{number}
prUrl: {url}
fixCommitSha: {sha}
threadCount: {n}
---

# Session capture — {owner}/{repo}#{number}

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread {n}

| Field | Value |
|-------|-------|
| **threadId** | {PRRT_…} |
| **path** | {path} |
| **line** | {line} |
| **verdict** | {valid \| partially_valid \| dismissed} |
| **reviewer** | {login} |
| **changedFiles** | {comma-separated paths or —} |

### Reviewer comment

{verbatim reviewer comment}

### Resolution

{BMO reply body without the `:robot: BMO reviewed :robot:` signature}
