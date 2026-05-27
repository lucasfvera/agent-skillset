---
name: bmo-merge-conflicts
description: Analyzes git merge conflicts during rebase (suggestions only by default). HEAD is upstream/main; incoming is replayed commits. Produces per-file, per-conflict guidance; favors main business logic while preserving notification/Hermod changes. Use when the user has rebase conflicts or conflict markers. Only edits files when the user explicitly asks to resolve or fix conflicts.
disable-model-invocation: true
---

# BMO Merge Conflicts

## Mode (mandatory)

**Default: suggestions only.** Do not edit files, stage, or run `git add` / `git rebase --continue` unless the user explicitly asks to resolve.

| Mode | User intent (examples) | Agent behavior |
|------|------------------------|----------------|
| **Analyze** (default) | "what are the conflicts", "how should I resolve", "suggestions", attaching this skill without a resolve ask | Read conflicts, explain, recommend picks — **no file changes** |
| **Resolve** | "resolve the conflicts", "fix the conflicts", "apply your suggestions", "go ahead and merge" | Edit conflicted files, fix tests, `git add`, continue rebase **only if user also asked to continue** |

If ambiguous, stay in **Analyze** and ask: "Want me to apply these resolutions?"

## Rebase semantics (always assume rebase)

| Marker | Meaning |
|--------|---------|
| `<<<<<<< HEAD` | **Upstream** — the branch you are rebasing onto (usually `main`) |
| `>>>>>>> <commit>` | **Incoming** — your commit being replayed onto that base |

Do **not** treat HEAD as "my branch" during rebase. That inversion causes wrong picks.

## Default resolution policy

Unless the user states otherwise:

1. **Business logic** (service rules, API shapes, idempotency, email side-effects, lifecycle gates) → prefer **HEAD (main)**.
2. **Notification / Hermod plumbing** (payload validation, `buildCreateNotificationQueuePayload`, `parse*NotificationPayload`, queue wire serialization) → keep from **incoming** when it does not replace main behavior.
3. **Imports** → often **both sides** (e.g. `type UUID` from main + `parseLoanUpdateNotificationPayload` from incoming).
4. **Tests** → match the **resolved production API**, not the pre-rebase incoming test shape.

In **Analyze** mode, describe test updates in suggestions; do not edit test files.

## Discovery workflow

```bash
git status
git diff --name-only --diff-filter=U
rg -l '^<<<<<<< ' <repo-root>
```

Note staged files without markers — they may already be resolved or need test alignment after production code is fixed.

## Analysis output format

Use **one block per conflicted file**, **one sub-block per conflict** (`<<<<<<<` … `>>>>>>>`):

```markdown
## `path/to/file.ts`

### Conflict N — [short label, e.g. imports / API signature / call site]

| Side | Content |
|------|---------|
| **HEAD (main)** | … |
| **Incoming (yours)** | … |

**Why:** …

**Suggestion:** …
```

End with a **Resolution cheat sheet** table (Area → Prefer) when multiple files share the same policy.

## Resolution patterns

### Interface / call-site drift

- Main often uses **positional** args; feature branches sometimes refactor to **params objects**.
- Pick **one** public shape (usually HEAD). Update all call sites (`LoansService`, engines, tests) to match.
- Reject **duplicate** interface methods from incoming (e.g. second `publishX` with a different signature).

### Implementation merge

- Keep HEAD: idempotency (`markIfFresh`), email side-effects, status gates (`REPAID` before `publishLoanClosed`).
- Graft small incoming helpers onto HEAD when they improve wire correctness (e.g. `formatLoanClosedAt(loan)` using `closedAt ?? updatedAt`).
- Keep incoming validation inside `publishToUser` / Hermod paths already merged below conflicts.

### Imports

Merge both when each side is used in the resolved file:

```ts
type UUID,
parseLoanUpdateNotificationPayload,
buildCreateNotificationQueuePayload,
```

### Tests

**Suggest** (Analyze) or **apply** (Resolve):

- Assert **HEAD call style** (positional args, `IBorrowMoreEvent` rows, etc.).
- Add full publisher deps when main added email/pg paths: `pg`, `mailingService`, `userRepository`.
- Run: `yarn workspace <app> test <test-file>` — only in **Resolve** mode (or when user asked to run tests).

### Hidden damage (no conflict markers)

Flag **duplicate blocks** from both branches (e.g. two `publishBorrowMore` calls). In Analyze: call out which block to delete. In Resolve: remove the stale incoming call; keep main's.

## Post-resolution checklist (Resolve mode only)

- [ ] No `<<<<<<<` / `=======` / `>>>>>>>` left
- [ ] No duplicate methods in returned objects (last key wins in JS)
- [ ] Call sites match interface (grep `publishLoanClosed`, etc.)
- [ ] Tests updated to resolved API
- [ ] `git add` conflicted files → `git rebase --continue` only if user asked to continue the rebase

## Commands reference

| Goal | Command |
|------|---------|
| Unmerged files | `git diff --name-only --diff-filter=U` |
| Find markers | `rg -n '^<<<<<<< ' path/` |
| Compare sides | `git show HEAD:path` and `git show <incoming-commit>:path` |
| Abort rebase | `git rebase --abort` |

## Example cheat sheet (loan / Hermod context)

| Area | Prefer |
|------|--------|
| When to emit terminal events | HEAD |
| Publisher API shape | HEAD (positional / `IBorrowMoreEvent`) |
| Hermod validate + queue payload | Incoming |
| `closedAt` on wire | Incoming helper on HEAD impl |
| Unit test call expectations | Match HEAD after resolve |

Adapt labels to the repo; the policy table is the portable part.
