import "./check-toolchain.mjs";
import { createHash } from "node:crypto";
import { readdir, readFile } from "node:fs/promises";
import { join, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";

// The engine in docs/app is changed only in the template, which records the hash of every engine
// file in template-provenance.json. A file edited, added or removed in place fails here, before
// the build does.
const root = fileURLToPath(new URL("../", import.meta.url));
const { engineFiles } = JSON.parse(await readFile(join(root, "template-provenance.json"), "utf8"));

// Installs and builds write node_modules, .astro and dist next to the engine; they are not part
// of it. Symbolic links, such as public/data, are not files of their own.
async function filesUnder(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory() && !["node_modules", ".astro", "dist"].includes(entry.name)) {
      files.push(...(await filesUnder(path)));
    } else if (entry.isFile()) {
      files.push(relative(root, path).split(sep).join("/"));
    }
  }
  return files;
}

const present = new Set(await filesUnder(join(root, "app")));
const problems = [];
for (const [file, expected] of Object.entries(engineFiles)) {
  if (!present.has(file)) {
    problems.push(`docs/${file} is missing`);
    continue;
  }
  const actual = createHash("sha256")
    .update(await readFile(join(root, file)))
    .digest("hex");
  if (actual !== expected) problems.push(`docs/${file} was edited`);
}
for (const file of present) {
  if (!(file in engineFiles)) problems.push(`docs/${file} is not an engine file`);
}
if (problems.length) {
  console.error(
    [
      "The engine in docs/app differs from the one docs/template-provenance.json records:",
      ...problems.map((problem) => `  ${problem}`),
      "Projects take the engine from the template: restore these files from python-repo-template. In the template, record the new hashes with the change.",
    ].join("\n"),
  );
  process.exit(1);
}
console.log(`Verified ${present.size} engine files.`);
