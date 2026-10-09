# Record the clip

Destination `pr` never reads this file. Load after Sentiless verify passed (`local`, `email`, or `message`).

Adapt the copy-from named in sentiless.md. Write `scripts/record-<slug>-clip.ts` in Sentiless. Leave the USD-toggle script unchanged unless this take _is_ that feature.

## Output

```
~/roxom/internal-sentinel/clips/<slug>/
  <slug>.webm
  take.json
```

`take.json`: origins used (no emails), every briefed surface as a boolean clicked/opened, `recordedAt`, `slug`.

## Walk

Exercise every briefed surface, in list order.

1. `recordVideo` at 1440×900 (same as the copy-from).
2. Logged-in: Sentiless passkey helpers from the copy-from. Logged-out: a fresh context, no storage state.
3. Overlay via `addInitScript`; `attachCursor` after every `goto`.
4. Pointer is **slow** (`mouse.move` with high `steps`, ~900ms pause on the control).
5. **Camera:** when the pointer reaches the focus control, zoom in, do the click, zoom out so the chrome change reads at full frame. Same beat for the reverse click.
6. Rename the Playwright file to `<slug>.webm`.

Run from `~/roxom/internal-sentinel`:

```bash
bun run scripts/record-<slug>-clip.ts
```

**Completion criterion:** `<slug>.webm` exists on disk; `take.json` has a true/false field for every briefed surface (false is allowed; omitting the field is not).
