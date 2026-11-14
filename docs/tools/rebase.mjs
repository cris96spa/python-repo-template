import { access, readdir, readFile, writeFile } from "node:fs/promises";
import { join, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { gzipSync } from "node:zlib";

// GitHub Pages serves a project site under /<repository>/, while the engine assumes the site
// root. Astro's --base prefixes its own assets; this prefixes the rest of a built site, so the
// engine's files stay untouched:
// - root-relative src and href attributes the template writes, such as /scripts/...;
// - paths under /data/ and /scripts/ that figures and bundled scripts load at run time;
// - with an origin, the absolute addresses the engine builds from Astro's default
//   http://localhost:4321, such as the canonical and social URLs.
// Code that a page displays, in <pre>, <code> and <textarea>, is left exactly as written.
const BUILD_ORIGIN = "http://localhost:4321";
const RUNTIME_FOLDERS = ["data", "scripts"];

export async function rebase(directory, prefix, origin) {
  const files = (await readdir(directory, { recursive: true, withFileTypes: true }))
    .filter((entry) => entry.isFile())
    .map((entry) => join(entry.parentPath ?? entry.path, entry.name).slice(directory.length + 1));
  const built = new Set(files.map((file) => file.split(sep).join("/")));
  // A path already starts with the prefix when Astro based it, except when the repository
  // itself is named like a runtime folder: then /data/x.csv is a figure path still to prefix,
  // while /data/_astro/x.js is already based. The build output tells them apart.
  const ambiguous = RUNTIME_FOLDERS.some((folder) => prefix === `/${folder}/`);
  const isBased = (url) => {
    if (!url.startsWith(prefix)) return false;
    if (!ambiguous) return true;
    const rest = url.slice(prefix.length).split(/[?#]/)[0];
    return !rest || built.has(rest) || built.has(`${rest.replace(/\/?$/, "/")}index.html`);
  };
  const based = (url) => (isBased(url) ? url : `${prefix}${url.slice(1)}`);

  let count = 0;
  const runtime = new RegExp(
    `(["'\`]|&#34;|&#39;|&quot;)(/(?:${RUNTIME_FOLDERS.join("|")})/[^"'\`&<>\\s]*)`,
    "g",
  );
  const rewriteRuntime = (text) =>
    text.replace(runtime, (match, quote, url) => {
      if (isBased(url)) return match;
      count += 1;
      return `${quote}${based(url)}`;
    });
  const rewriteHtml = (text) => {
    let next = rewriteRuntime(text).replace(
      /\b(src|href)="(\/(?!\/)[^"]*)"/g,
      (match, attribute, url) => {
        if (isBased(url) || url === prefix.slice(0, -1)) return match;
        count += 1;
        return `${attribute}="${based(url)}"`;
      },
    );
    if (origin) {
      next = next.replaceAll(new RegExp(`${BUILD_ORIGIN}(/[^"'\\s<>]*)?`, "g"), (_, path) => {
        count += 1;
        return `${origin}${based(path || "/")}`;
      });
    }
    return next;
  };

  for (const file of files.filter((name) => /\.(html|js)$/.test(name))) {
    const path = join(directory, file);
    const source = await readFile(path, "utf8");
    const next = file.endsWith(".js")
      ? rewriteRuntime(source)
      : source
          .split(/(<(pre|code|textarea)\b[^>]*>[\s\S]*?<\/\2>)/i)
          .map((part, i) => (i % 3 === 0 ? rewriteHtml(part) : i % 3 === 1 ? part : ""))
          .join("");
    if (next === source) continue;
    await writeFile(path, next);
    // The build also writes precompressed copies, which hosts may serve instead; keep them equal.
    const gzipped = `${path}.gz`;
    if (
      await access(gzipped).then(
        () => true,
        () => false,
      )
    ) {
      await writeFile(gzipped, gzipSync(next));
    }
  }
  const pages = files.filter((file) => file.endsWith(".html")).length;
  console.log(`Prefixed ${count} root-relative addresses in ${pages} pages with ${prefix}.`);
}

export function normalizeBase(value) {
  return `/${(value || "").replace(/^\/+|\/+$/g, "")}/`.replace(/^\/\/$/, "/");
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [directory, base, origin] = process.argv.slice(2);
  if (!directory || !base) {
    throw new Error("Usage: node tools/rebase.mjs <directory> <base> [origin]");
  }
  await rebase(directory, normalizeBase(base), origin?.replace(/\/+$/, ""));
}
