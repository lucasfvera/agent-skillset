---
name: step-deliver
description: Use when the user wants agent work delivered with clear scope, verification, runnable commands, and a human review checklist (specific files + risks). Optional multi-step slicing only when the task benefits from it—small tasks skip slicing and lean on review quality.
---

# Step-deliver

This skill defines a **delivery standard** for agent work: outcomes are **easy to review**, **easy to validate**, and **easy to roll back** when something goes wrong.

**Core outcomes (always):**

- Clear **scope** and boundaries (what changed, what did not).
- **Verification**: the narrowest proof that the change is sound.
- **How to run**: copy-paste commands or an honest “cannot run here” narrative.
- **Review handoff**: paths, intent, contracts, and risks—without rereading the chat.

**Slicing is optional.** Use multiple steps only when splitting **reduces risk**, **shrinks reviewable diffs**, or the user asked for paced delivery. For small, cohesive work, do **one unit of work** and spend effort on verification and the review guide—not artificial intermediate commits.

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

### A) Single-pass mode (default for small / cohesive work)

One scoped change → verify → review handoff.  
No mandatory pause unless the user asked for one.

### B) Sliced mode (opt-in)

Multiple **units of work**, each shippable: builds, tests that apply stay green, repo stays coherent.

Use sliced mode when **splitting genuinely helps**, for example:

- Multiple **independent failure domains** (DB + API + client).
- A natural **rollback seam** between steps.
- Reviewers would otherwise face one **unreviewable** diff.
- The user asked for **step-by-step** delivery.

**Do not slice** when the change is already small, or splitting would create **incoherent intermediate states** just to satisfy a process.

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

3. **What to pay attention to** — Use the categories below; pick those that apply. Put **most important** first.

**Reviewer checklist categories (general):**

- **User-visible behavior** — UX copy, feature flags, defaults, error messages.
- **Contracts** — HTTP/gRPC/event payloads, schemas, versioning, backward compatibility.
- **Authorization / privacy** — Who can do what; PII in logs or responses.
- **Operational risk** — Deploy order, migrations, caches, async ordering (commit vs publish), idempotency, retries.
- **Tests** — What this change proves; what remains intentionally untested.

Optional bullets:

- **Compare with** — “Same pattern as `path/to/...`” when it speeds review.
- **Non-goals** — One line so reviewers do not flag intentional omissions.
- **Blast radius** — Public API, published packages, docs, or scripts outside this repo (when deletion or export paths change).

### 7) Pause for confirmation (conditional)

Ask for a short token (e.g. `continue`) **only when**:

- Using **sliced mode** and more work remains, or
- The user explicitly asked for **pause between steps**.

Do **not** require a pause after every single-pass task.

---

## Failure handling

If verification fails:

- Fix inside the same unit if the fix is small and caused by this change.
- Otherwise stop, report the **smallest next action** (revert, narrower test, or scope split).

---

## Integration with other skills

- **`commit`** — When the user asks for a commit message or `/commit`, follow that skill’s format and conventions.
- **Planning** — If the task is large or ambiguous, propose planning mode before heavy implementation (whether sliced or not).
