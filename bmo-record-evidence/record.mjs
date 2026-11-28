#!/usr/bin/env node
// Runs one side of a bmo-record-evidence scenario: a video (and any stills) plus a verdict file.
// Usage: node record.mjs --scenario <file.json> --side before|after --out <dir> [--base-url <url>] [--video off] [--channel chrome]
//        node record.mjs --check [--out <dir>] [--base-url <url>] [--scenario <file.json>]
// Run it from the checkout under test: Playwright resolves from there first, then from global installs.
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { readFileSync, writeFileSync, renameSync, mkdirSync, rmSync, existsSync, accessSync, constants } from 'node:fs';
import { dirname, resolve, join, basename } from 'node:path';

const argv = process.argv.slice(2);
const args = {};
for (let i = 0; i < argv.length; i++) {
  const key = argv[i].replace(/^--/, '');
  const next = argv[i + 1];
  if (next === undefined || next.startsWith('--')) args[key] = true;
  else (args[key] = next), i++;
}
function fail(msg, code = 1) {
  console.error(`record.mjs: ${msg}`);
  process.exit(code);
}

// Finds a binary on PATH, then in the usual Homebrew folders (a shell started before an install may miss them).
function which(name) {
  const r = spawnSync('sh', ['-c', `command -v ${name}`], { encoding: 'utf8' });
  if (r.status === 0 && r.stdout.trim()) return r.stdout.trim();
  return ['/opt/homebrew/bin', '/usr/local/bin'].map((d) => join(d, name)).find((f) => existsSync(f)) ?? null;
}

function findPlaywright() {
  const bases = [join(process.cwd(), 'noop.js'), import.meta.url];
  const globalRoot = spawnSync('npm', ['root', '-g'], { encoding: 'utf8' }).stdout?.trim();
  if (globalRoot) bases.push(join(globalRoot, 'noop.js'));
  for (const base of bases) {
    for (const name of ['playwright', 'playwright-core', '@playwright/test']) {
      try {
        return createRequire(base)(name);
      } catch {}
    }
  }
  return null;
}
function loadPlaywright() {
  // Exit 3 = capture tool unavailable; the skill records "Skipped" and suggests an install.
  return findPlaywright() ?? fail('Playwright not found in this checkout or globally', 3);
}

// Preflight: reports every piece the run and the PR upload need, with what happens when one is missing.
// It never fails the caller: it always exits 0 and ends with `recording: ready`, `blocked` (fixable now), or `skipped`.
async function preflight() {
  const lines = [];
  let toolMissing = false;
  let runBlocked = false;
  // kind: 'tool' (missing → Skipped), 'run' (missing → fix it, then run), 'degrade' (missing → a fallback, run anyway).
  const report = (ok, item, ifMissing, kind = 'degrade') => {
    if (!ok && kind === 'tool') toolMissing = true;
    if (!ok && kind === 'run') runBlocked = true;
    lines.push(`${ok ? 'ok     ' : 'missing'} ${item}${ok ? '' : ` — ${ifMissing}`}`);
  };
  const pw = findPlaywright();
  report(pw, 'Playwright', 'recording is Skipped; suggest agent-browser, or `npm i -D playwright && npx playwright install chromium ffmpeg`', 'tool');
  if (pw && !args.channel) {
    let exe = null;
    try {
      exe = pw.chromium.executablePath();
    } catch {}
    report(exe && existsSync(exe), 'Chromium for Playwright', 'recording is Skipped; run `npx playwright install chromium`', 'tool');
  }
  report(which('ffmpeg'), 'ffmpeg', 'videos stay .webm (GitHub may not play them inline)');
  const gh = which('gh');
  let upload = null;
  if (gh) {
    const authed = spawnSync(gh, ['auth', 'status'], { encoding: 'utf8' }).status === 0;
    const attach = (spawnSync(gh, ['pr', 'create', '--help'], { encoding: 'utf8' }).stdout ?? '').includes('--attach');
    const image = (spawnSync(gh, ['extension', 'list'], { encoding: 'utf8' }).stdout ?? '').includes('gh-image');
    if (authed && attach) upload = 'gh --attach';
    else if (authed && image) upload = 'gh image';
  }
  report(upload, `PR upload path${upload ? ` (${upload})` : ''}`, 'media stays in the output folder; the PR gets a Skipped line (see bmo-pr/attach-media.md)');
  if (args.out && args.out !== true) {
    let writable = false;
    try {
      mkdirSync(resolve(args.out), { recursive: true });
      accessSync(resolve(args.out), constants.W_OK);
      writable = true;
    } catch {}
    report(writable, `output folder ${resolve(args.out)}`, 'pick another --out or set BMO_EVIDENCE_DIR', 'run');
  }
  if (args['base-url'] && args['base-url'] !== true) {
    let up = false;
    try {
      up = (await fetch(args['base-url'], { signal: AbortSignal.timeout(15000) })).status < 500;
    } catch {}
    report(up, `app at ${args['base-url']}`, 'browser steps will fail; start the app first', 'run');
  }
  if (args.scenario && args.scenario !== true) {
    const names = JSON.parse(readFileSync(resolve(args.scenario), 'utf8')).secrets ?? [];
    const absent = names.filter((n) => !process.env[n]);
    report(!absent.length, `secrets (${names.length})`, `the run stops with exit 4; set ${absent.join(', ')}`, 'run');
  }
  const verdict = toolMissing ? 'skipped' : runBlocked ? 'blocked' : 'ready';
  console.log([...lines, `recording: ${verdict}`].join('\n'));
  process.exit(0);
}

