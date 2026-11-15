# The documentation kit

`docs/components/` holds what every page of the site shares: the navigation, which
`tools/docs.mjs` puts at the top and bottom of each page, the project's accent colour, and four
components a page can import to route the reader and break up the prose: `CardGrid` with
`Card`, `Steps` and `Badge`. They draw with the engine's CSS variables and the kit's tints, so
they follow the light and dark themes and fit a phone.

| File                                                         | What it holds                                                                    |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| `DocsNav.astro`                                              | The navigation and the pager; the build places it, so a page never imports it    |
| `accent.css`                                                 | The project's accent colour, in light and dark themes                            |
| `kit.css`                                                    | The tint of each kind of page and of each status tone                            |
| `kinds.ts`                                                   | The kinds of page: the group that names each, its tint key and its eyebrow label |
| `icons.ts`                                                   | The line icons a `Card` can show                                                 |
| `CardGrid.astro`, `Card.astro`, `Steps.astro`, `Badge.astro` | The components a page imports                                                    |

## The navigation

Each entry of `docs/pages/pages.json` names a page, its group and a short label, in reading
order:

```json
{ "file": "write-an-operator.mdx", "group": "How-to guides", "label": "Write an operator" }
```

The label is what the menu shows, so it leaves out the kind ("Write an operator", not
"How-to: write an operator") and stays within two or three words: the pages of the largest
group share one row, which fits about 1,200 pixels on a desktop. The page's own `title` is
still the heading of the page.

The group decides where the page sits and how it is coloured:

| Group           | Tint                 | Eyebrow above the title |
| --------------- | -------------------- | ----------------------- |
| `Overview`      | the project's accent | Overview                |
| `Tutorial`      | green                | Tutorial                |
| `How-to guides` | blue                 | How-to guide            |
| `Reference`     | amber                | Reference               |
| `Explanation`   | magenta              | Explanation             |
| `Project`       | slate                | Project                 |

A group outside this table keeps its name and the slate tint, and an entry without a group
forms a group of its own named after its label.

At the top of a page, one row shows a tab per group, in the order `pages.json` first names
them, with a dot of the group's tint and the number of pages when there are several. Under it,
on a band of the same tint, a second row shows the pages of the current group, the current one
raised out of the band. A group of one page has no second row: its tab links to the page
directly. Above the page title, a small eyebrow names the kind of the page in its tint. At the
bottom, the pager links the previous and the next page and names the group of each.

Every item is a plain link, so the navigation works without JavaScript. A row too long for the
screen scrolls sideways, as on a phone; a short script then centres the current tab and page
and fades the edge behind which more items wait, with a chevron on the right. The engine's bar
of authors and dates is hidden when it has nothing to show.

## The accent colour

`accent.css` sets the engine's `--primary-base`, which links, buttons, figures and the
Overview tint derive from, twice: on `html:root` for the light theme and on
`html[data-theme="dark"]` for the dark one, each an `oklch()` colour. Change the two values to
recolour the whole site, and keep the dark one lighter so links stay readable on the dark page.
The template keeps the engine's default orange; each project sets its own hue.

## Using a component in a page

A page imports a component from `../../components/docs/`, where the build copies this folder:

```mdx
import CardGrid from "../../components/docs/CardGrid.astro";
import Card from "../../components/docs/Card.astro";
import Steps from "../../components/docs/Steps.astro";
import Badge from "../../components/docs/Badge.astro";
```

Markdown inside a component is read as Markdown only when a blank line separates it from the
opening and closing tags. None of the components draws a heading, so the table of contents
lists only the page's own headings.

## CardGrid and Card

A `CardGrid` lays out `Card`s in two columns, or three, and in one on a phone. Use it for
"where to go next" at the end of a page and for an overview of features. A card with a link is
clickable as a whole and shows an arrow after its title; a card without one is a static panel.

| `CardGrid` prop | Type     | Default | What it does                                       |
| --------------- | -------- | ------- | -------------------------------------------------- |
| `columns`       | `2 \| 3` | `2`     | Columns on a desktop; three become two on a tablet |

| `Card` prop | Type     | Default | What it does                                                                                                                                         |
| ----------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `title`     | `string` | —       | The card's title, in bold                                                                                                                            |
| `href`      | `string` | none    | The link; write another page as `/page-name/`, so `make doc-check` checks it like any page link                                                      |
| `kind`      | `string` | none    | A kind key (`overview`, `tutorial`, `howto`, `reference`, `explanation`, `project`) or group name: tints the card and names the kind above the title |
| `icon`      | `string` | none    | One of the icon names below, drawn in the card's tint                                                                                                |
| children    | Markdown | —       | The short text under the title, one or two sentences                                                                                                 |

```mdx
<CardGrid>
  <Card title="Overview" href="/" kind="overview" icon="book">
    What the project does, and the shortest path to a first run.
  </Card>
  <Card
    title="Updating from the template"
    href="/updating-from-template/"
    kind="project"
    icon="refresh"
  >
    Bring the template's later changes into the project.
  </Card>
</CardGrid>
```

A card without `kind` takes the project's accent. The icons are `arrow`, `book`, `bolt`,
`box`, `branch`, `bulb`, `chart`, `check`, `checklist`, `code`, `compare`, `compress`, `cpu`,
`database`, `eye`, `file`, `filter`, `flask`, `flow`, `gauge`, `layers`, `link`, `lock`,
`nodes`, `play`, `refresh`, `search`, `shield`, `sliders`, `sparkles`, `tag`, `terminal` and
`upload`. An unknown kind or icon stops the build with the list of valid names.

## Steps

`Steps` turns a Markdown ordered list into a numbered procedure: each item gets a numbered
circle in the accent tint, joined to the next by a line. It has no props. A step can hold
paragraphs, lists and code blocks, indented under the item:

````mdx
<Steps>

1. Install the development environment:

   ```sh
   make dev
   ```

2. Run the tests with `make test`.

</Steps>
````

## Badge

`Badge` is an inline label for a status or a kind, such as "optional", "experimental" or
"since 0.3".

| Prop     | Type     | Default  | What it does                                                                                                                                          |
| -------- | -------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tone`   | `string` | `accent` | `accent`, `neutral`, `success`, `info`, `warning` or `danger`, or a kind key (`overview`, `tutorial`, `howto`, `reference`, `explanation`, `project`) |
| children | text     | —        | The label, one or two words                                                                                                                           |

```mdx
This option is <Badge tone="success">stable</Badge>, that one <Badge tone="warning">new</Badge>.
```

An unknown tone stops the build with the list of valid ones.

## Tints and contrast

`kit.css` defines the tints once per theme. An element picks one with
`data-kit-tint="<name>"` and draws with `--kit-tint` for text, dots and borders and
`--kit-wash` for the pale fill behind it. Every light tint keeps a contrast above 4.5:1 on
white and on its own wash, and every dark tint above 6:1 on the dark page and its wash. The
status tones share the hues of the kinds: `success` is the tutorial green, `info` the how-to
blue, `warning` the reference amber and `neutral` the project slate; `danger` is red.
