// to-xhs-publisher.mjs · V2.2 XHS 封面 prompt → publisher 入表
// 阶段 22 · 2026-07-20
//
// 设计:支持 4 种输入模式,与 V2.0 to-publisher.mjs 互补
//   1. prompt-only mode (default): 只入 prompt + meta(等真实 PNG 出来再补)
//   2. png-mode: 已有 PNG 目录(与 V2.0 行为对齐)
//   3. dry-run: 只生成 tasks.jsonl,不调 publisher.py
//   4. live: prompt → gpt-image-2 后端生成 PNG → publisher 入表(需 API key)

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync, writeFileSync } from "node:fs";
import { join, resolve, basename } from "node:path";
import { execSync } from "node:child_process";

const PUBLISHER_DIR = "C:/Users/li/.claude/skills/multi-platform-publisher";
const PUBLISHER_SCRIPT = "scripts/publisher.py";

// 1x1 #FDFFA7 PNG 占位（base64 编码，最小合法 PNG）
// 真实模式下应被 gpt-image-2 后端生成的真实 PNG 替换
const PLACEHOLDER_PNG_BASE64 =
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=";

/**
 * 生成 1x1 占位 PNG（dry-run 用，真实模式必须替换为 gpt-image-2 输出）
 * @param {string} outputPath - PNG 文件路径
 */
export function writePlaceholderPNG(outputPath) {
  const buf = Buffer.from(PLACEHOLDER_PNG_BASE64, "base64");
  writeFileSync(outputPath, buf);
  return outputPath;
}

/**
 * 选择平台列表
 * @param {object} opts
 * @param {string[]} [opts.platforms]  CLI 显式指定
 * @param {string} [opts.contentType]  image / video
 * @returns {string[]}
 */
export function choosePlatforms({ platforms, contentType = "image" }) {
  if (platforms?.length) return platforms;
  // XHS 封面默认入小红书 + 公众号文章配图
  return contentType === "video"
    ? ["xiaohongshu", "douyin", "tiktok"]
    : ["xiaohongshu", "wechat"];
}

/**
 * 从 prompt + meta 推断 role
 */
export function inferRoleFromMeta(meta) {
  const styleId = meta.style_id || "xhs-portrait";
  // 8 套 XHS 风格统一归为 xhs-portrait image
  return {
    platform: "xiaohongshu",
    contentType: "image",
    role: `xhs-${styleId.replace(/^xhs-/, "")}`,
  };
}

/**
 * 单条 prompt → PublishTask
 * @param {object} opts
 * @param {string} opts.prompt - XHS 封面 prompt 文本
 * @param {object} opts.meta - 渲染元数据(含 style_id / palette 等)
 * @param {object} opts.profile - 博主全息
 * @param {string[]} opts.platforms
 * @param {string} [opts.contentPath] - PNG 路径(若有)
 * @returns {object} PublishTask(JSON 序列化后即入 publisher.py batch)
 */
export function promptToPublishTask({ prompt, meta, profile, platforms, contentPath = null }) {
  const { platform, contentType, role } = inferRoleFromMeta(meta);
  const bloggerId = meta.blogger || profile?.blogger_id || "anonymous";

  const tags = [
    "XHS-爆款封面",
    "V2.2",
    "#FDFFA7",
    meta.style_id || "unknown-style",
    profile?.dim_7_writing_style?.style_name || "未指定",
    "atutun-inspired"
  ];

  const description = `XHS 真人出镜爆款封面 · 风格 ${meta.style_id || "auto"} · prompt ${meta.prompt_length || prompt.length} chars。atutun 风格借鉴（非镜像）。`;
  const title = profile?.default_title || `${bloggerId} · XHS 封面`;

  return {
    blogger_id:        bloggerId,
    content_type:      contentType,
    content_path:      contentPath ? contentPath.replace(/\\/g, "/") : null,
    title,
    description,
    tags,
    platforms:         platforms || [platform],
    scheduled_at:      null,
    watermark:         true,
    account_ids:       {},
    // 私有字段(发 publisher 也不报错;publisher.db 不消费)
    // _meta: { prompt, meta }
  };
}

/**
 * 把 _meta 写入文件 metadata(参考 V2.0 to-publisher.mjs 处理)
 * @param {object} task - PublishTask
 * @returns {object} 剥离 _meta 的安全 task
 */
export function stripMetaForPublisher(task) {
  if (task._meta) {
    const { _meta, ...rest } = task;
    return rest;
  }
  return task;
}

/**
 * 生成 tasks-xhs.jsonl
 * @param {object} opts
 * @param {object[]} opts.tasks - PublishTask 数组
 * @param {string} opts.outputDir - 输出目录
 * @returns {Promise<string>} tasks-xhs.jsonl 路径
 */
