---
license: UNKNOWN
triggers: ["data privacy compliance skill", "17-08-data-privacy-compliance-skill"]
---
# 17-08-data-privacy-compliance-skill

## L0: 一句话描述

数据隐私合规技能包，涵盖GDPR/HIPAA/SOC2/CCPA合规审计、隐私影响评估(PIA)、数据血缘追踪、DSR请求自动化处理与Agent合规编排。

## L1: 使用场景

**适用场景**：新功能上线前的隐私合规审查、Agent数据血缘追踪、DSR请求处理、合规培训、合规审计应对。

**触发关键词**：`privacy`、`GDPR`、`HIPAA`、`合规`、`数据主体权利`、`PIA`、`隐私影响评估`、`数据分类`、`跨境传输`。

## L2: 详细文档

### 2.1 核心能力矩阵

| 能力 | 说明 | 命令 |
|------|------|------|
| **隐私影响评估 (PIA)** | 新功能/数据处理活动上线前的隐私风险评估 | `/privacy-impact-assessment` |
| **数据分类分级** | 自动识别并标记敏感数据（PII/PHI/财务数据） | `/classify-data` |
| **数据血缘追踪** | 追踪Agent决策链中的数据流向与处理节点 | `/data-lineage-trace` |
| **DSR请求处理** | 数据主体权利请求（Access/Deletion/Rectification）的自动化处理 | `/dsr-handle` |
| **合规审计准备** | 生成合规审计包（GDPR Article 30 Records、SOC 2证据） | `/compliance-audit-package` |
| **跨境传输评估** | 国际数据传输合规性评估（SCCs/BCR/Adequacy） | `/cross-border-assessment` |
| **Agent合规编排** | 在Agent工作流中嵌入合规门控（Privacy Gate） | `/agent-privacy-guard` |

### 2.2 合规检查工作流

```
┌─────────────────────────────────────────────────────────────┐
│              合规检查工作流 (Compliance Check Workflow)          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: 数据发现 (Data Discovery)                        │
│  └── 输入: 新功能/数据源                                   │
│      ├── 敏感数据扫描 (PII/PHI识别)                        │
│      ├── 数据流映射 (Data Flow Mapping)                      │
│      └── 数据主体识别 (Data Subject Identification)           │
│                                                             │
│  Phase 2: 隐私影响评估 (PIA)                              │
│  └── 评估维度:                                             │
│      ├── 数据处理的必要性与比例性                          │
│      ├── 数据主体权利影响                                  │
│      ├── 安全风险评估                                      │
│      └── 跨境传输影响                                      │
│                                                             │
│  Phase 3: 合规策略制定                                   │
│  └── 策略输出:                                             │
│      ├── 数据处理合法依据 (Legal Basis)                    │
│      ├── 技术和组织措施 (TOMs)                            │
│      ├── 数据保留期限 (Retention Period)                   │
│      └── 数据主体权利响应方案                              │
│                                                             │
│  Phase 4: 实施与监控                                     │
│  └── 实施项:                                              │
│      ├── Privacy by Design代码嵌入                         │
│      ├── 合规监控仪表板配置                               │
│      └── 定期合规审查计划                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 数据主体权利 (DSR) 自动化处理

```yaml
DSR类型与处理流程:
  Access (数据访问请求):
    - 识别请求者身份
    - 定位相关个人数据
    - 生成数据导出报告 (JSON/CSV/PDF)
    - 响应时效: 30天内 (GDPR)
    - 复杂度: ⭐⭐⭐

  Deletion (删除请求):
    - 验证删除条件 (GDPR Art.17)
    - 识别所有数据副本 (包括备份)
    - 执行遗忘机制 (Machine Unlearning)
    - 验证删除完成
    - 响应时效: 30天内
    - 复杂度: ⭐⭐⭐⭐⭐

  Rectification (修正请求):
    - 验证需要修正的数据
    - 执行数据修正
    - 通知所有接收方 (if disclosed)
    - 响应时效: 30天内
    - 复杂度: ⭐⭐⭐⭐

  Objection (拒绝处理请求):
    - 评估拒绝的法律依据
    - 提供拒绝理由说明
    - 提供投诉渠道
    - 响应时效: 30天内
    - 复杂度: ⭐⭐⭐

  Portability (数据可携带请求):
    - 导出结构化格式 (JSON/CSV)
    - 验证格式互操作性
    - 安全传输给请求者
    - 响应时效: 30天内
    - 复杂度: ⭐⭐⭐⭐