if (args.check) await preflight();
for (const k of ['scenario', 'side', 'out']) if (!args[k]) fail(`missing --${k}`);

const scenarioPath = resolve(args.scenario);
const scenarioDir = dirname(scenarioPath);
const scenario = JSON.parse(readFileSync(scenarioPath, 'utf8'));
const out = resolve(args.out);
const side = args.side;
const recordVideo = args.video !== 'off';
mkdirSync(out, { recursive: true });

// Secrets come only from the environment; every secret value is masked wherever it would be shown.
const secretNames = scenario.secrets ?? [];
const missing = secretNames.filter((n) => !process.env[n]);
if (missing.length) fail(`missing secret env vars: ${missing.join(', ')}`, 4);
const secretValues = secretNames.map((n) => process.env[n]).filter((v) => v.length >= 4);
const maskPatterns = [/eyJ[\w-]+\.[\w-]+\.[\w-]*/g, ...(scenario.mask ?? []).map((p) => new RegExp(p, 'g'))];
const mask = (input) => {
  let s = typeof input === 'string' ? input : JSON.stringify(input);
  for (const v of secretValues) s = s.split(v).join('•••');
  for (const p of maskPatterns) s = s.replace(p, '•••');
  return s;
};

const sh = (cmd) => {
  const r = spawnSync(cmd, { shell: true, cwd: scenarioDir, encoding: 'utf8', env: process.env });
  return { code: r.status, stdout: (r.stdout ?? '').trim(), stderr: (r.stderr ?? '').trim() };
};
for (const cmd of [].concat(scenario.setup ?? [])) {
  const r = sh(cmd);
  if (r.code !== 0) fail(`setup failed (${r.code}): ${mask(cmd)}\n${mask(r.stderr)}`);
}

const check = (expr, scope) => {
  if (!expr) return undefined;
  try {
    return Boolean(new Function(...Object.keys(scope), `return (${expr});`)(...Object.values(scope)));
  } catch {
    return false;
  }
};
const asRows = (text) => {
  try {
    const v = JSON.parse(text);
    if (Array.isArray(v) && v.every((r) => r && typeof r === 'object' && !Array.isArray(r))) return v;
  } catch {}
  return undefined;
};

const { chromium } = loadPlaywright();
// The app keeps `viewport`; the panel gets its own column to the right, so it never covers the app.
const appViewport = scenario.viewport ?? { width: 1600, height: 900 };
const PANEL = 480;
const viewport = { width: appViewport.width + PANEL, height: appViewport.height };
const browser = await chromium.launch({ channel: args.channel });
const context = await browser.newContext({
  viewport,
  ...(recordVideo ? { recordVideo: { dir: out, size: viewport } } : {}),
});
const page = await context.newPage();
// A blank stage keeps the run on video when a scenario has no browser steps (CLI, API, data changes).
await page.setContent('<!doctype html><html><body style="margin:0;background:#161b22"></body></html>');

const panel = [];
const results = [];
const stills = [];
const captured = {};
const add = (entry) => {
  panel.push(entry);
  if (entry.ok !== undefined) results.push({ step: entry.label, ok: entry.ok });
};

