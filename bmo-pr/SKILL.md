---
name: bmo-pr
description: Opens or updates concise GitHub pull requests with pre-PR checks, visual evidence, and a subagent merge-risk assessment.
disable-model-invocation: true
metadata:
  credits:
    - skill: merge-risk
      author: Warp
      url: "https://github.com/warpdotdev/common-skills/blob/main/.agents/skills/merge-risk/SKILL.md"
    - skill: pr
      author: Matt Pocock
      url: "https://github.com/mattpocock/skills/blob/main/skills/engineering/pr/SKILL.md"
---

# Pull requests (GitHub)

Give the reviewer what the diff cannot: why the change exists, any rejected alternative worth knowing, proof it works, and an independent merge-risk check. Keep the body shorter than the diff.

## 1. Inspect branch, commits, and slice size

1. Fetch refs and inspect history, open PRs, and diff stats (`<base>` defaults to `main` or the repo default; for stacked slices, `<base>` is the parent branch):

   ```bash
   git fetch origin <base>
   git --no-pager log origin/<base>..HEAD
   git --no-pager diff --stat origin/<base>...HEAD
   gh pr list --head <branch> --base <base> --state open
   ```

2. Read commit bodies before the diff for motivation, then verify every claim against the code (including deleted lines when fixing a bug).
3. **Slice size:** Target ~100 LOC of production code (soft ceiling ~200 LOC, excluding tests, lockfiles, snapshots, and generated code), keeping tests in the same PR as the code they verify. When an unstacked branch exceeds ~200 production LOC, warn the user and offer to split via [`bmo-stack-prs`](../bmo-stack-prs/SKILL.md); if kept together, state why in one bullet under `## Decisions`.

**Done:** Commit history, diff, and open PRs are checked; every claim planned for the body is verified in code.

---

## 2. Run pre-PR checks and push

1. Run the repository's `lint`, `typecheck`, and `test` commands on the committed `HEAD` per [`../hooks/pr-checks.md`](../hooks/pr-checks.md) until every present family exits `0`.
2. Push the branch when remote is missing or behind: `git push -u origin <branch>`. On a non-fast-forward rejection, stop and report so the user can reconcile.

**Done:** All discovered check families exited `0` on the committed `HEAD`, and `<branch>` is pushed.

---

## 3. Record evidence when behavior is observable

- **Observable behavior:** the change alters something a person can see by running the system, such as a page, copy, a request's response, stored data, CLI output, or logs. Read [`../bmo-record-evidence/SKILL.md`](../bmo-record-evidence/SKILL.md) and follow it from step 1. It records before/after video, stills, and assertions, then uploads them through [`attach-media.md`](attach-media.md).
- **Nothing observable:** for example docs, types only, or test-only changes. Put short behavior or test evidence in Step 4.

**Done:** The evidence is attached per `attach-media.md`, or `## Evidence` has a `Skipped` line naming what was missing, or the change has nothing observable and goes straight to Step 4.

---

## 4. Draft title and body

### Title

Match repository convention in order: (1) explicit user request, (2) repo docs or PR workflows (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONTRIBUTING.md`, `.github/workflows/`), (3) dominant pattern in `git log -n 20 origin/<base> --oneline`, (4) Conventional Commits (`<type>: <Subject>`). Use imperative present tense, ≤ 72 characters, no trailing period. Reuse a single commit's subject when it states the outcome.

### Body

1. **Repository PR template first:** If `.github/pull_request_template.md` (or `.github/PULL_REQUEST_TEMPLATE/`) exists, follow its headings and instructions in order. Answer directly under each heading without repeating template prompt text, strip instructional HTML comments while preserving machine-read markers/trailers, and place Step 5's merge-risk output at the end.
2. **Default template** (when no repo template exists):

   ```markdown
   <1 sentence: what changes at the behavior level, without file lists or flag names.>

   <1–2 sentences: why — who needs it and what fails or stays blocked without it. Link the issue or design doc when present.>

   <Stacked PRs only: Part i of k — depends on #<prev>.>

   <details>
   <summary>More details</summary>

   <Optional sketch — read references/sketches.md only when control flow, UI hierarchy, or module layout changed in a way the opening sentences hide.>

   ## Decisions
   - **<Choice> over <rejected alternative>:** <1 short plain-English reason> (<doc/issue link if any>).

   ## Evidence
   - **Before:** <prior screenshot, observed output, or failing behavior>
   - **After:** <new screenshot, observed output, or short verification mechanism such as `unit tests`>

   </details>

   ## Merge risk
   <output from Step 5>
   ```

3. **Pruning rules:**
   - **Accordion (`More details`):** Leave a blank line after `</summary>` and before `</details>` so GitHub renders Markdown inside it; omit the `<details>` block if none of sketch, `## Decisions`, or `## Evidence` apply.
   - **Decisions:** Write plain-English trade-offs only (`Choice over alternative — why`), max 3 short bullets (≤ 20 words each), free of file lists, symbol names, or exit codes. Omit `## Decisions` when no real alternative was rejected.
   - **Evidence:** Omit `**Before:**` on net-new non-UI additions; keep non-UI evidence to 1–2 short lines (such as before/after behavior or `Verified with unit tests`).
   - Omit raw shell command invocations, CLI flags, exit-code logs, file-by-file walkthroughs, and `N/A` placeholder sections.
   - Keep prose direct and free of tool-marketing footers.
   - When updating an open PR after new commits, re-run Step 2, refresh any stale lines, and add a brief `Updates:` line only when scope changed.

**Done:** Draft title and body file exist in a temporary path outside the repository, scaled shorter than the diff with zero raw command dumps.

---

## 5. Run merge-risk subagent (`bmo-merge-risk`)

1. Spawn **one read-only subagent** using the host's subagent tool with the prompt in [`references/merge-risk-subagent.md`](references/merge-risk-subagent.md), supplying `SKILLS_DIR`, `GIT_ROOT`, `<base>`, `<head>`, the draft title and body (including `## Evidence`), and any source issue or plan link. (If the host has no subagent tool, execute [`../bmo-merge-risk/SKILL.md`](../bmo-merge-risk/SKILL.md) inline.)
2. If the subagent flags an `Alignment` gap caused by a missing assumption or inaccurate sentence in the draft body, fix the draft body and update `Alignment` accordingly.
3. Paste the subagent's returned `**Merge risk: ...**` block verbatim under `## Merge risk` in the temporary body file.

**Done:** Temporary body file embeds the complete 5-category `bmo-merge-risk` output from the subagent.

---

## 6. Publish on GitHub

Open PRs **ready for review** by default (pass `--draft` only when the user explicitly asks for a draft):

```bash
gh pr create --base <base> --head <branch> \
  --title "<Title>" \
  --assignee @me \
  --body-file <temp-path>
```

Add one `--attach "<path>"` per media file when [`attach-media.md`](attach-media.md) chose Path A. Delete `<temp-path>` after publishing and reply with the PR URL.

**Update an existing PR:**

```bash
gh pr edit <n> --body-file <temp-path> --add-assignee @me
```

Include `--title "<Title>"` if scope changed. If `gh pr edit` fails on deprecated GraphQL fields, patch via REST: `gh api -X PATCH repos/<owner>/<repo>/pulls/<n> -F body=@<temp-path>`.

**Fallback when `gh` is unavailable or unauthenticated:** Ask the user to run `gh auth login` and write the draft + compare URL (`https://github.com/<org>/<repo>/compare/<base>...<branch>?expand=1`) to a scratch file.

**Done:** PR is open (or updated) on GitHub with the embedded merge-risk block, `<temp-path>` is deleted, and the canonical PR URL is printed.
