---
name: step-deliver
description: Use when the user wants agent work delivered with clear scope, verification, runnable commands, and a human review checklist—prefer per-file “what to review” prompts (intent, contracts, risks), not only generic categories. When the user attaches this skill alongside a multi-unit plan (U1/U2/… or explicit numbered steps), default to sliced delivery with a pause between units unless the user explicitly opts into single-pass.
---

# Step-deliver

This skill defines a **delivery standard** for agent work: outcomes are **easy to review**, **easy to validate**, and **easy to roll back** when something goes wrong.

**Core outcomes (always):**

- Clear **scope** and boundaries (what changed, what did not).
- **Verification**: the narrowest proof that the change is sound.
- **How to run**: copy-paste commands or an honest “cannot run here” narrative.
- **Review handoff**: paths, intent, contracts, and risks—without rereading the chat.

**Slicing is optional for tiny work, but not optional for plan-shaped work.** If the user provides (or references) a plan with multiple implementation units, treat those units as **review seams** by default: implement **one unit**, verify, hand off, then **pause** for confirmation before starting the next unit—unless the user explicitly requests single-pass mode.

For genuinely small, single-boundary work, do **one unit of work** and spend effort on verification and the review handoff—not artificial intermediate commits.

---

## When to use this skill

Use it when the user wants **structured delivery**: explicit verification, reviewer-oriented explanation, or paced steps.

Typical triggers:

- The user asks to proceed in **steps**, **slices**, or to **pause for confirmation**.
- The change touches **multiple files**, **layers** (API, persistence, UI), or **ordering matters** (migrate before code, flag before rollout).
- The user wants **runnable verification** and **what to review** spelled out.
- The task is **ambiguous or large** and benefits from clear boundaries—even if those boundaries fit in one PR.

**Do not treat “small” as incompatible with this skill.** A one-file fix still benefits from verification + review handoff.

---

## Choose a mode

Pick one at the start (explicitly or implicitly):

### A) Single-pass mode (default only when the work is truly one boundary)

One scoped change → verify → review handoff.  
No mandatory pause unless the user asked for one.

Use single-pass when **all** of the following are true:

- The user did **not** attach a multi-unit plan (no `U1`/`U2`/… style units, no explicit “Step 1/2/3”, no phased checklist), **or** the user explicitly opts in with language like **“single PR”**, **“one shot”**, **“don’t pause”**.
- The change is **one reviewable concern** (one subsystem, one contract surface, one failure domain) and reviewers can reason about the diff without a forced seam.

### B) Sliced mode (default when a plan already names multiple units)

Multiple **units of work**, each shippable: builds, tests that apply stay green, repo stays coherent.

**Default to sliced mode** when **any** of the following is true:

- The user invokes **`/bmo-step-deliver`** **and** the task is backed by a plan with **2+ implementation units** (`U1`, `U2`, …) or explicit numbered phases/steps.
- The change spans **multiple independent failure domains** (DB + API + client, proto + generated + handlers, bootstrap + docs + tests).
- There is a natural **rollback seam** between steps (delete public surface → adjust bootstrap/config → update docs/tests).
- Reviewers would otherwise face one **unreviewable** diff.
- The user asked for **step-by-step** delivery.

**Do not slice** when the change is already small, or splitting would create **incoherent intermediate states** just to satisfy a process.

**Anti-pattern to avoid:** collapsing a multi-unit plan into one mega-change **solely** because it is faster for the agent. Speed is not a substitute for reviewability when the plan already promised seams.

---

## Operating principles

1. **Scope before volume** — Deliver the smallest coherent outcome; avoid drive-by refactors.

2. **Verification over narration** — If a command can prove correctness, run it (or say precisely what blocked it).

3. **Correct workspace** — Commands must run against the **intended repo root**. In automation or multi-root workspaces, confirm cwd (e.g. `pwd`) or use **`yarn --cwd "<absolute-path>" <script>`** so verification is not silently running in the wrong package.

4. **Stop at boundaries** — End each unit at a natural checkpoint: passing tests, typecheck, or a documented “nothing runnable yet” milestone.

5. **No surprise scope** — If the user expands the task mid-flight, align scope before continuing (especially in sliced mode).

---

## The loop (single-pass or per slice)

Repeat until the agreed scope is done.

### 1) Align scope

State in one short paragraph:

- What this **unit of work** delivers.
- What is **explicitly out of scope** (including other repos, callers, or follow-ups).

If the repository documents architecture or testing conventions, read what applies before editing (example: monorepo `docs/architecture.md` when the change is architectural).

### 2) Implement

Stay within scope. Avoid unrelated cleanup unless the user asked or it blocks the change.

### 3) Verify

Pick the **narrowest meaningful proof**:

| Situation | Prefer |
|-----------|--------|
| Logic change | Focused unit tests |
| Types-only / imports | Typecheck |
| Formatting / lint rules | Lint |
| Integration-heavy path | Targeted integration test or scripted repro |
| Cannot run in agent env | Exact commands + prerequisites for the user |

**Codegen / generators:** If a step runs codegen (Protobuf, OpenAPI, GraphQL, etc.), treat output layout shifts as normal: run generation, then **search for broken imports** and fix call sites before declaring done.

**Stale generator caches:** If regenerated output still does not match the edited schema or proto (same RPCs/messages as before), the tool may be reading a **cached copy** instead of your latest files. Check the generator config for a **cache directory** (example: Protorox `cacheDir` / `.proto-cache`), delete the relevant cached artifact or clear the cache, regenerate, and **mention this in the review handoff** so reviewers know the checked-in generated files truly reflect the source.

**Tool output vs config:** If CLI warnings contradict expectations (e.g. a “generation” flag is a no-op), note it in the review handoff—config examples elsewhere may not match the installed tool version.

