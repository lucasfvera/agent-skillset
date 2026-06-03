---
name: bmo-step-deliver
description: Use when the user wants agent work delivered with clear scope, verification, runnable commands, and a structured human review digest (mandatory template: review blocks with absolute paths, block-level + per-file prompts, provenance/conventions). When the task is plan-shaped with multiple units (U1/U2/…, explicit numbered steps, or agreed slices), mandatory stop after each unit—full **review digest** (§6), then wait for the user to say continue (or equivalent) before implementing the next slice; do not batch slices in one turn unless the user explicitly opts into single-pass up front. Git commits require explicit approval per repository (or post–review-digest `continue` for that same repo’s slice); never commit repo B because the user asked to commit repo A then “continue” with work in B. Skipped scope-shaping questions block until re-ask or explicit defaults token; on continue, `/bmo-commit` the finished slice when applicable, then start the next unit only.
---

# Step-deliver

This skill defines a **delivery standard** for agent work: outcomes are **easy to review**, **easy to validate**, and **easy to roll back** when something goes wrong.

**Core outcomes (always):**

- Clear **scope** and boundaries (what changed, what did not).
- **Verification**: the narrowest proof that the change is sound.
- **How to run**: copy-paste commands or an honest “cannot run here” narrative.
- **Review digest** (mandatory structured section; see [§6 Review digest](#6-review-digest-mandatory-structure)): paths (absolute in multi-root), grouped blocks, block-level and per-file review prompts—including provenance, contracts, and repo conventions—so reviewers never need to ask “what format?” or “where did this come from?”

### Mandatory gate (plan-shaped / multi-slice work)

If the user invokes this skill **and** the work has **two or more** implementation units (named `U1`/`U2`/…, an attached plan with numbered phases, an agreed slice list, or explicit “step 1 / step 2”), you **must**:

1. Implement **exactly one** unit in that turn.
2. Verify it, deliver **how to run** (§5) then the **review digest** (§6)—see §6 for the preferred message order.
3. **Stop.** Do not open editors or run further implementation for the next unit in the same turn.
4. Wait until the user clearly signals the next unit—e.g. **`continue`**, **“next slice”**, **“proceed with U2”**—or explicitly authorizes **single-pass** / **“don’t pause”** for the rest of the plan.

**Hard rule:** Treat “finish the whole plan faster” as a **violation** of this skill when multiple units were named. Speed does not override the pause.

**Slicing is optional for tiny work** (one reviewable concern, no multi-unit plan): one scoped change → verify → hand off; no pause required unless the user asked for pacing—still invest in verification and concrete review prompts, not artificial intermediate commits.

---

## When to use this skill

Use it when the user wants **structured delivery**: explicit verification, reviewer-oriented explanation, or paced steps.

Typical triggers:

- The user asks to proceed in **steps**, **slices**, or to **pause for confirmation**.
- The change touches **multiple files**, **layers** (API, persistence, UI), or **ordering matters** (migrate before code, flag before rollout).
- The user wants **runnable verification** and **what to review** spelled out.
- The task is **ambiguous or large** and benefits from clear boundaries—even if those boundaries fit in one PR.

**Do not treat “small” as incompatible with this skill.** A one-file fix still benefits from verification + the §6 review digest (may be a single block with one file).

---

## Choose a mode

Pick one at the start (explicitly or implicitly). **Default:** if the attached work is **multi-unit**, you are in **sliced mode** (section B) with **mandatory** user `continue` between units unless the user has already opted into **single-pass** (section A).

### A) Single-pass mode (one unit, one turn—no multi-unit plan)

One scoped change → verify → review digest (§6).  
No pause between slices because there is **only one** coherent unit.

Use single-pass when **either**:

- **(Typical)** There is **no** multi-unit plan (no `U1`/`U2`/…, no numbered phased checklist the user asked you to execute step-by-step) **and** the work is **one reviewable concern** (one subsystem, one contract surface, one failure domain); **or**
- **(Explicit override)** The user gave a **multi-unit** plan **and** explicitly directed **single-pass** for it (e.g. **“single PR”**, **“one shot”**, **“don’t pause”**, **“implement the full plan in one go”**). State that opt-in once at the start of implementation.

Single-pass means one assistant turn may contain the full implementation **only** when the above applies; otherwise use sliced mode (section B).

### B) Sliced mode (mandatory pause between units)

Multiple **units of work**, each shippable: builds, tests that apply stay green, repo stays coherent.

**Use sliced mode with mandatory pauses** when **any** of the following is true:

- The user invokes **`/bmo-step-deliver`** **and** the task is backed by a plan with **2+ implementation units** (`U1`, `U2`, …) or explicit numbered phases/steps.
- The change spans **multiple independent failure domains** (DB + API + client, proto + generated + handlers, bootstrap + docs + tests) **and** the user or plan has expressed the work as multiple steps or slices.
- There is a natural **rollback seam** between steps (delete public surface → adjust bootstrap/config → update docs/tests).
- Reviewers would otherwise face one **unreviewable** diff.
- The user asked for **step-by-step** delivery.

After **each** unit in sliced mode: complete the **review digest** (§6), list **remaining** units (if any), and **end the turn** until the user continues (see [Pause for confirmation](#7-pause-for-confirmation-mandatory-for-sliced-mode)).

**Merging slices:** The user may compress work by explicit instruction only (e.g. **“single-pass from here”**, **“merge U2+U3”**, **“one shot for the rest”**). Without that, **one slice per user message** after the first.

**Do not slice** when the change is already a single coherent boundary **and** no multi-unit plan exists—or when splitting would create **incoherent intermediate states**. In that rare case, state why in one sentence and still use single-pass rules (section A); do not invent fake slices.

**Anti-pattern to avoid:** implementing the next unit in the same assistant turn because the prior unit “was small” or “summarized context suggested finishing.” **Never** advance slices without an explicit user signal unless they already opted into single-pass for this plan.

---

## Unanswered scope questions (AskQuestion / clarifications)

If a **scope-shaping question** was asked (structured `AskQuestion`, numbered options, or equivalent) and the user **skipped it**, left it blank, or did not pick an option:

- **Do not invent defaults** for those answers in the plan or implementation.
- **Re-ask once** with a single forced-choice question, **or** require an explicit token from the user such as **`defaults: yes`** (or a one-line “use defaults for skipped questions: A/B/C”) before proceeding.

Until that is resolved, treat the affected slice as **blocked**: no plan that depends on the missing answers, and no implementation that assumes them.

---

## Mid-flight scope correction

When the user **changes direction** after a plan exists (narrower/wider scope, different transport, “do not touch X”, “defer docs”, etc.):

1. **Update the plan artifact** (e.g. `.cursor/plans/*.plan.md` or the attached plan file): add a short **Revision** block with date or turn number, **new in/out scope**, and what superseded the prior text.
2. In chat, **restate one paragraph**: what is in scope now, what is explicitly out, and which prior assumptions are void.

Do not leave the written plan stale while code follows the new understanding.

---

## Operating principles

1. **Scope before volume** — Deliver the smallest coherent outcome; avoid drive-by refactors.

2. **Verification over narration** — If a command can prove correctness, run it (or say precisely what blocked it).

3. **Correct workspace (hard gate before verification)** — Commands must run against the **intended repo root**. Silent wrong-directory runs are a common failure mode.

    Before any install/test/build command:

    - Run **`pwd`** (or equivalent) and confirm it matches the repo root you intend, **or**
    - Prefer **`yarn --cwd "<absolute-path-to-package>" <script>`** (or the repo’s documented workspace runner) so the shell cwd cannot drift in multi-root or nested layouts.
    - Optionally confirm **`package.json`** at that root matches expectations (e.g. `name`, `scripts.test`).

    Do **not** assume the default shell cwd is correct after tool hops or parallel workspaces.

4. **Stop at boundaries** — End each unit at a natural checkpoint: passing tests, typecheck, or a documented “nothing runnable yet” milestone.

5. **No surprise scope** — If the user expands the task mid-flight, align scope before continuing (especially in sliced mode). See [Mid-flight scope correction](#mid-flight-scope-correction).

6. **Git commits: explicit approval per repository (hard gate)** — Do **not** run `git commit` in a repository unless **one** of these is true:

   - The user **explicitly** asked to commit **that repository** in the same turn (e.g. “commit the tx changes”, “commit in roxtarsverse”, `/bmo-commit` with clear intent for that root), **or**
   - **Sliced-mode `continue`:** the user sent **`continue`** (or an agreed equivalent like “next slice, commit it”) **after** you finished the **review digest** (§6) for a slice, and you are committing **only that slice’s changes in that same repo** per [Continue: commit slice, then next unit](#continue-commit-slice-then-next-unit).

   **Anti-patterns (never do this):**

   - User: “commit **schemas** changes … then continue with **next slice**” → commit schemas only; implement the next slice elsewhere; **do not** commit that next slice’s repo unless they ask again (or send `continue` after that slice’s review digest).
   - User approved a commit in **repo A** → you **must not** infer permission to commit **repo B** in the same turn or by default later.
   - Multi-root workspaces: each **git root** needs its **own** explicit commit instruction (or one message that names every repo to commit).

   After implementing a slice when the user did **not** ask to commit it: end with the review digest (§6) + “uncommitted locally”; you may offer **once** to commit—**do not** commit without a clear yes.

---

## The loop (single-pass or per slice)

Repeat until the agreed scope is done. In **sliced mode**, each repetition is **one user turn per slice** after the review digest (user sends `continue`, then you run the next loop iteration).

### 1) Align scope

State in one short paragraph:

- What this **unit of work** delivers.
- What is **explicitly out of scope** (including other repos, callers, or follow-ups).

If the repository documents architecture or testing conventions, read what applies before editing (example: monorepo `docs/architecture.md` when the change is architectural).

### 2) Implement

Stay within scope. Avoid unrelated cleanup unless the user asked or it blocks the change.

### 3) Verify

Apply the **correct workspace hard gate** from [Operating principles](#operating-principles) before running any command.

Pick the **narrowest meaningful proof**:

| Situation | Prefer |
|-----------|--------|
| Logic change | Focused unit tests |
| Types-only / imports | Typecheck |
| Formatting / lint rules | Lint |
| Integration-heavy path | Targeted integration test or scripted repro |
| Cannot run in agent env | Exact commands + prerequisites for the user |

**Codegen / generators:** If a step runs codegen (Protobuf, OpenAPI, GraphQL, etc.), treat output layout shifts as normal: run generation, then **search for broken imports** and fix call sites before declaring done.

**Stale generator caches:** If regenerated output still does not match the edited schema or proto (same RPCs/messages as before), the tool may be reading a **cached copy** instead of your latest files. Check the generator config for a **cache directory** (example: Protorox `cacheDir` / `.proto-cache`), delete the relevant cached artifact or clear the cache, regenerate, and **mention this in the review digest** so reviewers know the checked-in generated files truly reflect the source.

**Tool output vs config:** If CLI warnings contradict expectations (e.g. a “generation” flag is a no-op), note it in the review digest (§6)—config examples elsewhere may not match the installed tool version.

**Lockfiles / installs:** If `package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml` changes without an intentional dependency change in scope, **stop and classify**: accidental drift vs deliberate bump—do not silently ship unexplained lock churn.

### 4) Commit (only when requested, agreed, or `continue` in sliced mode)

When the user asks for a commit, follow repo conventions (see **`/bmo-commit`** in [Integration](#integration-with-other-skills)).

**Scoped wording:** If the user says “commit **X**” (a path, package, or repo name), **only** commit changes in **X**’s git root. “Then continue with [next slice]” means **implement + verify + review digest (§6)** for that slice, **not** automatic permission to commit another repo. See principle **6** under [Operating principles](#operating-principles).

In **sliced mode**, **`continue`** (after the slice’s **review digest** is delivered) normally implies committing that finished slice **before** the next unit—see [Continue: commit slice, then next unit](#continue-commit-slice-then-next-unit)—**only in the repo that slice belongs to**.

If using sliced mode and the user did not say `continue` and did not ask to commit, you may still ask once whether to commit before the next slice—**not** required for single-pass mode.

### 5) Report “how to run” (required)

Always end with **A** or **B**:

**A) Runnable commands**

Copy-paste commands from the correct directory. Prefer the repo’s package manager (`yarn`, `pnpm`, `npm` as documented). Prefer **`yarn --cwd "<absolute-path>" …`** when there is any doubt about cwd. State **`pwd`** (or the chosen `--cwd` path) when not repo root so reviewers can reproduce exactly.

**B) Nothing runnable yet**

Short chronological narrative of what will run later (env setup → migrations → tests → teardown).

### 6) Review digest (mandatory structure)

End every unit with a single clearly labeled section titled **`## Review digest`** (or `### Review digest` under a unit header). This is **not optional prose**; use the template below so reviewers get **scannable blocks**, **absolute paths** in multi-root workspaces, and **no missing “why / where from”** context.

**Message order:** In the assistant’s final reply, place **`## Review digest`** **after** the §5 “How to run” block (brief verification summary → §5 → §6) so the digest is the **last** thing in the message and easy to copy into a PR description.

#### When to use absolute paths

- **Multi-root Cursor workspace** or changes across **more than one git root**: list every file as an **absolute path**. Append the repo-relative path in parentheses if helpful, e.g. `` `/Users/me/proj/foo/apps/kyc/src/x.ts` (`apps/kyc/src/x.ts`) ``.
- **Single repo, single root**: absolute paths are still allowed; **repo-relative** paths are acceptable if there is no ambiguity.

Never rely only on bare filenames (`Notification.ts`) when more than one package could contain that name.

#### Template (copy and fill; do not omit headings)

Use **one block per coherent concern** (e.g. “Schema / types”, “Hermod publish”, “Window consumer”, “Tests”, “Docs”). Order blocks in **dependency / review order** (types/contracts before callers).

```markdown
## Review digest

**Scope:** <one sentence: what this unit delivered; what was deferred.>

### Block A — <short name: what this cluster is about>
**What this block is:** <one line: e.g. “Shared notification enums and payload shapes consumed by Hermod and Window.”>
**Git root:** `<absolute path to .git>` (if multiple repos touched)
**What to review in this block:** <1–3 sentences: cross-file invariant, contract, or ordering reviewers must sanity-check once for the whole block—not repeated per file.>
**Files:**
- `<absolute/path/to/file>` (`repo/relative/path`)
  - **Review:** <concrete prompt: intent / contract / failure mode; include **provenance** when non-obvious—e.g. “Payload fields match `docs/foo.csv` row …” or “Aligned with existing `Bar` type in `…/Bar.ts` line …”.>
- `<absolute/path/to/other>` (`…`)
  - **Review:** <…>

### Block B — <…>
**What this block is:** <…>
**Git root:** `<…>` (omit if same as previous block)
**What to review in this block:** <…>
**Files:**
- …
```

**Provenance and conventions (required when applicable)**

If the change introduces or reshapes **schemas, enums, payloads, or validation helpers**, the digest must state **where the shape came from** (spec URL, CSV, proto, ticket, product phrase, or “inferred from existing type X in file Y”) and **why two mechanisms exist** if both appear (e.g. type guard vs `parse*`—what each is for). If the repo has **automation** that replaces manual steps (e.g. “package version bumped by CI only”), call that out under the relevant file or block so reviewers do not flag intentional omissions.

**Minimum detail bar**

Each **file** line must include a **Review:** bullet that answers at least one of: intent vs main, contract field/RPC, failure mode if wrong, or red flag in the diff. **Vague** lines (“check handler”) violate this skill.

**Self-check before sending (silent; do not paste as a checklist unless the user wants it)**

- Every changed file appears **exactly once** under some block (or explicitly listed “unchanged but touched for …” if true).
- Each block has **What this block is**, **What to review in this block**, and **Files** with per-file **Review:** lines.
- Multi-root: all **File** paths are **absolute**; each block’s **Git root** is set when roots differ.
- No block is “misc” dumping: if everything is misc, split by **layer** (types → service → tests → docs).

**Reviewer checklist categories (general)**

Use these as **axes**, then **instantiate** them inside block- and file-level **Review:** text (not as empty section headers):

- **User-visible behavior** — UX copy, feature flags, defaults, error messages.
- **Contracts** — HTTP/gRPC/event payloads, schemas, versioning, backward compatibility.
- **Authorization / privacy** — Who can do what; PII in logs or responses.
- **Operational risk** — Deploy order, migrations, caches, async ordering (commit vs publish), idempotency, retries.
- **Tests** — What this change proves; what remains intentionally untested.

**Cross-cutting review prompts (use when relevant)**

- **Removing or narrowing a public surface** (RPC route, REST path, proto RPC, exported client): state **blast radius** (who consumed it), whether **callers outside this repo** must change, and whether the commit should carry **`BREAKING CHANGE`** (see **`/bmo-commit`** skill).
- **Docs and manifests:** After changing scripts, entrypoints, env vars, or public APIs, cross-check **README**, **package scripts**, and **CI** so documented commands and tables match reality (no phantom scripts or stale “methods implemented today” lists).
- **Integration tests vs production ingress:** If tests **seed data via one path** (e.g. service or queue) but **assert another** (e.g. gRPC), say so explicitly so reviewers do not confuse **test setup** with **supported caller paths**.
- **Hooks vs changed paths:** If pre-commit or CI runs **lint/format only on part of the repo** (e.g. `src/` but not `tests/`), note it when your edits touch paths that hooks do not cover.

Optional bullets (attach to the right block):

- **Compare with** — “Same pattern as `path/to/...`” when it speeds review.
- **Non-goals** — One line so reviewers do not flag intentional omissions.
- **Blast radius** — Public API, published packages, docs, or scripts outside this repo (when deletion or export paths change).

**Sliced migrations (optional pattern)**

For transport or API moves (e.g. Rabbit → gRPC), a coherent sequence often reduces risk: **centralize behavior in domain/service** → **extend contract + codegen** → **add adapters/handlers** → **integration tests** → **remove deprecated surface**. When using slices, say **which slice** you are in and **what must stay working** until the next slice lands.

### 7) Pause for confirmation (mandatory for sliced mode)

**Sliced / multi-unit plans:** After steps **1–6** for the current unit, you **must** pause. List what is **done** (this unit), what **remains** (next unit ids or step names), and ask the user to confirm before you touch the next slice. Accept signals such as **`continue`**, **next slice**, **proceed with U2**, or equivalent unambiguous approval.

**Do not** in the same assistant response: finish U1’s **review digest** (§6) and then implement U2. The next slice starts in a **later** turn after the user’s message.

**Single-pass** (section A only): No mandatory pause between fictional “slices” because there is only one unit; still deliver **review digest** (§6) + **how to run** (§5) at the end.

**Optional pacing:** If the user asked for pause between steps even on single-pass-sized work, treat each step as its own unit and apply the same mandatory stop between steps.

**Compressing slices:** Only if the user explicitly opts in (e.g. “merge U2+U3”, “single-pass for the whole plan”, “don’t pause”) may you implement multiple units in one turn; restate that opt-in in one line so reviewers know pacing was user-directed.

#### Continue: commit slice, then next unit

This flow commits **only** the slice the user acknowledged, in **the same git repository** that slice was implemented in. It does **not** extend to another repo named in the same sentence as an earlier scoped commit (example: “commit schemas … then continue with U2 in tx” → commit **schemas** only; after U2, **stop** unless they ask to commit tx or send `continue` after U2’s **review digest**).

If the user sends **`continue`** (or clear equivalent: “next slice”, “proceed”) **and** there is a **next slice** still to do **or** you are confirming the slice is done before closing:

1. **Commit the completed slice first** (in **that** repository only) using the **`/bmo-commit`** skill ([`bmo-commit`](../bmo-commit/SKILL.md)): stage **only** that slice’s paths (`git add …`—no file edits, no normalize/lint-fix); then follow that skill—if `git diff --cached` is empty, **stop** and tell the user to stage; otherwise inspect `git diff --cached`, infer type and scope, compose the message, run `git commit`. If there is nothing left to commit (already committed), skip to step 2.
2. If there is **another slice** in the plan, **then** start implementation for that next slice (return to step **Align scope** for that unit only, or a short delta if scope unchanged).

If there is **no next slice** and nothing left to implement, **`continue`** after the final **review digest** may mean “commit if needed, then done”—still run **`/bmo-commit`** when there are uncommitted slice changes **in the repo the user means**.

If the user explicitly says **not** to commit (e.g. “continue without commit”), honor that and skip step 1.

---

## Failure handling

If verification fails:

- Fix inside the same unit if the fix is small and caused by this change.
- Otherwise stop, report the **smallest next action** (revert, narrower test, or scope split).

---

## Integration with other skills

- **`/bmo-commit`** / **`bmo-commit`** — When the user asks for a commit, says **`continue`** under [Continue: commit slice, then next unit](#continue-commit-slice-then-next-unit), or `/commit`, follow that skill: **no edits or auto-fix to files**; stage only when the user asked or when this skill’s continue flow requires staging the slice; staged diff empty → stop; else inspect `git diff --cached`, conventional type/scope, then `git commit`.
- **`bmo-sync-repo-documentation`** (or repo doc-sync equivalent) — After changing scripts, public APIs, or paths listed in onboarding docs, reconcile **README / manifests / CI** so the review handoff does not repeat stale commands (often paired with the **Docs and manifests** bullet above).
- **Planning** — If the task is large or ambiguous, propose planning mode before heavy implementation (whether sliced or not).
