# Odoo Grid View v2 Specification

## 架构约束
Grid 视图用于多维数据展现（如考勤、库存）。

## 核心组件
- `<grid>`: 根元素。
- `<field name="row_name" type="row">`: 行维度。
- `<field name="col_name" type="col">`: 列维度。
- `<field name="value" type="measure">`: 聚合度量值。

## 防御性设计
- **Range Constraint**: 必须定义 `range_selection`，防止加载过大数据集。
- **Read-only Logic**: 非编辑状态下强制 `readonly="1"`。
- **JS Class**: 扩展功能必须继承 `GridView` 并处理 `onUpdate` 事件。
