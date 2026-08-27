// to-html.mjs · pages.jsonl + theme → index.html（替换 <!-- POSTERS_HERE -->）
// 阶段 19 V2.0
//
// 输入：seed 模板（template-editorial-card.html / template-swiss-card.html）
// 输出：local-tests/<slug>/index.html（已注入 data-theme/data-accent + 多 section）

import fs from "node:fs";
import path from "node:path";
import { themeAttr, seedTemplatePath } from "./palette-rules.mjs";

/**
 * 根据 page 对象生成对应的 <section class="poster ..."> HTML 块
 * @param {object} page - pages.jsonl 中的单页
 * @param {{ theme: string, family: 'editorial'|'swiss' }} choice
 * @returns {string} HTML section 字符串
 */
export function pageToSection(page, choice) {
  const id = page.role || `page-${page.page}`;
  // 大多数 page 走 xhs 板（小红书 3:4）。wechat-cover-pair 走 wide + square。
  if (page.role === "wechat-cover-pair") {
    return renderWechatPair(page, choice);
  }
  return renderXhs(page, choice, id);
}

function renderXhs(page, choice, id) {
  const recipe = page.recipe || (choice.family === "swiss" ? "S01" : "M01");

  // Editorial 模板：<canvas class="mag-bg"> + .grain + .content.stack.gap-4
  if (choice.family === "editorial") {
    return `
    <section class="poster xhs" id="xhs-${page.page}" data-recipe="${recipe}" data-role="${page.role}">
      <canvas class="mag-bg" data-bg="ink-flow"></canvas>
      <div class="grain"></div>
      <div class="content stack gap-4">
        ${page.kicker ? `<p class="kicker">${escapeHtml(page.kicker)}</p>` : ""}
        ${page.title ? `<h1 class="h-display">${escapeHtml(page.title)}</h1>` : ""}
        ${page.subtitle ? `<p class="h-sub">${escapeHtml(page.subtitle)}</p>` : ""}
        ${page.lead ? `<p class="lead">${escapeHtml(page.lead)}</p>` : ""}
        ${renderPageBody(page)}
      </div>
      <div class="issue-strip">
        <span>Page ${page.page}</span>
        <span>—</span>
        <span>${escapeHtml(page.kicker || "")}</span>
      </div>
    </section>`;
  }

  // Swiss 模板：.chrome-min + .t-cat + .h-statement + .lead + .t-meta
  return `
    <section class="poster xhs" id="xhs-${page.page}" data-recipe="${recipe}" data-role="${page.role}">
      <div class="content stack gap-9">
        <div class="chrome-min">
          <span>${escapeHtml(page.kicker || "Vol. 01")}</span>
          <span>${escapeHtml(page.meta?.date || "2026.07")}</span>
        </div>
        <div class="stack gap-7">
          ${page.kicker ? `<p class="t-cat">${escapeHtml(page.kicker)}</p>` : ""}
          ${page.title ? `<h1 class="h-statement">${escapeHtml(page.title)}</h1>` : ""}
        </div>
        <div class="grow"></div>
        ${page.lead ? `<p class="lead">${escapeHtml(page.lead)}</p>` : ""}
        <div class="row gap-6">
          <p class="t-meta">${escapeHtml(page.meta?.issue || "Issue 01")}</p>
          <p class="t-meta">/ Page ${page.page} / ${page.recipe || "S01"}</p>
        </div>
      </div>
    </section>`;
}

