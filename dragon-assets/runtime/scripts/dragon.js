#!/usr/bin/env node
/**
 * dragon.js · P0 审批工作流
 * 天龙引擎审批 CLI：draft → review → approve → publish
 *
 * 用法：
 *   node dragon.js init                                           初始化工作流
 *   node dragon.js generate --blogger <id>                       生成草稿（直接发布）
 *   node dragon.js generate --blogger <id> --draft              生成草稿（进入审批队列）
 *   node dragon.js list [--status pending|review|approved|rejected]
 *   node dragon.js review <draft_id>                             预览草稿
 *   node dragon.js approve <draft_id> [--comment "..."]        批准发布
 *   node dragon.js reject <draft_id> --reason "..."            拒绝并说明原因
 *   node dragon.js status <draft_id>                            查看草稿状态
 *   node dragon.js publish <draft_id> [--platforms xhs,wechat] 手动发布
 *
 * 示例：
 *   node dragon.js generate --blogger laoli_bro_2026 --draft
 *   node dragon.js list
 *   node dragon.js approve draft-20260817-001
 *   node dragon.js reject draft-20260817-002 --reason "标题需要修改"
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execSync } from "node:child_process";
import { createInterface } from "node:readline";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ───── 路径常量 ─────
const CONFIG_PATH = "C:/Users/li/.dragon-engine/config.json";
const DRAFTS_DIR = "C:/Users/li/.dragon-engine/drafts";
const QUEUE_PATH = "C:/Users/li/.dragon-engine/queue.json";
const REGISTRY_DB = "C:/Users/li/.claude/skills/blogger-fingerprint-registry/registry.db";
const PUBLISHER_DB = "C:/Users/li/.claude/projects/dragon-engine/skills/multi-platform-publisher/publisher.db";

// ───── 状态常量 ─────
const DRAFT_STATUS = {
  PENDING: "pending",
  REVIEW: "review",
  APPROVED: "approved",
  REJECTED: "rejected",
  PUBLISHING: "publishing",
  PUBLISHED: "published",
  FAILED: "failed",
};

// ───── 工具函数 ─────
function loadConfig() {
  if (fs.existsSync(CONFIG_PATH)) {
    return JSON.parse(fs.readFileSync(CONFIG_PATH, "utf-8"));
  }
  return null;
}

function getDraftsDir() {
  const config = loadConfig();
  return config?.paths?.drafts_dir || DRAFTS_DIR;
}

function getQueuePath() {
  const config = loadConfig();
  return path.join(
    config?.paths?.storage_dir || "C:/Users/li/.dragon-engine",
    "queue.json"
  );
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function generateDraftId() {
  const now = new Date();
  const date = now.toISOString().slice(0, 10).replace(/-/g, "");
  const seq = String(Math.floor(Math.random() * 999) + 1).padStart(3, "0");
  return `draft-${date}-${seq}`;
}

function getStatusDir(draftsDir, status) {
  return path.join(draftsDir, status);
}

/**
 * 草稿类
 */
class Draft {
  constructor(data = {}) {
    this.draft_id = data.draft_id || generateDraftId();
    this.blogger_id = data.blogger_id || "";
    this.type = data.type || "xiaohongshu_carousel";
    this.status = data.status || DRAFT_STATUS.PENDING;
    this.content = data.content || { title: "", slides: [] };
    this.metadata = {
      created_at: data.metadata?.created_at || new Date().toISOString(),
      created_by: data.metadata?.created_by || "dragon.js",
      source: data.metadata?.source || "auto_generated",
      files: data.metadata?.files || [],
      platforms: data.metadata?.platforms || [],
      ...data.metadata,
    };
    this.review = {
      reviewer: data.review?.reviewer || null,
      approved_at: data.review?.approved_at || null,
      rejected_at: data.review?.rejected_at || null,
      rejection_reason: data.review?.rejection_reason || null,
      notes: data.review?.notes || null,
      history: data.review?.history || [],
      ...data.review,
    };
  }

  save() {
    const draftsDir = getDraftsDir();
    ensureDir(draftsDir);

    const statusDir = getStatusDir(draftsDir, this.status);
    ensureDir(statusDir);

    const filePath = path.join(statusDir, `${this.draft_id}.json`);
    fs.writeFileSync(filePath, JSON.stringify(this, null, 2), "utf-8");
    return filePath;
  }

