---
license: UNKNOWN
name: data-dashboard-excel
version: 1.0.0
description: |
  Excel数据看板构建：KPI卡片布局、动态图表、数据刷新、格式自动化。支持Excel原生格式，与天龙xlsx技能深度集成，遵循天龙财务模型颜色编码标准。
author: 天龙引擎团队
created: 2026-05-09
category: visualization
triggers:
  - "用户提到「数据看板 data dashboard」时"
  - "用户提到「KPI卡片」时"
  - "用户提到「管理仪表盘 management dashboard」时"
  - "用户提到「Excel可视化」时"
---

# Data Dashboard Excel - Excel数据看板

## Overview

数据看板是管理决策的核心工具。本技能提供KPI卡片、动态图表、数据刷新等完整能力，与天龙xlsx技能深度集成。

## KPI卡片

### 创建KPI卡片

```bash
# 创建KPI卡片
data-dashboard-excel kpi create --name "收入" --value "1000万" --change "+15%" --trend "up"

# KPI卡片结构
# ┌──────────────────────┐
# │  收入                │
# │  ¥10,000,000        │
# │  ▲ +15% vs 上月      │
# └──────────────────────┘
```

### KPI类型

```bash
# 数值型KPI
data-dashboard-excel kpi number --name "用户数" --value 10000 --unit "人" --format "#,##0"

# 百分比型KPI
data-dashboard-excel kpi percent --name "毛利率" --value 35.5 --change "+2.3pp"

# 货币型KPI
data-dashboard-excel kpi currency --name "月收入" --value 1500000 --currency "¥"

# 比率型KPI
data-dashboard-excel kpi ratio --name "LTV/CAC" --value 3.5 --target "3.0"

# 时间型KPI
data-dashboard-excel kpi time --name "平均交付周期" --value 5.2 --unit "天"
```

### KPI状态指示

```bash
# 红绿状态
data-dashboard-excel kpi status --value 85 --target 80 --type "达成率"

# 趋势箭头
data-dashboard-excel kpi trend --value 120 --lastMonth 100 --trend "up"

# 仪表盘指示
data-dashboard-excel kpi gauge --value 75 --max 100 --zones "0-60红,60-80黄,80-100绿"
```

## 动态图表

### 图表类型

```bash
# 创建动态图表
data-dashboard-excel chart create --type "柱形图" --data "A1:B12" --title "月度收入趋势"

# 支持图表类型
# - 柱形图/条形图
# - 折线图
# - 面积图
# - 饼图/环形图
# - 组合图
# - 漏斗图
# - 仪表盘图
# - 迷你图 (sparklines)
```

### 动态数据源

```bash
# 定义数据源
data-dashboard-excel datasource define --name "月度销售" --range "销售!A:D" --refresh "每5分钟"

# 数据验证下拉
data-dashboard-excel dropdown create --cell "A1" --source "数据源!A1:A10"

# 动态图表绑定
data-dashboard-excel chart bind --name "月度销售" --chart "折线图"
```

### 迷你图

```bash
# 创建迷你图
data-dashboard-excel sparkline create --range "D1:D10" --data "B1:B10" --type "trend"

# 迷你图类型
# - trend: 趋势迷你图
# - winloss: 盈亏迷你图
# - column: 柱形迷你图
```

## 数据刷新

### 自动刷新设置

```bash
# 设置自动刷新
data-dashboard-excel refresh auto --interval 5 --unit minutes

# 刷新触发器
# - 打开文件时刷新
# - 定时刷新
# - 手动刷新（按钮）
# - VBA触发刷新
```

### 数据连接管理

```bash
# 创建数据连接
data-dashboard-excel connection create --type "CSV" --path "data/sales.csv"

# 支持连接类型
# - CSV文件
# - Excel文件
# - 数据库（ODBC）
# - Web查询
# - Power Query

# 刷新所有连接
data-dashboard-excel refresh all

# 刷新指定连接
data-dashboard-excel refresh connection --name "销售数据"
```

### VBA刷新代码

```bash
# 生成刷新代码
data-dashboard-excel vba refresh --connections "销售,库存"

# VBA代码示例
# Sub RefreshAll()
#     ThisWorkbook.RefreshAll
# End Sub
```

## 格式自动化

### 主题应用

```bash
# 应用主题
data-dashboard-excel theme apply --name "企业仪表盘"

# 内置主题
# - 企业仪表盘（蓝色系）
# - 销售看板（绿色系）
# - 财务看板（金色系）
# - 运营看板（橙色系）
# - 自定义主题
```

### 条件格式联动

```bash
# KPI状态格式
data-dashboard-excel format kpi --range "A1:D10" --type "status"

# 图表颜色联动
data-dashboard-excel format chart-link --chart "图表1" --thresholds "0-60-80-100"
```

