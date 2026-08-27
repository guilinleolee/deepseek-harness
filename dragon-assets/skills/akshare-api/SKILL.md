---
name: akshare-api 免费多市场数据接口
description: |
  AKShare API - 免费多市场金融数据接口 skill
  支持 A股/港股/美股/期货/外汇/基金/宏观
  零门槛，无需注册，完全免费
  用于天龙引擎投资中心数据底座
  触发: @akshare
version: 1.0.0
category: dragon-engine-data-免费数据
author: 天龙引擎团队
source: tongmuye项目提取 + akshare (MIT)
created: 2026-08-18
dependencies:
  - python >= 3.8
  - akshare
  - pandas
---

# AKShare API Skill

> **免费数据接口** | 开源 · 多市场 · 零门槛
> **License**: MIT
> **数据源**: 东方财富、同花顺、新浪财经等

---

## 概述

AKShare 是开源免费金融数据接口，支持 A股、港股、美股、期货、外汇、基金、宏观等多市场数据。

## 安装

```bash
pip install akshare pandas
```

## 快速开始

### 港股数据

```python
import akshare as ak

# 港股日线
df = ak.stock_hk_daily(symbol="00700", adjust="qfq")
print(df.head())
```

### 美股数据

```python
import akshare as ak

# 美股日线
df = ak.stock_us_daily(symbol="AAPL", adjust="qfq")
print(df.head())
```

### 期货数据

```python
import akshare as ak

# 期货日线
df = ak.futures_zh_daily_sina(symbol="rb2501")
print(df.head())
```

### Agent 调用示例

```python
from akshare_runtime import AKShareRuntime

runtime = AKShareRuntime()

# 获取港股
df = runtime.get_hk_daily("00700")

# 获取美股
df = runtime.get_us_daily("AAPL")

# 获取期货
df = runtime.get_futures_daily("rb2501")
```

## 核心接口

### 港股数据

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `stock_hk_daily` | 港股日线 | symbol, adjust |
| `stock_hk_spot_em` | 港股实时行情 | symbol |
| `stock_hk_hist` | 港股历史K线 | symbol, period, start_date, end_date |

### 美股数据

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `stock_us_daily` | 美股日线 | symbol, adjust |
| `stock_us_spot_em` | 美股实时行情 | symbol |
| `stock_us_hist` | 美股历史K线 | symbol, period |

### 期货数据

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `futures_zh_daily_sina` | 国内期货日线 | symbol |
| `futures_zh_spot` | 期货实时行情 | symbol |
| `futures_foreign` | 外盘期货 | symbol |

### 外汇数据

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `forex_usd_cny` | 美元兑人民币 | - |
| `forex_current` | 实时外汇 | symbol |
| `forex_hist` | 外汇历史 | symbol, period |

### 基金数据

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `fund_etf_hist_sina` | ETF历史 | symbol, period |
| `fund_fof_hist` | FOF基金历史 | symbol, period |

### 宏观数据

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `macro_china_money_supply` | 货币供应量 | - |
| `macro_china_gdp` | GDP数据 | - |
| `macro_china_cpi` | CPI数据 | - |

## 代码规则

### 港股代码

| 股票 | 代码 |
|------|------|
| 腾讯控股 | 00700 |
| 阿里巴巴 | 09988 |
| 美团 | 03690 |
| 小米集团 | 01810 |

### 美股代码

| 股票 | 代码 |
|------|------|
| 苹果 | AAPL |
| 特斯拉 | TSLA |
| 英伟达 | NVDA |
| 谷歌 | GOOGL |
| 亚马逊 | AMZN |

### 期货代码

| 品种 | 代码规则 | 示例 |
|------|---------|------|
| 螺纹钢 | rb + 年月 | rb2501 |
| 铁矿石 | i + 年月 | i2501 |
| 原油 | sc + 年月 | sc2501 |
| 黄金 | au + 年月 | au2501 |
| 白银 | ag + 年月 | ag2501 |

## 与 Baostock 对比

| 维度 | AKShare | Baostock |
|------|---------|----------|
| **A股市** | 支持 | ✅ 支持 |
| **港股** | ✅ 支持 | ❌ 不支持 |
| **美股** | ✅ 支持 | ❌ 不支持 |
| **期货** | ✅ 支持 | 部分支持 |
| **外汇** | ✅ 支持 | ❌ 不支持 |
| **宏观** | ✅ 支持 | ❌ 不支持 |
| **实时** | ✅ 支持 | ❌ 不支持 |

## 下游岗位

| 岗位 | 用途 |
|------|------|
| 65-02 个股档案分析师 | 港股/美股数据 |
| 28-10 财经数据底座师 | 多市场数据采集 |

## 参考文档

- [references/code-map.md](references/code-map.md) - 代码映射表
- [references/method-guide.md](references/method-guide.md) - 方法使用指南

## 来源

- AKShare: https://github.com/akfamily/akshare
- Tongmuye: D:\tongmuye 项目提取
