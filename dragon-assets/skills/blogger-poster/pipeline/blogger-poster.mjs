#!/usr/bin/env node
/*
 * blogger-poster.mjs · 天龙引擎适配版 V1.0
 *
 * 8维博主全息 → 小红书/公众号 PNG → multi-platform-publisher
 *
 * 用法:
 *   node blogger-poster.mjs --blogger <id> [--platforms xiaohongshu,wechat] [--draft] [--dry-run]
 *   node blogger-poster.mjs --all [--platforms xhs]
 *   node blogger-poster.mjs --profile /path/to/ip_profile.json
 *
 * 天龙引擎路径:
 *   SKILL_ROOT: skills/blogger-poster/
 *   IP_PROFILES: C:/Users/li/.claude/ip-profiles/
 *   REGISTRY_DB: C:/Users/li/.claude/skills/blogger-fingerprint-registry/registry.db
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execSync } from "node:child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = path.resolve(__dirname, "..");

// 天龙引擎路径配置
const PATHS = {
  SKILL_ROOT: "C:/Users/li/.claude/projects/dragon-engine/skills/blogger-poster",
  GUIZANG_ROOT: "C:/Users/li/.claude/projects/dragon-engine/skills/guizang-social-card-skill",
  PUBLISHER_DIR: "C:/Users/li/.claude/skills/multi-platform-publisher",
  REGISTRY_DB: "C:/Users/li/.claude/skills/blogger-fingerprint-registry/registry.db",
  IP_PROFILES_DIR: "C:/Users/li/.claude/ip-profiles",
  DRAFTS_DIR: "C:/Users/li/.dragon-engine/drafts",
};

// ───── CLI 解析 ─────
const args = process.argv.slice(2);
const opts = {
  blogger: null,
  profile: null,
  platforms: null,
  dryRun: false,
  slug: null,
  all: false,
  draft: false,
};

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--blogger") opts.blogger = args[++i];
  else if (args[i] === "--profile") opts.profile = args[++i];
  else if (args[i] === "--platforms") opts.platforms = args[++i].split(",").map(s => s.trim());
  else if (args[i] === "--slug") opts.slug = args[++i];
  else if (args[i] === "--dry-run") opts.dryRun = true;
  else if (args[i] === "--all") opts.all = true;
  else if (args[i] === "--draft") opts.draft = true;
  else if (args[i] === "--help" || args[i] === "-h") {
    printHelp();
    process.exit(0);
  }
}

// ───── 工具函数 ─────
function printHelp() {
  console.log(`
blogger-poster.mjs · 天龙引擎适配版 V1.0

用法:
  node blogger-poster.mjs --blogger <id> [--platforms xiaohongshu,wechat] [--draft] [--dry-run]
  node blogger-poster.mjs --all [--platforms xhs]
  node blogger-poster.mjs --profile /path/to/ip_profile.json

参数:
  --blogger <id>      博主 ID
  --profile <path>    博主全息路径（覆盖默认位置）
  --platforms <list>  目标平台（逗号分隔）
  --draft             草稿审批模式
  --dry-run           预览模式（不渲染、不发布）
  --all               批量发布所有活跃博主
  --slug <name>       自定义输出目录名
  --help, -h          显示帮助

示例:
  node blogger-poster.mjs --blogger laoli_bro_2026
  node blogger-poster.mjs --blogger laoli_bro_2026 --platforms xiaohongshu
  node blogger-poster.mjs --blogger laoli_bro_2026 --draft
  node blogger-poster.mjs --all --platforms xiaohongshu,douyin
`);
}

// ───── 加载博主全息 ─────
function loadProfile(bloggerId, profilePath) {
  if (profilePath && fs.existsSync(profilePath)) {
    return JSON.parse(fs.readFileSync(profilePath, "utf-8"));
  }
  const p = path.join(PATHS.IP_PROFILES_DIR, bloggerId, "ip_profile_8dim.json");
  if (!fs.existsSync(p)) {
    const p9 = path.join(PATHS.IP_PROFILES_DIR, bloggerId, "ip_profile_9dim.json");
    if (fs.existsSync(p9)) {
      return JSON.parse(fs.readFileSync(p9, "utf-8"));
    }
    console.error(`[FAIL] 找不到博主全息: ${p}`);
    console.error(`       请先用 35-06 蒸馏该博主，或使用 --profile 指定路径`);
    process.exit(2);
  }
  return JSON.parse(fs.readFileSync(p, "utf-8"));
}

// ───── IP 授权三重护栏 ─────
function checkConsent(profile) {
  const consent = profile._meta?.consent || profile.ip_consent_summary || {};
  const errors = [];
  const warnings = [];

  if (!consent.voice_consent_file && !consent.voice_authorized) {
    errors.push("[HARD] 缺少声纹授权（voice_consent_file / voice_authorized）");
  }
  if (!consent.ip_consent_file && !consent.ip_image_authorized) {
    errors.push("[HARD] 缺少 IP 形象授权（ip_consent_file / ip_image_authorized）");
  }
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

// ───── 调色板选择 ─────
function detectPalette(colors = []) {
  if (!colors?.length) {
    return { family: "ink", theme: "default", label: "ink-default", confidence: 0.5 };
  }
  const hasWarm = colors.some(c => {
    const r = parseInt(c.slice(1, 3), 16) || 0;
    return r > 150;
  });
  const hasCool = colors.some(c => {
    const b = parseInt(c.slice(5, 7), 16) || 0;
    return b > 150;
  });
  if (hasWarm) return { family: "warm", theme: "sunset", label: "warm-sunset", confidence: 0.8 };
  if (hasCool) return { family: "cool", theme: "ocean", label: "cool-ocean", confidence: 0.8 };
  return { family: "ink", theme: "default", label: "ink-default", confidence: 0.5 };
}

// ───── 读取 Registry ─────
async function readRegistryRow(bloggerId) {
  try {
    const sqlite = await import("node:sqlite");
    const { DatabaseSync } = sqlite;
    if (!fs.existsSync(PATHS.REGISTRY_DB)) return null;
    const db = new DatabaseSync(PATHS.REGISTRY_DB);
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

async function readRegistryActiveRows() {
  const sqlite = await import("node:sqlite");
  const { DatabaseSync } = sqlite;
  if (!fs.existsSync(PATHS.REGISTRY_DB)) return [];
  const db = new DatabaseSync(PATHS.REGISTRY_DB);
  const rows = db.prepare(`
    SELECT blogger_id, blogger_name, design_style, consent_expires_at
    FROM fingerprints WHERE retired_at IS NULL ORDER BY id
  `).all();
  db.close();
  return rows;
}

// ───── 选择平台 ─────
function choosePlatforms(argPlatforms) {
  if (argPlatforms && argPlatforms.length > 0) return argPlatforms;
  return ["xiaohongshu", "wechat"];
}

// ───── 推断文件名角色 ─────
function inferRoleFromFilename(filename) {
  const base = path.basename(filename, ".png");
  if (base.startsWith("xhs-")) {
    return { platform: "xiaohongshu", contentType: "image", role: "carousel-page" };
  }
  if (base.startsWith("wechat-21x9")) {
    return { platform: "wechat", contentType: "article", role: "article-cover" };
  }
  if (base.startsWith("wechat-1x1")) {
    return { platform: "wechat", contentType: "article", role: "article-share" };
  }
  return { platform: "xiaohongshu", contentType: "image", role: "image" };
}

// ───── 生成 tasks.jsonl ─────
function toTasksJsonl({ taskDir, profile, platforms, dryRun = false }) {
  const outputDir = path.join(taskDir, "output");
  const pngs = (fs.existsSync(outputDir) ? fs.readdirSync(outputDir) : [])
    .filter(f => f.endsWith(".png"))
    .sort();

  if (!dryRun && pngs.length === 0) {
    throw new Error(`output dir 下没有 PNG: ${outputDir}`);
  }

  const tags = ["博主全息", profile.dim_7_writing_style?.style_name || "个人风", "blogger-poster-v1.0"];
  const bloggerId = profile.blogger_id || "unknown";
  const description = `基于博主 ${profile.blogger_name || bloggerId} 全息自动生成。`;

  const tasks = pngs.length
    ? pngs.map(png => {
        const contentPath = path.join(outputDir, png);
        const { platform, contentType } = inferRoleFromFilename(png);
        return {
          blogger_id: bloggerId,
          content_type: contentType,
          content_path: contentPath.replace(/\\/g, "/"),
          title: `${profile.blogger_name || bloggerId} · 全息自动出图`,
          description,
          tags,
          platforms,
          scheduled_at: null,
          watermark: true,
          account_ids: {},
        };
      })
    : [{
        blogger_id: bloggerId,
        content_type: "image",
        content_path: null,
        title: `${profile.blogger_name || bloggerId} · 全息自动出图`,
        description,
        tags,
        platforms,
        scheduled_at: null,
        watermark: true,
        account_ids: {},
      }];

  const outPath = path.join(taskDir, "tasks.jsonl");
  fs.writeFileSync(outPath, tasks.map(t => JSON.stringify(t)).join("\n") + "\n", "utf-8");
  return outPath;
}

// ───── 调用 publisher.py ─────
function runPublisherBatch(tasksPath, dryRun = false) {
  const cmd = `python scripts/publisher.py batch --file "${tasksPath}"`;
  if (dryRun) {
    return { cmd, code: 0, stdout: "(dry-run)", stderr: "" };
  }
  try {
    const stdout = execSync(cmd, {
      cwd: PATHS.PUBLISHER_DIR,
      encoding: "utf-8",
      timeout: 60000,
      stdio: ["ignore", "pipe", "pipe"],
    });
    return { cmd, code: 0, stdout, stderr: "" };
  } catch (e) {
    return {
      cmd,
      code: e.status || 1,
      stdout: e.stdout?.toString() || "",
      stderr: e.stderr?.toString() || e.message,
    };
  }
}

// ───── 简化 Page 抽取 ─────
function extractPages(profile, choice) {
  const pageCount = 5;
  const pages = [];
  const bloggerName = profile.blogger_name || profile.blogger_id || "博主";

  for (let i = 1; i <= pageCount; i++) {
    pages.push({
      page: i,
      role: i === 1 ? "cover" : i === pageCount ? "ending" : "content",
      title: `第${i}页 · ${bloggerName}`,
      content: profile.dim_7_writing_style?.sample_posts?.[i % 3] || "",
    });
  }
  return pages;
}

// ───── 写 pages.jsonl ─────
function writePages(pages, pagesPath) {
  fs.writeFileSync(pagesPath, pages.map(p => JSON.stringify(p)).join("\n") + "\n", "utf-8");
}

// ───── 草稿保存 ─────
async function saveToDraftQueue(options) {
  const { bloggerId, taskDir, tasksPath, pages, platforms, pngCount, profile } = options;

  const now = new Date();
  const dateStr = now.toISOString().slice(0, 10).replace(/-/g, "");
  const seq = String(Math.floor(Math.random() * 999) + 1).padStart(3, "0");
  const draftId = `draft-${dateStr}-${seq}`;

  const outDir = path.join(taskDir, "output");
  const files = [];
  if (fs.existsSync(outDir)) {
    const pngFiles = fs.readdirSync(outDir).filter(f => f.endsWith(".png"));
    for (const f of pngFiles) {
      files.push(path.join(outDir, f));
    }
  }

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
      })),
      tags: platforms,
    },
    metadata: {
      created_at: now.toISOString(),
      created_by: "blogger-poster.mjs v1.0",
      source: "auto_generated",
      files,
      platforms,
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

  const pendingDir = path.join(PATHS.DRAFTS_DIR, "pending");
  fs.mkdirSync(pendingDir, { recursive: true });

  const draftPath = path.join(pendingDir, `${draftId}.json`);
  fs.writeFileSync(draftPath, JSON.stringify(draft, null, 2), "utf-8");
  console.log(`    → 草稿文件: ${draftPath}`);

  const queuePath = path.join(PATHS.DRAFTS_DIR, "queue.json");
  let queue = { version: "1.0", updated_at: now.toISOString(), queue: [] };
  if (fs.existsSync(queuePath)) {
    try {
      queue = JSON.parse(fs.readFileSync(queuePath, "utf-8"));
    } catch (e) { /* 忽略 */ }
  }

  queue.queue.push({
    draft_id: draftId,
    position: queue.queue.length + 1,
    status: "pending",
    blogger_id: bloggerId,
    platforms,
    submitted_at: now.toISOString(),
  });
  queue.updated_at = now.toISOString();
  fs.writeFileSync(queuePath, JSON.stringify(queue, null, 2), "utf-8");

  console.log(`    草稿ID: ${draftId}`);
  console.log(`    使用 dragon.js approve ${draftId} 批准发布`);
}

