import { access, readFile, readdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import GithubSlugger from "github-slugger";

// Paths are reported relative to the repository root, which holds this workspace in docs/.
const repository = fileURLToPath(new URL("../../", import.meta.url));
const at = (path) => join(repository, path);

async function markdownFiles(directory) {
  const files = [];
  for (const entry of await readdir(at(directory), { withFileTypes: true })) {
    const path = `${directory}/${entry.name}`;
    if (entry.isDirectory()) files.push(...(await markdownFiles(path)));
    else if (/\.mdx?$/.test(entry.name)) files.push(path);
  }
  return files;
}

// Code blocks and spans can contain example links; check the prose around them.
const prose = (source) =>
  source.replace(/^(`{3,}|~{3,}).*\n[\s\S]*?^\1\s*$/gm, "").replace(/`[^`\n]+`/g, "");

// The documentation site's pages, and the anchors each one offers: heading slugs, made the way
// the engine's rehype-slug makes them, and explicit ids such as figure ids.
const pages = JSON.parse(await readFile(at("docs/pages/pages.json"), "utf8"));
const anchors = new Map();
for (const { file } of pages) {
  const source = await readFile(at(`docs/pages/${file}`), "utf8");
  const slugger = new GithubSlugger();
  const ids = new Set();
  for (const [, heading] of prose(source).matchAll(/^#{2,6}\s+(.+)$/gm)) {
    ids.add(slugger.slug(heading.replace(/\[([^\]]*)\]\([^)]*\)/g, "$1").replace(/[`*_]/g, "")));
  }
  for (const [, id] of source.matchAll(/\bid="([^"]+)"/g)) ids.add(id);
  anchors.set(file === "index.mdx" ? "" : file.replace(/\.mdx$/, ""), ids);
}

// Only the site's pages are read from docs/: the engine in docs/app and the notes in
// docs/superpowers are not documentation.
const files = [
  "README.md",
  "CLAUDE.md",
  "docs/README.md",
  ...(await markdownFiles(".claude/skills")),
  ...(await markdownFiles("docs/pages")),
];
const broken = [];
for (const file of files) {
  const page = file.match(/^docs\/pages\/(.+)\.mdx$/)?.[1];
  const source = prose(await readFile(at(file), "utf8"));
  // Markdown links, and the HTML links the README-style pages use.
  for (const match of source.matchAll(/\]\(([^\s)]+)\)|\bhref="([^"]+)"/g)) {
    const link = match[1] ?? match[2];
    const [path, anchor] = link.split("#");
    if (/^(?:[a-z]+:|\/\/)/.test(path)) continue;
    if (page !== undefined && (path.startsWith("/") || !path)) {
      // A link between pages of the documentation site, which the site serves at /<page>/.
      const target = path ? path.replace(/^\/|\/$/g, "") : page === "index" ? "" : page;
      if (!anchors.has(target)) broken.push(`${file}: ${link} names no page of the site`);
      else if (anchor && !anchors.get(target).has(anchor)) {
        broken.push(`${file}: ${link} names no heading or id on that page`);
      }
      continue;
    }
    if (!path || path.startsWith("/")) continue;
    await access(resolve(dirname(at(file)), path)).catch(() =>
      broken.push(`${file}: ${link} does not exist`),
    );
  }
}
if (broken.length) throw new Error(`Broken documentation links:\n${broken.join("\n")}`);
console.log(`Checked links in ${files.length} documentation files.`);
