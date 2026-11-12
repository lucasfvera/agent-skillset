# Visual screenshots for PR bodies (release-free)

Load this file when the visual check in [`SKILL.md`](SKILL.md) (`## 3. Capture screenshots when visual`) fires.

**Hard rule — never create GitHub releases, prereleases, or tags** to upload screenshots, and never commit temporary PNGs into the repository. If a release-free upload path or browser capture tool is unavailable, **skip the screenshot step cleanly** instead.

## 1. Tooling & release-free upload check

Verify both capture and a release-free upload path before booting the app:

1. **Capture CLI (`agent-browser`):**

   ```bash
   command -v agent-browser >/dev/null 2>&1 && agent-browser --version
   ```

2. **Release-free upload path** — detect the first available option:
   - **Path A (preferred — native GitHub CLI 2.99.0+ `--attach`):**
     ```bash
     gh pr create --help | grep -q -- '--attach' && gh auth status
     ```
   - **Path B (`gh image` extension):**
     ```bash
     gh extension list | grep -q gh-image && gh auth status
     ```

**When either check fails — skip cleanly (never create GitHub releases, prereleases, or tags):**
- Set `## Screenshots` in the PR body to `Skipped — screenshot tooling unavailable in this environment` and note which tool was missing (`agent-browser`, `gh 2.99.0+ --attach`, or `gh-image`) in your chat summary so the user can attach media manually if needed.
- Stop reading this file and continue to [`SKILL.md`](SKILL.md) `## 4. Title`.

**Done:** Both `agent-browser` and Path A (`--attach`) or Path B (`gh image`) are available, or `## Screenshots` is marked `Skipped` and capture is bypassed.

---

## 2. Mode & surfaces

Pick one mode from the diff:

| Mode | When | What to capture |
|------|------|-----------------|
| **before/after** | Existing screen, component, or copy changes | Same URL/path and viewport: **after** on the PR branch, **before** on `<base>` (or a still-base preview/QA URL) |
| **implementation-only** | Brand-new UI surface with no prior screen | **after** shots of the new surface |

If capturing **before** is blocked (no runnable base or preview URL), fall back to **implementation-only** and add a one-line note beneath the image.

For each affected surface, list: `URL path — optional control to click/open — expected visual state` (so modals, menus, toggles, and validation states are captured open, not just initial page load).

**Done:** Mode and ordered surface list (with URLs and interactive controls) are defined.

---

## 3. Sessions & authentication

Keep logged-out and logged-in state isolated in separate `agent-browser` sessions:

| Auth requirement | Session flag |
|------------------|--------------|
| Logged-out / public route | `--session anon` |
| Logged-in / guarded route | `--session authed` |
| Both | Capture both; prefix filenames with `anon-` and `authed-` |

**Logged-in state resolution (in order):**
1. Existing state file in `$AGENT_BROWSER_STATE`: `agent-browser --session authed --state "$AGENT_BROWSER_STATE" ...`
2. Environment credentials (`$E2E_USER_EMAIL` and `$E2E_USER_PASSWORD`): open the login route, fill from env vars without printing secret values, save state, then walk the target surfaces.
3. If the route is auth-gated and neither session state nor credentials exist, **skip capture** (or ask the user once if interactive) rather than screenshotting a login redirect wall as fake proof.

**Done:** Required session(s) are authenticated or the auth blocker is handled honestly.

---

## 4. Capture stills

Write PNGs under a temporary directory outside git tracking:

```bash
OUT="${TMPDIR:-/tmp}/bmo-pr-screenshots/<branch-slug>"
mkdir -p "$OUT"

agent-browser --session <anon|authed> open "<absolute-url>"
agent-browser --session <anon|authed> wait 2000
# If the surface requires opening a modal, tab, or toggle:
# agent-browser --session <anon|authed> click "<selector>" && agent-browser --session <anon|authed> wait 1000
agent-browser --session <anon|authed> screenshot "$OUT/<name>.png"
```

- **Naming:** `<route-slug>-before.png` / `<route-slug>-after.png` (`before/after`), or `<route-slug>-after.png` (`implementation-only`).
- **Before/after order on a local dev server:** capture **after** on the PR branch first; if switching to `origin/<base>` locally for **before**, restore the PR branch checkout/worktree immediately afterward.

**Done:** Every planned PNG exists on disk and is non-empty; working branch is restored.

---

## 5. Embed & attach (release-free)

### Using Path A (`gh pr create --attach` / `gh pr edit --attach`)

1. Reference the local `$OUT/<file>.png` paths directly in the PR body file (`gh` uploads each file and rewrites the Markdown path to `https://github.com/user-attachments/assets/...`):

   ```markdown
   | Before | After |
   | --- | --- |
   | ![before](<OUT>/<route-slug>-before.png) | ![after](<OUT>/<route-slug>-after.png) |
   ```

   *(Or `![after](<OUT>/<route-slug>-after.png)` for `implementation-only`.)*

2. Pass one `--attach` flag per referenced PNG on `gh pr create` or `gh pr edit`:

   ```bash
   gh pr create ... --body-file <temp-path> \
     --attach "$OUT/<route-slug>-before.png" \
     --attach "$OUT/<route-slug>-after.png"
   ```

3. Verify `gh pr view <n> --json body -q .body` contains `https://github.com/user-attachments/assets/` URLs and zero leftover local `$OUT` paths.

### Using Path B (`gh image`)

1. Upload each still before creating/updating the PR:

   ```bash
   gh image "$OUT/<name>.png"
   ```

2. Place the returned `![...](https://github.com/user-attachments/assets/...)` Markdown URLs into `## Screenshots` in the PR body file, then run `gh pr create` / `gh pr edit`.

**Done:** Published PR body renders live `user-attachments` image URLs with zero GitHub releases or tags created.