// ───── 主流程 ─────
async function main() {
  console.log("=== blogger-poster.mjs · 天龙引擎适配版 V1.0 ===\n");

  if (opts.all) {
    return await runAll(opts);
  }

  if (!opts.blogger && !opts.profile) {
    console.error("请提供 --blogger <blogger_id> 或 --profile <path>");
    process.exit(2);
  }

  const profile = loadProfile(opts.blogger, opts.profile);
  console.log(`[1] 加载博主全息: ${profile.blogger_id || opts.blogger} (${profile.blogger_name || ""})`);

  checkConsent(profile);

  console.log("\n[2] 调色板选择:");
  let designStyle = null;
  const _row = await readRegistryRow(profile.blogger_id);
  if (_row && _row.design_style) designStyle = _row.design_style;
  profile._design_style = designStyle;

  const pal = detectPalette(profile.dim_8_ip_visual?.spec?.color_palette || []);
  const choice = { theme: pal.theme, family: pal.family, source: designStyle ? "registry" : "palette-auto" };
  console.log(`    design_style: ${designStyle || "（未设置）"}`);
  console.log(`    → 推断 ${pal.family}/${pal.theme} (confidence=${pal.confidence})`);

  console.log("\n[3] Page 抽取:");
  const pages = extractPages(profile, choice);
  console.log(`    → ${pages.length} 页`);

  const slug = opts.slug || `blogger-${profile.blogger_id}-${(choice.theme || "ink").toLowerCase()}`;
  const taskDir = path.join(PATHS.SKILL_ROOT, "local-tests", slug);
  fs.mkdirSync(taskDir, { recursive: true });
  console.log(`\n[4] task 目录: ${taskDir}`);

  const pagesPath = path.join(taskDir, "pages.jsonl");
  writePages(pages, pagesPath);
  console.log(`    → pages.jsonl 写出`);

  console.log("\n[5] 生成发布任务:");
  const platforms = choosePlatforms(opts.platforms);
  const tasksPath = toTasksJsonl({ taskDir, profile, platforms, dryRun: opts.dryRun });
  const pngCount = (() => {
    try {
      const outDir = path.join(taskDir, "output");
      return fs.existsSync(outDir) ? fs.readdirSync(outDir).filter(f => f.endsWith(".png")).length : 0;
    } catch { return 0; }
  })();
  console.log(`    → ${platforms.join(", ")} · ${pngCount} PNG`);

  if (opts.draft) {
    await saveToDraftQueue({ bloggerId: profile.blogger_id || opts.blogger, taskDir, tasksPath, pages, platforms, pngCount, profile });
  } else if (!opts.dryRun) {
    console.log("\n[6] 调用 publisher.py:");
    const res = runPublisherBatch(tasksPath, false);
    console.log(`    cmd: ${res.cmd}`);
    console.log(`    exit code: ${res.code}`);
    if (res.code !== 0) {
      console.warn(`    [advisory] publisher.py exit ${res.code} — 可能为编码问题`);
    }
  } else {
    console.log("\n[6] publisher (skipped due to --dry-run)");
  }

  console.log("\n=== 完成 ===");
  console.log(`task 目录: ${taskDir}`);
  console.log(`tasks.jsonl: ${tasksPath}`);
}

