#!/usr/bin/env node
/**
 * resource-manager.js · P1 项目隔离增强
 * 博主专属资源包管理器：背景图、版式模板
 *
 * 用法：
 *   node resource-manager.js init --blogger <id>                    初始化资源包结构
 *   node resource-manager.js list --blogger <id>                   列出所有资源包
 *   node resource-manager.js add --blogger <id> --path <path>     添加资源
 *   node resource-manager.js remove --blogger <id> --pack <pack>   移除资源包
 *   node resource-manager.js get --blogger <id> --pack <pack>     获取资源包详情
 *   node resource-manager.js default --blogger <id> --pack <pack>  设置默认资源包
 *
 * 示例：
 *   node resource-manager.js init --blogger laoli_bro_2026
 *   node resource-manager.js list --blogger laoli_bro_2026
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execSync } from "node:child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ───── 路径常量 ─────
const CONFIG_PATH = "C:/Users/li/.dragon-engine/config.json";
const IP_PROFILES_BASE = "C:/Users/li/.claude/projects/dragon-engine/ip-profiles";

// ───── 工具函数 ─────
function loadConfig() {
  if (fs.existsSync(CONFIG_PATH)) {
    const content = fs.readFileSync(CONFIG_PATH, "utf-8");
    return JSON.parse(content);
  }
  return { paths: { ip_profiles_dir: IP_PROFILES_BASE } };
}

function getBloggerDir(bloggerId) {
  const config = loadConfig();
  const baseDir = config.paths?.ip_profiles_dir || IP_PROFILES_BASE;
  return path.join(baseDir, bloggerId);
}

function ensureResourcePackDir(bloggerId) {
  const bloggerDir = getBloggerDir(bloggerId);
  const resourcePackDir = path.join(bloggerDir, "resource-packs");
  if (!fs.existsSync(resourcePackDir)) {
    fs.mkdirSync(resourcePackDir, { recursive: true });
  }
  return resourcePackDir;
}

/**
 * 资源包索引
 */
class ResourceIndex {
  constructor(bloggerId) {
    this.bloggerId = bloggerId;
    this.bloggerDir = getBloggerDir(bloggerId);
    this.resourcePackDir = path.join(this.bloggerDir, "resource-packs");
    this.indexPath = path.join(this.resourcePackDir, "_index.json");
    this.data = this.load();
  }

  load() {
    if (fs.existsSync(this.indexPath)) {
      try {
        return JSON.parse(fs.readFileSync(this.indexPath, "utf-8"));
      } catch (e) {
        return this.createDefault();
      }
    }
    return this.createDefault();
  }

