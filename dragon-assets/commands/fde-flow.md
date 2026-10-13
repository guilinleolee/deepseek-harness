---
name: fde-flow
description: FDE全流程编排——land→discover→plan→build→ship→close六阶段自动推进
invokable: true
allowed-tools: All
argument-hint: [客户名] [起始阶段]
model: sonnet
---
# FDE 全流程编排（fde-flow）

天龙 CEC v1.0 核心 command。封装 FDE 六阶段（land → discover → plan → build → ship → close），调用对应 agent/skill 推进项目。

## 参数

- **客户名**: $1 (必需) - 必须已通过 `/customer-onboard` 建档
- **起始阶段**: $2 (可选) - 默认 land，可选 discover/plan/build/ship/close

## 执行流程

### 阶段 1：land（获客 + 进场）

**调用**：`/customer-onboard`
**天龙代理**：`[[agents/38-sales-manager]]` → `[[agents/39-forward-deployed-engineer]]`
**skill**：`fde-onboarding-runbook`
**产出**：
- `~/customers/$1/profile.md`
- `~/customers/$1/fieldbook/land.md`
- 干系人清单 + 决策链

**退出条件**：
- [ ] 客户档案已建
- [ ] 干系人 ≥ 3 人已确认
- [ ] 48h 内访谈时间已锁定

---

### 阶段 2：discover（发现 + 访谈）

**调用**：`/customer-interview`
**天龙代理**：`[[agents/39-forward-deployed-engineer]]` + `[[agents/32-user-insight]]`
**skill**：`customer-interview-template`
**产出**：
- `~/customers/$1/interviews/` ≥ 3 场访谈
- `problem-statement.md`（可执行问题定义）

**退出条件**：
- [ ] 关键干系人访谈覆盖 ≥ 80%
- [ ] problem-statement 经客户确认
- [ ] 成功指标量化（基线 + 目标 + 时间窗）

---

### 阶段 3：plan（方案 + 架构）

**调用**：直接调用 `[[agents/02-architect]]` + `[[agents/14-product-manager]]`
**天龙命令**：`/01架构师`
**产出**：
- 方案选项 1-3（最小/完整/不做）
- MVP 边界 + 里程碑
- 时间/成本估算

**退出条件**：
- [ ] 客户对方案选项表态
- [ ] SOW 草稿已发
- [ ] 报价单已确认

---

### 阶段 4：build（实施 + 跑通）

**调用**：`[[agents/03-builder]]` + `[[agents/04-validator]]`
**天龙命令**：`/02建模师` `/03验证师`
**产出**：
- MVP 可演示
- 测试用例覆盖 ≥ 80%
- 文档初稿

**退出条件**：
- [ ] MVP 通过 [[04-validator]] 验收
- [ ] 客户演示通过
- [ ] 部署脚本就绪

---

### 阶段 5：ship（上线 + 交接）

**调用**：`[[agents/16-devops]]` + `[[agents/07-scribe]]`
**天龙命令**：`/deploy` `/docs-sync`
**产出**：
- 上线包（代码 + 文档 + 配置）
- 客户方 owner 已指定
- 接管条件 / SLA 已签

**退出条件**：
- [ ] 客户环境跑通 7 天无 P0/P1
- [ ] 客户方 owner 签字确认接管
- [ ] 交付证据包已生成

---

### 阶段 6：close（复盘 + 续约）

**调用**：`/aar`
**天龙代理**：`[[agents/41-customer-success-architect]]` + `[[agents/04-validator]]`
**skill**：`account-health-dashboard`
**产出**：
- AAR 5 段齐全
- 客户健康度基线
- 续约/扩单/流失信号

**退出条件**：
- [ ] AAR 写入并完成反向链接
- [ ] 健康度仪表盘已建立
- [ ] 续约预测已上报

---

## 状态机

| 当前阶段 | 下一步动作 | 触发 command |
|---|---|---|
| land | 启动访谈 | `/customer-interview` |
| discover | 启动方案 | `/01架构师` |
| plan | 启动实施 | `/02建模师` |
| build | 启动测试 | `/03验证师` |
| ship | 启动复盘 | `/aar` |
| close | 启动 CS | `/customer-success-handoff`（未来） |

## 跨阶段规则

1. **每个阶段必须退出条件全勾**才能进入下一阶段
2. **任何阶段重大变更**（如客户改需求）→ 回退到上一阶段
3. **每个阶段产物必须进入 `~/customers/$1/`** 客户目录，建立可追溯记录
4. **每个阶段触发天龙 memory 增量更新**

## 使用示例

```bash
# 从头开始（自动从 land 推进）
/fde-flow acme-corp

# 从 discover 起步（已有 profile.md）
/fde-flow acme-corp discover

# 从 close 复查（项目已交付）
/fde-flow acme-corp close
```

## 反向链接

- [[FDE]] — FDE 概念
- [[天龙引擎-FDE能力映射]] — 每个阶段的天龙调用
- [[天龙引擎-CEC客户工程中心-蓝图]] — CEC 架构
- [[03-FDE交付模板]] — 报告骨架
- [[06-FDE-AAR复盘机制]] — 5 段 AAR 模板