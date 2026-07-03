---
name: bmo-respond-pr-review
description: >-
  Triage human PR review comments, including inline threads and non-empty
  top-level review bodies, implement fixes, run one bmo-block-reviewer
  subagent per code-changing review item before publish, reply without duplicate
  top-level follow-up comments, resolve threads, and post a single summary /
  overall-review follow-up comment.
  Use when the user asks to address PR review feedback, respond to review
  comments, resolve PR threads, or invokes /bmo-respond-pr-review with a PR URL
  or number.
disable-model-invocation: true
argument-hint: "[pr url or number]"
---

# Respond to PR review (BMO)

Close the loop on human PR review. Triage inline threads and overall review bodies, implement solutions, **block-review each code solution before push**, then publish replies on GitHub without duplicating top-level PR comments.

**Input:** `$ARGUMENTS` is a PR URL or number. If missing, infer from the current branch (`gh pr view`) or ask once.

**Prerequisite:** `gh` authenticated with permission to comment, react, and resolve review threads on the repo.

**Related skills:** [`bmo-block-reviewer`](../bmo-block-reviewer/SKILL.md) (mandatory pre-publish review per code solution); [`bmo-commit`](../bmo-commit/SKILL.md) for scoped commit messages; [`bmo-update-block-reviewer-skill`](../bmo-update-block-reviewer-skill/SKILL.md) (session feedback capture); Cursor **babysit** for broader merge readiness.

---

## Order of operations

Execute **in order**. Do not commit, push, or post GitHub replies until block review passes for every code-changing review item.

```
1. Resolve PR context
2. Fetch unresolved review threads and non-empty overall review bodies
3. Triage each review item
4. Implement solutions (local — not pushed yet)
5. Parallel block review — one subagent per code-changing review item
6. Apply review fixes, verify, commit, push
7. Reply on each review item
8. Resolve handled threads
9. Post one summary / overall-review follow-up comment
10. Capture session feedback to inbox (pending)
11. Report back in chat
```

**Data shape (per review item):**

| Field | Use |
|-------|-----|
| `kind` | `thread` \| `overall_review` |
| `threadId` | Resolve in step 8 for inline threads; `null` for overall review bodies |
| `reviewId` | Numeric GitHub review id for a non-empty overall review body; `null` for inline threads |
| `commentDatabaseId` | Inline reply target + reaction target for threads |
| `path`, `line` | Triage anchor + subagent handoff; may be `null` for overall review bodies |
| `verdict` | valid / partially valid / dismissed |
| `replyMode` | `inline` \| `top_level_followup` |
| `changedFiles[]` | Subagent diff scope |
| `needsBlockReview` | `true` when verdict is valid or partially valid; `false` when dismissed (explanation only) |

---

## 1. Resolve PR context

```bash
gh pr view <n> --json number,url,headRefName,baseRefName,headRepository
```

Record **owner**, **repo**, **PR number**, **git root**, **branch checkout path**.

---

## 2. Fetch unresolved review threads and non-empty overall review bodies

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

Fetch non-empty top-level review bodies too:

```bash
gh api repos/OWNER/REPO/pulls/NUMBER/reviews \
  --jq '.[]
    | select(.state != "PENDING")
    | select(((.body // "") | gsub("\\s"; "")) != "")
    | {
        reviewId: .id,
        author: .user.login,
        body: .body,
        state: .state,
        submittedAt: .submitted_at
      }'
```

Treat each non-empty top-level review body as a review item even when every inline thread is already resolved.

Before posting any top-level follow-up comment, fetch existing BMO markers so reruns can skip duplicates:

```bash
ME=$(gh api user --jq .login)

gh api repos/OWNER/REPO/issues/NUMBER/comments \
  --jq '.[]
    | select(.user.login == "'"$ME"'")
    | select(
        (.body | contains("<!-- bmo-summary:"))
        or
        (.body | contains("<!-- bmo-review-followup:"))
      )
    | { id: .id, body: .body }'
```

Before posting replies, check for a **pending review** on the PR (blocks inline replies for the same user):

```bash
gh api repos/OWNER/REPO/pulls/NUMBER/reviews --jq '.[] | select(.state == "PENDING")'
```

Submit or discard pending reviews before step 7.

---

## 3. Triage each review item

| Verdict | Meaning | Block review? | Action |
|---------|---------|---------------|--------|
| **Valid** | Correct; should change | Yes | Implement in step 4 |
| **Partially valid** | Direction right, detail off | Yes | Fix valid part; explain rest in reply |
| **Dismissed** | Wrong, out of scope, or nitpick | No | Draft explanation only |

Use [`bmo-block-reviewer`](../bmo-block-reviewer/SKILL.md) as the initial quality bar during triage. Build a triage table (anchor, verdict, planned action) before editing.

For a top-level review body:

- Mark `replyMode: top_level_followup`.
- Dismiss it if an existing BMO follow-up comment already contains `<!-- bmo-review-followup:REVIEW_ID -->`.
- Dismiss it if it adds no action beyond already-triaged inline threads, but still mention that coverage in the top-level follow-up when useful.

---

## 4. Implement solutions (local)

1. Apply fixes for **Valid** and **Partially valid** review items only.
2. Keep changes **unpushed** until step 6 completes.
3. Record per review item which files changed (`git diff --name-only` per solution scope when possible).

If every review item is **Dismissed**, skip to step 7 (draft replies only).

---

## 5. Parallel block review (mandatory before publish)

For **each review item** with `needsBlockReview: true`:

