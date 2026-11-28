---
name: bmo-record-evidence
description: Records before/after evidence for any PR (video, stills, and pass/fail assertions) by running one scripted scenario against the base and PR commits.
disable-model-invocation: true
argument-hint: "[PR number, branch, or issue to prove]"
---

# Record before/after evidence

A **scenario** is the repro written as data: the state it needs, the steps a person would take, and the **observables** that show the outcome. Steps can be browser actions, console replays, or any shell command (DB queries, CLIs, HTTP calls, logs). The same scenario runs on the base commit (**before**) and the PR commit (**after**). Each run produces a video with a panel that shows every step and its output, any screenshots the scenario asks for, and a verdict file of assertions. The assertions are the proof, and the video lets a human check them without rerunning anything.

`$OUT` is `${BMO_EVIDENCE_DIR:-$HOME/bmo-evidence}/<repo>/<pr-branch-slug>`. It holds the scenario, its helpers, and every run's output, and it stays outside git. Name it after the PR branch, not the current checkout, because step 4 checks out other commits.

## 1. Preflight

From the checkout that runs the app, run:

```bash
node "$SKILLS_DIR/bmo-record-evidence/record.mjs" --check --out "$OUT" [--base-url <url>] [--scenario "$OUT/scenario.json"]
```

It always exits `0`. Each line is `ok` or `missing`, and each missing line says what happens without it. The last line is the verdict:

- `recording: ready` — go on.
- `recording: blocked` — the app is down, a secret is unset, or `$OUT` isn't writable. Fix that line and run the check again.
- `recording: skipped` — Playwright or its Chromium is missing. Write `- **Recording:** Skipped — <missing line>` under `## Evidence`, put the line's install hint in the chat summary, and end this skill. A caller such as `bmo-pr` treats that as done and carries on.

A missing `ffmpeg` or upload path never stops the run: videos stay `.webm`, or the media stays in `$OUT` and the PR gets the `Skipped` line from `attach-media.md`.

Run it once without `--scenario` before step 3, and again with it before step 4.

**Done:** The verdict is `ready`, or a `Skipped` line is recorded.

## 2. Pick the mode and observables

| Change | Mode | Done when |
|---|---|---|
| Bug or security fix | **red → green** | Before: at least one assertion fails. After: every assertion passes. |
| Feature, new surface | **after-only** | After: every assertion passes. Before is not run. |
| Refactor, migration, dependency bump | **parity** | Both sides pass every assertion, and each `run` step prints the same output on both sides. |
| Visual-only change (layout, copy, styles) | **stills** | Both sides have their screenshots. Use `--video off` unless the change involves interaction. |

Pick observables a reviewer would trust without reading the code: a DB row, a response status, a CLI's exit code and output, text on screen, a log line.

**Done:** The mode is recorded, and every observable has a matching `assert` or `screenshot` step.

## 3. Write the scenario

Write `scenario.json` and its helper files to `$OUT`. The format is in [`scenario-format.md`](scenario-format.md). Read the repo's own seed scripts, fixtures, and test personas, and reuse them.

- Every value on screen ends up in the PR, so seed only synthetic data.
- Log in as a user that exists only for evidence. See [Logins](#logins).
- Make `setup` reset state before it seeds, so both sides start from the same state. Touch only rows the scenario created.

**Done:** A run on the PR commit with `--video off` reaches the last step and produces the verdicts the mode expects for **after**.

## 4. Run both sides, one after the other

Both sides use the same checkout and the same running app. Start with a clean working tree (`git status --porcelain` prints nothing); otherwise stop and ask the user. Note the current commit so you can return to it.

1. Check out the **before** commit: the merge-base with `<base>` for an open PR, or the merge commit's first parent (`'<merge>^1'`, quoted for zsh) for a merged one.
2. Wait for the app to serve that commit. A dev server reloads on its own; restart it when dependencies changed. When the PR changes the DB schema, run the repo's migrate step for this commit.
3. Run the side:

   ```bash
   node "$SKILLS_DIR/bmo-record-evidence/record.mjs" --scenario "$OUT/scenario.json" \
     --side before --base-url "$APP_URL" --out "$OUT"
   ```

4. Check out the **after** commit (the PR head, or the merge commit) and repeat steps 2 and 3 with `--side after`.
5. Check out the commit you noted at the start.

`--base-url` is only needed when the scenario has browser steps. Each run converts its video to MP4 when `ffmpeg` is available and rebuilds `$OUT/index.html`, which shows both sides next to each other.

**Done:** Every side the mode needs has its `<side>.json` plus its video or stills, and the verdicts match the mode's done line. When they don't, first confirm the app was serving the right commit. Then report it as a finding: give the step that differed and its output, and stop. Do not edit the scenario until it passes.

## 5. Add it to the PR

1. Under `## Evidence`, write one line per side with its counts, for example `**Before:** 1 of 3 assertions failed · **After:** 3 of 3 passed`. Put the media under those lines.
2. Upload the media with [`../bmo-pr/attach-media.md`](../bmo-pr/attach-media.md).

When the user only wants to review the evidence (for example, on a merged PR), skip this step and give them the path to `$OUT/index.html`.

**Done:** `attach-media.md` reached its done line and the counts in the PR match the JSON files, or the user has the `index.html` path.

## Logins

The runner reads passwords only from env vars named in the scenario's `secrets`, and masks them everywhere.

- **Local auth (an emulator or a local user table):** create a dedicated evidence user through the emulator's or the app's admin API, with a random password, plus whatever DB rows the app needs for that user. That password unlocks nothing outside this machine, so the agent may hold it: write `export <NAME>=<password>` to `$OUT/local-user.env` with mode `600`, `source` it before each run, and list `<NAME>` in `secrets`. The agent runs both sides itself.
- **A real secret (a shared persona, staging, any remote login):** when the env var is already set in the agent's shell, run as usual. Otherwise hand the user the step 4 command for each side to run in their own terminal, wrapped in their secret manager if they use one (for example `op run --env-file="$OUT/secrets.env" -- node …` with 1Password), then read the `<side>.json` files they produce. Files in `$OUT` hold references only, never values.

**Done:** No real secret value appears in the chat, in the scenario, or in `$OUT`.
