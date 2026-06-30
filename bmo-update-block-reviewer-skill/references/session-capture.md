# Session capture — respond-pr-review → inbox

## Where to write

```
bmo-update-block-reviewer-skill/inbox/pending/{id}.md
```

Path from respond-pr-review skill:

```
../bmo-update-block-reviewer-skill/inbox/pending/
```

## File id

`{ISO8601 compact}-{owner}-{repo}-pr{number}`

Example: `20260629T143022Z-roxom-markets-roxtopia-pr833`

Use UTC. If the same PR is captured twice in one second, append `-2`, `-3`, etc.

## Frontmatter (required)

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | Matches filename without `.md` |
| `status` | `pending` | Always `pending` on capture |
| `capturedAt` | ISO8601 | UTC |
| `actionedAt` | `null` | Set by updater skill |
| `pr` | string | `owner/repo#number` |
| `prUrl` | string | Full GitHub PR URL |
| `fixCommitSha` | string | Commit from step 6 |
| `threadCount` | number | Handled threads in this session |

## Per-thread body sections

One `## Thread {n}` per handled thread. Include:

- `threadId`, `path`, `line`, `verdict`, `reviewer`, `changedFiles`
- **Reviewer comment** — verbatim (inbox is raw capture)
- **Resolution** — BMO reply without signature

## Verdicts

| Triage verdict | `verdict` value |
|----------------|-----------------|
| Valid | `valid` |
| Partially valid | `partially_valid` |
| Dismissed / Keeping as-is | `dismissed` |

## What to capture

- Every thread that received a reply in step 7.
- Block-review findings that changed the fix (note in resolution if relevant).
- Do **not** capture bot-only threads unless the user opted in.

## What not to do

- Do not abstract to guidelines here. That is the updater skill's job.
- Do not set `actionedAt` or move files. Only the updater touches `actioned/`.
- Do not fetch GitHub again if the session already has thread text.

## Template

Copy structure from [templates/session-capture.md](../templates/session-capture.md).
