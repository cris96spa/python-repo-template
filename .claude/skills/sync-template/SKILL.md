---
name: sync-template
description: Pull upstream python-repo-template changes into this project and land them on a reviewed branch. Use when asked to sync, update from, or rebase onto the template.
allowed-tools: Bash(git:*), Bash(uv:*), Bash(make:*), Read, Edit
---

# Sync From Template

`utils/update_template.py` grafts this project's history onto a known template
commit, squash-merges the template branch, and leaves an `update-template`
branch to review. The sync point lives in `[tool.template]` in `pyproject.toml`.

## Pre-flight

All four must hold before the first run. They do not apply when resuming after
a conflict — see On conflict below, where you stay on `update-template`.

```bash
git status --porcelain          # must be empty
git branch --show-current       # must be the default branch
git fetch && git status -sb     # must not be behind
grep -A2 '\[tool.template\]' pyproject.toml
```

If `[tool.template]` is absent this is the first sync; the script estimates the
reference commit from the project's creation date. Say so before proceeding.

## Run

```bash
uv run python utils/update_template.py
```

## On conflict

The script stops and leaves you on `update-template`. Do not restart from
scratch:

1. Resolve the conflicts in the working tree.
2. Stage the resolution: `git add -A`
3. Commit it.
4. Re-run `uv run python utils/update_template.py`. It resumes from the branch.
   Do not return to Pre-flight and do not check out the default branch first:
   the script detects it is already on `update-template` and continues, whereas
   checking out the default branch makes it try to create that branch again and
   abort.

Conflicts concentrate in files derived projects edit. `CLAUDE.md` conflicts
almost always belong to its `## Project` section — keep the project's version of
that section and take the template's version of everything else.

## After the merge

```bash
make dev
make format-check && make lint && make lint-doc && make test
```

Then summarise, for the user:

- The template commit range that came in. The script's own commit message is
  the fixed string `chore: update_template auto-commit` and carries no detail,
  so read the range from the sync point it recorded:
  `git diff HEAD~1 HEAD -- pyproject.toml` shows the old and new
  `[tool.template] template_commit` values.
- Which files changed, grouped by area: `git show --stat HEAD`.
- Anything requiring a manual follow-up, such as a new make target or dependency.

Open the PR against the default branch.

## Never

- Force-push the `update-template` branch.
- Delete the temporary `template` remote or the graft commit by hand; the script
  removes both, even on failure.
- Start on a dirty working tree — the graft step will lose uncommitted work.
- Edit `[tool.template]` manually to skip a conflicted range.