// The panel is redrawn after every step so it survives navigations. Full width on the blank stage.
const render = () =>
  page
    .evaluate(
      ({ entries, title, side, appWidth }) => {
        const esc = (s) => String(s ?? '').replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[c]);
        const badge = (ok) =>
          ok === undefined ? '' : ok ? ' <b style="color:#3fb950">PASS</b>' : ' <b style="color:#f85149">FAIL</b>';
        let el = document.getElementById('__evidence');
        if (!el) {
          el = document.createElement('div');
          el.id = '__evidence';
          document.documentElement.appendChild(el);
        }
        const stage = location.href === 'about:blank';
        if (!stage) document.documentElement.style.setProperty('width', `${appWidth}px`);
        el.style.cssText = `pointer-events:none;position:fixed;top:0;right:0;width:${stage ? '100vw' : `calc(100vw - ${appWidth}px)`};height:100vh;overflow:auto;z-index:2147483647;background:#0d1117;border-left:1px solid #30363d;color:#e6edf3;font:13px/1.45 ui-monospace,monospace;padding:14px;box-sizing:border-box`;
        const cell = 'border:1px solid #30363d;padding:2px 6px;text-align:left;color:#e6edf3;font:inherit';
        el.innerHTML =
          `<div style="font-size:15px;font-weight:bold">${esc(title)} · <span style="color:${side === 'before' ? '#d29922' : '#58a6ff'}">${side.toUpperCase()}</span></div>` +
          entries
            .map((e) => {
              const head = `<div style="margin-top:12px;color:#8b949e">${esc(e.kind)} · ${esc(e.label)}${badge(e.ok)}</div>`;
              if (e.rows) {
                const cols = [...new Set(e.rows.flatMap((r) => Object.keys(r)))];
                if (!cols.length) return `${head}<div>(no rows)</div>`;
                return `${head}<table style="border-collapse:collapse;margin-top:4px"><tr>${cols.map((c) => `<th style="${cell}">${esc(c)}</th>`).join('')}</tr>${e.rows.map((r) => `<tr>${cols.map((c) => `<td style="${cell}">${esc(typeof r[c] === 'object' ? JSON.stringify(r[c]) : r[c])}</td>`).join('')}</tr>`).join('')}</table>`;
              }
              return `${head}${e.detail ? `<pre style="white-space:pre-wrap;margin:4px 0">${esc(e.detail)}</pre>` : ''}`;
            })
            .join('');
        el.scrollTop = el.scrollHeight;
      },
      { entries: panel, title: scenario.title, side, appWidth: appViewport.width },
    )
    .catch(() => {});

const url = (path) => {
  if (!args['base-url']) throw new Error('a browser step needs --base-url');
  return new URL(path, args['base-url']).href;
};
const matches = (req, m = {}) =>
  (!m.method || req.method() === m.method.toUpperCase()) &&
  (!m.urlIncludes || req.url().includes(m.urlIncludes)) &&
  (!m.header || req.headers()[m.header.toLowerCase()] !== undefined);

let aborted = null;
for (const step of scenario.steps) {
  try {
  if (step.note) add({ kind: 'note', label: step.note });
  else if (step.goto) {
    await page.goto(url(step.goto), { waitUntil: 'networkidle' });
    add({ kind: 'goto', label: step.goto });
  } else if (step.fill) {
    const value = step.secret ? process.env[step.secret] : step.value;
    if (step.secret && !secretNames.includes(step.secret)) throw new Error(`secret ${step.secret} is not declared in "secrets"`);
    await page.fill(step.fill, value ?? '');
    add({ kind: 'fill', label: `${step.fill} = ${step.secret ? '•••' : mask(value)}` });
  } else if (step.capture) {
    // DevTools "Copy as fetch": save the next request that matches, triggered by an optional click.
    const pending = page.waitForRequest((r) => matches(r, step.match));
    if (step.click) await page.click(step.click);
    const r = await pending;
    captured[step.capture] = { url: r.url(), method: r.method(), headers: r.headers(), body: r.postData() };
    add({ kind: 'capture', label: `${step.capture} ${r.method()} ${new URL(r.url()).pathname}`, detail: mask(r.postData() ?? '') });
  } else if (step.click) {
    await page.click(step.click);
    if (step.waitFor) await page.waitForURL((u) => u.href.includes(step.waitFor));
    else await page.waitForLoadState('networkidle').catch(() => {});
    add({ kind: 'click', label: step.click });
  } else if (step.press) {
    await (step.on ? page.press(step.on, step.press) : page.keyboard.press(step.press));
    add({ kind: 'press', label: step.press });
  } else if (step.screenshot) {
    await page.evaluate(() => document.getElementById('__evidence')?.remove());
    const file = join(out, `${step.screenshot}-${side}.png`);
    await page.screenshot({ path: file, fullPage: Boolean(step.fullPage), clip: step.fullPage ? undefined : { x: 0, y: 0, ...appViewport } });
    stills.push(file);
    add({ kind: 'screenshot', label: step.screenshot });
  } else if (step.replay) {
    // Console paste: re-send a captured request from inside the page with one field changed.
    const c = captured[step.replay];
    if (!c) throw new Error(`replay of uncaptured request ${step.replay}`);
    let body = c.body;
    try {
      body = JSON.parse(c.body);
    } catch {}
    if (step.edit) body = new Function('body', `${step.edit}; return body;`)(body);
    const sent = typeof body === 'string' ? body : JSON.stringify(body);
    const { status, text } = await page.evaluate(
      async ({ url, method, headers, body }) => {
        const res = await fetch(url, { method, headers, body });
        return { status: res.status, text: await res.text() };
      },
      { url: c.url, method: c.method, headers: c.headers, body: sent },
    );
    add({
      kind: 'console',
      label: `replay ${step.replay} → ${status}`,
      detail: `body: ${mask(sent)}\nresponse: ${mask(text.slice(0, 400))}`,
      ok: check(step.assert, { status, text }),
    });
  } else if (step.eval) {
    const value = await page.evaluate(step.eval);
    add({ kind: 'console', label: mask(step.eval), detail: mask(value ?? 'undefined'), ok: check(step.assert, { value }) });
  } else if (step.run) {
    // Any command: a DB query, a CLI, curl, a log tail. JSON-array output renders as a table.
    const r = sh(step.run);
    const rows = asRows(r.stdout);
    add({
      kind: 'run',
      label: step.label ?? mask(step.run),
      rows,
      detail: rows ? undefined : mask([r.stdout, r.stderr].filter(Boolean).join('\n').slice(0, 1500) || `(exit ${r.code})`),
      ok: check(step.assert, { code: r.code, stdout: r.stdout, stderr: r.stderr, rows }),
    });
  } else throw new Error(`unknown step: ${JSON.stringify(step)}`);
  } catch (e) {
    // A broken step still yields a video and a verdict file, so the failure can be reviewed.
    aborted = { step: JSON.parse(mask(JSON.stringify(step))), error: mask(String(e.message ?? e)).split('\n')[0] };
    add({ kind: 'error', label: aborted.error, ok: false });
  }
  await render();
  await page.waitForTimeout(aborted ? 3000 : step.pauseMs ?? 1200);
  if (aborted) break;
}
await page.waitForTimeout(2000);

