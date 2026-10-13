---
name: trading-agents-astock-wrapper
description: A股多Agent投研辩论框架 — simonlin1212/TradingAgents-astock (Apache-2.0) 7 分析师角色 + bull/bear 辩论 + 风险评估 + 投资决策
version: 1.0
base_version: 0.0
category: research-center
department: 研究中心-多Agent投研部
license: Apache-2.0
upstream:
  name: simonlin1212/TradingAgents-astock
  version: V1.x
  url: https://github.com/simonlin1212/TradingAgents-astock
  license: Apache-2.0
  stars: 2530
  architecture: 7-analyst multi-agent debate
  framework: 基于 TradingAgents 深度改造，适配大A
modified: 2026-07-30
modified_by: 天龙引擎 dragon-engine
triggers:
  - "[@多Agent辩论]"
  - "[@辩论框架]"
  - "multi-agent debate"
  - "bull bear debate"
  - "7 分析师"
  - "投资决策"
  - "风险评估"
  - "TradingAgents"
  - "trading-agents-astock"
  - "辩论剧本"
  - "decision framework"
  - "research debate"
  - "风险经理"
  - "多头观点"
  - "空头观点"
  - "基本面分析"
  - "技术面分析"
  - "情绪面分析"
  - "估值分析"
  - "宏观分析"
  - "辩论决策"
---

# trading-agents-astock-wrapper · A股多Agent投研辩论框架 V1.0

