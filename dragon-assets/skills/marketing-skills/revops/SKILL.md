---
name: revops
description: "收益运营 - 线索生命周期管理、收入流程优化、数据驱动增长。"
trigger: "收益运营、RevOps、线索生命周期、收入增长"
metadata:
  version: 1.0.0
  source: https://github.com/coreyhaines31/marketingskills
---

# RevOps (Revenue Operations)

> **核心价值**：打通营销-销售-客户成功，实现收入可预测、可规模化增长。

## Before Starting

1. 确认已完善 `product-marketing-context`
2. 获取现有收入流程数据

---

## 核心概念

### 什么是RevOps？

```
传统模式（孤岛）：
营销 → 销售 → 客户成功
 ↓      ↓        ↓
各自优化  各自优化   各自优化

RevOps模式（统一）：
营销 ↔ 销售 ↔ 客户成功
       ↓
    RevOps团队统一优化
```

### 三大支柱

| 支柱 | 职责 | 关键指标 |
|------|------|----------|
| **营销运营** | 线索获取与培育 | MQL数量、CAC |
| **销售运营** | 线索转化与成交 | 转化率、ACV |
| **客户成功运营** | 留存与扩张 | NRR、LTV |

---

## 线索生命周期管理

### 1. 线索阶段定义

```
陌生访客 → 潜在线索 → MQL → SQL → 客户 → 忠诚客户
    ↓         ↓        ↓      ↓      ↓        ↓
  曝光      留资     评分    跟进   成交    推荐/复购
```

### 2. 线索评分模型

| 行为 | 分数 | 阶段 |
|------|------|------|
| 访问官网 | +1 | 认知 |
| 下载白皮书 | +5 | 兴趣 |
| 参加Webinar | +10 | 考虑 |
| 申请试用 | +20 | 意向 |
| 联系销售 | +30 | 决策 |
| 查看定价页 | +15 | 评估 |

**阈值设定**：
- MQL：≥30分
- SQL：≥50分 + 销售确认

### 3. 线索流转规则

```yaml
# MQL → SQL
condition:
  - score >= 50
  - has_budget: true
  - timeline <= 90_days
action:
  - assign_to: sales_rep
  - notify: slack_sales_channel
  - create_task: follow_up_24h

# SQL → 成交
condition:
  - proposal_sent
  - contract_signed
action:
  - close_date: update
  - revenue: record
  - notify: customer_success
```

---

## 关键指标体系

### 收入指标

| 指标 | 公式 | 健康值 |
|------|------|--------|
| **ARR** | 年度经常性收入 | - |
| **MRR** | 月度经常性收入 | - |
| **ARPU** | ARPU = ARR / 客户数 | 因产品而异 |
| **ACV** | 平均合同价值 | 因产品而异 |

### 效率指标

| 指标 | 公式 | 健康值 |
|------|------|--------|
| **CAC** | 获客成本 = 营销销售费用 / 新客户数 | < LTV/3 |
| **LTV** | 客户终身价值 | > 3×CAC |
| **CAC回收期** | CAC / 月毛利 | < 12个月 |
| **LTV/CAC** | LTV / CAC | > 3 |

### 增长指标

| 指标 | 公式 | 健康值 |
|------|------|--------|
| **NRR** | 净收入留存率 | > 100% |
| **GRR** | 毛收入留存率 | > 85% |
| **增长率** | (本月-上月)/上月 | 因阶段而异 |

---

## 收入预测模型

### 预测公式

```
下月收入预测 = 现有MRR + 新增预测 - 流失预测

新增预测 = Pipeline × 转化率 × 平均ACV
流失预测 = 现有MRR × 历史流失率
```

### Pipeline阶段权重

| 阶段 | 权重 | 说明 |
|------|------|------|
| 初步沟通 | 10% | 可能性低 |
| 需求确认 | 25% | 有意向 |
| 方案演示 | 50% | 较高可能 |
| 商务谈判 | 75% | 高可能 |
| 合同签署 | 90% | 基本确定 |

---

## Output Format

```markdown
## RevOps诊断报告

### 收入概况
- ARR：[金额]
- MRR：[金额]
- 同比增长：[百分比]

### 漏洞分析
| 阶段 | 转化率 | 问题 | 建议 |
|------|--------|------|------|
| 访客→线索 | [X]% | [问题] | [建议] |
| 线索→MQL | [X]% | [问题] | [建议] |
| MQL→SQL | [X]% | [问题] | [建议] |
| SQL→成交 | [X]% | [问题] | [建议] |

### 关键指标
- CAC：[金额]
- LTV：[金额]
- LTV/CAC：[比值]
- NRR：[百分比]

### 优化建议
1. [建议1]
2. [建议2]
3. [建议3]
```

---

## Related Skills

- [analytics-tracking](../analytics-tracking/SKILL.md) - 数据追踪
- [churn-prevention](../churn-prevention/SKILL.md) - 流失预防
- [pricing-strategy](../pricing-strategy/SKILL.md) - 定价策略