#!/usr/bin/env node
/*
 * validate-social-deck.mjs
 *
 *   node validate-social-deck.mjs <task-dir|index.html>
 *
 * Checks each <section class="poster …"> in the target HTML against the rules
 * codified in SKILL.md / qa-checklist.md / components.md. Exits 1 if any FAIL.
 *
 * Rules implemented:
 *   R1  overflow              scrollHeight > clientHeight on the poster
 *   R2  footer collision      .foot is position:absolute AND content above reaches into its band
 *   R3  swiss bold display    .h-xl / .h-hero / .h-statement / .num-mega with computed weight >= 600
 *   R4  min readable font     body/lead/caption/label/meta below the mobile-safe floor
 *   R5  4-band density        on 3:4 boards: <75% filled OR any under-filled band > 216px
 *   R6  h-xl hard cap         display title lines/chars exceed the per-board cap
 *   R7  figure margin drift    browser-default <figure> margin offsets media alignment
 *   R8  visual bounds          measured top/bottom blank space and visual overflow
 *   R9  title gap              display title touches the next content block
 */
import { chromium } from "playwright";
import { fileURLToPath } from "node:url";
import path from "node:path";
import fs from "node:fs";

const args = process.argv.slice(2);
let target = null;
let styleOverride = null;
for (const a of args) {
  if (a.startsWith("--style=")) styleOverride = a.slice(8);
  else if (!target) target = a;
}
if (!target) {
  console.error("usage: node validate-social-deck.mjs <task-dir|index.html> [--style=swiss|editorial]");
  process.exit(2);
}
const abs = path.resolve(target);
let htmlPath = abs;
if (fs.statSync(abs).isDirectory()) {
  htmlPath = path.join(abs, "index.html");
}
if (!fs.existsSync(htmlPath)) {
  console.error(`not found: ${htmlPath}`);
  process.exit(2);
}

