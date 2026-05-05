# stack-prs — reference

## Incremental run (feat-3 on top of existing PRs)

**Git:** `main` → `feat-1` → `feat-2` → `feat-3` (single history line). **Tip** for the run: `feat-3` (or current branch if omitted).

**No manual branch list:** discovery finds `feat-1`, `feat-2`, `feat-3`; push-set compares each to `origin/*`; create-set is gap heads only.

**GitHub open PRs:** PR A has `baseRefName=main`, `headRefName=feat-1`. PR B has `baseRefName=feat-1`, `headRefName=feat-2`.

**Planned pairs:** `(main, feat-1)`, `(feat-1, feat-2)`, `(feat-2, feat-3)`.

**Reconcile:**

- Slice 1–2: satisfied → **no** `gh pr create`. **Push** still applies if `git rev-parse feat-N != git rev-parse origin/feat-N` for any stack head (keeps remote aligned).
- Slice 3: gap → include `feat-3` in push-set if needed, then `gh pr create --base feat-2 --head feat-3`.

## Push-set check (local vs origin)

For stack branch `B` (when `origin/B` exists):

```bash
[ "$(git rev-parse B)" = "$(git rev-parse origin/B)" ] && echo "skip push" || echo "push B"
```

If `origin/B` is missing, push `B`.

## Check one head against an expected base

```bash
gh pr list --state open --head "feat-2" --json number,url,baseRefName,headRefName
```

Confirm `baseRefName` equals the predecessor branch (e.g. `feat-1`). If the list is empty, the slice is a **gap**.

## Ordered stack table (example)

After computing `ROOT..TIP`, the planned PRs look like:

| PR | `--base` | `--head` |
|----|----------|----------|
| 1 | `main` | `feat/1-step/...` |
| 2 | `feat/1-step/...` | `feat/2-step/...` |
| … | previous head | next head |
| n | `feat/create-notif-queue` | `test/e2e-pub-hermod` |

Each row’s base must be a **strict ancestor** of its head.

## Commit list for PR1 body when local `main` diverged

Use remote tip for the log range:

```bash
git log --oneline origin/main..HEAD_OF_PR1
```

Still pass `--base main` to `gh pr create` so the PR targets GitHub’s default branch.

## One-shot ancestry check (heredoc)

```bash
while read -r base head; do
  git merge-base --is-ancestor "$base" "$head" \
    && echo "OK $head <- $base" \
    || echo "BAD $head <- $base"
done <<'EOF'
origin/main feat/first-branch
feat/first-branch feat/second-branch
EOF
```

Use real branch names; first line uses `origin/main` only for the **check**, not as `--base` on GitHub.

## Discover tips on path (conceptual)

1. `git log --reverse --format=%H origin/main..TIP > /tmp/path_commits`
2. For each candidate branch `B`, `H=$(git rev-parse B)`; keep `B` if `H` is in the path set.

Implement with shell or a short script as needed; large repos may need efficiency tweaks.
