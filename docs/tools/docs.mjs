import "./check-toolchain.mjs";
import { spawn } from "node:child_process";
import { watch } from "node:fs";
import { access, cp, mkdir, readdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { gzipSync } from "node:zlib";

// The Node workspace is docs/: the engine in app/, and the pages, components, embeds and assets
// the documentation is written in.
const root = fileURLToPath(new URL("../", import.meta.url));
const app = join(root, "app");
const [command = "dev", ...args] = process.argv.slice(2);
if (!["dev", "build", "preview"].includes(command)) {
  throw new Error("Usage: node tools/docs.mjs dev|build|preview [Astro options]");
}

// The native engine reads content through both module imports and filesystem paths.
// An ignored working copy preserves those assumptions without writing into the engine.
// Servers get one copy per process, so two can run at once; each removes its own on exit,
// and copies left by a process that no longer runs are removed here.
const cache = join(root, ".cache");
const stage = join(cache, `docs-${command}${command === "build" ? "" : `-${process.pid}`}`);
for (const name of await readdir(cache).catch(() => [])) {
  const pid = Number(name.match(/^(?:docs|guide)-(?:dev|preview)-(\d+)$/)?.[1]);
  if (pid && !isRunning(pid)) await rm(join(cache, name), { recursive: true, force: true });
}
function isRunning(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return error.code === "EPERM";
  }
}
const content = join(stage, "src/content");
const output = join(root, "dist");
if (command === "preview") {
  await access(join(output, "index.html")).catch(() => {
    throw new Error("Build the documentation first with make doc-build.");
  });
}
await rm(stage, { recursive: true, force: true });
await cp(app, stage, {
  recursive: true,
  verbatimSymlinks: true,
  filter: (source) => {
    const path = relative(app, source).split(sep);
    return !path.some(
      (part) => ["node_modules", ".astro", "dist"].includes(part) || part.startsWith(".env"),
    );
  },
});
// Packages resolve from the root npm workspace; Vite caches stay local to this copy.
await mkdir(join(stage, "node_modules"));
// The engine builds one article per site, and the documentation is a set of pages. Each page in
// docs/pages is copied into chapters/: article.mdx imports index.mdx at /, and every other page
// is served at /<name>/ by a copy of the engine's own article page that imports it instead.
await mkdir(join(content, "chapters"), { recursive: true });
const pagesDir = join(root, "pages");
const pages = JSON.parse(await readFile(join(pagesDir, "pages.json"), "utf8")).map((page) => ({
  ...page,
  slug: page.file === "index.mdx" ? "" : page.file.replace(/\.mdx$/, ""),
}));
const articlePage = await readFile(join(app, "src/pages/index.astro"), "utf8");
for (const needle of ['"../content/article.mdx"', '"src/content/article.mdx"']) {
  if (!articlePage.includes(needle)) {
    throw new Error(
      `The engine's article page no longer reads ${needle}; update docs/tools/docs.mjs.`,
    );
  }
}
for (const { slug } of pages.filter((page) => page.slug)) {
  const taken = await access(join(app, "src/pages", slug)).then(
    () => true,
    () =>
      access(join(app, "src/pages", `${slug}.astro`)).then(
        () => true,
        () => false,
      ),
  );
  if (taken) throw new Error(`docs/pages/${slug}.mdx would replace the site's /${slug}/ page.`);
  await writeFile(
    join(stage, "src/pages", `${slug}.astro`),
    articlePage
      .replace('"../content/article.mdx"', `"../content/chapters/${slug}.mdx"`)
      .replace('"src/content/article.mdx"', `"src/content/chapters/${slug}.mdx"`),
  );
}
// Every page gets the same navigation, so pages never link to each other by hand.
await mkdir(join(stage, "src/components/docs"), { recursive: true });
const components = join(root, "components");
await cp(components, join(stage, "src/components/docs"), { recursive: true });
await writeFile(join(stage, "src/components/docs/pages.json"), JSON.stringify(pages, null, 2));
async function writePage(file) {
  const page = pages.find((entry) => entry.file === file);
  if (!page) return;
  const source = await readFile(join(pagesDir, file), "utf8");
  const frontmatter = source.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n/)?.[0] ?? "";
  const nav = 'import DocsNav from "../../components/docs/DocsNav.astro";\n\n<DocsNav />\n';
  const body = `${frontmatter}\n${nav}${source.slice(frontmatter.length)}\n\n<DocsNav position="bottom" />\n`;
  await writeFile(join(content, "chapters", file), body);
  if (!page.slug) {
    const entry = `${frontmatter}\nimport Page from "./chapters/index.mdx";\n\n<Page />\n`;
    await writeFile(join(content, "article.mdx"), entry);
  }
}
for (const { file } of pages) await writePage(file);
// The documentation's own figures live in docs/embeds, and its images and data in docs/assets.
// Each folder is optional and joins the engine's folder of the same name. A shared name would
// silently replace an engine file, so it stops the build instead.
const exists = (path) =>
  access(path).then(
    () => true,
    () => false,
  );
