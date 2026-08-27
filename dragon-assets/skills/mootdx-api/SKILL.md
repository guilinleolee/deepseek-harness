---
name: mootdx-api 免费实时行情接口
description: |
  Mootdx API - 免费A股实时行情接口 skill
  支持实时行情/分时数据/盘口数据
  零门槛，无需注册，完全免费
  用于天龙引擎投资中心数据底座
  触发: @mootdx
version: 1.0.0
category: dragon-engine-data-免费数据
author: 天龙引擎团队
source: tongmuye项目提取 + mootdx (MIT)
created: 2026-08-18
dependencies:
  - python >= 3.8
  - mootdx
  - pandas
---

# Mootdx API Skill

> **免费实时行情接口** | 开源 · 实时数据 · 零门槛
> **License**: MIT
> **数据源**: 通达信/东方财富

---

## 概述

Mootdx 是免费 A 股实时行情接口，支持实时行情、分时数据、盘口数据等。

## 安装

```bash
pip install mootdx pandas
```

## 快速开始

### 实时行情

```python
from mootdx import Reader

reader = Reader()
df = reader.daily(code='600519')
print(df.head())
```

### 分时数据

```python
from mootdx import Reader

reader = Reader()
df = reader.minute(code='600519')
print(df.head())
```

### 盘口数据

```python
from mootdx import Reader

reader = Reader()
df = reader.bidAsk(code='600519')
print(df.head())
```

### Agent 调用示例

```python
from mootdx_runtime import MootdxRuntime

runtime = MootdxRuntime()

# 获取实时行情
df = runtime.get_daily("600519")

# 获取分时数据
df = runtime.get_minute("600519")

# 获取盘口数据
df = runtime.get_bidask("600519")
```

## 核心接口

### 数据读取

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `daily` | 日线数据 | code, start, end |
| `minute` | 分时数据 | code |
| `bidAsk` | 盘口数据 | code |
| `realtime` | 实时行情 | code |

### 数据源

| 方法 | 说明 |
|------|------|
| `Bestpay` | 电信天翼 |
| `Zhang` | 张大霄 |
| `Tdx` | 通达信 |

## 代码规则

### A股股票代码

| 市场 | 前缀 | 示例 |
|------|------|------|
| 上交所 | sh | sh600519 |
| 深交所 | sz | sz000858 |

## 与 Baostock 对比

| 维度 | Mootdx | Baostock |
|------|--------|----------|
| **实时性** | ✅ 实时 | 日线为主 |
| **数据类型** | 实时/分时/盘口 | 历史日线 |
| **数据范围** | A股 | A股 |
| **使用场景** | 实时监控 | 历史分析 |

## 下游岗位

| 岗位 | 用途 |
|------|------|
| 65-01 市场复盘分析师 | 实时行情监控 |
| 65-02 个股档案分析师 | 实时价格获取 |

## 参考文档

- [references/code-map.md](references/code-map.md) - 代码映射表
- [references/method-guide.md](references/method-guide.md) - 方法使用指南

## 来源

- Mootdx: https://github.com/mootdx/mootdx
- Tongmuye: D:\tongmuye 项目提取