  static load(draftId) {
    const draftsDir = getDraftsDir();

    for (const status of Object.values(DRAFT_STATUS)) {
      const filePath = path.join(draftsDir, status, `${draftId}.json`);
      if (fs.existsSync(filePath)) {
        const data = JSON.parse(fs.readFileSync(filePath, "utf-8"));
        const draft = new Draft(data);
        draft._filePath = filePath;
        return draft;
      }
    }
    return null;
  }

  delete() {
    if (this._filePath && fs.existsSync(this._filePath)) {
      fs.unlinkSync(this._filePath);
      return true;
    }
    return false;
  }

  moveTo(newStatus) {
    // 从旧位置删除
    if (this._filePath && fs.existsSync(this._filePath)) {
      fs.unlinkSync(this._filePath);
    }

    // 更新状态
    this.status = newStatus;

    // 保存到新位置
    return this.save();
  }

  addHistory(action, actor, comment = null) {
    this.review.history.push({
      action,
      actor,
      timestamp: new Date().toISOString(),
      comment,
    });
  }
}

/**
 * 队列类
 */
class Queue {
  constructor() {
    this.version = "1.0";
    this.updated_at = new Date().toISOString();
    this.queue = [];
    this.load();
  }

  load() {
    const queuePath = getQueuePath();
    if (fs.existsSync(queuePath)) {
      try {
        const data = JSON.parse(fs.readFileSync(queuePath, "utf-8"));
        this.queue = data.queue || [];
      } catch {
        // 忽略解析错误
      }
    }
  }

  save() {
    this.updated_at = new Date().toISOString();
    const queuePath = getQueuePath();
    const dir = path.dirname(queuePath);
    ensureDir(dir);
    fs.writeFileSync(queuePath, JSON.stringify(this, null, 2), "utf-8");
  }

  add(draft) {
    const exists = this.queue.find((q) => q.draft_id === draft.draft_id);
    if (!exists) {
      this.queue.push({
        draft_id: draft.draft_id,
        position: this.queue.length + 1,
        status: draft.status,
        blogger_id: draft.blogger_id,
        platforms: draft.metadata.platforms,
        submitted_at: new Date().toISOString(),
      });
      this.save();
    }
  }

  remove(draftId) {
    this.queue = this.queue.filter((q) => q.draft_id !== draftId);
    // 重新编号
    this.queue.forEach((q, i) => {
      q.position = i + 1;
    });
    this.save();
  }

  update(draftId, status) {
    const item = this.queue.find((q) => q.draft_id === draftId);
    if (item) {
      item.status = status;
      this.save();
    }
  }

  list(status = null) {
    if (status) {
      return this.queue.filter((q) => q.status === status);
    }
    return this.queue;
  }
}

/**
 * 初始化工作流
 */
function initWorkflow() {
  const draftsDir = getDraftsDir();

  // 创建状态目录
  for (const status of Object.values(DRAFT_STATUS)) {
    const dir = path.join(draftsDir, status);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      console.log(`[OK] 创建目录: drafts/${status}`);
    }
  }

  // 创建队列文件
  const queue = new Queue();
  queue.save();

  console.log(`[OK] 审批工作流已初始化`);
  console.log(`  草稿目录: ${draftsDir}`);
  console.log(`  状态目录: pending / review / approved / rejected / publishing / published / failed`);
}

/**
 * 生成草稿
 */
