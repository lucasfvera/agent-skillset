---
name: bmo-pr
description: Opens or updates GitHub pull requests with conventional titles and a full PR body (repo template or default sections). Use when the user says /pr, asks to open a PR, update PR description after new commits, or target a base branch (e.g. main) with gh.
disable-model-invocation: true
---

# Pull requests (GitHub)

## Goal

Produce a **conventional-commit-style title** and a **complete PR body**, then either **create** a PR or **refresh** an existing one. Prefer **`gh`**; if it is missing or unauthenticated, write the same content to a markdown file and tell the user how to open the PR manually.

## Before you start

1. **Confirm branch and base** (default base: `main` if the user did not specify).
2. **`git fetch origin <base> <head>`** so `origin/<base>` and the PR branch ref are current.
3. **Inspect commits** the PR will include:

   ```bash
   git log origin/<base>..HEAD --oneline
   ```

4. **Check for an open PR** on the same head/base (avoid duplicates):

   ```bash
   gh pr list --head <branch> --base <base> --state open
   ```

5. **Push if needed**: if `HEAD` is not on the remote branch, `git push -u origin <branch>` (or the user’s equivalent). If push is **rejected (non-fast-forward)**, stop and explain: local and remote diverged—user should reconcile (merge/rebase/`--force-with-lease` only when appropriate). Do not silently force-push.

6. **Rebase onto base** is optional: only if the user wants a linear history and you can resolve conflicts quickly; otherwise open/update the PR and let GitHub show mergeability.

## Title (`<type>: <subject>`)

- **One dominant commit**: reuse that commit’s type and a tightened subject if it still fits.
- **Multiple commits**: one **summary** line covering the main outcome; do not paste the entire log into the title.
- **`<type>`**: `feat`, `fix`, `chore`, `refactor`, `docs`, `style`, `test`, `perf`, `build`, `ci`, `revert`, `security`.
- **`<subject>`**: imperative, present tense, **capital first letter**, **no trailing period**, **≤ ~72 chars** (GitHub truncates long titles).

## Body

1. If **`.github/pull_request_template.md`** exists, **read it** and fill every section the template asks for (delete placeholder instruction lines where appropriate).
2. Otherwise use this **default skeleton**:

   ```markdown
   # Description
   [What shipped: product/technical outcome. For large branches, one umbrella paragraph plus a short bullet list grouped by theme or by recent follow-up commits.]

   # Context
   [Review risks, contracts, data/ingress paths, follow-ups, anything non-obvious from the diff.]

   # Screenshots
   [N/A for backend-only unless the user attached UI—say N/A briefly.]

   ## How to test
   [Numbered steps: checkout, env, migrate, commands, expected result. Prefer repo README/package.json scripts when unsure.]
   ```

3. **Tone**: professional release notes—**no** “Made with …” / tool marketing footers unless the user explicitly wants them.

4. **After new commits land on an existing PR**: **pushing updates the diff automatically**; still **edit the body** if behavior or review focus changed—add a **“Updates since open”** (or similar) subsection with bullets derived from `git log origin/<base>..HEAD` (recent commits first).

## Create a new PR

```bash
gh pr create --base <base> --head <branch> \
  --title "<type>: <Subject>" \
  --assignee @me \
  --body-file <path>
```

Use **`--body-file`** for multi-line bodies (write a temp file, pass it, then **delete** the temp file unless the user asked to keep it). If `--body-file` is awkward, `-F` / heredoc is fine.

Reply with the **canonical PR URL** from `gh` output.

## Update an existing PR

1. Resolve the PR number: from `gh pr list` or the user’s link.
2. If only the description is stale: **`gh pr edit <n> --body-file <path>`** (and **`--title`** if the scope changed a lot).
3. Re-check **assignees**; if none, **`gh pr edit <n> --add-assignee @me`**.

## If `gh` is unavailable or not logged in

1. Tell the user to install or run **`gh auth login`**.
2. Write **`pr-draft.md`** (or `PR-<branch>.md`) in the repo root with **title, base, head, full body, and** suggested URL shape `https://github.com/<org>/<repo>/compare/<base>...<branch>?expand=1` **only if** org/repo are known from `git remote`.

## Assignee

Default **assign the author**: **`--assignee @me`** on create; on edit use **`--add-assignee @me`** if missing.

## Quick checklist

- [ ] Fetched; log from `origin/<base>..HEAD` reviewed
- [ ] No duplicate open PR for same head/base (unless user asked to replace)
- [ ] Title conventional; body filled from template or default sections
- [ ] How-to-test grounded in this repo
- [ ] `gh pr create` or `gh pr edit` succeeded **or** fallback markdown written
