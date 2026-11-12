# Agent skillset

Portable agent skills for planning vertical slices, shipping verified code, running two-pass domain code reviews, opening anti-cognitive-surrender PR stacks, and closing review loops.

```bash
npx github:lucasfvera/agent-skillset
```

Copies every `bmo-*` skill into `~/.cursor/skills/` (or `$BMO_SKILLS_DIR` when set) and installs the pre-PR checks hook (`hooks/pr-checks.py`) into `~/.cursor/hooks/`. Environments without shell hooks enforce the same pre-PR checks directly via [`hooks/pr-checks.md`](hooks/pr-checks.md) inside `/bmo-builder` and `/bmo-pr`.

## Manual Workflow

<img width="6455" height="1272" alt="Manual workflow overview" src="https://github.com/user-attachments/assets/e44b4794-a54a-46cb-9955-0d8fa17bb0f1" />

The original flow from which these skills evolved: running one skill at a time with human checkpoints before composing them into automated pipelines.

## Skills

| Skill | When to use it |
|-------|----------------|
| `/bmo-block-reviewer` | Two-pass findings-first diff review: Pass 1 (`[issue]`) catches correctness, contract, security, performance, and false-test defects; Pass 2 (`[style]`) checks conventions across domain catalogs (`core`, `frontend`, `backend`, `database`, `testing`). |
| `/bmo-commit` | Creates a git commit strictly from staged changes without editing files or running formatters, matching the repository's commit style. |
| `/bmo-document-html` | Produces standalone, graphics-first technical documentation as a self-contained HTML page with diagrams, semantic layout, and light/dark styling. |
| `/bmo-git-stack-update-refs-push` | Rebases a local branch stack with `git rebase --update-refs`, aligns upstream tracking, and publishes rewritten tips with `--force-with-lease`. |
| `/bmo-integration-tests` | Adds or extends service integration tests against real databases, HTTP/gRPC/RPC transports, and message brokers using the smallest real stack that proves the production boundary. |
| `/bmo-merge-conflicts` | Analyzes git rebase merge conflicts side-by-side (suggestions only by default; resolves files only on explicit ask). |
| `/bmo-pr` | Opens or updates a GitHub PR (~100–200 LOC production soft ceiling, tests co-located) with green pre-PR checks (`hooks/pr-checks.md`), an anti-cognitive-surrender review body, and release-free visual screenshots when tooling is available. |
| `/bmo-stack-prs` | Infers stacked branch order from git history, pushes out-of-sync stack heads, and opens/updates stacked GitHub PRs (`Part i of k`) with anti-cognitive-surrender bodies. |
| `/bmo-step-deliver` | Delivers scoped ~100–200 LOC vertical slices (with tests) one unit at a time, running narrow verification and emitting a structured review digest before pausing for `continue`. |
| `/bmo-step-planner` | Authors a sliced markdown plan (`U1`, `U2`, …) with ~100–200 LOC vertical units, co-located tests, backing docs, boundary failure modes, and rollback seams before writing code. |
| `/bmo-sync-repo-documentation` | Brings repository documentation (`README`, `docs/`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, rules, skills) back in sync with real scripts, env samples, paths, and CI. |
| `/bmo-teach` | Scaffolds an offline, hands-on learning repository calibrated to your starting point across sprint, portfolio, and TDD kata tracks. |
| `/bmo-tone` | Enforces direct, zero-fluff engineering prose when ghostwriting PRs/comments/docs or replying in chat. |
| `/bmo-triage` | Scores an issue (Linear, GitHub Issues, or pasted text) on complexity, Kano user value, importance, ROI, and automated pickup readiness. |
| `/bmo-update-block-reviewer-skill` | Distills pending PR review captures from `inbox/pending/` into domain- and tier-classified rules (`issue` on 1+ PR source; `style` staged in `ledger.md` and promoted on 2+ PR sources). |

## Workflows

### `/bmo-builder`

| When to use it |
|----------------|
| End-to-end build when you already know the work: authors a vertical-sliced plan (`U1..Uk`), creates isolated worktrees per repo with stacked unit branches by default, delivers each unit with parallel 2-pass block review and commits, runs parallel domain-scoped final review + pre-PR checks (`hooks/pr-checks.md`), and opens stacked PRs. |

### `/bmo-issue-pipeline`

<img width="3908" height="1489" alt="Issue pipeline workflow" src="https://github.com/user-attachments/assets/4bb56419-1783-415d-885e-f098b487e5e9" />

| When to use it |
|----------------|
| Hands-off pickup of an issue (Linear key/URL, GitHub Issue, or tracker text): runs `/bmo-triage` first, checks Gate 1 (`Proceed` + `Pickup: Yes`), and hands off to `/bmo-builder` to ship the PR(s). Stops cleanly on `Skip`, unclear acceptance criteria, or `Pickup: No`. |

### `/bmo-respond-pr-review`

<img width="5828" height="1404" alt="Respond to PR review workflow" src="https://github.com/user-attachments/assets/1523ef30-755d-443f-a1cd-adc7c046c81c" />

| When to use it |
|----------------|
| Closes the human PR review loop end to end: triages inline threads and top-level review bodies, implements fixes locally, runs one 2-pass `bmo-block-reviewer` subagent per code-changing review item before push, replies and resolves threads on GitHub without duplicate top-level comments, and captures raw feedback into `inbox/pending/`. |
