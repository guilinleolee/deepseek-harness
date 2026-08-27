#!/usr/bin/env node
/**
 * dragon-config.js · P2 统一配置入口
 * 天龙引擎配置管理器：读写配置、获取项目、路径解析
 *
 * 用法：
 *   node dragon-config.js get <key>                    # 读取配置
 *   node dragon-config.js set <key> <value>            # 设置配置
 *   node dragon-config.js get-project <project_id>     # 获取项目配置
 *   node dragon-config.js get-active-project           # 获取当前项目
 *   node dragon-config.js list-projects                # 列出所有项目
 *   node dragon-config.js init                         # 初始化配置
 *   node dragon-config.js path <name>                 # 获取路径
 *
 * 示例：
 *   node dragon-config.js get active_project           # → laoli_bro_2026
 *   node dragon-config.js get paths.ip_profiles_dir   # → C:/Users/li/.claude/projects/dragon-engine/ip-profiles
 *   node dragon-config.js path drafts                 # → C:/Users/li/.dragon-engine/drafts
 *   node dragon-config.js list-projects               # → [laoli_bro_2026, outdoor_lily, tech_vc_bro]
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createInterface } from "node:readline";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ───── 默认配置 ─────
const DEFAULT_CONFIG = {
  version: "1.0",
  active_project: "laoli_bro_2026",
  paths: {
    storage_dir: "C:/Users/li/.dragon-engine",
    ip_profiles_dir: "C:/Users/li/.claude/projects/dragon-engine/ip-profiles",
    drafts_dir: "C:/Users/li/.dragon-engine/drafts",
    output_dir: "C:/Users/li/.dragon-engine/output",
    cache_dir: "C:/Users/li/.dragon-engine/cache",
    logs_dir: "C:/Users/li/.dragon-engine/logs",
  },
  projects: {},
  defaults: {
    design_style: null,
    color_scheme: "auto",
    quality: "high",
    review_before_publish: true,
    platforms: ["xiaohongshu"],
  },
  safety: {
    max_concurrent_tasks: 3,
    require_approval_for_publish: true,
    auto_retry_failed: true,
    max_retry_attempts: 3,
    watermark_by_default: true,
  },
  server: {
    port: 8787,
    enabled: false,
    host: "127.0.0.1",
  },
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

// ───── 路径常量 ─────
const CONFIG_PATH = "C:/Users/li/.dragon-engine/config.json";

// ───── 配置类 ─────
class DragonConfig {
  constructor(configPath = CONFIG_PATH) {
    this.configPath = configPath;
    this.config = null;
  }

  /**
   * 加载配置
   */
  load() {
    if (this.config) return this.config;

    if (fs.existsSync(this.configPath)) {
      try {
        const content = fs.readFileSync(this.configPath, "utf-8");
        this.config = JSON.parse(content);
        return this.config;
      } catch (e) {
        console.error(`[ERROR] 配置文件解析失败: ${this.configPath}`);
        console.error(`  ${e.message}`);
        process.exit(1);
      }
    }

    // 配置不存在，返回默认配置
    return DEFAULT_CONFIG;
  }

  /**
   * 保存配置
   */
  save(config = this.config) {
    const dir = path.dirname(this.configPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    config.updated_at = new Date().toISOString();
    fs.writeFileSync(
      this.configPath,
      JSON.stringify(config, null, 2),
      "utf-8"
    );
    this.config = config;
  }

  /**
   * 获取配置值
   * @param {string} key - 点分隔的路径，如 "paths.ip_profiles_dir"
   * @param {*} defaultValue - 默认值
   */
  get(key, defaultValue = undefined) {
    const config = this.load();
    const keys = key.split(".");
    let value = config;

    for (const k of keys) {
      if (value && typeof value === "object" && k in value) {
        value = value[k];
      } else {
        return defaultValue;
      }
    }

    return value !== undefined ? value : defaultValue;
  }

  /**
   * 设置配置值
   * @param {string} key - 点分隔的路径
   * @param {*} value - 新值
   */
  set(key, value) {
    const config = this.load();
    const keys = key.split(".");
    let obj = config;

    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i];
      if (!(k in obj) || typeof obj[k] !== "object") {
        obj[k] = {};
      }
      obj = obj[k];
    }

    obj[keys[keys.length - 1]] = value;
    this.save(config);
    return config;
  }

  /**
   * 获取路径
   * @param {string} name - 路径名称
   */
  getPath(name) {
    return this.get(`paths.${name}`);
  }

  /**
   * 获取项目配置
   * @param {string} projectId - 项目 ID
   */
  getProject(projectId) {
    const projects = this.get("projects", {});
    if (projectId in projects) {
      return projects[projectId];
    }
    return null;
  }

  /**
   * 获取当前活跃项目
   */
  getActiveProject() {
    const activeId = this.get("active_project");
    return this.getProject(activeId);
  }

  /**
   * 列出所有项目
   */
  listProjects() {
    const projects = this.get("projects", {});
    return Object.keys(projects).filter(
      (id) => projects[id] && projects[id].enabled
    );
  }

  /**
   * 初始化配置（首次运行）
   */
  init() {
    if (fs.existsSync(this.configPath)) {
      console.log(`[INFO] 配置已存在: ${this.configPath}`);
      console.log(`  使用 --force 强制重新初始化`);
      return false;
    }

    // 扫描 ip-profiles 目录自动发现项目
    const ipProfilesDir = this.getPath("ip_profiles_dir");
    const discoveredProjects = {};

    if (fs.existsSync(ipProfilesDir)) {
      const entries = fs.readdirSync(ipProfilesDir, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.isDirectory()) {
          const bloggerId = entry.name;
          const profilePath = path.join(ipProfilesDir, bloggerId, "ip_profile_8dim.json");

          discoveredProjects[bloggerId] = {
            enabled: true,
            priority: Object.keys(discoveredProjects).length + 1,
            default_platforms: ["xiaohongshu"],
            watermark: true,
            auto_review: false,
          };

          // 如果有 8 维指纹文件，尝试读取博主名
          if (fs.existsSync(profilePath)) {
            try {
              const profile = JSON.parse(fs.readFileSync(profilePath, "utf-8"));
              if (profile.blogger_name) {
                discoveredProjects[bloggerId].blogger_name = profile.blogger_name;
              }
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
      }
    }

    const config = {
      ...DEFAULT_CONFIG,
      projects: discoveredProjects,
      active_project: Object.keys(discoveredProjects)[0] || "laoli_bro_2026",
    };

    this.save(config);
    console.log(`[OK] 配置已初始化: ${this.configPath}`);
    console.log(`  发现 ${Object.keys(discoveredProjects).length} 个项目`);
    return true;
  }

  /**
   * 验证配置完整性
   */
  validate() {
    const config = this.load();
    const issues = [];

    // 检查必需路径
    for (const [name, p] of Object.entries(config.paths || {})) {
      if (!p) {
        issues.push(`paths.${name} 为空`);
      }
    }

    // 检查活跃项目存在
    const activeId = config.active_project;
    if (!config.projects || !config.projects[activeId]) {
      issues.push(`活跃项目 "${activeId}" 不存在`);
    }

    // 检查 IP 授权有效期
    const ipProfilesDir = config.paths?.ip_profiles_dir;
    if (ipProfilesDir && fs.existsSync(ipProfilesDir)) {
      for (const [bloggerId, project] of Object.entries(config.projects || {})) {
        if (project.enabled) {
          const consentPath = path.join(ipProfilesDir, bloggerId, "ip_consent.txt");
          if (fs.existsSync(consentPath)) {
            // TODO: 检查授权是否过期
          }
        }
      }
    }

    return {
      valid: issues.length === 0,
      issues,
    };
  }
}

// ───── CLI 入口 ─────
function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command) {
    console.log(`dragon-config.js · 天龙引擎配置管理器

用法:
  node dragon-config.js get <key>                    读取配置
  node dragon-config.js set <key> <value>          设置配置
  node dragon-config.js get-project <project_id>    获取项目配置
  node dragon-config.js get-active-project          获取当前项目
  node dragon-config.js list-projects               列出所有项目
  node dragon-config.js path <name>                获取路径
  node dragon-config.js init [--force]              初始化配置
  node dragon-config.js validate                    验证配置

示例:
  node dragon-config.js get active_project
  node dragon-config.js get paths.ip_profiles_dir
  node dragon-config.js path drafts
  node dragon-config.js list-projects
`);
    process.exit(0);
  }

  const cfg = new DragonConfig();

  try {
    switch (command) {
      case "get": {
        const key = args[1];
        if (!key) {
          console.error("[ERROR] 请提供配置键名");
          process.exit(1);
        }
        const value = cfg.get(key);
        console.log(JSON.stringify(value, null, 2));
        break;
      }

      case "set": {
        const key = args[1];
        const valueStr = args[2];
        if (!key || valueStr === undefined) {
          console.error("[ERROR] 请提供配置键名和新值");
          process.exit(1);
        }
        let value;
        try {
          value = JSON.parse(valueStr);
        } catch {
          value = valueStr;
        }
        cfg.set(key, value);
        console.log(`[OK] ${key} = ${JSON.stringify(value)}`);
        break;
      }

      case "get-project":
      case "getProject": {
        const projectId = args[1];
        if (!projectId) {
          console.error("[ERROR] 请提供项目 ID");
          process.exit(1);
        }
        const project = cfg.getProject(projectId);
        console.log(JSON.stringify(project, null, 2));
        break;
      }

      case "get-active-project":
      case "getActiveProject": {
        const project = cfg.getActiveProject();
        console.log(JSON.stringify(project, null, 2));
        break;
      }

      case "list-projects":
      case "listProjects": {
        const projects = cfg.listProjects();
        console.log(JSON.stringify(projects, null, 2));
        break;
      }

      case "path": {
        const name = args[1];
        if (!name) {
          console.error("[ERROR] 请提供路径名称");
          process.exit(1);
        }
        const p = cfg.getPath(name);
        console.log(p || "");
        break;
      }

      case "init": {
        const force = args.includes("--force");
        if (force) {
          console.log("[WARN] 强制重新初始化...");
        }
        cfg.init();
        break;
      }

      case "validate": {
        const result = cfg.validate();
        if (result.valid) {
          console.log("[OK] 配置验证通过");
        } else {
          console.log("[WARN] 配置存在问题:");
          for (const issue of result.issues) {
            console.log(`  - ${issue}`);
          }
        }
        break;
      }

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

// 导出类供其他模块使用
export { DragonConfig };

// 直接运行
main();
