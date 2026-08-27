---
name: univer-base
description: Create, edit, calculate, inspect, export, and review Univer Base database Units through DSH tools and the Lite Interface. Use proactively for Base tables, fields, records, views, Formula fields, structured references, Sheet-backed external references, Base import/export, or any Base Unit task.
metadata:
  source: dream-num/dsh-univer-office v0.2.9 (Apache-2.0)
  mirrored: 2026-08-26
  version_upstream: 0.2.9
---

> **Apache-2.0 镜像说明**：本文件是上游 `dream-num/dsh-univer-office` 仓库 `skills/univer-base/SKILL.md` 的镜像。
> **完整上游文件**：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-base/SKILL.md>

---

# Univer Base Units（镜像摘要）

**先加载 `univer`。** Base 用 `univer_unit` 在 draft worktree 创建，用返回的 `unitId` 做后续所有操作。在 `univer_execute` 内用 `univerAPI.getBase(unitId)` 拿 Base。

未知 API 先 `univer_api`（`FUniver.createBase` / `FUniver.getBase` / `FBase` / table / field / record / view）。Facade 改完读回模型，按核心 ready/status 交付。

## Base 公式字段（OOXML 结构化引用）

Base Formula 字段必须用精确的 Excel 结构化引用：

- `Table[[#This Row],[Column]]` 或 `Table[@[Column]]` 读当前记录行的某字段
- `Table[[#Data],[Column]]` 或 `Table[Column]` 读完整数据列
- 无前缀 `[@[Column]]` 只在当前 Host 表行有效
- `table[Column]` 无效（除非 `table` 就是真实表名）

每个表的公式标识符用 `table.getFormulaName()` 拿，可能与 display name 不同。

```js
const ordersName = orders.getFormulaName();
orders.addField("Line Total", univerAPI.Enum.BaseFieldType.Formula, {
  field: {
    config: {
      formula: `=${ordersName}[[#This Row],[Quantity]]*${pricingName}[[#This Row],[Unit Price]]`,
    },
  },
  externalReferences: [],
});
```

跨表 `Table[[#This Row],[Column]]` 对齐靠行位置 —— 只在两表刻意共享行顺序时用。关系数据用稳定 key 或 RecordLink + 查找逻辑。

**写完 Formula 字段**先订阅 calculation 完成事件再触发改动，await 后读计算后的记录值。**仅公式文本不算证据。**

## 含 Sheet 源的 Formula 字段

持久化完整的 external-reference 绑定：

```js
table.addField("Current Total", univerAPI.Enum.BaseFieldType.Formula, {
  field: {
    config: { formula: "=SUM('[Sales Source]Data'!B2:B4)" },
  },
  externalReferences: [
    {
      qualifier: "Sales Source",
      sourceUnitId: "<sheet-unit-id>",
      sourceUnitType: univerAPI.Enum.UniverInstanceType.UNIVER_SHEET,
    },
  ],
});
```

公式 qualifier 和绑定 qualifier 必须精确一致。复杂跨 Unit 公式同时加载 `univer-cross-unit-formula`。

## 验证（每次 mutation 后）

新只读 `univer_execute` 校验：
- Base 与 table ID
- table 显示名 + formula name
- field 名/类型/formula 源/external 绑定
- 记录值 + 计算结果
- view ID/类型/筛选/排序/分组/可见字段

然后 `univer_screenshot`（Base `unitId` + 选定 worktree/trunk + 显式 workspace output 目录）。检视返回的完整工作台 PNG —— Base 截图只接受通用参数，**不要**传 Sheet range / Slide pages / Board selectors。

Base 可通过 `univer_export` 导出为 `.xlsx/.csv/.tsv`。**导出前必须 await calculation + 完成读回。**

## 上游原文指针

- 完整 SKILL.md：<https://raw.githubusercontent.com/dream-num/dsh-univer-office/main/skills/univer-base/SKILL.md>
