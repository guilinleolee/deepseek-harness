# integration-runbook - 整合阶段运行手册

## L0: 一句话描述 (≤15字)
并购后整合阶段运行手册生成

## L1: 使用场景 (50-100字)
并购法务工程师通过AI辅助生成并购后整合阶段（Post-Merger Integration）运行手册，包括整合计划模板、里程碑跟踪、风险清单和合规检查。适用于78-02投融资法务的整合阶段管理和73-02合规师的持续合规监控场景。

## L2: 详细文档

### 核心能力

1. **整合计划生成**
   - Day 1整合行动计划
   - 100天整合计划模板
   - 年度整合路线图

2. **里程碑管理**
   - 关键整合里程碑设置
   - 完成进度跟踪
   - 延期预警

3. **风险清单维护**
   - 整合期特有风险识别
   - 风险应对措施跟踪
   - 风险责任人分配

4. **合规持续监控**
   - 交割后合规条件检查
   - 监管报告义务提醒
   - 合规培训计划

### 整合阶段划分

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Day 1 整合 (交割日)                               │
│   - 交易关闭确认                                          │
│   - 管理层沟通                                            │
│   - 基础系统切换                                          │
│   - 员工沟通                                              │
├─────────────────────────────────────────────────────────────┤
│ Phase 2: 短期整合 (Day 1-100)                             │
│   - 业务运营整合                                          │
│   - 财务整合                                              │
│   - IT系统整合                                            │
│   - 人力资源整合                                          │
├─────────────────────────────────────────────────────────────┤
│ Phase 3: 中期整合 (100天-1年)                             │
│   - 深度业务整合                                          │
│   - 企业文化融合                                          │
│   - 运营效率优化                                          │
├─────────────────────────────────────────────────────────────┤
│ Phase 4: 长期整合 (1年+)                                   │
│   - 战略协同实现                                          │
│   - 品牌整合                                              │
│   - 组织优化                                              │
└─────────────────────────────────────────────────────────────┘
```

### 整合维度矩阵

| 整合维度 | Day 1 | 100天 | 1年 | 责任人 |
|----------|-------|-------|------|--------|
| **法律实体** | 股权变更登记 | 注销/合并 | - | 法务 |
| **许可证/资质** | 主体变更申请 | 完成变更 | - | 合规 |
| **合同** | 合同审查 | 关键合同重谈 | - | 法务 |
| **知识产权** | IP转让登记 | 商标变更 | - | IP团队 |
| **劳动关系** | 员工沟通 | 福利整合 | 薪酬统一 | HR |
| **合规义务** | 报告义务梳理 | 持续合规 | - | 合规 |
| **数据保护** | GDPR/个保法审查 | 政策整合 | - | DPO |

### 输出格式

```yaml
integration_runbook:
  deal_id: string
  closing_date: date
  integration_type: "full|partial| JV"

  phases:
    - phase: "day1|short|medium|long"
      start_date: date
      end_date: date
      milestones:
        - milestone_id: string
          description: string
          due_date: date
          status: "pending|in_progress|completed|blocked"
          responsible_party: string
          evidence_reference: string

  risk_register:
    - risk_id: string
      risk_description: string
      likelihood: "high|medium|low"
      impact: "high|medium|low"
      mitigation: string
      owner: string
      status: "open|mitigated|realized"

  compliance_checklist:
    - item_id: string
      obligation: string
      regulatory_body: string
      report_frequency: "monthly|quarterly|annually"
      next_due_date: date
      status: "compliant|pending|breach"

  recommendations:
    - area: string
      action: string
      priority: "critical|high|medium"
```

### 使用命令

```bash
# 生成整合运行手册
/integration-runbook generate --deal-id "MA-001" --closing-date "2024-06-01" --output ./integration/runbook.yaml

# 生成100天整合计划
/integration-runbook 100day --deal-id "MA-001" --output ./integration/100day-plan.md

# 添加/更新里程碑
/integration-runbook milestone --deal-id "MA-001" --add --phase day1 --milestone "完成股权变更登记" --due "2024-06-15"

# 更新风险状态
/integration-runbook risk --deal-id "MA-001" --risk "R-001" --status mitigated --evidence ./evidence/remediation.pdf

# 合规检查提醒
/integration-runbook compliance --deal-id "MA-001" --format table

# 生成整合进度报告
/integration-runbook report --deal-id "MA-001" --format markdown --output ./integration/report.md
```

### 整合运行手册模板

```markdown
# 并购后整合运行手册

