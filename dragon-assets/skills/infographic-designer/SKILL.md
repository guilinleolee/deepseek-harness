---
license: UNKNOWN
name: skill-infographic-designer
description: |
github_repo: anthropics/claude-code
github_hash: ab3ce06c9ac0a6a0405850e642b80b0bb2c9fb25
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
author: 天龙引擎团队
created: 2026-02-26
category: workflow
triggers: ["infographic designer", "SKILL: Infographic Designer (信息图设计专家)"]
---

# SKILL: Infographic Designer (信息图设计专家)

**触发词：信息图设计专家**

专业级信息图表设计专家，专注于瑞士设计风格（Swiss Design），致力于将复杂的管理学或技术性文案转化为高密度、视觉逻辑严密的商务海报，并自动完成文件保存与截图。

## 技能定位
本技能旨在通过严格的网格系统、扁平化美学和高对比色彩方案，为用户提供“即学即用”的高级感视觉呈现。**本技能已集成自动化保存与截图工作流。**

## 核心设计规范 (Swiss Style)
在执行任务时，必须严格遵守以下瑞士设计准则：
1. **极致扁平化**：严禁使用阴影、渐变或 3D 效果。
2. **理性网格**：所有元素必须基于隐含的网格对齐，强调秩序感。
3. **字级层级**：使用极致的字号对比（如 60pt 对标 12pt）来引导视觉重心。
4. **配色方案**：优先使用 Navy (#1E3A5F)、Crimson (#C8102E) 和 Slate (#6B7C93) 的商务组合。
5. **背景质感**：使用浅米色 (#F5F5F0) 或极简浅灰，并加入低透明度 (10%) 的品牌水印。

## 固定品牌元素 (Fixed Brand Elements)
生成的每一张图表必须包含以下固定项，严禁修改文字内容：
1. **水印 (Watermark)**：居中横向，文字为“卡巴格企业管理培训”，透明度固定为 10%。
2. **左上角标签 (Top-Left)**：深海军蓝背景，白色文字，内容为“卡巴格企业管理培训”，字号需与右侧对称 (text-xl)。
3. **右上角标签 (Top-Right)**：文字为“SYSTEM v1.0”，深绯红色，斜体，Mono 字体 (text-xl)。
4. **页脚标语 (Footer Slogan)**：在页脚显著位置包含“From People to Systems”。

## 内容结构规范 (Content Specifications)
1. **双色主标题 (Dual-Color Title)**：
   - **结构**：必须采用两段式结构（换行显示）。
   - **配色**：第一段为海军蓝 (#1E3A5F)，第二段为绯红色 (#C8102E)。
   - **样式**：超重黑体 (font-black)、极紧字间距 (tracking-tighter)。
2. **副标题**：深蓝灰色 (#6B7C93)，左侧带 4px 宽度、海军蓝色的竖线修饰（Border-left）。字号需较常规大 2 号（建议 20px）。
3. **网格节点**：采用 3x2 或 2x3 布局，标题前带红色竖线，正文为深灰色 (#64748B)。字号需较常规大 4 号（标题建议 24px，正文建议 15px）。
4. **总结金句 (Summary Gold Sentence)**：
   - **位置**：位于底部深海军蓝 (#1E3A5F) 色块内。
   - **样式**：白色加粗文字，字号建议 25px。

## 自动化工作流 (Automated Workflow)

### 第一步：获取时间戳
- 使用 `date +%Y%m%d%H%M` 获取当前时间作为文件名（格式：年月时分）。

### 第二步：生成并保存 HTML
- 将生成的 HTML 代码保存至 `D:/文生图/HTML/{timestamp}.html`。
- 确保 HTML 引用了 Tailwind CSS 且包含完整的品牌母版布局。

### 第三步：自动化截图
- 使用 `playwright-skill` 打开生成的本地 HTML 文件。
- **精准裁剪**：指定截取 `.poster-card` 元素，而非全网页。
- 设置视口宽度为 1000px（确保渲染空间足够）。
- 截图保存至 `D:/文生图/截图/{timestamp}.png`。

### 第四步：反馈结果
- 向用户报告 HTML 和图片文件的完整路径。

## 常用方法 (Methods)

### `generate_and_capture`
接收文案，执行全自动化设计、保存与截图流程。
- 参数：`text_content`

---
🤖 Generated with [Claude Code](https://github.com/anthropics/claude-code)

#### Evolution Pattern (Maintenance)

To preserve custom improvements when a core skill is upgraded, avoid editing `SKILL.md` directly for individual modifications. Instead:

1. Create or update an `evolution.json` file in the skill's root directory.
2. Store modification suggestions, custom rules, or evolved logic there.
3. This ensures that your custom "evolutions" are preserved even if the base `SKILL.md` is replaced during an upgrade.
