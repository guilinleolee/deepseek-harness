# Pandadata DeepView 接口契约速查表

> 本文件是 Pandadata DeepView 38个期货接口的快速参考。详细参数和返回字段请查阅 `pandadata-api` SKILL。

---

## 📈 L1: 基础行情与合约

| 方法 | 用途 | 关键参数 | 返回字段 |
|------|------|---------|---------|
| `get_future_daily` | 日线行情 | symbol, start_date, end_date | date, open, high, low, close, volume, amount |
| `get_future_daily_post` | 日线行情（盘后） | symbol, start_date, end_date | 同上，含持仓量 |
| `get_future_min` | 分钟行情 | symbol, start_time, end_time, period | datetime, open, high, low, close, volume |
| `get_future_detail` | 合约详情 | symbol | name, exchange, list_date, delist_date, multiplier |
| `get_future_dominant` | 主力合约 | variety, date | symbol, variety, date |

---

## 🪑 L2: 席位持仓与建仓

| 方法 | 用途 | 关键参数 | 返回字段 |
|------|------|---------|---------|
| `get_broker_netmarg` | 席位净保证金 | trade_date, symbol/variety | broker, net_long, net_short, net |
| `get_broker_netmarg_change` | 净保证金变化 | trade_date, symbol | broker, change, change_pct |
| `get_broker_totlmarg` | 席位总保证金 | trade_date, symbol/variety | broker, long_marg, short_marg, total |
| `get_broker_grade` | 席位评级 | trade_date, symbol | broker, grade, score |
| `get_broker_oi_value` | 席位持仓市值 | trade_date, symbol | broker, oi_value |
| `get_broker_build_process` | 建仓过程 | trade_date, symbol, broker | date, action, volume, price |
| `get_future_nonbroker_net` | 非席位净持仓 | trade_date, symbol | date, net_position |
| `get_future_netposi_rank` | 净持仓排行 | trade_date, symbol | broker, net_posi, rank |
| `get_future_netcap_change` | 净持仓变化 | trade_date, symbol | broker, netcap, change |

---

## 💰 L3: 席位盈亏与资金流

| 方法 | 用途 | 关键参数 | 返回字段 |
|------|------|---------|---------|
| `get_broker_profit` | 席位盈亏 | trade_date, symbol/variety | broker, profit, profit_pct |
| `get_broker_variety_profit` | 品种盈亏 | trade_date, variety | variety, profit |
| `get_broker_profit_rank` | 盈亏排行 | trade_date, symbol | broker, profit, rank |
| `get_broker_loss_rank` | 亏损排行 | trade_date, symbol | broker, loss, rank |
| `get_broker_flow_daily` | 日资金流 | trade_date, symbol | broker, inflow, outflow, net_flow |

---

## ⚖️ L4: 多空情绪与合约排行

| 方法 | 用途 | 关键参数 | 返回字段 |
|------|------|---------|---------|
| `get_future_ls_ratio` | 多空比 | trade_date, symbol | date, long_ratio, short_ratio, net_ratio |
| `get_broker_ls_ratio` | 席位多空比 | trade_date, symbol | broker, ls_ratio |
| `get_future_contract_indicators` | 合约指标 | symbol | volume, oi, basis, basis_rate |
| `get_future_contract_rank` | 合约排行 | trade_date | symbol, rank, volume, change |
| `get_future_contract_pool` | 合约池 | date | symbols, count, dominant |
| `get_future_net_flow` | 净流向 | trade_date, symbol | date, inflow, outflow, net |

---

## 📐 L5: 基差与期限结构

| 方法 | 用途 | 关键参数 | 返回字段 |
|------|------|---------|---------|
| `get_future_basis` | 基差 | trade_date, symbol, spot_price | date, basis, basis_rate, spot |
| `get_future_term_structure` | 期限结构 | trade_date, variety | contract, price, distance, shape |
| `get_future_dominant_corr` | 主力相关性 | trade_date, variety | correlation, strength |

---

## 📦 L6: 仓单、库存与现货