  createDefault() {
    return {
      version: "1.0",
      blogger_id: this.bloggerId,
      packs: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }

  save() {
    this.data.updated_at = new Date().toISOString();
    const dir = path.dirname(this.indexPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(this.indexPath, JSON.stringify(this.data, null, 2), "utf-8");
  }

  addPack(pack) {
    const existing = this.data.packs.findIndex((p) => p.id === pack.id);
    if (existing >= 0) {
      this.data.packs[existing] = { ...this.data.packs[existing], ...pack };
    } else {
      this.data.packs.push(pack);
    }
    this.save();
  }

  removePack(packId) {
    this.data.packs = this.data.packs.filter((p) => p.id !== packId);
    this.save();
  }

  getPack(packId) {
    return this.data.packs.find((p) => p.id === packId);
  }

  listPacks() {
    return this.data.packs;
  }

  getDefaultPack() {
    return this.data.packs.find((p) => p.default) || this.data.packs[0];
  }

  setDefaultPack(packId) {
    for (const p of this.data.packs) {
      p.default = p.id === packId;
    }
    this.save();
  }
}

/**
 * 初始化资源包结构
 */
function initResourcePacks(bloggerId) {
  const bloggerDir = getBloggerDir(bloggerId);

  if (!fs.existsSync(bloggerDir)) {
    console.error(`[ERROR] 博主目录不存在: ${bloggerDir}`);
    console.error(`  请先创建博主指纹档案`);
    return false;
  }

  // 创建目录结构
  const dirs = [
    "resource-packs",
    "resource-packs/backgrounds",
    "resource-packs/templates",
    "resource-packs/logos",
    "resource-packs/fonts",
    "resource-packs/stock-assets",
  ];

  for (const d of dirs) {
    const dirPath = path.join(bloggerDir, d);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
      console.log(`[OK] 创建目录: ${d}`);
    }
  }

  // 创建索引文件
  const index = new ResourceIndex(bloggerId);
  index.save();

  console.log(`[OK] 资源包结构已初始化: ${path.join(bloggerDir, "resource-packs")}`);
  return true;
}

/**
 * 列出资源包
 */
function listPacks(bloggerId) {
  const bloggerDir = getBloggerDir(bloggerId);

  if (!fs.existsSync(bloggerDir)) {
    console.error(`[ERROR] 博主目录不存在: ${bloggerDir}`);
    return [];
  }

  const index = new ResourceIndex(bloggerId);
  const packs = index.listPacks();

  if (packs.length === 0) {
    console.log(`[INFO] ${bloggerId} 暂无资源包`);
    console.log(`  运行 init 命令初始化`);
    return [];
  }

  console.log(`\n📦 ${bloggerId} 资源包列表 (${packs.length}):\n`);
  for (const pack of packs) {
    const defaultMark = pack.default ? " ⭐" : "";
    console.log(`  [${pack.type}] ${pack.id}${defaultMark}`);
    if (pack.name) console.log(`    名称: ${pack.name}`);
    if (pack.tags) console.log(`    标签: ${pack.tags.join(", ")}`);
    if (pack.count) console.log(`    资源数: ${pack.count}`);
    console.log(`    路径: ${pack.path}`);
    console.log();
  }

  return packs;
}

/**
 * 添加资源包
 */
function addPack(bloggerId, options = {}) {
  const { id, name, type, path: packPath, tags = [] } = options;

  if (!id) {
    console.error("[ERROR] 请提供 --id 参数");
    return false;
  }

  const bloggerDir = getBloggerDir(bloggerId);

  if (!fs.existsSync(bloggerDir)) {
    console.error(`[ERROR] 博主目录不存在: ${bloggerDir}`);
    return false;
  }

  // 确保资源包目录存在
  ensureResourcePackDir(bloggerId);

  // 创建资源包目录
  const resourceDir = path.join(bloggerDir, "resource-packs", id);
  if (!fs.existsSync(resourceDir)) {
    fs.mkdirSync(resourceDir, { recursive: true });
  }

  // 添加到索引
  const index = new ResourceIndex(bloggerId);
  const pack = {
    id,
    name: name || id,
    type: type || "background",
    path: packPath || `backgrounds/${id}`,
    tags,
    count: 0,
    default: index.listPacks().length === 0, // 第一个设为默认
    created_at: new Date().toISOString(),
  };

  index.addPack(pack);
  console.log(`[OK] 资源包已添加: ${id}`);
  console.log(`  类型: ${pack.type}`);
  console.log(`  路径: ${resourceDir}`);

  return true;
}

/**
 * 获取资源包详情
 */
function getPack(bloggerId, packId) {
  const bloggerDir = getBloggerDir(bloggerId);

  if (!fs.existsSync(bloggerDir)) {
    console.error(`[ERROR] 博主目录不存在: ${bloggerDir}`);
    return null;
  }

  const index = new ResourceIndex(bloggerId);
  const pack = index.getPack(packId);

  if (!pack) {
    console.error(`[ERROR] 资源包不存在: ${packId}`);
    return null;
  }

  console.log(JSON.stringify(pack, null, 2));
  return pack;
}

/**
 * 移除资源包
 */
function removePack(bloggerId, packId) {
  const bloggerDir = getBloggerDir(bloggerId);

  if (!fs.existsSync(bloggerDir)) {
    console.error(`[ERROR] 博主目录不存在: ${bloggerDir}`);
    return false;
  }

  const index = new ResourceIndex(bloggerId);
  const pack = index.getPack(packId);

  if (!pack) {
    console.error(`[ERROR] 资源包不存在: ${packId}`);
    return false;
  }

  // 从索引移除
  index.removePack(packId);

  // 删除目录（可选）
  const resourceDir = path.join(bloggerDir, "resource-packs", packId);
  if (fs.existsSync(resourceDir)) {
    console.log(`[INFO] 资源包目录保留: ${resourceDir}`);
    console.log(`  如需删除，请手动删除`);
  }

  console.log(`[OK] 资源包已移除: ${packId}`);
  return true;
}

/**
 * 设置默认资源包
 */
function setDefaultPack(bloggerId, packId) {
  const bloggerDir = getBloggerDir(bloggerId);

  if (!fs.existsSync(bloggerDir)) {
    console.error(`[ERROR] 博主目录不存在: ${bloggerDir}`);
    return false;
  }

  const index = new ResourceIndex(bloggerId);
  const pack = index.getPack(packId);

  if (!pack) {
    console.error(`[ERROR] 资源包不存在: ${packId}`);
    return false;
  }

  index.setDefaultPack(packId);
  console.log(`[OK] 默认资源包已设置: ${packId}`);
  return true;
}

/**
 * 获取背景图路径列表
 */
function getBackgroundPaths(bloggerId, packId = null) {
  const bloggerDir = getBloggerDir(bloggerId);
  const backgroundsDir = path.join(bloggerDir, "resource-packs", "backgrounds");

  if (!fs.existsSync(backgroundsDir)) {
    return [];
  }

  const packs = fs.readdirSync(backgroundsDir, { withFileTypes: true });
  const paths = [];

  for (const pack of packs) {
    if (pack.isDirectory() && (!packId || pack.name === packId)) {
      const packDir = path.join(backgroundsDir, pack.name);
      const files = fs.readdirSync(packDir);
      for (const file of files) {
        if (/\.(jpg|jpeg|png|webp)$/i.test(file)) {
          paths.push(path.join(packDir, file));
        }
      }
    }
  }

  return paths;
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
    else if (arg === "--id") options.id = args[++i];
    else if (arg === "--name") options.name = args[++i];
    else if (arg === "--type") options.type = args[++i];
    else if (arg === "--path") options.path = args[++i];
    else if (arg === "--tags") options.tags = args[++i].split(",");
    else if (arg === "--pack") options.packId = args[++i];
  }

