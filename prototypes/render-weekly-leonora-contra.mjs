import { createRequire } from 'node:module';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('/Users/bytedance/.codex/skills/wechat-article-fetch/node_modules/playwright');

const here = path.dirname(fileURLToPath(import.meta.url));
const htmlPath = path.join(here, 'weekly-2026-07-21-to-07-27-leonora-contra.html');
const outputDir = path.join(here, 'weekly-2026-07-21-to-07-27-leonora-contra');
await mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 810 }, deviceScaleFactor: 1 });
const pageErrors = [];
page.on('pageerror', (error) => pageErrors.push(String(error)));
await page.goto(`file://${htmlPath}`, { waitUntil: 'load' });
await page.evaluate(() => document.fonts?.ready);

const frames = page.locator('.frame');
const frameCount = await frames.count();
for (let index = 0; index < frameCount; index += 1) {
  await frames.nth(index).screenshot({ path: path.join(outputDir, `frame-${String(index + 1).padStart(2, '0')}.png`) });
}
await page.screenshot({ path: path.join(outputDir, 'full-page.png'), fullPage: true });

const desktopMetrics = await page.evaluate(() => ({
  viewportWidth: document.documentElement.clientWidth,
  bodyScrollWidth: document.documentElement.scrollWidth,
  pageHasHorizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  frameCount: document.querySelectorAll('.frame').length,
  frameAspectRatios: [...document.querySelectorAll('.frame')].map((frame) => {
    const rect = frame.getBoundingClientRect();
    return Number((rect.width / rect.height).toFixed(2));
  }),
}));

const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
const mobileErrors = [];
mobile.on('pageerror', (error) => mobileErrors.push(String(error)));
await mobile.goto(`file://${htmlPath}`, { waitUntil: 'load' });
await mobile.evaluate(() => document.fonts?.ready);
await mobile.screenshot({ path: path.join(outputDir, 'mobile-full-page.png'), fullPage: true });
const mobileMetrics = await mobile.evaluate(() => ({
  viewportWidth: document.documentElement.clientWidth,
  bodyScrollWidth: document.documentElement.scrollWidth,
  pageHasHorizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  frameCount: document.querySelectorAll('.frame').length,
  frameMinHeights: [...document.querySelectorAll('.frame')].map((frame) => Math.round(frame.getBoundingClientRect().height))
}));

await browser.close();
console.log(JSON.stringify({ outputDir, frameCount, pageErrors, desktopMetrics, mobileErrors, mobileMetrics }, null, 2));
