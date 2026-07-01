# Agent skillset

Cursor skills for how we plan work, ship code, open PRs, and close review loops.

```bash
npx github:lucasfvera/agent-skillset
```

Copies every `bmo-*` skill into `~/.cursor/skills/`.

## Manual Workflow

<img width="6455" height="1272" alt="image" src="https://github.com/user-attachments/assets/e44b4794-a54a-46cb-9955-0d8fa17bb0f1" />

The original flow from which I started. I ran, manually, one skill at a time until I felt comfortable to automate.

## Skills

| Skill | When to use it |
|-------|----------------|
| `/bmo-block-reviewer` | You want a short, findings-first review of a delivery slice against a specific code-quality bar (typing, tests, duplication), using the actual diff. |
| `/bmo-commit` | You want a conventional commit from what's already staged. Won't auto-stage, edit files, or run formatters. Infers monorepo scope from staged paths. |
| `/bmo-document-html` | You want a self-contained HTML doc (architecture, migration, handoff) with diagrams, not another markdown file. |
| `/bmo-git-stack-update-refs-push` | You have a local branch stack to rebase with `--update-refs`, wire to `origin/<branch>`, and publish with force-with-lease. |
| `/bmo-integration-tests` | You need Roxom-style integration tests with real Postgres, RabbitMQ, and gRPC (tx, hermod, similar services). Uses the smallest real stack that proves the behavior. |
| `/bmo-merge-conflicts` | You're mid-rebase with conflict markers. Default is suggestions only; it edits files when you ask it to resolve. |
| `/bmo-pr` | You want to open or update a GitHub PR with a conventional title and a filled-out body (repo template or default sections). |
| `/bmo-stack-prs` | You have a stacked branch line and need ordered PRs, pushes for out-of-sync heads, and missing PRs opened from git history alone. |
| `/bmo-step-deliver` | You want work in reviewable slices: scope, verification commands, and a structured review digest. Stops after each unit until you say continue. |
| `/bmo-step-planner` | The task is big or cross-cutting and you want a plan (U1, U2, …) written under `.cursor/plans` before anyone writes code. |
| `/bmo-sync-repo-documentation` | Scripts, paths, env, or public APIs changed and docs (README, `docs/`, AGENTS.md, `.cursor` rules/skills) may be out of date. |
| `/bmo-triage` | You have a Linear issue and want complexity, importance, and ROI before planning or coding. Skips issues that are done or unreachable. |
| `/bmo-update-block-reviewer-skill` | Pending session captures in `inbox/pending/` need distilling into the learnings catalog and promotion into `bmo-block-reviewer`. |

## Workflows

### `/bmo-linear-pipeline`

<img width="3908" height="1489" alt="image" src="https://github.com/user-attachments/assets/4bb56419-1783-415d-885e-f098b487e5e9" />

| When to use it |
|----------------|
| Hands-off pickup of a low-complexity Linear issue: isolated worktrees per repo, deliver each plan unit with block review and commit in a loop. Stops on medium/high complexity or if triage says skip. Opens PRs with changes. |

### `/bmo-respond-pr-review`

<img width="5828" height="1404" alt="image" src="https://github.com/user-attachments/assets/1523ef30-755d-443f-a1cd-adc7c046c81c" />

| When to use it |
|----------------|
| You have human PR review comments to address end to end: triage threads, implement fixes, block-review before publish, commit and push, reply on GitHub, resolve threads, post a summary, and capture session feedback for the block-reviewer inbox. |