```

### 2.4 Agent隐私合规编排

```yaml
Agent隐私合规编排模板:
  适用场景: 新Agent能力上线前合规审查

  工作流步骤:
    1. data-inventory:
       - 识别该Agent处理的所有个人数据类别
       - 映射数据流: 输入 → 处理 → 输出 → 存储

    2. legal-basis:
       - 确定每个数据处理活动的合法依据
       - 评估同意有效性 (Consent Validity)
       - 记录Legitimate Interest评估 (if applicable)

    3. risk-assessment:
       - 评估隐私风险 (High/Medium/Low)
       - 识别风险缓解措施
       - 确定是否需要DPO consultation

    4. technical-controls:
       - 实施最小化原则 (Data Minimization)
       - 配置访问控制 (Need-to-Know)
       - 启用数据加密 (At-Rest + In-Transit)
       - 配置脱敏规则 (用于日志/输出)

    5. audit-trail:
       - 启用数据处理活动日志
       - 配置日志保留策略
       - 设置异常告警阈值

    6. documentation:
       - 生成Records of Processing Activities (GDPR Art.30)
       - 记录数据处理活动清单
       - 更新隐私声明 (Privacy Notice)

    7. monitoring:
       - 配置合规监控仪表板
       - 设置关键指标告警
       - 计划定期合规审查
```

### 2.5 合规工具链

```yaml
合规工具集成:
  数据发现与分类:
    - BigID: 个人数据自动发现与分类
    - OneTrust: 隐私管理平台 (PIA/DSR/Consent)
    - Vanta: SOC 2持续合规监控

  数据血缘追踪:
    - Privacidade: Agent数据血缘可视化
    - OpenLineage: 数据血缘开放标准
    - DataHub: 元数据管理与血缘

  合规自动化:
    - TrustArc: 隐私合规工作流自动化
    - Drata: 合规证据收集自动化
    - Secureframe: SOC 2/ISO 27001自动化

  DSR处理:
    - OneTrust DSR: 端到端DSR工作流
    - BigID DSR: 自动化数据搜索与删除
    -雷锋: 开源DSR管理工具
```

### 2.6 合规报告模板

#### GDPR Article 30 记录模板

```markdown
## 数据处理活动记录 (Records of Processing Activities)

### 基本信息
- **数据控制者**: [组织名称]
- **DPO联系方式**: [邮箱]
- **记录日期**: [YYYY-MM-DD]
- **最后更新**: [YYYY-MM-DD]

### 数据处理活动 #N: [活动名称]
| 字段 | 内容 |
|------|------|
| 处理目的 | [例如: 用户账户管理] |
| 合法依据 | [例如: Contract (Art.6(1)(b))] |
| 数据类别 | [例如: 姓名、邮箱、IP地址] |
| 数据主体类别 | [例如: 网站用户、员工] |
| 接收方类别 | [例如: AWS (云存储)、Stripe (支付)] |
| 第三国传输 | [是/否, 如是则说明保障措施] |
| 保留期限 | [例如: 账户删除后30天] |
| 安全措施 | [例如: AES-256加密、TLS 1.3] |
| 合规负责人 | [姓名/职位] |

### 数据主体权利
| 权利 | 是否支持 | 行使方式 |
|------|---------|---------|
| Access | [是/否] | [API/表单/邮箱] |
| Deletion | [是/否] | [API/表单/邮箱] |
| Rectification | [是/否] | [API/表单/邮箱] |
| Portability | [是/否] | [JSON导出] |
| Objection | [是/否] | [邮件申请] |
```

#### 隐私影响评估 (PIA) 报告模板

```markdown
## 隐私影响评估报告 (Privacy Impact Assessment)

### 1. 处理活动概述
- **项目名称**: [新功能/系统名称]
- **处理活动描述**: [详细描述数据处理活动]
- **上线日期**: [计划日期]
- **评估日期**: [YYYY-MM-DD]
- **评估人**: [姓名/职位]

