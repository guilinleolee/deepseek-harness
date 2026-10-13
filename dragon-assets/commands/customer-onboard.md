---
name: customer-onboard
description: FDE客户入场引导——签约后建立客户档案、启动fieldbook、初始化天龙调用链
invokable: true
allowed-tools: Write, Read, Bash, TodoWrite
argument-hint: [客户名]
model: sonnet
---
# 客户入场引导（customer-onboard）

FDE 工作流 **land** 阶段的标准化入口。客户签 NDA / 合同后第一个动作。

## 参数

- **客户名**: $1 (必需) - 用 `[A-Za-z0-9_-]+` 命名（参考 [[天龙引擎-CEC客户工程中心-蓝图]]）

## 执行流程

### 1. 验证前置条件
- [ ] 已签约（含 NDA / SOW）
- [ ] 客户名符合命名规范（无中文/空格/特殊字符）
- [ ] 已分配客户档案目录路径

### 2. 创建客户目录骨架

基于 `~/.claude/skills/fde-onboarding-runbook/SKILL.md` 模板，在天龙本地建立：

```
~/customers/$1/
├── profile.md            # 客户档案（行业/规模/干系人/决策链）
├── interviews/           # 访谈记录原始笔记
│   └── .gitkeep
├── fieldbook/            # FDEOps 风格客户记忆
│   └── land.md           # 进场记录
├── health/               # 健康度仪表盘
│   └── baseline.md       # 基线状态
├── contract/             # 合同相关
│   └── sow.md            # SOW 副本
└── README.md             # 客户目录索引
```

### 3. 初始化 profile.md

从 SOW + NDA 提取以下字段写入 `profile.md`：

| 字段 | 来源 | 必填 |
|---|---|---|
| 客户名 | SOW | ✅ |
| 行业 / 规模 | SOW | ✅ |
| 关键干系人 | 销售交接 | ✅ |
| 决策链深度 | 销售交接 | ✅ |
| 进场日期 | SOW | ✅ |
| 合同金额 / 档位 | SOW | ✅ |
| 已尝试方案 | 客户自述 | ⭕ |
| 风险等级 | FDE 评估 | ⭕ |

### 4. 启动 land.md（fieldbook 第一页）

格式参考 [[Quivly Skills]] `kickoff-prep`：

```markdown
# LAND - $1 - YYYY-MM-DD

## 进场事实
- 进场日期: YYYY-MM-DD
- 签约金额: X 万
- 档位: 报告级 / 周顾问级 / 项目级

## 干系人确认
| 角色 | 姓名 | 联系方式 | 影响力 |
|---|---|---|---|
| 决策人 | ... | ... | 高 |
| 使用人 | ... | ... | 中 |
| 配合人 | ... | ... | 中 |

## 首次接触承诺
- 客户期待: [一句话]
- 我们承诺: [一句话]
- 风险信号: [无/有]

## 下一步（48h 内）
- [ ] 启动访谈（调用 /customer-interview）
- [ ] 同步 [[agents/38-sales-manager]] 交接清单
```

### 5. 调用 [[agents/39-forward-deployed-engineer]]

把 `profile.md` + `land.md` 路径传给天龙，由 FDE 子代理继续推进 **discover** 阶段。

### 6. 在天龙 memory 追加 entry

```
## [YYYY-MM-DD] customer-onboard | $1
- 客户档案已建：~/customers/$1/
- FDE 阶段：land → discover
- 调用链：/customer-interview（下一步）
```

## 使用示例

```bash
# 完整进场
/customer-onboard acme-corp

# 指定档位
/customer-onboard acme-corp 项目级
```

## 反向链接

- [[agents/39-forward-deployed-engineer]] — 接管后续阶段
- [[Quivly Skills]] `kickoff-prep` — fieldbook 模板
- [[天龙引擎-CEC客户工程中心-蓝图]] — 目录结构规范
- [[03-FDE交付模板]] A 节 — 客户与进场记录