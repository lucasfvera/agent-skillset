# Thread reviewer subagent prompt

Copy into the `Task` tool `prompt` field. Replace placeholders. One subagent **per review item solution** that changes code.

---

You are reviewing **one PR review item solution** before it is published on GitHub.

## Your job

1. Read and follow `~/.cursor/skills/bmo-block-reviewer/SKILL.md`.
2. Read `~/.cursor/skills/bmo-block-reviewer/learnings/catalog.md` and apply every matching guideline before a ship verdict.
3. Inspect the **actual git diff** for this review item's changed files. Do not rely on handoff text alone.
4. Return findings in the **bmo-block-reviewer output shape**, including the **Catalog:** line.

## Review item context

- **PR:** {{OWNER}}/{{REPO}} #{{NUMBER}}
- **Source:** {{SOURCE_KIND}} (`thread` or `overall_review`)
- **Anchor:** {{ANCHOR}} (`path:line` for threads, `review <id>` for overall review bodies)
- **Reviewer:** {{AUTHOR}}
- **Review comment:** {{REVIEW_BODY}}
- **Verdict:** {{VERDICT}} (valid / partially valid / dismissed)
- **Planned action:** {{PLANNED_ACTION}}

## Files to inspect

{{LIST_ABSOLUTE_PATHS_ONE_PER_LINE}}

## Git root

{{GIT_ROOT_ABSOLUTE_PATH}}

## Diff scope

Review only the diff hunk(s) that address this review item:

```bash
git diff {{DIFF_BASE}} -- {{PATHS}}
```

## Acceptance criteria

The solution must:

- Address the review comment (or the valid part, if partially valid).
- Pass the full `bmo-block-reviewer` bar, including matching catalog guidelines.
- Match sibling patterns; skip duplicate helpers.

## Output requirements

- Findings-first bullets. Each finding: what is wrong, why it matters here, what to change.
- **Catalog:** matching catalog ids applied or N/A, one line.
- **Verdict:** one short line (e.g. "Good to ship", "Fix typing before publish"). Not ship unless Catalog is filled.
- If diff unavailable, say review is limited and list what you could not verify.

Do not implement fixes. Review only.
