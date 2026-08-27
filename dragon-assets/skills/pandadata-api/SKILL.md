---
name: pandadata-api A股数据接口
description: |
  Pandadata API - A股/港股/美股金融数据接口 skill
  支持 Claude Code/Codex、Cursor、OpenAI 多平台
  用于天龙引擎投资中心数据底座，支持 65-01/65-02 岗位
  触发: @pandadata
version: 1.0.0
category: dragon-engine-data-投资数据
author: 天龙引擎团队
source: quantskills/skill-pandadata-api (GPL-3.0)
created: 2026-08-18
dependencies:
  - python >= 3.10
  - requests
---

# Pandadata API Skill

> **Codex Skill** | 整合自 [quantskills/skill-pandadata-api](https://github.com/quantskills/skill-pandadata-api)
> **License**: GPL-3.0
> **多平台支持**: Claude Code / Codex · Cursor · OpenAI

---

## 概述

Pandadata API 是一个金融数据接口服务，提供 A 股、港股、美股等市场的行情、财务、资金流、研报等数据。本 Skill 提供统一调用接口，支持多种 Agent 环境。

## 安装

```bash
# Claude Code / Codex
cp -r skill-pandadata-api ~/.claude/skills/pandadata-api

# Cursor
mkdir -p .cursor/skills
cp -r skill-pandadata-api .cursor/skills/pandadata-api

# OpenAI
mkdir -p ~/.openai/skills
cp -r skill-pandadata-api ~/.openai/skills/pandadata-api
```

## 环境配置

### API Key

设置环境变量：

```bash
export PANDADATA_API_KEY="your-api-key"
```

### Python 依赖

```bash
pip install requests pandas
```

## 快速开始

### 基础调用

```python
from pandadata_runtime import PandadataRuntime

runtime = PandadataRuntime()

# 获取股票日线数据
result = runtime.call("get_stock_daily", code="600519", date="2026-08-18")

# 获取资金流向
result = runtime.call("get_money_flow", code="600519", date="2026-08-18")
```

### Agent 调用示例

```python
# Claude Code / Codex
from pandadata_runtime import PandadataRuntime

runtime = PandadataRuntime()

# 65-02 个股档案 - 获取多维度数据
def get_stock_dossier(code: str) -> dict:
    """生成个股档案数据"""
    return {
        "basic": runtime.call("get_stock_detail", code=code),
        "daily": runtime.call("get_stock_daily", code=code),
        "money_flow": runtime.call("get_money_flow", code=code),
        "valuation": runtime.call("get_fina_indicator", code=code),
        "financial": runtime.call("get_fina_report", code=code),
        "research": runtime.call("get_research_report", code=code),
        "margin": runtime.call("get_margin", code=code),
    }
```

## 核心接口

### 行情数据

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `get_stock_daily` | 个股日线数据 | code, date |
| `get_stock_rt_daily` | 实时行情 | code |
| `get_stock_detail` | 股票基本信息 | code |
| `get_index_daily` | 指数日线 | date |
| `get_trade_cal` | 交易日历 | year, month |
| `get_trade_list` | 交易列表 | date |

### 资金流向

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `get_money_flow` | 资金流向 | code, date |
| `get_main_force` | 主力资金 | code, date |
| `get_stock_pledge_ratio` | 质押比例 | code |

### 财务数据

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `get_fina_indicator` | 财务指标 | code |
| `get_fina_report` | 财务报表 | code, count |
| `get_profit_predict` | 盈利预测 | code |

### 龙虎榜

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `get_lhb_list` | 龙虎榜列表 | date |
| `get_lhb_detail` | 龙虎榜明细 | code, count |

### 融资融券

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `get_margin` | 融资融券 | code, date |

### 研报数据

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `get_research_report` | 研报汇总 | code |
| `get_fina_reports` | 研报列表 | code |
| `get_fina_performance` | 业绩预告 | code |
| `get_fina_forecast` | 业绩预测 | code |

### 公告数据

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `get_notice` | 重要公告 | code, count |
| `get_latest_notice` | 最新公告 | code |

## 接口调用规范

### 请求格式

```python
runtime.call(method_name, **kwargs)
```

### 响应格式

```python
{
    "code": 0,          # 0=成功, 非0=失败
    "message": "success",
    "data": {...}       # 返回数据
}
```

### 错误处理

```python
result = runtime.call("get_stock_daily", code="600519", date="2026-08-18")
if result["code"] != 0:
    print(f"Error: {result['message']}")
else:
    data = result["data"]
```

### 限流与重试

```python
import time

def call_with_retry(runtime, method, max_retries=3, **kwargs):
    """带重试的接口调用"""
    for i in range(max_retries):
        result = runtime.call(method, **kwargs)
        if result["code"] == 0:
            return result["data"]
        if "rate limit" in result.get("message", "").lower():
            time.sleep(2 ** i)  # 指数退避
        else:
            raise Exception(result["message"])
    raise Exception(f"Max retries ({max_retries}) exceeded")
```

## 数据日期规范

| 数据类型 | 日期格式 | 说明 |
|---------|---------|------|
| 实时数据 | `YYYY-MM-DD HH:MM:SS` | 包含时间 |
| 日线数据 | `YYYY-MM-DD` | 仅日期 |
| T+1数据 | `T-1` | 融资融券等 |
| 季报数据 | `YYYYQ1/2/3/4` | 季度格式 |

## 与 a-stock-data 的对比

| 维度 | pandadata-api | a-stock-data |
|------|--------------|--------------|
| **定位** | 分析层 API | 基础数据层 |
| **数据源** | Pandadata 聚合 | mootdx/东财/同花顺 |
| **接口数量** | ~60+ | ~43 A股 |
| **特色** | 研报/资金流 | 实时行情 |
| **适用场景** | 个股深度分析 | 批量行情获取 |

## 下游岗位

| 岗位 | 用途 |
|------|------|
| 65-01 市场复盘分析师 | 每日复盘数据 |
| 65-02 个股档案分析师 | 个股多维度数据 |
| 28-10 财经数据底座师 | 金融数据底座 |

## 参考文档

- [references/api_catalog.json](references/api_catalog.json) - API 完整目录
- [references/method-index.md](references/method-index.md) - 方法索引
- [references/agent-integration.md](references/agent-integration.md) - Agent 集成指南

## 许可证

本项目基于 GPL-3.0 许可证，源自 [quantskills/skill-pandadata-api](https://github.com/quantskills/skill-pandadata-api)。
