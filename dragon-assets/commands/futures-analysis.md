---
name: futures-analysis
description: 期货深度分析命令 - 席位博弈+期限结构+仓单库存+跨期套利
version: 1.0
category: finance
triggers:
  - "futures-analysis"
  - "[@期货分析]"
  - "期货深度分析"
examples:
  - "futures-analysis RB 席位博弈"
  - "[@期货分析] 分析螺纹钢的席位博弈"
  - "futures-analysis M 结构研判"
  - "[@期货分析] 看看豆粕的期限结构"
requires:
  - skills/pandadata-deepview
  - agents/66-03-futures-analyst
---

# futures-analysis 命令

## 功能说明

期货深度分析命令，调用 `pandadata-deepview` SKILL 和 `66-03 期货深度分析师` Agent，对期货品种进行席位博弈、期限结构、仓单库存、跨期套利等综合研判。

## 使用方式

```bash
# 基本用法
futures-analysis <品种代码> <分析模式>

# 示例
futures-analysis RB 席位博弈
futures-analysis M 结构研判
futures-analysis CU 库存现货
futures-analysis SC 全品种扫描

# 或使用触发词
[@期货分析] 分析螺纹钢的席位博弈
[@期货分析] 看看豆粕的期限结构和仓单情况
```

## 分析模式

| 模式 | 命令 | 典型问法 |
|------|------|---------|
| 🪑 席位博弈 | `席位博弈` | "主力是否看多螺纹钢？" |
| 📐 结构研判 | `结构研判` | "豆粕现在 contango 还是 back？" |
| 📦 库存现货 | `库存现货` | "仓单压力大不大？" |
| 🔍 全品种扫描 | `全品种扫描` | "哪些品种有跨期套利机会？" |

## 常用品种代码

| 品种 | 代码 | 品种 | 代码 |
|------|------|------|------|
| 螺纹钢 | RB | 豆粕 | M |
| 热轧卷板 | HC | 豆油 | Y |
| 铜 | CU | 棕榈油 | P |
| 铝 | AL | 玉米 | C |
| 锌 | ZN | 铁矿石 | I |
| 镍 | NI | 焦煤 | JM |
| 原油 | SC | 焦炭 | J |
| 黄金 | AU | 橡胶 | RU |
| 白银 | AG | 白糖 | SR |
| PTA | TA | 甲醇 | MA |

## 报告输出

- **完整报告**：9段标准结构（摘要→数据范围→行情背景→席位博弈→期限结构→仓单库存→交叉验证→风险限制→附录）
- **快速问答**：4段压缩（结论/关键证据/矛盾点/数据来源）

## 注意事项

1. 首次调用会加载 `pandadata-deepview` SKILL 的分析手册和接口契约
2. 默认回看窗口：近端分析 20 个交易日，分位分析 120 个交易日
3. 报告自动标注数据来源和 trade_date
4. 严格区分事实描述和推断结论

## 相关命令

- `[@市场复盘]` - A股每日复盘（65-01）
- `[@财经底座]` - 财经数据底座（28-10）
