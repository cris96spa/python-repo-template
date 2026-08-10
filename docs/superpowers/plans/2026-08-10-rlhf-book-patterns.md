# rlhf-book Patterns Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a shared Rich console layer, agent-facing project context with repo-local skills, and an optional removable diagrams module to `python-repo-template`, plus the pre-commit and CI repairs this surfaces.

**Architecture:** Three additive layers plus repairs. `utils/console.py` becomes the single owner of the Rich `Console`, which `utils/logger.py` then shares so log lines and panels cannot interleave. `CLAUDE.md` and `.claude/skills/` are documentation artifacts verified by running the commands they describe. `diagrams/` is a self-contained directory behind a `pyproject` extra, wired into the root `Makefile` with `$(wildcard diagrams)` so deleting the directory disables it silently.

**Tech Stack:** Python 3.12+, uv, make, Rich, pytest, ruff, pydoclint/flake8, pre-commit, TikZ/pdflatex, ImageMagick, pdf2svg, `xy` 0.0.6.

**Spec:** `docs/superpowers/specs/2026-08-10-rlhf-book-patterns-design.md`

## Global Constraints

- Python `>=3.12`. `typing.override` is already used in `utils/experiment_logger.py`.
- Line length 100. Ruff selects `E, W, I, F, D, C90, PGH, RUF, DOC` with the `google` docstring convention.
- Docstrings: types live in the signature, never in the docstring. pydoclint runs with `skip-checking-short-docstrings = true`, so a single-summary-line docstring is exempt from section checks; anything longer must document every parameter.
- Never invoke bare `python`. Always `uv run python`.
- Commit subjects must start with a type from the `conventional-pre-commit` allowlist: `feat, fix, chore, build, ci, docs, perf, refactor, revert, style, test, merge`.
- Comments earn their place: no narration of the following line, no justification of constant values, no explanatory blobs. Prefer renaming a symbol or extracting a function over writing a comment.
- Symbol names must be explicit. No abbreviations that need decoding.
- Tests cover critical behaviour and edge cases. Coverage is never a goal; do not add a test to move the number.
- `xy` is pinned `>=0.0.6,<0.1.0` and lives in `[project.optional-dependencies]`, never in a dependency group.
- Work on a feature branch. `main` is the default branch.

## Deviation from the spec

The spec gives chart scripts a `--theme` flag matching the TikZ side. This plan implements **light-only charts**: `xy` 0.0.6 offers no documented transparent-background control, and a flag that silently ignores its dark value is worse than no flag. Dark variants remain TikZ-only, and `diagrams/README.md` states this. Revisit if Task 7 discovers a supported mechanism.

## File Structure

| Path | Responsibility |
|---|---|
| `utils/console.py` | **Create.** Owns the shared `Console` and all presentation helpers. |
| `utils/logger.py` | **Modify.** Stops constructing its own `Console`; imports the shared one. |
| `main.py` | **Modify.** Showcase of every console helper. |
| `tests/test_console.py` | **Create.** Boundary tests for `format_metric` and `highlight_markers`, one render smoke test. |
| `tests/test_main.py` | **Create.** Smoke test that the showcase runs. |
| `CLAUDE.md` | **Create.** Agent-facing project context. |
| `AGENTS.md` | **Create.** Symlink to `CLAUDE.md`. |
| `.claude/skills/*/SKILL.md` | **Create.** Four repo-local skills. |
| `utils/post_checkout.py` | **Create.** Dependency-drift notice for the existing post-checkout hook; reads argv, falling back to the `PRE_COMMIT_*` environment variables pre-commit actually sets. |
| `tests/test_post_checkout.py` | **Create.** Argv and diff-detection edge cases, plus the environment-variable fallback and its precedence over argv. |
| `.pre-commit-config.yaml` | **Modify.** Remove the dead `update-progress` hook; fix `post-checkout`'s `entry` to run as a module so the import resolves. |
| `.github/workflows/main-validate.yaml` | **Modify.** Narrow the Python matrix. |
| `.gitignore` | **Modify.** Ignore local Claude settings and generated diagrams. |
| `pyproject.toml` | **Modify.** Add the `diagrams` extra. |
| `Makefile` | **Modify.** Single `PYTHON_TARGETS` variable; diagram delegation targets. |
| `diagrams/` | **Create.** Self-contained, removable diagram module. |

---

## Task 0: Branch

- [ ] **Step 1: Create the feature branch**

Branch from the commit carrying the spec and this plan, not from `main` — the
docs are not on `main` yet.

```bash
git checkout -b feat/rlhf-book-patterns
```

- [ ] **Step 2: Verify the environment is installed**

Run: `make dev`
Expected: dependencies sync and pre-commit hooks install

---

## Task 1: Console module

**Files:**
- Create: `utils/console.py`
- Test: `tests/test_console.py`

**Interfaces:**
- Consumes: nothing.
- Produces: module-level `console: Console`; `STYLE_HEADER`, `STYLE_INFO`, `STYLE_METRIC`, `STYLE_MUTED` (all `str`); `section_header(title: str, *, style: str = STYLE_HEADER, console: Console | None = None) -> None`; `summary_panel(fields: Mapping[str, Any], *, title: str, style: str = STYLE_INFO, console: Console | None = None) -> None`; `metrics_panel(metrics: Mapping[str, Any], *, title: str = "Metrics", style: str = STYLE_HEADER, console: Console | None = None) -> None`; `two_column_panel(rows: Mapping[str, str], *, title: str, label_width: int = 12, style: str = STYLE_MUTED, console: Console | None = None) -> None`; `new_progress_bar(*, console: Console | None = None, transient: bool = False) -> Progress`; `format_metric(value: Any) -> str`; `highlight_markers(text: str, styles: Mapping[str, str]) -> str`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_console.py`:

```python
from io import StringIO

from rich.console import Console

from utils.console import (
    format_metric,
    highlight_markers,
    metrics_panel,
    new_progress_bar,
    section_header,
    summary_panel,
    two_column_panel,
)


def make_test_console() -> tuple[Console, StringIO]:
    buffer = StringIO()
    return Console(file=buffer, force_terminal=False, width=80), buffer


def test_format_metric_uses_plain_decimals_at_the_threshold():
    assert format_metric(1e-3) == "0.0010"


def test_format_metric_uses_scientific_notation_below_the_threshold():
    assert format_metric(9.9e-4) == "9.90e-04"
    assert format_metric(-9.9e-4) == "-9.90e-04"


def test_format_metric_keeps_zero_as_a_plain_decimal():
    assert format_metric(0.0) == "0.0000"


def test_format_metric_passes_non_floats_through():
    assert format_metric(3) == "3"
    assert format_metric("n/a") == "n/a"


def test_highlight_markers_renders_bracketed_text_literally():
    test_console, buffer = make_test_console()

    test_console.print(highlight_markers("[bold] stays literal", {}))

    assert "[bold] stays literal" in buffer.getvalue()


