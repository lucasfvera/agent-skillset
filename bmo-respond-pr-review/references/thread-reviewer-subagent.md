# Thread reviewer subagent prompt

Render this template with concrete values and pass it to a read-only subagent. One subagent **per review item solution** that changes code.

---

You are reviewing **one PR review item solution** before it is published on GitHub.

## Your job

1. Read and follow `{{SKILLS_DIR}}/bmo-block-reviewer/SKILL.md`.
2. Load only the domain catalog files under `{{SKILLS_DIR}}/bmo-block-reviewer/references/` (`frontend.md`, `backend.md`, `database.md`, `testing.md`) triggered by this review item's changed files.
3. Inspect the **actual git diff** for this review item's changed files. Use handoff text as context only.
4. Run **Pass 1 (`[issue]`)** before **Pass 2 (`[style]`)** and return findings in the `bmo-block-reviewer` output shape.

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
- Pass both **Pass 1 (`[issue]`)** and **Pass 2 (`[style]`)** in `bmo-block-reviewer` and the loaded domain catalogs.
- Match sibling patterns without adding duplicate helpers.

## Output requirements

- Findings-first bullets ordered **`[issue]` before `[style]`** (`- [issue] [<rule-id>] ...`, `- [style] [<rule-id>] ...`); each states what is wrong, why it matters here, and what to change.
- **Catalog:** `core[, frontend, backend, database, testing] — <triggered rule-ids or none>`, one line.
- **Verdict:** `<ship | fix style before ship | block — fix issues>`. Not `ship` unless **Catalog** is filled and zero `[issue]` or actionable `[style]` findings remain.
- If the diff is unavailable, state that the review is limited and list what could not be verified.

Review only; leave file edits to the parent orchestrator.
