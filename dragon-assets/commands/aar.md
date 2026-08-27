---
name: aar
description: FDE项目AAR复盘——5段强制结构+反向链接entity更新，确保知识复利
invokable: true
allowed-tools: Write, Read, TodoWrite
argument-hint: [客户名] [项目名]
model: sonnet
---
# 项目 AAR 复盘（aar）

FDE 工作流 **close** 阶段的强制动作。基于 [[06-FDE-AAR复盘机制]] 的 5 段结构，确保经验转化为可复用资产。

## 参数

- **客户名**: $1 (必需)
- **项目名**: $2 (必需)

## 触发时机（不是"想起来才做"）

| 时机 | 必做 | 备注 |
|---|---|---|
| 报告交付当天 | 立刻创建 AAR 草稿 | 趁记忆新鲜 |
| 客户验收后 3 天 | 补充客户反馈章节 | 客户感知最准 |
| 续约/流失后 7 天 | 补充续约/流失原因 | 复盘信号最强 |
| 每季度 | 跨客户横向 AAR | 找共性 |

## 执行流程

### 1. 加载 AAR 模板

读取 `~/.claude/skills/fde-onboarding-runbook/SKILL.md` 的 AAR 部分：

```markdown
---
type: aar
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
title: "AAR - $1 - $2"
summary: "[项目一句话总结] - 关键教训一句话"
tags: [AAR, 客户-$1, 项目类型, 教训]
related:
  - "[[FDE]]"
  - "[[Quivly Skills]]"
  - "[[03-FDE交付模板]]"
  - "[[天龙引擎-FDE能力映射]]"
confidence: 0.9
compilations: 1
---
```

### 2. 加载项目档案

读取 `~/customers/$1/` 下所有文件 + `interviews/` 记录，回顾：
- profile.md（客户档案）
- fieldbook/land.md → discover.md → plan.md → build.md → ship.md
- health/（健康度变化曲线）
- interviews/（关键引述）

### 3. 强制 5 段结构（不可跳，全填）

#### 段 1: 预期 vs 实际（Expectation vs Reality）

| 假设 | 预期 | 实际 | 偏差原因 |
|---|---|---|---|
| 客户决策链 ≤ 2 层 | 是 | 实际 3 层 | 初次访谈没问清 |
| 客户数据可访问 | 是 | 部分权限申请未批 | SOW 没明确权限清单 |
| 2 周可交付 | 是 | 实际 2.5 周 | 客户访谈协调慢 |
| ... | ... | ... | ... |

#### 段 2: 客户侧意外（Customer Surprises）
- 流程意外：客户比我们想象的更死板 / 更灵活
- 人意外：某个干系人突然离职 / 反水
- 合规意外：某条业务规则之前不知道

#### 段 3: 工具/方法问题（Tool & Method Issues）
- 哪些天龙 agent/skill 反复调用？哪些根本没用到？
- 哪些 skill 有用？哪些鸡肋？
- 哪个交付模板节段超出预期 / 被砍掉？

#### 段 4: 可复用的教训（Reusable Lessons）
- 新发现的 entity 候选（如新工具、新方法）→ 触发创建新笔记
- 现存 entity 的 confidence 需要调整（高估或低估）
- 现存 concept 的边界需要重新定义

#### 段 5: 下次要改的清单（Next-Time Action Items）
```markdown
- [ ] 在 [[03-FDE交付模板]] X 节加 Y 段
- [ ] 在 [[04-FDE客户获取与冷启动]] 决策链 >3 层列入红线
- [ ] 在 [[05-FDE定价与SOW模板]] 加"权限申请清单"附件
- [ ] 在 [[天龙引擎-FDE能力映射]] 把 X agent 标记为"高频调用"
```

### 4. 字数与链接强制（防敷衍）

| 项 | 下限 |
|---|---|
| 每段字数 | ≥ 100 字（否则视为敷衍） |
| 反向链接 entity/concept | ≥ 3 个 |
| 第 5 段 action item | ≥ 3 条 |

### 5. 写入 ~/customers/$1/aar/YYYY-MM-DD-$2.md

```
~/customers/$1/aar/
├── YYYY-MM-DD-$2.md           # 本次 AAR
├── YYYY-MM-DD-$2-客户反馈.md  # 验收后 3 天补
└── YYYY-MM-DD-$2-续约.md      # 续约/流失后 7 天补
```

### 6. 反向链接到所有相关 entity

调用 [[agents/07-scribe]] 更新：
- [[FDE]] / [[FDEOps]] / [[Quivly Skills]] — 调整 confidence 或 status
- [[03-FDE交付模板]] / [[04-FDE客户获取与冷启动]] — 在"下次要改的清单"里落实
- [[天龙引擎-FDE能力映射]] — 标注本项目高频调用了哪些 agent
- [[log]] — 追加 aar 操作记录

### 7. 调用 [[agents/41-customer-success-architect]]

把 AAR 摘要 + 教训清单传给 CS 架构师，由其继续推进 **客户成功 + 续约预测**。

### 8. 触发过期机制

AAR 创建后 14 天未完成 action item 的，[[index]] 自动标黄（待实施）。

## 使用示例

```bash
# 项目交付当天（草稿）
/aar acme-corp 前置调研报告

# 验收后 3 天（补客户反馈）
/aar acme-corp 前置调研报告 -append customer-feedback

# 续约/流失后 7 天
/aar acme-corp 前置调研报告 -append renewal-outcome
```

## 反向链接

- [[06-FDE-AAR复盘机制]] — 5 段模板 + 触发时机
- [[Quivly Skills]] `aar-template` — 国际版本参考
- [[agents/04-validator]] — 事实校验
- [[agents/41-customer-success-architect]] — CS 接管