# Share — when a reviewer opens the brief on another machine

GitHub will not render this HTML from a PR comment. Recipients unzip and open the HTML locally.

Skip this file if the user is opening the brief on this machine.

From the directory that contains the HTML and `demo/`:

```bash
zip -r "pr-<N>-review-brief.zip" "pr-<N>-<slug>-review.html" demo
```

Include every file the Demo tab references. Always omit recorder scripts, `.env`, and passkeys. Include `take.json` only after confirming it has no emails or credentials; strip those fields if present.

Report the zip path. Recipients: unzip, open the HTML. Relative `demo/` paths break if they move the HTML without the folder.

**Completion criterion:** zip exists, contains the HTML plus every `demo/` asset the HTML references, and the user has the path.
