---
name: univer-sheet
description: Read, write, format, calculate, and verify Univer Sheet Units through DSH tools and the Lite Interface. Use proactively for spreadsheet values, formulas, ranges, tables, charts, images, formatting, validation, filters, pivots, rich text, xlsx/csv/tsv import or export, and any Sheet Unit task.
metadata:
  source: dream-num/dsh-univer-office v0.2.9 (Apache-2.0)
  mirrored: 2026-08-26
  version_upstream: 0.2.9
---

> **Apache-2.0 镜像说明**：本文件是上游 `dream-num/dsh-univer-office` 仓库 `skills/univer-sheet/SKILL.md` 的镜像。
> **完整上游文件**：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-sheet/SKILL.md>

---

# Univer Sheet Units（镜像摘要）

**先加载 `univer`。** `univer_execute` 注入 `univerAPI` / `api` / `workbook`（按 unitId 选的 `FWorkbook`）。**不要重新声明。** 执行环境是 ESM，无 `require`。

用 `workbook.getActiveSheet()` 或 `workbook.getSheetByName("…")` 拿 worksheet。**用 `getSheetName()`**；`FWorksheet` 没有 `getName()`。未知 API 先 `univer_api`。

## 单元格模型：v / t / f / s

```js
{ v: "text", t: 1 }                    // 文本
{ v: 42, t: 2 }                        // 数字
{ v: 1, t: 3 }                         // 布尔
{ v: "00123", t: 4 }                   // 强制文本
{ f: "=A1+B1" }                        // 公式
{ v: "=A1+B1", t: 4 }                  // 强制文本形式
```

- 日期/百分比/货币：数字 + `s.n.pattern` 格式
- 富文本：在 `cell.p`，**不要手写内部结构**，用 `api.newRichText()`
- `displayValue` 是显示文本，**不要写回 `v`**

## 关键 API 速查

- **范围**：`sheet.getRange("A1:C9")` 或 `getRange(row, col, numRows, numCols)`（0 基）
- **表**：`getActiveSheet()` / `getSheetByName()` / `getSheets()`
- **权威读**：`getCellData()` / `getCellDatas()` / `getRawValues()`
- **展示读**：`getDisplayValues()` / `getFormula()`
- **写**：`setValue()` / `setValues(grid)` / `setFormula()` / `clearContent()` / `clear()`
- **维度**：`getLastRow()` / `getLastColumn()` / `setRowCount(n)`（越界前必调）
- **样式**：颜色必须 `#RRGGBB` 或 `rgb(r,g,b)`

**⚠️ `setValues()` 是合并操作** —— `{}` 或 `{ s }` 不会清掉已有 `v/f/p`。要替换区域先 `clearContent()` 再 `setValues()`。

## 公式重算（关键陷阱）

```js
const calculated = api.getFormula().onCalculationResultApplied();
api.getFormula().executeCalculation();
await calculated;
```

**必须先订阅再触发。** 新写公式也要先订阅。**导出前必须重算**（xlsx 会把缓存值和公式一起存）。

## 富文本

```js
const rich = api.newRichText();
rich.insertText("Hello World");
rich.setStyle(0, 5, { bl: 1, cl: { rgb: "#FF0000" } });
workbook.getActiveSheet().getRange("A1").setRichTextValueForCell(rich);
```

`setStyle(start, end, style)` 是 **半开区间**。

## 验证（每次 mutation 后必走）

1. `univer_inspect` 带精确 unitId / worktree / range（如 `Sheet1!A1:D20`）
2. 校验 stored value / type / formula / display value / 行序 / 任务特定计算
3. 缺字段用新的只读 `univer_execute` 补读
4. **可视化相关改动**：调 `univer_screenshot`，逐张检视 PNG
5. **导出前重算并重读公式结果**
6. 按 `univer` 的 ready/status 流程交付

## 红线

- 🔴 写非公式单元格**必须**显式 `t`
- 🔴 不要用 `getValue()` / `getValues()` 做权威读 —— 格式值和布尔可能被转换
- 🔴 不要把显示文本写回 `v`
- 🔴 csv/tsv 导入后**必须**检查每列值类型 —— 混合值会让整列按文本导入

## 上游原文指针

- 完整 SKILL.md：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-sheet/SKILL.md>
