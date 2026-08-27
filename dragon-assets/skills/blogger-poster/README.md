# blogger-poster · 博主海报发布器

> 8维博主全息 → 小红书/公众号 PNG → 多平台一键发布

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](../../SKILL.md)
[![Platform](https://img.shields.io/badge/platform-9%E5%B9%B3%E5%8F%B0-green.svg)](#-支持的平台)
[![License](https://img.shields.io/badge/license-AGPL--3.0-orange.svg)](../../LICENSE)

---

## 🚀 快速开始

### 1. 发布单个博主

```bash
node pipeline/blogger-poster.mjs --blogger <blogger_id>
```

### 2. 指定平台

```bash
node pipeline/blogger-poster.mjs --blogger <blogger_id> --platforms xiaohongshu,wechat
```

### 3. 草稿审批模式

```bash
node pipeline/blogger-poster.mjs --blogger <blogger_id> --draft
```

### 4. 批量发布

```bash
node pipeline/blogger-poster.mjs --all --platforms xiaohongshu
```

---

## 📋 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 加载博主全息                                            │
│    └── ip_profile_8dim.json / ip_profile_9dim.json          │
├─────────────────────────────────────────────────────────────┤
│ 2. IP授权三重护栏                                           │
│    ├── 声纹授权                                            │
│    ├── IP形象授权                                          │
│    └── 有效期检查                                          │
├─────────────────────────────────────────────────────────────┤
│ 3. 调色板选择                                              │
│    ├── 第9维: design_style                                │
│    └── 自动推断: color_palette                             │
├─────────────────────────────────────────────────────────────┤
│ 4. 出图 → output/*.png                                   │
├─────────────────────────────────────────────────────────────┤
│ 5. 发布 → publisher.db                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🖥️ 支持的平台

| 平台 | 标识 | 类型 | QPS | 水印 |
|------|------|------|-----|------|
| 小红书 | `xiaohongshu` | 图片 | 3 | ✅ |
| 微信公众号 | `wechat` | 文章 | 1 | ❌ |
| 抖音 | `douyin` | 视频 | 5 | ✅ |
| TikTok | `tiktok` | 视频 | 5 | ✅ |
| 视频号 | `shipinhao` | 视频 | 2 | ✅ |
| B站 | `bilibili` | 视频 | 2 | ❌ |
| 快手 | `kuaishou` | 视频 | 4 | ✅ |
| 微博 | `weibo` | 图片 | 10 | ❌ |
| YouTube | `youtube` | 视频 | 1 | ❌ |

---

## 🔒 质量门禁

### IP授权三重护栏

| 检查项 | 类型 | 说明 |
|--------|------|------|
| 声纹授权 | HARD | 必须提供 |
| IP形象授权 | HARD | 必须提供 |
| 授权过期 | HARD | 过期阻断 |
| 授权<30天 | SOFT | 警告 |

### 发布保护

- **内容去重**: SHA256 指纹
- **限流**: Token Bucket
- **重试**: 指数退避 (0.1s → 0.2s → 0.4s)

---

## 📁 目录结构

```
blogger-poster/
├── SKILL.md              # 主 Skill 文件
├── README.md             # 本文件
├── pipeline/
│   └── blogger-poster.mjs   # 核心脚本
├── references/
│   └── publish-workflow.md  # 工作流详解
└── commands/
    └── blogger-poster.md    # 命令文档
```

---

## 📊 输出结构

```
local-tests/<slug>/
├── index.html          # HTML预览
├── pages.jsonl         # Page计划
├── tasks.jsonl         # 发布任务
└── output/
    ├── xhs-01-xxx.png   # 小红书图文
    ├── xhs-02-xxx.png
    └── wechat-xxx.png    # 公众号封面
```

---

## ⚙️ 配置

### 路径配置

| 变量 | 默认值 |
|------|--------|
| `SKILL_ROOT` | `skills/blogger-poster/` |
| `IP_PROFILES_DIR` | `C:/Users/li/.claude/ip-profiles/` |
| `REGISTRY_DB` | `C:/Users/li/.claude/skills/blogger-fingerprint-registry/registry.db` |
| `PUBLISHER_DIR` | `C:/Users/li/.claude/skills/multi-platform-publisher/` |
| `DRAFTS_DIR` | `C:/Users/li/.dragon-engine/drafts/` |

### 数据库

**publisher.db** 位置: `C:/Users/li/.claude/skills/multi-platform-publisher/publisher.db`

---

## 🔧 依赖

### 运行时

- **Node.js**: 22.5+
- **Python**: 3.8+

### 依赖模块

- `node:sqlite` (内置)
- `publisher.py` (multi-platform-publisher)

---

## 📚 相关资源

- [guizang-social-card-skill](../guizang-social-card-skill/) - 社交卡片渲染
- [multi-platform-publisher](../multi-platform-publisher/) - 多平台发布器
- [blogger-fingerprint-registry](../blogger-fingerprint-registry/) - 博主指纹库

---

## 📄 许可证

AGPL-3.0

---

**维护者**: 天龙引擎团队
**版本**: v1.0.0
**更新**: 2026-08-18
