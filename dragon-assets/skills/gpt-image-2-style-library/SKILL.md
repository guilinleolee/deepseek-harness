---
name: gpt-image-2-style-library
description: Choose GPT-Image2 / gpt-image-2 visual styles and industrial prompt templates from the awesome-gpt-image-2 style library. Use when an agent needs to create, rewrite, classify, or improve image-generation prompts with repository-backed templates, categories, style tags, scene tags, pitfalls, and example cases. Triggers: "GPT-Image2 模板", "海报模板", "UI 截图模板", "图表信息图模板", "工业级提示词", "Prompt as Code", "21 套模板", "Style Library", "案例库".
version: 2.0.0
author: 天龙引擎集成 (基于 freestylefly/awesome-gpt-image-2)
source: https://github.com/freestylefly/awesome-gpt-image-2
license: MIT
stars: 7771
last_updated: 2026-06-22
triggers: ["gpt image 2 style library", "GPT-Image2 Style Library · 天龙引擎集成版 V2.0"]
---

# GPT-Image2 Style Library · 天龙引擎集成版 V2.0

## L0: 一句话描述 (≤15字)
GPT-Image2 工业级提示词模板库 + Style Library

## L1: 使用场景 (50-100字)
当用户需要生成专业级图像（海报 / UI / 图表 / 电商 / 品牌 / 摄影 / 角色 / 场景 / 历史等），或需要从 21 套工业模板中选型 + 防坑时，使用本 skill。覆盖小红书配图、公众号封面、UI Mockup、海报设计、电商详情页、品牌视觉、IP 角色、直播截图等场景。

## L2: 详细文档

### 核心能力

