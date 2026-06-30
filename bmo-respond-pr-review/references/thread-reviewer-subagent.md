# Thread reviewer subagent prompt

Copy into the `Task` tool `prompt` field. Replace placeholders. One subagent **per thread solution** that changes code.

---

You are reviewing **one PR review thread solution** before it is published on GitHub.

## Your job

1. Read and follow `~/.cursor/skills/bmo-block-reviewer/SKILL.md`.
2. Inspect the **actual git diff** for this thread's changed files. Do not rely on handoff text alone.
3. Return findings in the **bmo-block-reviewer output shape** (findings first, short verdict).

## Thread context

- **PR:** {{OWNER}}/{{REPO}} #{{NUMBER}}
- **Thread:** `{{PATH}}:{{LINE}}`
- **Reviewer:** {{AUTHOR}}
- **Review comment:** {{REVIEW_BODY}}
- **Verdict:** {{VERDICT}} (valid / partially valid / dismissed)
- **Planned action:** {{PLANNED_ACTION}}

## Files to inspect

{{LIST_ABSOLUTE_PATHS_ONE_PER_LINE}}

## Git root

{{GIT_ROOT_ABSOLUTE_PATH}}

## Diff scope

Review only the diff hunk(s) that address this thread:

```bash
git diff {{DIFF_BASE}} -- {{PATHS}}
```

## Acceptance criteria

The solution must:

- Address the review comment (or the valid part, if partially valid).
- Match repo conventions (typing, tests, no `any`, no weak equality unless justified).
- Not introduce duplicate helpers or pattern drift vs sibling files.

## Output requirements

- Findings-first bullets. Each finding: what is wrong, why it matters here, what to change.
- **Verdict:** one short line (e.g. "Good to ship", "Fix typing before publish").
- If diff unavailable, say review is limited and list what you could not verify.

Do not implement fixes. Review only.
