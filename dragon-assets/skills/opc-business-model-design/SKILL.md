---
license: UNKNOWN
name: opc-business-model-design
description: 商业模式设计 - 确定怎么赚钱。Lean Canvas（9模块）+ BMC Lite（5模块）+ BMC9（9积木），结合定价策略和风险假设，生成完整商业模式方案。
trigger: /opc-business-model | opc商业模式 | opc盈利模式 | 商业模式设计
version: V1.0
source: easychen/opc-methodology
created: 2026-05-02
triggers: ["opc business model design", "OPC-Business-Model-Design 商业模式设计"]
---

# OPC-Business-Model-Design 商业模式设计

## 定位陈述

**职能**: 商业模式设计 | **协议**: OPC | **边界**: 只做模式结构，不进入具体定价数字或合同细节

## 核心价值

帮助用户确定"用什么方式赚钱"，通过三种商业模式画布（Lean Canvas/BMC Lite/BMC9）结构化呈现，结合定价策略和风险假设，给出可选择的商业模式方案。

## 核心概念

### Lean Canvas（精益画布，9模块）

| 模块 | 描述 | 核心问题 |
|------|------|---------|
| **Problem** | 最痛的3个问题 | 用户最痛的是什么 |
| **Customer Segments** | 目标客户细分 | 为谁创造价值 |
| **Unique Value Proposition** | 独特价值主张 | 为什么用户选你不选别人 |
| **Solution** | 解决方案 | 用什么方式解决 |
| **Channels** | 渠道 | 怎么触达用户 |
| **Revenue Streams** | 收入来源 | 怎么收钱 |
| **Cost Structure** | 成本结构 | 怎么花钱 |
| **Key Metrics** | 关键指标 | 跟踪什么数据 |
| **Unfair Advantage** | 不对称优势 | 什么护城河 |

### BMC Lite（商业模式精简版，5模块）

适合快速验证阶段，只聚焦5个核心问题：

| 模块 | 描述 | 核心问题 |
|------|------|---------|
| **Customer Segments + UVP** | 客户+价值主张 | 卖给谁、为什么买 |
| **Key Resources** | 关键资源 | 靠什么交付 |
| **Channels + Customer Relationships** | 渠道+客户关系 | 怎么卖 |
| **Key Revenue** | 主要收入来源 | 收什么钱 |
| **Key Cost** | 主要成本 | 花什么钱 |

### BMC9（9积木，Ash Maurya版本）

| 积木 | 说明 |
|------|------|
| CS - Customer Segments | 客户细分 |
| VP - Value Proposition | 价值主张 |
| KR - Key Resources | 关键资源 |
| CR - Customer Relationships | 客户关系 |
| CH - Channels | 渠道 |
| KS - Key Activities | 关键活动 |
| KP - Key Partnerships | 关键合作伙伴 |
| FR - Financials | 财务（收入/成本/毛利） |

### 定价策略参考

| 定价模式 | 适用场景 | 示例 |
|---------|---------|------|
| 成本加成 | 标准化产品 | 材料+工时×系数 |
| 价值定价 | 高感知价值 | 按用户收益定价 |
| 竞争定价 | 红海市场 | 参考竞品定价 |
| 渗透定价 | 快速获客 | 低价切入再提价 |
| 订阅定价 | 持续服务 | 月/年/终身订阅 |
| 成效定价 | 结果导向 | 按效果收费 |

### 风险假设

商业模式成立依赖的关键假设：
- 用户真的会付费吗
- 成本真的能覆盖吗
- 规模能放大吗
- 合规/法律风险有多大

## 执行协议

### SCP协议（苏格拉底对话）

- 默认**一次只问一个模块**（或2个紧密相关模块合并）
- 给出**3种商业模式方案**，并附加"4. 我有自己的方案"
- **用户确认后再写入正式结果**
- 不直接给推荐结论，只做方案分析

### 执行步骤