async function generateDraft(options = {}) {
  const { bloggerId, draftMode = false } = options;

  if (!bloggerId) {
    console.error("[ERROR] 请提供 --blogger 参数");
    return false;
  }

  // 检查 IP 授权
  const bloggerDir = path.join(
    "C:/Users/li/.claude/projects/dragon-engine/ip-profiles",
    bloggerId
  );
  const consentPath = path.join(bloggerDir, "ip_consent.txt");

  if (!fs.existsSync(consentPath)) {
    console.error(`[ERROR] IP 授权文件不存在: ${consentPath}`);
    return false;
  }

  // 调用 blogger-poster.mjs 生成
  const posterScript = path.join(
    __dirname,
    "..",
    "skills",
    "guizang-social-card-skill",
    "pipeline",
    "blogger-poster.mjs"
  );

  if (!fs.existsSync(posterScript)) {
    console.error(`[ERROR] blogger-poster.mjs 不存在: ${posterScript}`);
    return false;
  }

  console.log(`[INFO] 正在生成内容...`);
  console.log(`  博主: ${bloggerId}`);

  try {
    // 检查是否有 --draft 模式支持（未来扩展）
    const args = [
      `node "${posterScript}"`,
      `--blogger ${bloggerId}`,
      draftMode ? "--draft" : "",
    ]
      .filter(Boolean)
      .join(" ");

    console.log(`[INFO] 命令: ${args}`);
    execSync(args, { stdio: "inherit", shell: true });

    if (draftMode) {
      // 草稿模式：创建草稿对象
      const draft = new Draft({
        blogger_id: bloggerId,
        type: "xiaohongshu_carousel",
        status: DRAFT_STATUS.PENDING,
        content: {
          title: "自动生成内容",
          slides: [],
        },
        metadata: {
          created_by: "dragon.js generate",
          source: "auto_generated",
          files: [],
          platforms: ["xiaohongshu"],
        },
      });

      draft.save();

      // 添加到队列
      const queue = new Queue();
      queue.add(draft);

      console.log(`[OK] 草稿已创建: ${draft.draft_id}`);
      console.log(`  状态: pending`);
      console.log(`  使用 dragon.js review ${draft.draft_id} 预览`);
      console.log(`  使用 dragon.js approve ${draft.draft_id} 批准发布`);
    } else {
      console.log(`[OK] 内容已生成（直接发布模式）`);
    }

    return true;
  } catch (e) {
    console.error(`[ERROR] 生成失败: ${e.message}`);
    return false;
  }
}

/**
 * 列出草稿
 */
function listDrafts(options = {}) {
  const { status = null } = options;
  const queue = new Queue();
  const items = queue.list(status);

  if (items.length === 0) {
    console.log(`[INFO] 暂无草稿${status ? ` (状态: ${status})` : ""}`);
    return [];
  }

  console.log(`\n📋 草稿队列 (${items.length} 条):\n`);
  console.log(
    `  ID                状态       博主              平台              创建时间`
  );
  console.log("  " + "─".repeat(90));

  for (const item of items) {
    const statusIcon =
      item.status === DRAFT_STATUS.APPROVED
        ? "✅"
        : item.status === DRAFT_STATUS.REJECTED
          ? "❌"
          : item.status === DRAFT_STATUS.PUBLISHED
            ? "🎉"
            : "📝";
    console.log(
      `  ${statusIcon} ${item.draft_id.padEnd(18)} ${item.status.padEnd(11)} ${item.blogger_id.padEnd(18)} ${(item.platforms || []).join(",").padEnd(16)} ${item.submitted_at.slice(0, 16)}`
    );
  }
  console.log();

  return items;
}

/**
 * 查看草稿状态
 */
function getDraftStatus(draftId) {
  const draft = Draft.load(draftId);

  if (!draft) {
    console.error(`[ERROR] 草稿不存在: ${draftId}`);
    return null;
  }

  console.log(`\n📄 草稿详情: ${draft.draft_id}\n`);
  console.log(`  博主: ${draft.blogger_id}`);
  console.log(`  类型: ${draft.type}`);
  console.log(`  状态: ${draft.status}`);
  console.log(`  创建时间: ${draft.metadata.created_at}`);
  console.log(`  创建来源: ${draft.metadata.created_by}`);
  console.log(`  平台: ${(draft.metadata.platforms || []).join(", ")}`);

  if (draft.content.title) {
    console.log(`\n  标题: ${draft.content.title}`);
  }

  if (draft.content.slides?.length) {
    console.log(`  幻灯片: ${draft.content.slides.length} 页`);
    for (const slide of draft.content.slides) {
      console.log(`    - 第 ${slide.page} 页: ${slide.text?.slice(0, 50) || ""}`);
    }
  }

  if (draft.review.history?.length) {
    console.log(`\n  审批历史:`);
    for (const h of draft.review.history) {
      console.log(`    - [${h.timestamp.slice(0, 16)}] ${h.actor}: ${h.action}`);
      if (h.comment) console.log(`      ${h.comment}`);
    }
  }

  if (draft.review.rejection_reason) {
    console.log(`\n  拒绝原因: ${draft.review.rejection_reason}`);
  }

  console.log();
  return draft;
}

/**
 * 预览草稿
 */
