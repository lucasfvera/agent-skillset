# Doc sync checklist (general deep pass)

Use before release or when doing a full-doc audit. Skip rows that do not apply to the stack.

## Layout

- [ ] Identified **standalone vs monorepo** and the correct manifest(s) for the changed area
- [ ] Documented commands use the **same** package manager / task runner the repo uses (`pnpm`, `yarn`, `npm`, `cargo`, `poetry`, `make`, etc.)

## Markdown surfaces

- [ ] Root **README** — install, dev, build, test, lint match real scripts or tasks
- [ ] **Package READMEs** in workspaces (if monorepo) — not only root
- [ ] **`docs/**`** or site generator content — paths and commands still valid
- [ ] **CONTRIBUTING** / **SECURITY** — links and commands work
- [ ] **CHANGELOG** / **ADR** — if the change is user-facing or architectural
- [ ] **`.github/**/*.md`** — issue/PR templates and workflow-inline instructions

## Agent / editor docs

- [ ] **AGENTS.md** / **CLAUDE.md** (and similar) — same constraints as README for commands and paths
- [ ] **`.cursor/rules/**`** — examples and file paths match repo
- [ ] **Project `.cursor/skills/**/SKILL.md`** — if present, workflows reference real tools

## Accuracy vs code

- [ ] **Env vars** — match `.env.example` (or language-specific config schema)
- [ ] **File paths** in code blocks — exist on disk
- [ ] **Tests** named in docs — exist; globs match project test config
- [ ] **Public API** (routes, events, CLI) — only verify what this repo exposes; discover from source
- [ ] **CI** — README “how we CI” matches `.github/workflows` or equivalent

## Duplicates

- [ ] Same wrong command not left in **two** places (README + AGENTS + docs)
