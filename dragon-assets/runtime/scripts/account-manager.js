#!/usr/bin/env node
/**
 * account-manager.js · P1 项目隔离增强
 * 博主发布账户配置管理器
 *
 * 用法：
 *   node account-manager.js init --blogger <id>                         初始化账户配置结构
 *   node account-manager.js list --blogger <id>                        列出所有账户
 *   node account-manager.js add --blogger <id> --platform <platform> 添加账户
 *   node account-manager.js remove --blogger <id> --platform <platform> 移除账户
 *   node account-manager.js get --blogger <id> --platform <platform>   获取账户详情
 *   node account-manager.js enable --blogger <id> --platform <platform> 启用账户
 *   node account-manager.js disable --blogger <id> --platform <platform> 禁用账户
 *
 * 示例：
 *   node account-manager.js init --blogger laoli_bro_2026
 *   node account-manager.js add --blogger laoli_bro_2026 --platform xiaohongshu
 *   node account-manager.js list --blogger laoli_bro_2026
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import crypto from "node:crypto";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ───── 路径常量 ─────
const CONFIG_PATH = "C:/Users/li/.dragon-engine/config.json";
const IP_PROFILES_BASE = "C:/Users/li/.claude/projects/dragon-engine/ip-profiles";
const ENCRYPTION_KEY_PATH = "C:/Users/li/.dragon-engine/.account-key";

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

/**
 * 简单的加密/解密（用于敏感数据）
 * 注意：实际生产环境应使用更安全的加密方案
 */
class SimpleCrypto {
  constructor() {
    this.key = this.loadKey();
  }

  loadKey() {
    if (fs.existsSync(ENCRYPTION_KEY_PATH)) {
      return fs.readFileSync(ENCRYPTION_KEY_PATH);
    }
    // 生成新密钥
    const key = crypto.randomBytes(32);
    const dir = path.dirname(ENCRYPTION_KEY_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(ENCRYPTION_KEY_PATH, key);
    return key;
  }

  encrypt(text) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv("aes-256-cbc", this.key, iv);
    let encrypted = cipher.update(text, "utf8", "hex");
    encrypted += cipher.final("hex");
    return iv.toString("hex") + ":" + encrypted;
  }

  decrypt(encrypted) {
    try {
      const [ivHex, encryptedHex] = encrypted.split(":");
      const iv = Buffer.from(ivHex, "hex");
      const decipher = crypto.createDecipheriv("aes-256-cbc", this.key, iv);
      let decrypted = decipher.update(encryptedHex, "hex", "utf8");
      decrypted += decipher.final("utf8");
      return decrypted;
    } catch {
      return null;
    }
  }
}

/**
 * 账户索引
 */
class AccountIndex {
  constructor(bloggerId) {
    this.bloggerId = bloggerId;
    this.bloggerDir = getBloggerDir(bloggerId);
    this.accountsDir = path.join(this.bloggerDir, "publish-accounts");
    this.indexPath = path.join(this.accountsDir, "_index.json");
    this.data = this.load();
    this.crypto = new SimpleCrypto();
  }

  load() {
    if (fs.existsSync(this.indexPath)) {
      try {
        return JSON.parse(fs.readFileSync(this.indexPath, "utf-8"));
      } catch {
        return this.createDefault();
      }
    }
    return this.createDefault();
  }

