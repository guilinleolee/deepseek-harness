#!/usr/bin/env node
/*
 * render-poster.mjs — render <section class="poster"> sections as isolated PNGs via Playwright.
 *
 * Usage:
 *   node render-poster.mjs <task-dir> [output-dir]
 *
 * For each <section class="poster"> in the HTML, set the page viewport to
 * exactly that section's bounding box and take a full-page screenshot so the
 * output is the poster alone (no bleed from sibling sections in the same HTML).
 */
import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const taskDir = path.resolve(process.argv[2] || ".");
const outputDir = path.resolve(process.argv[3] || path.join(taskDir, "output"));
if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

const htmlPath = path.join(taskDir, "index.html");
if (!fs.existsSync(htmlPath)) {
  console.error(`not found: ${htmlPath}`);
  process.exit(2);
}

const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });

const sections = await (async () => {
  // Two-phase: open once, collect bounding boxes, then take per-section shots
  // with a re-sized viewport so sibling sections don't appear in the output.
  const ctx = await browser.newContext({
    viewport: { width: 2400, height: 1500 },
    deviceScaleFactor: 1,
  });
  const page = await ctx.newPage();
  await page.goto("file://" + htmlPath, { waitUntil: "domcontentloaded", timeout: 15000 });
  await page.waitForTimeout(1500);
  const debug = await page.evaluate(() => {
    const all = document.querySelectorAll("*");
    const sections = document.querySelectorAll("section");
    const posters = document.querySelectorAll("section.poster");
    return {
      totalNodes: all.length,
      totalSections: sections.length,
      posterSections: posters.length,
      bodyChildren: document.body ? document.body.children.length : 0,
      bodyOuterHTML: document.body ? document.body.outerHTML.slice(0, 300) : "(no body)",
      documentReadyState: document.readyState,
      posterIds: Array.from(posters).map(p => p.id || p.className),
    };
  });
  console.error("[debug]", JSON.stringify(debug).slice(0, 800));
  const nodes = await page.$$("section.poster");
  const boxes = [];
  for (const s of nodes) {
    const id = (await s.getAttribute("id")) || "";
    const box = await s.boundingBox();
    boxes.push({ el: s, id, box });
  }
  await ctx.close();
  return boxes;
})();

console.log(`found ${sections.length} poster section(s)`);
let i = 0;
for (const { el, id, box } of sections) {
  i += 1;
  const useId = id || `poster-${i}`;
  // Re-open a fresh page for each shot with viewport matched to this poster only.
  const ctx = await browser.newContext({
    viewport: { width: Math.ceil(box.width), height: Math.ceil(box.height) },
    deviceScaleFactor: 1,
  });
  const page = await ctx.newPage();
  await page.route("**/*", (route) => {
    const url = route.request().url();
    if (url.startsWith("file://") || url.startsWith("data:") || url.startsWith("about:")) return route.continue();
    return route.fulfill({ status: 204, body: "" });
  });
  await page.goto("file://" + htmlPath, { waitUntil: "domcontentloaded", timeout: 15000 });
  await page.waitForTimeout(1500);
  const target = await page.$("#" + useId).catch(() => null);
  // If id didn't resolve, take the i-th poster element directly.
  const handle = target || (await page.$$("section.poster"))[i - 1];
  const outPath = path.join(outputDir, `${useId}.png`);
  await handle.screenshot({ path: outPath });
  const stat = fs.statSync(outPath);
  console.log(`  ✓ ${useId} → ${outPath} (${stat.size} bytes, ${Math.round(box.width)}×${Math.round(box.height)})`);
  await ctx.close();
}
await browser.close();
console.log(`done → ${outputDir}`);