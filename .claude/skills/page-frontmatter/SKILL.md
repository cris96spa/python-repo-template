---
name: page-frontmatter
description: The frontmatter of a documentation page in docs/pages/ - title, subtitle, description, authors, layout template, table of contents and licence note. Use when adding a documentation page, or when asked about a page's title, metadata, layout or any frontmatter field.
---

# Page Frontmatter Reference

Every page in `docs/pages/` opens with a YAML frontmatter block. The engine renders each page
with its article layout, so the block uses the engine's article fields. A page's menu label and
its place in the menu are not frontmatter: they come from `docs/pages/pages.json`.

## The block every page starts with

```yaml
---
title: "Updating from the Template"
subtitle: "Bring the template's later changes into your project."
description: "How the update script replays the template's changes onto a branch for review."
authors: []
template: "article"
showPdf: false
licence: "Built with Thibaud Frere's research-article-template (CC BY 4.0)."
---
```

Keep `showPdf: false`: the site has no PDF export, and the field defaults to `true`, which
shows a download button with nothing behind it. Keep the `licence` note, which credits the
engine in the footer of the page as its CC BY 4.0 licence requires.

## Frontmatter fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | string | `"Untitled article"` | Page title, shown in the hero and the browser tab. Supports `\n` for line breaks. |
| `subtitle` | string | `""` | Line shown below the title. Falls back to `description`. |
| `description` | string | `""` | Summary used in the page metadata and the text export. |
| `authors` | array | `[]` | Authors shown in the hero (see below). Leave empty for unsigned pages. |
| `affiliations` | array | `[]` | Affiliations the authors refer to (see below). |
| `published` | string | — | Publication date shown in the hero, e.g. `"Apr. 04, 2026"`. |
| `template` | `"article"` or `"paper"` | `"article"` | Layout variant (see below). |
| `showPdf` | boolean | `true` | Shows a PDF download button. Set it to `false`. |
| `tableOfContentsAutoCollapse` | boolean | `false` | Collapses table-of-contents sections while scrolling. |
| `licence` | string | — | Licence note (HTML allowed), shown in the footer. |
| `doi` | string | — | DOI identifier, shown in the hero and the footer. |
| `seoThumbImage` | string | — | Image URL for link previews. |
| `links` | array | `[]` | Buttons shown in the hero of the `paper` template (see below). |

## Title line breaks

Long titles are balanced across lines (`text-wrap: balance`), and titles longer than 60
characters are downsized, with a smaller size again past 100. To force a line break, use `\n`
inside the title string:

```yaml
title: "Updating\nfrom the Template"
```

The plain-text title, used in the browser tab and the metadata, drops the break.

## Template variants

| Value | Layout | Features |
|-------|--------|----------|
| `article` (default) | Full layout | Sidebar table of contents, figure numbering, citation block in the footer |
| `paper` | Single centered column | No sidebar, no figure numbering, no citation block, lighter footer |

Both variants draw `docs/embeds/banner.html` at the top of the page. The existing pages use
`article`; keep one variant across the site.

## Authors and affiliations

```yaml
authors:
  - name: "Alice Martin"
    url: "https://example.com/alice"
    affiliations: [1]
  - name: "Bob Chen"
    affiliations: [1, 2]
affiliations:
  - name: "Example Lab"
    url: "https://example.com"
  - name: "Example University"
    url: "https://example.edu"
```

Affiliation indices are 1-based and rendered as superscript numbers next to author names.

## External links (paper template)

The `links` field adds buttons below the author line in the `paper` template hero. Each link
has a `label` and a `url`:

```yaml
links:
  - label: "Code"
    url: "https://github.com/YOUR-OWNER/YOUR-REPOSITORY"
  - label: "Package"
    url: "https://pypi.org/project/YOUR-PACKAGE/"
```

The `article` template does not show them.

## After the frontmatter

Import the components the page uses, then write the content. The import path is the same in
every page, because the build stages each page inside the engine:

```mdx
import Accordion from "../../components/Accordion.astro";
import Note from "../../components/Note.astro";
```

A new page also needs an entry in `docs/pages/pages.json`, in reading order, with its `file`, a
short `label` and the `group` the menu lists it under (`docs/components/KIT.md` names the
groups), and `make doc`
restarted. The prose follows the [writing guidelines](../writing-guidelines/SKILL.md).
