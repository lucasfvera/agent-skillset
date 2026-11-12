---
name: bmo-teach
description: Scaffolds an offline, hands-on learning repository for any technical topic across sprint, portfolio, and TDD kata tracks.
disable-model-invocation: true
argument-hint: "[topic, tools, or learning goal]"
---

# bmo-teach

Build a self-contained, hands-on learning repository calibrated to the learner's real starting point, grounded in current releases and official documentation, and runnable offline.

## Leading words

Hold these five tokens across every step and track:

- **`standalone`** — Written for a stranger cloning the public repository cold on any laptop: runs offline after one-time install, requires zero cloud accounts or active AI sessions, and carries zero chat-history assumptions or local identity leaks.
- **`parallel domain`** — Teaching prose and runnable `examples/` demonstrate patterns in an adjacent domain (e.g., `Customer`/`Order`), while learner exercises target a separate domain (`User`/`Post`) so solving requires transferring the concept.
- **`red stub`** — Learner exercises start stubbed (`TODO` / `Not implemented`) and fail `red` against an automated verifier until implemented; working references live separately (`examples/` or `solution`) so the harness itself is proven `green`.
- **`doc pointer`** — Pair a 1–3 sentence explanation (what it does + what bug or bottleneck it solves) and a compact snippet with a **`Go deeper:`** link to the version-pinned official guide and API `#anchor`, naming the related options or edge cases on that page.
- **`native CLI`** — Pair high-level library/SDK calls with direct inspection in the underlying system's native CLI, compiler, or inspector (`psql`, `redis-cli`, `curl`, `EXPLAIN`, DevTools) against the default namespace so raw commands match library state out of the box.

---

## Workflow

Execute Steps 1 through 5 in order.

### Step 1 — Calibrate scope

Inspect `$ARGUMENTS` (and the target directory if revising an existing repo). Identify which of these four inputs remain open:

1. **Learner baseline**: What the learner already knows vs. has never used (sets where Module 1 opens).
2. **Track selection** (offer all three by default, or any subset):
   - **Sprint (~2–3h)**: Progressive concept $\rightarrow$ `native CLI` $\rightarrow$ `red stub` exercise modules for fast fluency and interviews.
   - **Portfolio (1–2 days)**: Milestone-by-milestone guide where the learner builds a production-grade domain engine from `red stub`s; propose 2–3 concrete domains where the stack's guarantees matter and note that unfamiliar domain concepts will be explained from scratch.
   - **Katas (~3–4h)**: Test-driven `Red -> Green -> Refactor` drills with swappable reference solutions.
3. **Stack & test runner**: Language, library/runtime, test framework, and whether external services run via Docker Compose or in-process.
4. **Target path**: Directory where the repository will live (e.g., `~/learning/<topic-slug>`).

Ask concise questions for only the undecided items in a single turn, then **stop and wait** before Step 2.

**Completion criterion:** Target path, learner baseline, selected track(s) (plus chosen domain when Portfolio is included), and stack/test runner are explicitly confirmed by the user.

### Step 2 — Ground in current releases and official docs

Search live official release notes and documentation as of today's date before writing config, code, or prose:

1. Verify **current stable versions** of every runtime, library, test runner, and container image in the stack.
2. Catalog **paradigm shifts** from older major versions (deprecated APIs, replaced config files, architectural changes still common in older repos and articles). Place legacy-vs-modern contrasts in a late module *after* teaching the current workflow from scratch.
3. Record **version-pinned official documentation base URLs** (e.g., `/v7/` or `/18/`) whenever unversioned paths redirect to newer or incompatible releases.

**Completion criterion:** Current stable versions, major shifts from prior versions, and version-pinned official doc base URLs are verified against live upstream sources.

### Step 3 — Scaffold the `standalone` workspace

Create the shared root layout:

1. Write root `README.md` (Mermaid track-chooser diagram, track summary table, prerequisites, and offline quickstart per track), `.gitignore`, and `.env.example`.
2. When the stack uses external daemons (databases, brokers, caches), write one root `docker-compose.yml` pinned to current major image tags and provide localhost fallback defaults in config loaders so commands work immediately on clone. Use in-process toolchains directly when external daemons add no value.
3. **Default namespace alignment**: Bind the primary onboarding track (Sprint, or a single-track repo) to the service's **default database/schema/namespace** so opening the `native CLI` displays the learner's tables/keys/streams immediately without extra flags. Isolate additional tracks (`portfolio`, `katas`) in separate schemas, databases, or key prefixes so tracks coexist cleanly.