// ───── 批量模式 ─────
async function runAll(opts) {
  if (!fs.existsSync(PATHS.REGISTRY_DB)) {
    console.error(`registry.db not found: ${PATHS.REGISTRY_DB}`);
    process.exit(2);
  }
  const rows = await readRegistryActiveRows();
  if (!rows.length) {
    console.log("[--all] 没有活跃博主，退出");
    return;
  }

  const now = new Date();
  console.log(`=== blogger-poster.mjs · --all 模式 ===`);
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
      console.log(`  [OK]   ${r.blogger_id} · design_style=${r.design_style}`);
    }
  }

  console.log(`\n开始批量出图（${valid.length} 个）：\n`);
  const results = [];
  for (const r of valid) {
    console.log(`\n${"=".repeat(60)}\n处理博主: ${r.blogger_id}\n${"=".repeat(60)}`);
    try {
      const t0 = Date.now();
      execSync(`node "${__filename}" --blogger ${r.blogger_id} ${opts.platforms ? `--platforms ${opts.platforms.join(",")}` : ""}`, { stdio: "inherit" });
      results.push({ id: r.blogger_id, ok: true, ms: Date.now() - t0 });
    } catch (e) {
      results.push({ id: r.blogger_id, ok: false, ms: 0 });
    }
  }

  console.log(`\n${"=".repeat(60)}\n=== 批量完成 ===`);
  console.log(`成功: ${results.filter(r => r.ok).length} / ${results.length}`);
  for (const r of results) {
    console.log(`  ${r.ok ? "✓" : "✗"} ${r.id}`);
  }
}

main().catch(e => {
  console.error("[FATAL]", e.stack || e.message);
  process.exit(1);
});
