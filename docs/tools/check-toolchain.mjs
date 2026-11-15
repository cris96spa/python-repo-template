import { existsSync, readFileSync } from "node:fs";

// The scripts behind make doc, make doc-build and make doc-check import this module first, so
// a missing install stops them with what to do instead of a stack trace from inside a
// dependency. A Node.js older than the engines field names only gets a warning: the site is
// checked on that release and later, and an older one may still build it.
const root = new URL("../", import.meta.url);
function stop(...lines) {
  console.error(lines.join("\n"));
  process.exit(1);
}

const { engines } = JSON.parse(readFileSync(new URL("package.json", root), "utf8"));
const required = engines.node.replace(/^>=\s*/, "");
// Numeric collation compares each run of digits as a number, so 22.9.0 sorts below 22.12.0.
if (process.versions.node.localeCompare(required, "en", { numeric: true }) < 0) {
  console.warn(
    `The documentation is checked on Node.js ${required} or later, and this is Node.js ${process.versions.node}. If a command fails, switch to a newer Node.js first.`,
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
