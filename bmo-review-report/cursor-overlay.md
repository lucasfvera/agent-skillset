# Cursor overlay — when writing or adapting a recorder

Playwright `recordVideo` does not capture the OS pointer. A clip with no visible mouse looks like the UI changing by itself. Inject a page-level SVG follower and drive `page.mouse.move` then click.

Read this only on the record branch, and only when writing or adapting a recorder. If you are running an existing script that already installs the overlay, skip this file.

Copy the init script from:

`/Users/lucasferreyravera/roxom/internal-sentinel/scripts/record-usd-toggle-demo.ts`

(`cursorInitScript`, `context.addInitScript`, `attachCursor` after navigations).

## Required behavior

- `addInitScript` so the overlay survives full navigations
- Re-attach after `goto` (SPA shells can wipe `documentElement` children)
- SVG pointer, `pointer-events: none`, `z-index` above chrome
- `page.mouse.move(x, y, { steps })` to the control, pause (~500ms), then `page.mouse.click`
- After click, pause (~1s) so the state change is readable in the webm
- HoverCard / popover: move onto the card and stay there; moving off closes it

**Completion criterion:** the recorder calls `addInitScript` with the follower, every click is preceded by `mouse.move` + pause, and a HoverCard walk does not click with the pointer off the card.