const url = "file://" + htmlPath;
const browser = await chromium.launch({
  args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
const ctx = await browser.newContext({
  viewport: { width: 1400, height: 1700 },
  deviceScaleFactor: 1,
});
const page = await ctx.newPage();
// Block external fonts/CDN: they hang in offline/sandboxed environments and are not
// required for layout/DOM measurements. Allow same-origin (file://) and data URLs.
await page.route("**/*", (route) => {
  const url = route.request().url();
  if (url.startsWith("file://") || url.startsWith("data:") || url.startsWith("about:")) {
    return route.continue();
  }
  // External request: short-circuit with empty 204 so Chromium stops waiting.
  return route.fulfill({ status: 204, body: "" });
});
// domcontentloaded is enough — measurements are DOM-based, not network-based.
await page.goto(url, { waitUntil: "domcontentloaded", timeout: 15000 });
await page.waitForTimeout(1200);

const style = styleOverride || await page.evaluate(() => {
  const html = document.documentElement;
  if (html.dataset.theme) return "editorial";
  if (html.dataset.accent) return "swiss";
  // Fallback: any display class using a serif family = editorial; otherwise swiss.
  // Note: "sans-serif" generic name also contains the substring "serif", so we
  // match on serif-only families by token, not substring.
  const SERIF_TOKENS = ["noto serif", "playfair", "source serif", "songti", "stsong", "simsun", "serif sc", "kinfolk", "merriweather"];
  for (const n of document.querySelectorAll(".h-display, .h-xl, .h-hero, .pullquote, .h-statement")) {
    const ff = getComputedStyle(n).fontFamily.toLowerCase();
    if (SERIF_TOKENS.some(t => ff.includes(t))) return "editorial";
  }
  return "swiss";
});

const sections = await page.$$("section.poster");
const report = [];

// "Obviously too small" floors — below these, text becomes unreadable at phone size.
// Seeds use 26-28px body, 30-32px lead — those are fine. Anything 4+px below is suspect.
const MIN_FONT = {
  body: 22,
  lead: 26,
  caption: 18,
  meta: 18,
  cellTitle: 20,
  numAnnotation: 20,
};

const HXL_CAPS = {
  xhs:    { maxLines: 2, maxChars: 8 },
  square: { maxLines: 2, maxChars: 7 },
  wide:   { maxLines: 1, maxChars: 14 },
};

const DISPLAY_CLASSES = ["h-xl", "h-hero", "h-statement", "h-display", "num-mega", "num-xl"];

function overflowFix(px) {
  const n = Math.round(px);
  if (n <= 40) {
    return `only ${n}px over: nudge content up or tighten one gap/padding by 20-40px; do not delete content`;
  }
  if (n <= 90) {
    return `${n}px over: compact local gaps/padding and reduce one block height; avoid cutting copy`;
  }
  if (n <= 160) {
    return `${n}px over: reduce a display title slightly or compress one paragraph before deleting content`;
  }
  return `${n}px over: switch to a higher-capacity recipe or remove/merge content intentionally`;
}

for (const s of sections) {
  const meta = await s.evaluate(el => {
    const w = el.clientWidth, h = el.clientHeight;
    let board = el.classList.contains("xhs") ? "xhs"
              : el.classList.contains("square") ? "square"
              : el.classList.contains("wide") ? "wide" : null;
    if (!board) {
      const ratio = w / h;
      if (Math.abs(ratio - 0.75) < 0.02) board = "xhs";        // 3:4
      else if (Math.abs(ratio - 1.0) < 0.02) board = "square"; // 1:1
      else if (Math.abs(ratio - 7 / 3) < 0.05) board = "wide"; // 21:9
      else board = "unknown";
    }
    return { id: el.id || "(no-id)", dataId: el.dataset.id || "", board, clientH: h, scrollH: el.scrollHeight, clientW: w };
  });
  const fails = [];
  const warns = [];

  // R1 overflow
  const overflow = meta.scrollH - meta.clientH;
  if (overflow > 4) {
    fails.push({ rule: "R1", msg: `overflow ${overflow}px (scrollH ${meta.scrollH} > clientH ${meta.clientH})`, fix: overflowFix(overflow) });
  }

  // R8 visual bounds — measures the true rendered content extent, not just scrollHeight.
  const visualBounds = await s.evaluate(el => {
    const er = el.getBoundingClientRect();
    const H = el.clientHeight;
    const W = el.clientWidth;
    const posterArea = H * W;
    const TRANSPARENT = /rgba?\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0?\s*\)|transparent/;
    const hasDirectText = n => {
      for (const c of n.childNodes) {
        if (c.nodeType === 3 && c.textContent.trim().length > 0) return true;
      }
      return false;
    };
    const cssColorVisible = c => c && !TRANSPARENT.test(c);
    const meaningful = [];
    for (const n of el.querySelectorAll("*")) {
      if (n.closest("script, style")) continue;
      const tag = n.tagName;
      const cs = getComputedStyle(n);
      const r = n.getBoundingClientRect();
      if (r.width < 6 || r.height < 6) continue;
      if (n === el || n.classList.contains("content")) continue;
      if (cs.position === "absolute" && r.width * r.height >= posterArea * 0.85) continue;

      const isText = hasDirectText(n);
      const isMedia = tag === "IMG" || tag === "CANVAS" || tag === "SVG";
      const isRule = tag === "HR" || (r.height <= 4 && (
        parseFloat(cs.borderTopWidth) >= 1 ||
        parseFloat(cs.borderBottomWidth) >= 1 ||
        cssColorVisible(cs.backgroundColor)
      ));
      const hasBoxFill = cssColorVisible(cs.backgroundColor) &&
        r.width * r.height >= 1600 &&
        !["MAIN", "SECTION"].includes(tag);
      const hasBorderBox = (parseFloat(cs.borderTopWidth) + parseFloat(cs.borderBottomWidth) +
        parseFloat(cs.borderLeftWidth) + parseFloat(cs.borderRightWidth)) >= 1 &&
        r.width * r.height >= 1600;
      if (!isText && !isMedia && !isRule && !hasBoxFill && !hasBorderBox) continue;
      meaningful.push({
        top: r.top - er.top,
        bottom: r.bottom - er.top,
        left: r.left - er.left,
        right: r.right - er.left,
        cls: n.className ? "." + String(n.className).split(" ").filter(Boolean).join(".") : tag.toLowerCase(),
        text: n.textContent.trim().replace(/\s+/g, " ").slice(0, 32),
      });
    }
    if (meaningful.length === 0) return null;
    let top = Infinity, bottom = -Infinity;
    let topNode = null, bottomNode = null;
    for (const item of meaningful) {
      if (item.top < top) {
        top = item.top;
        topNode = item;
      }
      if (item.bottom > bottom) {
        bottom = item.bottom;
        bottomNode = item;
      }
    }
    return {
      top: Math.round(top),
      bottom: Math.round(bottom),
      activeHeight: Math.round(bottom - top),
      activeRatio: (bottom - top) / H,
      topGap: Math.max(0, Math.round(top)),
      bottomGap: Math.max(0, Math.round(H - bottom)),
      topOverflow: Math.max(0, Math.round(-top)),
      bottomOverflow: Math.max(0, Math.round(bottom - H)),
      topNode,
      bottomNode,
      count: meaningful.length,
    };
  });
  if (visualBounds) {
    if (visualBounds.bottomOverflow > 4) {
      fails.push({
        rule: "R8",
        msg: `visual bottom overflow ${visualBounds.bottomOverflow}px (lowest: ${visualBounds.bottomNode.cls}${visualBounds.bottomNode.text ? ` "${visualBounds.bottomNode.text}"` : ""})`,
        fix: overflowFix(visualBounds.bottomOverflow),
      });
    }
    if (visualBounds.topOverflow > 4) {
      fails.push({
        rule: "R8",
        msg: `visual top overflow ${visualBounds.topOverflow}px (highest: ${visualBounds.topNode.cls}${visualBounds.topNode.text ? ` "${visualBounds.topNode.text}"` : ""})`,
        fix: "move the content group down by the measured overflow plus 16-24px",
      });
    }
    const bottomGapLimit = meta.board === "wide" ? 130 : meta.board === "square" ? 160 : 190;
    if (visualBounds.bottomGap > bottomGapLimit && visualBounds.activeRatio < 0.78) {
      warns.push({
        rule: "R8",
        msg: `bottom whitespace ${visualBounds.bottomGap}px; active content height ${Math.round(visualBounds.activeRatio * 100)}%`,
        fix: "use the measured blank space to expand the last block or move the content down slightly; avoid over-tightening after an overflow fix",
      });
    }
  }

  // R2 footer collision — only flag leaf text or media nodes, not containers
  // whose bbox merely shares y-space with an absolute-positioned strip.
  const footIssue = await s.evaluate(el => {
    const foot = el.querySelector(".foot, .issue-strip, .magazine-foot");
    if (!foot) return null;
    const cs = getComputedStyle(foot);
    if (cs.position !== "absolute") return null;
    const footTop = foot.offsetTop;
    const er = el.getBoundingClientRect();
    const hasOwnText = n => {
      for (const c of n.childNodes) {
        if (c.nodeType === 3 && c.textContent.trim().length > 0) return true;
      }
      return false;
    };
    const isMedia = n => n.tagName === "IMG" || n.tagName === "CANVAS" || n.tagName === "SVG" || n.tagName === "FIGURE";
    let worstOverlap = 0;
    let worstSel = "";
    const posterArea = el.clientWidth * el.clientHeight;
    for (const node of el.querySelectorAll("*")) {
      if (node === foot || foot.contains(node)) continue;
      if (!hasOwnText(node) && !isMedia(node)) continue;
      const r = node.getBoundingClientRect();
      // Skip full-bleed background layers (>=95% of poster area + position:absolute).
      const ncs = getComputedStyle(node);
      if (ncs.position === "absolute" && r.width * r.height >= posterArea * 0.95) continue;
      const bottom = r.bottom - er.top;
      if (bottom > footTop + 2) {
        const overlap = bottom - footTop;
        if (overlap > worstOverlap) {
          worstOverlap = overlap;
          worstSel = node.className ? "." + node.className.split(" ").filter(Boolean).join(".") : node.tagName.toLowerCase();
        }
      }
    }
    return worstOverlap > 6 ? { overlap: Math.round(worstOverlap), sel: worstSel, footTop } : null;
  });
  if (footIssue) {
    fails.push({ rule: "R2", msg: `.foot is position:absolute, ${footIssue.sel} extends ${footIssue.overlap}px past foot top`, fix: "switch .foot to flex margin-top:auto (see style-system.md Anti-pattern C)" });
  }

  // R3 swiss bold display
  if (style === "swiss") {
    const bolds = await s.evaluate((el, cls) => {
      const out = [];
      for (const c of cls) {
        for (const n of el.querySelectorAll("." + c)) {
          const cs = getComputedStyle(n);
          const w = parseInt(cs.fontWeight, 10);
          const size = parseFloat(cs.fontSize);
          if (size >= 72 && w >= 600) {
            out.push({ cls: c, weight: w, size: Math.round(size), text: n.textContent.trim().slice(0, 20) });
          }
        }
      }
      return out;
    }, DISPLAY_CLASSES);
    for (const b of bolds) {
      fails.push({ rule: "R3", msg: `.${b.cls} "${b.text}" is ${b.size}px @ weight ${b.weight} — Swiss "larger = lighter" hard rule`, fix: "remove inline font-weight; use the typed class default (200-300)" });
    }
  }

  // R4 min readable font
  const textChecks = await s.evaluate((el, MIN) => {
    const out = [];
    const seen = new Set();
    const test = (selector, role, min, requireLeaf = true) => {
      for (const n of el.querySelectorAll(selector)) {
        if (seen.has(n)) continue;
        seen.add(n);
        // Skip containers — typography roles only apply to leaf text nodes.
        // A real `.lead` is a <p>; `.role-card.lead` is a container with children.
        if (requireLeaf && n.children.length > 0) continue;
        // Skip decorative chips inside map pins — labels are sized to fit on the map by design.
        if (n.closest(".map-pin .card")) continue;
        const cs = getComputedStyle(n);
        const size = parseFloat(cs.fontSize);
        const text = n.textContent.trim();
        if (!text) continue;
        if (size > 0 && size < min) {
          out.push({ role, selector, min, size: Math.round(size), text: text.slice(0, 30) });
        }
      }
    };
    test(".body, p.body", "body", MIN.body);
    test(".lead", "lead", MIN.lead);
    test(".kicker, .cap, .caption, .swiss-img-caption, .h-sub", "caption", MIN.caption);
    test(".meta, .label, .mono", "meta", MIN.meta);
    test(".matrix-fill .cell-title, .brief-card .title, .char-grid .name", "cellTitle", MIN.cellTitle);
    test(".stat-card .lbl, .ledger .sub, .num .sub", "numAnnotation", MIN.numAnnotation);
    return out;
  }, MIN_FONT);
  for (const t of textChecks) {
    warns.push({ rule: "R4", msg: `${t.role} "${t.text}" at ${t.size}px < ${t.min}px floor`, fix: "cut copy instead of shrinking type (components.md Minimum Readable Sizes)" });
  }

  // R7 figure margin drift — catches browser-default 40px figure margins on custom media blocks.
  const figureDrift = await s.evaluate(el => {
    const out = [];
    for (const fig of el.querySelectorAll("figure")) {
      const cs = getComputedStyle(fig);
      const ml = parseFloat(cs.marginLeft) || 0;
      const mr = parseFloat(cs.marginRight) || 0;
      if (ml >= 16 || mr >= 16) {
        const text = fig.textContent.trim().replace(/\s+/g, " ").slice(0, 32);
        out.push({
          cls: fig.className ? "." + fig.className.split(" ").filter(Boolean).join(".") : "figure",
          ml: Math.round(ml),
          mr: Math.round(mr),
          text,
        });
      }
    }
    return out;
  });
  for (const f of figureDrift) {
    warns.push({ rule: "R7", msg: `${f.cls} has horizontal figure margin ${f.ml}px / ${f.mr}px${f.text ? ` near "${f.text}"` : ""}`, fix: "reset figure margins in the seed or task CSS: .poster figure { margin: 0; }" });
  }

  // R5 4-band density (3:4 only)
  if (meta.board === "xhs") {
    const bands = await s.evaluate(el => {
      const er = el.getBoundingClientRect();
      const H = el.clientHeight;
      // Pixel-row occupancy bitmap. Mark any row covered by a content element.
      const rows = new Uint8Array(H);
      const hasDirectText = n => {
        for (const c of n.childNodes) {
          if (c.nodeType === 3 && c.textContent.trim().length > 0) return true;
        }
        return false;
      };
      for (const n of el.querySelectorAll("*")) {
        const r = n.getBoundingClientRect();
        if (r.width < 8 || r.height < 8) continue;
        const tag = n.tagName;
        const cs = getComputedStyle(n);
        const isText = hasDirectText(n);
        const isImg = tag === "IMG" || tag === "CANVAS" || tag === "SVG"
                    || (cs.backgroundImage && cs.backgroundImage !== "none");
        const isRule = tag === "HR" || (parseFloat(cs.borderTopWidth) >= 1 && r.height < 4);
        const hasFill = cs.backgroundColor && !cs.backgroundColor.match(/rgba?\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0?\s*\)/) && cs.backgroundColor !== "transparent";
        if (!isText && !isImg && !isRule && !hasFill) continue;
        const top = Math.max(0, Math.floor(r.top - er.top));
        const bot = Math.min(H, Math.ceil(r.bottom - er.top));
        for (let y = top; y < bot; y++) rows[y] = 1;
      }
      const BAND = H / 4;
      const occ = [0, 0, 0, 0];
      for (let i = 0; i < 4; i++) {
        let count = 0;
        const bTop = Math.floor(i * BAND), bBot = Math.floor((i + 1) * BAND);
        for (let y = bTop; y < bBot; y++) count += rows[y];
        occ[i] = count / (bBot - bTop);
      }
      return { H, BAND, occ };
    });
    const total = bands.occ.reduce((a, b) => a + b, 0) / 4;
    const pct = (o) => Math.round(o * 100) + "%";
    if (total < 0.745) {
      warns.push({ rule: "R5", msg: `density ${pct(total)} (bands ${bands.occ.map(pct).join(" / ")})`, fix: "expand copy or switch recipe — see qa-checklist.md 4-band density" });
    }
    for (let i = 0; i < 3; i++) {
      if (bands.occ[i] < 0.15 && bands.occ[i + 1] < 0.15) {
        warns.push({ rule: "R5", msg: `bands ${i + 1}+${i + 2} both under-filled (${pct(bands.occ[i])} / ${pct(bands.occ[i + 1])}) — >25% void mid-poster`, fix: "expand body content or insert a marginalia column" });
        break;
      }
    }
  }

  // R6 h-xl hard cap
  const cap = HXL_CAPS[meta.board];
  if (cap) {
    const titles = await s.evaluate(el => {
      const out = [];
      for (const n of el.querySelectorAll(".h-xl, .h-hero, .h-display, .h-statement")) {
        const cs = getComputedStyle(n);
        const size = parseFloat(cs.fontSize);
        const lineH = parseFloat(cs.lineHeight) || size * 1.2;
        const lines = Math.round(n.getBoundingClientRect().height / lineH);
        out.push({ cls: n.className.split(" ")[0], text: n.textContent.trim(), lines, size: Math.round(size) });
      }
      return out;
    });
    for (const t of titles) {
      const longestLine = t.text.split(/\s+/).reduce((m, w) => Math.max(m, w.length), t.text.length);
      if (t.lines > cap.maxLines) {
        warns.push({ rule: "R6", msg: `.${t.cls} "${t.text}" renders ${t.lines} lines (cap ${cap.maxLines} on ${meta.board})`, fix: "switch to S01/S05 cover recipes that allow taller titles, or trim copy" });
      } else if (longestLine > cap.maxChars + 2) {
        // soft warn only — wraps naturally
      }
    }
  }

  // R9 title gap — catches headings visually touching the next content block.
  const titleGaps = await s.evaluate((el, board) => {
    const er = el.getBoundingClientRect();
    const TRANSPARENT = /rgba?\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0?\s*\)|transparent/;
    const hasDirectText = n => {
      for (const c of n.childNodes) {
        if (c.nodeType === 3 && c.textContent.trim().length > 0) return true;
      }
      return false;
    };
    const colorVisible = c => c && !TRANSPARENT.test(c);
    const isMeaningful = n => {
      const tag = n.tagName;
      const cs = getComputedStyle(n);
      const r = n.getBoundingClientRect();
      if (r.width < 6 || r.height < 6) return false;
      if (n === el || n.classList.contains("content")) return false;
      if (hasDirectText(n)) return true;
      if (tag === "IMG" || tag === "CANVAS" || tag === "SVG" || tag === "HR") return true;
      if (colorVisible(cs.backgroundColor) && r.width * r.height >= 1600 && !["MAIN", "SECTION"].includes(tag)) return true;
      const border = parseFloat(cs.borderTopWidth) + parseFloat(cs.borderBottomWidth) +
        parseFloat(cs.borderLeftWidth) + parseFloat(cs.borderRightWidth);
      return border >= 1 && r.width * r.height >= 1600;
    };
    const label = n => {
      const cls = n.className ? "." + String(n.className).split(" ").filter(Boolean).join(".") : n.tagName.toLowerCase();
      const text = n.textContent.trim().replace(/\s+/g, " ").slice(0, 30);
      return text ? `${cls} "${text}"` : cls;
    };
    const nodes = Array.from(el.querySelectorAll("*")).filter(isMeaningful);
    const titles = Array.from(el.querySelectorAll(".h-xl, .h-hero, .h-display, .h-statement, .h-md, .row-title, .step-title"));
    const out = [];
    for (const title of titles) {
      if (!title.textContent.trim()) continue;
      const tr = title.getBoundingClientRect();
      const isLocal = title.matches(".h-md, .row-title, .step-title");
      const minGap = isLocal ? 16 : board === "wide" ? 24 : 28;
      let nearest = null;
      let nearestGap = Infinity;
      for (const node of nodes) {
        if (node === title || title.contains(node) || node.contains(title)) continue;
        const nr = node.getBoundingClientRect();
        const gap = nr.top - tr.bottom;
        if (gap < -2) continue;
        const overlap = Math.max(0, Math.min(tr.right, nr.right) - Math.max(tr.left, nr.left));
        const overlapRatio = overlap / Math.min(tr.width, nr.width);
        if (overlapRatio < 0.12 && gap < 96) continue;
        if (gap < nearestGap) {
          nearestGap = gap;
          nearest = node;
        }
      }
      if (nearest && nearestGap < minGap) {
        out.push({
          title: label(title),
          next: label(nearest),
          gap: Math.round(nearestGap),
          minGap,
        });
      }
    }
    return out;
  }, meta.board);
  for (const g of titleGaps) {
    warns.push({
      rule: "R9",
      msg: `${g.title} has ${g.gap}px gap before ${g.next} (min ${g.minGap}px)`,
      fix: "add/restore measured spacing under the title before reducing copy or resizing the whole layout",
    });
  }

  // ============================================================
  // R10–R15 · 5(+1) 维反 AI slop 自检 (huashu-design 集成)
  // 源:huashu-design/references/critique-guide.md §0-5
  // ============================================================
  const slopChecks = await s.evaluate((el, board) => {
    const out = { R10: null, R11: null, R12: null, R13: null, R14: null, R15: null };
    const nodes = Array.from(el.querySelectorAll("*"));
    const allCS = nodes.map(n => getComputedStyle(n));

    // R10 概念 (Editorial ≥ 5% / 其它 ≥ 25%) — 实际可见文本占画布高度,过低=空洞
    const H = el.clientHeight, W = el.clientWidth;
    let visualRows = new Uint8Array(H);
    let hasDirectText = n => {
      for (const c of n.childNodes) if (c.nodeType === 3 && c.textContent.trim().length > 0) return true;
      return false;
    };
    let top = Infinity, bot = -Infinity;
    for (const n of nodes) {
      const r = n.getBoundingClientRect();
      if (r.width < 6 || r.height < 6) continue;
      const tag = n.tagName;
      const cs = getComputedStyle(n);
      const er = el.getBoundingClientRect();
      const top0 = Math.max(0, Math.floor(r.top - er.top));
      const bot0 = Math.min(H, Math.ceil(r.bottom - er.top));
      for (let y = top0; y < bot0; y++) visualRows[y] = 1;
      if (hasDirectText(n)) {
        top = Math.min(top, r.top - er.top);
        bot = Math.max(bot, r.bottom - er.top);
      }
    }
    const activeRatio = visualRows.reduce((a, b) => a + b, 0) / H;
    const minActive = board === "wide" ? 0.30 : 0.40;
    if (activeRatio < minActive) {
      out.R10 = { activeRatio: Math.round(activeRatio * 100) + "%", min: Math.round(minActive * 100) + "%" };
    }

    // R11 调色板 (Editorial=Kraft/Indigo/Forest/Monocle/Dune/Midnight — pure neutrals;Swiss=B/W + accent)
    // 简单检测:背景色应落在主题调色板附近
    const bgColors = allCS.map(c => c.backgroundColor).filter(c => c && !c.match(/rgba?\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0?\s*\)/) && c !== "transparent");
    const isKraftLike = (rgb) => {
      const m = rgb.match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/);
      if (!m) return false;
      const [r, g, b] = [+m[1], +m[2], +m[3]].map(v => v < 40 ? 0 : v > 215 ? 255 : v);
      // 暖棕 #2a1e13 派生 / 米白 #eedfc7 派生
      if (r > 200 && g > 200 && b > 150 && b < 220) return true; // paper 系列
      if (r < 80 && g < 60 && b < 40) return true;                // ink 系列
      return false;
    };
    const paletteClash = bgColors.filter(c => !isKraftLike(c));
    if (paletteClash.length > bgColors.length * 0.3 && bgColors.length > 5) {
      out.R11 = { clashCount: paletteClash.length, total: bgColors.length };
    }

    // R12 8px baseline grid — padding/margin/gap 应是 8 倍数(允许 4 半数差,soft warn)
    const offGrid = [];
    for (const n of nodes) {
      if (n.tagName !== "DIV" && n.tagName !== "P" && n.tagName !== "SECTION" && n.tagName !== "H1" && n.tagName !== "H2") continue;
      if (n === el) continue;
      const cs = getComputedStyle(n);
      const r = n.getBoundingClientRect();
      if (r.width < 24 || r.height < 24) continue;
      const checks = [
        parseFloat(cs.paddingTop), parseFloat(cs.paddingBottom),
        parseFloat(cs.marginTop), parseFloat(cs.marginBottom),
      ];
      for (const v of checks) {
        if (v > 1 && v < 200 && Math.abs(v % 8) > 2 && Math.abs(v % 8) < 6) {
          offGrid.push({ tag: n.tagName, cls: n.className.split(" ").filter(Boolean)[0] || "", v: Math.round(v) });
          break;
        }
      }
    }
    if (offGrid.length > 6) {
      out.R12 = { offGridCount: offGrid.length, sample: offGrid.slice(0, 3) };
    }

    // R13 border-radius 滥用 — Editorial/Swiss 都禁用,任何 border-radius > 0 都记
    const radiusAbusers = [];
    for (const n of nodes) {
      const cs = getComputedStyle(n);
      const tl = parseFloat(cs.borderTopLeftRadius) || 0;
      const tr = parseFloat(cs.borderTopRightRadius) || 0;
      const bl = parseFloat(cs.borderBottomLeftRadius) || 0;
      const br = parseFloat(cs.borderBottomRightRadius) || 0;
      if (tl > 0 || tr > 0 || bl > 0 || br > 0) {
        const txt = n.textContent.trim().slice(0, 20);
        if (txt) radiusAbusers.push({ cls: n.className.split(" ").filter(Boolean)[0] || n.tagName, r: Math.max(tl, tr, bl, br), txt });
      }
    }
    if (radiusAbusers.length > 0) {
      out.R13 = { count: radiusAbusers.length, sample: radiusAbusers.slice(0, 3) };
    }

    // R14 contrast ≥ 4.5 — 简化检测:前景色 vs 背景色明亮度差异
    const getLuminance = c => {
      const m = c.match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/);
      if (!m) return null;
      const [r, g, b] = [+m[1], +m[2], +m[3]].map(v => {
        v /= 255;
        return v < 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };
    // 递归向上找最近非透明背景
    const findBgColor = (n) => {
      let cur = n;
      while (cur) {
        const cs = getComputedStyle(cur);
        const bg = cs.backgroundColor;
        if (bg && bg !== "transparent" && !bg.match(/rgba?\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0?\s*\)/)) {
          return getLuminance(bg);
        }
        cur = cur.parentElement;
      }
      // 兜底:页面 body bg 或 transparent → 用 1.0(白)
      return 1.0;
    };
    const lowContrast = [];
    for (const n of nodes) {
      if (!hasDirectText(n)) continue;
      const cs = getComputedStyle(n);
      const fg = cs.color;
      const fgL = getLuminance(fg);
      const bgL = findBgColor(n);
      if (fgL === null || bgL === null) continue;
      const ratio = (Math.max(fgL, bgL) + 0.05) / (Math.min(fgL, bgL) + 0.05);
      const fontSize = parseFloat(cs.fontSize);
      // 大字体 (≥24px) 阈值放宽到 3.0(WCAG AA large text)
      const threshold = fontSize >= 24 ? 3.0 : 4.5;
      // 装饰性小元素(span/em) skip
      if (["SPAN", "EM", "STRONG", "I"].includes(n.tagName) && n.textContent.trim().length < 4) continue;
      if (ratio < threshold) {
        const txt = n.textContent.trim().slice(0, 20);
        if (txt) lowContrast.push({ cls: n.className.split(" ").filter(Boolean)[0] || n.tagName, ratio: ratio.toFixed(2), size: fontSize, txt });
      }
    }
    if (lowContrast.length > 0 && lowContrast.length > nodes.length * 0.4) {
      out.R14 = { count: lowContrast.length, sample: lowContrast.slice(0, 3) };
    }

    // R15 创新性 (反 AI slop)
    const slops = [];
    // emoji 装饰 / 玻璃拟态 / 渐变滥用 / neon
    for (const n of nodes) {
      const cs = getComputedStyle(n);
      const t = n.textContent;
      // 1) emoji
      const emojiRe = /[\u{1F300}-\u{1F9FF}\u{1FA00}-\u{1FAFF}]/u;
      if (emojiRe.test(t) && n.children.length > 0) {
        slops.push({ type: "emoji-decoration", cls: n.className.split(" ").filter(Boolean)[0] || n.tagName, txt: t.slice(0, 20) });
      }
      // 2) backdrop-filter (玻璃拟态)
      if (cs.backdropFilter && cs.backdropFilter !== "none" && cs.backdropFilter !== "") {
        slops.push({ type: "backdrop-filter/glassmorphism", cls: n.className.split(" ").filter(Boolean)[0] || n.tagName });
      }
      // 3) 高饱和 neon text-shadow
      const ts = cs.textShadow;
      if (ts && ts !== "none" && ts !== "" && (ts.includes("rgb") || ts.includes("#"))) {
        // 提取任何 text-shadow 颜色,如果饱和度 > 50% 且亮度 > 50% 可能是 neon
        const m = ts.match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/);
        if (m) {
          const [r, g, b] = [+m[1], +m[2], +m[3]];
          const max = Math.max(r, g, b), min = Math.min(r, g, b);
          if (max - min > 180 && max > 180) {
            slops.push({ type: "neon-text-shadow", cls: n.className.split(" ").filter(Boolean)[0] || n.tagName, color: `rgb(${r},${g},${b})` });
          }
        }
      }
    }
    if (slops.length > 0) {
      out.R15 = { count: slops.length, sample: slops.slice(0, 3) };
    }

    return out;
  }, meta.board);

  // 把 R10-R15 注入到 fails/warns
  // R10(R 概念): FAIL 级 — 严重过低
  if (slopChecks.R10) {
    fails.push({
      rule: "R10",
      msg: `active visual content ${slopChecks.R10.activeRatio} < ${slopChecks.R10.min} min — poster too thin (概念 ≤5)`,
      fix: "expand content blocks (mother formula + body + steps); avoid over-large hero display; consider lowering .h-display size by 8-16px",
    });
  }
  // R11(调色板): WARN
  if (slopChecks.R11) {
    warns.push({
      rule: "R11",
      msg: `${slopChecks.R11.clashCount}/${slopChecks.R11.total} background colors fall outside the ${style === "editorial" ? "ink-paper Kraft" : "B/W + accent"} palette`,
      fix: "consolidate background colors to the chosen theme palette (editorial: ink-paper only; swiss: ink + paper + 1 accent)",
    });
  }
  // R12(8px baseline): WARN
  if (slopChecks.R12) {
    warns.push({
      rule: "R12",
      msg: `${slopChecks.R12.offGridCount} elements have non-8px-multiple padding/margin (off baseline grid)`,
      fix: `round padding/margin to multiples of 8 (e.g. 16/24/32px); affected: ${slopChecks.R12.sample.map(s => s.cls + "=" + s.v + "px").join(", ")}`,
    });
  }
  // R13(border-radius): FAIL 级 — Editorial/Swiss 严禁
  if (slopChecks.R13) {
    fails.push({
      rule: "R13",
      msg: `${slopChecks.R13.count} elements have border-radius > 0px (Editorial/Swiss hard rule)`,
      fix: `reset border-radius to 0 in CSS: .poster * { border-radius: 0 !important; }`,
    });
  }
  // R14(contrast ≥4.5): FAIL
  if (slopChecks.R14) {
    fails.push({
      rule: "R14",
      msg: `${slopChecks.R14.count} text nodes have contrast < 4.5:1 (WCAG AA fail)`,
      fix: `darken text or lighten background to reach ≥4.5:1 contrast`,
    });
  }
  // R15(反 AI slop): FAIL
  if (slopChecks.R15) {
    const slopTypes = [...new Set(slopChecks.R15.sample.map(s => s.type))];
    fails.push({
      rule: "R15",
      msg: `${slopChecks.R15.count} AI-slop indicators detected: ${slopTypes.join(", ")}`,
      fix: `remove emoji decoration / backdrop-filter / neon text-shadow; use the documented 5D anti-slop discipline`,
    });
  }

  report.push({ meta, fails, warns });
}

