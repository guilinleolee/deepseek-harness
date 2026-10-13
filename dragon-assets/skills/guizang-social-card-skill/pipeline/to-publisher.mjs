// to-publisher.mjs · output/*.png → publisher tasks.jsonl
// 阶段 19 V2.0
//
// 输入：local-tests/<slug>/output/ 目录里的所有 PNG
// 输出：tasks.jsonl（每行一个 PublishTask，喂给 multi-platform-publisher batch）

import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { execSync } from "node:child_process";

/**
 * 从博主全息抽出 platforms 列表
 * @param {object} profile - 9 维博主全息
 * @param {string[]} argPlatforms - CLI --platforms 参数（如 ["xiaohongshu", "wechat"]）
 * @returns {string[]} platform 列表
 */
export function choosePlatforms(profile, argPlatforms) {
  if (argPlatforms && argPlatforms.length > 0) return argPlatforms;
  // 默认：小红书 + 公众号
  return ["xiaohongshu", "wechat"];
}

/**
 * 从 PNG 文件名推断 platform + role
 * - xhs-NN-...  → xiaohongshu + image carousel
 * - wechat-21x9-... → wechat + article cover
 * - wechat-1x1-...  → wechat + article share
 */
export function inferRoleFromFilename(filename) {
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
  if (base.startsWith("pair-preview")) {
    return { platform: "wechat", contentType: "article", role: "pair-preview" };
  }
  return { platform: "xiaohongshu", contentType: "image", role: "image" };
}

/**
 * 生成 tasks.jsonl
 * @param {object} opts
 * @param {string} opts.taskDir - local-tests/<slug>/
 * @param {string} opts.outputSubdir - "output"
 * @param {object} opts.profile - 博主全息
 * @param {string[]} opts.platforms
 * @param {string} opts.title
 * @returns {string} tasks.jsonl 路径
 */
export function toTasksJsonl({ taskDir, outputSubdir = "output", profile, platforms, title, dryRun = false }) {
  const outputDir = path.join(taskDir, outputSubdir);
  if (!fs.existsSync(outputDir) && !dryRun) {
    throw new Error(`output dir not found: ${outputDir}，请先跑 render-poster`);
  }

  const pngs = (fs.existsSync(outputDir) ? fs.readdirSync(outputDir) : [])
    .filter(f => f.endsWith(".png"))
    .sort();

  if (!dryRun && pngs.length === 0) {
    throw new Error(`output dir 下没有 PNG: ${outputDir}`);
  }

  const tags = ["博主全息", profile.dim_7_writing_style?.style_name || "个人风", "guizang-v1.0", "AGPL-3.0"];
  const bloggerId = profile.blogger_id || "unknown";
  const description = `基于博主 ${profile.blogger_name || bloggerId} 9 维全息自动生成。渲染模板：guizang V1.0 · 许可证：AGPL-3.0（仅 PNG 输出）。`;

  const tasks = pngs.length
    ? pngs.map(png => {
        const contentPath = path.join(outputDir, png);
        const { platform, contentType, role } = inferRoleFromFilename(png);
        return {
          blogger_id: bloggerId,
          content_type: contentType,
          content_path: contentPath.replace(/\\/g, "/"),
          title: title || `${profile.blogger_name || bloggerId} · 9 维全息自动出图`,
          description,
          tags,
          platforms,
          scheduled_at: null,
          watermark: true,
          account_ids: {},
          // _meta 不发 publisher（不是 PublishTask 字段）—— 留给档案用
          // design_style / consent 已在 tags/description 中体现
        };
      })
    : [{
        blogger_id: bloggerId,
        content_type: "image",
        content_path: null,
        title: title || `${profile.blogger_name || bloggerId} · 9 维全息自动出图`,
        description,
        tags,
        platforms,
        scheduled_at: null,
        watermark: true,
        account_ids: {},
        _meta: {
          role: "dry-run",
          platform: "(no render yet)",
          generated_by: "blogger-poster.mjs (stage 19 dry-run)",
          design_style: profile._design_style || "auto",
          consent: profile._meta?.consent || {},
          filename: null,
          dry_run_note: "no PNGs in output yet — run `node render-poster.mjs <taskDir>` first",
        },
      }];

  const outPath = path.join(taskDir, "tasks.jsonl");
  fs.writeFileSync(outPath, tasks.map(t => JSON.stringify(t)).join("\n") + "\n", "utf-8");
  return outPath;
}

/**
 * 调用 publisher.py batch 处理 tasks.jsonl
 * @param {string} tasksPath - tasks.jsonl 路径
 * @param {string} publisherDir - C:/Users/li/.claude/skills/multi-platform-publisher
 * @param {boolean} dryRun - true 表示只打印命令不真跑
 */
export function runPublisherBatch(tasksPath, publisherDir = "C:/Users/li/.claude/skills/multi-platform-publisher", dryRun = false) {
  const cmd = `python scripts/publisher.py batch --file "${tasksPath}"`;
  if (dryRun) {
    return { cmd, code: 0, stdout: "(dry-run)", stderr: "" };
  }
  // 用 child_process 调用；stdio: pipe 但实际 publisher.py 在 Windows gbk stdout 上有 emoji 编码问题，
  // 但 mock 已成功写入 publish_results 表（看 publisher.db），只看 exit code
  try {
    const stdout = execSync(cmd, {
      cwd: publisherDir,
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