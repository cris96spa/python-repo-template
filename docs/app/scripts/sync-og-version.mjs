#!/usr/bin/env node
/**
 * Fingerprint the OG image URL in README.md with a content hash of the article.
 *
 * Why: social platforms (X/Twitter, LinkedIn, Slack, …) cache the share preview
 * by image URL and rarely re-fetch on their own. X removed its Card Validator,
 * so the only reliable way to refresh an existing preview is to change the
 * image URL. We append `?v=<hash>` where the hash is derived from the article
 * source, so the URL only changes when the article actually changes.
 *
 * The app page (served on *.hf.space) computes the very same hash at build time
 * in `src/pages/index.astro`. This script keeps the README `thumbnail:` field
 * (used by the huggingface.co Space card, which is what gets scraped when the
 * Space URL is shared) in sync with it.
 *
 * Run it before deploying when the article changed:
 *   npm run og:sync
 * then commit README.md and push.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const appRoot = resolve(scriptDir, '..'); // app/
const repoRoot = resolve(appRoot, '..'); // repository root
const articlePath = resolve(appRoot, 'src/content/article.mdx');
const readmePath = resolve(repoRoot, 'README.md');

// Keep this in sync with the hashing logic in src/pages/index.astro.
function computeVersion() {
  const source = readFileSync(articlePath, 'utf8');
  return createHash('sha256').update(source).digest('hex').slice(0, 10);
}

function main() {
  const version = computeVersion();

  let readme;
  try {
    readme = readFileSync(readmePath, 'utf8');
  } catch {
    console.error(`❌ README.md not found at ${readmePath}`);
    process.exit(1);
  }

  // Match: thumbnail: https://<space>.hf.space/thumb.auto.jpg[?v=...]
  const thumbRe = /^(thumbnail:[^\n]*thumb\.auto\.jpg)(\?\S*)?[ \t]*$/m;

  if (!thumbRe.test(readme)) {
    console.warn(
      '⚠️  No "thumbnail: …/thumb.auto.jpg" line found in README.md — nothing to fingerprint.',
    );
    console.log(`   OG version would be: ?v=${version}`);
    return;
  }

  const updated = readme.replace(thumbRe, `$1?v=${version}`);

  if (updated === readme) {
    console.log(`✅ README thumbnail already up to date (?v=${version}).`);
    return;
  }

  writeFileSync(readmePath, updated);
  console.log(`✅ README thumbnail fingerprinted: ?v=${version}`);
  console.log('   Commit README.md and redeploy so the Space card refreshes.');
}

main();