**数据来源**：[freestylefly/awesome-gpt-image-2](https://github.com/freestylefly/awesome-gpt-image-2) - **7,771 ⭐ / 1,010 Fork**，2026-06-22 最新更新
- **508 个**逆向工程案例（12 大类目）
- **21 套**工业级提示词模板（text + JSON + 防坑指南）
- **结构化 references/style-library.md**（659 行自动生成）

### 13 大模板类目（21 套模板）

| # | 类目 | 模板数 | 典型场景 |
|---|------|--------|----------|
| 1 | **UI 与界面** | 3 | App 截图、仪表盘、直播界面、社媒截图 |
| 2 | **图表与信息可视化** | 3 | 信息图、知识卡片、技术图解、科学尺度图 |
| 3 | **海报与排版** | 4 | 商业海报、运动 Campaign、概念字体、签名选择 |
| 4 | **商品与电商** | 2 | 电商详情页、产品广告 |
| 5 | **品牌与标志** | 1 | Logo、品牌系统 |
| 6 | **建筑与空间** | 1 | 建筑渲染、室内设计 |
| 7 | **摄影与写实** | 1 | 人像、商业摄影 |
| 8 | **插画与艺术** | 1 | 插画、艺术风格 |
| 9 | **人物与角色** | 1 | 角色设计、3D 玩具 |
| 10 | **场景与叙事** | 1 | 故事板、直播、世界观 |
| 11 | **历史与古风** | 1 | 古风长卷、历史人物、诗词视觉 |
| 12 | **文档与出版物** | 1 | 文档 OCR、出版物 |
| 13 | **其他应用场景** | 1 | 特殊任务（IP、Game UI 等）|

### 数据结构

```yaml
# 模板数据格式（references/style-library.md）
template:
  id: ui-screenshot-system
  category: UI & Interfaces
  styles: [UI]
  scenes: [Tech, Social]
  tags: [UI, Dashboard, Screenshot]
  cover: /images/case17.jpg
  use_when_en: "Use for app screens, dashboards..."
  use_when_zh: "用于 App 截图、仪表盘..."
  guidance: ["Lock platform, aspect ratio...", "锁定平台、比例..."]
  pitfalls: ["Avoid vague platform names...", "避免平台描述过泛..."]
  example_cases: [17, 2, 4]
```

### 工作流（天龙引擎增强版）

1. **检测用户语言**（中/英）→ 用对应语言回答
2. **识别目标产物**：product / poster / UI / infographic / brand / photo / illustration / character / scene / history / document / special
3. **三层匹配**：
   - 模板类目（13 类）
   - 视觉风格标签（UI / Realistic / 3D / Illustration / Classical / Brand / Poster）
   - 场景标签（commerce / education / social / food / travel / story / history / tech / creative）
4. **选型决策**：
   - 单一最强模板 → 直接使用
   - 多个候选 → 呈现 2-3 个选项 + 简短理由，请用户选择
5. **构建 6 块结构化 prompt**：
   - subject and task（主体与任务）
   - composition and layout（构图与布局）
   - visual style and materials（视觉风格与材质）
   - text and label requirements（文字与标签要求）
   - aspect ratio and output format（比例与输出格式）
   - constraints and negative details（约束与负面细节）
6. **输出可复制 prompt**，附模板名 + 案例 ID

### 核心命令

```bash
# 检索模板
python3 ~/.claude/skills/gpt-image-2-style-library/scripts/query.py \
  --category poster --scene commerce --style realistic

# 列出所有模板
python3 ~/.claude/skills/gpt-image-2-style-library/scripts/query.py --list

# 同步上游数据（每周一次）
node ~/.claude/skills/gpt-image-2-style-library/scripts/generate-style-skill.mjs
node ~/.claude/skills/gpt-image-2-style-library/scripts/install-style-skill.mjs

# 按案例 ID 查模板
python3 ~/.claude/skills/gpt-image-2-style-library/scripts/query.py --case 17
```

### 自然语言触发

```
# 模板选型
"帮我生成小红书海报" → poster + social media + commerce
"做个 App UI 截图" → ui-screenshot-system + tech
"画一张信息图" → infographic-engine + education
"角色设计卡牌" → character-design + illustration

# 风格查询
"Fujifilm 风格" / "CCD 色调" / "35mm 胶片"
"Mondo 风格" / "概念字体海报" / "运动商业海报"
```

### 与天龙引擎现有技能协同

| 现有技能 | 协同方式 |
|---------|---------|
| **gpt-image-2-prompt-library** (V2.0) | 社区 Twitter 提示词 ↔ Style Library 工业模板（互补）|
| **gpt-image-2-api-integration** (V2.0) | API 调用 → 模板 prompt 注入 |
| **smart-illustrator** (V2.1) | 配图系统接入 Style Library |
| **baoyu-cover-image** | 公众号封面 → Poster 模板 |
| **baoyu-danger-gemini-web** | Gemini 后端降级到 GPT-Image-2 |
| **qiaomu-mondo-poster-design** | Mondo 艺术家风格 vs Style Library 工业模板（分工）|
| **ui-social-mockup-generator** | UI 截图模板复用 |
| **seedance2-skill** | Image → Video 首帧模板 |
| **ecommerce-image-generator** | Product/Brand 模板 |
| **manga-style-video** | Character 模板 |
| **frontend-design** | UI Mockup 模板 |

### 天龙岗位升级

| 岗位 | 版本升级 | 新增能力 |
|------|---------|---------|
| **35-02 社媒运营** | V12.6 → **V13.0** | 13 类模板自动选型 + 21 套防坑 |
| **35-05 短视频编导** | V5.0 → **V6.0** | 视频封面 / 直播截图 / Storyboard 模板 |
| **35-06 博主蒸馏分析师** | — → **V1.0** | 蒸馏博主风格 → Style Library 镜像 |
| **13-01 设计师** | V11.10 → **V11.11** | Style Library 接入 + 12 类目案例库 |
| **28-01 文案策划** | V10 → **V10.1** | 概念字体海报 + 标题驱动视觉 |
| **09-01 视觉师** | V10 → **V10.1** | 截图 → 模板逆向审查 |
| **10-01 提示词架构师** | V11 → **V11.1** | 21 套 JSON 模板 → DSPy Signature 资产库 |
| **03 构建师** | V8.71 → **V8.72** | API → UI 原型图 |

### 快速示例

**用户请求**：`用 gpt-image-2 生成一张小红书爆款海报`

**天龙引擎响应**：
1. 选型 → `poster-commercial-campaign` 模板 + `social` scene
2. 输出可复制 prompt：
```
设计一张小红书爆款海报，主题为[主题词]。
主视觉：[主体元素]，标题文案：[标题]，副标题：[副标题]。
版式：左对齐对角构图，风格：未来极简。
色彩：主色 #FF6B6B + 辅色 #4ECDC4，氛围：年轻活力。
输出：3:4 比例，适合小红书传播的高分辨率海报。
约束：标题文字清晰可读，不超过 12 字；背景留白充足；避免杂乱拼贴。
```
3. 附 `template_id: poster-commercial-campaign` + 防坑指南
4. 调用 gpt-image-2-api-integration 生成

### 数据同步

```bash
# 同步上游仓库
cd /tmp/gpt-image2-staging/awesome-gpt-image-2
git pull
npm run generate:style-skill
node scripts/install-style-skill.mjs

# 或使用天龙引擎自带同步脚本
python3 ~/.claude/skills/gpt-image-2-style-library/scripts/sync.py --incremental
```

### 安装依赖

```bash
# 必需
npm install -g node  # 18+

# 可选（如果需要直接运行上游 .mjs）
cd ~/.claude/skills/gpt-image-2-style-library
npm install
```

### 注意事项

1. **模板版本**：与上游 `freestylefly/awesome-gpt-image-2` 同步（每周一次）
2. **Sponsor 段**：README 中的赞助商段落不纳入模板数据
3. **多语言**：references/style-library.md 已含中英双语
4. **图片资源**：templates.md 引用的图片路径在 `data/images/`（已剥离大文件，按需下载）

### 版本信息

- **Version**: 2.0.0
- **Author**: 天龙引擎集成
- **Source**: [freestylefly/awesome-gpt-image-2](https://github.com/freestylefly/awesome-gpt-image-2)
- **License**: MIT
- **Upstream Stars**: 7,771
- **Last Updated**: 2026-06-22