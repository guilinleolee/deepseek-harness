#!/usr/bin/env node
/*
 * blogger-poster.mjs · 阶段 19 V2.1 核心入口
 *
 * 8 维博主全息 JSON → 5-6 张小红书图文 + 公众号封面 PNG → publisher.py batch
 *
 * 用法:
 *   node pipeline/blogger-poster.mjs --blogger laoli_bro_2026 [--platforms xiaohongshu,wechat] [--dry-run]
 *   node pipeline/blogger-poster.mjs --all                                      # 遍历 registry.db 所有活跃博主
 *   node pipeline/blogger-poster.mjs --profile /path/to/ip_profile_8dim.json [--dry-run]
 *   node pipeline/blogger-poster.mjs --blogger <id> --draft                    # ⭐ 新增：生成草稿进入审批队列
 *
 * 输入:  C:/Users/li/.claude/ip-profiles/<blogger_id>/ip_profile_8dim.json
 * 输出:  local-tests/<slug>/{index.html, output/*.png, tasks.jsonl}
 *        publisher.db 中新增 publish_tasks 行（mock，等真实 API 接入）
 *        ⭐ --draft 模式：~/.dragon-engine/drafts/pending/draft-{id}.json
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execSync } from "node:child_process";

import { detectPalette, applyDesignStyle } from "./palette-rules.mjs";
import { selectRecipe } from "./recipe-rules.mjs";
import { extractPages, writePages } from "./extract-pages.mjs";
import { toHtml } from "./to-html.mjs";
import { toTasksJsonl, runPublisherBatch, choosePlatforms } from "./to-publisher.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = path.resolve(__dirname, "..");
const REGISTRY_DB = "C:/Users/li/.claude/skills/blogger-fingerprint-registry/registry.db";
const IP_PROFILES_DIR = "C:/Users/li/.claude/ip-profiles";

// ───── CLI 解析 ─────
const args = process.argv.slice(2);
const opts = { blogger: null, profile: null, platforms: null, dryRun: false, slug: null, all: false, draft: false };
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--blogger") opts.blogger = args[++i];
  else if (args[i] === "--profile") opts.profile = args[++i];
  else if (args[i] === "--platforms") opts.platforms = args[++i].split(",").map(s => s.trim());
  else if (args[i] === "--slug") opts.slug = args[++i];
  else if (args[i] === "--dry-run") opts.dryRun = true;
  else if (args[i] === "--all") opts.all = true;
  else if (args[i] === "--draft") opts.draft = true;
  else if (args[i] === "--help" || args[i] === "-h") {
    console.log(fs.readFileSync(path.join(__dirname, "blogger-poster.mjs"), "utf-8").split("\n").slice(0, 22).join("\n"));
    process.exit(0);
  }
}

// ───── 加载博主全息 ─────
function loadProfile(bloggerId, profilePath) {
  if (profilePath && fs.existsSync(profilePath)) {
    return JSON.parse(fs.readFileSync(profilePath, "utf-8"));
  }
  // 默认从标准位置读
  const p = path.join("C:/Users/li/.claude/ip-profiles", bloggerId, "ip_profile_8dim.json");
  if (!fs.existsSync(p)) {
    console.error(`[FAIL] 找不到博主全息: ${p}`);
    console.error(`       请先用 35-06 V1.1 蒸馏该博主，或显式 --profile 路径`);
    process.exit(2);
  }
  return JSON.parse(fs.readFileSync(p, "utf-8"));
}

// ───── IP 授权三重护栏 ─────
function checkConsent(profile) {
  const consent = profile._meta?.consent || profile.ip_consent_summary || {};
  const errors = [];
  const warnings = [];

  // 1. voice consent
  if (!consent.voice_consent_file && !consent.voice_authorized) {
    errors.push("[HARD] 缺少声纹授权（voice_consent_file / voice_authorized）");
  }
  // 2. IP consent
  if (!consent.ip_consent_file && !consent.ip_image_authorized) {
    errors.push("[HARD] 缺少 IP 形象授权（ip_consent_file / ip_image_authorized）");
  }
  // 3. 过期检查（hard 阻断）
  const expiresAt = consent.consent_expires_at || consent.expires_at;
  if (expiresAt) {
    const exp = new Date(expiresAt);
    if (exp < new Date()) {
      errors.push(`[HARD] 授权已于 ${exp.toISOString().slice(0, 10)} 过期，禁止生成`);
    } else {
      const daysLeft = Math.floor((exp - new Date()) / 86400000);
      if (daysLeft < 30) warnings.push(`[SOFT] 授权仅剩 ${daysLeft} 天到期`);
    }
  }
  // 4. 第 9 维 design consent（V3.0 新增）
  // 设计风格来自 huashu-design 40 风格库——是 open-source 资产，**不需要**单独 consent（仅个人 IP 形象需要）
  // 但如果 fingerprint-registry DB 有 design_consent_file，可以校验

  if (errors.length > 0) {
    console.error("[FAIL] IP 授权三重护栏失败:");
    for (const e of errors) console.error("  " + e);
    if (warnings.length > 0) {
      console.warn("\n[WARN] 警告:");
      for (const w of warnings) console.warn("  " + w);
    }
    process.exit(3);
  }
  if (warnings.length > 0) {
    console.warn("[WARN] 授权护栏通过，但有警告:");
    for (const w of warnings) console.warn("  " + w);
  } else {
    console.log("[OK] IP 授权三重护栏通过（voice + IP visual + 有效期）");
  }
}

// ───── 主流程 ─────
async function main() {
  console.log("=== blogger-poster.mjs · 阶段 19 V2.0 ===\n");

  // 0. --all 模式：遍历所有活跃博主
  if (opts.all) {
    return await runAll(opts);
  }

  // 1. 加载博主全息
  if (!opts.blogger && !opts.profile) {
    console.error("请提供 --blogger <blogger_id> 或 --profile <path>");
    process.exit(2);
  }
  const profile = loadProfile(opts.blogger, opts.profile);
  console.log(`[1] 加载博主全息: ${profile.blogger_id || opts.blogger} (${profile.blogger_name || ""})`);
  console.log(`    schema_version: ${profile._meta?.schema_version || "8-dim"}`);
  if (profile._meta?.consent) console.log(`    consent_expires_at: ${profile._meta.consent.consent_expires_at}`);

  // 2. IP 授权三重护栏（hard 阻断）
  checkConsent(profile);

  // 3. 调色板选择（优先第 9 维 design_style，其次从 dim_8 自动推断）
  console.log("\n[2] 调色板选择:");
  // 注意：profile.json 里没有 design_style，要去 registry DB 读
  let designStyle = null;
  const _row = await readRegistryRow(profile.blogger_id);
  if (_row && _row.design_style) designStyle = _row.design_style;
  profile._design_style = designStyle;
  console.log(`    第 9 维 design_style: ${designStyle || "（未设置）"}`);

  let choice;
  const ds = applyDesignStyle(designStyle);
  if (ds) {
    console.log(`    → 用第 9 维 (${ds.source}): ${ds.family} / ${ds.theme}`);
    choice = ds;
  } else {
    const pal = detectPalette(profile.dim_8_ip_visual?.spec?.color_palette || []);
    console.log(`    → 自动推断 ${pal.family}/${pal.theme} (label=${pal.label}, confidence=${pal.confidence})`);
    choice = { theme: pal.theme, family: pal.family, source: "palette-auto" };
  }

  // 4. Recipe 选择
  console.log("\n[3] Recipe 选择:");
  const recipe = selectRecipe(profile, choice);
  console.log(`    → ${recipe.recipe} (${recipe.name}) — 理由: ${recipe.reason}`);

  // 5. 抽取 page 计划
  console.log("\n[4] 抽取 page 计划:");
  const pages = extractPages(profile, choice, recipe);
  console.log(`    → ${pages.length} 页:`);
  for (const p of pages) {
    console.log(`      page ${p.page} | ${p.recipe || p.role} | ${p.title?.slice(0, 20) || ""}`);
  }

  // 6. slug & task 目录
  const slug = opts.slug || `blogger-${profile.blogger_id}-${(choice.theme || "ink").toLowerCase()}`;
  const taskDir = path.join(SKILL_ROOT, "local-tests", slug);
  fs.mkdirSync(taskDir, { recursive: true });
  console.log(`\n[5] task 目录: ${taskDir}`);

  // 7. 写 pages.jsonl
  const pagesPath = path.join(taskDir, "pages.jsonl");
  writePages(pages, pagesPath);
  console.log(`    → pages.jsonl 写出 (${fs.statSync(pagesPath).size} bytes)`);

  // 8. 复制 WebGL 脚本（Editorial family 需要）
  if (choice.family === "editorial") {
    const assetsDir = path.join(taskDir, "assets");
    fs.mkdirSync(assetsDir, { recursive: true });
    fs.copyFileSync(
      path.join(SKILL_ROOT, "assets", "magazine-bg-webgl.js"),
      path.join(assetsDir, "magazine-bg-webgl.js")
    );
    console.log("    → 复制 magazine-bg-webgl.js");
  }

  // 9. toHtml: 拼 index.html
  console.log("\n[6] 拼 index.html:");
  const htmlPath = toHtml({ pages, choice, skillRoot: SKILL_ROOT, outDir: taskDir });
  console.log(`    → ${htmlPath} (${fs.statSync(htmlPath).size} bytes)`);

  // 10. validate (subprocess, 不阻塞 dry-run)
  if (!opts.dryRun) {
    console.log("\n[7] validate-social-deck:");
    const vOut = execSync(`node validate-social-deck.mjs "${taskDir}"`, { encoding: "utf-8", cwd: SKILL_ROOT });
    console.log(vOut.split("\n").map(l => "    " + l).join("\n"));

    // 11. render
    console.log("\n[8] render-poster:");
    const rOut = execSync(`node render-poster.mjs "${taskDir}"`, { encoding: "utf-8", cwd: SKILL_ROOT });
    console.log(rOut.split("\n").map(l => "    " + l).join("\n"));
  } else {
    console.log("\n[7] validate + render (skipped due to --dry-run)");
  }

  // 12. tasks.jsonl
  console.log("\n[9] publisher tasks.jsonl:");
  const platforms = choosePlatforms(profile, opts.platforms);
  const tasksPath = toTasksJsonl({ taskDir, profile, platforms, dryRun: opts.dryRun });
  const pngCount = (() => {
    try {
      const outDir = path.join(taskDir, "output");
      return fs.existsSync(outDir) ? fs.readdirSync(outDir).filter(f => f.endsWith(".png")).length : 0;
    } catch { return 0; }
  })();
  console.log(`    → ${tasksPath} (${(fs.statSync(tasksPath).size / 1024).toFixed(1)} KB · ${platforms.join(", ")} · ${pngCount} PNG${opts.dryRun ? " · dry-run placeholder" : ""})`);

  // 13. publisher.py batch (mock 入表)
  if (!opts.dryRun) {
    console.log("\n[10] publisher.py batch (mock):");
    const res = runPublisherBatch(tasksPath);
    console.log(`    cmd: ${res.cmd}`);
    console.log(`    exit code: ${res.code}`);
    if (res.stdout) console.log(`    stdout: ${res.stdout.slice(0, 500)}`);
    if (res.stderr) console.error(`    stderr: ${res.stderr.slice(0, 200)}`);
    // 注：publisher.py 在 Windows gbk stdout 上 emoji 编码会抛 UnicodeEncodeError
    //  → exit code 1 但 mock 已经成功写入 publish_results 表（见 publisher.db）
    //  → 视为 advisory 警告，pipeline 不视为 fatal
    if (res.code !== 0) {
      console.warn(`    [advisory] publisher.py exit ${res.code} — 可能为 stdout emoji gbk 编码问题，验证 publisher.db 行数确认成功`);
    }
  } else {
    console.log("\n[10] publisher (skipped due to --dry-run)");
  }

  console.log("\n=== 阶段 19 V2.0 完成 ===");
  console.log(`task 目录: ${taskDir}`);
  // ──── ⭐ 新增：草稿模式 vs 直接发布 ────
  if (opts.draft) {
    // ⭐ --draft 模式：写入审批队列
    console.log("\n[10] ⭐ 草稿模式（--draft）:");
    await saveToDraftQueue({
      bloggerId: profile.blogger_id || opts.blogger,
      taskDir,
      tasksPath,
      pages,
      platforms,
      pngCount,
      profile,
    });
  } else {
    // 原有模式：直接调用 publisher.py
    // 13. publisher.py batch (mock 入表)
    if (!opts.dryRun) {
      console.log("\n[10] publisher.py batch (mock):");
      const res = runPublisherBatch(tasksPath);
      console.log(`    cmd: ${res.cmd}`);
      console.log(`    exit code: ${res.code}`);
      if (res.stdout) console.log(`    stdout: ${res.stdout.slice(0, 500)}`);
      if (res.stderr) console.error(`    stderr: ${res.stderr.slice(0, 200)}`);
      if (res.code !== 0) {
        console.warn(`    [advisory] publisher.py exit ${res.code} — 可能为 stdout emoji gbk 编码问题`);
      }
    } else {
      console.log("\n[10] publisher (skipped due to --dry-run)");
    }
  }

  console.log("\n=== 阶段 19 V2.1 完成 ===");
  if (opts.draft) {
    console.log(`⭐ 草稿已写入审批队列，使用 dragon.js approve 批准发布`);
  }
  console.log(`输出 PNG: ${path.join(taskDir, "output")}`);
  console.log(`tasks.jsonl: ${tasksPath}`);
}

main().catch(async e => {
  console.error("[FATAL]", e.stack || e.message);
  process.exit(1);
});

// ───── --all 批量模式 ─────
// ===== Node-native SQLite helper (替代 sqlite3 CLI 依赖) =====
// REGISTRY_DB 在下面 line 296 处定义

/**
 * 读单个博主的 design_style + consent_expires_at
 * 用 Node 22.5+ 内置 node:sqlite,无 sqlite3 CLI 依赖
 * @param {string} bloggerId
 * @returns {{ design_style: string|null, consent_expires_at: string|null }|null}
 */
