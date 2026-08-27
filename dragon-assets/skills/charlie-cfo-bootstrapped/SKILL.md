---
license: UNKNOWN
triggers: ["charlie cfo bootstrapped", "Charlie CFO Bootstrapped Framework"]
---
# Charlie CFO Bootstrapped Framework

## L0: 一句话描述 (≤15字)
精益创业CFO框架，源自芒格智慧

## L1: 使用场景 (50-100字)
适用于Bootstrapped创业公司CFO决策支持，提供单位经济学、现金管理、资本配置等核心框架。以芒格多元思维模型为底层哲学，强调"没有资本负债也是资本"。

## L2: 详细文档

### 来源项目
> [EveryInc/charlie-cfo-skill](https://github.com/EveryInc/charlie-cfo-skill) - 216 Stars, MIT License

### 核心哲学
以芒格多元思维模型为底层，应用于精益创业财务决策：
- **逆向思维**：从终点反推，而非正向预测
- **心理账户**：理解资金的时间价值
- **二阶思维**：考虑决策的长期后果
- **能力圈**：专注核心指标而非全部指标

### 核心决策领域

| 领域 | 关键决策 | 核心指标 |
|------|---------|---------|
| **单位经济学** | 定价、客户获取 | LTV, CAC, Payback |
| **现金管理** | 融资时机、支出节奏 | Runway, Burn Multiple |
| **资本配置** | 招聘、扩张时机 | ROI, Payback |
| **运营资本** | 收款、付款条款 | DSO, DPO, CCC |

### 指标基准体系

#### 单位经济学基准

| 指标 | 卓越 | 健康 | 一般 | 危险 |
|------|------|------|------|------|
| **LTV:CAC** | 7-8x | 3x | 2x | <1x |
| **CAC Payback** | <6个月 | <12个月 | 12-18个月 | >18个月 |
| **LTV** | >$100K | $30K-100K | $10K-30K | <$10K |

#### 现金管理基准

| 指标 | 卓越 | 健康 | 一般 | 危险 |
|------|------|------|------|------|
| **Burn Multiple** | <0.5x | <1x | 1-2x | >2x |
| **Runway** | >24个月 | 18-24个月 | 12-18个月 | <12个月 |
| **Cash Conversion** | >100% | 75-100% | 50-75% | <50% |

#### 收入效率基准

| 指标 | 卓越 | 健康 | 一般 | 危险 |
|------|------|------|------|------|
| **Magic Number** | >1.0 | 0.5-1.0 | 0.25-0.5 | <0.25 |
| **Revenue/Employee** | >$1M | $500K-1M | $250K-500K | <$250K |
| **Gross Margin** | >80% | 70-80% | 60-70% | <60% |

### 核心公式

```
# 单位经济学
LTV = ARPU × Gross Margin / Churn Rate
CAC Payback = CAC / (ARPU × Gross Margin)
LTV:CAC = LTV / CAC

# 现金管理
Burn Multiple = Net Burn / Net New ARR
Runway = Cash / Monthly Burn
Cash Conversion = Operating Cash Flow / Net Income

# 运营资本
Cash Conversion Cycle = DSO + DIO - DPO
DSO = (Accounts Receivable / Revenue) × 365
DPO = (Accounts Payable / COGS) × 365
DIO = (Inventory / COGS) × 365

# 收入效率
Magic Number = Net New ARR / S&M Spend
Revenue per Employee = Revenue / FTE Count
```

### 精益案例库

| 公司 | 核心洞察 | 关键指标 |
|------|---------|---------|
| **Mailchimp** | $12B退出，20年自力更生 | 零融资，50%年增速 |
| **Zapier** | $5B估值，远程优先文化 | 1000+集成，PLG主导 |
| **Basecamp** | 25年持续盈利 | 独立非上市，社区驱动 |
| **ConvertKit** | 51%利润率逆转 | 从订阅疲劳到创作者经济 |
| **Zoho** | $1B+营收，家族控制 | 产品驱动，零债务 |

### 决策检查清单

#### 新客户获取决策
- [ ] LTV:CAC ≥ 3x？
- [ ] CAC Payback < 12个月？
- [ ] 边际CAC在降低？
- [ ] 非营销获客占比 > 30%？

#### 融资时机决策
- [ ] Burn Multiple < 1.5x？
- [ ] Runway < 12个月？
- [ ] 有明确的里程碑需要资金？
- [ ] 条款有利于创始人？

#### 招聘决策
- [ ] 新人ROI > 2x？
- [ ] Revenue per Employee保持或增长？
- [ ] 有12个月现金支撑？
- [ ] 关键岗位空缺影响增长？

### 与天龙引擎协同

| 天龙岗位 | 协同方式 |
|---------|---------|
| **60-01 投资总监** | 投资决策框架 |
| **64-01 量化研究员** | 指标量化分析 |
| **80-01 财务总监** | 财务数据解读 |
| **00分析师** | 逆向决策思维 |

### 核心命令

```bash
# 单位经济学分析
[@60-01] 使用charlie-cfo分析客户获取效率
[@60-01] 计算LTV:CAC比例
[@60-01] 评估CAC Payback健康度

# 现金管理
[@60-01] 计算Burn Multiple
[@60-01] 评估Runway健康度
[@60-01] 现金转换效率分析

# 运营决策
[@60-01] 招聘ROI评估
[@60-01] 融资时机检查
[@60-01] 运营资本优化

# 基准对比
[@60-01] 对比SaaS行业基准
[@60-01] 精益创业标杆分析
```

### 预期收益

| 指标 | 效果 |
|------|------|
| **CFO决策质量** | 单位经济学框架支撑 |
| **指标基准** | 行业对标标准化 |
| **逆向思维** | 芒格多元思维模型应用 |
| **案例洞察** | 5家精益公司经验复用 |

### 技能文件

- [skills/charlie-cfo-bootstrapped/SKILL.md](skills/charlie-cfo-bootstrapped/SKILL.md)
- [skills/charlie-cfo-bootstrapped/references/metrics-benchmarks.md](skills/charlie-cfo-bootstrapped/references/metrics-benchmarks.md)
- [skills/charlie-cfo-bootstrapped/references/case-studies.md](skills/charlie-cfo-bootstrapped/references/case-studies.md)
- [skills/charlie-cfo-bootstrapped/references/decision-checklist.md](skills/charlie-cfo-bootstrapped/references/decision-checklist.md)


### 共享模块

> 天龙引擎各岗位共用的精益创业CFO模块，支持60-01投资总监/64-01量化研究员/80-01财务总监/charlie-cfo调用。

- [skills/shared/metrics-benchmarks.js](skills/shared/metrics-benchmarks.js) — 精益指标基准（4-tier: 卓越/健康/一般/危险，Bootstrap/VC双目标）
- [skills/shared/decision-checklist.js](skills/shared/decision-checklist.js) — 逆向决策检查清单（8大决策领域，Charlie Munger多元思维模型）
- [skills/shared/case-studies.js](skills/shared/case-studies.js) — Bootstrap案例库（Mailchimp/Zapier/Basecamp/ConvertKit/Zoho）