def test_highlight_markers_styles_mapped_substrings():
    assert highlight_markers("a <|user|> b", {"<|user|>": "blue"}) == (
        "a [blue]<|user|>[/blue] b"
    )


def test_highlight_markers_styles_substrings_containing_brackets():
    test_console, buffer = make_test_console()

    test_console.print(highlight_markers("say [pad] now", {"[pad]": "red"}))

    assert "say [pad] now" in buffer.getvalue()


def test_helpers_render_to_an_injected_console():
    test_console, buffer = make_test_console()

    section_header("Phase", console=test_console)
    summary_panel({"Model": "demo"}, title="Configuration", console=test_console)
    metrics_panel({"loss": 0.5}, console=test_console)
    two_column_panel({"Question": "why"}, title="Sample", console=test_console)
    with new_progress_bar(console=test_console) as progress:
        progress.add_task("working", total=1)

    output = buffer.getvalue()
    assert "Phase" in output
    assert "Configuration" in output
    assert "0.5000" in output
    assert "Sample" in output
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_console.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'utils.console'`

- [ ] **Step 3: Write the implementation**

Create `utils/console.py`:

```python
"""Shared Rich console and the presentation helpers built on it."""

import os
from collections.abc import Mapping
from typing import Any

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

DEFAULT_CONSOLE_WIDTH = 180
SCIENTIFIC_NOTATION_THRESHOLD = 1e-3

STYLE_HEADER = "cyan"
STYLE_INFO = "magenta"
STYLE_METRIC = "green"
STYLE_MUTED = "dim"

console = Console(width=int(os.environ.get("COLUMNS", DEFAULT_CONSOLE_WIDTH)))


def _resolve(override: Console | None) -> Console:
    return override if override is not None else console


def format_metric(value: Any) -> str:
    """Render a metric value, falling back to scientific notation for tiny floats."""
    if isinstance(value, float):
        if 0 < abs(value) < SCIENTIFIC_NOTATION_THRESHOLD:
            return f"{value:.2e}"
        return f"{value:.4f}"
    return str(value)


def highlight_markers(text: str, styles: Mapping[str, str]) -> str:
    """Escape text as literal content, then style each mapped substring.

    Escaping before styling is what stops square brackets inside ``text`` from
    being interpreted as Rich markup.

    Args:
        text: Text to render literally, including any square brackets.
        styles: Mapping of literal substring to the Rich style to wrap it in.

    Returns:
        Markup-safe text with every mapped substring styled.
    """
    result = escape(text)
    for marker, style in styles.items():
        escaped_marker = escape(marker)
        result = result.replace(escaped_marker, f"[{style}]{escaped_marker}[/{style}]")
    return result


def section_header(
    title: str,
    *,
    style: str = STYLE_HEADER,
    console: Console | None = None,
) -> None:
    """Print a full-width rule introducing a new phase of output."""
    _resolve(console).rule(f"[bold {style}]{title}[/]", style=style)


def summary_panel(
    fields: Mapping[str, Any],
    *,
    title: str,
    style: str = STYLE_INFO,
    console: Console | None = None,
) -> None:
    """Print a panel of compact ``label: value`` lines."""
    body = "\n".join(f"[{STYLE_MUTED}]{label}:[/] {value}" for label, value in fields.items())
    _resolve(console).print(Panel(body, title=f"[bold {style}]{title}[/]", border_style=style))


def metrics_panel(
    metrics: Mapping[str, Any],
    *,
    title: str = "Metrics",
    style: str = STYLE_HEADER,
    console: Console | None = None,
) -> None:
    """Print a single-line panel of formatted metric values."""
    body = "    ".join(
        f"[bold {STYLE_METRIC}]{name}:[/] {format_metric(value)}" for name, value in metrics.items()
    )
    _resolve(console).print(Panel(body, title=f"[bold {style}]{title}[/]", border_style=style))


def two_column_panel(
    rows: Mapping[str, str],
    *,
    title: str,
    label_width: int = 12,
    style: str = STYLE_MUTED,
    console: Console | None = None,
) -> None:
    """Print a panel whose rows share a fixed-width label column."""
    table = Table(show_header=False, box=None, padding=(0, 1), show_edge=False)
    table.add_column("label", style=STYLE_MUTED, width=label_width)
    table.add_column("value")
    for label, value in rows.items():
        table.add_row(f"{label}:", value)
    _resolve(console).print(
        Panel(table, title=f"[bold {STYLE_HEADER}]{title}[/]", border_style=style)
    )


