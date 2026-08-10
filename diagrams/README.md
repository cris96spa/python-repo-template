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
| xy | `make -C .. install-diagrams` | `charts` |

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