**Completion criterion:** Root `README.md`, `.gitignore`, `.env.example`, and any required service manifest exist on disk; external services (if any) are running and reachable via `native CLI` against the default namespace.

### Step 4 — Author selected tracks

Read only the reference file(s) for the track(s) selected in Step 1, applying every rule in [Teaching & prose rules](#teaching--prose-rules):

- **Sprint** ([`references/sprint.md`](references/sprint.md)) — 4–6 progressive modules with `parallel domain` lessons, `native CLI` tasks, `red stub` exercises, `check:N` verifiers, runnable `examples/`, cheatsheet, and interview Q&A. Read when building or updating the sprint track.
- **Portfolio** ([`references/portfolio.md`](references/portfolio.md)) — plain-English domain primer + 4–6 incremental build milestones (`red stub` layers verified by `test:m1`..`test:mN`, isolated `test:reference`, and portfolio cleanup/extension steps). Read when building or updating the portfolio track.
- **Katas** ([`references/katas.md`](references/katas.md)) — 5–8 self-contained `Red -> Green -> Refactor` challenges with per-kata mental models, `red stub` challenges, idiomatic solutions, and a zero-edit `test:solutions` swap. Read when building or updating the kata track.

**Completion criterion:** Every selected track satisfies the completion criterion in its reference file and every rule in [Teaching & prose rules](#teaching--prose-rules).

### Step 5 — Prove execution, links, and portable hygiene

Run all five checks in shell before handoff:

1. **Green paths**: Run install, schema/setup scripts, sprint `examples/`, portfolio `test:reference`, and kata `test:solutions`; every command exits `0`.
2. **`Red stub` proof**: Run learner check/test commands against untouched stubs; confirm every stub fails `red` (re-throwing `TODO` / `Not implemented` markers before catching expected domain errors or rollbacks).
3. **`Native CLI` parity**: Execute documented `native CLI` commands verbatim and confirm live output matches what the README promises.
4. **`Doc pointer` verification**: Fetch every external `https://` URL in authored Markdown; verify HTTP `200`, confirm version-pinned URLs stay on the target version path, and verify every `#anchor` fragment matches an `id` or `name` in the target HTML.
5. **Portable repo audit**: Scan tracked and unignored files (plus repo-local `git config` when committing) to verify public placeholders (`alice@example.com`, `localhost`), `.gitignore` exclusion of `.env` and proxy-tainted lockfiles when an internal registry mirror is active, and zero personal emails, hostnames, secrets, or machine-specific absolute paths.

**Completion criterion:** All five shell checks pass with zero unresolved failures; report a concise summary of created tracks, verified versions, and run commands.

---

## Teaching & prose rules

Apply across every Markdown file, exercise prompt, and code comment:

1. **Bridge from the baseline**: Introduce each new abstraction by contrasting it with the concrete baseline equivalent the learner already knows (e.g., raw SQL statement, HTTP request, or manual loop) before teaching tool-specific options.
2. **Match structural shapes in the `parallel domain`**: When an exercise asks the learner to transform arrays, handle nullable fields, or compose nested inputs, demonstrate that same data shape in the `parallel domain` snippet paired with its `doc pointer`.
3. **Diagram multi-part structure**: Use ASCII headings and Mermaid diagrams (`erDiagram`, `flowchart`, `sequenceDiagram`, `stateDiagram-v2`) whenever relationships, data flows, concurrency races, or state transitions cross boundaries; quote node labels containing parentheses or punctuation.
4. **Call out first-5-minute CLI traps**: Beside the `native CLI` launch command, document the 1–2 concrete traps newcomers hit immediately (identifier case-folding/quoting, verifying the active database/context prompt, distinguishing shell commands from REPL meta-commands).
5. **Plain engineering register**: Write direct declarative sentences with plain verbs (`read`, `lock`, `index`, `verify`) and exact domain nouns. State directly what each tool does rather than framing prose around rhetorical contrasts, hype adjectives, or emojis.
