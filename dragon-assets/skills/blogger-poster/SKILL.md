---
name: blogger-poster 博主海报发布器
description: |
  8维博主全息 → 小红书/公众号 PNG → 多平台一键发布。
  支持草稿审批模式、--all 批量发布、IP授权三重护栏。
  整合 blogger-poster.mjs + multi-platform-publisher。
  触发: @博主发布 / blogger-poster
version: 1.0.0
category: dragon-engine-role-营销
author: 天龙引擎团队
source: dragon-engine/skills/blogger-poster/
created: 2026-08-18
dependencies:
  - guizang-social-card-skill (pipeline/)
  - multi-platform-publisher (scripts/publisher.py)
---

# 博主海报发布器 (blogger-poster)

> **天龙引擎 Skill** | V1.0.0
> **分类**: 营销
> **核心能力**: 博主全息 → PNG渲染 → 多平台发布

---

## 📋 核心职责

### 主要功能

1. **博主全息加载**
   - 加载 8维/9维 博主全息 JSON
   - IP授权三重护栏校验（声纹 + IP形象 + 有效期）

2. **智能出图**
   - 调色板自动选择（第9维 design_style / 自动推断）
   - Recipe 智能匹配
   - Page 计划抽取（小红书/公众号双轨）

3. **多平台发布**
   - 支持 9 大平台（小红书、公众号、抖音、TikTok等）
   - Token Bucket 限流
   - SHA256 内容去重
   - 指数退避重试

4. **草稿审批模式**
   - --draft 模式生成审批队列
   - 草稿预览 + 批准/拒绝

---

## 🎯 支持的平台

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

## 🚀 命令接口

### 基础发布

```bash
# 发布单个博主
/blogger-poster post --blogger <blogger_id>

# 指定平台
/blogger-poster post --blogger <blogger_id> --platforms xiaohongshu,wechat

# 草稿模式（审批后发布）
/blogger-poster post --blogger <blogger_id> --draft

# 预览模式（不执行渲染和发布）
/blogger-poster post --blogger <blogger_id> --dry-run
```

### 批量发布

```bash
# 发布所有活跃博主
/blogger-poster post --all

# 批量指定平台
/blogger-poster post --all --platforms xiaohongshu
```

### 草稿管理

```bash
# 查看待审批草稿
/blogger-poster drafts

# 审批草稿
/blogger-poster approve <draft_id>

# 拒绝草稿
/blogger-poster reject <draft_id> --reason <原因>
```

### 发布状态

```bash
# 查看发布统计
/blogger-poster stats

# 查看任务状态
/blogger-poster status --task-id <task_id>

# 内容去重查询
/blogger-poster dedup --content <file_path>
```

---

## 🔄 工作流程

