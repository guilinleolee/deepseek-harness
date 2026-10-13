---
license: UNKNOWN
name: shibazi-illustrator
version: 1.0.0
description: |
  十八子写作智能配图系统（双引擎：HTML渲染 + AI生图）。

  支持掘金/知乎/公众号/小红书多平台尺寸，中文优化。

  ## 双引擎对比
  - HTML渲染：极快（~2秒）、免费、模板化
  - AI生图：较慢（~15-30秒）、¥1-2/图、无限创意

  触发词：配图、插图、illustration、shibazi-illustrate
author: 天龙引擎团队
created: 2026-02-26
category: design

triggers:
  - "用户说「帮我配个图」时"
  - "用户说「生成插图」时"
  - "用户说「illustrate」时"
  - "需要为文章生成配图时"

requires:
  tools: [bun, npx]
  skills: []

# scripts:
#   - path: scripts/html-export.ts
#     entrypoint: main
    description: HTML渲染引擎
    arguments:
      - name: input
        type: file
        required: true
      - name: template
        type: string
        required: false
      - name: format
        type: string
        required: false
  - path: scripts/playwright-screenshot.ts
    entrypoint: main
    description: PNG截图工具
  - path: scripts/generate-image.ts
    entrypoint: main
    description: AI单图生成
  - path: scripts/batch-generate.ts
    entrypoint: main
    description: AI批量生成

evaluation:
  benchmark: evals/benchmark.json
  quality_threshold: 0.8

see_also:
  - https://github.com/binaryify/OneDarkPro
---

# 十八子写作智能配图系统（双引擎）

## 🔄 双引擎架构

本系统提供两种配图引擎，按需求选择：

| 引擎 | 速度 | 成本 | 创意性 | 适用场景 |
|------|------|------|--------|----------|
| **HTML渲染** | ⚡ 极快（~2秒） | ¥0 | ❌ 模板化 | 知识卡片、金句海报、社交媒体卡片 |
| **AI生图** | 🐢 较慢（~15-30秒） | ¥1-2/图 | ✅ 无限创意 | 抽象概念、场景插图、隐喻说明、封面图 |

---

## ⛔ 强制规则

### 规则 1：用户提供的文件 = 要配图的文章

```
/shibazi-illustrate article.md      → article.md 是文章，为它配图
/shibazi-illustrate draft.md        → draft.md 是文章，为它配图
```

### 规则 2：引擎选择

**默认引擎：AI**（保持向后兼容）

**HTML引擎需要显式指定：**

```bash
/shibazi-illustrate article.md --engine html
/shibazi-illustrate article.md --engine ai  # 默认，可省略
```

### 规则 3：AI引擎必须读取 style 文件

生成任何图片 prompt 前，**必须读取**对应的 style 文件：

| 模式 | 必须读取的文件 |
|------|---------------|
| 文章配图（默认） | `styles/style-shibazi-light.md` |
| Cover 封面图 | `styles/style-shibazi-light.md` |
| `--style dark` | 从 smart-illustrator 读取 `styles/style-dark.md` |

**禁止自己编写 System Prompt。**

---

## 使用方式

### 📄 HTML渲染引擎

```bash
# 瑞士风格（Kabager）- 2列网格，品牌感强
/shibazi-illustrate article.md --engine html --template kabager

# 极简风格 - 单列，留白充足
/shibazi-illustrate article.md --engine html --template minimal

# 戏剧风格 - 高对比，暗色背景
/shibazi-illustrate article.md --engine html --template dramatic

# 输出格式选择
/shibazi-illustrate article.md --engine html --format html    # 仅HTML
/shibazi-illustrate article.md --engine html --format png     # 仅PNG（需Playwright）
/shibazi-illustrate article.md --engine html --format both    # HTML+PNG

# 自定义尺寸
/shibazi-illustrate article.md --engine html -w 800 -h 1200
```

### 🎨 AI生图引擎

```bash
# 默认掘金尺寸 16:9
/shibazi-illustrate path/to/article.md

# 指定平台
/shibazi-illustrate path/to/article.md --platform juejin
/shibazi-illustrate path/to/article.md --platform zhihu
/shibazi-illustrate path/to/article.md --platform wechat
/shibazi-illustrate path/to/article.md --platform xiaohongshu

# 只输出 prompt（不调用 API）
/shibazi-illustrate path/to/article.md --prompt-only

# 指定图片数量
/shibazi-illustrate path/to/article.md --count 3

# Cover 模式
/shibazi-illustrate path/to/article.md --mode cover --platform juejin
/shibazi-illustrate --mode cover --platform juejin --topic "AI写作工具对比"

# PPT/Slides 模式
/shibazi-illustrate path/to/script.md --mode slides
/shibazi-illustrate path/to/script.md --mode slides --prompt-only
```

---

## 参数说明

