# Fincept Market Data

金融市场数据一站式连接器，支持30+数据源。

## 安装

```bash
pip install yfinance pandas sqlalchemy requests
```

## 快速开始

### Python API

```python
from fincept_market_data import MarketDataClient

client = MarketDataClient()

# 实时行情
quote = client.quote("AAPL")
print(f"AAPL: ${quote['price']}")

# 历史数据
daily = client.historical("AAPL", start="2024-01-01", end="2024-12-31")

# 加密货币
btc = client.crypto("BTC-USD")
print(f"BTC: ${btc['price']}")

# 批量数据
data = client.batch_historical(
    ["AAPL", "MSFT", "GOOGL"],
    start="2024-01-01",
    end="2024-12-31"
)
```

### CLI

```bash
# 实时行情
fincept-market quote AAPL
fincept-market quotes AAPL,MSFT,GOOGL

# 历史数据
fincept-market hist AAPL --start 2024-01-01 --end 2024-12-31 --interval 1d

# 加密货币
fincept-market crypto BTC-USD
fincept-market crypto-hist BTC-USD --interval 1h

# 财务报表
fincept-market financials AAPL

# 期权链
fincept-market options AAPL
fincept-market expirations AAPL

# 批量数据
fincept-market batch AAPL,MSFT --start 2024-01-01 --end 2024-12-31

# 搜索
fincept-market search "Apple"

# 缓存管理
fincept-market cache-stats
fincept-market cache-clear
```

## 数据源支持

| 数据源 | 股票 | 加密货币 | 期货 | 期权 |
|--------|------|---------|------|------|
| Yahoo Finance | ✅ | ✅ | ✅ | ✅ |
| Polygon.io | ✅ | ❌ | ✅ | ✅ |
| Kraken | ❌ | ✅ | ❌ | ❌ |
| Binance | ❌ | ✅ | ❌ | ❌ |
| Coinbase | ❌ | ✅ | ❌ | ❌ |

## 天龙引擎集成

```bash
# 投资研究员使用
[@62-02] 使用fincept-market获取苹果和微软的历史数据进行对比分析

# 量化研究员使用
[@64-01] 获取BTC历史数据，进行波动率分析

# 财务分析师使用
[@17-01] 获取AAPL最新财报数据
```

## 缓存

数据默认缓存到 `~/.fincept_cache`，TTL 300秒。

```python
# 禁用缓存
client = MarketDataClient(cache_enabled=False)

# 查看缓存统计
client.cache.stats()

# 清除缓存
client.cache.clear()
```

## API Keys

部分数据源需要API Key:

```python
client = MarketDataClient(
    api_keys={
        "polygon": "YOUR_POLYGON_API_KEY",
        "alpha_vantage": "YOUR_ALPHA_VANTAGE_API_KEY"
    }
)
```
