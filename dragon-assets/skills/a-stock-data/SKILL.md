---
name: a-stock-data
description: A股全栈数据工具包 - 28个端点覆盖行情/研报/信号/资金面
trigger_keywords: - 估值查询
- 实时行情
- 研报
- 强势股
- 概念归因
- 北向资金
- 龙虎榜
- 大宗交易
- 融资融券
- 股票筛选
- A股分析
author: simonlin1212
stars: 420+
license: MIT
triggers: ["a stock data", "a-stock-data"]
---

# a-stock-data

## L0: 一句话描述 (≤15字)
A股全栈数据，零依赖免费

## L1: 使用场景 (50-100字)
A股投资研究时，需要获取实时行情、财务数据、研报摘要、资金流向、龙虎榜等关键数据。触发场景包括：股票估值分析、强势股筛选、概念板块轮动、北向资金追踪、龙虎榜异动等。

## L2: 详细文档

### 核心能力

| 层级 | 端点数 | 数据类型 | 代表API |
|------|--------|---------|---------|
| 行情层 | 8 | 实时/历史K线/分笔 | quote/ktype/history |
| 研报层 | 6 | 研报/公告/年报 | reports/notice/annual |
| 信号层 | 5 | 买卖信号/形态 | patterns/signals |
| 资金面 | 5 | 北向/融资/龙虎 | northmoney/margin/bath |
| 基础层 | 4 | 板块/指数/财务 | sector/index/financial |

### 7大特色

1. **零第三方封装** - 全部直连HTTP API，mootdx(TCP行情)+requests(HTTP)
2. **全免费数据源** - 13个公开源，除iwencai外全部免费
3. **中文友好** - pandas中文列名，requests响应中文直接处理
4. **批量操作** - 支持股票列表批量查询
5. **财务F10** - 上市公司财务报表、业绩预告
6. **研报摘要** - 最新研报、盈利预测、一致预期
7. **资金追踪** - 北向资金/融资融券/龙虎榜

### 快速使用

```python
from a_stock_data import Quote, Reports, Signals, MoneyFlow

# 实时行情
q = Quote()
data = q.quote("000001")  # 平安银行

# 批量查询
data = q.quotes(["000001","000002","600519"])

# 研报摘要
r = Reports()
reports = r.reports("600519", limit=10)

# 资金流向
m = MoneyFlow()
north = m.north_money()  # 北向资金

# 强势股筛选
s = Signals()
strong = s.strong_stocks(days=5, limit=20)
```

### 天龙引擎协同

| 天龙岗位 | 协同场景 |
|---------|---------|
| 60-01投资总监 | A股实时行情→估值分析→投资决策 |
| 62-03公司研究员 | 财务F10→研报→一致预期EPS |
| 64-01量化研究员 | 资金流信号→Alpha因子→量化策略 |
| 66-01风控经理 | 融资融券→杠杆风险→仓位管理 |

### 与现有Skill协同

```python
# 协同链路
a-stock-data(数据层) → AlphaGBM/stock-scorer(评分层) → ValueCell(决策层)
                         ↓
                  AlphaGBM/fear-score(恐慌指数)
                  AlphaGBM/greeks(期权Greeks)
```

### 安装

```bash
pip install a-stock-data
# 或从GitHub安装最新版
pip install git+https://github.com/simonlin1212/a-stock-data.git
```

### 数据源清单

| 数据源 | 类型 | 免费 | 用途 |
|--------|------|------|------|
| Sina | HTTP | ✅ | 实时行情 |
| 腾讯 | HTTP | ✅ | 实时行情 |
| 东方财富 | HTTP | ✅ | 研报/资金 |
| 同花顺 | HTTP | ✅ | 财务数据 |
| iwencai | HTTP | ⚠️ | 问财筛选 |
| 乌龟量化 | HTTP | ✅ | 历史数据 |
| 网易 | HTTP | ✅ | 资金流 |
| 新浪财经 | HTTP | ✅ | 公告 |
| 东方财富 | HTTP | ✅ | 研报 |

### 输出格式

```python
# pandas DataFrame 中文列名
df = q.quote("000001")
# columns: ['代码','名称','现价','涨跌幅','成交量','成交额',...]

# 字典格式
result = q.quote("000001", format="dict")
# {'代码': '000001', '名称': '平安银行', ...}
```

### 注意事项

1. **请求频率** - 实时行情请控制请求间隔≥0.5s
2. **数据缓存** - 建议本地缓存K线数据减少API调用
3. **API变更** - 数据源API可能变动，建议版本锁定
4. **创业板/科创板** - 完整支持，代码格式与主板一致

---

*本Skill填补天龙引擎A股数据空白，与AlphaGBM/skills、ValueCell形成三明治架构：数据层→分析层→决策层。*