def new_progress_bar(
    *,
    console: Console | None = None,
    transient: bool = False,
) -> Progress:
    """Create a progress bar with a spinner, bar, completed count and elapsed time."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=_resolve(console),
        transient=transient,
    )
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_console.py -v`
Expected: PASS, 8 passed

- [ ] **Step 5: Run the lint gates**

Run: `uv run ruff format utils/console.py tests/test_console.py && uv run ruff check utils/console.py tests/test_console.py && uv run flake8 utils/console.py`
Expected: no findings

- [ ] **Step 6: Commit**

```bash
git add utils/console.py tests/test_console.py
git commit -m "feat: add shared Rich console and presentation helpers"
```

---

## Task 2: Logger integration and main.py showcase

**Files:**
- Modify: `utils/logger.py:9-11` (imports), `utils/logger.py:53-58` (console construction and handler list)
- Modify: `main.py` (whole file)
- Test: `tests/test_main.py`

**Interfaces:**
- Consumes: `utils.console.console`, `section_header`, `summary_panel`, `metrics_panel`, `two_column_panel`, `new_progress_bar` from Task 1.
- Produces: `main.main(number: int) -> None`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_main.py`:

```python
from main import main


def test_main_runs_the_showcase(capsys):
    main(5)

    output = capsys.readouterr().out
    assert "Random sum demo" in output
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_main.py -v`
Expected: FAIL — `ImportError: cannot import name 'main' from 'main'`

- [ ] **Step 3: Point the logger at the shared console**

In `utils/logger.py`, delete the `from rich.console import Console` import and add `from utils.console import console` below the existing `from rich.logging import RichHandler` import, so the import block reads:

```python
import logging
import os
import random
import string
import threading
from datetime import datetime
from pathlib import Path

from rich import traceback
from rich.logging import RichHandler

from utils.console import console
```

Then replace these lines in `setup_logger`:

```python
    console_columns = int(os.environ.get("COLUMNS", 180))
    console = Console(width=console_columns)

    handlers: list[logging.Handler] = [
        RichHandler(show_time=False, console=console),
    ]
```

with:

```python
    handlers: list[logging.Handler] = [
        RichHandler(show_time=False, console=console),
    ]
```

- [ ] **Step 4: Rewrite main.py as the showcase**

Replace the whole of `main.py`:

```python
import argparse
import logging

from python_repo_template.func import random_sum
from utils.console import (
    metrics_panel,
    new_progress_bar,
    section_header,
    summary_panel,
    two_column_panel,
)
from utils.logger import setup_logger

SAMPLE_COUNT = 5

logger = logging.getLogger(__name__)


def main(number: int) -> None:
    """Draw random sums for the given number and report them through the console helpers.

    Args:
        number: The number each random draw is added to.
    """
    section_header("Random sum demo")
    summary_panel(
        {"Input number": number, "Samples": SAMPLE_COUNT},
        title="Run configuration",
    )

    samples: list[int] = []
    with new_progress_bar() as progress:
        task = progress.add_task("sampling", total=SAMPLE_COUNT)
        for _ in range(SAMPLE_COUNT):
            samples.append(random_sum(number))
            progress.advance(task)

    logger.info("Drew %d samples", SAMPLE_COUNT)

    metrics_panel(
        {
            "min": min(samples),
            "mean": sum(samples) / len(samples),
            "max": max(samples),
        }
    )
    two_column_panel(
        {"Input": str(number), "Samples": ", ".join(str(sample) for sample in samples)},
        title="Draws",
    )


if __name__ == "__main__":
    setup_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument("--number", type=int, required=True, help="Input number")
    main(parser.parse_args().number)
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `uv run pytest tests/test_main.py -v`
Expected: PASS

- [ ] **Step 6: Verify the showcase renders end to end**

Run: `uv run python main.py --number 5`
Expected: a cyan rule titled `Random sum demo`, a magenta `Run configuration` panel, a completed progress bar reading `5/5`, one `INFO` log line, a cyan `Metrics` panel, and a `Draws` panel with an aligned label column.

- [ ] **Step 7: Run the full gate**

Run: `make format-check && make lint && make lint-doc && make test`
Expected: all four pass

- [ ] **Step 8: Commit**

```bash
git add utils/logger.py main.py tests/test_main.py
git commit -m "refactor: share one Rich console between logging and panels"
```

---

## Task 3: CLAUDE.md, AGENTS.md and gitignore

**Files:**
- Create: `CLAUDE.md`
- Create: `AGENTS.md` (symlink)
- Modify: `.gitignore` (append)

**Interfaces:**
- Consumes: the console API from Task 1 (referenced in the `## Console Output` section).
- Produces: nothing importable. Later tasks append the `## Diagrams` section.

- [ ] **Step 1: Write CLAUDE.md**

Create `CLAUDE.md`:

````markdown
# Project Context

## Project

<!-- Derived projects own this section. Everything below it comes from the template. -->

- **Purpose:** A template for Python projects. Replace this with what your project does.
- **Package:** `python_repo_template` — rename it and the `PROJECT_NAME` variable in the `Makefile` together.
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
| Serve the docs | `make doc` |
| Run every pre-commit hook | `make pre-commit` |

CI runs `format-check`, `lint`, `lint-doc` and `test` through `.github/actions/validation`. Run those four before pushing.

## Directory Structure

```
main.py                  Entry point and console showcase
python_repo_template/    The package
utils/                   Cross-cutting helpers, not part of the package
configs/                 YAML files backing the config classes
tests/                   Pytest suite, mirroring the package
docs/                    properdocs/mkdocs sources
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

- properdocs over mkdocs-material. `make doc` serves it locally.
- API pages are generated by `utils/build_api_docs.py` through `mkdocs-gen-files`. To exclude or rename a page, edit `SKIP_FILENAMES`, `SKIP_PATHS` or the rename map in that script. Never hand-write files under `docs/api/`.
- A pre-commit hook builds the docs, so a broken cross-reference fails the commit.
- MathJax and mermaid fences are both available.

## Commits and PRs

- Conventional commits are enforced by `conventional-pre-commit`. Allowed types: `feat, fix, chore, build, ci, docs, perf, refactor, revert, style, test, merge`.
- Versions and the changelog belong to `python-semantic-release`. Never hand-edit a version.
- `no-commit-to-branch` blocks `development`, `staging` and `production`.

## Task Map

| I want to | Start here |
|---|---|
| Add a configuration class | `.claude/skills/new-config/SKILL.md`, then `utils/configs.py` |
| Pull in template updates | `.claude/skills/sync-template/SKILL.md`, then `docs/updating-from-template.md` |
| Open or update a pull request | `.claude/skills/push-to-pr/SKILL.md`, `.claude/skills/update-pr-body/SKILL.md` |
| Change what the CLI prints | `utils/console.py` |
| Add or exclude an API doc page | `utils/build_api_docs.py` |
| Add an experiment logger backend | `utils/experiment_logger.py` |

## Skills

- **`sync-template`** — pull template changes into this project and resolve the merge.
- **`new-config`** — add a config class with its YAML file and round-trip test.
- **`push-to-pr`** — commit, push and open or update the PR for the current branch.
- **`update-pr-body`** — rewrite an existing PR description.

## Template Sync

This repository is generated from `python-repo-template`. `utils/update_template.py` squash-merges template changes onto an `update-template` branch, recording the sync point in `[tool.template]` in `pyproject.toml`.

Keep project-specific content inside the `## Project` section above; everything else is template-owned and will conflict on every sync if edited.

`AGENTS.md` is a symlink to this file, for agents that look for that name. Edit `CLAUDE.md` directly. Never replace, unlink, or write through `AGENTS.md`. On Windows, `git config core.symlinks true` is required for the symlink to check out correctly.
````

- [ ] **Step 2: Create the AGENTS.md symlink**

```bash
ln -s CLAUDE.md AGENTS.md
```

- [ ] **Step 3: Verify the symlink resolves**

Run: `test -L AGENTS.md && head -1 AGENTS.md`
Expected: `# Project Context`

- [ ] **Step 4: Append the gitignore entries**

Append to `.gitignore`:

```gitignore

# Claude Code per-developer settings
.claude/settings.local.json
```

- [ ] **Step 5: Verify the symlink hook accepts it**

Run: `uv run pre-commit run check-symlinks --all-files`
Expected: Passed

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md AGENTS.md .gitignore
git commit -m "docs: add agent-facing project context"
```

---

## Task 4: sync-template and new-config skills

**Files:**
- Create: `.claude/skills/sync-template/SKILL.md`
- Create: `.claude/skills/new-config/SKILL.md`

**Interfaces:**
- Consumes: `CLAUDE.md` from Task 3 (its `## Skills` section already names these two).
- Produces: nothing importable.

- [ ] **Step 1: Write the sync-template skill**

Create `.claude/skills/sync-template/SKILL.md`:

````markdown
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
````

- [ ] **Step 2: Write the new-config skill**

Create `.claude/skills/new-config/SKILL.md`:

````markdown
---
name: new-config
description: Add a configuration class with its YAML file and round-trip test, following the template's config conventions. Use when asked to add, define, or scaffold a config.
allowed-tools: Read, Edit, Write, Bash(uv:*), Bash(make:*)
---

# New Config

## Pick the base class

- **`YamlBaseSettings`** — one instance per process, and environment variables
  may override the YAML. Process-wide settings only, such as the log level.
- **`YamlBaseModel`** — many instances loaded from different files, never
  reading the environment. Everything else.

When in doubt use `YamlBaseModel`. Environment variables are a flat,
process-global namespace and cannot express per-instance overrides.

## Write the class

Add it to `utils/configs.py` unless it belongs to a specific package module.
Every field carries a `Field(description=...)`. Set `DEFAULT_CONFIG_PATH` only
when the config has one canonical file.

```python
class ReportConfig(YamlBaseModel):
    """Configuration for the report generator."""

    DEFAULT_CONFIG_PATH: ClassVar[Path] = Path("configs/report.yaml")

    output_dir: Path = Field(description="Directory the report is written to.")
    include_charts: bool = Field(
        description="Whether to render charts alongside the tables.",
        default=True,
    )
```

## Write the YAML

Create `configs/<name>.yaml` with every field populated, defaults included, so
the file doubles as documentation:

```yaml
output_dir: artifacts/reports
include_charts: true
```

## Write the test

Add to `tests/test_configs.py`, creating it if absent. Test that the default
path loads and that a round trip preserves the data — not that pydantic works.

```python
def test_report_config_round_trips(tmp_path):
    config = ReportConfig.from_yaml()
    destination = tmp_path / "report.yaml"

    config.to_yaml(destination)

    assert ReportConfig.from_yaml(destination) == config
```

If the class defines no `DEFAULT_CONFIG_PATH`, assert instead that `from_yaml()`
with no argument raises `ValueError`.

## Verify

```bash
uv run ruff format utils/configs.py tests/test_configs.py
make lint && make lint-doc && make test
```

## Conventions that trip people up

- Types belong in the signature, never in the docstring.
- A docstring longer than one summary line must document every parameter.
- `YamlBaseSettings` subclasses set `model_config = SettingsConfigDict(yaml_file=...)`;
  `YamlBaseModel` subclasses set `DEFAULT_CONFIG_PATH`. They are not interchangeable.
````

- [ ] **Step 3: Verify the frontmatter parses**

Run: `uv run python -c "import pathlib, yaml; [print(p, yaml.safe_load(p.read_text().split('---')[1])['name']) for p in pathlib.Path('.claude/skills').glob('*/SKILL.md')]"`
Expected: two lines, each printing the path and the matching skill name

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/sync-template .claude/skills/new-config
git commit -m "docs: add sync-template and new-config skills"
```

---

## Task 5: push-to-pr and update-pr-body skills

**Files:**
- Create: `.claude/skills/push-to-pr/SKILL.md`
- Create: `.claude/skills/update-pr-body/SKILL.md`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: nothing importable.

- [ ] **Step 1: Write the push-to-pr skill**

Create `.claude/skills/push-to-pr/SKILL.md`:

````markdown
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

```bash
git add -A
git commit -m "$(cat <<'EOF'
feat: short imperative summary

Why the change was needed, and anything a reviewer cannot infer from the diff.
EOF
)"
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
````

- [ ] **Step 2: Write the update-pr-body skill**

Create `.claude/skills/update-pr-body/SKILL.md`:

````markdown
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
````

- [ ] **Step 3: Ignore the pytest report artifact**

`make test` writes `tests_report.xml` to the repo root, and `push-to-pr` runs
`git add -A` after it. Add `tests_report.xml` to `.gitignore` on the line
immediately after the existing `coverage.xml` entry.

- [ ] **Step 4: Verify all four skills parse**

Run: `uv run python -c "import pathlib, yaml; [print(yaml.safe_load(p.read_text().split('---')[1])['name']) for p in sorted(pathlib.Path('.claude/skills').glob('*/SKILL.md'))]"`
Expected: `new-config`, `push-to-pr`, `sync-template`, `update-pr-body`

- [ ] **Step 5: Commit**

```bash
git add .gitignore .claude/skills/push-to-pr .claude/skills/update-pr-body
git commit -m "fix: ignore the pytest report artifact and derive the default branch in push-to-pr"
```

---

## Task 6: Pre-commit repairs, post-checkout notice, CI matrix

**Files:**
- Create: `utils/post_checkout.py`
- Test: `tests/test_post_checkout.py`
- Modify: `.pre-commit-config.yaml` (remove the `update-progress` hook block)
- Modify: `.github/workflows/main-validate.yaml:15-17`

**Interfaces:**
- Consumes: `utils.console.console` from Task 1.
- Produces: `utils.post_checkout.dependency_files_changed(previous: str, current: str) -> list[str]`, `utils.post_checkout.main(argv: Sequence[str]) -> int`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_post_checkout.py`:

```python
import subprocess
from pathlib import Path

import pytest

from utils.post_checkout import dependency_files_changed, main

BRANCH_CHECKOUT = "1"
FILE_CHECKOUT = "0"


def run_git(repository: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@pytest.fixture(autouse=True)
def clear_pre_commit_environment(monkeypatch):
    monkeypatch.delenv("PRE_COMMIT_FROM_REF", raising=False)
    monkeypatch.delenv("PRE_COMMIT_TO_REF", raising=False)
    monkeypatch.delenv("PRE_COMMIT_CHECKOUT_TYPE", raising=False)


@pytest.fixture
def repository(tmp_path, monkeypatch):
    run_git(tmp_path, "init", "-q")
    run_git(tmp_path, "config", "user.email", "test@example.com")
    run_git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
    (tmp_path / "README.md").write_text("first\n")
    run_git(tmp_path, "add", "-A")
    run_git(tmp_path, "commit", "-q", "-m", "chore: first")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_detects_a_changed_dependency_file(repository):
    before = run_git(repository, "rev-parse", "HEAD")
    (repository / "pyproject.toml").write_text("[project]\nname = 'demo2'\n")
    run_git(repository, "commit", "-q", "-am", "chore: bump")
    after = run_git(repository, "rev-parse", "HEAD")

    assert dependency_files_changed(before, after) == ["pyproject.toml"]


def test_ignores_unrelated_changes(repository):
    before = run_git(repository, "rev-parse", "HEAD")
    (repository / "README.md").write_text("second\n")
    run_git(repository, "commit", "-q", "-am", "docs: edit")
    after = run_git(repository, "rev-parse", "HEAD")

    assert dependency_files_changed(before, after) == []


def test_file_checkout_prints_nothing(repository, capsys):
    head = run_git(repository, "rev-parse", "HEAD")

    assert main([head, head, FILE_CHECKOUT]) == 0
    assert capsys.readouterr().out == ""


def test_branch_checkout_with_a_changed_dependency_file_prints_a_notice(repository, capsys):
    before = run_git(repository, "rev-parse", "HEAD")
    (repository / "pyproject.toml").write_text("[project]\nname = 'demo2'\n")
    run_git(repository, "commit", "-q", "-am", "chore: bump")
    after = run_git(repository, "rev-parse", "HEAD")

    assert main([before, after, BRANCH_CHECKOUT]) == 0
    assert "make dev" in capsys.readouterr().out


def test_missing_arguments_exit_zero_without_raising(capsys):
    assert main([]) == 0
    assert capsys.readouterr().out == ""


def test_unknown_revisions_exit_zero_without_raising(repository, capsys):
    assert main(["deadbeef", "cafebabe", BRANCH_CHECKOUT]) == 0
    assert capsys.readouterr().out == ""


def test_branch_checkout_via_environment_prints_a_notice(repository, monkeypatch, capsys):
    before = run_git(repository, "rev-parse", "HEAD")
    (repository / "pyproject.toml").write_text("[project]\nname = 'demo2'\n")
    run_git(repository, "commit", "-q", "-am", "chore: bump")
    after = run_git(repository, "rev-parse", "HEAD")
    monkeypatch.setenv("PRE_COMMIT_FROM_REF", before)
    monkeypatch.setenv("PRE_COMMIT_TO_REF", after)
    monkeypatch.setenv("PRE_COMMIT_CHECKOUT_TYPE", BRANCH_CHECKOUT)

    assert main([]) == 0
    assert "make dev" in capsys.readouterr().out


def test_file_checkout_type_via_environment_prints_nothing(repository, monkeypatch, capsys):
    before = run_git(repository, "rev-parse", "HEAD")
    (repository / "pyproject.toml").write_text("[project]\nname = 'demo2'\n")
    run_git(repository, "commit", "-q", "-am", "chore: bump")
    after = run_git(repository, "rev-parse", "HEAD")
    monkeypatch.setenv("PRE_COMMIT_FROM_REF", before)
    monkeypatch.setenv("PRE_COMMIT_TO_REF", after)
    monkeypatch.setenv("PRE_COMMIT_CHECKOUT_TYPE", FILE_CHECKOUT)

    assert main([]) == 0
    assert capsys.readouterr().out == ""


def test_argv_takes_precedence_over_conflicting_environment_variables(
    repository, monkeypatch, capsys
):
    before = run_git(repository, "rev-parse", "HEAD")
    (repository / "pyproject.toml").write_text("[project]\nname = 'demo2'\n")
    run_git(repository, "commit", "-q", "-am", "chore: bump")
    after = run_git(repository, "rev-parse", "HEAD")
    monkeypatch.setenv("PRE_COMMIT_FROM_REF", before)
    monkeypatch.setenv("PRE_COMMIT_TO_REF", after)
    monkeypatch.setenv("PRE_COMMIT_CHECKOUT_TYPE", FILE_CHECKOUT)

    assert main([before, after, BRANCH_CHECKOUT]) == 0
    assert "make dev" in capsys.readouterr().out
```

The `clear_pre_commit_environment` autouse fixture at the top prevents the argv-only
tests from picking up `PRE_COMMIT_*` variables leaking in from an outer pre-commit run.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_post_checkout.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'utils.post_checkout'`

- [ ] **Step 3: Write the implementation**

Create `utils/post_checkout.py`. Note that pre-commit does **not** forward git's three
positional post-checkout arguments to a local hook's `entry` as `sys.argv` — it
consumes them internally (`pre_commit/commands/hook_impl.py`) and re-exposes them only
as `PRE_COMMIT_FROM_REF` / `PRE_COMMIT_TO_REF` / `PRE_COMMIT_CHECKOUT_TYPE` environment
variables (`pre_commit/commands/run.py`). `main` must read both sources, argv first, or
the hook can never fire when pre-commit is what invokes it — which is the only way it
runs in practice, since `default_install_hook_types` includes `post-checkout`.

```python
"""Post-checkout hook that flags dependency drift after a branch switch."""

import os
import subprocess
import sys
from collections.abc import Sequence

from utils.console import STYLE_HEADER, console

DEPENDENCY_FILES = ("pyproject.toml", "uv.lock")
BRANCH_CHECKOUT_FLAG = "1"


def dependency_files_changed(previous: str, current: str) -> list[str]:
    """List the dependency files that differ between two revisions.

    Args:
        previous: Revision checked out before the switch.
        current: Revision checked out after the switch.

    Returns:
        The changed dependency file paths, empty when nothing relevant changed.
    """
    completed = subprocess.run(
        ["git", "diff", "--name-only", previous, current, "--", *DEPENDENCY_FILES],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in completed.stdout.splitlines() if line]


def _hook_arguments(argv: Sequence[str]) -> tuple[str, str, str] | None:
    """Resolve the previous revision, the new revision and the checkout flag.

    pre-commit does not forward git's positional arguments to hooks. It consumes
    them and re-exposes them as ``PRE_COMMIT_*`` environment variables, so both
    sources have to be read.

    Args:
        argv: Positional arguments, as git passes them to a raw hook.

    Returns:
        The three values, or ``None`` when neither source supplies them.
    """
    if len(argv) >= 3:
        return argv[0], argv[1], argv[2]
    previous = os.environ.get("PRE_COMMIT_FROM_REF")
    current = os.environ.get("PRE_COMMIT_TO_REF")
    checkout_type = os.environ.get("PRE_COMMIT_CHECKOUT_TYPE")
    if previous and current and checkout_type:
        return previous, current, checkout_type
    return None


def main(argv: Sequence[str]) -> int:
    """Print a notice when a branch switch changed the dependency files.

    Reads the previous revision, the new revision, and the branch-checkout flag
    from argv when given, falling back to the ``PRE_COMMIT_FROM_REF`` /
    ``PRE_COMMIT_TO_REF`` / ``PRE_COMMIT_CHECKOUT_TYPE`` environment variables
    pre-commit sets, since pre-commit never forwards them as positional arguments.

    Args:
        argv: The previous revision, the new revision, and git's branch-checkout flag.

    Returns:
        Always zero, so a checkout never looks broken because of this hook.
    """
    arguments = _hook_arguments(argv)
    if arguments is None:
        return 0

    previous, current, checkout_type = arguments
    if checkout_type != BRANCH_CHECKOUT_FLAG:
        return 0

    try:
        changed = dependency_files_changed(previous, current)
    except (subprocess.CalledProcessError, OSError):
        return 0

    if changed:
        console.print(
            f"[bold {STYLE_HEADER}]{', '.join(changed)} changed on this branch — "
            f"run `make dev` to resync dependencies.[/]"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_post_checkout.py -v`
Expected: PASS, 9 passed

- [ ] **Step 5: Remove the dead update-progress hook and fix the post-checkout entry**

Delete this block from `.pre-commit-config.yaml`:

```yaml
  - repo: local
    hooks:
      - id: update-progress
        name: Update progress dashboard
        description: Regenerate difficulty counters and NeetCode 250 tracking in README and docs/index.md
        entry: uv run python utils/update_progress.py
        language: system
        pass_filenames: false
        files: '^leetcode/(Easy|Medium|Hard)/.*\.py$'
        stages: [pre-commit]
```

In the same file, change the `post-checkout` hook's `entry` from:

```yaml
        entry: uv run python utils/post_checkout.py
```

to:

```yaml
        entry: uv run python -m utils.post_checkout
```

Running the script by file path puts `utils/` — not the repository root — on
`sys.path[0]`, so `from utils.console import ...` raises `ModuleNotFoundError` and the
hook crashes on every real checkout. Running it as a module (`-m utils.post_checkout`)
resolves the import correctly because pre-commit always runs local hooks with the
repository root as the working directory.

- [ ] **Step 6: Verify every hook resolves**

Run: `uv run pre-commit run --all-files`
Expected: every hook reports Passed or Skipped; no hook fails with a missing-file error.
Note that `post-checkout` itself is scoped to `stages: [post-checkout]`, so it does not
run as part of this default-stage, all-files pass — verify it separately with a real
`git checkout` in a throwaway repository (install hooks with `pre-commit install -t
post-checkout`, commit a change to `pyproject.toml` on a branch, then check out back)
and confirm the notice prints.

- [ ] **Step 7: Commit the repairs**

```bash
git add utils/post_checkout.py tests/test_post_checkout.py .pre-commit-config.yaml
git commit -m "fix: repair post-checkout hook and drop the dead update-progress hook"
```

- [ ] **Step 7b: Verify with a real checkout, then commit the environment-variable fix**

If Step 3 was implemented with the `_hook_arguments` env-var fallback from the start,
this step has nothing to do. If it was implemented argv-only first and the gap was
caught later (as happened here), add the fallback and its three tests, then verify with
a real checkout before committing:

```bash
uv run pytest tests/test_post_checkout.py -v      # 9 passed
uv run pytest tests -n auto -q                    # full suite
make format-check && make lint && make lint-doc
```

Then reproduce a real checkout: build a throwaway repo, copy in `utils/console.py` and
`utils/post_checkout.py`, add a minimal `.pre-commit-config.yaml` with just the
`post-checkout` hook (`entry: ... -m utils.post_checkout`), `pre-commit install -t
post-checkout`, commit a change to `pyproject.toml` on a branch, and check out back to
confirm the resync notice actually prints.

```bash
git add utils/post_checkout.py tests/test_post_checkout.py docs/superpowers/plans/2026-08-10-rlhf-book-patterns.md
git commit -m "fix: read post-checkout refs from the environment pre-commit sets"
```

- [ ] **Step 8: Narrow the CI Python matrix**

In `.github/workflows/main-validate.yaml`, replace:

```yaml
        python-version: ["3.10", "3.11", "3.12", "3.13"]
```

with:

```yaml
        python-version: ["3.12", "3.13"]
```

- [ ] **Step 9: Commit the CI change**

```bash
git add .github/workflows/main-validate.yaml
git commit -m "ci: test only the Python versions the project supports"
```

---

## Task 7: xy headless export spike

**Files:**
- No files committed. This task produces a decision.

**Interfaces:**
- Consumes: nothing.
- Produces: a go/no-go for Task 9.

- [ ] **Step 1: Install xy in an isolated environment**

Run: `uv run --with 'xy>=0.0.6,<0.1.0' --no-project python -c "import xy; print(xy.__version__)"`
Expected: a version string in the `0.0.x` range. If this fails to install, record the error and stop — Task 9 is cancelled.

- [ ] **Step 2: Attempt a headless SVG export**

Run:

```bash
cd "$(mktemp -d)" && uv run --with 'xy>=0.0.6,<0.1.0' --no-project python -c "
import xy
chart = xy.line_chart(xy.line([1, 2, 3, 4, 5], [120, 180, 165, 240, 310]))
chart.to_svg('spike.svg')
print(open('spike.svg').read(120))
"
```

Expected: SVG markup printed, no display or browser required.

- [ ] **Step 3: Attempt a headless PNG export**

Run the same snippet with `chart.to_png('spike.png')`, then check the file is a PNG:

```bash
file spike.png
```

Expected: `PNG image data`

- [ ] **Step 4: Record the outcome**

Report to the user:

- Both exports succeed → proceed to Task 9 as written.
- Either fails → Task 9 is cancelled. Task 8 still ships; `diagrams/charts/` and the `charts` Makefile target are omitted, and `diagrams/README.md` records that charting is deferred. Quote the actual error.

---

## Task 8: Diagrams module — TikZ core

**Files:**
- Create: `diagrams/Makefile`
- Create: `diagrams/README.md`
- Create: `diagrams/tikz/_shared/styles.tex`
- Create: `diagrams/tikz/example/flow_tikz.tex`
- Modify: `Makefile:3-4` (targets variable) and the `format`/`format-check`/`lint`/`lint-fix`/`lint-doc` recipes; append the delegation targets
- Modify: `.gitignore` (append)
- Modify: `CLAUDE.md` (insert a `## Diagrams` section before `## Commits and PRs`)

**Interfaces:**
- Consumes: `CLAUDE.md` from Task 3.
- Produces: make targets `diagrams`, `diagrams-clean`, `install-diagrams` at the repo root; `make -C diagrams` targets `all`, `tikz`, `tikz-dark`, `dark`, `check-tools`, `clean`, `help`.

- [ ] **Step 1: Write the shared TikZ styles**

Create `diagrams/tikz/_shared/styles.tex`:

```tex
\usetikzlibrary{arrows.meta, positioning}

\providecommand{\figdark}{0}

\ifnum\figdark=1
  \definecolor{inkcolor}{HTML}{E6E6E6}
\else
  \definecolor{inkcolor}{HTML}{1A1A1A}
\fi

\tikzset{
  node distance=12mm,
  block/.style={
    draw=inkcolor,
    text=inkcolor,
    rounded corners=2pt,
    minimum width=26mm,
    minimum height=10mm,
    align=center
  },
  flow/.style={
    draw=inkcolor,
    -{Stealth[length=2.4mm]},
    shorten >=5pt,
    thick
  },
  edgelabel/.style={text=inkcolor, font=\small, midway, above}
}
```

- [ ] **Step 2: Write the example diagram**

Create `diagrams/tikz/example/flow_tikz.tex`:

```tex
\documentclass[border=4pt]{standalone}
\usepackage{lmodern}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{tikz}
\input{styles.tex}

\begin{document}
\begin{tikzpicture}
  \node[block] (input) {Input};
  \node[block, right=of input] (process) {Process};
  \node[block, right=of process] (output) {Output};
  \draw[flow] (input) -- node[edgelabel] {parse} (process);
  \draw[flow] (process) -- node[edgelabel] {render} (output);
\end{tikzpicture}
\end{document}
```

- [ ] **Step 3: Write the diagrams Makefile**

Create `diagrams/Makefile`:

```makefile
.PHONY: all tikz tikz-dark dark check-tools clean help

GENERATED_DIR := generated
TIKZ_SHARED := $(abspath tikz/_shared)
TIKZ_DENSITY ?= 800
PDFLATEX ?= pdflatex

help: # print all the available targets
	@echo "\nAvailable targets:\n"
	@grep -E '^[a-zA-Z_-]+:.*?# .*$$' $(MAKEFILE_LIST) | sed 's/:.*#/\t/' | column -t -s '	' ; echo

all: tikz # build every diagram

check-tools: # report which diagram tools are installed
	@for tool in $(PDFLATEX) magick pdf2svg; do \
		if command -v $$tool > /dev/null; then \
			echo "  found    $$tool"; \
		else \
			echo "  MISSING  $$tool"; \
		fi; \
	done

tikz: | $(GENERATED_DIR) # compile every tikz source to pdf, png and svg
	@mkdir -p $(GENERATED_DIR)/pdf $(GENERATED_DIR)/png $(GENERATED_DIR)/svg
	@for texfile in $$(find tikz -name '*_tikz.tex' | sort); do \
		dir=$$(dirname "$$texfile"); \
		base=$$(basename "$$texfile" .tex); \
		echo "Compiling $$base"; \
		( cd "$$dir" && TEXINPUTS=".:$(TIKZ_SHARED):" $(PDFLATEX) -interaction=nonstopmode "$$base.tex" > /dev/null 2>&1 ); \
		if [ -f "$$dir/$$base.pdf" ]; then \
			cp "$$dir/$$base.pdf" $(GENERATED_DIR)/pdf/$$base.pdf; \
			if command -v magick > /dev/null; then \
				magick -density $(TIKZ_DENSITY) "$$dir/$$base.pdf" -trim -quality 100 $(GENERATED_DIR)/png/$$base.png; \
			else \
				echo "  skipped png: magick not installed"; \
			fi; \
			if command -v pdf2svg > /dev/null; then \
				pdf2svg "$$dir/$$base.pdf" $(GENERATED_DIR)/svg/$$base.svg; \
			else \
				echo "  skipped svg: pdf2svg not installed"; \
			fi; \
		else \
			echo "  FAILED $$base"; \
			tail -n 20 "$$dir/$$base.log" 2>/dev/null; \
		fi; \
		rm -f "$$dir/$$base.aux" "$$dir/$$base.log" "$$dir/$$base.pdf"; \
	done

tikz-dark: | $(GENERATED_DIR) # compile every tikz source to a transparent dark png
	@mkdir -p $(GENERATED_DIR)/png
	@for texfile in $$(find tikz -name '*_tikz.tex' | sort); do \
		dir=$$(dirname "$$texfile"); \
		base=$$(basename "$$texfile" .tex); \
		echo "Compiling $$base (dark)"; \
		( cd "$$dir" && TEXINPUTS=".:$(TIKZ_SHARED):" $(PDFLATEX) -interaction=nonstopmode -jobname "$$base-dark" "\def\figdark{1}\input{$$base.tex}" > /dev/null 2>&1 ); \
		if [ -f "$$dir/$$base-dark.pdf" ] && command -v magick > /dev/null; then \
			magick -density $(TIKZ_DENSITY) -background none "$$dir/$$base-dark.pdf" -trim -quality 100 $(GENERATED_DIR)/png/$$base-dark.png; \
		else \
			echo "  FAILED $$base-dark"; \
			tail -n 20 "$$dir/$$base-dark.log" 2>/dev/null; \
		fi; \
		rm -f "$$dir/$$base-dark.aux" "$$dir/$$base-dark.log" "$$dir/$$base-dark.pdf"; \
	done

dark: tikz-dark # build every dark-mode variant

$(GENERATED_DIR):
	mkdir -p $(GENERATED_DIR)

clean: # remove generated output and latex build artifacts
	rm -rf $(GENERATED_DIR)
	find tikz \( -name '*.pdf' -o -name '*.aux' -o -name '*.log' \) -delete
```

- [ ] **Step 4: Wire the root Makefile**

In `Makefile`, replace:

```makefile
PYTHON_FORMAT_TARGETS ?= main.py $(PROJECT_NAME) tests utils
```

with:

```makefile
PYTHON_TARGETS ?= main.py $(PROJECT_NAME) tests utils $(wildcard diagrams)
```

Then replace every occurrence of `$(PYTHON_FORMAT_TARGETS)` with `$(PYTHON_TARGETS)` in the `format` and `format-check` recipes, and replace `$(PROJECT_NAME) utils tests` with `$(PYTHON_TARGETS)` in the `lint`, `lint-fix` and `lint-doc` recipes.

Append these targets to the end of the file:

```makefile

install-diagrams: # install the optional diagram toolchain
	uv sync --extra diagrams

diagrams: # build every diagram
	$(MAKE) -C diagrams all

diagrams-clean: # remove generated diagram output
	$(MAKE) -C diagrams clean
```

- [ ] **Step 5: Add the diagrams extra to pyproject.toml**

Insert after the `dependencies = [...]` block in `[project]`:

```toml
[project.optional-dependencies]
diagrams = [
    "xy>=0.0.6,<0.1.0",
]
```

- [ ] **Step 6: Ignore generated output**

Append to `.gitignore`:

```gitignore

# Generated diagram output
diagrams/generated/
```

- [ ] **Step 7: Write the diagrams README**

Create `diagrams/README.md`:

````markdown
# Diagrams

An optional module for generating figures. Delete it whenever a project does not
need it — see [Removing this module](#removing-this-module).

## Tool boundary

- **TikZ** owns schematics: boxes, arrows, annotated flows, anything with maths.
- **xy** owns data charts: line, scatter, density.

Matplotlib is deliberately absent. `xy` is a charting library, not a drawing
canvas — it has no equivalent of matplotlib's `patches` API — so TikZ covers
everything xy cannot.

## Layout

```
tikz/
  _shared/styles.tex   shared styles, found through TEXINPUTS
  <topic>/*_tikz.tex   one file per diagram, discovered recursively
charts/                xy scripts, one per chart
specs/                 YAML inputs for data-driven figures
generated/             build output: pdf/, png/, svg/ — never committed
```

Sources are discovered by suffix, so adding a diagram means dropping a
`<name>_tikz.tex` into a topic folder. Output basenames stay flat regardless of
which folder the source lives in.

## Building

```bash
make -C .. install-diagrams   # only needed for charts
make check-tools              # report which tools are installed
make all                      # every diagram, every format
make tikz                     # tikz sources to pdf, png and svg
make dark                     # transparent dark-mode png variants
make clean                    # remove generated output
```

Override the raster density per build: `make tikz TIKZ_DENSITY=1200`. PDFs and
SVGs stay vector; the density only affects PNGs.

## Requirements

| Tool | Install | Needed for |
|---|---|---|
| pdflatex | `brew install --cask basictex` | `tikz`, `tikz-dark` |
| ImageMagick | `brew install imagemagick` | PNG rasterisation |
| pdf2svg | `brew install pdf2svg` | SVG conversion |

Missing tools are reported and skipped rather than failing the build.

## Style conventions

- Arrows are flush at the source and stop just short of the target
  (`shorten >=5pt` in the `flow` style). This reads as a more dynamic connection
  than edge-to-edge arrows.
- Keep boxes close. `-trim` crops the outer canvas, not the gaps inside the
  layout, so loose spacing survives into the final image.
- Text is Latin Modern Sans. Helvetica metrics are absent from a basic TeX Live.
- Colours come from `inkcolor` in `_shared/styles.tex`, which switches with
  `\figdark`. Never hardcode a colour in a diagram source.

## Dark mode

`make dark` recompiles each source with `\figdark` set, producing a transparent
`<name>-dark.png`. Dark variants are PNG only, and TikZ only — `xy` 0.0.6
exposes no background control.

In the docs, pair the two with mkdocs-material's theme suffixes:

```markdown
![Flow](images/flow_tikz.png#only-light)
![Flow](images/flow_tikz-dark.png#only-dark)
```

## Publishing a figure

`generated/` is build output and stays ignored. Copy reviewed figures into
`docs/images/` and commit them there.

## Removing this module

1. `rm -rf diagrams/`
2. Delete `[project.optional-dependencies]` `diagrams` from `pyproject.toml`.
3. Delete the `install-diagrams`, `diagrams` and `diagrams-clean` targets from
   the root `Makefile`. The `$(wildcard diagrams)` entry in `PYTHON_TARGETS`
   disables itself.
4. Delete the `diagrams/generated/` block from `.gitignore`.
5. Delete the `## Diagrams` section from `CLAUDE.md`.
6. Delete any generated figures from `docs/images/`.
````

- [ ] **Step 8: Add the Diagrams section to CLAUDE.md**

Insert into `CLAUDE.md`, immediately before `## Commits and PRs`:

```markdown
## Diagrams

The optional `diagrams/` module generates figures. TikZ owns schematics — boxes,
arrows, maths. `xy` owns data charts. Matplotlib is not used.

- Build with `make diagrams`; `make -C diagrams check-tools` reports what is installed.
- `diagrams/generated/` is build output and is never committed. Copy reviewed
  figures to `docs/images/`.
- Colours come from `inkcolor` in `diagrams/tikz/_shared/styles.tex`. Never
  hardcode a colour in a diagram source.
- `diagrams/README.md` has the removal checklist for projects that do not want it.

```

- [ ] **Step 9: Verify the tool report runs without a toolchain**

Run: `make -C diagrams check-tools`
Expected: one line per tool, each reading `found` or `MISSING`; exit code 0

- [ ] **Step 10: Verify the TikZ build**

Run: `make -C diagrams tikz && ls diagrams/generated/pdf diagrams/generated/png`
Expected with a LaTeX toolchain installed: `flow_tikz.pdf` and `flow_tikz.png` exist.
Expected without one: `FAILED flow_tikz` followed by log output, and exit code 0. Record which case applies.

- [ ] **Step 11: Verify the lint targets still resolve**

Run: `make format-check && make lint && make lint-doc`
Expected: all pass, now also covering `diagrams/`

- [ ] **Step 12: Commit**

```bash
git add diagrams Makefile pyproject.toml .gitignore CLAUDE.md
git commit -m "feat: add optional diagrams module with tikz pipeline"
```

---

## Task 9: Diagrams module — xy charts

**Prerequisite:** Task 7 reported both exports succeeding. If it did not, skip this task entirely and record why in `diagrams/README.md`.

**Files:**
- Create: `diagrams/charts/example_chart.py`
- Modify: `diagrams/Makefile` (add the `charts` target, add it to `all` and `.PHONY`, add the xy check to `check-tools`)
- Modify: `diagrams/README.md` (add xy to the Requirements table)

**Interfaces:**
- Consumes: the `diagrams/Makefile` and layout from Task 8.
- Produces: make target `charts` under `diagrams/`.

- [ ] **Step 1: Write the example chart script**

Create `diagrams/charts/example_chart.py`:

```python
"""Render the example chart shipped with the diagrams module."""

import argparse
from pathlib import Path

import xy

CHART_NAME = "example_chart"


def build_chart():
    """Build the example line chart."""
    return xy.line_chart(xy.line([1, 2, 3, 4, 5], [120, 180, 165, 240, 310]))


def main() -> None:
    """Parse arguments and write the example chart to disk."""
    parser = argparse.ArgumentParser(description="Render the example chart.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write to.")
    parser.add_argument(
        "--format",
        choices=["png", "svg"],
        default="png",
        help="Output format.",
    )
    arguments = parser.parse_args()

    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    destination = arguments.output_dir / f"{CHART_NAME}.{arguments.format}"

    chart = build_chart()
    writers = {"png": chart.to_png, "svg": chart.to_svg}
    writers[arguments.format](str(destination))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Add the charts target**

In `diagrams/Makefile`, change:

```makefile
all: tikz # build every diagram
```

to:

```makefile
all: tikz charts # build every diagram
```

Add `charts` to the `.PHONY` line, and append this target after `tikz-dark`:

```makefile
charts: | $(GENERATED_DIR) # render every chart script to png and svg
	@mkdir -p $(GENERATED_DIR)/png $(GENERATED_DIR)/svg
	@for script in $$(find charts -name '*.py' | sort); do \
		echo "Rendering $$script"; \
		uv run --extra diagrams python "$$script" --output-dir $(GENERATED_DIR)/png --format png; \
		uv run --extra diagrams python "$$script" --output-dir $(GENERATED_DIR)/svg --format svg; \
	done
```

Add the xy check to `check-tools`, after the tool loop:

```makefile
	@if uv run --extra diagrams python -c "import xy" > /dev/null 2>&1; then \
		echo "  found    xy"; \
	else \
		echo "  MISSING  xy (run: make -C .. install-diagrams)"; \
	fi
```

- [ ] **Step 3: Add xy to the README requirements table**

In `diagrams/README.md`, add this row to the Requirements table, below `pdf2svg`:

```markdown
| xy | `make -C .. install-diagrams` | `charts` |
```

- [ ] **Step 4: Install the extra**

Run: `make install-diagrams`
Expected: `xy` resolves and installs

- [ ] **Step 5: Verify the chart build**

Run: `make -C diagrams charts && ls diagrams/generated/png diagrams/generated/svg`
Expected: `example_chart.png` and `example_chart.svg` exist

- [ ] **Step 6: Verify the chart script passes the lint gates**

Run: `make format-check && make lint && make lint-doc`
Expected: all pass

- [ ] **Step 7: Commit**

```bash
git add diagrams/charts diagrams/Makefile diagrams/README.md
git commit -m "feat: add xy chart generation to the diagrams module"
```

---

## Final verification

- [ ] Run `make format-check && make lint && make lint-doc && make test` — all four pass.
- [ ] Run `uv run pre-commit run --all-files` — no hook fails with a missing-file error.
- [ ] Run `uv run python main.py --number 5` — the showcase renders every helper.
- [ ] Run `test -L AGENTS.md` — the symlink is intact.
- [ ] Confirm `.claude/skills/` contains four `SKILL.md` files with parsing frontmatter.
- [ ] Confirm `git status` is clean and every commit subject uses an allowed conventional type.