  if (!command) {
    console.log(`resource-manager.js · 博主资源包管理器

用法:
  node resource-manager.js init --blogger <id>                    初始化资源包结构
  node resource-manager.js list --blogger <id>                   列出所有资源包
  node resource-manager.js add --blogger <id> --id <pack_id>     添加资源包
  node resource-manager.js get --blogger <id> --pack <pack_id>   获取资源包详情
  node resource-manager.js remove --blogger <id> --pack <pack_id> 移除资源包
  node resource-manager.js default --blogger <id> --pack <pack_id> 设置默认

示例:
  node resource-manager.js init --blogger laoli_bro_2026
  node resource-manager.js list --blogger laoli_bro_2026
  node resource-manager.js add --blogger laoli_bro_2026 --id coffee-shop --name "咖啡馆风" --type background
`);
    process.exit(0);
  }

  const bloggerId = options.blogger;

  if (!bloggerId && command !== "help") {
    console.error("[ERROR] 请提供 --blogger 参数");
    process.exit(1);
  }

  try {
    switch (command) {
      case "init":
        initResourcePacks(bloggerId);
        break;

      case "list":
        listPacks(bloggerId);
        break;

      case "add":
        addPack(bloggerId, options);
        break;

      case "get":
        getPack(bloggerId, options.packId);
        break;

      case "remove":
        removePack(bloggerId, options.packId);
        break;

      case "default":
        setDefaultPack(bloggerId, options.packId);
        break;

      case "backgrounds":
        console.log(JSON.stringify(getBackgroundPaths(bloggerId, options.packId), null, 2));
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

export { ResourceIndex, getBloggerDir, getBackgroundPaths };
main();
