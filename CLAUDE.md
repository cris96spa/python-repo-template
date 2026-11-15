# Project Context

## Project

<!-- Derived projects own this section. Everything below it comes from the template. -->

- **Purpose:** A template for Python projects. Replace this with what your project does.
- **Package:** `python_repo_template`. To rename it: rename the directory, then
  update every occurrence of the old name and of `PROJECT_NAME` —
  `grep -rn 'python_repo_template\|PROJECT_NAME' --exclude-dir=.git --exclude-dir=node_modules .`
  — including `Makefile`, `Dockerfile`, `pyproject.toml` (project name, hatch wheel
  packages, pyright include), `main.py`, `tests/test_func.py`,
  `.github/workflows/publish.yaml` and `docs/pages/index.mdx`.
- **Entry point:** `main.py`.

## Toolchain

uv manages dependencies, make runs everything else.

- Always `uv run python`, never bare `python` or `python3`.
- `make help` lists every target.
- Use `uv run ruff`, not `uvx ruff`. The dev group pins the version CI uses; an unpinned `uvx ruff` drifts from it and produces findings CI does not have.
- Python 3.12+ is required.

## Code Style

- Comments earn their place. Never narrate the line below, never justify a constant's value, never write an explanatory blob. If a comment feels necessary, first try renaming a symbol or extracting a function — that usually removes the need.
- Symbol names carry their own meaning. No abbreviations that need decoding.
- Documentation reads clean: no filler, no restating the API in prose.
- Tests cover critical behaviour and edge cases. Coverage is a diagnostic, never a goal. Never add a test to move the number.

These are the essentials. The full standard lives in three skills: read
`.claude/skills/coding-guidelines/SKILL.md` before writing or reviewing Python or YAML,
`.claude/skills/writing-guidelines/SKILL.md` before writing documentation, a pull request
description, a commit message or a review report, and follow
`.claude/skills/review-guidelines/SKILL.md` whenever asked to review a change.

## Commands

| Task | Command |
|---|---|
| Create the dev environment and install hooks | `make dev` |
| Install production dependencies only | `make install` |
| Format | `make format` |
| Check formatting | `make format-check` |
| Lint | `make lint` / `make lint-fix` |
| Lint docstrings | `make lint-doc` |
| Test | `make test` |
| Install the docs toolchain (Node.js 22.23.4+) | `make install-docs` |
| Serve the docs | `make doc` |
| Build the docs into `docs/dist/` | `make doc-build` |
| Check the docs: engine files, links and build | `make doc-check` |
| Run every pre-commit hook | `make pre-commit` |

CI runs `format-check`, `lint`, `lint-doc` and `test` through `.github/actions/validation`, and `doc-check` in a job of its own. Run those four before pushing, and `make doc-check` when the documentation changed.

## Directory Structure

```
main.py                  Entry point and console showcase
python_repo_template/    The package
utils/                   Cross-cutting helpers, not part of the package
configs/                 YAML files backing the config classes
tests/                   Pytest suite, mirroring the package
docs/                    Documentation site: pages, figures and the engine that builds them
diagrams/                Optional figure generation (see diagrams/README.md)
.claude/skills/          Repo-local agent skills
.github/                 Workflows and the shared validation action
```

## Configuration

Two base classes in `utils/configs.py`, chosen by one rule:

- **`YamlBaseSettings`** — one instance per process, and the environment may override the YAML. Use it for process-wide settings such as the log level.
- **`YamlBaseModel`** — many instances loaded from different files, never reading the environment. Use it for everything else.

`YamlBaseModel.from_yaml()` reads `DEFAULT_CONFIG_PATH` when called with no argument, and the given path otherwise. Classes without a `DEFAULT_CONFIG_PATH` require an explicit path.

The `@command` decorator in `utils/commands.py` turns a function into a `--config`-driven CLI. The function's first parameter must be annotated with a config class exposing `from_yaml`.

YAML files live in `configs/`.

## Console Output

- Use the helpers in `utils/console.py`. Never construct a bare `Console()` — a second console interleaves with the logging handler and disagrees on width.
- Diagnostics go through `logging`; `setup_logger` attaches a `RichHandler` bound to the same shared console.
- Text that may contain square brackets must go through `highlight_markers`, which escapes before styling.

## Docstrings and Linting

- Google convention. Types belong in the signature, never in the docstring — pydoclint is configured with `arg-type-hints-in-docstring = false`.
- pydoclint skips docstrings that are a single summary line. Anything longer must document every parameter.
- Line length is 100.
- Ruff's `D10*` rules are off, so docstrings are optional; when present they must be well-formed.

## Testing

- pytest with `pytest-xdist`; tests live in `tests/` and mirror the package.
- Test critical behaviour and edge cases. Coverage is reported, not targeted.

## Documentation