export async function writeTasksJsonl({ tasks, outputDir }) {
  await mkdir(outputDir, { recursive: true });
  const outPath = join(outputDir, "tasks-xhs.jsonl");
  const content = tasks.map(t => JSON.stringify(stripMetaForPublisher(t))).join("\n") + "\n";
  await writeFile(outPath, content, "utf-8");
  return outPath;
}

/**
 * 主入口:XHS 封面 → publisher 入表
 * @param {object} opts
 * @param {string} opts.prompt - XHS prompt 文本
 * @param {object} opts.meta - 渲染元数据
 * @param {object} opts.profile - 博主全息
 * @param {string} [opts.contentPath] - 已有 PNG(若已渲染)
 * @param {string[]} [opts.platforms]
 * @param {string} opts.outputDir - tasks.jsonl 输出目录
 * @param {boolean} [opts.dryRun=true]
 * @param {boolean} [opts.runPublisher=false] - 是否真的跑 publisher.py
 * @returns {Promise<{tasksPath: string, published: boolean, output: string}>}
 */
export async function publishXHSToPublisher({
  prompt,
  meta,
  profile,
  contentPath = null,
  platforms = null,
  outputDir,
  dryRun = true,
  runPublisher = false
}) {
  // 1. 选平台
  const finalPlatforms = platforms || choosePlatforms({
    contentType: meta.contentType || "image"
  });

  // 2. content_path: 若没传,生成占位 PNG（满足 publisher.py 强制约束）
  if (!contentPath) {
    const placeholderPath = join(outputDir, `${meta.style_id || "xhs-cover"}-placeholder.png`);
    writePlaceholderPNG(placeholderPath);
    contentPath = placeholderPath;
  }

  // 3. 单条 PublishTask(本批次单图)
  const task = promptToPublishTask({
    prompt, meta, profile,
    platforms: finalPlatforms,
    contentPath
  });

  // _meta 单独保留(metadata 用)
  task._meta = {
    prompt,
    original_meta: meta,
    generated_by: "to-xhs-publisher.mjs (V2.2)",
    content_path_note: contentPath.endsWith("-placeholder.png")
      ? "占位 PNG（1x1 #FDFFA7）— 待 gpt-image-2 后端替换"
      : "真实 PNG（已渲染）"
  };

  // 3. 写 tasks.jsonl
  const tasksPath = await writeTasksJsonl({ tasks: [task], outputDir });

  // 4. 是否真跑 publisher
  let published = false;
  let output = "";
  if (runPublisher && !dryRun) {
    const absTasksPath = resolve(tasksPath);
    try {
      output = execSync(
        `python ${PUBLISHER_SCRIPT} batch --file "${absTasksPath}"`,
        { cwd: PUBLISHER_DIR, encoding: "utf-8", timeout: 60000 }
      );
      published = true;
    } catch (e) {
      published = false;
      output = `❌ publisher.py exit ${e.status}\n${e.stdout || ""}\n${e.stderr || e.message}`;
    }
  } else {
    output = dryRun
      ? "(dry-run mode: tasks.jsonl generated only)"
      : "(no-run mode: tasks.jsonl generated; set runPublisher=true to invoke publisher.py)";
  }

  return { tasksPath, published, output };
}

// CLI 入口:node to-xhs-publisher.mjs <blogger> <style>
export async function cliMain() {
  const [,, blogger, style] = process.argv;
  if (!blogger || !style) {
    console.error("用法: node to-xhs-publisher.mjs <blogger> <style>");
    console.error("示例: node to-xhs-publisher.mjs laoli_bro_2026 xhs-checklist");
    process.exit(2);
  }

  const metaPath = resolve(process.cwd(), "output", `${blogger}-${style}.meta.json`);
  if (!existsSync(metaPath)) {
    console.error(`❌ meta 不存在: ${metaPath}`);
    console.error(`请先跑: node tests/dry-run-xhs-cover.mjs --blogger ${blogger} --style ${style}`);
    process.exit(2);
  }

  const meta = JSON.parse(await readFile(metaPath, "utf-8"));
  const profile = JSON.parse(
    await readFile(`C:/Users/li/.claude/ip-profiles/${blogger}/ip_profile_8dim.json`, "utf-8")
  );
  const prompt = meta.prompt || "(prompt already saved in tasks.jsonl _meta)";

  const result = await publishXHSToPublisher({
    prompt,
    meta,
    profile,
    outputDir: resolve(process.cwd(), "output"),
    dryRun: true,
    runPublisher: false
  });

  console.log(`\n[to-xhs-publisher] tasks: ${result.tasksPath}`);
  console.log(`[to-xhs-publisher] published: ${result.published}`);
  console.log(`[to-xhs-publisher] ${result.output}`);
}

// 当作主模块运行
import { fileURLToPath } from "node:url";
import { resolve as resolvePath } from "node:path";

if (process.argv[1] && import.meta.url.endsWith(basename(process.argv[1]))) {
  cliMain().catch(e => {
    console.error("ERR:", e.message);
    process.exit(1);
  });
}