| 方法 | 用途 | 关键参数 | 返回字段 |
|------|------|---------|---------|
| `get_future_warehouse_receipt` | 仓单 | trade_date, symbol | date, warehouse, receipt, change |
| `get_future_inventory` | 库存 | trade_date, variety | date, inventory, change, yoy |
| `get_future_virtual_ratio` | 虚实盘比 | trade_date, symbol | date, virtual_ratio, physical_ratio |
| `get_future_trader_quote` | 贸易商报价 | trade_date, variety | trader, quote, premium |
| `get_future_spot_profit` | 现货利润 | trade_date, variety | date, spot_profit, margin |

---

## 🔁 L7: 跨期套利

| 方法 | 用途 | 关键参数 | 返回字段 |
|------|------|---------|---------|
| `get_future_calendar_arbitrage` | 日历套利 | trade_date, variety | front, back, spread, spread_rate |
| `get_future_free_spread` | 自由价差 | trade_date, symbol1, symbol2 | spread, spread_rate, signal |
| `get_future_free_ratio` | 自由价比 | trade_date, symbol1, symbol2 | ratio, ratio_rate, signal |

---

## 🏗️ L8: 持仓规模与市值

| 方法 | 用途 | 关键参数 | 返回字段 |
|------|------|---------|---------|
| `get_future_variety_posi` | 品种持仓 | trade_date, variety | date, open_interest, position |
| `get_future_symbol_posi` | 合约持仓 | trade_date, symbol | date, open_interest, volume |
| `get_future_variety_mcap` | 品种市值 | trade_date, variety | date, market_cap, turnover |

---

## 📋 常用品种代码对照

| 品种 | 代码 | 交易所 |
|------|------|--------|
| 螺纹钢 | RB | SHFE |
| 热轧卷板 | HC | SHFE |
| 铜 | CU | SHFE |
| 铝 | AL | SHFE |
| 锌 | ZN | SHFE |
| 镍 | NI | SHFE |
| 豆粕 | M | DCE |
| 豆油 | Y | DCE |
| 棕榈油 | P | DCE |
| 玉米 | C | DCE |
| 铁矿石 | I | DCE |
| 焦煤 | JM | DCE |
| 焦炭 | J | DCE |
| 原油 | SC | INE |
| 黄金 | AU | SHFE |
| 白银 | AG | SHFE |
| 橡胶 | RU | SHFE |
| 沥青 | BU | BU |
| 纸浆 | SP | SHFE |
| 棉花 | CF | CZCE |
| 白糖 | SR | CZCE |
| PTA | TA | CZCE |
| 甲醇 | MA | CZCE |
| 尿素 | UR | CZCE |
| 玻璃 | FG | CZCE |
| 纯碱 | SA | CZCE |
| 菜粕 | RM | CZCE |
| 菜油 | OI | CZCE |
| 粳米 | RR | CZCE |
| 苯乙烯 | EB | CZCE |

---

## 🔗 接口依赖关系

```
get_future_dominant (获取主力合约)
    ↓
get_future_detail (确认合约信息)
    ↓
席位分析 → get_broker_netmarg / get_broker_build_process
    ↓
盈亏分析 → get_broker_profit / get_broker_flow_daily
    ↓
结构分析 → get_future_basis / get_future_term_structure
    ↓
库存分析 → get_future_warehouse_receipt / get_future_inventory
```

---

## ⚠️ 参数注意事项

1. **日期格式**：统一使用 `YYYY-MM-DD`
2. **品种 vs 合约**：
   - 品种（variety）：如 `RB`（螺纹钢）
   - 合约（symbol）：如 `RB2510`（2025年10月合约）
3. **交易日判断**：非交易日可能无数据，返回空数组
4. **披露限制**：席位数据仅披露前20名席位，不代表全市场

---

## 📚 相关文档

- 详细信号配方：[analysis-playbook.md](./analysis-playbook.md)
- Pandadata API 完整文档：[pandadata-api SKILL](../pandadata-api/)