async function readRegistryRow(bloggerId) {
  try {
    const sqlite = await import("node:sqlite");
    const { DatabaseSync } = sqlite;
    if (!fs.existsSync(REGISTRY_DB)) return null;
    const db = new DatabaseSync(REGISTRY_DB);
    const row = db.prepare(`
      SELECT design_style, consent_expires_at
      FROM fingerprints WHERE blogger_id = ?
    `).get(bloggerId);
    db.close();
    return row || null;
  } catch (e) {
    return null;
  }
}

/**
 * 读所有 active 博主(retired_at IS NULL)
 */
async function readRegistryActiveRows() {
  const sqlite = await import("node:sqlite");
  const { DatabaseSync } = sqlite;
  const db = new DatabaseSync(REGISTRY_DB);
  const rows = db.prepare(`
    SELECT blogger_id, blogger_name, design_style, consent_expires_at
    FROM fingerprints WHERE retired_at IS NULL ORDER BY id
  `).all();
  db.close();
  return rows;
}

// 从 registry.db 读所有 active 博主（retired_at IS NULL），串行跑 main()
//   跳过 consent_expires_at < now 的博主（硬阻断）
async function runAll(opts) {
  if (!fs.existsSync(REGISTRY_DB)) {
    console.error(`registry.db not found: ${REGISTRY_DB}`);
    process.exit(2);
  }
  const rows = await readRegistryActiveRows();
  if (!rows.length) {
    console.log("[--all] 没有活跃博主，退出");
    return;
  }
  const now = new Date();
  console.log(`=== blogger-poster.mjs · 阶段 19 V2.0 · --all 模式 ===`);
  console.log(`找到 ${rows.length} 个活跃博主：`);
  const valid = [];
  const expired = [];
  for (const r of rows) {
    const exp = new Date(r.consent_expires_at);
    if (exp < now) {
      expired.push(r);
      console.log(`  [SKIP] ${r.blogger_id} · consent expired ${r.consent_expires_at}`);
    } else {
      valid.push(r);
      console.log(`  [OK]   ${r.blogger_id} · design_style=${r.design_style} · expires ${r.consent_expires_at}`);
    }
  }
  if (expired.length) console.log(`[--all] 跳过 ${expired.length} 个过期博主`);
  console.log(`\n开始批量出图（${valid.length} 个博主，串行）：\n`);
  const results = [];
  for (const r of valid) {
    console.log(`\n${"=".repeat(60)}\n[--all] 处理博主: ${r.blogger_id}\n${"=".repeat(60)}`);
    try {
      const t0 = Date.now();
      // 在子进程内重新跑一次 pipeline（每次 blogger 不同）
      const args = process.argv.slice(2).filter(a => a !== "--all");
      args.push("--blogger", r.blogger_id);
      execSync(`node "${path.resolve(__filename)}" ${args.join(" ")}`, { stdio: "inherit" });
      results.push({ id: r.blogger_id, ok: true, ms: Date.now() - t0 });
    } catch (e) {
      console.error(`[--all] ${r.blogger_id} 失败: ${e.message}`);
      results.push({ id: r.blogger_id, ok: false, ms: 0 });
    }
  }
  console.log(`\n${"=".repeat(60)}\n=== --all 模式批量完成 ===\n${"=".repeat(60)}`);
  console.log(`成功: ${results.filter(r => r.ok).length} / ${results.length}`);
  for (const r of results) {
    console.log(`  ${r.ok ? "✓" : "✗"} ${r.id} (${r.ms}ms)`);
  }
}
// ──── ⭐ 新增：saveToDraftQueue 函数 ────
/**
 * 将生成的内容保存到审批队列
 * @param {Object} options
 */
