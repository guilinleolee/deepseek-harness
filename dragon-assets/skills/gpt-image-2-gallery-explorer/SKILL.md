---
name: gpt-image-2-gallery-explorer
description: GPT-Image-2 508+ 案例探索器（按类目/风格/关键词检索 freestylefly/awesome-gpt-image-2 gallery 案例库）. Use when user asks "找 GPT-Image2 参考图", "案例检索", "看海报案例", "海报灵感", "UI mockup 案例", "参考图库", "case 17", "case 350", "gallery".
version: 1.0.0
author: 天龙引擎集成
source: https://github.com/freestylefly/awesome-gpt-image-2
license: MIT
case_count: 518
last_updated: 2026-06-22
triggers: ["gpt image 2 gallery explorer", "gpt-image-2-gallery-explorer · 案例探索器"]
---

# gpt-image-2-gallery-explorer · 案例探索器

## L0: 一句话描述 (≤15字)
GPT-Image-2 案例库探索（518 案例）

## L1: 使用场景 (50-100字)
当用户需要查找 GPT-Image-2 真实生成案例（按类目/风格/关键词），或需要找海报/UI/角色/电商等视觉灵感时，使用本 skill。覆盖 12 大类目（UI/Charts/Posters/Products/Brand/Architecture/Photography/Illustration/Characters/Scenes/History/Document）的 518 个逆向工程案例，含图片链接 + Prompt + 分类标签。

## L2: 详细文档

### 核心能力

**数据来源**：[freestylefly/awesome-gpt-image-2/docs/gallery](https://github.com/freestylefly/awesome-gpt-image-2/tree/main/docs) — 7.7k⭐
- `gallery.md` (49KB, 13 类别索引)
- `gallery-part-1.md` (295KB, 165 案例)
- `gallery-part-2.md` (575KB, 353 案例)
- **总计 518 个真实生成案例**（含 Prompt + 标签 + 截图链接）

### 12 大类目

| # | 类目 | 案例数 | 典型场景 |
|---|------|--------|----------|
| 1 | **UI & Interfaces** | ~73 | App 截图 / 仪表盘 / 直播界面 |
| 2 | **Charts & Infographics** | ~52 | 信息图 / 知识卡片 |
| 3 | **Posters & Typography** | ~80 | 海报 / Campaign |
| 4 | **Products & E-commerce** | ~38 | 电商详情页 / 产品广告 |
| 5 | **Brand & Logos** | ~25 | Logo / 品牌系统 |
| 6 | **Architecture & Spaces** | ~12 | 建筑 / 室内 |
| 7 | **Photography & Realism** | ~73 | 人像 / 商业摄影 |
| 8 | **Illustration & Art** | ~53 | 插画 / 艺术风格 |
| 9 | **Characters & People** | ~25 | 角色 / 3D 玩具 |
| 10 | **Scenes & Storytelling** | ~20 | 故事板 / 直播 |
| 11 | **History & Classical** | ~16 | 古风长卷 / 历史 |
| 12 | **Document & Publication** | — | 文档 OCR / 出版物 |

### 数据结构

```yaml
case:
  id: case-17
  category: UI & Interfaces
  styles: [UI]
  scenes: [Tech, Social]
  title: "Notion-like dashboard with AI sidebar"
  prompt: "the full gpt-image-2 prompt"
  image_url: "/images/case-17.jpg"
  source_url: "https://github.com/.../case-17"
  tags: [UI, Dashboard, Notion]
```

### 核心命令

```bash
# 按类目查询
python3 ~/.claude/skills/gpt-image-2-gallery-explorer/scripts/query.py \
  --category "UI & Interfaces" --limit 5

# 按案例 ID 查询
python3 ~/.claude/skills/gpt-image-2-gallery-explorer/scripts/query.py \
  --case 17

# 按关键词搜索
python3 ~/.claude/skills/gpt-image-2-gallery-explorer/scripts/query.py \
  --keyword "fujifilm" --limit 10

# 按风格 + 场景组合
python3 ~/.claude/skills/gpt-image-2-gallery-explorer/scripts/query.py \
  --style "Poster" --scene "Commerce"

# 列出所有类目统计
python3 ~/.claude/skills/gpt-image-2-gallery-explorer/scripts/query.py --stats

# 随机推荐
python3 ~/.claude/skills/gpt-image-2-gallery-explorer/scripts/query.py --random 5
```

### 与其他 skill 协同

| 技能 | 协同方式 |
|------|---------|
| **gpt-image-2-style-library** | 案例 → 模板映射（style-library.md 自动列案例） |
| **gpt-image-2-prompt-library** V2.0 | 案例 Prompt → 复用 + 改写 |
| **gpt-image-2-api-integration** V2.0 | 案例 → 反向工程 → 用模板生成 |
| **smart-illustrator** | 案例库作为灵感和参考 |
| **35-06 博主蒸馏分析师** V1.0 | 案例 → 博主风格提取 |

### 快速示例

**示例 1: 找 UI 灵感**
```
用户: "想看 Notion 风格的 UI 截图"
→ query.py --category "UI & Interfaces" --keyword "notion"
→ 返回 case-17 (Notion dashboard), case-4 (iPhone mockup)...
```

**示例 2: 反向工程**
```
用户: "这张海报是怎么生成的？"（附图）
→ 反向 → 检索风格/场景 → 找到对应案例 → 提取 Prompt
```

**示例 3: 跨类目灵感**
```
用户: "找一张有食物的 UI 截图"
→ query.py --category "UI & Interfaces" --keyword "food"
→ 或 query.py --category "Photography & Realism" --keyword "food ui"
```

### 数据同步

```bash
# 完整同步（首次）
python3 ~/.claude/skills/gpt-image-2-gallery-explorer/scripts/sync.py

# 增量同步（每周）
python3 ~/.claude/skills/gpt-image-2-gallery-explorer/scripts/sync.py --incremental
```

### 安装依赖

无需额外依赖（纯 Python 标准库）。

### 注意事项

1. **图片下载**：cases 引用 `/images/*.jpg`，需要从上游 `data/images/` 下载（按需，约 30-50MB）
2. **Prompt 复用**：案例 Prompt 已结构化，可直接修改复用
3. **跨类目**：一个案例可能属多类目（如 food + UI），检索时按主类目
4. **离线模式**：默认不下载图片，仅提供 URL；如需图片加 `--download-images`

### 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| **V1.0.0** | **2026-06-22** | **初始版（518 案例 + 12 类目 + 5 维检索）** |

### 版本信息

- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **Source**: [freestylefly/awesome-gpt-image-2](https://github.com/freestylefly/awesome-gpt-image-2)
- **Case Count**: 518
- **Last Updated**: 2026-06-22