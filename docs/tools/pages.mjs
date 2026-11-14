import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { normalizeBase, rebase } from "./rebase.mjs";

// Builds the documentation as GitHub Pages publishes it, for the subpath and origin Pages
// serves it at.
const root = fileURLToPath(new URL("../", import.meta.url));
const [baseValue, originValue] = process.argv.slice(2);
if (!baseValue) {
  throw new Error("Usage: npm run pages:build -- /<repository>/ [https://<origin>]");
}
const base = normalizeBase(baseValue);
const origin = originValue?.replace(/\/+$/, "");

const build = spawnSync(process.execPath, ["tools/docs.mjs", "build", "--base", base], {
  cwd: root,
  stdio: "inherit",
});
if (build.status !== 0) process.exit(build.status ?? 1);
if (base !== "/" || origin) await rebase(`${root}dist`, base, origin);
