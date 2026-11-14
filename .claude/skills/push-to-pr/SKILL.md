---
name: push-to-pr
description: Commit, push, and open or update the pull request for the current branch. Use when asked to push, open a PR, or send changes for review.
allowed-tools: Bash(git:*), Bash(gh:*), Bash(make:*)
---

# Push To PR

## 1. Check the state

```bash
git branch --show-current
git status --porcelain
gh pr list --head "$(git branch --show-current)" --json number,url,title

DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name 2>/dev/null)
[ -n "$DEFAULT_BRANCH" ] || DEFAULT_BRANCH=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||')
echo "default branch: ${DEFAULT_BRANCH:-UNKNOWN}"
```

If that prints `UNKNOWN`, neither `gh` nor the local remote HEAD could tell you
the default branch. Stop and ask — do not carry on, because an empty value makes
the check below pass no matter which branch you are on.

If the current branch is the default branch, stop and create a feature branch
first — the skills and CI here assume branch-then-PR. Nothing enforces this:
`no-commit-to-branch` in `.pre-commit-config.yaml` guards `development`,
`staging` and `production`, not the default branch, so this check is the only
thing standing between you and a direct commit to it.

## 2. Run the gate before committing

```bash
make format-check && make lint && make lint-doc && make test
```

These are exactly what `.github/actions/validation` runs. Fix failures before
continuing; do not push a red branch.

## 3. Commit

The `commit-msg` hook runs `conventional-pre-commit`. The subject must start
with one of: `feat, fix, chore, build, ci, docs, perf, refactor, revert, style,
test, merge`. A non-conforming subject is rejected and the commit is lost.

A commit message is that one line: no body and no attribution trailers. What a
reviewer cannot infer from the diff belongs in the PR description.

```bash
git add -A
git commit -m "feat: short imperative summary"
```

Version numbers are owned by `python-semantic-release`. Never bump one by hand.

## 4. Push and open or update the PR

No PR yet:

```bash
git push -u origin "$(git branch --show-current)"
gh pr create --title "<conventional-style title>" --body "$(cat <<'EOF'
## Summary

<what changed and why>

## Changes

- <bullet per meaningful change>

## Verification

- `make format-check && make lint && make lint-doc && make test` — passing
EOF
)"
```

PR already exists:

```bash
git push
```

Report the PR URL either way.