### 自动化格式模板

```bash
# 使用模板
data-dashboard-excel template apply --name "销售日报" --data "销售数据.xlsx"

# 生成模板代码
data-dashboard-excel template generate --type "管理看板"
```

## 看板布局

### 页面布局

```bash
# 创建看板页面
data-dashboard-excel page create --name "销售看板" --layout "仪表盘"

# 布局类型
# - 仪表盘（全屏KPI）
# - 报告（KPI+图表+表格）
# - 运营（实时数据+告警）
```

### 区域划分

```bash
# 定义看板区域
data-dashboard-excel layout region --name "KPI区" --cells "A1:D4"
data-dashboard-excel layout region --name "图表区" --cells "A5:D12"
data-dashboard-excel layout region --name "明细区" --cells "E1:L20"

# 冻结窗格
data-dashboard-excel freeze set --cell "A5"
```

### 响应式设计

```bash
# 设置打印区域
data-dashboard-excel print area --range "A1:L25"

# 分页设置
data-dashboard-excel print page --orientation "横向" --fit 1页宽

# 页眉页脚
data-dashboard-excel print header --left "报表名称" --center "页码" --right "日期"
```

## 常见看板模板

### 销售管理看板

```
┌─────────────────────────────────────────────────────────────┐
│ 销售管理看板                                                │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│ │ 本月收入 │ │ 销售目标│ │ 完成率  │ │ 同比增速│          │
│ │ ¥120万  │ │ ¥150万  │ │ 80%    │ │ +15%   │          │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────┐ ┌──────────────────────────┐  │
│ │ 月度收入趋势             │ │ 产品销量排行              │  │
│ │ [折线图]                │ │ [柱形图]                │  │
│ └──────────────────────────┘ └──────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────┐ ┌──────────────────────────┐  │
│ │ 地区销售分布             │ │ TOP10客户               │  │
│ │ [饼图]                  │ │ [表格]                  │  │
│ └──────────────────────────┘ └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 财务看板

```
┌─────────────────────────────────────────────────────────────┐
│ 财务看板                                                    │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│ │ 营收     │ │ 毛利率  │ │ 净利润  │ │ 现金流  │          │
│ │ ¥500万   │ │ 35%    │ │ ¥80万   │ │ ¥120万  │          │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────┐    │
│ │ 收入成本趋势 [组合图]                                 │    │
│ └──────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│ │ 资产负债表摘要│ │ 利润表摘要   │ │ 现金流量表  │       │
│ │ [迷你表]     │ │ [迷你表]    │ │ [迷你表]    │       │
│ └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 运营看板

```
┌─────────────────────────────────────────────────────────────┐
│ 运营看板                                                    │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│ │ DAU     │ │ 活跃率  │ │ 转化率  │ │ 留存率  │          │
│ │ 12.5万  │ │ 68%    │ │ 3.5%   │ │ 45%    │          │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────┐ ┌──────────────────────────┐  │
│ │ 用户活跃趋势             │ │ 漏斗转化                 │  │
│ │ [折线图]                │ │ [漏斗图]                │  │
│ └──────────────────────────┘ └──────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────┐    │
│ │ 实时告警 [表格+条件格式]                              │    │
│ └──────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 命令速查

```bash
# KPI卡片
data-dashboard-excel kpi create --name "指标名" --value 1000 --change "+10%"
data-dashboard-excel kpi status --value 85 --target 80

# 动态图表
data-dashboard-excel chart create --type "柱形图" --data "A1:B10"
data-dashboard-excel datasource define --name "数据源" --range "Sheet!A:D"

# 数据刷新
data-dashboard-excel refresh auto --interval 5
data-dashboard-excel connection create --type "CSV" --path "data.csv"

# 格式自动化
data-dashboard-excel theme apply --name "企业仪表盘"
data-dashboard-excel format kpi --range "A1:D10"

# 看板布局
data-dashboard-excel page create --name "看板名" --layout "仪表盘"
data-dashboard-excel layout region --name "区域名" --cells "A1:D4"

# 导出
data-dashboard-excel export --format xlsx --password "密码"
```

## 天龙引擎协同

| 天龙岗位 | 协同方式 |
|---------|---------|
| **17-01数据分析师** | 数据看板+可视化分析 |
| **60-01投资总监** | 投资看板+财务指标 |
| **64-01量化研究员** | 策略看板+绩效追踪 |
| **excel-advanced** | 动态图表+数据透视表 |
| **financial-model** | 三表联动+财务数据 |

## 依赖要求

- openpyxl (Excel操作)
- xlsxwriter (图表生成)
- pandas (数据处理)
- pywin32 (自动刷新，Windows)
