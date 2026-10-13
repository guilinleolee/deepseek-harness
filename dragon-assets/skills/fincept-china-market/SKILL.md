---
license: UNKNOWN
triggers: ["fincept china market", "Fincept China Market - 中国市场数据能力"]
---
# Fincept China Market - 中国市场数据能力

## 版本
V1.0.0 - 2026-04-27

## 概述

Fincept China Market 是天龙引擎独家封装 AkShare 的中国市场数据 Skill，覆盖 A 股、期货、基金、宏观、加密货币等 20+ 数据类别。**这是天龙引擎独家能力**，填补国内其他 Agent 在中国市场数据领域的空白。

## 核心价值

| 指标 | 值 |
|------|-----|
| **数据类别** | 20+ |
| **A股覆盖** | 全市场 5000+ 股票 |
| **更新频率** | 实时/日频/季频 |
| **数据源** | AkShare (东方财富、同花顺等) |

## 数据覆盖

### 股票市场
- 实时行情 (stock_zh_a_spot_em)
- 历史 K 线 (日/周/月)
- 财务报表 (利润表、资产负债表、现金流量表)
- 财务指标 (ROE、PE、PB 等)
- 股东信息
- 分红配股

### 期货市场
- 商品期货实时行情
- 金融期货 (IF/IC/IH/IM)
- 持仓排名分析
- 仓单数据

### 期权市场
- 50ETF 期权
- 沪深 300 期权
- 波动率数据

### 债券市场
- 国债实时行情
- 企业债数据
- 可转债数据

### 基金市场
- 公募基金列表
- ETF 实时/历史数据
- LOF 基金数据
- 基金净值 (NAV)

### 宏观数据
- GDP 季度/年度
- CPI 月度
- PPI 月度
- 货币供应量 (M0/M1/M2)
- 社会融资规模

### 加密货币
- BTC/CNH 实时行情
- ETH/CNH 实时行情
- USDT/CNY 汇率

## 安装

```bash
# 安装依赖
pip install akshare>=1.14.0 pandas

# 或使用 requirements.txt
pip install -r ~/.claude/skills/fincept-china-market/requirements.txt
```

## 快速开始

### Python API

```python
from fincept_china_market import ChinaMarketClient

client = ChinaMarketClient()

# === A股市场 ===
# 实时行情
client.realtime("000001")              # 平安银行
client.realtime(["000001", "600000"])  # 批量查询

# 历史K线
client.kline("000001", start="20240101", end="20241231")
client.kline("000001", period="1d")   # 日线
client.kline("000001", period="1w")   # 周线

# 财务数据
client.financial("000001")             # 财务报表
client.indicator("000001")             # 财务指标
client.balance("000001")               # 资产负债表
client.cashflow("000001")             # 现金流量表

# === 期货市场 ===
client.futures("IF")                  # IF当月连续
client.futures_spot()                 # 商品期货实时
client.futures_positions("IF")        # 持仓排名

# === 期权市场 ===
client.options_50etf()                # 50ETF期权
client.options_300()                  # 沪深300期权

# === 债券市场 ===
client.bond()                          # 国债
client.corporate_bond()               # 企业债

# === 基金 ===
client.fund("510300")                 # 华泰柏瑞沪深300ETF
client.fund_nav("510300")             # 净值数据
client.fund_list()                    # 基金列表

# === 宏观数据 ===
client.macro_cpi()                    # CPI月度
client.macro_gdp()                    # GDP季度
client.macro_ppi()                    # PPI月度
client.money_supply()                 # 货币供应量M2

# === 加密货币 ===
client.crypto_cn("BTC")               # BTC实时(CNY)
client.crypto_cn("ETH")              # ETH实时(CNY)
```

### CLI 使用

