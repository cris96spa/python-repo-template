# Adopting rlhf-book patterns into the Python repo template

**Date:** 2026-08-10
**Status:** Approved design, ready for implementation planning
**Source of inspiration:** [natolambert/rlhf-book](https://github.com/natolambert/rlhf-book)

## Goal

Bring three capabilities the template currently lacks into `python-repo-template`,
adapting patterns from `rlhf-book` rather than copying them:

1. A reusable Rich console presentation layer.
2. Agent-facing project context and repo-local skills.
3. An optional, removable diagram-generation module.

Plus the pre-commit and CI repairs that this work surfaces.

## Non-goals

- Porting rlhf-book's pandoc/Make book pipeline, matplotlib generators, or the
  ML-specific helpers (`resolve_device`, flash-attention shims).
- Adopting rlhf-book's `CHANGELOG.md` convention or its changelog-enforcing CI
  job. The template already uses conventional commits plus
  `python-semantic-release`; the two overlap and the existing setup wins.
- A standalone `pre-submit-pr` skill. Its verification step is folded into
  `push-to-pr` instead.
- Raising test coverage as an end in itself.

## Cross-cutting constraint: template sync

`utils/update_template.py` propagates template changes to derived projects by
squash-merging the template diff, with manual conflict resolution. Every file
this design adds is therefore inherited by derived projects, and any file those
projects rewrite will conflict on each sync. Two consequences shape the design:

- `CLAUDE.md` confines project-specific content to a single marked section, so
  conflicts localise to one block.
- The diagrams module is fully self-contained and removable via a documented
  checklist, so projects that do not want it can delete it cleanly.

## Code style standard

These rules apply to all code and documentation produced by this work, and are
written into `CLAUDE.md` so they apply to future work too.

- Comments must earn their place. No narration of the following line, no
  justification of constant values, no explanatory blobs. When a comment feels
  necessary, first try renaming a symbol or extracting a function; that usually
  removes the need.
- Symbol names must be explicit enough to carry their own meaning. No
  abbreviations that need decoding.
- Documentation reads clean: no filler, no restating the API in prose.
- Tests target critical behaviour and edge cases. Coverage is a diagnostic,
  never a goal. No test exists to move the coverage number.

---

## Phase 1 — `utils/console.py`

### Module

A new module holding one shared `Console` and stateless presentation helpers.
Every helper takes an optional trailing `console` parameter defaulting to the
shared instance: call sites stay clean, and tests inject a `StringIO`-backed
console.

```python
console = Console(width=int(os.environ.get("COLUMNS", 180)))

STYLE_HEADER = "cyan"
STYLE_INFO = "magenta"
STYLE_METRIC = "green"
STYLE_MUTED = "dim"

def section_header(title, *, style=STYLE_HEADER, console=None) -> None
def summary_panel(fields: Mapping[str, Any], *, title, style=STYLE_INFO, console=None) -> None
def metrics_panel(metrics: Mapping[str, Any], *, title="Metrics", console=None) -> None
def two_column_panel(rows: Mapping[str, str], *, title, label_width=12, console=None) -> None
def new_progress_bar(*, console=None, transient=False) -> Progress
def format_metric(value: Any) -> str
def highlight_markers(text: str, styles: Mapping[str, str]) -> str
```

Behaviour of each:

- `section_header` — a `console.rule` divider for phase boundaries.
- `summary_panel` — compact `key: value` lines in a bordered panel, for run
  configuration and summaries.
- `metrics_panel` — a single line of `key: value` pairs, values passed through
  `format_metric`.
- `two_column_panel` — a borderless `Table` inside a `Panel`, with a fixed-width
  dim label column so long or wrapping values stay aligned.
- `new_progress_bar` — returns a fresh `Progress` composed of `SpinnerColumn`,
  description, `BarColumn`, `MofNCompleteColumn` and `TimeElapsedColumn`, bound
  to the shared console. The name states that each call returns a new object.
- `format_metric` — floats render as `{:.2e}` when `0 < abs(value) < 1e-3`, else
  `{:.4f}`; all other types pass through `str`.
- `highlight_markers` — takes a mapping of literal substrings to Rich styles.
  It escapes the whole text with `rich.markup.escape` first, then wraps each
  occurrence of a mapped substring in its style. Escaping before styling is the
  point of the function: it is what stops text such as `[bold]` in a value from
  being interpreted as markup.

`fields` and `rows` are `Mapping`, not `**kwargs`, so labels may contain spaces.

### Logger integration

`utils/logger.py` currently constructs its own `Console` and reads `COLUMNS`. A
second bare `Console` writing panels alongside it interleaves output and
disagrees on width. `setup_logger` will import the shared console and pass it to
`RichHandler(console=console)`; the `COLUMNS` handling moves into
`utils/console.py`. `utils/console.py` imports nothing from `utils`, so there is
no import cycle.

### Showcase

`main.py` keeps its `--number` argument and `random_sum` call, and wraps them in
`section_header` → `summary_panel` (run configuration) → `new_progress_bar` over
a short loop → `metrics_panel` (results) → `two_column_panel` (one sample), so
`uv run python main.py --number 5` demonstrates the whole surface.

### Tests

`tests/test_console.py`, scoped to what can actually break:

- `format_metric` branch boundary: exactly `1e-3`, just below it, `0.0` (the
  `0 < abs(value)` guard is what stops zero rendering as `0.00e+00`), small
  negative values, and non-float passthrough.
- `highlight_markers`: a value containing `[bold]` renders literally rather than
  being interpreted as markup, and markers still apply after escaping.
- One smoke test that the panels, header and progress bar render to an injected
  console without raising.

No per-helper substring assertions on the panels; they are thin Rich
configuration.

---

## Phase 2 — Agent infrastructure

### `CLAUDE.md`

A single root file, written generically so it is true in any derived project,
with `AGENTS.md` as a symlink to it. Sections in this order:

| Section | Content |
|---|---|
| `## Project` | The only project-owned block: purpose, domain notes, entry points. A comment marks it and states that everything below is template-owned. |
| `## Toolchain` | uv + make. Always `uv run python`, never bare `python`. `make help` lists targets. Use `uv run ruff` (pinned in the dev group) rather than `uvx ruff`, so local matches CI. |
| `## Code Style` | The four rules from the Code style standard section above. |
| `## Commands` | Every make target, and the note that CI runs `format-check`, `lint`, `lint-doc`, `test` via `.github/actions/validation`. |
| `## Directory Structure` | Annotated tree. |
| `## Configuration` | `YamlBaseSettings` vs `YamlBaseModel` with the decision rule, `DEFAULT_CONFIG_PATH`, the `@command` decorator, `configs/` layout. |
| `## Console Output` | Use `utils.console`; never construct a bare `Console()`. Diagnostics go through `logging`. Escape untrusted text. |
| `## Docstrings & Linting` | Google convention, types in signatures not docstrings, line length 100, and why each ruff ignore in `pyproject.toml` exists. |
| `## Testing` | pytest, xdist, coverage; tests mirror the package; the coverage rule from Code Style. |
| `## Documentation` | properdocs/mkdocs-material; API pages are generated by `utils/build_api_docs.py` — edit its `SKIP_FILENAMES`/`SKIP_PATHS`, never hand-write `api/` pages. A pre-commit hook builds the docs, so a broken reference fails the commit. |
| `## Diagrams` | Present only while the optional module is. TikZ owns schematics, xy owns charts, never commit `generated/`, `magick` always with `-trim`. |
| `## Commits & PRs` | Conventional commits enforced by `conventional-pre-commit`; versions owned by `python-semantic-release` and never hand-edited; `no-commit-to-branch` behaviour. |
| `## Task Map` | "I want to… → start here" rows for: add a config, sync the template, open a PR, change console output, add an API doc page, add a diagram. |
| `## Skills` | One line per skill and when to reach for it. |
| `## Template Sync` | How `update_template.py` works, keep project edits inside `## Project`, never edit through the `AGENTS.md` symlink. |

The `AGENTS.md` symlink is compatible with the existing `check-symlinks` hook,
which fails only on broken symlinks. The file notes the Windows `core.symlinks`
caveat, since a template is cloned on machines the author does not control.

### Skills

Four skills under `.claude/skills/<name>/SKILL.md`, each with `name`,
`description` and `allowed-tools` frontmatter.

**`sync-template`** — `Bash(git:*)`, `Bash(uv:*)`, `Read`, `Edit`.
Pre-flight: clean tree, on the default branch, up to date, `[tool.template]`
present in `pyproject.toml`. Runs `utils/update_template.py`. On conflict,
follows the resolve → stage → commit → re-run resume protocol from
`docs/updating-from-template.md`. Afterwards runs `make dev` and the four CI
commands, summarises what the template changed, and opens a PR. Carries an
explicit don't-list: no force-push, no hand-deleting the `template` remote,
never start on a dirty tree.

**`new-config`** — `Read`, `Edit`, `Write`, `Bash(uv:*)`.
Picks the base class by the decision rule; writes the class with
`Field(description=...)` on every field and a google docstring; sets
`DEFAULT_CONFIG_PATH` when there is a canonical file; creates a fully populated
`configs/<name>.yaml`; adds a round-trip test; runs `make lint-doc`,
`make format` and `make test`. Includes a filled-in worked example so the shape
is copied rather than invented.

**`push-to-pr`** — `Bash(git:*)`, `Bash(gh:*)`.
Adapted from rlhf-book: the commit subject must start with a type from the
`conventional-pre-commit` allowlist or the `commit-msg` hook rejects it; checks
`no-commit-to-branch`; runs the four CI commands before pushing; creates the PR
or pushes to the existing one.

**`update-pr-body`** — `Bash(gh:*)`. Near-verbatim port; already generic.

---

## Phase 3 — Optional `diagrams/` module

```
diagrams/
  README.md      catalog, conventions, removal checklist
  Makefile       all · tikz · tikz-dark · charts · charts-dark · check-tools · clean · help
  tikz/
    _shared/styles.tex        found via TEXINPUTS, no relative paths
    example/flow_tikz.tex
  charts/
    example_chart.py          xy, with --output-dir/--format/--theme
  specs/                      YAML inputs where a figure is data-driven
  generated/                  gitignored: png/ svg/ pdf/
```

### Tool boundary

Anything with boxes, arrows or math is TikZ. Anything plotting data is xy.
Matplotlib is not used. The boundary is stated in both `diagrams/README.md` and
`CLAUDE.md`.

The boundary exists because `xy` is a charting library — line, scatter and
density marks over data — not a vector drawing canvas. It has no equivalent of
matplotlib's `patches` API, and its `xy.pyplot` compatibility shim covers
pyplot-style charting calls, not artist drawing.

### Dependency handling

`xy` goes in `[project.optional-dependencies]`, not a PEP 735 dependency group.
`make dev` runs `uv sync --all-groups`, which would pull an alpha Rust package
into every development environment and every CI leg. Extras are excluded from
`--all-groups`, so a new `make install-diagrams` target running
`uv sync --extra diagrams` keeps it genuinely opt-in.

Pin as `xy>=0.0.6,<0.1.0`.

### xy spike — first task of this phase

Verify in a clean environment that `chart.to_svg()` and `chart.to_png()` work
headless. The package describes a GPU render client, and 0.0.6 offers no
guarantee that static export runs without a display or browser. Also determine
whether a transparent or dark variant is reachable.

Outcomes:

- Export works → build `charts/` as designed.
- Export fails headless → `xy` is dropped from this phase and `charts/` waits.
  TikZ ships regardless; nothing else in the plan moves.
- Only the dark variant fails → dark mode is TikZ-only.

### TikZ pipeline

Recursive `*_tikz.tex` discovery under `tikz/`. Each source compiles in place
with `pdflatex -interaction=nonstopmode` and `TEXINPUTS` pointed at
`tikz/_shared`, so any source can `\input{styles.tex}` without a relative path.
Output basenames stay flat regardless of subfolder. The PDF is copied to
`generated/pdf/`, rasterised to `generated/png/` with
`magick -density $(TIKZ_DENSITY) -trim -quality 100`, and converted to
`generated/svg/` with `pdf2svg`. `TIKZ_DENSITY` defaults to 800.

`tikz-dark` recompiles each source under `\def\figdark{1}` with
`-jobname <base>-dark` and `-background none`, producing a transparent
`<base>-dark.png` for dark-mode pages. No SVG or PDF for dark variants.

Two improvements over the rlhf-book original:

- On a failed compile, print the tail of the `.log`. The original pipes
  `pdflatex` to `/dev/null` and reports only that the PDF was not generated.
- A `check-tools` target reports which of `pdflatex`, `magick`, `pdf2svg` and
  `xy` are installed, instead of silently skipping outputs.

### Root Makefile changes

- New targets `diagrams`, `diagrams-clean`, `install-diagrams`, delegating with
  `$(MAKE) -C diagrams`.
- The hardcoded lint and format target lists become variables ending in
  `$(wildcard diagrams)`, so the directory is linted when present and skipped
  when deleted.

### Docs wiring

Reviewed outputs are copied to `docs/images/` and committed;
`diagrams/generated/` stays ignored build output. Light and dark variants are
selected with mkdocs-material's `#only-light` and `#only-dark` image suffixes,
which the existing palette toggle in `properdocs.yml` supports.

### Removal checklist

Documented in `diagrams/README.md`:

1. `rm -rf diagrams/`
2. Remove the `diagrams` entry from `[project.optional-dependencies]`.
3. Remove the `diagrams`, `diagrams-clean` and `install-diagrams` targets from
   the root `Makefile`. The `$(wildcard diagrams)` lint entries self-disable.
4. Remove the `diagrams/generated/` block from `.gitignore`.
5. Remove the `## Diagrams` section from `CLAUDE.md`.
6. Remove any generated figures from `docs/images/`.

---

## Phase 4 — Repairs and consistency

### Remove the `update-progress` hook

`.pre-commit-config.yaml` runs `utils/update_progress.py` on changes under
`leetcode/(Easy|Medium|Hard)/`. Neither the script nor the directory exists;
it is residue from another repository. Delete the hook.

### Implement `utils/post_checkout.py`

The `post-checkout` hook is already wired with `always_run: true` and
`verbose: true`; only the script is missing.

pre-commit passes post-checkout hooks three git arguments: previous HEAD, new
HEAD, and a flag that is `1` for a branch checkout and `0` for a file checkout.
The script exits silently when the flag is not `1`. Otherwise it diffs
`previous..new` for `pyproject.toml` and `uv.lock`, and when either changed
prints a notice through `utils.console` telling the user to run `make dev`.

Every path exits `0` — missing or malformed argv, unknown revisions, not a git
repository — so the hook is never the reason a checkout looks broken.

Tests:

- Flag `0` produces no output.
- A changed `pyproject.toml` across a branch switch produces the notice.
- No relevant change produces nothing.
- Missing or malformed argv exits `0` without raising.

### Narrow the Python version matrix

`pyproject.toml` declares `requires-python = ">=3.12"`, and
`utils/experiment_logger.py` imports `typing.override`, which is 3.12+. The CI
matrix in `.github/workflows/main-validate.yaml` lists 3.10, 3.11, 3.12 and
3.13. uv honours `requires-python` and resolves a compatible interpreter
regardless of what `setup-python` placed on `PATH`, so the first two legs run
3.12+ under a misleading label. Narrow the matrix to `["3.12", "3.13"]`.

### `.gitignore`

Add `.claude/settings.local.json` (per-developer) and `diagrams/generated/`.

### Observation, no change proposed

`no-commit-to-branch` guards `development`, `staging` and `production`, none of
which exist in this repository, while `main` — the actual default branch — is
unguarded. The skills in Phase 2 assume a branch-then-PR workflow. Enforcing it
is a one-word edit, left to the maintainer.

---

## Sequencing

Phases run in order: console → agent infrastructure → diagrams → repairs, with
one exception. Phase 4's `post_checkout.py` depends on Phase 1's console module,
and the `.gitignore` and pre-commit edits are independent, so Phase 4 items may
land alongside the phase that unblocks them.

Console comes first because both `CLAUDE.md` and `post_checkout.py` reference
it. Diagrams comes last because it depends on an unproven alpha package and is
the removable module, so a failed spike delays nothing else.

## Verification

Each phase is complete when `make format-check`, `make lint`, `make lint-doc`
and `make test` all pass — the same four commands CI runs. Phase 3 additionally
requires `make -C diagrams check-tools` to report accurately, and `make -C
diagrams tikz` to produce PNG, SVG and PDF output from the example source on a
machine with the LaTeX toolchain installed.

## Corrections found during implementation

This design was written before implementation and two of its statements
turned out to be wrong. The design above is left as originally written; this
section records what actually happened instead.

- **Post-checkout hook arguments.** This design says pre-commit "passes
  post-checkout hooks three git arguments." It does not: pre-commit exposes
  the previous HEAD, new HEAD, and branch-checkout flag as the environment
  variables `PRE_COMMIT_FROM_REF`, `PRE_COMMIT_TO_REF` and
  `PRE_COMMIT_CHECKOUT_TYPE`, not as `sys.argv`. `utils/post_checkout.py`
  reads both the environment variables and positional argv so it also works
  when invoked directly (e.g. via a native git hook) rather than only through
  pre-commit.
- **`install-diagrams` dependency sync.** This design specifies `make
  install-diagrams` running `uv sync --extra diagrams`. The implementation
  instead runs `uv sync --all-groups --extra diagrams`, because
  `[tool.uv] default-groups = []` makes `uv sync` exact: a bare `uv sync
  --extra diagrams` would evict the `dev` group from the environment rather
  than adding the extra to it.
- **`xy` 0.0.6 export formats.** The xy spike above only names `to_svg()` and
  `to_png()`. `xy` 0.0.6 has no `to_pdf`, so `diagrams/charts` exports PNG and
  SVG only; the TikZ pipeline remains the only source of PDF output.