function renderWechatPair(page, choice) {
  const longTitle = page.title || "本期 · 老李兄弟";
  const shortTitle = (page.title || "本期").slice(0, 8);
  const italicSub = page.subtitle || `Letters · ${page.meta?.date || "2026.07"}`;
  const issueStrip = `${page.kicker || ""}`;

  if (choice.family === "editorial") {
    return `
    <section class="poster wide" id="wechat-21x9" data-role="wechat-wide">
      <canvas class="mag-bg" data-bg="ink-flow"></canvas>
      <div class="grain"></div>
      <div class="paper-wash"></div>
      <div class="content stack gap-3">
        <div class="issue-row">
          <span>${escapeHtml(page.meta?.date?.split('-')[1] || "07")}</span><span class="dot"></span><span>${escapeHtml(page.meta?.date?.split('-')[0] || "2026")}</span><span class="dot"></span><span>${escapeHtml(page.kicker || "本期")}</span>
        </div>
        <div class="stack gap-2">
          <p class="kicker">${escapeHtml(page.kicker || "")}</p>
          <h1 class="h-display">${escapeHtml(longTitle)}</h1>
          <p class="h-sub">${escapeHtml(italicSub)}</p>
        </div>
      </div>
      <div class="issue-strip">
        <span>${escapeHtml(issueStrip)}</span>
        <span>—</span>
        <span>${escapeHtml(shortTitle)}</span>
      </div>
    </section>

    <section class="poster square" id="wechat-1x1" data-role="wechat-square">
      <canvas class="mag-bg" data-bg="ink-flow"></canvas>
      <div class="grain"></div>
      <div class="paper-wash"></div>
      <div class="content center" style="justify-content:center; align-items:center; text-align:center">
        <div class="stack gap-2">
          <p class="kicker">${escapeHtml(page.kicker || "")}</p>
          <h1 class="h-display">${escapeHtml(shortTitle)}</h1>
        </div>
      </div>
      <div class="issue-strip">
        <span>${escapeHtml(issueStrip)}</span>
        <span>—</span>
        <span>${escapeHtml(shortTitle)}</span>
      </div>
    </section>

    <section class="pair-preview" id="pair-preview">
      <div class="preview-wide">
        <canvas class="mag-bg" data-bg="ink-flow"></canvas>
        <div class="grain"></div>
        <div class="paper-wash"></div>
        <div class="content stack gap-3">
          <h2 class="h-display">${escapeHtml(longTitle)}</h2>
        </div>
      </div>
      <div class="preview-square">
        <canvas class="mag-bg" data-bg="ink-flow"></canvas>
        <div class="grain"></div>
        <div class="paper-wash"></div>
        <div class="content center" style="justify-content:center; align-items:center; text-align:center">
          <h2 class="h-display">${escapeHtml(shortTitle)}</h2>
        </div>
      </div>
    </section>`;
  }

  // Swiss 公众号封面（21:9 + 1:1）：直接复用 S01 Accent Cover 骨架
  return `
    <section class="poster wide" id="wechat-21x9" data-role="wechat-wide">
      <div class="content stack gap-9">
        <div class="chrome-min">
          <span>${escapeHtml(page.kicker || "Vol. 01")}</span>
          <span>${escapeHtml(page.meta?.date || "2026.07")}</span>
        </div>
        <div class="stack gap-7">
          <p class="t-cat">${escapeHtml(italicSub)}</p>
          <h1 class="h-statement">${escapeHtml(longTitle)}</h1>
        </div>
        <div class="grow"></div>
        <hr class="hr-accent">
        <p class="lead">${escapeHtml(page.lead || "")}</p>
        <div class="row gap-6">
          <p class="t-meta">${escapeHtml(page.meta?.issue || "Issue 01")}</p>
          <p class="t-meta">/ 21:9</p>
        </div>
      </div>
    </section>

    <section class="poster square" id="wechat-1x1" data-role="wechat-square">
      <div class="content stack gap-9" style="justify-content:center; align-items:center; text-align:center">
        <div class="stack gap-7">
          <p class="t-cat">${escapeHtml(page.kicker || "")}</p>
          <h1 class="h-statement">${escapeHtml(shortTitle)}</h1>
        </div>
        <hr class="hr-accent">
      </div>
    </section>

    <section class="pair-preview" id="pair-preview">
      <div class="preview-wide"><div class="content"><h2 class="h-statement">${escapeHtml(longTitle)}</h2></div></div>
      <div class="preview-square"><div class="content" style="justify-content:center; align-items:center"><h2 class="h-statement">${escapeHtml(shortTitle)}</h2></div></div>
    </section>`;
}

/**
 * 渲染 page.body / page.ledger / page.pipeline / page.trap 子结构
 */