```bash
# 实时行情
fincept-china realtime 000001
fincept-china realtime 000001 600000

# 历史K线
fincept-china kline 000001 --start 20240101 --end 20241231
fincept-china kline 000001 --period 1d

# 财务数据
fincept-china financial 000001
fincept-china indicator 000001

# 期货
fincept-china futures IF
fincept-china futures-spot

# 基金
fincept-china fund 510300
fincept-china fund-nav 510300

# 宏观
fincept-china macro-cpi
fincept-china macro-gdp

# 加密
fincept-china crypto BTC
fincept-china crypto ETH
```

## AkShare 覆盖映射

| 类别 | AkShare 函数 | 说明 |
|------|-------------|------|
| **股票-行情** | ak.stock_zh_a_spot_em() | 全 A 股实时行情 |
| **股票-历史** | ak.stock_zh_a_hist() | 日 K 线数据 |
| **股票-财务** | ak.stock_financial_analysis_indicator() | 财务指标 |
| **股票-分析** | ak.stock_profit_sheet_by_report_em() | 利润表 |
| **期货** | ak.futures_zh_spot() | 商品期货实时 |
| **期货** | ak.futures_zh_daily_sina() | 期货日线 |
| **期权** | ak.option_50etf_spot() | 50ETF 期权 |
| **基金** | ak.fund_etf_hist_sina() | ETF 历史净值 |
| **基金** | ak.fund_open_fund_info() | 公募基金信息 |
| **债券** | ak.bond_zh_cibm_spot() | 国债+企业债 |
| **宏观** | ak.macro_china_gdp() | 中国 GDP |
| **宏观** | ak.macro_china_cpi() | 中国 CPI |
| **宏观** | ak.macro_china_money_supply() | 货币供应量 |
| **加密** | ak.crypto_js_spot() | 加密货币实时 |

## 天龙岗位应用

| 岗位 | 应用场景 |
|------|---------|
| **64-01 量化研究员** | 策略回测数据、因子计算 |
| **60-01 投资总监** | 市场数据监控、趋势分析 |
| **00 分析师** | 宏观经济分析、CPI/GDP 关联 |
| **62-02 行业研究员** | 行业板块数据、资金流向 |
| **19-01 数据工程师** | 数据管道构建、ETL |

## 命令速查

```bash
# 安装
pip install akshare>=1.14.0

# 验证安装
python -c "import akshare; print(akshare.__version__)"

# 常用命令
fincept-china realtime [代码]     # 实时行情
fincept-china kline [代码]        # 历史K线
fincept-china financial [代码]    # 财务数据
fincept-china indicator [代码]   # 财务指标
fincept-china futures [品种]      # 期货行情
fincept-china fund [代码]        # 基金数据
fincept-china macro-cpi          # CPI数据
fincept-china macro-gdp          # GDP数据
fincept-china crypto [币种]      # 加密货币
```

## 数据缓存

```python
client = ChinaMarketClient(cache=True, cache_dir="/tmp/fincept_cache")

# 缓存会在首次请求时自动创建
# 相同请求会从缓存读取
```

## 错误处理

```python
from fincept_china_market import ChinaMarketClient, FinceptError

client = ChinaMarketClient()

try:
    data = client.realtime("000001")
except FinceptError as e:
    print(f"数据获取失败: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 注意事项

1. **网络要求**: 需要能访问国内数据源 (东方财富、同花顺等)
2. **数据版权**: AkShare 数据来自公开网络，仅供学习研究使用
3. **更新频率**: 实时数据有 15-60 秒延迟
4. **请求限制**: 建议添加延迟避免高频请求被封禁

## 文件结构

```
fincept-china-market/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── __init__.py
│   ├── client.py               # 主客户端
│   ├── providers/
│   │   ├── stock_provider.py  # 股票数据
│   │   ├── futures_provider.py # 期货数据
│   │   ├── fund_provider.py   # 基金数据
│   │   └── macro_provider.py   # 宏观数据
│   └── cli.py                  # CLI入口
├── requirements.txt
└── README.md
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0.0 | 2026-04-27 | 初始版本，20+数据类别覆盖 |

---

**天龙引擎独家能力** - 国内其他 Agent 都没有完整的中国 A 股/期货/基金/宏观数据覆盖
