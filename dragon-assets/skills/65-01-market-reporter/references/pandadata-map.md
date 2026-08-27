# Pandadata Map

使用此映射表规划每日复盘。在调用任何方法之前，始终使用 `pandadata-api` 确认确切的签名和字段。

## 核心日期和范围

| 需求 | 首选方法 | 说明 |
| --- | --- | --- |
| 最近交易日 | `get_last_trade_date` | 当用户说"今日复盘"或未指定日期时使用 |
| 交易日历 | `get_trade_cal` | 确认目标日期是否开放 |
| 可交易 A 股范围 | `get_trade_list` | 用作宽度和批量行情查询的股票列表 |

## 市场章节

| 报告章节 | 首选方法 | 衍生指标 |
| --- | --- | --- |
| 指数概览与估值 | `get_index_daily`, `get_index_indicator` | 指数收益、成交额、PE/PB、估值分位 |
| 市场宽度与情绪 | `get_stock_daily` 或 `get_stock_rt_daily`, `get_stock_status_change` | 上涨/下跌家数、涨停/跌停家数、成交额龙头、ST/状态变更 |
| 行业与概念热点 | `get_industry_constituents`, `get_concept_list`, `get_concept_constituents` | 按成分股聚合的行业/概念收益率、代表性领涨股 |
| 龙虎榜与大宗 | `get_lhb_list`, `get_lhb_detail`, `get_block_trade` | 上榜原因、席位买卖金额、净买卖、大宗交易折溢价 |
| 两融与北向 | `get_margin`, `get_hsgt_hold` | 融资余额及变化、北向持股增减排名 |

## 降级策略

如果全市场或概念聚合调用太慢或不可用：

1. 保留交易日、指数和估值章节
2. 如果可用，保留龙虎榜和大宗章节
3. 用清晰的不可用说明替换市场宽度，**不要估算**
4. 在 `数据说明` 下添加跳过的接口名称和原因

## 接口详细说明

### get_index_daily

获取指数日线行情数据。

**参数**：
- `date`: str - 目标日期 (YYYY-MM-DD)

**返回字段**：
- `name`: str - 指数名称
- `close`: float - 收盘点位
- `pct_chg`: float - 涨跌幅 (%)
- `amount`: float - 成交额

**示例**：
```python
data = await connector.get_index_daily("2026-08-18")
# [{'name': '上证指数', 'close': 3250.0, 'pct_chg': 0.5, 'amount': 350000000000}]
```

### get_index_indicator

获取指数估值指标。

**参数**：
- `date`: str - 目标日期 (YYYY-MM-DD)

**返回字段**：
- `name`: str - 指数名称
- `pe`: float - 市盈率
- `pb`: float - 市净率
- `valuation_pctile`: float - 估值分位 (%)

**示例**：
```python
data = await connector.get_index_indicator("2026-08-18")
# [{'name': '上证指数', 'pe': 12.5, 'pb': 1.3, 'valuation_pctile': 30}]
```

### get_stock_daily

获取个股日线行情（全市场）。

**参数**：
- `date`: str - 目标日期 (YYYY-MM-DD)
- `market`: str - 市场代码 (SSE/SZSE)

**返回字段**：
- `code`: str - 股票代码
- `name`: str - 股票名称
- `close`: float - 收盘价
- `pct_chg`: float - 涨跌幅
- `amount`: float - 成交额
- `volume`: float - 成交量

**示例**：
```python
data = await connector.get_stock_daily("2026-08-18", market="SSE")
```

### get_stock_status_change

获取个股状态变更（ST、停复牌等）。

**参数**：
- `date`: str - 目标日期 (YYYY-MM-DD)

**返回字段**：
- `new_st`: List[str] - 新增 ST
- `removed_st`: List[str] - 摘帽
- `suspended`: List[str] - 停牌

### get_industry_constituents

获取行业成分及涨跌幅。

**参数**：无

**返回字段**：
- `industry`: str - 行业名称
- `pct_chg`: float - 涨跌幅

**示例**：
```python
data = await connector.get_industry_constituents()
# [{'industry': '半导体', 'pct_chg': 3.5}]
```

### get_concept_list

获取概念列表及涨跌幅。

**参数**：无

**返回字段**：
- `concept`: str - 概念名称
- `pct_chg`: float - 涨跌幅

### get_concept_constituents

获取概念成分股。

**参数**：
- `concept`: str - 概念名称

**返回字段**：
- `code`: str - 股票代码
- `name`: str - 股票名称
- `pct_chg`: float - 涨跌幅

### get_lhb_list

获取龙虎榜列表。

**参数**：
- `date`: str - 目标日期 (YYYY-MM-DD)

**返回字段**：
- `stock`: str - 股票名称
- `reason`: str - 上榜原因
- `buy_amount`: float - 买入金额
- `sell_amount`: float - 卖出金额
- `net_amount`: float - 净买入额

### get_lhb_detail

获取龙虎榜详细席位信息。

**参数**：
- `date`: str - 目标日期
- `stock`: str - 股票名称

**返回字段**：
- `seat`: str - 席位名称
- `buy_amount`: float - 买入金额
- `sell_amount`: float - 卖出金额

### get_block_trade

获取大宗交易数据。

**参数**：
- `date`: str - 目标日期 (YYYY-MM-DD)

**返回字段**：
- `stock`: str - 股票名称
- `block_amount`: float - 成交额
- `premium_discount`: float - 折溢价率 (%)
- `buyer`: str - 买方席位
- `seller`: str - 卖方席位

### get_margin

获取融资融券数据。

**参数**：
- `date`: str - 目标日期 (YYYY-MM-DD)，注意 T+1

**返回字段**：
- `margin_balance`: float - 融资余额
- `margin_change`: float - 融资余额变化
- `short_balance`: float - 融券余额
- `short_change`: float - 融券余额变化

### get_hsgt_hold

获取北向持股数据。

**参数**：
- `date`: str - 目标日期 (YYYY-MM-DD)，注意 T+2

**返回字段**：
- `increase`: List[Dict] - 加仓股票列表
- `decrease`: List[Dict] - 减仓股票列表

每个元素包含：
- `code`: str - 股票代码
- `name`: str - 股票名称
- `change`: float - 持股变化数量