  createDefault() {
    return {
      version: "1.0",
      blogger_id: this.bloggerId,
      accounts: [],
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

  addAccount(account) {
    const existing = this.data.accounts.findIndex(
      (a) => a.platform === account.platform
    );
    if (existing >= 0) {
      this.data.accounts[existing] = { ...this.data.accounts[existing], ...account };
    } else {
      this.data.accounts.push(account);
    }
    this.save();
  }

  removeAccount(platform) {
    this.data.accounts = this.data.accounts.filter((a) => a.platform !== platform);
    // 同时删除配置文件
    const configPath = path.join(this.accountsDir, `${platform}.json`);
    if (fs.existsSync(configPath)) {
      fs.unlinkSync(configPath);
    }
    this.save();
  }

  getAccount(platform) {
    return this.data.accounts.find((a) => a.platform === platform);
  }

  listAccounts(includeDisabled = false) {
    if (includeDisabled) {
      return this.data.accounts;
    }
    return this.data.accounts.filter((a) => a.enabled);
  }

  enableAccount(platform) {
    const account = this.getAccount(platform);
    if (account) {
      account.enabled = true;
      this.save();
      return true;
    }
    return false;
  }

  disableAccount(platform) {
    const account = this.getAccount(platform);
    if (account) {
      account.enabled = false;
      this.save();
      return true;
    }
    return false;
  }
}

/**
 * 平台默认配置模板
 */
const PLATFORM_TEMPLATES = {
  xiaohongshu: {
    name: "小红书",
    category: "image",
    qps: 3,
    max_retry: 3,
    watermark: true,
    fields: ["cookie", "xsec_token", "default_tags", "auto_watermark"],
  },
  wechat: {
    name: "公众号",
    category: "article",
    qps: 1,
    max_retry: 3,
    watermark: false,
    fields: ["app_id", "app_secret", "template_id"],
  },
  bilibili: {
    name: "B站",
    category: "video",
    qps: 2,
    max_retry: 3,
    watermark: false,
    fields: ["access_key", "access_secret", "mid"],
  },
  douyin: {
    name: "抖音",
    category: "video",
    qps: 5,
    max_retry: 3,
    watermark: true,
    fields: ["client_key", "client_secret"],
  },
  youtube: {
    name: "YouTube",
    category: "video",
    qps: 1,
    max_retry: 3,
    watermark: false,
    fields: ["api_key", "channel_id"],
  },
  tiktok: {
    name: "TikTok",
    category: "video",
    qps: 5,
    max_retry: 3,
    watermark: true,
    fields: ["access_token", "open_id"],
  },
};

/**
 * 初始化账户配置结构
 */
function initAccounts(bloggerId) {
  const bloggerDir = getBloggerDir(bloggerId);

  if (!fs.existsSync(bloggerDir)) {
    console.error(`[ERROR] 博主目录不存在: ${bloggerDir}`);
    return false;
  }

  // 创建账户配置目录
  const accountsDir = path.join(bloggerDir, "publish-accounts");
  if (!fs.existsSync(accountsDir)) {
    fs.mkdirSync(accountsDir, { recursive: true });
    console.log(`[OK] 创建目录: publish-accounts`);
  }

  // 创建索引文件
  const index = new AccountIndex(bloggerId);
  index.save();

  console.log(`[OK] 账户配置结构已初始化: ${accountsDir}`);
  console.log(`\n支持的平台:`);
  for (const [platform, config] of Object.entries(PLATFORM_TEMPLATES)) {
    console.log(`  - ${platform}: ${config.name}`);
  }
  console.log(`\n使用 add 命令添加账户配置`);

  return true;
}

/**
 * 列出账户
 */
function listAccounts(bloggerId) {
  const bloggerDir = getBloggerDir(bloggerId);

  if (!fs.existsSync(bloggerDir)) {
    console.error(`[ERROR] 博主目录不存在: ${bloggerDir}`);
    return [];
  }

  const index = new AccountIndex(bloggerId);
  const accounts = index.listAccounts();

  if (accounts.length === 0) {
    console.log(`[INFO] ${bloggerId} 暂无账户配置`);
    console.log(`  运行 add 命令添加账户`);
    return [];
  }

  console.log(`\n📋 ${bloggerId} 账户列表 (${accounts.length}):\n`);
  for (const account of accounts) {
    const status = account.enabled ? "✅" : "❌";
    const template = PLATFORM_TEMPLATES[account.platform];
    console.log(`  ${status} [${account.platform}] ${template?.name || account.platform}`);
    if (account.nickname) console.log(`       昵称: ${account.nickname}`);
    if (account.auto_publish) console.log(`       自动发布: ✅`);
    if (account.draft_before_publish) console.log(`       发布前需审批: ✅`);
    console.log();
  }

  return accounts;
}

/**
 * 添加账户
 */
function addAccount(bloggerId, platform, options = {}) {
  const bloggerDir = getBloggerDir(bloggerId);

  if (!fs.existsSync(bloggerDir)) {
    console.error(`[ERROR] 博主目录不存在: ${bloggerDir}`);
    return false;
  }

  if (!PLATFORM_TEMPLATES[platform]) {
    console.error(`[ERROR] 不支持的平台: ${platform}`);
    console.log(`  支持的平台: ${Object.keys(PLATFORM_TEMPLATES).join(", ")}`);
    return false;
  }

  // 确保目录存在
  const accountsDir = path.join(bloggerDir, "publish-accounts");
  if (!fs.existsSync(accountsDir)) {
    fs.mkdirSync(accountsDir, { recursive: true });
  }

  // 读取现有配置（如果存在）
  const configPath = path.join(accountsDir, `${platform}.json`);
  let config = {};
  if (fs.existsSync(configPath)) {
    try {
      config = JSON.parse(fs.readFileSync(configPath, "utf-8"));
    } catch {
      // 忽略解析错误
    }
  }

  // 合并配置
  config = {
    ...config,
    platform,
    blogger_id: bloggerId,
    ...options,
    updated_at: new Date().toISOString(),
  };

  // 写入配置文件
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2), "utf-8");