### 标准发布流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 加载博主全息                                            │
│    └── ip_profile_8dim.json                                │
├─────────────────────────────────────────────────────────────┤
│ 2. IP授权三重护栏                                           │
│    ├── 声纹授权 (voice_consent_file / voice_authorized)    │
│    ├── IP形象授权 (ip_consent_file / ip_image_authorized)   │
│    └── 有效期检查 (consent_expires_at)                     │
├─────────────────────────────────────────────────────────────┤
│ 3. 调色板选择                                              │
│    ├── 第9维: registry.db → design_style                   │
│    └── 自动推断: dim_8_ip_visual.spec.color_palette        │
├─────────────────────────────────────────────────────────────┤
│ 4. Recipe匹配 + Page抽取                                    │
│    └── 输出: pages.jsonl                                   │
├─────────────────────────────────────────────────────────────┤
│ 5. 渲染出图                                                │
│    └── toHtml → render-poster → output/*.png               │
├─────────────────────────────────────────────────────────────┤
│ 6. 生成发布任务                                            │
│    └── toTasksJsonl → tasks.jsonl                          │
├─────────────────────────────────────────────────────────────┤
│ 7. 多平台发布                                              │
│    └── publisher.py batch → publisher.db                    │
└─────────────────────────────────────────────────────────────┘
```

### 草稿审批流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. --draft 模式                                            │
│    └── 生成草稿 JSON → drafts/pending/                     │
├─────────────────────────────────────────────────────────────┤
│ 2. 草稿预览                                                │
│    └── dragon.js review <draft_id>                         │
├─────────────────────────────────────────────────────────────┤
│ 3. 审批决定                                                │
│    ├── approve → 发布                                       │
│    └── reject → 记录原因 → 归档                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 输出结构

```
local-tests/<slug>/
├── index.html          # HTML预览
├── pages.jsonl         # Page计划
├── tasks.jsonl         # 发布任务
├── output/
│   ├── xhs-01-xxx.png   # 小红书图文
│   ├── xhs-02-xxx.png
│   ├── wechat-21x9-xxx.png  # 公众号封面
│   └── wechat-1x1-xxx.png   # 公众号分享图
└── assets/
    └── magazine-bg-webgl.js  # Editorial风格需要
```

---

## 🔒 质量门禁

### IP授权护栏

| 检查项 | 类型 | 处理 |
|--------|------|------|
| 声纹授权 | HARD | 无则阻断 |
| IP形象授权 | HARD | 无则阻断 |
| 授权过期 | HARD | 过期则阻断 |
| 授权<30天 | SOFT | 警告，不阻断 |

### 发布去重

- SHA256 内容指纹
- 跨平台去重索引
- 重复发布拦截

### 限流保护

- Token Bucket 令牌桶
- 平台级 QPS 控制
- 指数退避重试（0.1s → 0.2s → 0.4s）

---

## 📊 数据存储

### SQLite 数据库

**publisher.db** 路径: `C:/Users/li/.claude/skills/multi-platform-publisher/publisher.db`

| 表名 | 用途 |
|------|------|
| `publish_tasks` | 发布任务队列 |
| `publish_results` | 各平台发布结果 |
| `content_dedup` | 内容去重索引 |
| `rate_limit_state` | 限流状态 |
| `dead_letter_queue` | 死信队列（重试失败） |

---

## 🤝 协作接口

### 上游依赖

| 角色 | 输入内容 | 用途 |
|------|---------|------|
| 35-06 博主蒸馏师 | ip_profile_8dim.json | 出图素材 |
| blogger-fingerprint-registry | design_style, consent | 授权校验 |

### 下游交付

| 角色 | 输出内容 | 用途 |
|------|---------|------|
| 35-04 内容运营 | 发布结果 | 数据分析 |
| blogger-fingerprint-registry | 发布记录 | 博主画像更新 |

---

## ⚙️ 配置参数

```json
{
  "role": "blogger-poster",
  "version": "1.0.0",
  "model": "sonnet",
  "timeout": 300,
  "pipeline": {
    "skill_root": "C:/Users/li/.claude/projects/dragon-engine/skills/guizang-social-card-skill",
    "publisher_dir": "C:/Users/li/.claude/skills/multi-platform-publisher",
    "registry_db": "C:/Users/li/.claude/skills/blogger-fingerprint-registry/registry.db",
    "ip_profiles_dir": "C:/Users/li/.claude/ip-profiles"
  },
  "defaults": {
    "platforms": ["xiaohongshu", "wechat"],
    "watermark": true
  },
  "output": {
    "base_dir": "local-tests",
    "format": "png"
  }
}
```

---

## 📚 相关资源

- [guizang-social-card-skill](../guizang-social-card-skill/) - 社交卡片渲染
- [multi-platform-publisher](../multi-platform-publisher/) - 多平台发布器
- [blogger-fingerprint-registry](../blogger-fingerprint-registry/) - 博主指纹库
- [35-04内容运营](../35-04内容运营/) - 内容运营

---

**维护者**: 营销中心
**最后更新**: 2026-08-18
**版本**: v1.0.0

---

## Codex 使用说明

### 调用方式

```
@博主发布 <blogger_id> [--platforms xhs,wechat] [--draft] [--dry-run]
```

或

```
/blogger-poster post --blogger <blogger_id> --platforms xiaohongshu
```

### 环境注意事项

1. **路径差异**: Windows 路径需转换为 Unix 风格
2. **Python 依赖**: publisher.py 需要 Python 3.8+
3. **Node 依赖**: pipeline/*.mjs 需要 Node 22.5+
4. **数据库**: publisher.db 自动初始化