### 2. 数据映射
```yaml
数据类别:
  - 姓名: 标识符
  - 邮箱: 联系信息
  - IP地址: 技术标识符
  - 行为数据: 使用记录

数据主体数量: [估计人数]
数据敏感性: [高/中/低]
```

### 3. 必要性评估
**处理是否必要**: [是/否]
**评估理由**: [详细说明为何该处理对服务是必要的]

### 4. 风险评估矩阵
| 风险 | 可能性 | 影响 | 风险等级 | 缓解措施 |
|------|--------|------|---------|---------|
| 未授权访问 | 低 | 高 | 中 | 加密+访问控制 |
| 数据泄露 | 低 | 高 | 中 | 安全措施+DPA |
| 过度采集 | 中 | 中 | 中 | 最小化审核 |
| 第三方风险 | 中 | 高 | 高 | DPA签署+SCCs |

### 5. DPO意见
**建议**: [批准/有条件批准/拒绝]
**条件/建议**: [详细说明]

### 6. 审批
| 角色 | 姓名 | 日期 | 签名 |
|------|------|------|------|
| 业务负责人 | | | |
| DPO | | | |
| CISO | | | |
```

### 2.7 合规命令速查

```bash
# 隐私影响评估
/privacy-impact-assessment "新Agent能力:用户行为分析" --scope full
/privacy-impact-assessment "功能更新:新增邮件通知" --scope quick

# 数据分类
/classify-data --source "database/production" --sensitivity high
/classify-data --scan-file ./data-export.csv

# 数据血缘追踪
/data-lineage-trace --agent "marketing-agent" --depth full
/data-lineage-trace --user-id "user-12345" --output json

# DSR请求处理
/dsr-handle --type access --requester "user@example.com"
/dsr-handle --type deletion --requester "user@example.com" --cascade
/dsr-handle --status --request-id DSR-2024-001

# 合规审计准备
/compliance-audit-package --framework "GDPR" --period "2024-Q1"
/compliance-audit-package --framework "SOC2" --evidence-type all

# 跨境传输评估
/cross-border-assessment --transfer "EU → US" --mechanism "SCCs"
/cross-border-assessment --transfer "CN → SG" --mechanism "Adequacy"

# Agent隐私合规编排
/agent-privacy-guard --agent "sales-agent" --mode review
/agent-privacy-guard --agent "data-processor" --mode enforce

# 合规培训
/compliance-training --role "engineer" --framework "GDPR"
/compliance-training --progress --department "engineering"

# 合规监控
/compliance-dashboard
/compliance-metrics --kpi all
/compliance-alert --threshold "breach_response_time>48h"
```

### 2.8 与天龙引擎协同

```yaml
天龙引擎协同:
  09-02编排协调师:
    - 在Agent编排流程中嵌入合规门控
    - 配置数据处理活动日志
    - 编排DSR自动化工作流

  05安全师:
    - 安全事件中的数据泄露评估
    - 协同制定泄露通知策略
    - 安全控制与隐私控制协同

  03构建师:
    - Privacy by Design代码审查
    - 数据脱敏实现检查
    - 安全编码实践培训

  08发布师:
    - 发布前合规检查门控
    - 合规发布清单验证
    - 合规发布文档准备

  07记录师:
    - 合规文档归档
    - 合规报告生成
    - 监管机构通信记录
```

### 2.9 ruflo合规增强

```yaml
ruflo合规增强功能:
  audit-trail:
    - Agent决策链全程审计日志
    - 不可篡改性保障 (Hash Chain)
    - 合规举证支持

  consent-management:
    - 细粒度同意管理 (Granular Consent)
    - 按数据用途分类同意
    - 同意撤回机制

  data-lineage:
    - 列级数据血缘追踪
    - Agent级数据溯源
    - 实时血缘图谱

  retention-policy:
    - 数据保留策略自动化执行
    - 自动过期提醒
    - 合规删除工作流

  breach-response:
    - 泄露事件自动检测
    - 72小时通知工作流
    - 监管机构报告模板
```

---

**Skill版本**: V1.0
**来源**: ruflo compliance audit trail + GDPR/HIPAA/SOC2合规框架
**创建日期**: 2026-05-08
**岗位**: 17-08 数据隐私合规工程师
**天龙引擎版本**: V11.08
