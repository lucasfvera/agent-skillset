# bmo-respond-pr-review — reference

## Parse owner/repo/number from URL

```bash
# https://github.com/roxom-markets/roxtopia/pull/833
OWNER=roxom-markets REPO=roxtopia NUMBER=833
```

Or:

```bash
gh pr view 833 --json number,repository --jq '{number, owner: .repository.owner.login, repo: .repository.name}'
```

## List unresolved threads (compact)

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
          comments(first: 1) {
            nodes { databaseId author { login } body }
          }
        }
      }
    }
  }
}' -f owner="$OWNER" -f repo="$REPO" -F number="$NUMBER" \
  --jq '.data.repository.pullRequest.reviewThreads.nodes[]
    | select(.isResolved == false)
    | {
        threadId: .id,
        path: .path,
        line: .line,
        commentId: .comments.nodes[0].databaseId,
        author: .comments.nodes[0].author.login,
        preview: .comments.nodes[0].body[0:120]
      }'
```

## Reply + react (one thread)

```bash
COMMENT_ID=3483609348
SIG=$'\n\n:robot: BMO reviewed :robot:'

gh api "repos/${OWNER}/${REPO}/pulls/${NUMBER}/comments" \
  -F "in_reply_to=${COMMENT_ID}" \
  -f "body=Valid. Removed the redundant branch.${SIG}"

gh api "repos/${OWNER}/${REPO}/pulls/comments/${COMMENT_ID}/reactions" \
  -f content='+1'
```

## Batch resolve threads

```bash
gh api graphql -f query='
mutation {
  t1: resolveReviewThread(input: { threadId: "PRRT_kwDOQ59d5s6MnQc_" }) { thread { isResolved } }
  t2: resolveReviewThread(input: { threadId: "PRRT_kwDOQ59d5s6MnRiB" }) { thread { isResolved } }
}'
```

## Reaction content values

Common GitHub reaction `content` values: `+1`, `-1`, `laugh`, `confused`, `heart`, `hooray`, `rocket`, `eyes`.

Default for "handled": `+1`.

## Signature

Fixed line for all thread replies and the summary comment:

```text
:robot: BMO reviewed :robot:
```
