---
name: bmo-merge-risk
description: Assesses the risk of merging a PR across alignment, impact, verification, rollback cost, and error detection.
disable-model-invocation: true
argument-hint: "[optional pr number/url or base ref]"
metadata:
  credits:
    - skill: merge-risk
      author: Warp
      url: "https://github.com/warpdotdev/common-skills/blob/main/.agents/skills/merge-risk/SKILL.md"
    - skill: pr
      author: Matt Pocock
      url: "https://github.com/mattpocock/skills/blob/main/skills/engineering/pr/SKILL.md"
---

# Merge risk

Read-only assessment of how risky a pull request is to merge. Runs either standalone on an existing PR/branch or inside a subagent spawned by [`bmo-pr`](../bmo-pr/SKILL.md) and [`bmo-stack-prs`](../bmo-stack-prs/SKILL.md). Leave all repository files untouched.

## 1. Load the diff and context

- **Subagent handoff from `bmo-pr` / `bmo-stack-prs`:** Read the provided draft PR title/body, linked issue or plan (when supplied), and run `git -C "<GIT_ROOT>" diff <base>...<head>` (opening touched files when surrounding context is needed to judge blast radius or error handling).
- **Standalone invocation (`/bmo-merge-risk [pr | base]`):**
  - PR number or URL → fetch `gh pr view <pr> --json title,body,baseRefName,headRefName,files` and `gh pr diff <pr>`.
  - Local branch → compare `git diff origin/<base>...HEAD` and `git log origin/<base>..HEAD` (default `<base>`: `main`).

**Done:** Every changed file in `<base>...<head>` and the PR description (plus source issue, when present) are inspected.

## 2. Evaluate categories and score

Rate every category below against the diff (`good` / `small` / `low` / `N/A` defines low risk):

- **Alignment (`poor ⚠️` / `decent 👀` / `good ✅`):** Code matches the PR description and source issue (when present). Behavior assumptions and unrelated side changes are documented.
- **Impact (`large ⚠️` / `medium 👀` / `small ✅`):** Scope is contained and outside sensitive code paths.
  - Evaluate **blast radius** across callers and surfaces (layout shift, consumer breakages, mobile responsiveness, shared contract changes).
  - Flag **sensitive areas** regardless of diff size: auth, permissions, payments, personal data (PII), secrets, data migrations, dependency updates, and infrastructure or config changes. Call out widened access, weakened validation, or logged sensitive data.
- **Verification (`poor ⚠️` / `decent 👀` / `good ✅`):** Behavior is verified where applicable.
  - User-experience changes require end-to-end proof (screenshots or recording); performance-affecting changes require profiling. Prefer before-and-after proof over standalone proof; missing required proof lowers the verdict to `poor ⚠️`.
  - Edge cases are tested, or documented with links/paths to the relevant code when untested.
- **Rollback cost (`high ⚠️` / `medium 👀` / `low ✅`):** Code is reversible once merged. Distinguish **two-way doors** (reversible with a git revert) from **one-way doors** (destructive writes, irreversible schema/data migrations, external contract commitments).
- **Error detection (`poor ⚠️` / `decent 👀` / `good ✅` / `N/A ✅`):** When applicable, critical flows emit signals or monitoring so production breakage surfaces before users report it. Flag swallowed errors or fallbacks that mask failures.

Compute the overall `low` / `medium` / `high` rating internally:

- Verdict values: `⚠️ = 3`, `👀 = 2`, `✅ = 1`
- Category weights: `Impact = 2x`, `Verification = 2x`, `Rollback cost = 1.5x`, `Error detection = 1x`, `Alignment = 1x` (total weight `7.5`)
- Weighted score: `Σ(value × weight) / 7.5` → `low`: `< 1.5`, `medium`: `1.5` to `< 2.25`, `high`: `≥ 2.25`

Keep the numeric values, weights, and score calculation internal; omit all math from the output.

**Done:** All 5 categories have an evidence-backed verdict and the overall `low` / `medium` / `high` level matches the weighted formula.

## 3. Emit the report

Write every bullet as an **actionable reviewer check** for a cold human deciding whether to approve:

- **Actionable, not descriptive** — 1 plain-English sentence (≤ 25 words) stating *what could go wrong* and *what the reviewer should check, confirm, or accept* before merging.
- **High-signal only (no padding)** — default to **0–1 bullet** per `👀`/`⚠️` category (hard cap **2**); skip minor edge cases that would not change a merge decision, and omit bullets under `✅` categories.
- **No code-symbol soup** — never list internal function names, CLI flags, regexes, or stack multiple issues into one bullet; use at most 1 short filename anchor in backticks at the end (e.g. ``(`auth/callback.ts`)``).

Good actionable bullet examples:
- "Auth middleware skips role checks for service tokens; confirm this wider access is intended (`auth/middleware.ts`)."
- "Duplicate webhook retries have no automated test; inspect the idempotency check manually (`billing/webhooks.ts`)."
- "Database errors return an empty list instead of failing; confirm silent empty results are acceptable (`orders/repo.ts`)."

Return this exact structure, keeping the italic definition line under every category subtitle:

```markdown
**Merge risk: <low | medium | high>**

**Alignment:** <poor ⚠️ | decent 👀 | good ✅>
*Code matches the PR description and source issue, with no undocumented side changes.*
- <1 actionable reviewer check (≤ 25 words) + optional (`filename`) — omit when ✅>

**Impact:** <large ⚠️ | medium 👀 | small ✅>
*Blast radius across callers/surfaces and any touch on sensitive areas (auth, data, deps, config).*

**Verification:** <poor ⚠️ | decent 👀 | good ✅>
*Changed behavior and edge cases are backed by tests, screenshots/recordings, or profiling.*

**Rollback cost:** <high ⚠️ | medium 👀 | low ✅>
*Reversible with a git revert (`low`) vs. a one-way change like a migration or external contract (`high`).*

**Error detection:** <poor ⚠️ | decent 👀 | good ✅ | N/A ✅>
*Failures in critical paths surface via errors or monitoring instead of failing silently.*
```

**Done:** All 5 categories include their italic definition line; every `👀`/`⚠️` category has 0–2 actionable plain-English bullets (≤ 25 words, at most 1 filename anchor); zero internal code jargon or score math appears; zero files were modified.