await browser.close();

let totalFail = 0, totalWarn = 0;
const ruleCounts = new Map();
for (const { fails, warns } of report) {
  totalFail += fails.length;
  totalWarn += warns.length;
  for (const v of [...fails, ...warns]) ruleCounts.set(v.rule, (ruleCounts.get(v.rule) || 0) + 1);
}
const cleanCount = report.filter(r => r.fails.length === 0 && r.warns.length === 0).length;

const lines = [];
lines.push(`==== validate-social-deck ====`);
lines.push(`target:   ${path.relative(process.cwd(), htmlPath)}`);
lines.push(`style:    ${style}`);
lines.push(`sections: ${report.length}  ·  ${cleanCount} clean  ·  ${totalFail} fails  ·  ${totalWarn} warns`);
if (ruleCounts.size > 0) {
  const ruleSummary = [...ruleCounts.entries()].sort().map(([r, c]) => `${r}=${c}`).join("  ");
  lines.push(`rules:    ${ruleSummary}`);
}
lines.push("");

const fixCache = new Map();
for (const { meta, fails, warns } of report) {
  if (fails.length === 0 && warns.length === 0) {
    lines.push(`[PASS]  ${meta.id} ${meta.dataId ? ` · ${meta.dataId}` : ""} · ${meta.board}`);
    continue;
  }
  const tag = fails.length ? "[FAIL]" : "[WARN]";
  lines.push(`${tag}  ${meta.id} ${meta.dataId ? ` · ${meta.dataId}` : ""} · ${meta.board}`);
  for (const v of [...fails, ...warns]) {
    const sev = fails.includes(v) ? "FAIL" : "WARN";
    lines.push(`  ${sev} · ${v.rule}  ${v.msg}`);
    if (!fixCache.has(v.rule)) {
      lines.push(`         fix: ${v.fix}`);
      fixCache.set(v.rule, true);
    }
  }
}

lines.push("");
lines.push(`Legend: R1 overflow · R2 footer collision · R3 swiss bold display · R4 min font · R5 4-band density · R6 h-xl cap · R7 figure margin drift · R8 visual bounds · R9 title gap · R10 概念(active visual) · R11 调色板(palette discipline) · R12 8px baseline(grid discipline) · R13 细节(border-radius=0) · R14 contrast ≥4.5 · R15 反 AI cliché(emoji/glassmorphism/neon)`);
lines.push(`Exit code 1 only on FAIL. Warnings are advisory.`);

console.log(lines.join("\n"));
process.exit(totalFail > 0 ? 1 : 0);
