---
license: UNKNOWN
name: fde-onboarding-runbook
description: FDE客户入场运行手册——profile+fieldbook+contract+sandbox+AAR五件套的标准化模板和检查清单
github_repo: dragon-engine/cec
github_hash: pending
last_updated: 2026-08-10
source_type: dragon-engine-original
triggers: ["fde-onboarding", "FDE客户入场", "fde-onboarding-runbook", "FDE runbook"]
---

# FDE 客户入场运行手册（fde-onboarding-runbook）

天龙 CEC v1.0 核心 skill。封装 FDE 工作流 **land** 阶段的全部入场标准化动作。

## L0: 一句话描述 (≤15字)
FDE客户入场五件套模板

## L1: 使用场景 (50-100字)
客户签约后第一动作：建立客户档案（profile）、启动 fieldbook、复制 SOW、初始化 sandbox、AAR 占位。覆盖天龙 FDE 工作流 land 阶段，与 [[agents/39-forward-deployed-engineer]] 和 `/customer-onboard` command 协同使用。

## L2: 详细文档

### 客户目录标准结构

```
~/customers/$CUSTOMER/
├── profile.md            # 客户档案（必填）
├── interviews/           # 访谈原始记录
│   └── YYYY-MM-DD-{主题}-{干系人}.md
├── fieldbook/            # FDEOps 风格客户记忆
│   ├── land.md           # 进场记录（必填）
│   ├── discover.md       # 发现阶段
│   ├── plan.md           # 方案阶段
│   ├── build.md          # 实施阶段
│   └── ship.md           # 上线阶段
├── health/               # 健康度仪表盘
│   ├── baseline.md       # 基线
│   └── dashboard.md      # 实时
├── contract/             # 合同相关
│   ├── sow.md            # SOW 副本（脱敏）
│   └── nda.md            # NDA 副本
├── sandbox/              # 客户环境（可选）
│   └── README.md         # sandbox 说明
├── aar/                  # AAR 复盘
│   └── YYYY-MM-DD-{项目}.md
└── README.md             # 客户目录索引
```

### profile.md 模板

```markdown
# $CUSTOMER - 客户档案

## 基本信息
- 客户名: $CUSTOMER
- 行业: 
- 规模: 
- 主营: 
- 成立: 

## 关键干系人
| 角色 | 姓名 | 联系方式 | 影响力 | 立场 |
|---|---|---|---|---|
| 决策人 | ... | ... | 高 | 支持/中立/反对 |
| 使用人 | ... | ... | 中 | ... |
| 配合人 | ... | ... | 中 | ... |
| 反对者 | ... | ... | 高/中 | 反对原因 |

## 决策链
- 层级: X 层
- 关键节点: 
- 周期: 

## 进场合同
- 签约日期: YYYY-MM-DD
- 档位: 报告级 / 周顾问级 / 项目级
- 金额: X 万
- 周期: X 周
- SOW: [链接]

## 客户已尝试方案
| 时间 | 方案 | 结果 | 教训 |
|---|---|---|---|
| ... | ... | ... | ... |

## 风险评估（老李视角）
- 数据可访问性: 高 / 中 / 低
- 决策链复杂度: 简单 / 中 / 复杂
- 客户期望合理性: 高 / 中 / 低
- 综合风险: 🟢 / 🟡 / 🔴

## 关键引述（来自首次接触）
> "..."

## 反向链接
- [[FDE]]
- [[天龙引擎-CEC客户工程中心-蓝图]]
- [[03-FDE交付模板]] A 节
```

### fieldbook/land.md 模板

```markdown
# LAND - $CUSTOMER - YYYY-MM-DD

## 进场事实
- 进场日期: YYYY-MM-DD
- 签约金额: X 万
- 档位: 报告级 / 周顾问级 / 项目级
- 周期: X 周

## 干系人确认（基于 profile.md）
- 决策人已确认: [名单]
- 关键使用人已确认: [名单]

## 首次接触承诺
- 客户期待: [一句话]
- 我们承诺: [一句话]
- 风险信号: [无/有 + 描述]

## 48h 内必做
- [ ] 启动访谈（调用 /customer-interview）
- [ ] 同步 [[agents/38-sales-manager]] 交接清单
- [ ] 客户方 owner 确认（决策人本人）
- [ ] 数据访问权限清单（基于 SOW）

## 资源准备
- [ ] sandbox 环境就绪（如有）
- [ ] 客户方对接人联系方式归档
- [ ] NDA 副本已存 contract/nda.md

## 反向链接
- [[agents/39-forward-deployed-engineer]] — 接管 discover
- [[Quivly Skills]] `kickoff-prep` — 模板参考
```

### contract/sow.md 模板

SOW 副本按 [[05-FDE定价与SOW模板]] 模板，**强制脱敏后存入**：
- 公司名 → `客户X`
- 金额 → 区间（如 `5-10万`）
- 干系人 → `决策人A` / `使用人B`

### sandbox/README.md 模板

```markdown
# $CUSTOMER - Sandbox 环境

## 类型
- [ ] e2b-sandbox（云端隔离）
- [ ] nemo-claw-sandbox（本地 Docker）
- [ ] 客户 VPC（生产环境镜像）
- [ ] 仅文档（无代码环境）

## 访问权限
- 老李本人: ✅
- 客户方 owner: ✅
- 第三方: ❌（需 SOW 明确授权）

## 数据脱敏规则
- [ ] 真实客户数据已脱敏（手机号/身份证/订单）
- [ ] 仅保留业务流程示范数据
- [ ] 客户方审核通过脱敏方案

## 操作日志
- YYYY-MM-DD 创建
- YYYY-MM-DD 最近访问

## 反向链接
- [[agents/05-security-reviewer]] — 审计
```

### aar/YYYY-MM-DD-{项目}.md 模板

详见 [[06-FDE-AAR复盘机制]] 的 5 段结构。

### 客户目录命名约束（强约定）

| 规则 | 说明 |
|---|---|
| 命名字符 | 仅 `[A-Za-z0-9_-]+` |
| 禁止中文 | 避免 Obsidian 双链断裂 |
| 禁止空格 | 避免 shell 转义问题 |
| 长度 | ≤ 32 字符 |
| 例 | `acme-corp` ✅ / `客户 A` ❌ / `客户-A 公司` ❌ |

### 客户目录 .gitignore 推荐

```bash
# 在 d:/知识库/.gitignore 增加：
customers/*/profile.md          # 含联系方式
customers/*/interviews/         # 含客户原话
customers/*/contract/           # 合同原文
customers/*/health/dashboard.md # 含使用数据

# 例外（AAR 可入 git）
!customers/*/aar/
```

## 天龙岗位升级

| 阶段 | 调用 |
|---|---|
| land | [[agents/39-forward-deployed-engineer]] + `/customer-onboard` |
| 后续 | 由 [[agents/39-forward-deployed-engineer]] 推进 discover/plan/build/ship |
| 安全审计 | [[agents/05-security-reviewer]] — 数据脱敏 + 权限 |

## 反向链接

- [[agents/39-forward-deployed-engineer]] — FDE 子代理
- [[FDEOps]] — 第二大脑理念
- [[Quivly Skills]] `kickoff-prep` `account-360` — 国际版本
- [[天龙引擎-CEC客户工程中心-蓝图]] — CEC 架构
- [[03-FDE交付模板]] — A 节客户与进场
- [[06-FDE-AAR复盘机制]] — AAR 模板