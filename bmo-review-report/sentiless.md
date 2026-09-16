# Sentiless — record branch only

Read this after the recording decision is **yes**. Do not load it on a types-only / no-clip run.

**Sentiless** is `~/roxom/internal-sentinel` on branch `sentiless`. Passkey + `E2E_USER_EMAIL` live in its gitignored `.env`. Never print emails, passkeys, or `.env` values.

When writing or adapting a recorder, open this script as the walk to copy, then read [cursor-overlay.md](cursor-overlay.md):

`/Users/lucasferreyravera/roxom/internal-sentinel/scripts/record-usd-toggle-demo.ts`

Do not paste that file into chat.

## Push back before faking a take

If the feature is visual and a clip would help, but Sentiless, passkey, or the local app is missing: **push back**. Refuse to fake a QA recording or skip auth. Ask the user to enroll or to skip the clip. Then stop this file and return to the HTML step with no Demo video.

## Verify (do not print secrets)

Run from `~/roxom/internal-sentinel`. Report only present/missing, never values.

1. Repo exists: `test -d "$HOME/roxom/internal-sentinel"`
2. Passkey present — **one** of:
   - `test -f playwright/.auth/passkey.json`
   - `E2E_PASSKEY_PATH` names an existing file (do not print the path)
   - `E2E_PASSKEY_CREDENTIAL` is set: `awk -F= '/^E2E_PASSKEY_CREDENTIAL=/ { found=1; print ($2=="" ? "missing" : "set") } END { if (!found) print "missing" }' .env`
3. Email set, value hidden: `awk -F= '/^E2E_USER_EMAIL=/ { found=1; print ($2=="" ? "missing" : "set") } END { if (!found) print "missing" }' .env`
4. Target app actually running (HEAD or GET, status < 500)

If any check fails → **push back**. Do not launch Chromium.

## Local Roxom ports

These facts are for a local Roxtopia take. Other apps: same rules, different origins — still no Caddy unless CORS on the API allows it.

- Login on roxoland `http://localhost:3001`
- Walk exchange at `http://localhost:3000/exchange` (basePath `/exchange`)
- Do **not** use Caddy `:8080`: Window `CORS_ORIGIN` is `:3000`–`:3002`; Caddy login hangs
- Ignore Sentiless `.env` `BASE_URL=https://pu.mba` unless the user set an explicit QA target (`DEMO_TARGET=qa` or equivalent)
- Flag/feature must be on locally if the demo depends on it

## Recording walk

Exercise the actual user surfaces, not one control. For a toggle that lives in two places, walk both. HoverCards: keep the mouse on the card or it closes.

Inject a **cursor overlay**; drive `page.mouse.move` then click; pause so clicks are readable (see [cursor-overlay.md](cursor-overlay.md)).

Write artifacts next to the brief:

- `demo/<slug>.webm`
- stills for each state shown in the Demo tab
- `demo/take.json` — origins used (no emails), each surface/control, boolean clicked/opened, `recordedAt`

Point the Demo tab at those files with relative paths (`demo/...`).

**Completion criterion:** `take.json` exists and every intended click is a true/false field (false is allowed; omitting the field is not) **or** the user was told to enroll/skip — not a silent skip.