function renderPageBody(page) {
  if (page.body) {
    const lines = page.body.split("\n").filter(Boolean).map(l => `<p class="body">${escapeHtml(l)}</p>`).join("");
    return `<div class="stack gap-2">${lines}</div>`;
  }
  if (page.ledger && page.ledger.length > 0) {
    return `
    <div class="stack gap-3">
      ${page.ledger.map(item => `
        <div class="row gap-4" style="border-bottom: 1px solid var(--line); padding-bottom: 8px">
          <span class="meta">${escapeHtml(item.n)}</span>
          <div>
            <p class="t-md"><strong>${escapeHtml(item.title)}</strong></p>
            <p class="body">${escapeHtml(item.desc)}</p>
          </div>
        </div>`).join("")}
    </div>`;
  }
  if (page.pipeline && page.pipeline.length > 0) {
    return `
    <div class="pipeline-v">
      ${page.pipeline.map(step => `
        <div class="step">
          <div class="step-nb">${escapeHtml(step.nb)}</div>
          <div>
            <h3 class="step-title">${escapeHtml(step.title)}</h3>
            <p class="step-desc">${escapeHtml(step.desc)}</p>
          </div>
        </div>`).join("")}
    </div>`;
  }
  if (page.trap && page.trap.length > 0) {
    return `
    <div class="stack gap-3">
      ${page.trap.map(item => `
        <div class="row gap-4" style="border-bottom: 1px solid var(--line); padding-bottom: 8px">
          <span class="meta">${escapeHtml(item.nb)}</span>
          <div>
            <p class="t-md"><strong>${escapeHtml(item.title)}</strong></p>
            <p class="body">${escapeHtml(item.desc)}</p>
          </div>
        </div>`).join("")}
    </div>`;
  }
  return "";
}

function escapeHtml(s) {
  if (typeof s !== "string") return "";
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

/**
 * 主入口：从 seed 模板 + pages + theme 拼出 index.html
 * @param {object} opts
 * @param {string[]} opts.pages - pages 数组
 * @param {{ theme: string, family: 'editorial'|'swiss' }} opts.choice
 * @param {string} opts.skillRoot - guizang skill 根路径
 * @param {string} opts.outDir - 输出目录
 * @returns {string} 写入的 index.html 路径
 */
export function toHtml({ pages, choice, skillRoot, outDir }) {
  const seedPath = seedTemplatePath(choice, skillRoot);
  let seed = fs.readFileSync(seedPath, "utf-8");

  // 注入 data-theme 或 data-accent
  const attr = themeAttr(choice);
  seed = seed.replace(/<html\s+lang="zh-CN"\s+data-(theme|accent)="[^"]*"/, `<html lang="zh-CN" ${attr}`);

  // 注入 AGPL-3.0 版权声明到 head（在 </head> 前）
  const agplFooter = `
  <!-- AGPL-3.0 版权声明 · 阶段 19 自动注入 -->
  <meta name="generator" content="guizang V1.0 · stage 19 blogger-poster pipeline (AGPL-3.0)">
  <meta name="guizang-source" content="https://github.com/op7418/guizang-social-card-skill">
  <meta name="agpl-license" content="https://www.gnu.org/licenses/agpl-3.0.html">
  `;
  seed = seed.replace("</head>", `${agplFooter}</head>`);

  // 替换 POSTERS_HERE
  const sections = pages.map(p => pageToSection(p, choice)).join("\n");
  if (!seed.includes("<!-- POSTERS_HERE -->")) {
    throw new Error("seed 模板里找不到 <!-- POSTERS_HERE --> 标记");
  }
  // POSTERS_HERE 标记可能出现在 <style> 块的注释里（不能替换）
  // 只替换真正在 <main> 块内的标记：定位 "    <!-- POSTERS_HERE -->" 后跟缩进
  const replacementRegex = /(    <!-- POSTERS_HERE -->)[\s\S]*?(  <\/main>)/;
  if (!replacementRegex.test(seed)) {
    throw new Error("seed 模板里找不到 main 块内的 POSTERS_HERE 标记");
  }
  seed = seed.replace(replacementRegex, `    <!-- POSTERS_HERE -->\n${sections}\n  </main>`);

  // 写入
  fs.mkdirSync(outDir, { recursive: true });
  const outPath = path.join(outDir, "index.html");
  fs.writeFileSync(outPath, seed, "utf-8");
  return outPath;
}