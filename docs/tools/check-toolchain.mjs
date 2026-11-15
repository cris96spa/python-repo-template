import { existsSync, readFileSync } from "node:fs";

// The scripts behind make doc, make doc-build and make doc-check import this module first, so
// a missing install or a Node.js older than the engines field stops them with what to do
// instead of a stack trace from inside a dependency. Astro itself refuses to start on an older
// Node.js, so there is nothing to try below that release.
const root = new URL("../", import.meta.url);
function stop(...lines) {
  console.error(lines.join("\n"));
  process.exit(1);
}

const { engines } = JSON.parse(readFileSync(new URL("package.json", root), "utf8"));
const required = engines.node.replace(/^>=\s*/, "");
// Numeric collation compares each run of digits as a number, so 22.9.0 sorts below 22.23.4.
if (process.versions.node.localeCompare(required, "en", { numeric: true }) < 0) {
  stop(
    `The documentation needs Node.js ${required} or later, and this is Node.js ${process.versions.node}; switch to a newer Node.js and run the command again.`,
  );
}

for (const dependency of ["astro", "github-slugger"]) {
  if (!existsSync(new URL(`node_modules/${dependency}/package.json`, root))) {
    stop(
      `The documentation toolchain is not installed: docs/node_modules/${dependency} is missing.`,
      "Run make install-docs from the repository root, then run the command again.",
    );
  }
}