```
1. 解释本步目标和三种画布
   └→ Lean Canvas适合详细规划
   └→ BMC Lite适合快速验证
   └→ BMC9适合模块化思考
   └→ 先选一种作为主框架

2. 一次只问一个模块（或2-3个轻量相关模块）
   └→ 目标客户是谁
   └→ 解决什么问题/创造什么价值
   └→ 通过什么方式交付
   └→ 怎么收钱
   └→ 主要成本是什么

3. 每轮回答后，给简短确认

4. 生成3种商业模式方案：
   方案1（服务型）：
   - 画布类型：[Lean Canvas / BMC Lite / BMC9]
   - 核心模式：[服务/产品/订阅/成效等]
   - 价值主张：
   - 收入来源：
   - 成本结构：
   - 关键假设：
   - 优点：
   - 代价/风险：

   方案2（产品型）：
   （同上格式）

   方案3（混合型）：
   （同上格式）

5. 默认增加"4. 我有自己的方案"

6. 让用户选择、组合、修改，或直接提出自己的版本

7. 用户确认后，再写入正式结果
```

## 本阶段边界

### ✅ 本步做什么

- 确定商业模式类型（服务/产品/订阅/平台等）
- 明确价值主张和目标客户
- 确认收入来源和定价逻辑
- 识别关键成本结构
- 分析核心风险假设

### ❌ 本步不做什么

- 不给具体定价数字（→后续运营阶段）
- 不写合同模板或法律文件（→法务阶段）
- 不做详细财务预测（→仪表盘回顾阶段）
- 不设计具体产品功能（→MVP设计阶段）

**越界检测**：如果出现"定多少钱""合同怎么写""能赚多少"：
> "定价和财务预测在后续阶段处理。现在先把商业模式的框架确认好。"

## 前置依赖

**优先读取**：
- `opc-doc/outputs/02-niche-positioning/positioning-statement.md`
- `opc-doc/outputs/03-value-proposition/messaging.md`
- `opc-doc/outputs/06-mvp-design/mvp-spec.md`

**如果前置不完整**：先判断当前对话是否已有足够信息
- 如果够，继续
- 如果不够，先建议完成前置阶段

## 落盘文件

用户确认商业模式后，**立即**写入：

```
opc-doc/outputs/04-business-model/
├── lean-canvas.md              # Lean Canvas完整版
├── business-model-canvas-lite.md  # BMC Lite精简版
├── pricing-notes.md           # 定价策略说明
└── risky-assumptions.md       # 风险假设清单

opc-doc/state/
├── current-stage.json           # {"stage": "04-business-model", "status": "completed", "next_stage": "05-risky-assumptions", "summary": "一句话商业模式核心"}
└── decisions.json            # 追加商业模式确认
```

**落盘完成后告知用户**：
> "✅ 商业模式方案已保存。下次对话可以从风险假设确认继续。"

**只有落盘完成后，才可以提示进入 `opc-risky-assumptions` 或 `opc-mvp-design`**。

## 完成标准

- [ ] 商业模式类型已确定
- [ ] 价值主张和目标客户已明确
- [ ] 收入来源和定价逻辑已确认
- [ ] 成本结构已识别
- [ ] 关键风险假设已列出
- [ ] 用户已确认主商业模式

## 异常处理

| 情况 | 处理 |
|------|------|
| 用户说"我不知道怎么赚钱" | 从已有价值主张反推收入可能 |
| 多个商业模式都可行 | 并列呈现，让用户选择主模式 |
| 前置依赖缺失 | 引导补全再继续 |

## 命令触发

| 命令 | 说明 |
|------|------|
| `/opc-business-model` | 启动商业模式设计流程 |
| `/opc-business-model-design` | 启动商业模式设计流程 |
| `opc商业模式` | 启动商业模式设计流程 |

## 天龙引擎协同

| 天龙岗位 | 协同方式 |
|---------|---------|
| **25-01营销战略策划** | 商业模式战略输入 |
| **30-01营销总监** | 渠道策略和客户关系设计 |
| **50-01产品策划** | 产品作为商业模式核心 |
| **22-02品牌策划** | 品牌价值主张设计 |
| **60-01投资总监** | 商业模式财务评估 |
| **22-01战略策划** | 商业模式战略整合 |

---

**版本**: V1.0 | **来源**: easychen/opc-methodology | **日期**: 2026-05-02
