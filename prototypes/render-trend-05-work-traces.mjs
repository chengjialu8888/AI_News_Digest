import { mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('/Users/bytedance/.codex/skills/wechat-article-fetch/node_modules/playwright');

const root = resolve(import.meta.dirname);
const htmlPath = resolve(root, 'trend-05-work-traces-visual.html');
const outputDir = resolve(root, 'weekly-2026-07-21-to-07-27-contemporary-exhibition');
mkdirSync(outputDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 810 }, deviceScaleFactor: 1 });
const pageErrors = [];
page.on('pageerror', (error) => pageErrors.push(error.message));

await page.goto(`file://${htmlPath}`, { waitUntil: 'load' });
await page.waitForTimeout(250);
await page.locator('.frame').screenshot({ path: resolve(outputDir, 'trend-05-work-traces.png') });

const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
await mobile.goto(`file://${htmlPath}`, { waitUntil: 'load' });
await mobile.waitForTimeout(150);
const mobileMetrics = await mobile.evaluate(() => ({
  viewportWidth: document.documentElement.clientWidth,
  bodyScrollWidth: document.body.scrollWidth,
  frameCount: document.querySelectorAll('.frame').length,
  overflowingFrames: [...document.querySelectorAll('.frame')]
    .filter((frame) => frame.scrollWidth > frame.clientWidth + 1 || frame.scrollHeight > frame.clientHeight + 1)
    .length,
}));

console.log(JSON.stringify({ output: resolve(outputDir, 'trend-05-work-traces.png'), pageErrors, mobileMetrics }, null, 2));
await browser.close();
