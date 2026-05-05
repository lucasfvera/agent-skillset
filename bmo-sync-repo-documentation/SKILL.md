---
name: sync-repo-documentation
description: >-
  Brings repository documentation back in sync with the codebase after features,
  refactors, or tooling changes. Works for standalone repos and monorepos: discovers
  where package manifests, config, and tests live, then cross-checks Markdown and
  agent docs (README, docs/, AGENTS.md, .cursor rules, skills) against real scripts,
  env samples, paths, CI, and public behavior. Use when finishing changes that could
  leave docs stale, when the user asks to update README or docs, or when reconciling
  documentation with implementation in any project layout.
---

# Sync repository documentation with code

## When to apply

- After edits to **scripts**, **entrypoints**, **config**, **public API** (HTTP, RPC, messages, CLIs), **tests**, or **paths** that docs might still name incorrectly.
- When the user asks to **refresh README**, **fix outdated commands**, **update docs**, or **reconcile documentation with the repo** — in a **monorepo or a single-package repo**.

## Principles

1. **Treat docs as code.** Assume docs are stale until checked against the tree and manifests.
2. **Discover before assuming.** Do not hardcode one layout (`apps/`, `src/config`, etc.). Find the right `package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml` / `Makefile` for the scope of the change (workspace root vs package).
3. **Prefer sources of truth** over prose: package/tool manifests, CI workflows, config loaders, and the filesystem.
4. **Match each doc’s existing tone and structure** — fix accuracy, not voice.

## Discover repo shape (do this first)

- **Standalone:** one root manifest and one primary source tree; commands usually run from repo root.
- **Monorepo:** workspace manifests (`package.json` workspaces, `pnpm-workspace.yaml`, `Cargo.toml` workspace, etc.) — documented commands must say **which directory or workspace** they apply to (`pnpm --filter`, `yarn workspace`, `nx`, `turbo`, etc.).
- Note **where tests live** (`tests/`, `__tests__/`, `spec/`, package-local `test/`) and **which config loads env** — varies by language and framework.

## Markdown and agent-doc inventory

Scan and include any paths that exist under the target repo (not every repo has all of these):

| Kind | Typical locations |
| ---- | ----------------- |
| Primary onboarding | `README.md`, `readme.md`, package-local `README.md` in workspaces |
| Deep docs | `docs/**`, `documentation/**`, `guide/**`, `mkdocs.yml` + content dir, `website/` / `docusaurus` |
| Contributing / legal | `CONTRIBUTING*`, `CODE_OF_CONDUCT*`, `SECURITY*`, `LICENSE*` cross-links |
| Changelog / decisions | `CHANGELOG*`, `HISTORY*`, `adr/**`, `docs/adr/**` |
| GitHub / GitLab | `.github/**/*.md` (templates, workflows that embed instructions), `.gitlab/**/*.md` |
| Agent & editor guidance | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/**` (`.md`, `.mdc`), `.cursor/skills/**/SKILL.md`, `.github/copilot-instructions.md`, `.vscode/` doc snippets if they duplicate commands |
| Rules-of-thumb | Any `*.md` linked from README or AGENTS; wiki mirrors noted in-repo |

When updating for a **scoped change** (one package in a monorepo), refresh **that package’s README** and any **root docs** that describe the whole system.

## Workflow

1. **Identify drift drivers** — From the task or diff: scripts, env, routes, renamed files, removed features, new test locations.

2. **Verify against sources of truth** (use only what the repo actually has):

   | Topic | How to verify |
   | ----- | ------------- |
   | Install / build / test / lint commands | Root and workspace **package scripts**, **Makefile** / **Taskfile** / **justfile**, **Cargo**/ **Go**/ **Poetry** commands as applicable — align docs with the manifest users must run. |
   | Monorepo vs single package | If workspaces exist, documented commands must match **real** workspace tooling (filter flags, app names); never document a root `yarn dev` if only `turbo run dev` is used, etc. |
   | Environment variables | `.env.example`, `.env.sample`, `config.*`, `**/application*.yml`, env schema modules — wherever this project defines config. |
   | Paths, files, imports in prose | Repo tree — referenced paths must exist or be marked legacy/historical. |
   | Tests / checks listed in docs | Same filenames or globs must exist under the project’s test layout; config from `jest.config.*`, `vitest.config.*`, `pytest.ini`, `Cargo.toml` `[package.metadata]`, etc. |
   | Public behavior (HTTP, RPC, queues, gRPC, CLI) | Only if the project exposes them: match **actual** route definitions, protos, handlers, or CLI parsers — no boilerplate list; discover from code. |
   | CI | `.github/workflows/**`, `.gitlab-ci.yml`, Circle, Buildkite — documented checks should resemble what runs in CI. |

3. **Edit documentation** — Update commands, paths, env names, architecture bullets, and test inventories. If behavior is **transitioning** (deprecated path vs new path), say so in one clear sentence. Optional: a **removal cue** when a doc describes something intentionally temporary (e.g. a suite to delete when a feature flag is removed).

4. **Sanity-check** — Grep for old symbols/paths from the change; confirm documented shell commands exist on the intended manifest.

## Anti-patterns

- Assuming **one** `package.json` at root when the change lives in a workspace package.
- Fixing only root `README.md` while **workspace READMEs** or **`docs/`** repeat the same wrong command.
- Documenting **aspirational** behavior without labeling it (unless the team wants “planned” explicitly).
- Broken **relative links** or **old path prefixes** after moves (e.g. `apps/legacy/...` still in examples after extraction to a standalone repo).

## Output

Apply edits in-repo. Summarize **which files** changed and **what source** each correction used (e.g. “commands aligned with `packages/foo/package.json` scripts”).

## Additional resources

Optional extended checklist: [reference.md](reference.md).
