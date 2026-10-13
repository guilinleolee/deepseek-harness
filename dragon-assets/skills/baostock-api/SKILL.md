---
name: baostock-api 免费A股数据接口
description: |
  Baostock API - A股免费金融数据接口 skill
  零门槛，无需注册，完全免费
  用于天龙引擎投资中心数据底座，支持 65-01/65-02 岗位
  触发: @baostock
version: 1.0.0
category: dragon-engine-data-免费数据
author: 天龙引擎团队
source: tongmuye项目提取 + baostock (BSD-3-Clause)
created: 2026-08-18
dependencies:
  - python >= 3.8
  - baostock
  - pandas
---

# Baostock API Skill

> **免费数据接口** | 零门槛 · 无需注册 · 完全免费
> **License**: BSD-3-Clause
> **数据源**: 东方财富网

---

## 概述

Baostock 是免费 A 股金融数据接口，无需注册、无需 API Key，直接安装即可使用。数据来源于东方财富网。

## 安装

```bash
pip install baostock pandas
```

## 快速开始

### 基础调用

```python
import baostock as bs
import pandas as pd

# 登录（每次使用前登录）
lg = bs.login()
print(f"登录结果: {lg.error_msg}")

# 查询日线数据
rs = bs.query_history_k_data_plus(
    "sh.600519",  # 股票代码
    "date,code,open,high,low,close,volume",
    start_date='2026-01-01',
    end_date='2026-08-18',
    frequency="d",  # 日线
    adjustflag="2"  # 前复权
)

# 转换为 DataFrame
data_list = []
while rs.error_code == '0' and rs.next():
    data_list.append(rs.get_row_data())
df = pd.DataFrame(data_list, columns=rs.fields)

# 登出
bs.logout()
```

### Agent 调用示例

```python
from baostock_runtime import BaostockRuntime

runtime = BaostockRuntime()

# 获取股票日线
df = runtime.get_stock_daily("600519", days=30)

# 获取指数数据
df = runtime.get_index_daily("000001", days=60)

# 获取财务数据
df = runtime.get_fina_indicator("600519")
```

## 核心接口

### 行情数据

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `query_history_k_data_plus` | 个股/指数历史K线 | code, start_date, end_date, frequency, adjustflag |
| `query_trade_dates` | 交易日历 | start_date, end_date |
| `query_stock_basic` | 股票列表 | code |

### 财务数据

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `query_fina_indicator` | 财务指标 | code, start_date, end_date |
| `query_fina_statements` | 财务报表 | code, start_date, end_date, statement_type |
| `query_dividend_data` | 分红数据 | code, year |
| `query_rights_issue_data` | 配股数据 | code, year |

### 基金/期货

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `query_fund_basic` | 基金列表 | code |
| `query_fund_nav` | 基金净值 | code |
| `query_future_daily` | 期货日线 | code, start_date, end_date |

## 代码规则

### A股股票代码

| 市场 | 前缀 | 示例 |
|------|------|------|
| 上交所 | sh. | sh.600519 (茅台) |
| 深交所 | sz. | sz.000858 (五粮液) |
| 北交所 | bj. | bj.873001 (N樱花园) |

### 指数代码

| 指数 | 代码 |
|------|------|
| 上证指数 | sh.000001 |
| 深证成指 | sz.399001 |
| 沪深300 | sh.000300 |
| 创业板指 | sz.399006 |
| 上证50 | sh.000016 |
| 中证500 | sh.000905 |

### K线周期

| frequency | 说明 |
|-----------|------|
| d | 日K线 |
| w | 周K线 |
| m | 月K线 |
| 5 | 5分钟线 |
| 15 | 15分钟线 |
| 30 | 30分钟线 |
| 60 | 60分钟线 |

### 复权方式

| adjustflag | 说明 |
|------------|------|
| 1 | 不复权 |
| 2 | 前复权 |
| 3 | 后复权 |

## 错误处理

```python
rs = bs.query_history_k_data_plus(...)
if rs.error_code != '0':
    print(f"错误: {rs.error_msg}")
else:
    while rs.next():
        data = rs.get_row_data()
```

## 与其他数据源对比

| 维度 | baostock | akshare | a-stock-data |
|------|----------|---------|--------------|
| **费用** | 免费 | 免费 | 免费 |
| **注册** | 不需要 | 不需要 | 不需要 |
| **数据范围** | A股为主 | A/H/美/期货 | A股为主 |
| **实时性** | 日线/分钟 | 日线/实时 | 日线/实时 |
| **财务数据** | 完整 | 完整 | 完整 |

## 下游岗位

| 岗位 | 用途 |
|------|------|
| 65-01 市场复盘分析师 | 指数/涨跌家数 |
| 65-02 个股档案分析师 | 个股K线/财务数据 |
| 28-10 财经数据底座师 | 基础数据采集 |

## 参考文档

- [references/code-map.md](references/code-map.md) - A股代码映射表
- [references/method-guide.md](references/method-guide.md) - 方法使用指南

## 来源

- Baostock: https://github.com/baostock/baostock
- Tongmuye: D:\tongmuye 项目提取
