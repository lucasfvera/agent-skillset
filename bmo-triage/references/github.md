# GitHub Issues adapter (`bmo-triage`)

Load this file only when `$ARGUMENTS` is a GitHub issue URL (`https://github.com/<owner>/<repo>/issues/<n>`), `owner/repo#<n>`, or `#<n>` inside a git checkout.

## Fetch steps

1. **Identifier:** Normalize to `owner/repo#<n>` when `owner/repo` is given or resolvable from the current git remote (`gh repo view --json nameWithOwner -q .nameWithOwner`), else `#<n>`.
2. **Fetch via `gh`:**
   ```bash
   gh issue view <n> -R <owner>/<repo> \
     --json number,title,body,state,stateReason,labels,comments,milestone,url,closedAt
   ```
   (Omit `-R <owner>/<repo>` when running inside the target repository checkout.)
   - If `gh` is missing or unauthenticated (`gh auth status` fails), ask the user once to authenticate or paste title + description (or record `Skip — unreachable` in Step 2).
3. **Fields to map:**
   - **Status & terminal check:** `state == "CLOSED"` (`stateReason` `COMPLETED`, `NOT_PLANNED`, or `DUPLICATE`) is terminal (`Skip — already done`).
   - **Type:** infer from labels (`bug`, `enhancement`, `feature`, `chore`, `documentation`) and body template headings.
   - **Priority / Importance:** infer from priority/severity labels (`P0`/`P1`, `priority: critical/high`, `urgent`, `blocker`, `incident`) and `milestone.dueOn`.
   - **Linked PRs:** if ambiguous whether work is already underway, check `gh pr list --search "<n>" --state all --json number,state,url`.

**Done:** GitHub issue fields are mapped for `bmo-triage` Step 2, or fetch failure is recorded.