**Lockfiles / installs:** If `package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml` changes without an intentional dependency change in scope, **stop and classify**: accidental drift vs deliberate bump—do not silently ship unexplained lock churn.

### 4) Commit (only when requested or agreed)

When the user asks for a commit, follow repo conventions (see integration with `commit` skill).

If using sliced mode and the user did not ask to commit, you may still ask once whether to commit before the next slice—**not** required for single-pass mode.

### 5) Report “how to run” (required)

Always end with **A** or **B**:

**A) Runnable commands**

Copy-paste commands from the correct directory. Prefer the repo’s package manager (`yarn`, `pnpm`, `npm` as documented). State cwd when not repo root.

**B) Nothing runnable yet**

Short chronological narrative of what will run later (env setup → migrations → tests → teardown).

### 6) Review handoff for humans (required)

Make review fast: **where to look**, **what changed in intent**, **what could break in production**.

**Include every time:**

1. **Scope line** — One sentence: what this unit delivered and what was deferred (if anything).

2. **Files to review** — Bullets with **repo-relative paths**. Group by concern when many files repeat one theme.

3. **What to pay attention to** — Go beyond labels like “contracts” or “tests”: reviewers should not have to **guess what to grep for** or **which assumption might be wrong**.

**Minimum detail bar**

Each important file (or each logical group of tiny edits) should get at least **one concrete review prompt**—a sentence that tells the reviewer *what to verify* and *why it matters*, for example:

- **Intent** — What behavior or API shape changed here vs main?
- **Contract** — Which field, RPC, error code, or envelope changed? Backward compatible?
- **Failure mode** — What breaks if this file is wrong (wrong status code, silent data loss, security hole)?
- **Red flag** — What would look “off” in the diff (new coupling, duplicate logic, missing validation)?

If the diff is **multi-file or cross-layer** (proto + generated + handlers + tests + docs), prefer a **per-file (or per-group) subsection** instead of only top-level categories. Same information can be structured like:

```text
- path/to/foo.proto — RPC list and message fields match the product decision; enums cover NOT_FOUND (or explicit unknown).
- path/to/generated/… — Regenerated only; diff should mirror proto; no hand edits.
- path/to/grpc/foo.handler.ts — Thin adapter: validation, requestContext, mapping to service; errors mapped to proto enums.
```

Short bullets are fine; **vague** bullets (“check handler”) are not.

**Reviewer checklist categories (general)**

Use these as **axes**, then **instantiate** them with file-specific bullets above:

- **User-visible behavior** — UX copy, feature flags, defaults, error messages.
- **Contracts** — HTTP/gRPC/event payloads, schemas, versioning, backward compatibility.
- **Authorization / privacy** — Who can do what; PII in logs or responses.
- **Operational risk** — Deploy order, migrations, caches, async ordering (commit vs publish), idempotency, retries.
- **Tests** — What this change proves; what remains intentionally untested.

**Cross-cutting review prompts (use when relevant)**

- **Removing or narrowing a public surface** (RPC route, REST path, proto RPC, exported client): state **blast radius** (who consumed it), whether **callers outside this repo** must change, and whether the commit should carry **`BREAKING CHANGE`** (see **`commit`** skill).
- **Docs and manifests:** After changing scripts, entrypoints, env vars, or public APIs, cross-check **README**, **package scripts**, and **CI** so documented commands and tables match reality (no phantom scripts or stale “methods implemented today” lists).
- **Integration tests vs production ingress:** If tests **seed data via one path** (e.g. service or queue) but **assert another** (e.g. gRPC), say so explicitly so reviewers do not confuse **test setup** with **supported caller paths**.
- **Hooks vs changed paths:** If pre-commit or CI runs **lint/format only on part of the repo** (e.g. `src/` but not `tests/`), note it when your edits touch paths that hooks do not cover.

Optional bullets:

- **Compare with** — “Same pattern as `path/to/...`” when it speeds review.
- **Non-goals** — One line so reviewers do not flag intentional omissions.
- **Blast radius** — Public API, published packages, docs, or scripts outside this repo (when deletion or export paths change).

**Sliced migrations (optional pattern)**

For transport or API moves (e.g. Rabbit → gRPC), a coherent sequence often reduces risk: **centralize behavior in domain/service** → **extend contract + codegen** → **add adapters/handlers** → **integration tests** → **remove deprecated surface**. When using slices, say **which slice** you are in and **what must stay working** until the next slice lands.

### 7) Pause for confirmation (conditional)

Ask for a short token (e.g. `continue`) **only when**:

- Using **sliced mode** and more work remains, or
- The user explicitly asked for **pause between steps**.

In **sliced mode**, treat the pause as **part of the delivery**, not optional polish:

- After each unit: give the **review handoff** for *just that unit’s diff*, list **remaining units**, and ask for `continue` before editing further.
- If the user wants to compress slices, they must explicitly say so (e.g. “merge U2+U3”, “single-pass from here”).

Do **not** require a pause after every single-pass task.

---

## Failure handling

If verification fails:

- Fix inside the same unit if the fix is small and caused by this change.
- Otherwise stop, report the **smallest next action** (revert, narrower test, or scope split).

---

## Integration with other skills

- **`commit`** — When the user asks for a commit message or `/commit`, follow that skill’s format and conventions.
- **`bmo-sync-repo-documentation`** (or repo doc-sync equivalent) — After changing scripts, public APIs, or paths listed in onboarding docs, reconcile **README / manifests / CI** so the review handoff does not repeat stale commands (often paired with the **Docs and manifests** bullet above).
- **Planning** — If the task is large or ambiguous, propose planning mode before heavy implementation (whether sliced or not).
