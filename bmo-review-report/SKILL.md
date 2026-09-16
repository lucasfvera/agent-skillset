---
name: bmo-review-report
description: >-
  Builds a shareable HTML review brief for a large PR or diff. Use when the
  user wants a review brief for reviewers who will not read 100+ files; when
  they want a Sentiless UI demo recording with a visible cursor overlay
  attached to that brief; or when recording is requested or needed but
  Sentiless is not in place and the agent must push back.
disable-model-invocation: true
---

# Review brief

A **review brief** is standalone HTML a reviewer opens locally. It is not GitHub markdown, not a diary of the agent session, and not a visual-recap canvas/plan. Visual-recap maps a diff onto hosted plan blocks; this skill writes an HTML file plus an optional **Sentiless** clip.

Do not commit the brief, `demo/`, or recorder unless the user asks.

## 1. Decide whether a recording is needed

Recording is for user-visible behavior (toggles, account pages, layout). Not for types-only, formatter-only, or test-mock PRs unless the user asks.

Write **yes** or **no** and one sentence of why.

**Completion criterion:** a single written verdict (`yes`/`no` + why). If **no**, skip step 2 entirely — do not read `sentiless.md` or `cursor-overlay.md`.

## 2. Record branch (only if step 1 is yes)

Read [sentiless.md](sentiless.md) **now**, before any Playwright. It owns Sentiless checks, **push back**, local ports, and the recording walk.

When writing or adapting a recorder (not when only running an existing script), also read [cursor-overlay.md](cursor-overlay.md) before the first `page.mouse` call.

**Completion criterion:** either a real take (`take.json` listing every surface clicked) **or** an explicit **push back**. A silent skip is a failed step. If the outcome is push back, continue to step 3 with no Demo clip — never a fake video, never skipped auth.

## 3. Write the HTML

When you start the HTML file, read [html-shell.md](html-shell.md). Until then, do not load it.

When building a new brief, open this file as the shell to copy — do not paste it into chat, and do not read it before this step:

`/Users/lucasferreyravera/roxom/roxtopia/docs/pr-1162-usd-display-toggle-review.html`

Write `docs/pr-<N>-<slug>-review.html` in the repo under review. Demo assets live in a sibling `demo/` folder with relative paths from the HTML.

An **excerpt** is the gold-gutter hunk: the rule-carrying line, not the review surface. Full commit `+N`/`−M` belongs on the accordion title. Link commits inside the PR (`/pull/N/commits/<sha>`) so next/prev stays on the PR.

Copy is a review brief: cut CORS, Caddy, bun paths, how we filmed, agent diary. One **rule** banner; do not restate it in every panel. “Reject if” rows are executable checks a reviewer can see on screen or in the linked commit — not jargon unless defined once in that brief.

**Completion criterion — every item true:**

- Tabs: Demo (only if a take exists) / How to review / Hub / Commits / Surfaces / FAQ
- One rule banner; no second copy of the same rule in other panels
- Every commit in the PR has an accordion: Why, a persistent **Look at** (not hover-only), one excerpt hunk with gold gutter + tooltip, PR-scoped commit link, `+N`/`−M` on the title, layer pill, Reviewed checkbox
- Reviewed checkbox sits next to the layer tag, persists `localStorage`, does not hide viewed commits, does not toggle `<details>`
- External `http(s)` links: `target="_blank"` `rel="noopener noreferrer"`. Same-doc and `demo/` assets stay in-page
- Demo tab (if recorded) points at the webm + stills with relative paths; those files exist
- “Reject if” is a table of observable fails, each independently checkable

## 4. Share (only if a reviewer opens it elsewhere)

GitHub will not run the HTML. When the user will send the brief off this machine, read [share.md](share.md) and zip. Skip this step if they are opening the file locally themselves.

**Completion criterion:** either a zip of HTML + `demo/` with a path reported to the user, or a written “local only — no zip” because they will open the HTML here.
