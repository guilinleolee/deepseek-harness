# issue-extraction - 问题提取与追踪管理

## L0: 一句话描述 (≤15字)
尽职调查问题提取与追踪管理

## L1: 使用场景 (50-100字)
并购法务工程师通过AI辅助从尽职调查材料中提取关键问题，按优先级分类管理，跟踪答复状态并生成问题追踪报告。适用于78-02投融资法务的问题清单管理和73-03风控师的风险追踪场景。

## L2: 详细文档

### 核心能力

1. **问题自动提取**
   - 从法律文件自动识别未解答问题
   - 从会议纪要提取待确认事项
   - 从问卷答复识别信息缺口

2. **优先级分类**
   - P0：交易阻断项（红）
   - P1：高优先级项（橙）
   - P2：一般关注项（黄）
   - P3：信息参考项（灰）

3. **状态追踪管理**
   - Open/In Progress/Answered/Closed状态
   - 答复期限预警
   - 责任人分配

4. **问题关联分析**
   - 问题→条款→风险关联
   - 跨文件问题聚合
   - 问题影响链可视化

### 优先级判定矩阵

| 问题类型 | 法律合规 | 交易结构 | 财务影响 | 战略价值 | 默认优先级 |
|----------|---------|---------|---------|---------|---------|
| 许可/执照缺失 | 高 | 阻断 | 中 | 高 | **P0** |
| 重大诉讼 | 高 | 阻断 | 高 | 中 | **P0** |
| 核心知识产权争议 | 高 | 中 | 高 | 高 | **P0** |
| 高管关键人依赖 | 中 | 中 | 高 | 高 | **P1** |
| 合同续期风险 | 中 | 低 | 中 | 中 | **P1** |
| 财务披露不完整 | 高 | 中 | 高 | 低 | **P1** |
| 劳动合规瑕疵 | 中 | 低 | 低 | 低 | **P2** |
| 关联交易 | 中 | 低 | 中 | 低 | **P2** |
| 环保合规记录 | 中 | 低 | 中 | 低 | **P2** |
| 历史信息参考 | 低 | 低 | 低 | 低 | **P3** |

### 输出格式

```yaml
issue_extraction:
  deal_id: string
  extraction_date: date
  source_documents: [string]

  issues:
    - issue_id: string
      priority: "P0|P1|P2|P3"
      category: string
      question: string
      source_reference: string
      responsible_party: string
      due_date: date
      status: "open|in_progress|answered|closed"
      risk_implication: string

  tracking:
    total_issues: number
    p0_open: number
    p1_open: number
    p2_open: number
    p3_open: number
    answered_count: number
    closed_count: number

  recommendations:
    - action: string
      priority_justification: string
```

### 使用命令

```bash
# 从文档提取问题
/issue-extraction extract --deal-id "MA-001" --source ./materials/legal/ --output ./issues/

# 提取特定类别问题
/issue-extraction extract --deal-id "MA-001" --category IP --output ./issues/ip-issues.yaml

# 添加/更新问题
/issue-extraction add --deal-id "MA-001" --issue "核心专利归属存疑" --priority P0 --responsible "卖方法务"

# 查看问题状态
/issue-extraction status --deal-id "MA-001" --format table

# 生成问题追踪报告
/issue-extraction report --deal-id "MA-001" --format markdown --output ./issues/report.md

# 期限预警
/issue-extraction alerts --deal-id "MA-001" --days 7
```

### 问题追踪报告模板

```markdown
# 尽职调查问题追踪报告

## 项目概览
- 项目编号：MA-001
- 报告日期：2024-XX-XX
- 问题总数：45项
- 开放问题：12项

---

## P0交易阻断项（需立即处理）

| # | 问题 | 来源 | 责任人 | 期限 | 状态 |
|---|------|------|--------|------|------|
| 1 | 3项核心专利证书缺失 | DDQ-附件C | 卖方法务 | 3天 | 🔴 Open |
| 2 | 环评批复存在瑕疵 | 环境问卷 | 卖方EHS | 5天 | 🔴 Open |
| 3 | 1起未决劳动仲裁 | 法律问卷 | 卖方法务 | 7天 | 🔴 Open |

---

## P1高优先级项

| # | 问题 | 来源 | 责任人 | 期限 | 状态 |
|---|------|------|--------|------|------|
| 1 | 高管劳动合同竞业条款 | 劳动问卷 | 卖方HR | 10天 | 🟠 In Progress |
| 2 | 关联交易披露不完整 | 财务问卷 | 卖方财务 | 14天 | 🟠 In Progress |
| 3 | 客户集中度超预期 | 财务问卷 | 卖方IR | 14天 | 🟠 Open |

---

## 答复状态统计

| 状态 | 数量 | 占比 |
|------|------|------|
| 🔴 Open | 5 | 11% |
| 🟠 In Progress | 7 | 16% |
| ✅ Answered | 28 | 62% |
| ✅ Closed | 5 | 11% |

---

## 建议行动

### 立即处理（本周）
1. 要求卖方补充3项专利证书原件
2. 就环评瑕疵获取律师意见

### 尽快确认（下周）
3. 高管稳定性承诺函签署
4. 关联交易完整披露
```

### 与天龙引擎协同

```yaml
天龙岗位协同:
  78-02 投融资法务: issue-extraction主调用者
  73-03 风控师: 问题追踪数据消费者

数据流:
  tabular-review → 问题清单 → issue-extraction
  issue-extraction → 追踪报告 → 路由至78-02/73-03
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal issue-extraction |
