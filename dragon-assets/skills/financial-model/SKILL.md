---
license: UNKNOWN
name: financial-model
version: 1.0.0
description: |
  财务模型Excel构建：三表联动(BS/IS/CF)、场景分析(scenario)、DCF/WACC估值、敏感性分析。支持LBO/Comps/DCF模型，与天龙60-01投资总监深度集成，遵循xlsx技能颜色编码标准。
author: 天龙引擎团队
created: 2026-05-09
category: finance
triggers:
  - "用户提到「财务模型 financial model」时"
  - "用户提到「DCF估值 DCF valuation」时"
  - "用户提到「三表联动 BS/IS/CF」时"
  - "用户提到「LBO模型 LBO model」时"
---

# Financial Model - 财务模型Excel构建

## Overview

财务模型是投资决策的核心工具。本技能提供三表联动、估值分析、敏感性分析等完整财务建模能力，与天龙xlsx技能深度集成。

## 模型类型

### DCF (Discounted Cash Flow)

```bash
# 创建DCF模型
financial-model new --type dcf --company "示例公司"

# DCF组件
# - 收入假设
# - 成本假设
# - 折旧摊销
# - 资本支出
# - 营运资金
# - 自由现金流
# - 终值
# - WACC
# - 估值
```

### LBO (Leveraged Buyout)

```bash
# 创建LBO模型
financial-model new --type lbo --target "目标公司"

# LBO组件
# - 交易结构
# - 融资方案
# - 股权回报分析
# - 债务偿还计划
# - 退出分析
```

### Comps (Trading Comparables)

```bash
# 创建可比公司模型
financial-model new --type comps --sector "科技"

# Comps组件
# - 可比公司筛选
# - 交易倍数
# - 财务比率
# - 估值区间
```

## 三表联动

### 资产负债表 (Balance Sheet)

```bash
# 创建BS
financial-model bs --company "示例" --currency CNY

# BS结构
# - 流动资产
#   - 货币资金
#   - 应收账款
#   - 存货
# - 非流动资产
#   - 固定资产
#   - 无形资产
# - 流动负债
# - 非流动负债
# - 所有者权益
```

### 利润表 (Income Statement)

```bash
# 创建IS
financial-model is --company "示例" --currency CNY

# IS结构
# - 营业收入
# - 营业成本
# - 毛利
# - 期间费用
# - 营业利润
# - 所得税
# - 净利润
```

### 现金流量表 (Cash Flow)

```bash
# 创建CF
financial-model cf --company "示例" --currency CNY

# CF结构
# - 经营活动现金流
# - 投资活动现金流
# - 筹资活动现金流
# - 现金及等价物变动
```

### 联动机制

```bash
# 建立联动
financial-model link --bs "BS" --is "IS" --cf "CF"

# 联动规则
# IS净利润 → BS未分配利润
# BS固定资产变化 → CF资本支出
# BS借款变化 → CF筹资
```

## 场景分析 (Scenario Analysis)

```bash
# 创建场景
financial-model scenario new --name "乐观" --revenue-growth 15%

# 场景类型
# - 乐观场景
# - 基准场景
# - 悲观场景
# - 自定义场景

# 场景切换
financial-model scenario switch --name "乐观"

# 场景对比
financial-model scenario compare --scenarios "乐观,基准,悲观"
```

## 估值分析

### WACC计算

```bash
# 计算WACC
financial-model wacc --re 12% --rd 5% --tax-rate 25% --debt-ratio 40%

# WACC公式
# WACC = E/V × Re + D/V × Rd × (1-T)
```

### DCF估值

```bash
# DCF估值
financial-model dcf --fcfs "forecast.xlsx" --wacc 10% --terminal-growth 3%

# 输出
# - 预测期现金流
# - 终值
# - 现值汇总
# - 估值区间
```

### 敏感性分析

```bash
# 敏感性分析
financial-model sensitivity --var "wacc,terminal-growth" --range "8-14%,2-5%"

# 输出热力图
#        | WACC 8% | WACC 10% | WACC 12% | WACC 14%
# TG 2% |  100     |   85      |   72      |   62
# TG 3% |  115     |   95      |   80      |   68
# TG 4% |  132     |  108      |   89      |   75
# TG 5% |  152     |  123      |  100      |   84
```

## 颜色编码标准

遵循天龙xlsx技能标准：

| 颜色 | 含义 | 示例 |
|------|------|------|
| **蓝色** (RGB:0,0,255) | 硬编码输入 | 增长率、市盈率 |
| **黑色** (RGB:0,0,0) | 公式计算 | =SUM(B2:B9) |
| **绿色** (RGB:0,128,0) | 同文件跨表引用 | =IS!B10 |
| **红色** (RGB:255,0,0) | 外部文件引用 | ='[外部.xlsx]Sheet1'!A1 |
| **黄色背景** | 需关注假设 | 关键输入 |

## 输出格式

### 数字格式

```bash
# 金额格式
# $#,##0 (百万)
# $#,##0;($#,##0);- (含负数)

# 百分比
# 0.0% (一位小数)

# 倍数
# 0.0x (EV/EBITDA)

# 零值显示
# 零值显示为 "-"
```

### 文档注释

```bash
# 添加来源注释
# Source: [系统/文档], [日期], [具体参考], [URL]
```

## 天龙引擎协同

| 天龙岗位 | 协同方式 |
|---------|---------|
| **60-01投资总监** | 估值建模→投资决策 |
| **17-01数据分析师** | 财务分析→数据验证 |
| **07记录师** | 模型说明→文档归档 |

## 依赖要求

- openpyxl (Excel操作)
- pandas (数据分析)
- recalc.py (公式重算，必须执行)
- LibreOffice (公式验证)

## Evolution Pattern

To preserve custom improvements when this skill is upgraded, maintain an `evolution.json` file in the skill directory.
