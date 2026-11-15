# Documentation

The project's documentation is a static site built from the MDX pages in `pages/`. Run
`make doc` from the repository root, after `make install-docs` the first time, and open
http://127.0.0.1:8031/ to read it. The [overview page](pages/index.mdx) explains how to install
the toolchain and add a page.

| Folder         | Holds                                                                                    | Owner        |
| -------------- | ---------------------------------------------------------------------------------------- | ------------ |
| `pages/`       | One MDX file per page, and `pages.json`, which lists their menu order, labels and groups | You          |
| `embeds/`      | Figures, one HTML file each; `banner.html` is drawn at the top of every page             | You          |
| `assets/`      | Images in `image/` and figure data in `data/`; create it when a page needs it            | You          |
| `components/`  | The navigation, the accent colour and the page components; `KIT.md` documents them       | You          |
| `tools/`       | The scripts behind `make doc`, `make doc-build` and `make doc-check`                     | The template |
| `app/`         | The engine that renders the pages, modified from upstream as the template maintains it   | The template |
| `superpowers/` | Working notes on earlier changes, which the site does not publish                        | The template |

`template-provenance.json` records the upstream commit the engine is derived from, the changes
made to it since, and a SHA-256 hash of every engine file. `make doc-check` fails when an engine
file is edited, added or removed. Change the engine only in the template, and record the new
hashes with the change; projects receive it through the template sync.

## Licence and attribution

The engine in `app/` is a modified version of Thibaud Frere's
[research-article-template](https://github.com/tfrere/research-article-template), licensed under
[CC BY 4.0](LICENSE). It came through
[Latent Writing Lab](https://github.com/cris96spa/latent-writing-lab), which adds the scripts in
`tools/` and the navigation in `components/`. The template runs it on current Astro and
dependencies and removes the tools a documentation site does not use, such as the PDF and LaTeX
exports; `template-provenance.json` lists every change. The engine's demonstration article,
figures and images are not included, and its banner lives in `embeds/banner.html`.