  // 更新索引
  const index = new AccountIndex(bloggerId);
  index.addAccount({
    platform,
    blogger_id: bloggerId,
    nickname: options.nickname || null,
    enabled: options.enabled !== false,
    auto_publish: options.auto_publish || false,
    draft_before_publish: options.draft_before_publish !== false,
    config_file: `${platform}.json`,
  });

  const template = PLATFORM_TEMPLATES[platform];
  console.log(`[OK] 账户已添加: ${platform} (${template.name})`);
  console.log(`  配置文件: ${configPath}`);
  console.log(`\n请编辑配置文件添加 API 凭证`);
  console.log(`  需要配置: ${template.fields.join(", ")}`);

  return true;
}

/**
 * 获取账户详情
 */
function getAccount(bloggerId, platform) {
  const bloggerDir = getBloggerDir(bloggerId);

  if (!fs.existsSync(bloggerDir)) {
    console.error(`[ERROR] 博主目录不存在: ${bloggerDir}`);
    return null;
  }

  const accountsDir = path.join(bloggerDir, "publish-accounts");
  const configPath = path.join(accountsDir, `${platform}.json`);

  if (!fs.existsSync(configPath)) {
    console.error(`[ERROR] 账户配置不存在: ${platform}`);
    return null;
  }

  try {
    const config = JSON.parse(fs.readFileSync(configPath, "utf-8"));
    // 隐藏敏感字段
    const safeConfig = { ...config };
    for (const key of Object.keys(safeConfig)) {
      if (/secret|key|token|password/i.test(key) && safeConfig[key]) {
        safeConfig[key] = "***MASKED***";
      }
    }
    console.log(JSON.stringify(safeConfig, null, 2));
    return config;
  } catch (e) {
    console.error(`[ERROR] 配置文件解析失败: ${e.message}`);
    return null;
  }
}

/**
 * 移除账户
 */
function removeAccount(bloggerId, platform) {
  const bloggerDir = getBloggerDir(bloggerId);

  if (!fs.existsSync(bloggerDir)) {
    console.error(`[ERROR] 博主目录不存在: ${bloggerDir}`);
    return false;
  }

  const index = new AccountIndex(bloggerId);
  const account = index.getAccount(platform);

  if (!account) {
    console.error(`[ERROR] 账户不存在: ${platform}`);
    return false;
  }

  // 删除配置文件
  const accountsDir = path.join(bloggerDir, "publish-accounts");
  const configPath = path.join(accountsDir, `${platform}.json`);
  if (fs.existsSync(configPath)) {
    fs.unlinkSync(configPath);
  }

  // 从索引移除
  index.removeAccount(platform);

  console.log(`[OK] 账户已移除: ${platform}`);
  return true;
}

