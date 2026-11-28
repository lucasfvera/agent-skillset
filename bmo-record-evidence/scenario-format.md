# Scenario format

A scenario is JSON. Paths and commands run from the scenario file's folder.

| Key | Meaning |
|---|---|
| `title` | Shown at the top of the panel. |
| `secrets` | Names of env vars the run needs, such as passwords or tokens. The run stops if any is missing. Their values are masked everywhere. |
| `mask` | Extra regexes to mask in the panel, for example IDs that look like personal data. JWTs are always masked. |
| `setup` | Shell commands run before the browser opens: reset, then seed. Any non-zero exit stops the run. |
| `teardown` | Shell commands run after recording. Their failures are ignored. |
| `viewport` | `{ "width", "height" }`. The default is 1600×900. |
| `steps` | Run in order. Each one is drawn in the panel. |

## Steps

| Step | Effect | `assert` scope |
|---|---|---|
| `{ "note": "…" }` | Adds a caption. | |
| `{ "goto": "/path" }` | Opens a path relative to `--base-url`. | |
| `{ "fill": "<selector>", "value": "…" }` or `"secret": "NAME"` | Types into a field. A `secret` must be listed in `secrets`. | |
| `{ "click": "<selector>", "waitFor": "/url-part" }` | Clicks. `waitFor` is optional; without it the step waits for the network to go idle. | |
| `{ "press": "Enter", "on": "<selector>" }` | Presses a key. | |
| `{ "screenshot": "name", "fullPage": false }` | Saves `name-<side>.png` with the panel hidden. | |
| `{ "capture": "name", "match": { "method", "urlIncludes", "header" }, "click": "<selector>" }` | Saves the next matching request: method, URL, headers, and body. This is DevTools' **Copy as fetch**. | |
| `{ "replay": "name", "edit": "body.id = 'x'" }` | Re-sends a captured request from inside the page, like pasting into the console. `edit` is JS that changes `body`, which is parsed JSON when it parses and text when it doesn't. | `status`, `text` |
| `{ "eval": "<js>" }` | Runs JS in the page. | `value` |
| `{ "run": "<shell>", "label": "…" }` | Runs any command: a DB query, a CLI, an HTTP call, a log grep. Output that is a JSON array of objects is drawn as a table. | `code`, `stdout`, `stderr`, `rows` |

Each `assert` is a JS expression over the scope listed in the table. Its verdict goes into `<side>.json`.

To make a DB query render as a table, have it output a JSON array. For Postgres:
`psql "$DATABASE_URL" -XAtc "SELECT coalesce(json_agg(t),'[]') FROM (SELECT …) t"`

## Web example: replaying a request with another user's ID

```json
{
  "title": "Users cannot archive another user's document",
  "secrets": ["E2E_PASSWORD_ATTACKER"],
  "setup": ["psql \"$DATABASE_URL\" -X -v ON_ERROR_STOP=1 -f reset.sql -f seed.sql"],
  "steps": [
    { "goto": "/login" },
    { "fill": "input[name=email]", "value": "attacker@example.test" },
    { "fill": "input[name=password]", "secret": "E2E_PASSWORD_ATTACKER" },
    { "click": "button[type=submit]", "waitFor": "/dashboard" },
    { "run": "./q.sh \"SELECT id, archived_at FROM documents WHERE id = 'victim-doc'\"", "label": "Victim document" },
    { "goto": "/documents" },
    { "capture": "archiveOwn", "match": { "method": "POST", "urlIncludes": "/documents" }, "click": "[data-id=own-doc] >> text=Archive" },
    { "replay": "archiveOwn", "edit": "body.documentId = 'victim-doc'", "assert": "status >= 400" },
    { "run": "./q.sh \"SELECT id, archived_at FROM documents WHERE id = 'victim-doc'\"", "label": "Victim document", "assert": "rows[0].archived_at === null" }
  ]
}
```

## Non-browser example: a CLI or data change

Without `goto` steps, the panel fills the screen and the video works like a terminal recording.

```json
{
  "title": "Backfill sets missing slugs without touching existing ones",
  "setup": ["./reset-and-seed.sh"],
  "steps": [
    { "run": "./q.sh \"SELECT id, slug FROM posts ORDER BY id\"", "label": "Posts before backfill" },
    { "run": "yarn backfill:slugs --dry-run=false", "assert": "code === 0" },
    { "run": "./q.sh \"SELECT id, slug FROM posts ORDER BY id\"", "label": "Posts after backfill", "assert": "rows.every(r => r.slug)" }
  ]
}
```
