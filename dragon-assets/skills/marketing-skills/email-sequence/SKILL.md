---
name: email-sequence
description: "邮件序列设计 - 自动化邮件流程、用户培育、转化优化。"
trigger: "邮件营销、邮件序列、自动化邮件、用户培育"
metadata:
  version: 1.0.0
  source: https://github.com/coreyhaines31/marketingskills
---

# Email Sequence

> **核心价值**：自动化用户培育，让邮件营销效率提升5倍。

## Before Starting

1. 确认已完善 `product-marketing-context`
2. 明确邮件序列目标（欢迎/培育/转化/挽回）

---

## 邮件序列类型

| 类型 | 触发条件 | 邮件数 | 目标 |
|------|----------|--------|------|
| **欢迎序列** | 新注册 | 3-5封 | 建立信任，引导首次使用 |
| **培育序列** | 特定行为 | 5-7封 | 教育用户，展示价值 |
| **转化序列** | 试用到期 | 3-5封 | 推动付费转化 |
| **挽回序列** | 流失预警 | 3-5封 | 激活用户，防止流失 |

---

## 欢迎序列模板

### 邮件1：欢迎+快速开始（立即发送）

```
主题：欢迎加入！这是你的快速开始指南

Hi [名字]，

欢迎加入 [产品名]！

我是 [创始人/团队]，感谢你选择我们。

接下来3天，我会每天分享一个使用技巧，
帮你快速上手。

今天，先完成这3步：
1. [步骤1]
2. [步骤2]
3. [步骤3]

[CTA按钮：开始使用]

有任何问题，直接回复这封邮件。

[签名]
```

### 邮件2：核心价值（+24小时）

```
主题：用这个技巧，[核心利益]

Hi [名字]，

昨天你完成了快速开始，
今天分享一个核心使用技巧。

[技巧描述+具体步骤]

这个技巧帮用户[具体结果]。

[案例/社会证明]

[CTA按钮：立即尝试]

明天，我会分享[预告]。

[签名]
```

### 邮件3：社会证明（+48小时）

```
主题：[数字]人都在这样用...

Hi [名字]，

你可能会好奇，其他用户是怎么用 [产品名] 的。

今天分享3个真实案例：

案例1：[用户] 用 [功能] 达成了 [结果]
案例2：[用户] 用 [功能] 达成了 [结果]
案例3：[用户] 用 [功能] 达成了 [结果]

[CTA按钮：查看完整案例]

你也能做到。

[签名]
```

---

## 邮件优化要素

### 1. 主题行优化

| 类型 | 示例 | 打开率 |
|------|------|--------|
| 好奇型 | "我发现了一个问题..." | +15% |
| 利益型 | "3个方法帮你..." | +10% |
| 紧迫型 | "仅剩24小时" | +20% |
| 个性化 | "[名字]，这是给你的" | +25% |

### 2. 发送时间优化

| 时间段 | 打开率 | 适用类型 |
|--------|--------|----------|
| 6-8点 | 高 | B2B工作邮件 |
| 10-11点 | 最高 | 通用 |
| 14-15点 | 中 | B2C休闲 |
| 20-21点 | 高 | B2C娱乐 |

### 3. 关键指标

| 指标 | 健康值 | 优秀值 |
|------|--------|--------|
| 打开率 | >20% | >35% |
| 点击率 | >2% | >5% |
| 退订率 | <0.5% | <0.2% |
| 回复率 | >1% | >3% |

---

## 自动化触发规则

```yaml
# 欢迎序列
trigger: user_signup
sequence:
  - email: welcome_1, delay: 0h
  - email: welcome_2, delay: 24h
  - email: welcome_3, delay: 48h
  - email: welcome_4, delay: 72h, condition: not_opened

# 培育序列
trigger: trial_start
sequence:
  - email: tip_1, delay: 0h
  - email: tip_2, delay: 48h, condition: logged_in
  - email: tip_3, delay: 96h, condition: used_feature
  - email: conversion, delay: 168h, condition: not_converted

# 挽回序列
trigger: no_activity_14_days
sequence:
  - email: re_engage_1, delay: 0h
  - email: re_engage_2, delay: 72h, condition: not_opened
  - email: re_engage_3, delay: 168h, condition: not_opened
```

---

## Output Format

```markdown
## 邮件序列方案

### 序列类型
- 类型：[欢迎/培育/转化/挽回]
- 触发条件：[条件]
- 目标：[目标]

### 邮件内容

#### 邮件1
- 延迟：[时间]
- 主题：[主题行]
- 内容摘要：[摘要]
- CTA：[按钮文案]

#### 邮件2
[同上]

### 预期效果
- 打开率：[预期]
- 点击率：[预期]
- 转化率：[预期]
```

---

## Related Skills

- [revops](../revops/SKILL.md) - 收益运营
- [churn-prevention](../churn-prevention/SKILL.md) - 流失预防
- [copywriting](../copywriting/SKILL.md) - 文案写作