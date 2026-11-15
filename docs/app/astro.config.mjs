import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { unified } from '@astrojs/markdown-remark';
import mermaid from 'astro-mermaid';
import compressor from 'astro-compressor';
import generateLlmsTxt from './plugins/astro/generate-llms-txt.mjs';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';
import rehypeCitation from 'rehype-citation';
import rehypeCodeCopy from './plugins/rehype/code-copy.mjs';
import rehypeReferencesAndFootnotes from './plugins/rehype/post-citation.mjs';
import remarkIgnoreCitationsInCode from './plugins/remark/ignore-citations-in-code.mjs';
import remarkUnwrapCitationLinks from './plugins/remark/unwrap-citation-links.mjs';
import remarkDirective from 'remark-directive';
import remarkOutputContainer from './plugins/remark/output-container.mjs';
import remarkRestoreTextDirectives from './plugins/remark/restore-text-directives.mjs';
import rehypeRestoreAtInCode from './plugins/rehype/restore-at-in-code.mjs';
import rehypeWrapTables from './plugins/rehype/wrap-tables.mjs';
import rehypeWrapOutput from './plugins/rehype/wrap-outputs.mjs';
// Built-in Shiki (dual themes) — no rehype-pretty-code

// Plugins moved to app/plugins/*

// Auto-detect HF Space URL for SEO (og:image needs absolute URLs)
const spaceId = process.env.SPACE_ID; // e.g. "tfrere/research-article-template"
const siteUrl = spaceId
  ? `https://${spaceId.replace('/', '-').toLowerCase()}.hf.space`
  : undefined;

export default defineConfig({
  ...(siteUrl ? { site: siteUrl } : {}),
  output: 'static',
  // Astro 7 defaults to JSX whitespace rules; keep the lossless compression the pages were laid out with.
  compressHTML: true,
  integrations: [
    mermaid({ theme: 'neutral', autoTheme: true }),
    mdx(),
    sitemap(),
    generateLlmsTxt(),
    // Precompress output with Gzip only (Brotli disabled due to server module mismatch)
    compressor({ brotli: false, gzip: true, zstd: false })
  ],
  devToolbar: {
    enabled: false
  },
  markdown: {
    shikiConfig: {
      themes: {
        light: 'github-light',
        dark: 'github-dark'
      },
      defaultColor: false,
      wrap: false,
      langAlias: {
        // Map MDX fences to TSX for better JSX tokenization
        mdx: 'tsx'
      }
    },
    // The remark/rehype pipeline; .mdx files inherit it. GitHub-flavoured Markdown, including
    // [^name] footnotes, is built into the processor.
    processor: unified({
      remarkPlugins: [
        remarkUnwrapCitationLinks,
        remarkIgnoreCitationsInCode,
        remarkMath,
        remarkDirective,
        remarkRestoreTextDirectives,
        remarkOutputContainer
      ],
      rehypePlugins: [
        rehypeSlug,
        [rehypeAutolinkHeadings, { behavior: 'wrap' }],
        [rehypeKatex, {
          trust: true,
        }],
        [rehypeCitation, {
          bibliography: 'src/content/bibliography.bib',
          linkCitations: true,
          csl: "apa",
          noCite: false,
          suppressBibliography: false,
        }],
        rehypeReferencesAndFootnotes,
        rehypeRestoreAtInCode,
        rehypeCodeCopy,
        rehypeWrapOutput,
        rehypeWrapTables
      ]
    })
  }
});
