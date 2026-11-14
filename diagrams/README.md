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
make tikz-dark                # transparent dark-mode png variants from tikz sources
make charts                   # xy chart scripts to png and svg
make dark                     # transparent dark-mode png variants
make clean                    # remove generated output
```

Override the raster density per build: `make tikz TIKZ_DENSITY=1200`. PDFs and
SVGs stay vector; the density only affects PNGs.

`make charts` runs through `uv run --extra diagrams`, which installs the
`diagrams` extra on demand if it is missing — no separate `install-diagrams`
step is required for it.

## Requirements

| Tool | Install | Needed for |
|---|---|---|
| pdflatex | `brew install --cask basictex` | `tikz`, `tikz-dark` |
| ImageMagick | `brew install imagemagick` | PNG rasterisation |
| pdf2svg | `brew install pdf2svg` | SVG conversion |
| xy | `make -C .. install-diagrams` | `charts` |

Missing tools are reported and skipped rather than failing the build. A source
that genuinely fails to build reports `FAILED` and makes the target exit
non-zero, after attempting every other source.

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

In Markdown that GitHub renders, such as `README.md`, pair the two with a `<picture>`
element:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/image/flow_tikz-dark.png">
  <img src="docs/assets/image/flow_tikz.png" alt="Flow">
</picture>
```

A documentation page shows one variant, whichever theme the reader chose.

## Publishing a figure

`generated/` is build output and stays ignored. Copy reviewed figures into
`docs/assets/image/` and commit them there. A documentation page in `docs/pages/` imports
the file and places it with the `Image` component:

```mdx
import Image from "../../components/Image.astro";
import flow from "../assets/image/flow_tikz.png";

<Image src={flow} alt="What the figure shows" caption="What the figure is for." />
```

## Removing this module

1. `rm -rf diagrams/`
2. Delete `[project.optional-dependencies]` `diagrams` from `pyproject.toml`.
3. Delete the `install-diagrams`, `diagrams` and `diagrams-clean` targets from
   the root `Makefile`. The `$(wildcard diagrams)` entry in `PYTHON_TARGETS`
   disables itself.
4. Delete the `diagrams/generated/` block from `.gitignore`.
5. Delete the `## Diagrams` section from `CLAUDE.md`, and the `diagrams/` line
   from its Directory Structure block.
6. Delete any generated figures from `docs/assets/image/`.
