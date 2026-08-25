# Visual screenshots for PR bodies

Load this file only when the **visual** gate in `SKILL.md` is **yes**. Capture and embed images **before** `gh pr create` / `gh pr edit` so the Screenshots section is never a leftover `N/A` on a visual PR.

## Tooling gate (mandatory)

Run this **before** mode, targets, or capture. Visual PRs need real screenshots in the body — missing tools are a hard stop, not a soft fallback.

1. **`agent-browser`** (capture — same CLI as `~/roxom/outworld` `screenshot-browser`):

   ```bash
   command -v agent-browser >/dev/null 2>&1 && agent-browser --version
   ```

   Exit **0** and a version line required.

2. **Upload path** — at least one of:

   ```bash
   gh extension list | grep -q gh-image && echo "gh-image OK"
   # or stock gh is enough for the prerelease-asset path below:
   gh auth status
   ```

   Prefer **`gh image`** ([`drogers0/gh-image`](https://github.com/drogers0/gh-image)). If it is missing but `gh auth status` succeeds, the prerelease-asset path is allowed. If **both** fail, treat as missing tooling.

**If anything required is missing — push back and stop:**

- Do **not** create or edit the PR.
- Do **not** substitute Cursor browser MCP, Playwright, or “open the PR and drag-drop later”.
- Tell the user what failed and how to install, then wait for them to retry `/bmo-pr`:

  ```text
  Visual PR needs screenshots. Install tooling, then re-run /bmo-pr:

  # capture
  npm install -g agent-browser && agent-browser install

  # upload (recommended)
  gh extension install drogers0/gh-image

  # or ensure gh is logged in for prerelease asset uploads
  gh auth login
  ```

**Done (tooling):** `agent-browser` verified; upload path verified (`gh image` or authenticated `gh`). Otherwise stopped with the install ask above.

## Mode

Pick exactly one:

| Mode | When | What to capture |
|------|------|-----------------|
| **before/after** | An existing screen or flow changes | Same URL/path, same viewport: **before** on base (or current prod/QA still on base), **after** on the PR branch |
| **implementation-only** | New UI with no prior screen to compare | One (or a short set of) **after** shots of the new surface |

If before is blocked (no runnable base, no stable base URL, auth wall), fall back to **implementation-only** and say so in one line under the images — do not invent a fake before.

**Done (mode):** one mode chosen; if before/after, both sides targeted for the same route(s).

## Targets

1. **Routes** — From the diff and “How to test”, list the URL path(s) a reviewer must open (e.g. `/exchange/account/deposit`). Prefer the fewest paths that show the change.
2. **Base URL** — Local dev from README/`package.json` scripts, or a QA/preview host the user names. Do not hardcode a host from another repo.
3. **Viewport** — Default desktop unless the change is mobile-specific; keep before and after identical.

**Done (targets):** every capture has a concrete absolute URL and output path.

## Capture (`agent-browser` only)

Use **`agent-browser` only** (outworld flow: open → settle → screenshot). No other browser tool.

Write under a **temp** directory (do not commit screenshots unless the user asks):

```bash
OUT="${TMPDIR:-/tmp}/bmo-pr-screenshots/<branch-slug>"
mkdir -p "$OUT"

agent-browser open "<absolute-url>"
agent-browser wait 2000
agent-browser screenshot "$OUT/<name>.png"
# optional: agent-browser screenshot --full "$OUT/<name>.png"
```

**Settle** = fixed **2000 ms** wait after open (match outworld) unless the page needs a longer explicit wait for a known spinner/route transition — then wait that, still once, before the shot.

**Naming:**

- before/after: `<route-slug>-before.png`, `<route-slug>-after.png`
- implementation-only: `<route-slug>-after.png` (or `-01`, `-02` for a short set)

**before/after order (local app):**

1. Ensure the app serves the **PR branch** → capture **after**.
2. Switch to **base** (stash if needed, `git checkout origin/<base>` or equivalent) → same URL → capture **before** → restore the PR branch and stash.
3. If switching branches is too costly, capture **before** from a still-base remote URL, then **after** from the PR preview/local URL.

If capture fails after tooling was verified (app down, auth wall, bad URL), **push back and stop** — fix the environment, then re-run. Do not open a PR with empty Screenshots.

**Done (capture):** every planned PNG exists on disk and is readable; branch/worktree restored if you checked out base.

## Embed in the PR body

Images must be **URLs** GitHub can render (local paths do not work in the PR body).

**Upload preference:**

1. **`gh image`** when installed — prints markdown `![…](https://github.com/user-attachments/assets/…)`:

   ```bash
   gh image "$OUT/<name>.png"
   ```

2. Else **prerelease assets** on a throwaway tag (authenticated `gh`):

   ```bash
   TAG="pr-screenshots-<branch-slug>"
   gh release create "$TAG" "$OUT"/*.png \
     --title "PR screenshots ($TAG)" \
     --notes "Temporary assets for PR body; safe to delete after merge." \
     --prerelease
   # Resolve each asset's browser_download_url via:
   #   gh api "repos/<owner>/<repo>/releases/tags/$TAG" --jq '.assets[] | {name, browser_download_url}'
   ```

If upload fails, **push back and stop** — do not create/edit the PR with local-only paths.

**Body shapes** (fill the template’s Screenshots section, or the default skeleton):

before/after:

```markdown
| Before | After |
| -- | -- |
| ![before](<url>) | ![after](<url>) |
```

implementation-only:

```markdown
![after](<url>)
```

Multiple routes: one table (or one after block) **per route**, with the path as a short subheading.

**Done (embed):** Screenshots section has live image markdown for the chosen mode.

## Out of scope

- Pixel diff / `odiff` (that is outworld `screenshot-compare`, not required for PR bodies).
- Committing PNGs into the app repo by default.
- Capturing every page in the product — only routes the change touches.
- MCP/Playwright capture substitutes when `agent-browser` is missing.
