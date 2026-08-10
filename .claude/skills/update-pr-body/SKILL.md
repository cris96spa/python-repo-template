---
name: update-pr-body
description: Rewrite the description of a GitHub pull request. Use when asked to update, edit, or rewrite a PR body or description.
allowed-tools: Bash(gh:*), Bash(git:*)
---

# Update PR Body

## 1. Find the PR

```bash
gh pr list --head "$(git branch --show-current)" --json number,url --jq '.[0]'
```

## 2. Read the current body before replacing it

```bash
gh pr view <number> --json body -q '.body'
```

Never overwrite blind. Reviewers put checklists and test notes in PR bodies;
carry them forward unless asked to drop them.

## 3. Write the new body

```bash
gh pr edit <number> --body "$(cat <<'EOF'
## Summary

<what changed and why>

## Changes

- <bullet per meaningful change>

## Verification

- `make format-check && make lint && make lint-doc && make test` — passing
EOF
)"
```

To append instead of replace, capture the current body first:

```bash
CURRENT=$(gh pr view <number> --json body -q '.body')
gh pr edit <number> --body "${CURRENT}

## Follow-up

<new content>"
```
