---
license: UNKNOWN
github_repo: OpenBB-finance/OpenBB
github_hash: a08d5d75d00564f10503f915e4aab64119c50a13
last_updated: 2026-04-25
source_type: derived
triggers: ["openbb skill", "OpenBB Skill - 金融数据基础设施"]
---
# OpenBB Skill - 金融数据基础设施

## 概述

OpenBB 是开源金融数据基础设施层，支持 30+ 数据源、150+ 标准数据模型，覆盖股票、加密货币、ETF、宏观经济、固定收益、衍生品等资产类别。

## 核心能力

### 数据源支持（30+）

| 类型 | 提供者 | 数据内容 |
|------|--------|---------|
| **免费** | yfinance, sec, fred, ecb, nasdaq | 股票、财报、宏观数据 |
| **付费** | fmp, benzinga, intrinio | 实时行情、新闻、深度数据 |
| **专业** | tradingeconomics, tiingo | 全球宏观、另类数据 |

### 资产类别

- **股票**: 历史价格、财务报表、分析师预测、持仓、期权链
- **加密货币**: 价格历史、搜索、快照
- **ETF**: 持仓、历史净值、行业配置
- **宏观经济**: GDP、CPI、失业率、利率、央行数据
- **固定收益**: 国债收益率、债券指数
- **衍生品**: 期权链、期货曲线

## 安装

```bash
# 基础安装
pip install openbb

# 全部扩展
pip install "openbb[all]"

# 单独安装提供者
pip install openbb-yfinance openbb-fmp
```

## Python SDK 使用

### 基础用法

```python
from openbb import obb

# 股票历史数据
data = obb.equity.price.historical("AAPL", provider="yfinance")
df = data.to_df()

# 获取多个数据
prices = obb.equity.price.historical(["AAPL", "MSFT", "GOOGL"])
```

### 宏观数据

```python
# GDP
gdp = obb.economy.gdp(provider="fred")

# CPI
cpi = obb.economy.cpi(provider="fred")

# 国债收益率
rates = obb.economy.treasury_rates()

# 经济日历
calendar = obb.economy.calendar()
```

### 财务数据

```python
# 资产负债表
balance = obb.equity.fundamental.balance_sheet("AAPL", provider="fmp")

# 利润表
income = obb.equity.fundamental.income_statement("AAPL")

# 现金流量表
cashflow = obb.equity.fundamental.cash_flow("AAPL")
```

### 期权数据

```python
# 期权链
options = obb.derivatives.options.chains("AAPL")

# 期权定价
price = obb.derivatives.options.pricing("AAPL", "2024-12-20", 150, "call")
```

### ETF 数据

```python
# ETF 持仓
holdings = obb.etf.holdings("SPY")

# ETF 信息
info = obb.etf.info("SPY")
```

## REST API 服务

### 启动服务

```bash
pip install "openbb[all]"
openbb-api  # 启动 FastAPI 服务器
# 访问 http://127.0.0.1:6900
```

### API 端点

```bash
# 获取股票历史数据
curl "http://127.0.0.1:6900/api/v1/equity/price/historical?symbol=AAPL&provider=yfinance"

# 获取宏观数据
curl "http://127.0.0.1:6900/api/v1/economy/gdp?provider=fred"
```

## MCP Server 集成

### 配置 mcp_settings.json

```json
{
  "mcpServers": {
    "openbb": {
      "command": "python",
      "args": ["-m", "openbb_mcp_server"],
      "env": {}
    }
  }
}
```

### 安装 MCP Server

```bash
pip install openbb-mcp-server
```

## 投资岗位集成

### 60-01 投资总监

```python
# 全市场概览
from openbb import obb

sp500 = obb.equity.price.historical("SPY")
nasdaq = obb.equity.price.historical("QQQ")
btc = obb.crypto.price.historical("BTC")
rates = obb.economy.treasury_rates()
```

### 62-01 宏观研究员

```python
# 宏观仪表盘
gdp = obb.economy.gdp(provider="fred")
cpi = obb.economy.cpi(provider="fred")
unemployment = obb.economy.unemployment(provider="fred")
rates = obb.economy.treasury_rates()
calendar = obb.economy.calendar()
```

### 64-01 量化研究员

```python
# 回测数据获取
prices = obb.equity.price.historical(
    ["AAPL", "MSFT", "GOOGL"],
    start_date="2020-01-01",
    end_date="2024-01-01",
    provider="yfinance"
).to_df()

# 技术指标
ma = obb.technical.ma(symbol="AAPL", length=50)
rsi = obb.technical.rsi(symbol="AAPL", length=14)
```

## OBBject 统一返回

```python
# 所有 OpenBB 命令返回 OBBject
result = obb.equity.price.historical("AAPL")

# 转换格式
df = result.to_df()           # Pandas DataFrame
polars = result.to_polars()   # Polars DataFrame
dict_data = result.model_dump()  # 字典

# 访问元数据
print(result.provider)  # 数据提供者
print(result.warnings)  # 警告信息
```

## 常用命令速查

| 任务 | 命令 |
|------|------|
| 股票历史价格 | `obb.equity.price.historical(symbol)` |
| 实时报价 | `obb.equity.price.quote(symbol)` |
| 财务报表 | `obb.equity.fundamental.balance_sheet(symbol)` |
| 公司信息 | `obb.equity.info(symbol)` |
| 同行对比 | `obb.equity.peers(symbol)` |
| 分析师预测 | `obb.equity.estimates.consensus(symbol)` |
| 期权链 | `obb.derivatives.options.chains(symbol)` |
| GDP | `obb.economy.gdp()` |
| CPI | `obb.economy.cpi()` |
| 国债利率 | `obb.economy.treasury_rates()` |
| ETF持仓 | `obb.etf.holdings(symbol)` |
| 加密货币价格 | `obb.crypto.price.historical(symbol)` |

## 错误处理

```python
from openbb import obb
from openbb_core.provider import ProviderError

try:
    data = obb.equity.price.historical("INVALID_SYMBOL")
except ProviderError as e:
    print(f"Provider error: {e}")
except Exception as e:
    print(f"General error: {e}")
```

## 参考资料

- GitHub: https://github.com/OpenBB-finance/OpenBB
- 文档: https://docs.openbb.co
- API 参考: https://docs.openbb.co/platform/reference