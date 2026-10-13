---
name: univer-cross-unit-formula
description: Author, calculate, update, inspect, and verify cross-Unit formulas through DSH tools and the Lite Interface. Use proactively when a Sheet cell or formula-driven Shape in a Sheet, Doc, Slide, or Board reads a Sheet range or Base table column from another Unit in the same .univer file.
metadata:
  source: dream-num/dsh-univer-office v0.2.9 (Apache-2.0)
  mirrored: 2026-08-26
  version_upstream: 0.2.9
---

> **Apache-2.0 镜像说明**：本文件是上游 `dream-num/dsh-univer-office` 仓库 `skills/univer-cross-unit-formula/SKILL.md` 的镜像。
> **完整上游文件**：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-cross-unit-formula/SKILL.md>

---

# Cross-Unit formulas（镜像摘要）

**先加载 `univer` + 宿主 Unit skill + 源 Sheet/Base Unit skill。** 本 Skill 负责跨 Unit 外部源绑定 + 公式 + 计算 + 验证；宿主 Skill 负责坐标 + 内容 + 视觉行为。

跨 Unit 公式支持两类消费方：
- **Sheet 单元格**
- **Sheet / Doc / Slide / Board 的普通 Shape**（其显示文本来自公式结果）

## 公共 API 解析

写前先 `univer_api` 查：`FRange.setFormula` / `FShape.setFormula` / `FShape.getFormulaResult` / `FShape.removeFormula` / `FFormula.buildReference` / `FFormula.upsertExternalReference` / `FFormula.onCalculationResultApplied`。

**用显式宿主 + 源 handle。不要用 `getActive*()`。** 按 `univer_status` 选的 Unit ID 解析，例如 `univerAPI.getWorkbook(hostUnitId)` / `univerAPI.getWorkbook(sourceUnitId)` / `univerAPI.getBase(sourceUnitId)`。

## 引用规则

- 调用方提供源 Unit。`buildReference()` 序列化引用，不发现 Unit
- 用 `sourceUnit.getName()` 作 `formulaQualifier`（公式按名寻址，metadata 保稳定 ID）
- `SHEET_RANGE` 用于 Sheet 范围，`TABLE_COLUMN` 用于 Base 表列
- 让 `buildReference()` 负责 Unit/sheet/table/column 名字的引号转义
- Sheet 单元格和 formula-driven Shape 读宿主的 external-reference metadata
- 单元格直接读持久映射；Shape 在 `setFormula()` 时同时收公式 + 完整源身份
- **改前订阅 calculation 完成事件，写后 await**

## Sheet 源绑定

```js
const hostUnit = univerAPI.getWorkbook("<host-sheet-unit-id>");
const hostSheet = hostUnit.getSheetByName("Dashboard");
const sourceUnit = univerAPI.getWorkbook("<source-sheet-unit-id>");
const sourceSheet = sourceUnit.getSheetByName("Orders");

const formula = univerAPI.getFormula();
const reference = formula.buildReference({
  hostUnitId: hostUnit.getId(),
  unit: { unitId: sourceUnit.getId(), formulaQualifier: sourceUnit.getName() },
  target: {
    kind: univerAPI.Enum.FormulaReferenceType.SHEET_RANGE,
    sheetName: sourceSheet.getSheetName(),
    range: { startRow: 1, endRow: 3, startColumn: 1, endColumn: 1 },
  },
});
```

## Sheet 单元格消费方

```js
const targetCell = hostSheet.getRange("C1");
const applied = formula.onCalculationResultApplied(30_000);
targetCell.setFormula(`=SUM(${reference})`);
await applied;
```

## Formula-driven Shape 消费方

```js
const shape = hostSheet.insertShape({
  shapeType: univerAPI.Enum.ShapeTypeEnum.Rect,
  transform: { left: 700, top: 240, width: 280, height: 72 },
});
const applied = formula.onCalculationResultApplied(30_000);
shape.setFormula({
  formula: `=SUM(${reference})`,
  externalReferences: [{
    qualifier: sourceUnit.getName(),
    sourceUnitId: sourceUnit.getId(),
    sourceUnitType: univerAPI.Enum.UniverInstanceType.UNIVER_SHEET,
  }],
});
await applied;
const result = shape.getFormulaResult();
if (result?.status !== univerAPI.Enum.FormulaShapeResultStatus.SUCCESS) {
  throw new Error(`Formula-driven Shape failed: ${JSON.stringify(result)}`);
}
return { shapeId: shape.getId(), formula: shape.getFormula(), result };
```

## Base 源绑定

```js
const sourceUnit = univerAPI.getBase("<source-base-unit-id>");
const reference = univerAPI.getFormula().buildReference({
  hostUnitId: hostUnit.getId(),
  unit: { unitId: sourceUnit.getId(), formulaQualifier: sourceUnit.getName() },
  target: {
    kind: univerAPI.Enum.FormulaReferenceType.TABLE_COLUMN,
    tableName: "Budget",
    columnName: "Amount",
  },
});
```

- `tableName` 必须是源 Base 的真实 OOXML formula 标识符；`columnName` 是真实字段名
- **永远不要把 `table` 当占位符**
- Shape 用 `UNIVER_BASE` 在 `externalReferences`

## 宿主 Shape 差异

| 宿主 | 创建 Shape | 按稳定 ID 读 |
|---|---|---|
| Sheet | `worksheet.insertShape(...)` | `worksheet.getShape(shapeId)` |
| Doc | `document.insertShape(...)` | `document.getShape(shapeId)` |
| Slide | `slide.insertShape(...)` | `slide.getShape(shapeId)` |
| Board | `board.insertShape(...)` | `board.getShape(shapeId)` |

live Shape 一旦存在，公式 API 一致。**完全限定源**，行为不依赖隐式 active 上下文。

## 更新与移除

- `FRange.setFormula()` 替换单元格公式
- `FShape.setFormula()` 替换 Shape 公式
- 改源前订阅 `onCalculationResultApplied`，再 await

公式驱动 Shape 的格式：`setFormulaNumberFormat`。动画控制：`setFormulaAnimationEnabled`。`shape.removeFormula()` 转成普通 Shape 保留内容/样式；要彻底删 Shape 用宿主删除。

## 验收（最终 mutation 后）

1. 单元格：fresh range，断言精确公式 + 期望缓存值
2. Shape：用稳定 ID 断言 `isFormulaShape()` + 精确公式 + 成功 result（含 raw value/display text/number format）
3. 改一个被引用源值，await 计算，证明消费方随之变
4. inspect 宿主 + 源 Unit，按宿主 Skill 的 `univer_screenshot` 流程确认选中单元格/Shape 渲染、UI 响应、几何/格式/裁剪正确
   - 浏览器能否解析未加载的外部源取决于产品；**除非捕获 View 真正解析**，否则不要声称视觉更新
5. 按 `univer` ready/status 流程交付

## 上游原文指针

- 完整 SKILL.md：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-cross-unit-formula/SKILL.md>
