---
name: create-html-embed
description: Create a self-contained D3 HTML embed for a documentation page in docs/pages/ - a chart, an interactive figure or a diagram. Use when asked to create a chart, visualization, embed, D3 chart, line chart, bar chart, scatter plot, sankey diagram, diagram or any data visualization for the documentation.
---

# Create HTML Embed

A figure in a documentation page is one self-contained HTML file: a root element, scoped
styles and a script that draws with D3. The page places it with the engine's `HtmlEmbed`
component, which mounts it, themes it and gives it a title and a caption. Diagrams are figures
too: in a documentation page, draw one as an embed rather than as a Mermaid fence.

## Before you start

Read [directives.md](directives.md) in full. It is the single source of truth for embed
authoring: colors and palettes, layout, SVG scope, mounting, theming, controls, tooltips, data
loading, responsiveness, legends, accessibility, performance, error handling, printing and the
agent checklist. The figure's title and caption follow the
[writing guidelines](../writing-guidelines/SKILL.md).

## Workflow

### Step 1: Understand the request

Clarify with the user:

- What type of chart? (line, bar, scatter, sankey, waffle, heatmap, diagram, custom)
- What data source? (CSV path, JSON, inline data)
- Interactive controls needed? (metric selector, filters)
- Any specific design requirements?

### Step 2: Create the HTML file

- Location: `docs/embeds/`
- Naming: `d3-<descriptive-name>.html` (e.g., `d3-training-loss.html`)
- Root class: `.d3-<descriptive-name>` (must match the filename)

`docs/embeds/banner.html` is the figure the engine draws at the top of every page; keep that
name for it. Never put an embed in `docs/app/`, which is the engine the template maintains.

### Step 3: Follow the mandatory structure

Every embed must have this structure:

```html
<div class="d3-yourname"></div>
<style>
  .d3-yourname { /* scoped styles */ }
</style>
<script>
  (() => {
    const ensureD3 = (cb) => { /* D3 CDN loader */ };
    const bootstrap = () => {
      /* mount guard + container selection */
      /* tooltip setup */
      /* SVG scaffolding */
      /* data loading */
      /* render function with ResizeObserver */
    };
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => ensureD3(bootstrap), { once: true });
    } else { ensureD3(bootstrap); }
  })();
</script>
```

### Step 4: Integrate in MDX

Import `HtmlEmbed` in the page under `docs/pages/` and place the embed. The import path is
the same in every page, because the build stages each page inside the engine:

```mdx
import HtmlEmbed from "../../components/HtmlEmbed.astro";

<HtmlEmbed src="d3-yourname.html" title="Chart Title" desc="Description text" />
```

#### HtmlEmbed props

| Prop | Type | Description |
|------|------|-------------|
| `src` | string | Path to the HTML file, relative to `docs/embeds/` (required) |
| `title` | string | Title above the card |
| `desc` | string | Description below (supports HTML) |
| `frameless` | boolean | Removes card background/border |
| `wide` | boolean | Wide layout (~1100px) |
| `data` | string or string[] | Path(s) to data files |
| `config` | object | JSON config passed via `data-config` attribute |

#### Usage examples

```mdx
{/* Simple embed */}
<HtmlEmbed src="d3-training-loss.html" title="Training Loss" />

{/* With external data */}
<HtmlEmbed src="d3-line-simple.html" title="Attention" data="attention_loss.csv" />

{/* With config */}
<HtmlEmbed
  src="d3-line-simple.html"
  title="Learning Rate"
  data="lr_loss.csv"
  config={{ defaultMetric: 'loss', xDomain: [0, 45e9] }}
/>

{/* Multiple data files */}
<HtmlEmbed
  src="d3-comparison.html"
  title="A vs B"
  data={['formatting_filters.csv', 'relevance_filters.csv']}
/>

{/* Frameless */}
<HtmlEmbed frameless src="d3-banner.html" />
```

## Key conventions (quick reference)

Full details are in the directives file. The critical ones:

1. **Colors**: Use `window.ColorPalettes.getColors('categorical', n)` — never hardcode palettes
2. **CSS variables**: `--text-color`, `--surface-bg`, `--border-color`, `--axis-color`, `--tick-color`, `--grid-color`
3. **Dark mode**: Check `document.documentElement.getAttribute('data-theme') === 'dark'`
4. **Mount guard**: Always set `container.dataset.mounted = 'true'`
5. **Data loading**: Try `/data/<file>` first, then `./assets/data/<file>` — use `fetchFirstAvailable()`
6. **Responsiveness**: `ResizeObserver` on container, recompute on resize
7. **Legend**: HTML-based, title "Legend", swatch 14x14px
8. **Controls**: HTML only (no SVG UI), selects labeled "Metric" when applicable
9. **Tooltip**: Single `.d3-tooltip` absolutely positioned inside container
10. **No globals**: Everything in IIFE, nothing on `window`

## Data files

- Store data in: `docs/assets/data/`
- Served from: `/data/` on the built site
- Formats: CSV (preferred for tabular), JSON (for nested/hierarchical)

## Post-creation checklist

After creating the embed, verify it against the **Agent Checklist** (section 14.1) and the
**Definition of Done** (section 14.2) in [directives.md](directives.md). Then run
`make doc-check`, and operate the figure in both themes on the page `make doc` serves.