| 参数 | 默认值 | 说明 | 引擎 |
|------|--------|------|------|
| `--engine` | `ai` | 引擎：`html`/`ai` | 两者 |
| `--template` | `kabager` | HTML模板：`kabager`/`minimal`/`dramatic` | HTML |
| `--format` | `html` | 输出格式：`html`/`png`/`both` | HTML |
| `--platform` | `juejin` | 平台：`juejin`/`zhihu`/`wechat`/`xiaohongshu` | AI |
| `--mode` | `article` | 模式：`article`/`slides`/`cover` | AI |
| `--style` | `light` | 样式：`light`/`dark`/`minimal` | AI |
| `--count` | auto | 图片数量（自动根据文章长度） | AI |
| `--prompt-only` | false | 只输出 prompt，不调用 API | AI |
| `--no-cover` | false | 不生成封面图 | AI |
| `-w, --width` | 600 | 宽度（像素） | HTML |
| `-h, --height` | 900 | 高度（像素） | HTML |

---

## 平台尺寸（AI引擎）

| 平台 | 代码 | 宽高比 | 分辨率 |
|------|------|--------|--------|
| 掘金 | `juejin` | 16:9 | 1600×900 |
| 知乎 | `zhihu` | 16:9 | 1600×900 |
| 微信公众号 | `wechat` | 2.35:1 | 1200×512 |
| 小红书 | `xiaohongshu` | 3:4 | 1080×1440 |

---

## 工作流程

### HTML引擎流程

1. **分析文章结构** → 提取标题、章节、金句
2. **加载模板** → 读取 `templates/{template}.html`
3. **变量替换** → 将内容注入模板
4. **渲染输出** → 生成 HTML（可选 PNG）

### AI引擎流程

1. **分析文章结构**
   - 读取文章内容
   - 识别关键配图点（抽象概念、流程、对比等）
   - 确定配图类型和数量

2. **生成图片 Prompt**
   - 读取对应的 style 文件
   - 为每个配图点生成 Gemini prompt
   - 构建完整的 JSON 格式请求

3. **调用 Gemini API（除非 --prompt-only）**
   - 使用 `scripts/generate-image.ts` 生成单张图片
   - 使用 `scripts/batch-generate.ts` 批量生成
   - 输出到 `article-image-01.png` 等文件

4. **插入图片到文章**
   - 生成 `article-illustrated.md`
   - 在合适位置插入图片引用
   - 保持原文结构不变

---

## 配图类型（AI引擎）

| 类型 | 引擎 | 适用场景 | 示例 |
|------|------|---------|------|
| `process` | Mermaid | 流程、步骤 | 工作流程、算法步骤 |
| `architecture` | Mermaid | 系统架构 | 技术架构图 |
| `concept` | Gemini | 抽象概念 | 核心概念解释 |
| `comparison` | Gemini | 对比分析 | 方案对比、优缺点 |
| `data` | Gemini | 数据展示 | 统计数据、趋势 |
| `scene` | Gemini | 使用场景 | 场景说明、故事 |
| `metaphor` | Gemini | 类比说明 | 隐喻、类比 |

---

## 输出文件

### HTML引擎

```bash
article.md                  # 原文
article-poster.html         # HTML海报（--format html）
article-poster.png          # PNG截图（--format png）
```

### AI引擎

```bash
article.md                  # 原文
article-illustrated.md      # 带配图的文章（主输出）
article-cover.png           # 封面图（16:9）
article-image-01.png        # 内容图（根据平台尺寸）
article-image-02.png
article-image-03.png
```

---

## 成本估算

### HTML引擎
- **成本**：¥0
- **速度**：~2秒/张

### AI引擎
- **成本**：约 ¥1/图（2K 分辨率）
- **一篇中等文章（2-4 张图）**：约 ¥2-4
- **速度**：~15-30秒/图

---

## 直接脚本调用

### HTML引擎

```bash
# 生成HTML
npx -y bun ~/.claude/skills/shibazi-illustrator/scripts/html-export.ts article.md -t kabager

# 生成HTML+PNG（需Playwright）
npx -y bun ~/.claude/skills/shibazi-illustrator/scripts/html-export.ts article.md -t kabager -f both

# PNG截图
npx -y bun ~/.claude/skills/shibazi-illustrator/scripts/playwright-screenshot.ts poster.html -o poster.png
```

### AI引擎

```bash
# 生成单张图
npx -y bun ~/.claude/skills/shibazi-illustrator/scripts/generate-image.ts -p "A cute cat" -o cat.png

# 批量生成
npx -y bun ~/.claude/skills/shibazi-illustrator/scripts/batch-generate.ts prompts.json
```

---

# 变更历史

## 1.0.0 (2026-02-26)

### 新增
- V8.0 格式迁移
- 添加 version、tags、category、triggers 字段
- 添加 scripts 配置
- 添加 evaluation 配置
