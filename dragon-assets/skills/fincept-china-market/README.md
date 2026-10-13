# Fincept China Market

> **天龙引擎独家 Skill** - 封装 AkShare 中国市场数据能力

## 特性

- **20+ 数据类别**: A股、期货、期权、债券、基金、宏观、加密货币
- **全市场覆盖**: 5000+ A股实时行情
- **简单 API**: Python + CLI 双接口
- **数据缓存**: 自动缓存避免重复请求

## 安装

```bash
pip install -r ~/.claude/skills/fincept-china-market/requirements.txt
```

## 快速开始

### Python API

```python
from fincept_china_market import ChinaMarketClient

client = ChinaMarketClient()

# 实时行情
client.realtime("000001")

# 历史K线
client.kline("000001", start="20240101", end="20241231")

# 财务数据
client.financial("000001")
client.indicator("000001")

# 期货
client.futures_spot()
client.futures("IF")

# 基金
client.fund("510300")
client.fund_nav("510300")

# 宏观
client.macro_cpi()
client.macro_gdp()
client.money_supply()

# 加密货币
client.crypto_cn("BTC")
```

### CLI

```bash
# 实时行情
fincept-china realtime 000001
fincept-china realtime 000001,600000

# 历史K线
fincept-china kline 000001 --start 20240101 --end 20241231

# 财务数据
fincept-china financial 000001
fincept-china indicator 000001

# 期货
fincept-china futures IF --spot
fincept-china futures IF --positions

# 基金
fincept-china fund 510300
fincept-china fund 510300 --nav

# 宏观
fincept-china macro --cpi
fincept-china macro --gdp
fincept-china macro --money

# 加密货币
fincept-china crypto BTC
```

## 数据覆盖

| 类别 | 数据 | AkShare 函数 |
|------|------|-------------|
| A股-行情 | 全市场实时 | stock_zh_a_spot_em |
| A股-K线 | 日/周/月线 | stock_zh_a_hist |
| A股-财务 | 财务报表 | stock_profit_sheet_by_report_em |
| A股-指标 | PE/PB/ROE | stock_financial_analysis_indicator |
| 期货 | 实时/日线 | futures_zh_spot, futures_zh_daily_sina |
| 期权 | 50ETF/300 | option_50etf_spot |
| 基金 | ETF/公募 | fund_etf_hist_sina |
| 宏观 | CPI/GDP/M2 | macro_china_cpi, macro_china_gdp |
| 加密 | BTC/ETH | crypto_js_spot |

## 注意事项

1. 需要网络连接国内数据源
2. 实时数据有 15-60 秒延迟
3. 建议添加请求延迟避免被封禁

## License

MIT License - 天龙引擎