1. **Spawn one subagent** via `Task`. Wait for **all** to finish before step 6.
2. Use the prompt template at [references/thread-reviewer-subagent.md](references/thread-reviewer-subagent.md).
3. Pass each subagent:
   - Review comment body, verdict, planned action
   - Absolute paths of changed files for that review item
   - Git root and diff base (`HEAD` before commit, or staged diff)
   - One sibling file to compare against when pattern drift is likely

**Subagent rules:** read `bmo-block-reviewer/SKILL.md`; review only that review item's diff; do not implement fixes.

**Parent triage after all subagents return:**

| Finding | Action |
|---------|--------|
| **Real** | Fix before commit |
| **Style** | Fix only when a clear repo/sibling pattern or prior user feedback applies |
| **Deferred / nitpick** | Note in reply or skip; do not churn |

Do **not** push or post GitHub replies until real findings are fixed or explicitly dismissed with a one-line reason.

**Explanation-only review items** (dismissed): no subagent. Parent validates the reply draft against `bmo-block-reviewer` bar inline.

---

## 6. Apply review fixes, verify, commit, push

1. Fix **real** block-review findings.
2. Run the **narrowest verification** per changed area (same test file/command as the PR).
3. Commit and push to the PR branch.

Record **fix commit SHA** for the summary comment.

---

## 7. Reply on each review item

### BMO signature

Every inline reply and the top-level follow-up comment end with:

```text

:robot: BMO reviewed :robot:
```

### Reply body

- Lead with verdict (`Valid.`, `Partially valid.`, `Keeping as-is.`).
- One or two sentences on what changed or why not.
- Append the signature.

### Inline thread reply (REST — preferred)

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

### Overall review bodies

Do **not** post a separate one-off PR comment per overall review body. Queue one short reply per handled `reviewId`, then publish all of them inside the single top-level follow-up comment in step 9.

Use a hidden marker per handled review body:

```text
<!-- bmo-review-followup:REVIEW_ID -->
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

Resolve after reply when the thread is fully addressed. Top-level review bodies have no review thread to resolve.

---

## 9. Post one summary / overall-review follow-up comment

```bash
gh pr comment NUMBER --body "$(cat <<'EOF'
<!-- bmo-summary:FIX_COMMIT_SHA -->
<!-- bmo-review-followup:REVIEW_ID -->
## Review follow-up

### Overall review REVIEW_ID
Valid. Explain the architectural split or the action taken for this review body in one or two sentences.

### Threads

Shipped in `<sha>`:

| Review item | Verdict | Action |
|-------------|---------|--------|
| `path:line` or `review REVIEW_ID` | Valid | … |

Block review: one pass per code-changing review item before push.

Tests: …

Replied on each handled thread with 👍.

:robot: BMO reviewed :robot:
EOF
)"
```

Before posting, check existing issue comments. If a prior BMO top-level comment already contains `<!-- bmo-summary:FIX_COMMIT_SHA -->` and every queued `<!-- bmo-review-followup:REVIEW_ID -->` marker, do **not** post another top-level PR comment.

---

## 10. Capture session feedback

Write one file to the updater skill inbox so feedback can accumulate across sessions.

**Path:** `../bmo-update-block-reviewer-skill/inbox/pending/{id}.md`

**Format:** [bmo-update-block-reviewer-skill/references/session-capture.md](../bmo-update-block-reviewer-skill/references/session-capture.md)

**Required content per handled review item:**

- `threadId`, `path`, `line`, `verdict`, reviewer login
- Verbatim reviewer comment
- Resolution text (BMO reply without signature)
- `changedFiles` when applicable

**Frontmatter:** `status: pending`, `actionedAt: null`, `pr`, `prUrl`, `fixCommitSha`, `threadCount`, `capturedAt` (UTC).

For overall review bodies, record:

- `threadId: review:REVIEW_ID`
- `path: —`
- `line: —`

Do not abstract to guidelines here. Do not mark actioned.

---

## 11. Chat report

- PR URL
- Threads handled (fixed / explained / dismissed)
- Overall review bodies handled (replied / dismissed as already covered)
- Block-review summary (real fixes vs skipped findings)
- Link to summary comment
- Inbox capture path written (`inbox/pending/{id}.md`)

Run [`bmo-update-block-reviewer-skill`](../bmo-update-block-reviewer-skill/SKILL.md) in a **later session** to distill pending captures into the learnings catalog.

---

## Checklist

```
- [ ] Unresolved threads fetched
- [ ] Non-empty overall review bodies fetched
- [ ] Each review item triaged
- [ ] Solutions implemented locally
- [ ] One bmo-block-reviewer subagent per code-changing review item (all finished)
- [ ] Real block-review findings fixed
- [ ] Verification passed, committed, pushed
- [ ] Inline reply + reaction on each handled thread
- [ ] Overall review bodies folded into one top-level follow-up comment
- [ ] No duplicate top-level follow-up comment posted
- [ ] `:robot: BMO reviewed :robot:` on every reply and top-level follow-up
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
| Missing the top-level review body | Fetch non-empty `pulls/{number}/reviews` bodies in step 2 |
| Posting a duplicate PR follow-up comment | Reuse step 9 markers and skip when they already exist |

---

## Additional reference

- Command templates: [reference.md](reference.md)
- Subagent prompt: [references/thread-reviewer-subagent.md](references/thread-reviewer-subagent.md)
- Session capture format: [bmo-update-block-reviewer-skill/references/session-capture.md](../bmo-update-block-reviewer-skill/references/session-capture.md)
