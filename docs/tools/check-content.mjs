import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";

// The engine in docs/app is used exactly as upstream ships it. Each file is compared with the
// hash recorded for it, so an edit to the engine fails here, before the build does.
const root = new URL("../", import.meta.url);
const provenance = JSON.parse(await readFile(new URL("template-provenance.json", root), "utf8"));
for (const [file, expected] of Object.entries(provenance.upstreamFiles)) {
  const actual = createHash("sha256")
    .update(await readFile(new URL(file, root)))
    .digest("hex");
  assert.equal(
    actual,
    expected,
    `Upstream implementation changed: docs/${file}. Review and record the change.`,
  );
}
console.log(`Verified ${Object.keys(provenance.upstreamFiles).length} upstream engine files.`);
