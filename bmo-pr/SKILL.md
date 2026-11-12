---
name: bmo-pr
description: Opens or updates GitHub pull requests with repo-aligned titles, green pre-PR checks, anti-cognitive-surrender review bodies, and release-free visual screenshots.
disable-model-invocation: true
---

# Pull requests (GitHub)

Produce a **repository-aligned PR title** and an **anti-cognitive-surrender PR body** that equips a human reviewer to judge product behavior, design trade-offs, and runtime failure boundaries rather than rubber-stamping the diff. Prefer **`gh`**; if unavailable or unauthenticated, write the draft to a markdown file and give the manual compare link.

## 1. Verify branch, base, and slice size

1. **Confirm `<base>` and `<head>`** (default base: `main` or the repo's default branch; for stacked slices, `<base>` is the parent branch in the stack).
2. **Fetch current refs** and inspect commits and open PRs:

   ```bash
   git fetch origin <base> <head>
   git log origin/<base>..HEAD --oneline
   gh pr list --head <branch> --base <base> --state open
   ```

3. **Check production LOC and self-containment:**

   ```bash
   git diff --stat origin/<base>...HEAD
   ```

   - **Target ~100 LOC of production code (soft ceiling ~200 LOC)**, excluding test files, lockfiles, snapshots, and generated code.
   - **Keep tests in the same PR as the code they verify.** Every PR must be self-contained and significant on its own, even when tests push total lines above 200.
   - If production code exceeds ~200 LOC on an unstacked branch, warn the user and offer to split into stacked vertical slices via [`bmo-stack-prs`](../bmo-stack-prs/SKILL.md) before opening; if the change cannot be split cleanly, note why under **Decisions, trade-offs & backing docs**.

**Done:** `origin/<base>..HEAD` commits and diff stats are inspected; no duplicate open PR exists.

---

## 2. Run pre-PR checks (`hooks/pr-checks.md`)

1. Read and follow [`../hooks/pr-checks.md`](../hooks/pr-checks.md) in the target git root or worktree: discover and run the repository's `lint`, `typecheck`, and `test` commands on the committed `HEAD`.
2. Do not push or run `gh pr create` until every discovered check family exits `0` on the current `HEAD`.
3. **Push `<branch>` if needed:** `git push -u origin <branch>`. If rejected (non-fast-forward), stop and explain so the user can reconcile (`rebase` / `--force-with-lease`).

**Done:** Every discovered check family exited `0` on the committed `HEAD`, and `<branch>` is pushed.

---

## 3. Capture screenshots when visual

- **Visual or UI-copy changes** ([`screenshots.md`](screenshots.md)) — Diff touches UI components, routes/pages, templates, CSS/design tokens, user-visible layouts, **or user-visible UI copy/constants** (such as `*.constants.ts` rendered in templates). Read [`screenshots.md`](screenshots.md) to capture stills and attach them via a release-free upload path (`gh pr create --attach` or `gh image`). **Never create GitHub releases, prereleases, or git tags** just to host media; if release-free screenshot tooling is unavailable in the environment, skip capture cleanly and write `Skipped — screenshot tooling unavailable in this environment` under `## Screenshots`.
- **Non-visual changes** — Write `N/A — non-visual change` under `## Screenshots`.

**Done:** Visual PRs have release-free attached images (or an explicit `Skipped` note when tooling is absent); non-visual PRs are marked `N/A`.

---

## 4. Title

Match the repository's title convention in order: (1) explicit user ask, (2) repo docs / PR workflow (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONTRIBUTING.md`, `.github/workflows/`), (3) dominant style in `git log -n 20 origin/<base> --oneline`, (4) Conventional Commit style (`<type>: <Subject>`).

- **Single commit:** Reuse its subject if it covers the slice.
- **Multiple commits:** Write one summary line covering the slice's outcome.
- **Format:** Imperative present tense, capital first letter after optional `<type>: `, no trailing period, ≤ 72 chars.

---

## 5. Body (preventing cognitive surrender)

Automated checks (`bmo-block-reviewer`, typecheck, tests) already verify file-level mechanics. Design the PR body for **human judgment**—exposing trade-offs, backing docs, boundary failure modes, high-level product/decision questions, and what tests *could not* prove:

1. If **`.github/pull_request_template.md`** exists, read it, fill every required section, and embed the decisions, failure modes, high-level review focus, and unverified gaps inside the template's context/review/testing sections.
2. Otherwise use this structure:

```markdown
## Intent & stack position
- **Why:** <1–2 sentences on the product or system behavior this PR delivers>
- **Out of scope:** <what this PR intentionally defers to later stack slices or non-goals>
- **Stack position:** <`Standalone` or `Part i of k — stacked on #<prev>: <how this slice fits the feature>`>

## Decisions, trade-offs & backing docs
- **<Decision or assumption>:** <Why approach A was chosen over B, or what invariant was assumed> — backed by `<spec / ticket / ADR / schema / sibling path>`.

## Failure modes & boundary risks
- **`<contract / boundary / state transition>` (`<file or module>`):** <What could fail at runtime — e.g., upstream API error/status mapping, payload nullability, DB transaction/migration lock, retry idempotency, race state>.

## How to review (product & decision focus)
1. **<Product or domain behavior to judge>:** <High-level question for the human — e.g., does this state transition, error recovery, or UX flow match product expectations?>
2. **<Architectural or contract trade-off to verify>:** <Decision or cross-service boundary the reviewer should validate against the backing spec/contract>.

## Verification & unverified gaps
- **Automated proof:** `<exact test / typecheck / lint commands run and exit results>`
- **Unverified gaps (human check needed):** `<what automated tests did not prove — live third-party endpoints, prod data distribution, manual UX feel>`
- **How to test locally:**
  1. `<checkout, env, migration, runnable command, expected result>`

## Screenshots
<Attached image markdown from screenshots.md, `Skipped — screenshot tooling unavailable in this environment`, or `N/A — non-visual change`>
```

3. **Tone:** Direct engineering prose; no tool-marketing footers unless requested.
4. **Updating an existing PR after new commits:** Re-run pre-PR checks (`hooks/pr-checks.md`) and edit the body (`gh pr edit <n> --body-file <path>`) whenever decisions, risks, or verification changed, adding an **Updates since open** bullet list derived from `git log origin/<base>..HEAD`.

**Done:** Every section is grounded in the actual diff, plan/digest handoff, and repo scripts; unverified gaps and backing docs are stated honestly.

---

## 6. Create or update on GitHub

### Create a new PR

```bash
gh pr create --base <base> --head <branch> \
  --title "<Title>" \
  --assignee @me \
  --body-file <temp-path>
```

When using `gh --attach` from [`screenshots.md`](screenshots.md), append one `--attach "$OUT/<file>.png"` per referenced still. Delete `<temp-path>` after creation unless the user asked to keep it, and reply with the canonical PR URL.

### Update an existing PR

```bash
gh pr edit <n> --body-file <temp-path> --add-assignee @me
```

Include `--title "<Title>"` if scope shifted (and `--attach` for any newly captured stills when supported).

### Fallback when `gh` is unavailable or unauthenticated

1. Instruct the user to run `gh auth login`.
2. Write `pr-draft.md` in the workspace with title, base, head, full body, and compare URL `https://github.com/<org>/<repo>/compare/<base>...<branch>?expand=1` (when `<org>/<repo>` is known from `git remote`).
