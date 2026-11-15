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
| `app/`         | The engine that renders the pages, exactly as upstream ships it                          | Upstream     |
| `superpowers/` | Working notes on earlier changes, which the site does not publish                        | The template |

`template-provenance.json` records the upstream commit and a SHA-256 hash of every engine file,
and `make doc-check` stops at the first file that differs. Change the engine only by vendoring
a newer upstream revision, and record the new hashes with it.

## Licence and attribution

The engine in `app/` is Thibaud Frere's
[research-article-template](https://github.com/tfrere/research-article-template), licensed under
[CC BY 4.0](LICENSE). It comes through
[Latent Writing Lab](https://github.com/cris96spa/latent-writing-lab), which adds the scripts in
`tools/` and the navigation in `components/`. The engine's files are unmodified; its
demonstration article, figures and images are not included, and its banner lives in
`embeds/banner.html`.
