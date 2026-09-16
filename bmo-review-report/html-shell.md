# HTML shell — when writing the brief file

Read this when you start the HTML file, not before. Copy visual language (`<style>`, tab JS, syntax paint) from:

`/Users/lucasferreyravera/roxom/roxtopia/docs/pr-1162-usd-display-toggle-review.html`

Replace the copy. Keep the Reviewed handlers that `stopPropagation`.

## Tabs and rule

- Sticky tablist: Demo (omit the tab if there is no take) / How to review / Hub / Commits / Surfaces / FAQ
- One `.rule` banner under the masthead. Do not restate the rule inside panels
- Demo: `<video class="demo" controls playsinline>` + still grid, all `src` relative (`demo/...`)

## Commit accordion

Every commit:

```html
<details class="acc" data-layer="…" data-review-id="01">
  <summary>
    <span class="hash">01</span>
    <span>Title</span>
    <span class="end">
      <span class="loc"><span class="ins">+N</span> <span class="del">−M</span></span>
      <span class="pill …">layer</span>
      <!-- Reviewed checkbox is injected next to the pill; do not put it in summary HTML by hand unless you copy the stopPropagation handlers -->
    </span>
  </summary>
  <div class="acc-body">
    <p class="intent"><strong>Why.</strong> …</p>
    <p class="look">Look at: …</p>
    <div class="diff">…excerpt…</div>
    <div class="links">
      <a href="https://github.com/<org>/<repo>/pull/<N>/commits/<sha>" target="_blank" rel="noopener noreferrer">commit</a>
    </div>
  </div>
</details>
```

- **Look at** is always visible in the body (`p.look`). Hover-only is not enough
- **Excerpt:** a few lines; the rule-carrying line is `.diff-line.marked` with gold gutter (`box-shadow: inset 3px 0 0 …`) and a `.tip` tooltip. The accordion is not a full diff
- `+N`/`−M` on the title are `git show --stat` (or `gh`) totals for that commit, not the excerpt line count
- Commit href is `/pull/<N>/commits/<sha>`, not `/commit/<sha>` (next/prev must stay on the PR)
- External `http(s)`: `target="_blank"` `rel="noopener noreferrer"`. In-page `#` and `demo/` stay in-page

## Reviewed checkbox

Inject beside the layer pill. Unique `localStorage` key per PR. Checking must not toggle `<details>` (`click`/`keydown` `preventDefault` + `stopPropagation` on the label and input). Do not hide viewed commits — class `reviewed` is a tint only. Layer filters may hide other layers; they must not hide a reviewed commit of the active layer.

Copy the handler block from the example (`REVIEW_STORAGE_KEY`, `data-review-id` loop). Change the storage key to this PR.

## Reject if

Each row: what the reviewer would **see** (UI or a specific line in the linked commit) → why that is a merge blocker. Define a term once if you need it; do not use undefined jargon.

## Copy

Reviewer-facing only. No CORS, Caddy, bun, filming notes, or agent session log.

**Completion criterion:** the file opens as `file://` with working tabs; every commit accordion matches the contract above; Demo relative paths resolve if a take exists; checkbox marks reviewed without collapsing the accordion.
