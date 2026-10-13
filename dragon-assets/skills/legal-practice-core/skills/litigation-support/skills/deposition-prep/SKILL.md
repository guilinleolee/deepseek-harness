# deposition-prep - 取证准备助手

## L0: 一句话描述 (≤15字)
证人取证问题生成与准备

## L1: 使用场景 (50-100字)
诉讼支持工程师基于案件档案和证据材料，生成取证（Deposition）问题清单，生成证人备忘录，准备取证要点清单。适用于73-05诉讼支持工程师的取证准备和73-03风控师的事前风险评估场景。

## L2: 详细文档

### 核心能力

1. **取证问题生成**
   - 基于案件争议焦点的问题链
   - 开放式与闭合式问题组合
   - 诱导性问题的适度使用

2. **证人备忘录**
   - 证人背景与利益分析
   - 已知陈述与潜在矛盾
   - 证人弱点与挑战策略

3. **取证要点清单**
   - 关键事实确认清单
   - 证据验证问题
   - 对方证人可信度评估

4. **取证策略报告**
   - 证人排名（高价值/高风险）
   - 取证顺序建议
   - 替代证人识别

### 问题类型矩阵

| 问题类型 | 用途 | 示例 |
|----------|------|------|
| **背景问题** | 建立证人资格 | "请介绍一下您的职位和职责" |
| **事实确认问题** | 确认已知事实 | "您何时开始与该公司合作？" |
| **探索性问题** | 发现新信息 | "那次会议的目的是什么？" |
| **确认问题** | 强化有利事实 | "您是否确认合同签署日期是..." |
| **挑战性问题** | 测试证人可信度 | "您的说法与文件记载不符，如何解释？" |

### 输出格式

```yaml
deposition_prep:
  case_id: string
  witness_name: string
  witness_role: string

  question_package:
    - category: "background|facts|exploration|confirmation|challenge"
      question: string
      purpose: string
      anticipated_answer: string
      follow_up: string

  witness_memo:
    background: string
    known_statements: [string]
    potential_contradictions: [string]
    vulnerabilities: [string]
    strategy_notes: string

  check_list:
    - item: string
      priority: "critical|high|medium"
      status: "pending|completed|not_applicable"

  recommendations:
    - action: string
      rationale: string
      order: number
```

### 使用命令

```bash
# 生成证人问题清单
/deposition-prep questions --witness "张三" --role "合同签署人" --case-id "CTR-001"

# 生成证人备忘录
/deposition-prep memo --witness "张三" --case-id "CTR-001" --output ./memo.md

# 生成取证要点清单
/deposition-prep checklist --case-id "CTR-001" --witness "张三" --output ./checklist.md

# 批量生成所有证人材料
/deposition-prep generate-all --case-id "CTR-001" --output-dir ./deposition-materials

# 取证策略报告
/deposition-prep strategy --case-id "CTR-001" --format markdown
```

### 取证问题模板

```markdown
# 取证准备：证人[张三]

## 证人基本信息
- 职位：[CEO]
- 与案件关系：[合同签署人]
- 利益立场：[原告方证人]

---

## 问题清单

### 第一部分：背景（建立证人资格）
1. 请介绍一下您的教育背景和工作经历
2. 您在[公司名称]担任什么职位？何时加入？
3. 您在公司中的具体职责是什么？

### 第二部分：事实确认（关键事实）
1. 请描述[合同名称]的签订过程
   - 预期回答：[描述谈判过程]
   - 跟进：为什么选择这家供应商？

2. 合同中的关键条款是如何确定的？
   - 预期回答：[描述条款讨论]
   - 跟进：谁参与了条款的最终确定？

### 第三部分：探索性问题（发现新信息）
1. 您是否了解合同履行过程中的任何问题？
2. 公司内部对这项合同有何讨论或争议？

### 第四部分：挑战性问题（测试可信度）
1. 您的说法与[文件名称]中的记载不一致，您如何解释？
2. [日期]的邮件显示您当时知道[情况]，但您现在说不了解，请说明

---

## 证人备忘录

### 潜在矛盾
- 陈述1：2024年1月才参与合同谈判
- 文件证据：2023年11月即参与讨论

### 需要挑战的弱点
- 证人声称不了解财务条款，但邮件显示其直接参与了价格谈判

### 策略建议
- 从[日期]的邮件入手，逐步揭示证人参与程度
```

### 与天龙引擎协同

```yaml
天龙岗位协同:
  73-05 诉讼支持工程师: deposition-prep主调用者
  73-03 风控师: 取证风险评估数据消费者

数据流:
  demand-intake → 案件档案 → deposition-prep
  claim-chart-builder → 图表 → deposition-prep问题生成
  deposition-prep → 取证材料 → 路由至73-05出庭准备
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal deposition-prep |