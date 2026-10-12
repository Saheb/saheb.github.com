const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { pathToFileURL } = require('node:url');

const root = path.resolve(__dirname, '..');
const runtime = path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies');
let chromium;
try {
  ({ chromium } = require('playwright'));
} catch (error) {
  if (error.code !== 'MODULE_NOT_FOUND') throw error;
  ({ chromium } = require(path.join(runtime, 'node/node_modules/playwright')));
}

async function main() {
  const profiles = JSON.parse(fs.readFileSync(path.join(root, 'cv/profiles.json'), 'utf8'));
  const selected = process.argv.slice(2);
  const names = selected.length ? selected : Object.keys(profiles);
  for (const name of names) {
    if (!profiles[name]) throw new Error(`Unknown CV profile: ${name}`);
  }
  const bundledPython = path.join(runtime, 'python/bin/python3');
  const python = fs.existsSync(bundledPython) ? bundledPython : 'python3';
  const build = spawnSync(python, [path.join(root, 'scripts/build-cvs.py')], { encoding: 'utf8' });
  if (build.error) throw build.error;
  if (build.status !== 0) throw new Error(build.stderr || 'CV generation failed');

  const defaultChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  const chrome = process.env.CV_CHROME_EXECUTABLE || (fs.existsSync(defaultChrome) ? defaultChrome : undefined);
  const browser = await chromium.launch({ executablePath: chrome, headless: true });
  try {
    const outputDir = path.join(root, 'output/pdf');
    fs.mkdirSync(outputDir, { recursive: true });
    for (const name of names) {
      const profile = profiles[name];
      if (!/^[A-Za-z0-9-]+\.pdf$/.test(profile.pdf_filename)) throw new Error('Invalid PDF filename');
      const page = await browser.newPage({ viewport: { width: 673, height: 1032 } });
      await page.goto(pathToFileURL(path.join(root, profile.filename)).href, { waitUntil: 'load' });
      await page.emulateMedia({ media: 'print' });
      const geometry = await page.locator('.cv-page').evaluateAll(pages => pages.map(p => ({
        height: p.getBoundingClientRect().height,
        contentBottom: p.querySelector('section:last-of-type').getBoundingClientRect().bottom - p.getBoundingClientRect().top,
      })));
      const contentLimit = 272 * 96 / 25.4 - 24;
      if (geometry.some(p => p.contentBottom > contentLimit)) {
        throw new Error(`${name}: content crowds the footer: ${JSON.stringify(geometry)}`);
      }
      const output = path.join(outputDir, profile.pdf_filename);
      await page.pdf({ path: output, printBackground: true, preferCSSPageSize: true, displayHeaderFooter: false, tagged: true });
      await page.emulateMedia({ media: 'screen' });
      await page.setViewportSize({ width: 390, height: 844 });
      if (await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)) {
        throw new Error(`${name}: horizontal overflow on mobile`);
      }
      console.log(JSON.stringify({ profile: name, output, geometry, mobileOverflow: false }));
      await page.close();
    }
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