## 基本信息
- 项目编号：MA-001
- 交割日期：2024-06-01
- 整合类型：全资收购
- 整合负责人：[姓名]
- Long Stop Date：2024-06-30

---

## Day 1 整合行动计划

### 法律与合规（Day 1）
| 任务 | 负责人 | 完成时间 | 状态 |
|------|--------|---------|------|
| 确认交割条件全部满足 | 法务 | 09:00 | ✅ |
| 股权变更登记申请 | 法务 | 10:00 | ✅ |
| 工商变更登记 | 法务 | 14:00 | 🟠 In Progress |
| 银行账户变更 | 财务 | 14:00 | 🟠 In Progress |

### 员工沟通（Day 1）
| 任务 | 负责人 | 完成时间 | 状态 |
|------|--------|---------|------|
| 全员邮件通知 | HR | 09:30 | ✅ |
| 管理层会议 | HR+法务 | 10:30 | ✅ |
| 员工问答会（上午场） | HR | 11:00 | ✅ |
| 员工问答会（下午场） | HR | 15:00 | 🔴 Pending |

---

## 100天整合计划

### Phase 1: 基础设施整合（Day 1-30）

| 里程碑 | 目标日期 | 状态 | 负责人 |
|--------|---------|------|--------|
| 完成工商变更登记 | Day 7 | 🟠 65% | 法务 |
| 完成银行账户变更 | Day 7 | 🟠 80% | 财务 |
| IT系统访问权限配置 | Day 14 | 🟠 50% | IT |
| HR系统合并 | Day 30 | 🔴 20% | HR |

### Phase 2: 业务运营整合（Day 30-60）

| 里程碑 | 目标日期 | 状态 | 负责人 |
|--------|---------|------|--------|
| 销售团队整合 | Day 45 | 🔴 10% | 运营 |
| 供应链整合 | Day 60 | 🔴 5% | 运营 |
| 财务系统切换 | Day 60 | 🟠 30% | 财务 |

### Phase 3: 深度整合（Day 60-100）

| 里程碑 | 目标日期 | 状态 | 负责人 |
|--------|---------|------|--------|
| 企业文化融合启动 | Day 75 | 🔴 Pending | HR |
| KPI体系统一 | Day 90 | 🔴 Pending | 运营 |
| 整合后首次董事会 | Day 100 | 🔴 Pending | 董秘 |

---

## 风险登记册

| 风险ID | 风险描述 | 可能性 | 影响 | 应对措施 | 责任人 | 状态 |
|--------|---------|-------|------|---------|--------|------|
| R-001 | 关键员工离职 | 高 | 高 | 挽留计划+股权激励 | HR总监 | 🟠 Mitigation |
| R-002 | 客户流失 | 高 | 高 | 客户沟通计划 | 销售VP | 🟠 Mitigation |
| R-003 | IT系统整合延迟 | 中 | 中 | 备选方案准备 | CTO | 🔴 Open |
| R-004 | 供应商合同重谈失败 | 中 | 中 | 合同条款审查 | 采购总监 | 🔴 Open |

---

## 合规义务清单

| 义务编号 | 合规义务 | 监管机构 | 报告频率 | 下次截止 | 状态 |
|----------|---------|---------|---------|---------|------|
| C-001 | 外商投资年报 | 商务部 | 年度 | 2025-03-31 | ✅ Compliant |
| C-002 | 税务申报变更 | 税务局 | 月度 | 2024-07-15 | 🟠 Pending |
| C-003 | 社保合并申报 | 人社局 | 月度 | 2024-07-05 | 🔴 Pending |
| C-004 | 数据安全评估 | 网信办 | 年度 | 2024-12-31 | ✅ Compliant |

---

## 建议行动

### 本周优先事项
1. 完成工商变更登记（法务）
2. 启动关键员工挽留计划（HR）
3. 确认客户沟通策略（销售）

### 下周待办
4. IT系统访问权限全面配置（IT）
5. HR系统合并方案确定（HR）
6. 供应商合同审查启动（法务）

### 月度审查
7. 100天整合进度第一次审查
8. 风险登记册更新
9. 合规义务检查
```

### 与天龙引擎协同

```yaml
天龙岗位协同:
  78-02 投融资法务: integration-runbook主调用者
  73-02 合规师: 合规义务监控数据消费者

数据流:
  closing-checklist → 交割确认 → integration-runbook
  integration-runbook → 整合报告 → 路由至78-02/73-02
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal integration-runbook |
