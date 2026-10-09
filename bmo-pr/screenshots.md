# Attach stills to the PR body

Load after `/bmo-feature-recorder` destination `pr` has returned `OUT` and `take.json`. Capture lives in the recorder; this file attaches with `gh` itself.

## Tooling

`gh pr create` / `gh pr edit` must list `--attach` (GitHub CLI 2.99.0+):

```bash
gh pr create --help | grep -q -- '--attach' && gh auth status
```

If either fails, **push back** and stop — no PR yet:

```text
Visual PR needs gh 2.99.0+ for --attach. Then re-run /bmo-pr:

brew upgrade gh    # or your OS package manager
gh auth login      # write access to the repo is required
```

**Done:** `--attach` present and `gh auth status` succeeds, or stopped.

## Body

Write the Screenshots section (template or default skeleton) with the **local PNG paths** from `OUT`. `gh` rewrites each referenced path to the uploaded URL and keeps the alt text.

before/after:

```markdown
| Before | After |
| -- | -- |
| ![before](<OUT>/<route-slug>-before.png) | ![after](<OUT>/<route-slug>-after.png) |
```

implementation-only:

```markdown
![after](<OUT>/<route-slug>-after.png)
```

Multiple routes: one table (or one after block) **per route**, with the path as a short subheading. If mode fell back to implementation-only, one line under the images.

**Done:** every PNG that `take.json` marks true is referenced once in the body file.

## Attach

Pass one `--attach` per referenced PNG on the same command that writes the body:

```bash
gh pr create ... --body-file <path> \
  --attach "$OUT/<route-slug>-before.png" \
  --attach "$OUT/<route-slug>-after.png"

# existing PR
gh pr edit <n> --body-file <path> --attach "$OUT/<route-slug>-after.png"
```

A partial upload still creates or edits the PR but exits non-zero. Treat any non-zero exit as a failed attach: report which file failed and re-run `gh pr edit <n> --body-file <path> --attach …` for it.

**Done:** `gh pr view <n> --json body --jq .body` shows `https://github.com/user-attachments/assets/` URLs and no `OUT` paths.