const overlays = [];
for (const folder of ["embeds", "assets"]) {
  const source = join(root, folder);
  if (!(await exists(source))) continue;
  for (const entry of await readdir(source, { recursive: true, withFileTypes: true })) {
    if (!entry.isFile()) continue;
    const name = relative(source, join(entry.parentPath ?? entry.path, entry.name));
    if (await exists(join(app, "src/content", folder, name))) {
      throw new Error(`docs/${folder}/${name} has the same name as an engine file; rename it.`);
    }
  }
  await cp(source, join(content, folder), { recursive: true });
  overlays.push({ source, target: join(content, folder) });
}

const watchers = [];
let pending = Promise.resolve();
function mirror(sourceRoot, targetRoot, accept = () => true) {
  const watcher = watch(sourceRoot, { recursive: true }, (_event, filename) => {
    if (!filename || !accept(filename)) return;
    pending = pending
      .then(async () => {
        const source = join(sourceRoot, filename);
        const target = join(targetRoot, filename);
        const info = await stat(source).catch((error) => {
          if (error.code !== "ENOENT") throw error;
          return null;
        });
        if (!info) await rm(target, { recursive: true, force: true });
        else {
          await mkdir(dirname(target), { recursive: true });
          await cp(source, target, { recursive: info.isDirectory() });
        }
      })
      .catch((error) => console.error("Documentation source update failed:", error));
  });
  watchers.push(watcher);
}

if (command === "dev") {
  for (const { source, target } of overlays) mirror(source, target);
  mirror(components, join(stage, "src/components/docs"));
  const pageWatcher = watch(pagesDir, (_event, filename) => {
    if (!filename?.endsWith(".mdx")) return;
    pending = pending
      .then(() => writePage(filename))
      .catch((error) => console.error("Documentation page update failed:", error));
  });
  watchers.push(pageWatcher);
}

// The command-line entry is the one Astro's package.json declares, so a release that moves it
// still starts.
const astroPackage = join(root, "node_modules/astro/package.json");
const { bin } = JSON.parse(await readFile(astroPackage, "utf8"));
const astro = resolve(dirname(astroPackage), typeof bin === "string" ? bin : bin.astro);
const flags = command === "dev" ? [] : ["--outDir", output];
if (command !== "build") {
  // Astro detaches a server it believes an AI agent started, and this process removes the
  // server's copy as soon as Astro returns. --ignore-lock keeps the server in the foreground;
  // the lock it skips guards one server per project, and each server here has its own copy.
  flags.push("--host", "127.0.0.1", "--ignore-lock");
  if (!args.some((arg) => arg === "--port" || arg.startsWith("--port="))) {
    flags.push("--port", command === "dev" ? "8031" : "8033");
  }
}
const child = spawn(process.execPath, [astro, command, ...flags, ...args], {
  cwd: stage,
  stdio: "inherit",
});
for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => child.kill(signal));
}
child.on("error", (error) => {
  console.error(error);
  for (const watcher of watchers) watcher.close();
  process.exitCode = 1;
});
child.on("exit", async (code, signal) => {
  for (const watcher of watchers) watcher.close();
  process.exitCode = code ?? (signal === "SIGINT" || signal === "SIGTERM" ? 0 : 1);
  if (command === "build" && code === 0) await exportAllPagesAsText();
  if (command !== "build") await rm(stage, { recursive: true, force: true });
});

// The engine's llms.txt export follows the chapters the entry file renders, and the site's
// entry renders only the overview. After the build, run the same upstream export once more on
// an entry that renders every page, so the text export covers the whole documentation.
async function exportAllPagesAsText() {
  const overview = await readFile(join(pagesDir, "index.mdx"), "utf8");
  const frontmatter = overview.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n/)?.[0] ?? "";
  const imports = pages.map((page, i) => `import Page${i} from "./chapters/${page.file}";`);
  const tags = pages.map((_, i) => `<Page${i} />`);
  await writeFile(
    join(content, "article.mdx"),
    `${frontmatter}\n${imports.join("\n")}\n\n${tags.join("\n\n")}\n`,
  );
  const plugin = pathToFileURL(join(stage, "plugins/astro/generate-llms-txt.mjs"));
  const { hooks } = (await import(plugin)).default();
  const cwd = process.cwd();
  process.chdir(stage);
  try {
    await hooks["astro:build:done"]({ dir: pathToFileURL(`${output}/`) });
  } finally {
    process.chdir(cwd);
  }
  const text = await readFile(join(output, "llms.txt"));
  await writeFile(join(output, "llms.txt.gz"), gzipSync(text));
}
