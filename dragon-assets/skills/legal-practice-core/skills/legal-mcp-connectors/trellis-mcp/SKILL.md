# trellis-mcp - 诉讼进度追踪连接器

## L0: 一句话描述 (≤15字)
诉讼案件进度追踪与状态监控

## L1: 使用场景 (50-100字)
并购法务工程师通过MCP协议连接Trellis案件数据库，追踪诉讼进度、监控关键日期、生成案件状态报告。适用于78-01法律总顾问的活跃诉讼管理和73-03风控师的风险预警场景。

## L2: 详细文档

### 核心能力

1. **案件状态追踪**
   - 活跃案件实时监控
   - 关键日期预警
   - 法官分配跟踪

2. **进度里程碑**
   - 诉答阶段完成度
   - 证据开示进度
   - 动议截止日追踪

3. **案件分析报告**
   - 法官裁决模式分析
   - 案件持续时间预估
   - 和解可能性评估

### 输出格式

```yaml
trellis_case_tracking:
  matter_id: string
  case_name: string
  court: string
  docket_number: string
  filed_date: date
  status: "Active|Settled|Dismissed|Trial"

  parties:
    plaintiffs: [string]
    defendants: [string]

  judge:
    name: string
    assigned_date: date
    ruling_pattern: "string"

  milestones:
    - phase: string
      due_date: date
      status: "pending|in_progress|completed|overdue"
      completed_date: date

  key_dates:
    - event: string
      date: date
      reminder_days: number

  risk_assessment:
    exposure_level: "high|medium|low"
    trial_probability: number
    settlement_range: "string"
    estimated_duration_months: number

  alerts:
    - type: "deadline|hearing|discovery|settlement"
      description: string
      urgency: "critical|high|medium"
      due_date: date
```

### 使用命令

```bash
# 追踪案件
/mcp trellis track --case-id "CASE-001" --monitor daily

# 查看进度
/mcp trellis status --case-id "CASE-001" --format table

# 关键日期预警
/mcp trellis alerts --case-id "CASE-001" --days 30

# 法官分析
/mcp trellis judge-analysis --judge "Judge Smith" --court "SDNY"

# 生成报告
/mcp trellis report --case-id "CASE-001" --format markdown --output ./case/report.md

# 批量导入
/mcp trellis import --file ./cases.csv --monitor weekly
```

### 诉讼进度报告模板

```markdown
# 诉讼进度追踪报告

## 案件概览
- 案件编号：LIT-2026-001
- 案件名称：XYZ公司 v. ABC公司
- 受理法院：纽约南区联邦地区法院
- 案号：1:26-cv-01234
- 当前状态：🟠 证据开示阶段

## 当事人
| 角色 | 名称 | 代理律所 |
|------|------|---------|
| 原告 | XYZ公司 | 世达律师事务所 |
| 被告 | ABC公司 | 高伟绅律师事务所 |

## 法官信息
- 承办法官：Sarah Thompson法官
- 指派日期：2026-01-15
- 裁决模式：倾向支持原告（65%有利裁决）

## 进度追踪

### 里程碑完成度
| 阶段 | 完成度 | 状态 |
|------|--------|------|
| 诉答阶段 | 100% | ✅ 完成 |
| 证据开示 | 60% | 🟠 进行中 |
| 动议截止 | 30% | 🟡 进行中 |
| 审前会议 | 0% | 🔴 待处理 |
| 审判 | 0% | 🔴 待处理 |

### 关键日期
| 事件 | 日期 | 剩余天数 | 紧急程度 |
|------|------|---------|---------|
| 证据开示截止 | 2026-07-15 | 62天 | 🟠 高 |
| 答辩动议截止 | 2026-06-01 | 18天 | 🔴 紧急 |
| 审前会议 | 2026-09-15 | 124天 | 🟡 中 |

## 风险评估
- **暴露金额**：$50M - $100M
- **审判概率**：35%
- **预估持续时间**：18-24个月
- **和解区间**：$20M - $40M

## 预警提醒
### 🔴 紧急（本周）
- 答辩动议截止：2026-06-01（18天）

### 🟠 高优先级（本月）
- 证据开示完成节点：2026-06-15
- 专家证人报告截止：2026-06-30

## 建议行动
1. 立即准备答辩动议（法律部）
2. 完成剩余文件开示（证据团队）
3. 安排与外部律师策略会议（本周）
```

### 与天龙引擎协同

```yaml
天龙岗位协同:
  78-01 法律总顾问: trellis-mcp主调用者
  73-03 风控师: 案件风险数据消费者

数据流:
  trellis-mcp → 案件状态 → demand-intake
  trellis-mcp → 风险预警 → 73-03风控师
  trellis-mcp → 关键日期 → closing-checklist(合规义务)
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Trellis案件管理API |