- The documentation is a static site built from the MDX pages in `docs/pages/` by the engine in `docs/app/`, a modified version of Thibaud Frere's [research-article-template](https://github.com/tfrere/research-article-template) (CC BY 4.0). `docs/pages/pages.json` lists the pages in menu order, each with a short label and the group the menu shows it under. `docs/components/KIT.md` documents the navigation and the components a page can use.
- The toolchain is a Node workspace under `docs/` and needs Node.js 22.23.4+; the docs commands stop on an older release. It is optional: `make dev` and the Python checks never use it. `make install-docs` installs it, `make doc` serves the site at `http://127.0.0.1:8031/`, and `make doc-check` verifies the engine files, checks the links and builds the site.
- `docs/app/` is the engine, maintained in python-repo-template and received by projects through the template sync. Never edit it by hand in a project: `docs/template-provenance.json` records the upstream commit, the changes made since and a hash of every engine file, and `make doc-check` fails when a file is edited, added or removed. Authors own `docs/pages/`, `docs/embeds/`, `docs/assets/` and `docs/components/`.
- No API reference is generated from docstrings; that is deliberate.
- A diagram in a page is an HTML embed in `docs/embeds/`, placed with `HtmlEmbed`. Mermaid fences belong only in plain Markdown files such as `README.md`.
- `docs/superpowers/` holds working notes, not documentation; the site does not publish it.
- No pre-commit hook builds the docs. CI runs `make doc-check`, so a broken link fails there.

## Diagrams

The optional `diagrams/` module generates figures. TikZ owns schematics — boxes,
arrows, maths. `xy` owns data charts. Matplotlib is not used.

- Build with `make diagrams`; `make -C diagrams check-tools` reports what is installed.
- `diagrams/generated/` is build output and is never committed. Copy reviewed
  figures to `docs/assets/image/`.
- Colours come from `inkcolor` in `diagrams/tikz/_shared/styles.tex`. Never
  hardcode a colour in a diagram source.
- `diagrams/README.md` has the removal checklist for projects that do not want it.

## Commits and PRs

- Conventional commits are enforced by `conventional-pre-commit`. Allowed types: `feat, fix, chore, build, ci, docs, perf, refactor, revert, style, test, merge`.
- Versions and the changelog belong to `python-semantic-release`. Never hand-edit a version.
- `no-commit-to-branch` blocks `development`, `staging` and `production`.

## Task Map

| I want to | Start here |
|---|---|
| Write or change Python or YAML | `.claude/skills/coding-guidelines/SKILL.md` |
| Review a change, branch or pull request | `.claude/skills/review-guidelines/SKILL.md` |
| Write docs, a PR description or a commit message | `.claude/skills/writing-guidelines/SKILL.md` |
| Add or change a documentation page | `.claude/skills/writing-guidelines/SKILL.md`, then `.claude/skills/page-frontmatter/SKILL.md` |
| Add a figure or a diagram to a documentation page | `.claude/skills/create-html-embed/SKILL.md` |
| Add a configuration class | `.claude/skills/new-config/SKILL.md`, then `utils/configs.py` |
| Pull in template updates | `.claude/skills/sync-template/SKILL.md`, then `docs/pages/updating-from-template.mdx` |
| Open or update a pull request | `.claude/skills/push-to-pr/SKILL.md`, `.claude/skills/update-pr-body/SKILL.md` |
| Change what the CLI prints | `utils/console.py` |
| Add an experiment logger backend | `utils/experiment_logger.py` |

## Skills

- **`coding-guidelines`** — the house style for Python and config files: design, file conventions, docstrings, modeling and tests.
- **`review-guidelines`** — how to scope a review, what to check, the finding format and the P0–P3 priorities.
- **`writing-guidelines`** — how to write docs, PR descriptions, commit messages and review reports for their reader.
- **`page-frontmatter`** — the frontmatter fields of a documentation page.
- **`create-html-embed`** — build a figure or a diagram for a documentation page as a self-contained HTML embed.
- **`sync-template`** — pull template changes into this project and resolve the merge.
- **`new-config`** — add a config class with its YAML file and round-trip test.
- **`push-to-pr`** — commit, push and open or update the PR for the current branch.
- **`update-pr-body`** — rewrite an existing PR description.

## Template Sync

This repository is generated from `python-repo-template`. `utils/update_template.py` squash-merges template changes onto an `update-template` branch, recording the sync point in `[tool.template]` in `pyproject.toml`.

Keep project-specific content inside the `## Project` section above; everything else is template-owned and will conflict on every sync if edited.

`AGENTS.md` is a symlink to this file, for agents that look for that name. Edit `CLAUDE.md` directly. Never replace, unlink, or write through `AGENTS.md`. On Windows, `git config core.symlinks true` is required for the symlink to check out correctly.
