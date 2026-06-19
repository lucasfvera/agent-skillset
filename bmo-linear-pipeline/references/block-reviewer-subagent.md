# Block reviewer subagent prompt

Copy this template into the `Task` tool `prompt` field. Replace placeholders.

---

You are reviewing **one delivery block** from a `bmo-step-deliver` review digest.

## Your job

1. Read and follow the skill at `~/.cursor/skills/bmo-block-reviewer/SKILL.md`.
2. Inspect the **actual git diff** for every file listed in this block (read files / `git diff` — do not rely on handoff text alone).
3. Return findings in the **bmo-block-reviewer output shape** (findings first, short verdict).

## Context

- **Linear issue:** {{ISSUE_ID}}
- **Plan unit:** {{UNIT_ID}} (e.g. U1)
- **Block:** {{BLOCK_NAME}} (e.g. Block A — Schema / types)

## Block handoff (from review digest)

{{PASTE_FULL_BLOCK_SECTION_HERE}}

## Files to inspect

{{LIST_ABSOLUTE_PATHS_ONE_PER_LINE}}

## Git root

{{GIT_ROOT_ABSOLUTE_PATH}}

## Output requirements

- Findings-first bullets; each finding: what is wrong, why it matters here, what to change.
- **Verdict:** one short line (e.g. "Good to ship", "Fix typing before commit").
- If diff unavailable, say review is limited and list what you could not verify.

Do not implement fixes. Review only.
