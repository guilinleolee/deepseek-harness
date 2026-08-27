---
name: univer-board
description: Create, edit, chart, inspect, and review Univer Board canvas Units through DSH tools and the Lite Interface. Use proactively for Board shapes, text, connectors, routing, images, native charts, diagrams, canvas layout, or any Board Unit task.
metadata:
  source: dream-num/dsh-univer-office v0.2.9 (Apache-2.0)
  mirrored: 2026-08-26
  version_upstream: 0.2.9
---

> **Apache-2.0 镜像说明**：本文件是上游 `dream-num/dsh-univer-office` 仓库 `skills/univer-board/SKILL.md` 的镜像。
> **完整上游文件**：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-board/SKILL.md>

---

# Univer Board Units（镜像摘要）

**先加载 `univer`。** Board 用 `univer_unit` 在 draft worktree 创建并保留 `unitId`。`univer_execute` 注入 `univerAPI` / `api` / `board`（按 unitId 选）。**不要重新声明。**

未知 API 先 `univer_api`，尤其是 `FBoard.insertShape` / `insertShapes` / `FShape` / 连接线方法 / `FBoard.newChart` / `insertChart` / `getCharts` / `getChart`。

```js
const shape = board.insertShape({
  shapeType: api.Enum.ShapeTypeEnum.RoundRect,
  transform: { left: 80, top: 80, width: 180, height: 100 },
});
if (!shape) throw new Error("Cannot insert Board shape");
shape.getText().setText("Review");
return { shapeId: shape.getId(), elements: board.describeElements() };
```

`insertShape` 接受 `IShapeCreateInput`：**几何在 `transform`**，**视觉数据在 `shapeData`**，文本通过返回的 live handle 改。**不接受顶层 `id`/`left`/`top`/`width`/`height`/`text`。** 立刻保留生成 ID。

读回：`board.getElements()` / `board.describeElements()` / `board.save()`。

## 连接线与布局

- 创建关联形状先 `insertShapes()` 再创建连接线
- 用生成的 element ID + 绑定的端点
- 多节点图优先 `routing: "orthogonal"` + `routingMode: "auto"`
- straight 用短清晰通道，curve 用自环/紧凑反馈边，free polyline 只用于刻意手画

外接端点：左→右用 Right → Left，上→下用 Bottom → Top。反馈边走外车道。

## 端点 lint

`element-overlap` / `connector-through-element` / `connector-collinear-overlap` 视为阻塞。`connector-crossing` 是 warning 但要 review。

**模型分析**对没有持久路由点的 auto 连接线会报 unresolved —— 因为浏览器负责最终路由；**不要**用缺路由点推断"清晰路径"。

自由端点靠近可连元素时用 `board.setConnectorConnection()` 重绑。时序图用声明的 sequence-shape + lifeline 端点契约；**不要**用虚线连接线假装 lifeline。`normalizeConnectorRouting()` 不修端点语义。

**指定连接线意图、marker 类型/大小/offset、routing。** 导入/手画的路线可能暴露 marker-target 重叠 / 角点重叠 / marker 冲突 / 短端茎 / 虚线不连续。**重叠/冲突视为 error**。只对命名受影响连接线 normalize 一次，然后重读模型分析；**不要**循环或自动移无关元素。

## 图片

用户提供的 workspace 资源 + 内置 SVG 资源库。本地 SVG/位图按 Base64 data URI 给 `board.insertImage()`（`ImageSourceType.BASE64`）。除非资源声明 `colorEditable: true`，否则保留固有颜色。记录返回的 element ID，新读一次验 source type/bounds/stacking。

🔴 **不要**用 Unicode 字符假装必需 icon。**不要**持久化临时签名 URL。

## 原生图表

```js
const info = board.newChart(univerAPI.Enum.ChartTypeString.Column)
  .setTitle({ text: "..." })
  .setSource([...])
  .setCategoryField(0)
  .setValueFields([1])
  .setAbsolutePosition(80, 80)
  .setSize(640, 360)
  .build();
const inserted = await board.insertChart(info);
```

`board.getCharts()` / `board.getChart(id)` 返回 live。Common setter 更新 live chart；await `chart.setDataSource(values)`。完整替换 `chart.toBuilder().build()` + `await chart.update(info)`。删除 `await chart.remove()`。

**在 execution 返回前 await 插入/数据更新/替换/删除。** 后置新只读执行验：`board.getCharts().map(...)` 确认 ID/数量/类型/标题/位置/大小/数据。

## 验证（每次 mutation 后）

1. 用新 `univer_execute` 的 `board.describeElements()` / `board.save()` 读所有相关元素
2. 验 ID/kind/bounds/text/styles/stacking/连接线端点/routing/图片源/图表描述/布局分析 finding
3. DSH 实时预览最终路由布局/裁剪/marker 绘制/对比度/整体构图（**模型读回不能证明浏览器路由几何**）
4. `univer_screenshot` 完整 Board + 检视返回的 metadata（含渲染连接线布局分析时）。有缺陷就捕获 `focusBounds` 作 `region` 或连接线和端点 ID 作 `elementIds`（含合理 `padding` + `scale`），检视聚焦 PNG。修完重跑一次完整总览
5. 按 `univer` ready/status 流程交付

**心智图 / 表格 / ink / 高级编辑 不在本 Skill 已验证的创作契约内。** Board 不支持 export；交付 ready worktree 预览。

## 上游原文指针

- 完整 SKILL.md：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-board/SKILL.md>
