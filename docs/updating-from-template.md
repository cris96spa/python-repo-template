# Updating from the Template

Projects created from this template can pull in later template changes with the
`utils/update_template.py` script. It fetches the template, replays only the
changes made *since your project last synced*, and leaves you a branch to review
and merge.

## How it works

The script links your project's history to the template's by temporarily
grafting your first commit onto a known template reference commit, then
squash-merges the template branch on top. Git therefore sees a real merge base
and produces a diff of **only the template's changes since that reference
point** — not its entire history.

The reference point is recorded in `pyproject.toml` so each run knows where the
previous one left off:

```toml
[tool.template]
template_commit = "<last synced template commit>"
template_branch = "main"
```

On the first run, when this section is absent, the script estimates the
reference commit from your project's creation date.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) and `git` available on your `PATH`.
- Read access to the template repository (SSH by default).
- A clean working tree on your project's default branch.

## Running the update

From the project root:

```bash
uv run python utils/update_template.py
```

The available options are:

| Option | Description | Default |
| --- | --- | --- |
| `-u`, `--template-url` | URL of the template repository. | The template's Git URL |
| `-b`, `--branch` | Template branch to pull changes from. | `[tool.template].template_branch`, else `main` |
| `-c`, `--commit` | Template commit to treat as the last synced reference. | `[tool.template].template_commit`, else estimated |

For example, to sync from a specific template branch:

```bash
uv run python utils/update_template.py --branch main
```

## What the script does

1. Verifies `uv` is installed and that no leftover graft commits remain.
2. Creates an `update-template` branch from your project's default branch.
3. Adds the template as a read-only remote, grafts the histories, and
   squash-merges the chosen template branch.
4. Updates the `[tool.template]` reference in `pyproject.toml`.
5. Removes the temporary graft commit and template remote.

!!! note "Cleanup is automatic"
    The graft commit and the `template` remote are temporary and are removed
    even if the update fails partway through, so they are never pushed.

## Resolving conflicts

A clean merge is committed automatically. When the squash-merge hits conflicts,
the script stops and asks you to resolve them by hand:

1. Resolve the conflicts in your editor and stage the results.
2. Commit the resolution.
3. Re-run the script. Because you are already on the `update-template` branch
   with a clean staging area, it resumes from there.

Once the `update-template` branch looks right, open a pull request against your
default branch as usual.