const video = recordVideo ? page.video() : null;
await context.close();
await browser.close();
let videoFile = null;
if (video) {
  const webm = join(out, `${side}.webm`);
  rmSync(webm, { force: true });
  renameSync(await video.path(), webm);
  videoFile = webm;
  // MP4 plays inline on GitHub; keep the .webm only when the conversion is not possible.
  const ffmpeg = which('ffmpeg');
  if (ffmpeg) {
    const mp4 = join(out, `${side}.mp4`);
    const r = spawnSync(ffmpeg, ['-loglevel', 'error', '-y', '-i', webm, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', mp4]);
    if (r.status === 0) {
      rmSync(webm);
      videoFile = mp4;
    }
  }
}
for (const cmd of [].concat(scenario.teardown ?? [])) sh(cmd);

const summary = { side, passed: results.filter((r) => r.ok).length, total: results.length, aborted, results, video: videoFile, stills };
writeFileSync(join(out, `${side}.json`), JSON.stringify(summary, null, 2));

// index.html: both sides next to each other, rebuilt after every run from whatever <side>.json files exist.
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const column = (name) => {
  const f = join(out, `${name}.json`);
  if (!existsSync(f)) return `<section><h2>${name}</h2><p class="muted">Not recorded.</p></section>`;
  const s = JSON.parse(readFileSync(f, 'utf8'));
  const media = s.video ? `<video src="${esc(basename(s.video))}" controls muted playsinline></video>` : '';
  const shots = (s.stills ?? []).map((p) => `<img src="${esc(basename(p))}" alt="${esc(basename(p))}">`).join('');
  const rows = s.results.map((r) => `<li class="${r.ok ? 'pass' : 'fail'}">${r.ok ? 'PASS' : 'FAIL'} · ${esc(r.step)}</li>`).join('');
  const verdict = s.aborted ? `Aborted: ${esc(s.aborted.error)}` : `${s.passed} of ${s.total} assertions passed`;
  return `<section><h2>${name}</h2><p>${verdict}</p>${media}${shots}<ul>${rows}</ul></section>`;
};
writeFileSync(
  join(out, 'index.html'),
  `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(scenario.title)}</title>
<style>:root{color-scheme:light dark}body{margin:0;padding:16px;font:14px/1.5 system-ui,sans-serif;background:Canvas;color:CanvasText}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr));gap:16px}video,img{width:100%;border:1px solid #8884;border-radius:6px;margin-bottom:8px}
ul{padding-left:0;list-style:none}.pass{color:#1a7f37}.fail{color:#cf222e}.muted{opacity:.6}h2{text-transform:capitalize;margin:0 0 4px}</style>
<h1>${esc(scenario.title)}</h1><main>${column('before')}${column('after')}</main>`,
);
console.log(`${side}: ${aborted ? `ABORTED at ${aborted.error} · ` : ''}${summary.passed}/${summary.total} assertions passed${videoFile ? ` · ${videoFile}` : ''}${stills.length ? ` · ${stills.length} still(s)` : ''} · ${join(out, 'index.html')}`);
