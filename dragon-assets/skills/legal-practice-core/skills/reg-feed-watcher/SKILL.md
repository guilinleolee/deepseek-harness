# reg-feed-watcher - 监管动态监控

## L0: 一句话描述 (≤15字)
监管动态实时追踪分析

## L1: 使用场景 (50-100字)
实时监控监管动态源（NPRM/Final Rule/监管指南），追踪政策变化，识别合规缺口，生成监管影响评估报告。适用于73-02合规师V11.0和73-04法律合规工程师的持续监管合规场景。

## L2: 详细文档

### 核心能力

1. **NPRM追踪**
   - 联邦注册公告扫描
   - 评论期倒计时
   - 行业影响评估

2. **Final Rule监控**
   - 生效日期追踪
   - 合规要求提取
   - 过渡期识别

3. **政策差异分析**
   - 新规vs现行政策对比
   - 差距量化评分
   - 修复优先级排序

4. **监管缺口评分**
   - 影响范围（组织级别/行业级别）
   - 紧迫程度（生效日期/评论截止）
   - 实施难度（技术/流程/培训）

### 监管源矩阵

| 监管机构 | 追踪范围 | 更新频率 |
|----------|---------|---------|
| **SEC** | 证券法规/披露要求 | 实时 |
| **CFTC** | 大宗商品/衍生品 | 实时 |
| **FinCEN** | 反洗钱/KYC | 每日 |
| **FRB/OCC** | 银行监管 | 每周 |
| ** FTC** | 消费者保护/竞争 | 实时 |
| **EU/UK Regulators** | GDPR/DORA/MiFID | 实时 |

### 差距分析输出格式

```yaml
regulatory_gap_analysis:
  regulation:
    name: string
    agency: string
    effective_date: date
    citation: string
  gap_assessment:
    current_compliance: "full|partial|non"
    gaps: [{ requirement: string, current_state: string, remediation: string }]
    impact_score: 1-10
    urgency_score: 1-10
    effort_score: 1-10
  recommendations:
    priority: "critical|high|medium|low"
    actions: [string]
    timeline: string
    owner: string
```

### 使用命令

```bash
# 全面监管扫描
/reg-feed-watcher scan --scope all

# 特定机构追踪
/reg-feed-watcher track --agency SEC --topics securities_disclosure

# 差距分析报告
/reg-feed-watcher gap-analysis --regulation Dodd-Frank

# 政策红皮书生成
/reg-feed-watcher policy-redbook --output ./reports/policy-redbook.md
```

### 与MCP连接器协同

```yaml
MCP连接器:
  courtlistener-mcp: 判例法追踪
  trellis-mcp: 法院规则监控

数据流:
  reg-feed-watcher → courtlistener-mcp → 监管判例关联分析
  reg-feed-watcher → trellis-mcp → 法院程序变更追踪
```

### 与73-02合规师V11.0协同

```yaml
Agent: 73-02 合规师 V11.0
Role: reg-feed-watcher主消费者
Flow:
  1. reg-feed-watcher发现监管变化 → 触发73-02分析
  2. 73-02执行差距分析 → 生成compliance-gap-report
  3. 报告 → 自动路由至相关Stakeholders
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal reg-monitor |