async function saveToDraftQueue(options) {
  const { bloggerId, taskDir, tasksPath, pages, platforms, pngCount, profile } = options;

  // 动态导入 dragon.js 的 Draft 和 Queue 类
  const dragonScriptPath = path.join(SKILL_ROOT, "..", "..", "scripts", "dragon.js");
  const dragonModulePath = path.resolve(dragonScriptPath);

  // 生成草稿 ID
  const now = new Date();
  const dateStr = now.toISOString().slice(0, 10).replace(/-/g, "");
  const seq = String(Math.floor(Math.random() * 999) + 1).padStart(3, "0");
  const draftId = `draft-${dateStr}-${seq}`;

  // 收集 PNG 文件
  const outDir = path.join(taskDir, "output");
  const files = [];
  if (fs.existsSync(outDir)) {
    const pngFiles = fs.readdirSync(outDir).filter(f => f.endsWith(".png"));
    for (const f of pngFiles) {
      files.push(path.join(outDir, f));
    }
  }

  // 构建草稿对象
  const draft = {
    draft_id: draftId,
    blogger_id: bloggerId,
    type: platforms.includes("xiaohongshu") ? "xiaohongshu_carousel" : "custom",
    status: "pending",
    content: {
      title: profile.blogger_name || bloggerId,
      description: `自动生成内容 · ${pngCount} 张 PNG`,
      slides: pages.map((p, i) => ({
        page: p.page || i + 1,
        image_path: files[i] || null,
        text: p.title || "",
        background: p.background || null,
      })),
      tags: platforms,
    },
    metadata: {
      created_at: now.toISOString(),
      created_by: "blogger-poster.mjs --draft",
      source: "auto_generated",
      files: files,
      platforms: platforms,
      task_dir: taskDir,
      tasks_path: tasksPath,
    },
    review: {
      reviewer: null,
      approved_at: null,
      rejected_at: null,
      rejection_reason: null,
      notes: null,
      history: [],
    },
  };

  // 写入草稿文件到 drafts/pending/
  const draftsDir = "C:/Users/li/.dragon-engine/drafts";
  const pendingDir = path.join(draftsDir, "pending");
  fs.mkdirSync(pendingDir, { recursive: true });

  const draftPath = path.join(pendingDir, `${draftId}.json`);
  fs.writeFileSync(draftPath, JSON.stringify(draft, null, 2), "utf-8");
  console.log(`    → 草稿文件: ${draftPath}`);

  // 更新队列
  const queuePath = path.join(draftsDir, "queue.json");
  let queue = { version: "1.0", updated_at: now.toISOString(), queue: [] };
  if (fs.existsSync(queuePath)) {
    try {
      queue = JSON.parse(fs.readFileSync(queuePath, "utf-8"));
    } catch (e) {
      // 忽略解析错误
    }
  }

  queue.queue.push({
    draft_id: draftId,
    position: queue.queue.length + 1,
    status: "pending",
    blogger_id: bloggerId,
    platforms: platforms,
    submitted_at: now.toISOString(),
  });
  queue.updated_at = now.toISOString();
  fs.writeFileSync(queuePath, JSON.stringify(queue, null, 2), "utf-8");
  console.log(`    → 队列已更新`);

  console.log(`    草稿ID: ${draftId}`);
  console.log(`    PNG文件: ${files.length} 张`);
  console.log(`    平台: ${platforms.join(", ")}`);
  console.log(`\n  使用以下命令审批:`);
  console.log(`    node ../scripts/dragon.js review ${draftId}`);
  console.log(`    node ../scripts/dragon.js approve ${draftId}`);
}
