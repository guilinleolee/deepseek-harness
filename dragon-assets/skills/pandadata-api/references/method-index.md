# Pandadata API 方法索引

> 本文档是 pandadata-api 的快速查询索引

---

## A-Z 方法索引

### A

- `get_annual_report` - 年度报告详情

### B

- `get_balance_sheet` - 资产负债表

### C

- `get_cash_flow` - 现金流量表

### D

- `get_disclosure` - 披露公告

### F

- `get_fina_forecast` - 业绩预测
- `get_fina_indicator` - 财务指标 ⭐常用
- `get_fina_performance` - 业绩预告
- `get_fina_report` - 财务报表 ⭐常用
- `get_fina_reports` - 研报列表
- `get_float_shareholder` - 流通股东

### G

- `get_history_minutes` - 历史分钟线

### I

- `get_income_statement` - 利润表
- `get_institution_holder` - 机构持仓
- `get_institutional_trade` - 机构交易

### L

- `get_last_trade_date` - 最近交易日
- `get_lhb_detail` - 龙虎榜明细 ⭐常用
- `get_lhb_history` - 龙虎榜历史
- `get_lhb_list` - 龙虎榜列表
- `get_lhb_seats` - 龙虎榜席位
- `get_lhb_statistics` - 龙虎榜统计
- `get_lhb_summary` - 龙虎榜汇总
- `get_latest_notice` - 最新公告

### M

- `get_main_force` - 主力资金 ⭐常用
- `get_margin` - 融资融券 ⭐常用
- `get_margin_detail` - 融资融券明细
- `get_margin_history` - 融资融券历史
- `get_margin_rank` - 融资融券排行
- `get_minute_data` - 分钟线数据

### N

- `get_new_pledge` - 新增质押
- `get_notice` - 重要公告 ⭐常用
- `get_notice_content` - 公告内容

### O

- `get_order_book` - 订单簿

### P

- `get_performance_express` - 业绩快报
- `get_performance_preview` - 业绩预告
- `get_pledge_detail` - 质押明细
- `get_profit_predict` - 盈利预测 ⭐常用
- `get_promise_not_unlocked` - 限售股解禁

### Q

- `get_quarter_report` - 季度报告

### R

- `get_realtime_quotes` - 实时报价
- `get_research_report` - 研报汇总 ⭐常用

### S

- `get_share_bonus` - 分红送转
- `get_shareholder_change` - 股东变化
- `get_shareholder_count` - 股东户数 ⭐常用
- `get_short_balance` - 融券余额
- `get_short_volume` - 融券余量
- `get_stock_daily` - 个股日线 ⭐常用
- `get_stock_detail` - 股票详情 ⭐常用
- `get_stock_list` - 股票列表
- `get_stock_pledge_ratio` - 质押比例
- `get_stock_rt_daily` - 实时日线 ⭐常用
- `get_stock_status_change` - 股票状态变更

### T

- `get_target_price` - 目标价
- `get_tick_data` - 分笔数据
- `get_top_shareholder` - 前十大股东
- `get_trade_cal` - 交易日历
- `get_trade_list` - 交易列表

### I

- `get_index_daily` - 指数日线 ⭐常用
- `get_index_indicator` - 指数指标 ⭐常用

---

## 常用方法组合

### 65-02 个股档案（必需）

```python
# 基础组合
get_stock_detail      # 股票基本信息
get_stock_daily       # 今日行情
get_money_flow        # 资金流向
get_fina_indicator    # 估值指标
get_fina_report       # 财务数据

# 扩展组合
get_research_report   # 研报汇总
get_margin            # 融资融券
get_shareholder_count # 股东户数
get_lhb_detail        # 龙虎榜
get_notice           # 重要公告
```

### 65-01 市场复盘（必需）

```python
get_last_trade_date   # 最近交易日
get_trade_cal        # 交易日历
get_index_daily      # 指数行情
get_index_indicator  # 指数估值
get_stock_status_change  # 涨跌停
get_industry_constituents  # 行业成分
get_concept_list     # 概念列表
get_lhb_list         # 龙虎榜
get_block_trade      # 大宗交易
get_margin           # 两融
get_hsgt_hold       # 北向持股
```

---

## 方法别名

某些方法有别名或等价写法：

| 别名 | 原方法 |
|------|-------|
| `get_quote` | `get_stock_daily` |
| `get_valuation` | `get_fina_indicator` |
| `get_financial` | `get_fina_report` |
| `get_main_flow` | `get_main_force` |
| `get_mf` | `get_money_flow` |
