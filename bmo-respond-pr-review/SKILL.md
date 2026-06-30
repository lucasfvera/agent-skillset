---
name: bmo-respond-pr-review
description: >-
  Triage human PR review comments, implement fixes, run one bmo-block-reviewer
  subagent per code-changing thread before publish, then reply on each thread
  with a BMO signature and reaction, resolve threads, and post a summary comment.
  Use when the user asks to address PR review feedback, respond to review
  comments, resolve PR threads, or invokes /bmo-respond-pr-review with a PR URL
  or number.
disable-model-invocation: true
argument-hint: "[pr url or number]"
---

# Respond to PR review (BMO)

Close the loop on human PR review. Triage threads, implement solutions, **block-review each code solution before push**, then publish replies on GitHub.

**Input:** `$ARGUMENTS` is a PR URL or number. If missing, infer from the current branch (`gh pr view`) or ask once.

**Prerequisite:** `gh` authenticated with permission to comment, react, and resolve review threads on the repo.

**Related skills:** [`bmo-block-reviewer`](../bmo-block-reviewer/SKILL.md) (mandatory pre-publish review per code solution); [`bmo-commit`](../bmo-commit/SKILL.md) for scoped commit messages; [`bmo-update-block-reviewer-skill`](../bmo-update-block-reviewer-skill/SKILL.md) (session feedback capture); Cursor **babysit** for broader merge readiness.

---

## Order of operations

Execute **in order**. Do not commit, push, or post GitHub replies until block review passes for every code-changing thread.

```
1. Resolve PR context
2. Fetch unresolved review threads
3. Triage each thread
4. Implement solutions (local — not pushed yet)
5. Parallel block review — one subagent per code-changing thread
6. Apply review fixes, verify, commit, push
7. Reply on each thread (signature + reaction)
8. Resolve handled threads
9. Post summary PR comment
10. Capture session feedback to inbox (pending)
11. Report back in chat
```

**Data shape (per thread solution):**

| Field | Use |
|-------|-----|
| `threadId` | Resolve in step 8 |
| `commentDatabaseId` | Reply + reaction in step 7 |
| `path`, `line` | Triage anchor + subagent handoff |
| `verdict` | valid / partially valid / dismissed |
| `changedFiles[]` | Subagent diff scope |
| `needsBlockReview` | `true` when verdict is valid or partially valid; `false` when dismissed (explanation only) |

---

## 1. Resolve PR context

```bash
gh pr view <n> --json number,url,headRefName,baseRefName,headRepository
```

Record **owner**, **repo**, **PR number**, **git root**, **branch checkout path**.

---

## 2. Fetch unresolved review threads

```bash
gh api graphql -f query='
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          path
          line
          comments(first: 10) {
            nodes {
              id
              databaseId
              body
              author { login }
            }
          }
        }
      }
    }
  }
}' -f owner=OWNER -f repo=REPO -F number=NUMBER \
  --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)'
```

Filter to **human review threads** unless the user wants bot threads (Bugbot). For Bugbot, apply skeptical triage from **babysit**.

Before posting replies, check for a **pending review** on the PR (blocks inline replies for the same user):

```bash
gh api repos/OWNER/REPO/pulls/NUMBER/reviews --jq '.[] | select(.state == "PENDING")'
```

Submit or discard pending reviews before step 7.

---

## 3. Triage each thread

| Verdict | Meaning | Block review? | Action |
|---------|---------|---------------|--------|
| **Valid** | Correct; should change | Yes | Implement in step 4 |
| **Partially valid** | Direction right, detail off | Yes | Fix valid part; explain rest in reply |
| **Dismissed** | Wrong, out of scope, or nitpick | No | Draft explanation only |

Use [`bmo-block-reviewer`](../bmo-block-reviewer/SKILL.md) as the initial quality bar during triage. Build a triage table (file:line, verdict, planned action) before editing.

---

## 4. Implement solutions (local)

1. Apply fixes for **Valid** and **Partially valid** threads only.
2. Keep changes **unpushed** until step 6 completes.
3. Record per thread which files changed (`git diff --name-only` per solution scope when possible).

If every thread is **Dismissed**, skip to step 7 (draft replies only).

---

## 5. Parallel block review (mandatory before publish)

For **each thread** with `needsBlockReview: true`:

1. **Spawn one subagent** via `Task`. Wait for **all** to finish before step 6.
2. Use the prompt template at [references/thread-reviewer-subagent.md](references/thread-reviewer-subagent.md).
3. Pass each subagent:
   - Review comment body, verdict, planned action
   - Absolute paths of changed files for that thread
   - Git root and diff base (`HEAD` before commit, or staged diff)
   - One sibling file to compare against when pattern drift is likely

**Subagent rules:** read `bmo-block-reviewer/SKILL.md`; review only that thread's diff; do not implement fixes.

**Parent triage after all subagents return:**

