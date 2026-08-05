import { createRequire } from 'node:module';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('/Users/bytedance/.codex/skills/wechat-article-fetch/node_modules/playwright');

const here = path.dirname(fileURLToPath(import.meta.url));
const htmlPath = path.join(here, 'weekly-2026-07-21-to-07-27-leonora-carrington.html');
const outputDir = path.join(here, 'weekly-2026-07-21-to-07-27-leonora-carrington');
await mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 810 }, deviceScaleFactor: 1 });
const pageErrors = [];
page.on('pageerror', error => pageErrors.push(String(error)));
await page.goto(`file://${htmlPath}`, { waitUntil: 'load' });
await page.evaluate(() => document.fonts?.ready);

const frames = page.locator('.frame');
const frameCount = await frames.count();
for (let i = 0; i < frameCount; i += 1) {
  await frames.nth(i).screenshot({ path: path.join(outputDir, `frame-${String(i + 1).padStart(2, '0')}.png`) });
}
await page.screenshot({ path: path.join(outputDir, 'full-page.png'), fullPage: true });

const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
await mobile.goto(`file://${htmlPath}`, { waitUntil: 'load' });
await mobile.evaluate(() => document.fonts?.ready);
const mobileMetrics = await mobile.evaluate(() => {
  const allFrames = [...document.querySelectorAll('.frame')];
  return {
    viewportWidth: document.documentElement.clientWidth,
    bodyScrollWidth: document.documentElement.scrollWidth,
    frameCount: allFrames.length,
    overflowingFrames: allFrames.filter(frame => frame.scrollWidth > frame.clientWidth + 1).length,
    overflowingFrameLabels: allFrames.filter(frame => frame.scrollWidth > frame.clientWidth + 1).map(frame => frame.dataset.frame),
    frameAspectRatios: allFrames.map(frame => {
      const rect = frame.getBoundingClientRect();
      return Number((rect.width / rect.height).toFixed(2));
    })
  };
});

await browser.close();
console.log(JSON.stringify({ frameCount, outputDir, pageErrors, mobileMetrics }, null, 2));