> **TL;DR**：基于 [simonlin1212/TradingAgents-astock](https://github.com/simonlin1212/TradingAgents-astock)（Apache-2.0 ✅ · 2,530⭐ · Python · 7 分析师多 Agent 辩论框架）二次开发。提供 **7 位分析师角色** + **bull/bear 辩论** + **风险评估** + **最终投资决策** 的 4 阶段工作流，输入 28-10 财经数据底稿 + 28-04 行业数据，输出结构化投资决策剧本（含 5 必检 + 3 推荐质检）。

## L0: 一句话描述（≤15 字）

**7 分析师辩论 + bull/bear + 风险评估 → 投资决策**

## L1: 使用场景

用户做**系统性 A 股个股 / 中概股美港股投研**时使用：

1. **7 分析师角色** 并行辩论（fundamental/technical/sentiment/valuation/risk/macro/regulatory）
2. **bull/bear debate** —— 多头 vs 空头基于数据展开辩论
3. **risk assessment** —— 风险经理综合评估
4. **最终投资决策** —— 决策经理综合 7 分析师 + 辩论 + 风险给出 buy/hold/sell
5. **决策剧本导出** —— Markdown + JSON 双产物，含 5 必检 + 3 推荐质检

## L2: 详细文档

### 7 分析师角色

| # | 分析师 | 角色定位 | 输入 | 产出 |
|---|--------|---------|------|------|
| 1 | **fundamental_analyst** 基本面分析师 | 财报三表 + 季报 37 字段 + 分红送 | financial_3statements + quarterly_37fields | 财务健康评分 + ROE/毛利率趋势 |
| 2 | **technical_analyst** 技术面分析师 | K 线 + 成交量 + 5 指标 | historical_ohlcv + ma/macd/rsi/kdj/bollinger | 技术面评分 + 关键位 |
| 3 | **sentiment_analyst** 情绪面分析师 | 雪球 + 同花顺问财 + 互动易 | xueqiu_hot_rank + iwencai_qa + interactive_qa | 市场情绪评分 + 情绪转折点 |
| 4 | **valuation_analyst** 估值分析师 | PE/PB/PS + 历史百分位 + 同业 | pe_pb_market_cap + valuation_full + peer_compare | 估值评分 + 合理价区间 |
| 5 | **risk_analyst** 风险评估师 | 波动率 + Beta + 解禁 + 大宗 | block_trade + restricted_unlock + valuation_ratios | 风险等级 + 风险评分 |
| 6 | **macro_analyst** 宏观分析师 | 利率 + CPI + PMI + 行业政策 | 全球新闻 + 行业研报 | 宏观评分 + 行业影响 |
| 7 | **regulatory_analyst** 合规分析师 | 公告 + 监管事件 + 互动易问答 | cninfo_announcement + interactive_qa | 合规评分 + 风险事件识别 |

### 4 阶段工作流

```
输入：股票代码 + 28-10 财经底稿
   │
   ▼
Stage 1：7 分析师并行辩论（3-5 轮 round）
   ├── Round 1: 各分析师独立给出初评
   ├── Round 2-3: 互相质疑与数据补充
   ├── Round 4: 综合评分（1-10）
   └── Round 5: 各自结论（buy/hold/sell）
   │
   ▼
Stage 2：bull/bear debate（多头 vs 空头）
   ├── bull: 找 3-5 个最强多头论据
   ├── bear: 找 3-5 个最强空头论据
   ├── 互相答辩
   └── 综合得分
   │
   ▼
Stage 3：risk assessment（风险评估）
   ├── 5 类风险（市场/政策/流动性/合规/经营）
   ├── 综合风险评分（1-10）
   └── 风险事件标记
   │
   ▼
Stage 4：final decision（决策经理综合）
   ├── 7 分析师评分加权
   ├── bull/bear debate 加权
   ├── risk 评分反向加权
   └── 最终决策：buy / hold / sell + 仓位 + 持有期
   │
   ▼
输出：决策剧本（Markdown + JSON）
   ├── 5 必检：分析师全到位 / 评分有依据 / 辩论完整 / 风险识别 / Apache 归属
   └── 3 推荐：数据溯源 / 跨评分一致性 / 决策可追溯
```

### bull/bear debate 模板

| 维度 | 多头(bull) | 空头(bear) |
|------|-----------|------------|
| **基本面目击** | 营收增长 / 毛利率提升 | 营收减速 / 毛利率承压 |
| **技术面目击** | 站上 MA60 / MACD 金叉 | RSI 超买 / 跌破 MA20 |
| **情绪面** | 雪球讨论量暴增 / 机构持仓 | 散户跟风 / 北向流出 |
| **估值面** | PE 历史百分位 20% / 安全边际 | PE 历史百分位 80% / 估值泡沫 |
| **风险面** | 解禁已过 / 大宗折价收窄 | 大解禁期 / 商誉减值 |

### 5 必检（em_debate_check.py）

| 编号 | 名称 | 检查内容 |
|------|------|----------|
| **W1** | 7 分析师全到位 | 7 个分析师角色段落完整 |
| **W2** | 评分有依据 | 每个分析师有数据引用 + 评分理由 |
| **W3** | 辩论完整 | bull/bear 双边论据 ≥ 3 条/方 |
| **W4** | 风险识别 | 5 类风险（市场/政策/流动性/合规/经营）全标记 |
| **W5** | Apache 归属 | 含 simonlin1212/TradingAgents-astock + Apache-2.0 + Modified 段 |

### 3 推荐

| 编号 | 名称 | 检查内容 |
|------|------|----------|
| **R1** | 数据溯源 | 每个评分引用 ≥ 1 个数据端点 |
| **R2** | 决策可追溯 | buy/hold/sell + 仓位 + 持有期 3 字段全 |
| **R3** | 跨评分一致性 | 7 评分加权平均与最终决策方向一致 |

### 退出码契约

| 退出码 | 含义 |
|--------|------|
| 0 | [PASS] 5 必检全过 |
| 1 | [FAIL] 至少 1 项必检未过 |
| 2 | [WARN] 仅推荐未过 |
| 3 | [ERROR] 调用方式错误 |

### 与 28-10 / 35-07 关系

```
28-10 财经数据底座 (V1.1 双赛道)
   │
   ├─► trading-agents-astock-wrapper (本 skill)
   │      │
   │      ├── 输入 7 类数据（来自 28-10 各端点）
   │      └── 输出 4 阶段辩论剧本
   │
   └─► 35-07 横纵研究员 V1.1 (V1.0 5 步工作流 + V1.1 多 Agent 辩论为可选增强)

协同关系：
- 35-07 V1.0 5 步工作流 = 横向主路径（产品/公司/概念/人物）
- 35-07 V1.1 多 Agent 辩论 = 个股投研专门增强
- 用户输入"研究 XX 公司"→ 默认走 35-07 V1.0
- 用户输入"辩论 XX 个股"/"XX 决策"→ 走 35-07 V1.1 + trading-agents-astock
```

## 使用示例

```bash
# 1. 单股辩论剧本（A 股 平安 601318.SH）
python trading_agents.py --symbol "601318.SH" \
  --data-source 28-10 \
  --output-md pingan_debate.md

# 2. 中概股美港股（AAPL）
python trading_agents.py --symbol "AAPL" \
  --data-source 28-10-V1.1-global \
  --output-md aapl_debate.md

# 3. 港股（0700.HK）
python trading_agents.py --symbol "0700.HK" \
  --data-source 28-10-V1.1-global \
  --output-md tencent_debate.md

# 4. 限定辩论回合数（默认 5 轮）
python trading_agents.py --symbol "601318.SH" \
  --rounds 3 \
  --output-md pingan_quick_debate.md

# 5. 5 必检 + 3 推荐 质检
python em_debate_check.py pingan_debate.md

# 6. 强制模拟某一分析师不参与（测试 6 vs 7 路径）
python trading_agents.py --symbol "AAPL" \
  --skip-analyst regulatory_analyst \
  --dry-run
```

## 合规边界

> 本 skill 集成自上游 Apache-2.0 Python 仓库，调用 LLM API（默认 stub）执行 7 角色辩论。

| 数据源 | 协议状态 | 天龙对策 |
|--------|---------|----------|
| LLM API（OpenAI/Anthropic/开源）| 由用户配置 | ⚠️ 仅辩论剧本用，不外发原始 prompt |
| simonlin1212/TradingAgents-astock | Apache-2.0 | ✅ 已声明 NOTICE |
| simonlin1212/a-stock-data V3.4.0 | Apache-2.0 | ⚠️ 数据底稿合规边界继承 |
| simonlin1212/global-stock-data V1.0.1 | Apache-2.0 | ⚠️ 同上 |

## Attribution

本 skill 集成自上游 [simonlin1212/TradingAgents-astock](https://github.com/simonlin1212/TradingAgents-astock)（V1.x · Apache-2.0）。

**上游版权**：simonlin1212, 2026
**上游 LICENSE**：Apache License 2.0 — 详见 [`./LICENSE`](./LICENSE) 或 https://www.apache.org/licenses/LICENSE-2.0
**上游 NOTICE**：[`./NOTICE`](./NOTICE)

**本 skill 修改**（按 Apache-2.0 §4(d)）：
1. 包装上游 Python 多 Agent 框架为天龙 SKILL.md 形式
2. 显式定义 7 分析师角色 + bull/bear debate + risk + decision 4 阶段工作流
3. 与 28-10 财经数据底座师 V1.1 联动（数据驱动辩论）
4. 与 35-07 横纵研究员 V1.0/V1.1 协同
5. 新增 `em_debate_check.py` 5 必检 + 3 推荐质检
6. 新增 Markdown + JSON 双产物 + Apache-2.0 NOTICE 三件套

按 Apache-2.0 §4(d)，本 skill 的 NOTICE 文件已保留上游 simonlin1212 的归属声明，并标注 "Modified by 天龙引擎 dragon-engine, 2026-07-30"。

---

## 版本信息

- **Version**: 1.0
- **Base**: V0.0（新 skill）
- **Upgrade Date**: 2026-07-30
- **Upgrade Trigger**: simonlin1212/TradingAgents-astock 集成（阶段 25.2）
- **Author**: 天龙引擎集成
- **License**: Apache-2.0（与上游一致）
- **Triggers**: 21 个新增关键词