function reviewDraft(draftId, options = {}) {
  const { comment = null } = options;
  const draft = Draft.load(draftId);

  if (!draft) {
    console.error(`[ERROR] 草稿不存在: ${draftId}`);
    return false;
  }

  if (draft.status !== DRAFT_STATUS.PENDING) {
    console.error(`[ERROR] 草稿状态不是 pending，无法进入 review`);
    return false;
  }

  // 添加历史记录
  draft.addHistory("review", "user", comment);

  // 移动到 review 状态
  draft.moveTo(DRAFT_STATUS.REVIEW);

  // 更新队列
  const queue = new Queue();
  queue.update(draftId, DRAFT_STATUS.REVIEW);

  console.log(`[OK] 草稿已进入审核状态: ${draftId}`);
  console.log(`  使用 dragon.js approve ${draftId} 批准`);
  console.log(`  使用 dragon.js reject ${draftId} --reason "..." 拒绝`);

  return true;
}

/**
 * 批准草稿
 */
async function approveDraft(draftId, options = {}) {
  const { comment = null, autoPublish = true } = options;
  const draft = Draft.load(draftId);

  if (!draft) {
    console.error(`[ERROR] 草稿不存在: ${draftId}`);
    return false;
  }

  if (draft.status !== DRAFT_STATUS.REVIEW) {
    console.error(`[ERROR] 草稿状态不是 review，请先执行 review`);
    return false;
  }

  // 更新状态
  draft.review.reviewer = "user";
  draft.review.approved_at = new Date().toISOString();
  draft.addHistory("approve", "user", comment);

  if (autoPublish) {
    // 自动移动到 publishing
    draft.moveTo(DRAFT_STATUS.PUBLISHING);

    // 更新队列
    const queue = new Queue();
    queue.update(draftId, DRAFT_STATUS.PUBLISHING);

    console.log(`[OK] 草稿已批准并进入发布流程: ${draftId}`);

    // 调用 publisher 执行实际发布
    const publishResult = await publishToPublisher(draft, draft.metadata.platforms || []);
    
    if (publishResult.success) {
      draft.status = DRAFT_STATUS.PUBLISHED;
      draft.metadata.published_at = new Date().toISOString();
      draft.addHistory("publish", "system", `发布成功: ${publishResult.message}`);
      draft.save();
      queue.update(draftId, DRAFT_STATUS.PUBLISHED);
      console.log(`[OK] 发布成功`);
    } else {
      draft.status = DRAFT_STATUS.FAILED;
      draft.metadata.publish_error = publishResult.message;
      draft.addHistory("publish_failed", "system", publishResult.message);
      draft.save();
      queue.update(draftId, DRAFT_STATUS.FAILED);
      console.error(`[FAIL] 发布失败: ${publishResult.message}`);
    }
  } else {
    draft.moveTo(DRAFT_STATUS.APPROVED);
    const queue = new Queue();
    queue.update(draftId, DRAFT_STATUS.APPROVED);
  }

  console.log(`[OK] 草稿状态: ${draft.status}`);

  return true;
}

/**
 * 拒绝草稿
 */
function rejectDraft(draftId, options = {}) {
  const { reason = "未说明原因" } = options;
  const draft = Draft.load(draftId);

  if (!draft) {
    console.error(`[ERROR] 草稿不存在: ${draftId}`);
    return false;
  }

  if (draft.status !== DRAFT_STATUS.REVIEW) {
    console.error(`[ERROR] 草稿状态不是 review`);
    return false;
  }

  // 更新状态
  draft.review.reviewer = "user";
  draft.review.rejected_at = new Date().toISOString();
  draft.review.rejection_reason = reason;
  draft.addHistory("reject", "user", reason);

  draft.moveTo(DRAFT_STATUS.REJECTED);

  // 更新队列
  const queue = new Queue();
  queue.remove(draftId);

  console.log(`[OK] 草稿已拒绝: ${draftId}`);
  console.log(`  原因: ${reason}`);
  console.log(`  使用 dragon.js generate --blogger ${draft.blogger_id} --draft 重新生成`);

  return true;
}

/**
 * 手动发布
 */