/**
 * 启用账户
 */
function enableAccount(bloggerId, platform) {
  const bloggerDir = getBloggerDir(bloggerId);

  if (!fs.existsSync(bloggerDir)) {
    console.error(`[ERROR] 博主目录不存在: ${bloggerDir}`);
    return false;
  }

  const index = new AccountIndex(bloggerId);
  if (!index.enableAccount(platform)) {
    console.error(`[ERROR] 账户不存在: ${platform}`);
    return false;
  }

  console.log(`[OK] 账户已启用: ${platform}`);
  return true;
}

/**
 * 禁用账户
 */
function disableAccount(bloggerId, platform) {
  const bloggerDir = getBloggerDir(bloggerId);

  if (!fs.existsSync(bloggerDir)) {
    console.error(`[ERROR] 博主目录不存在: ${bloggerDir}`);
    return false;
  }

  const index = new AccountIndex(bloggerId);
  if (!index.disableAccount(platform)) {
    console.error(`[ERROR] 账户不存在: ${platform}`);
    return false;
  }

  console.log(`[OK] 账户已禁用: ${platform}`);
  return true;
}

// ───── CLI 入口 ─────
function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  // 解析参数
  const options = {};
  let bloggerId = null;
  let platform = null;

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--blogger") bloggerId = args[++i];
    else if (arg === "--platform") platform = args[++i];
    else if (arg === "--nickname") options.nickname = args[++i];
    else if (arg === "--enabled") options.enabled = args[++i] === "true";
    else if (arg === "--auto-publish") options.auto_publish = true;
    else if (arg === "--no-draft") options.draft_before_publish = false;
  }

  if (!command) {
    console.log(`account-manager.js · 博主发布账户管理器

用法:
  node account-manager.js init --blogger <id>                          初始化账户结构
  node account-manager.js list --blogger <id>                         列出所有账户
  node account-manager.js add --blogger <id> --platform <platform>     添加账户
  node account-manager.js get --blogger <id> --platform <platform>    获取账户详情
  node account-manager.js remove --blogger <id> --platform <platform>  移除账户
  node account-manager.js enable --blogger <id> --platform <platform>  启用账户
  node account-manager.js disable --blogger <id> --platform <platform> 禁用账户

支持的平台:
  xiaohongshu - 小红书
  wechat     - 公众号
  bilibili   - B站
  douyin     - 抖音
  youtube    - YouTube
  tiktok     - TikTok

示例:
  node account-manager.js init --blogger laoli_bro_2026
  node account-manager.js add --blogger laoli_bro_2026 --platform xiaohongshu --nickname "老李兄弟"
  node account-manager.js list --blogger laoli_bro_2026
`);
    process.exit(0);
  }

  if (!bloggerId && command !== "help") {
    console.error("[ERROR] 请提供 --blogger 参数");
    process.exit(1);
  }

  try {
    switch (command) {
      case "init":
        initAccounts(bloggerId);
        break;

      case "list":
        listAccounts(bloggerId);
        break;

      case "add":
        if (!platform) {
          console.error("[ERROR] 请提供 --platform 参数");
          process.exit(1);
        }
        addAccount(bloggerId, platform, options);
        break;

      case "get":
        if (!platform) {
          console.error("[ERROR] 请提供 --platform 参数");
          process.exit(1);
        }
        getAccount(bloggerId, platform);
        break;

      case "remove":
        if (!platform) {
          console.error("[ERROR] 请提供 --platform 参数");
          process.exit(1);
        }
        removeAccount(bloggerId, platform);
        break;

      case "enable":
        if (!platform) {
          console.error("[ERROR] 请提供 --platform 参数");
          process.exit(1);
        }
        enableAccount(bloggerId, platform);
        break;

      case "disable":
        if (!platform) {
          console.error("[ERROR] 请提供 --platform 参数");
          process.exit(1);
        }
        disableAccount(bloggerId, platform);
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

export { AccountIndex, getBloggerDir, PLATFORM_TEMPLATES };
main();
