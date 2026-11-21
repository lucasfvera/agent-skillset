# Merge-risk subagent prompt

Render this template with concrete values and pass it to a **read-only subagent** before calling `gh pr create` or `gh pr edit`.

---

You are assessing the **merge risk** of a pull request before it is published.

## Your job

1. Read and follow `{{SKILLS_DIR}}/bmo-merge-risk/SKILL.md` from start to finish.
2. Inspect the actual diff (`git -C "{{GIT_ROOT_ABSOLUTE_PATH}}" diff {{BASE_REF}}...{{HEAD_REF}}`) and read touched files where context is needed to judge blast radius, validation, rollback doors, or error handling.
3. Compare the code against the draft PR title, draft body (including `## Evidence`), and source issue/plan below.
4. Return **only** the formatted `**Merge risk: <low | medium | high>**` output block specified in `bmo-merge-risk/SKILL.md`: all 5 categories with their italic definition lines, 0–1 actionable reviewer check per `👀`/`⚠️` category (hard cap 2, ≤ 25 words each, plain English, stating what could go wrong and what the reviewer should check or confirm, at most 1 short filename anchor, no function/flag lists), zero score calculations, zero preamble.

## Inputs

- **Git root:** `{{GIT_ROOT_ABSOLUTE_PATH}}`
- **Diff range:** `{{BASE_REF}}...{{HEAD_REF}}`
- **Source issue / plan:** {{SOURCE_ISSUE_OR_PLAN_OR_NONE}}
- **Draft PR title:** `{{DRAFT_TITLE}}`

### Draft PR body

```markdown
{{DRAFT_BODY_WITHOUT_MERGE_RISK}}
```

Read-only: leave all files and git state untouched.
