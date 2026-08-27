---
name: univer-doc
description: Read, create, edit, paginate, chart, inspect, export, and review Univer Doc Units through DSH tools and the Lite Interface. Use proactively for paragraphs, rich text, lists, tasks, tables, images, charts, headers, footers, page layout, Traditional or Modern documents, docx import/export, and any Doc Unit task.
metadata:
  source: dream-num/dsh-univer-office v0.2.9 (Apache-2.0)
  mirrored: 2026-08-26
  version_upstream: 0.2.9
---

> **Apache-2.0 镜像说明**：本文件是上游 `dream-num/dsh-univer-office` 仓库 `skills/univer-doc/SKILL.md` 的镜像。
> **完整上游文件**：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-doc/SKILL.md>

---

# Univer Doc Units（镜像摘要）

**先加载 `univer`。** `univer_execute` 注入 `univerAPI` / `api` / `doc`（按 unitId 选的 `FDocument`）。**不要重新声明。** Doc 不提供 `workbook` / `presentation`；若取到 undefined 就是 Unit 类型选错。

## 模型要点

- 新 Doc 只有一个空段落。常用 `setText` 更新或 `doc.appendParagraph(text)` 追加
- 段落编辑 API 在 `doc` 上：`appendParagraph` / `insertParagraph` / `insertText` / `deleteRange`
- **段落 ID 跨多步编辑稳定**；索引会随内容漂移
- `FDocumentParagraph` 支持 `getText` / `setText` / `appendText` / `setStyle` / `getRange`
- List / Task 助手：`isListItem` / `isTask` / `setTaskChecked`
- 原生图表：`doc.newChart()` / `doc.insertChart()` / `doc.getCharts()` / `doc.getChart()`
- 颜色必须 `#RRGGBB`。**Doc 不支持公式 / 不重算**

## 数据流（重要）

- 主体是一个 `dataStream` 字符串
- 段落用 `\r` 分隔，文档以 `\r\n` 结尾
- `body.paragraphs[i].startIndex` 是终止 `\r` 的位置
- `insertText` / `deleteRange` / 文本样式操作的 offset 都基于这个流
- **永远保留段落终止符**

## 段落与文本样式

```js
const paragraph = doc.appendParagraph("Section Title");
const changed = paragraph.setStyle({
  namedStyleType: api.Enum.NamedStyleType?.HEADING_1 ?? "HEADING_1",
  textStyle: { bl: api.Enum.BooleanNumber.TRUE },
});
if (!changed) throw new Error("paragraph style update failed");
```

关键段落字段：`horizontalAlign` / `namedStyleType` / `headingId` / `indentStart` / `indentFirstLine`
文本样式紧凑字段：`bl` / `it` / `cl: { rgb }` / `bg: { rgb }`
**后续样式写入可能覆盖前面字段** —— 合并基础 fontFamily/size/spacing/color + 本地覆盖要刻意为之。

## 图片

```js
const image = await doc.insertImage({
  source: imageDataUri,
  imageSourceType: api.Enum.ImageSourceType.BASE64,
  width: 320,
  height: 180,
  wrappingStyle: api.Enum.DocsImageWrappingStyle.INLINE,
  textRange: { startOffset: ..., endOffset: ..., collapsed: true, segmentId: ... },
});
```

- `INLINE` 常规内容
- `WRAP_SQUARE` / `WRAP_TOP_AND_BOTTOM` 文本回流
- `BEHIND_TEXT` / `IN_FRONT_OF_TEXT` 刻意叠层

## 文档风格与分页

- **新 Doc 是 Modern 且不分页**。要先调 `doc.getDocumentFlavor()` 或 `doc.isTraditional()`
- Traditional 才支持物理分页；Modern 用大空白段伪装页是错的
- Traditional Doc 插入硬分页用一段原子 section 命令：

```js
if (!doc.isTraditional()) throw new Error("Traditional Doc required for physical pagination");
const section = doc.insertSectionBreak(chapter.getInfo().startOffset, {
  nextSectionType: api.Enum.SectionType.NEXT_PAGE,
});
```

## 表格与布局

固定列宽的 Traditional Doc 推荐无边框布局表。真数据表必须显式定义列宽、表头行、合并、边框。

## 验证（每次 mutation 后）

1. `univer_inspect` 看文档概览与相关段落/range
2. 用新只读 `univer_execute` 校验：段落文本/顺序、稳定 ID、样式、列表/任务、表格维度、图片身份、图表描述、document flavor、section break、headers/footers、page setup
3. `univer_screenshot` + 检视每张返回的页 PNG（**逻辑读回不能证明这些事实**）
4. 若需 `.docx` 交付，`univer_export` 前必须结构读回成功
5. 按 `univer` ready/status 流程交付

## 红线

- 🔴 `compile-typst` 在本插件不可用 —— **不要**用其他转换器伪造
- 🔴 不要尝试 Public Facade 没有的"动态当前页字段 / 表格单元格 padding 变更 / 单元格垂直对齐变更" —— 直接报告 gap
- 🔴 不要持久化临时签名 URL / 装全局 image polyfill / 直接写 drawing 存储

## 上游原文指针

- 完整 SKILL.md：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-doc/SKILL.md>
