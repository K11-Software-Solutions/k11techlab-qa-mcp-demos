// Render source.html to PNG frames with Playwright's Chromium.
//   node render.cjs <playwright module path> [fps] [only-seconds-comma-separated]
const { chromium } = require(process.argv[2]);
const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");

(async () => {
  const fps = +(process.argv[3] || 30);
  const only = process.argv[4] ? process.argv[4].split(",").map(Number) : null;
  const out = path.join(__dirname, only ? "keyframes" : "frames");
  fs.rmSync(out, { recursive: true, force: true });
  fs.mkdirSync(out);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1080 } });
  await page.goto(pathToFileURL(path.join(__dirname, "source.html")).href);
  await page.evaluate(() => document.fonts.ready);
  const total = await page.evaluate(() => window.TOTAL);
  const times = only || Array.from({ length: Math.round(total * fps) }, (_, i) => i / fps);
  for (let i = 0; i < times.length; i++) {
    await page.evaluate((t) => window.render(t), times[i]);
    const name = only ? `t${String(times[i]).replace(".", "_")}.png` : `${String(i).padStart(5, "0")}.png`;
    await page.screenshot({ path: path.join(out, name) });
  }
  await browser.close();
  console.log(`${times.length} frame(s), ${total}s`);
})();
