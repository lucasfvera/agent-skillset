# Attach media to a PR

This file is the only place that defines how screenshots and videos get to GitHub. Media goes up as **PR attachments**, through `gh --attach` or `gh image`, and GitHub serves it from `https://github.com/user-attachments/assets/…`.

**Hard rule:** media goes only into PR attachments. Never host media any other way: no GitHub releases or prereleases, no git tags, no gists, no commits on any branch, and no outside file hosts. When neither upload path below works, the evidence is `Skipped`. That counts as a finished result, not a problem to route around.

## 1. Pick the upload path

Use the first one that is available:

- **Path A — `gh` 2.99.0 or later:** `gh pr create --help | grep -q -- '--attach' && gh auth status`
- **Path B — `gh image` extension:** `gh extension list | grep -q gh-image && gh auth status`

When neither is available, write `- **Screenshots/Recording:** Skipped — no PR attachment upload path (needs gh 2.99+ or gh-image)` under `## Evidence`. Mention it in the chat summary and stop reading this file.

**Done:** Path A or Path B is chosen, or a `Skipped` line is in the body.

## 2. Embed and upload

- **Path A:** In the body file, refer to each local file by its path. Images use `![before](<path>.png)`. A video goes on its own line as the bare path. Pass one `--attach "<path>"` per file to `gh pr create` or `gh pr edit`, and `gh` swaps each path for its `user-attachments` URL.
- **Path B:** Run `gh image "<path>"` for each file. Paste the Markdown it returns into the body before you publish.

Use a table for before/after stills: `| Before | After |`.

## 3. Verify

Run `gh pr view <n> --json body -q .body`.

**Done:** Every piece of media in the body is a `user-attachments` URL, and no local path is left. When a video upload didn't produce a URL, delete that line, keep the stills, and add `Video not attached — upload path rejected it`.