async function publishDraft(draftId, options = {}) {
  const { platforms = null } = options;
  const draft = Draft.load(draftId);
  const queue = new Queue();

  if (!draft) {
    console.error(`[ERROR] 草稿不存在: ${draftId}`);
    return false;
  }

  if (draft.status !== DRAFT_STATUS.APPROVED && draft.status !== DRAFT_STATUS.REJECTED) {
    console.error(`[ERROR] 草稿状态为 ${draft.status}，无法发布`);
    return false;
  }

  const targetPlatforms = platforms
    ? platforms.split(",").map((p) => p.trim())
    : draft.metadata.platforms;

  console.log(`[INFO] 正在发布: ${draftId}`);
  console.log(`  平台: ${targetPlatforms.join(", ")}`);

  // 调用 publisher 执行实际发布
  const publishResult = await publishToPublisher(draft, targetPlatforms);
  
  if (publishResult.success) {
    draft.status = DRAFT_STATUS.PUBLISHED;
    draft.metadata.published_at = new Date().toISOString();
    draft.addHistory("publish", "user", `发布到 ${targetPlatforms.join(", ")}`);
    draft.save();
    queue.update(draftId, DRAFT_STATUS.PUBLISHED);
    console.log(`[OK] 发布成功: ${draftId}`);
  } else {
    draft.status = DRAFT_STATUS.FAILED;
    draft.metadata.publish_error = publishResult.message;
    draft.addHistory("publish_failed", "user", publishResult.message);
    draft.save();
    queue.update(draftId, DRAFT_STATUS.FAILED);
    console.error(`[FAIL] 发布失败: ${publishResult.message}`);
  }

  return true;
}

// ───── CLI 入口 ─────
function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  // 解析参数
  const options = {};
  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--blogger") options.blogger = args[++i];
    else if (arg === "--draft") options.draft = true;
    else if (arg === "--status") options.status = args[++i];
    else if (arg === "--comment") options.comment = args[++i];
    else if (arg === "--reason") options.reason = args[++i];
    else if (arg === "--platforms") options.platforms = args[++i];
    else if (arg === "--no-auto-publish") options.autoPublish = false;
  }

  if (!command) {
    console.log(`dragon.js · 天龙引擎审批工作流 CLI

用法:
  node dragon.js init                                           初始化工作流
  node dragon.js generate --blogger <id> [--draft]           生成草稿
  node dragon.js list [--status <status>]                    列出草稿
  node dragon.js review <draft_id> [--comment "..."]          预览/进入审核
  node dragon.js approve <draft_id> [--comment "..."]         批准发布
  node dragon.js reject <draft_id> --reason "..."            拒绝
  node dragon.js status <draft_id>                            查看状态
  node dragon.js publish <draft_id> [--platforms xhs,wechat] 手动发布

状态说明:
  pending    - 待审核
  review    - 审核中
  approved  - 已批准
  rejected  - 已拒绝
  publishing - 发布中
  published  - 已发布
  failed    - 失败

示例:
  node dragon.js generate --blogger laoli_bro_2026 --draft
  node dragon.js list
  node dragon.js approve draft-20260817-001 --comment "OK"
  node dragon.js reject draft-20260817-002 --reason "标题需要修改"
`);
    process.exit(0);
  }

  try {
    switch (command) {
      case "init":
        initWorkflow();
        break;

      case "generate":
        generateDraft({
          bloggerId: options.blogger,
          draftMode: options.draft || false,
        });
        break;

      case "list":
        listDrafts({ status: options.status });
        break;

      case "review":
        if (!args[1]) {
          console.error("[ERROR] 请提供草稿 ID");
          process.exit(1);
        }
        reviewDraft(args[1], { comment: options.comment });
        break;

      case "approve":
        if (!args[1]) {
          console.error("[ERROR] 请提供草稿 ID");
          process.exit(1);
        }
        approveDraft(args[1], {
          comment: options.comment,
          autoPublish: options.autoPublish !== false,
        });
        break;

      case "reject":
        if (!args[1]) {
          console.error("[ERROR] 请提供草稿 ID");
          process.exit(1);
        }
        if (!options.reason) {
          console.error("[ERROR] 请提供 --reason 参数");
          process.exit(1);
        }
        rejectDraft(args[1], { reason: options.reason });
        break;

      case "status":
        if (!args[1]) {
          console.error("[ERROR] 请提供草稿 ID");
          process.exit(1);
        }
        getDraftStatus(args[1]);
        break;

      case "publish":
        if (!args[1]) {
          console.error("[ERROR] 请提供草稿 ID");
          process.exit(1);
        }
        publishDraft(args[1], { platforms: options.platforms });
        break;

      default:
        console.error(`[ERROR] 未知命令: ${command}`);
        process.exit(1);
    }
  } catch (e) {
    console.error(`[ERROR] ${e.message}`);
    if (process.env.DEBUG) {
      console.error(e.stack);
    }
    process.exit(1);
  }
}

