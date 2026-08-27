---
name: univer-slide
description: Create, redesign, edit, inspect, lint, export, and review Univer Slide Units through DSH tools and the Lite Interface. Use proactively for presentations, slide decks, pages, SVG-authored layouts, shapes, text, images, tables, charts, transitions, pptx import/export, or any request whose deliverable is a presentation; generated pages should use univer_compile_svg and every changed page should use univer_lint.
metadata:
  source: dream-num/dsh-univer-office v0.2.9 (Apache-2.0)
  mirrored: 2026-08-26
  version_upstream: 0.2.9
---

> **Apache-2.0 镜像说明**：本文件是上游 `dream-num/dsh-univer-office` 仓库 `skills/univer-slide/SKILL.md` 的镜像。
> **完整上游文件**：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-slide/SKILL.md>

---

# Univer Slide Units（镜像摘要）

**先加载 `univer`。** `univer_execute` 注入 `univerAPI` / `api` / `presentation`（按 unitId 选）。**不要重新声明。** Slide 不提供 `workbook`，undefined 就是 Unit 类型选错。

- **Facade 页面索引 0 基**（`getSlideByIndex` / `getSlides()[i]`）
- **工具页面号 1 基**（`univer_compile_svg.page` / 数字 `univer_lint.pages` 用 1 表示第一页）
- **跨回合携带页面用稳定 page ID**

## 路由选择

- **新建/重做页面**：手写 SVG → `univer_compile_svg`（**不要手写 Facade 绘制调用**）
- **编辑已有内容**：`univer_execute` + 实时 Facade handle
- **插入/更新原生图表**：先在 SVG 里预留矩形，再用 `FSlide` chart 方法
- **每个改动页面必走**：`univer_inspect` → `univer_lint` → `univer_screenshot` 并检视 PNG
- **验证后导出**：`univer_export` → `.pptx`

## 多页 deck 工作流（重要）

### 1. 先写页规格 spec.md

固定 deck 级常量（`#RRGGBB` 色板、`fontSize = px × 0.75`、字体、icon 风格、页面尺寸）。

每页写明：精确布局 + 层级/卡片数 + 页面尺寸 + 结构类型（流程/中心放射/层级/圆形阶段/时间线/对比/卡片网格/Hero）+ 一句话核心信息 + 标题/标签/卡片/注释逐字最终文案 + 所需 workspace 图片/SVG 资产。

**相邻页面不要重复同结构。**

### 2. 闭环构建每页（先完成 N 再做 N+1）

1. 准备本页本地资产，记录在 spec 里。icon/logo/emoji/插画走 `univer_resources find` → `export`
2. 手写完整 `page-NN.svg`（内联样式 + workspace 相对资源）
3. 调 `univer_compile_svg`（带 `source` / `file` / `worktreeId` / Slide `unitId` / 1 基 `page` / `mode: "replace"`）
4. **清掉每个编译器 warning**。每条 lint 要么修、要么有意保留并写明理由
5. `univer_inspect` Slide Unit → `univer_lint` 第 N 页
6. 修 SVG → 替换同页 → 直至干净或每条幸存 lint 有显式理由

**🔴 不要用 `mode: "add"` 修页**（只会叠加）。要修改就重渲 SVG 用 `replace`。`add` 只用于已完成页的真新元素。

### 3. 审 deck

每页通过后调 `univer_screenshot`，每批最多 5 页。

检查清单：
1. 元素被页面/容器裁剪
2. 文字溢出卡片/色块
3. 文本框意外重叠
4. 形状挡住必要信息
5. 对比度过低或文字放在复杂图片上没衬底
6. 缺需求内容
7. 箭头断连、方向错、配色错
8. 跨页一致性（色板/字体/icon 风格/边距/结构多样性）

每条缺陷按模式查：搜所有页 SVG 同错、修源、替换受影响页、重跑 inspect/lint、重截图受影响页。

### 4. 交付

按 `univer` ready/status 走。仅在用户要求时给 `.univer` artifact + `.pptx` 导出。**不要自动 merge**。

## SVG 是生成路径（核心）

`univer_compile_svg` 是声明式：
- `replace` 清掉并重建已存在页
- `pageCount + 1` 是 append
- 更大页号失败
- 重复 `replace` 是幂等
- `mode: "add"` 叠加不清空

支持的 SVG：shapes/paths/transforms/gradients/text/bitmaps/`<use>`/style sheets/CSS 单位和颜色函数。`<image>` 必须声明 width/height，只能引用 session workspace 内的资源。

**换行用 `<tspan>`**，scalar `x` + 绝对 `y` 或非零 `dy`。**不要**用 `dx` / 单字坐标 / 空格排版。SVG 默认空白会折叠连续和前导空格 —— 用 `xml:space="preserve"` / 定位 text 元素 / `&#160;` 故意保留固定间距。

中心徽章/圆文字：`dominant-baseline="middle"` + `text-anchor="middle"`。
箭头：` <marker orient="auto-start-reverse">`，**不要**手放三角顶点。
渐变默认对象包围盒分数坐标，垂直渐变用 `x2="0" y2="1"`。

**Slide 渲染器无法忠实重现滤镜 / 半透明渐变 / 非正方形的径向渐变**。可接受位图嵌入的子树标 `data-univer-embed="image"`；可编辑文字/布局结构留在外面。**编译器 warning = 内容降级或丢弃，必须处理**。

## Lint 三条规则（保守）

`univer_lint` 用渲染字形几何检查 3 条：
- 文字越页
- 文字越出矩形容器
- 文字字形带重叠

**每条 finding 都当作真的，直到证据证明它是设计意图。**

- 越页：必修
- 越框：缩文案 / 显式换行 / 加宽加高卡片
- 字形重叠：检视两元素颜色/不透明度/预期堆叠再决定

**每条 finding 最终必须修掉，或在终稿显式注明理由。**

## Deck / 页 / 元素

- **页面**：`presentation.getSlideByIndex(0)` / `getSlideById(id)` / `getSlides()`
- **背景**：`slide.setBackground`（颜色/图片/渐变/图案）
- **删除/插入/移动**：`deleteSlide` / `insertSlide` / `moveSlide` 都返回布尔 —— 检查
- **元素**：读 `getElements()` / `getElementById(id)`；`getShapes()` / `getImages()` / `getGroups()` 收窄
- **创建普通形状**：`slide.insertShape({ shapeType, transform?, shapeData? })` 返回 live handle 或 null；检查 + 立刻保留 `getId()`
- **删除**：`deleteElement(element)` 不要 id；检查 boolean/null 返回
- **栈顺序**：无 `zIndex`；底到顶 = 元素顺序；SVG 文档顺序保留

## 原生图表

```js
const info = slide.newChart(univerAPI.Enum.ChartTypeString.Donut)
  .setTitle({ text: "..." })
  .setSource([...])
  .setCategoryField(0)
  .setValueFields([1])
  .setDoughnutHole(0.46)
  .setLegend(true)
  .setAbsolutePosition(390, 160)
  .setSize(260, 220)
  .build();
const inserted = await slide.insertChart(info);
```

`slide.getCharts()` / `slide.getChart(id)` 返回 live。await `chart.setDataSource(values)`。完整替换用 `chart.toBuilder().build()` + `await chart.update(info)`。删除 `await chart.remove()`。

**插图表要在最终整页 SVG 替换之后**，因为替换会清掉所有页元素。

## 上游原文指针

- 完整 SKILL.md：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-slide/SKILL.md>
