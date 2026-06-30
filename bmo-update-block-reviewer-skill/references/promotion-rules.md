# Promotion rules — catalog → bmo-block-reviewer

## Default

**Do not promote.** New learnings stay in [learnings/catalog.md](../learnings/catalog.md). The block reviewer reads the catalog via its **Accumulated learnings** pointer.

## Promote only when all apply

1. **Gap:** `bmo-block-reviewer/SKILL.md` has no bullet that already states the rule (same intent, even if different words).
2. **Durable:** The rule applies across repos and feature areas, not one file or one PR.
3. **Actionable:** A reviewer can check it on a diff without product context.
4. **High signal:** The feedback was **Valid**, encodes a repeated dismissal pattern, or the same abstract rule appears in **2+ session captures** or **2+ `sources`** in the catalog.

## Do not promote

- Rules already covered in block-reviewer (mark catalog entry `promoted: true` with note "already in block-reviewer").
- Thread-specific instructions.
- Style nits the block reviewer explicitly says not to flood on.
- Learnings with only one source unless the user asks to promote in chat.

## How to promote

1. Add **one bullet** under the best-matching section in `bmo-block-reviewer/SKILL.md`:
   - `What to look for`
   - `When reviewing tests`
   - `What not to do`
2. Keep the bullet under one line when possible.
3. Set `promoted: true` on the catalog entry.
4. Do **not** remove the catalog entry. The catalog remains the audit trail.

## First-time setup

On the first promotion (or first run if the pointer is missing), add to `bmo-block-reviewer/SKILL.md` before `## Output`:

```markdown
## Accumulated learnings

Team-specific rules distilled from PR review live in
[`bmo-update-block-reviewer-skill/learnings/catalog.md`](../bmo-update-block-reviewer-skill/learnings/catalog.md).
Apply them when they strengthen or specialize the rules above.
```

## Batch limit

Promote at most **three** new bullets per session. Queue the rest for a later run or leave catalog-only.