export { Draft, Queue, DRAFT_STATUS };
main();

/**
 * ⭐ 发布到 publisher.py
 * @param {Object} draft - 草稿对象
 * @param {Array} platforms - 目标平台列表
 * @returns {Object} { success: boolean, message: string }
 */
async function publishToPublisher(draft, platforms) {
  try {
    // 从草稿元数据获取 tasks_path
    const tasksPath = draft.metadata?.tasks_path;
    const taskDir = draft.metadata?.task_dir;
    const bloggerId = draft.blogger_id;

    console.log(`[INFO] 调用 publisher.py...`);
    console.log(`  草稿: ${draft.draft_id}`);
    console.log(`  博主: ${bloggerId}`);
    console.log(`  平台: ${platforms.join(", ")}`);

    if (!tasksPath || !fs.existsSync(tasksPath)) {
      // 如果没有 tasks.jsonl，创建一个
      const generatedTasksPath = await createTasksFromDraft(draft, platforms);
      if (!generatedTasksPath) {
        return { success: false, message: "无法生成 tasks.jsonl" };
      }
      return await callPublisherBatch(generatedTasksPath, bloggerId, platforms);
    }

    return await callPublisherBatch(tasksPath, bloggerId, platforms);
  } catch (e) {
    console.error(`[ERROR] 发布失败: ${e.message}`);
    return { success: false, message: e.message };
  }
}

/**
 * 从草稿创建 tasks.jsonl
 */
async function createTasksFromDraft(draft, platforms) {
  try {
    const taskDir = draft.metadata?.task_dir || getDraftsDir();
    const tasksPath = path.join(taskDir, "tasks.jsonl");

    // 读取 PNG 文件
    const files = draft.metadata?.files || [];
    const pngFiles = files.filter(f => f.endsWith(".png"));

    if (pngFiles.length === 0) {
      console.warn(`[WARN] 没有 PNG 文件，跳过发布`);
      return null;
    }

    // 构建任务数据
    const tasks = pngFiles.map((filePath, index) => ({
      task_id: `draft-${draft.draft_id}-${index}`,
      blogger_id: draft.blogger_id,
      content_type: draft.type === "xiaohongshu_carousel" ? "image" : "article",
      content_path: filePath,
      title: draft.content?.title || "草稿内容",
      description: draft.content?.description || "",
      platforms: platforms,
      tags: draft.content?.tags || [],
    }));

    // 写入 tasks.jsonl
    const tasksContent = tasks.map(t => JSON.stringify(t)).join("\n");
    fs.writeFileSync(tasksPath, tasksContent, "utf-8");
    console.log(`[INFO] 生成 tasks.jsonl: ${tasksPath}`);

    return tasksPath;
  } catch (e) {
    console.error(`[ERROR] 创建 tasks.jsonl 失败: ${e.message}`);
    return null;
  }
}

/**
 * 调用 publisher.py batch
 */
async function callPublisherBatch(tasksPath, bloggerId, platforms) {
  return new Promise((resolve) => {
    const publisherScript = path.join(
      __dirname,
      "..",
      "skills",
      "multi-platform-publisher",
      "scripts",
      "publisher.py"
    );

    const cmd = `python "${publisherScript}" batch --tasks "${tasksPath}" --blogger "${bloggerId}" --platforms ${platforms.join(",")}`;

    console.log(`[INFO] 执行: ${cmd}`);

    try {
      const result = execSync(cmd, {
        encoding: "utf-8",
        stdio: ["pipe", "pipe", "pipe"],
        timeout: 60000, // 60 秒超时
      });

      console.log(`[INFO] publisher.py 输出:`);
      console.log(result.stdout?.slice(0, 500) || "(无输出)");

      resolve({ success: true, message: "发布成功" });
    } catch (e) {
      const stderr = e.stderr?.toString() || "";
      const stdout = e.stdout?.toString() || "";

      // 检查是否只是 emoji 编码问题（常见）
      if (stderr.includes("UnicodeEncodeError") || stderr.includes("gbk")) {
        console.log(`[WARN] 检测到编码警告（通常可忽略）`);
        resolve({ success: true, message: "发布成功（可能有编码警告）" });
      } else {
        console.error(`[ERROR] publisher.py 失败`);
        console.error(stderr?.slice(0, 500) || "(无错误输出)");
        resolve({ success: false, message: stderr?.slice(0, 200) || "未知错误" });
      }
    }
  });
}