| Finding | Action |
|---------|--------|
| **Real** | Fix before commit |
| **Style** | Fix only when a clear repo/sibling pattern or prior user feedback applies |
| **Deferred / nitpick** | Note in reply or skip; do not churn |

Do **not** push or post GitHub replies until real findings are fixed or explicitly dismissed with a one-line reason.

**Explanation-only threads** (dismissed): no subagent. Parent validates the reply draft against `bmo-block-reviewer` bar inline.

---

## 6. Apply review fixes, verify, commit, push

1. Fix **real** block-review findings.
2. Run the **narrowest verification** per changed area (same test file/command as the PR).
3. Commit and push to the PR branch.

Record **fix commit SHA** for the summary comment.

---

## 7. Reply on each thread

### BMO signature

Every inline reply and the summary comment end with:

```text

:robot: BMO reviewed :robot:
```

### Reply body

- Lead with verdict (`Valid.`, `Partially valid.`, `Keeping as-is.`).
- One or two sentences on what changed or why not.
- Append the signature.

### Post reply (REST — preferred)

```bash
SIG=$'\n\n:robot: BMO reviewed :robot:'

gh api repos/OWNER/REPO/pulls/NUMBER/comments \
  -F in_reply_to=COMMENT_DATABASE_ID \
  -f body="Your reply text here.${SIG}"
```

### Reaction

```bash
gh api repos/OWNER/REPO/pulls/comments/COMMENT_DATABASE_ID/reactions \
  -f content='+1'
```

### API fallbacks

1. REST `pulls/{pr}/comments` with `-F in_reply_to=<databaseId>`
2. REST `pulls/comments/{databaseId}/replies`
3. GraphQL `addPullRequestReviewComment` (PRRC_… node id)

If GraphQL returns `FORBIDDEN`, stay on REST.

---

## 8. Resolve handled threads

```bash
gh api graphql -f query='
mutation($threadId: ID!) {
  resolveReviewThread(input: { threadId: $threadId }) {
    thread { isResolved }
  }
}' -f threadId=PRRT_...
```

Resolve after reply when the thread is fully addressed.

---

## 9. Summary PR comment

```bash
gh pr comment NUMBER --body "$(cat <<'EOF'
## Review follow-up — all threads addressed

Shipped in `<sha>`:

| Thread | Verdict | Action |
|--------|---------|--------|
| `path:line` — topic | Valid | … |

Block review: one pass per code-changing thread before push.

Tests: …

Replied on each thread with 👍.

:robot: BMO reviewed :robot:
EOF
)"
```

---

## 10. Capture session feedback

Write one file to the updater skill inbox so feedback can accumulate across sessions.

**Path:** `../bmo-update-block-reviewer-skill/inbox/pending/{id}.md`

**Format:** [bmo-update-block-reviewer-skill/references/session-capture.md](../bmo-update-block-reviewer-skill/references/session-capture.md)

**Required content per handled thread:**

- `threadId`, `path`, `line`, `verdict`, reviewer login
- Verbatim reviewer comment
- Resolution text (BMO reply without signature)
- `changedFiles` when applicable

**Frontmatter:** `status: pending`, `actionedAt: null`, `pr`, `prUrl`, `fixCommitSha`, `threadCount`, `capturedAt` (UTC).

Do not abstract to guidelines here. Do not mark actioned.

---

## 11. Chat report

- PR URL
- Threads handled (fixed / explained / dismissed)
- Block-review summary (real fixes vs skipped findings)
- Link to summary comment
- Inbox capture path written (`inbox/pending/{id}.md`)

Run [`bmo-update-block-reviewer-skill`](../bmo-update-block-reviewer-skill/SKILL.md) in a **later session** to distill pending captures into the learnings catalog.

---

## Checklist

```
- [ ] Unresolved threads fetched
- [ ] Each thread triaged
- [ ] Solutions implemented locally
- [ ] One bmo-block-reviewer subagent per code-changing thread (all finished)
- [ ] Real block-review findings fixed
- [ ] Verification passed, committed, pushed
- [ ] Inline reply + reaction on each thread
- [ ] `:robot: BMO reviewed :robot:` on every reply and summary
- [ ] Threads resolved
- [ ] Summary PR comment posted
- [ ] Session capture written to `inbox/pending/`
```

---

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| Push before block review | Steps 4–6 gate publish |
| One subagent for all threads | One subagent **per code solution** |
| `in_reply_to` as string | Use `-F in_reply_to=3483609348` |
| Pending PR review blocks replies | Submit/discard before step 7 |
| GraphQL comment mutation forbidden | REST endpoints in step 7 |
| Reacting on your own reply | React on reviewer's `databaseId` |

---

## Additional reference

- Command templates: [reference.md](reference.md)
- Subagent prompt: [references/thread-reviewer-subagent.md](references/thread-reviewer-subagent.md)
- Session capture format: [bmo-update-block-reviewer-skill/references/session-capture.md](../bmo-update-block-reviewer-skill/references/session-capture.md)
