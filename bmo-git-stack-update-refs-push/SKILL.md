---
name: git-stack-update-refs-push
description: >-
  Rebases a stacked branch line with `git rebase --update-refs`, wires each
  local branch to `origin/<same-name>` when that remote ref exists, and pushes
  rewritten tips with `git push --force-with-lease` (optionally `--atomic`).
  Use after restacking local branches, when the user mentions update-refs,
  stacked branches out of sync after rebase, or pushing a rebased PR stack.
disable-model-invocation: true
---

# Git stack: `update-refs` rebase and push

## When to use

- Local **stack** of branches was rebased (often `git rebase --update-refs …`) and **diverged** from `origin/*`.
- User wants **upstream tracking** set so each branch tracks `origin/<branch>`.
- User needs to **publish** the new history without a bare `--force`.

**Requires Git 2.38+** for `git rebase --update-refs` (stack-aware rebase).

## Do not confuse with

- **stack-prs** (personal skill `~/.cursor/skills/stack-prs/`) — discovers stack order from history, reconciles GitHub PRs, pushes/creates PRs. Use that when the goal is **PR workflow + automation**. Use **this** skill for the **rebase/update-refs + upstream + force-with-lease** mechanics.

## Preconditions

1. `git fetch origin` (or the relevant remote) so `origin/*` is current.
2. Know which **remote** to use (`origin` unless the user says otherwise).
3. Confirm **shared branches**: force-pushing rewrites remote history; coordinate if others use the same branches.

## 1. Rebase with update-refs (reminder)

Typical pattern while moving the bottom of the stack onto new base (example: onto updated `main`):

```bash
git checkout <bottom-branch-of-stack>
git rebase --update-refs <new-base>   # e.g. origin/main
```

`--update-refs` moves **other local branches** that pointed into the rebased commits so they stay stacked without manual `git branch -f` per layer.

If the user already rebased, skip this section.

## 2. Ensure upstream (`branch` → `origin/branch`)

For each local branch in the stack that should track the remote **same name**:

- If `origin/<branch>` **exists**:

```bash
git branch --set-upstream-to=origin/<branch> <branch>
```

- While **checked out** on that branch:

```bash
git branch -u origin/<branch>
```

**Find locals missing upstream:**

```bash
git for-each-ref refs/heads --format='%(refname:short)|%(upstream:short)' | awk -F'|' '$2=="" {print $1}'
```

**Skip or handle specially:**

- **`origin/<branch>` missing** — remote branch deleted or never pushed: either `git push -u origin <branch>` (create remote) or delete/rename local branch; do not invent an upstream.
- **Rename mismatch** — local name ≠ remote name: use explicit upstream `origin/<actual-remote-name>` or rename local branch to match team convention.

## 3. Sanity check before push

Optional, per branch:

```bash
git log --oneline origin/<branch>..<branch>
```

Shows commits you are about to publish on top of current remote tip.

## 4. Push rewritten stacks

After **any** history rewrite on tracked branches, normal push fails; use **`--force-with-lease`** (not bare `--force`) so the push aborts if the remote advanced unexpectedly.

**Single branch:**

```bash
git push --force-with-lease origin <branch>
```

**Several branches (one invocation):**

```bash
git push --force-with-lease origin <b1> <b2> <b3>
```

**Atomic multi-ref push** (all refs updated or none — helps keep a stack consistent when the server supports it):

```bash
git push --force-with-lease --atomic origin <b1> <b2> <b3>
```

**First-time remote branch** (no `origin/<branch>` yet):

```bash
git push -u --force-with-lease origin <branch>
```

Order of branch arguments **usually does not matter** for tip updates; use the stack order only if it helps the user read logs.

## 5. If `--force-with-lease` rejects

Remote moved (new commits) since your fetch. **Fetch**, reconcile (rebase again or merge), then retry. Do not escalate to `--force` without user approval.

## Checklist (agent or human)

- [ ] `git fetch <remote>`
- [ ] List stack branches that were rewritten
- [ ] For each: `origin/<name>` exists → `git branch -u origin/<name> <name>`
- [ ] For each: push with `git push --force-with-lease` (and `--atomic` if multi-branch and desired)
- [ ] Warn if branches are shared or CI depends on exact SHAs on remote
