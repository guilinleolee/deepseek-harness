# Browserbase Company Research

## L0: 一句话描述 (≤15字)
B2B调研ICP评分自动化

## L1: 使用场景 (50-100字)
适用于B2B销售线索挖掘、ICP(理想客户画像)评分、竞品客户定位。当需要批量发现目标客户、评估客户质量时，使用Browserbase Company Research。自动抓取公司信息、评估规模/收入/行业匹配度，生成优先级排序的客户列表。

## L2: 详细文档

### 来源项目
| 项目 | Stars | 核心能力 |
|------|-------|---------|
| [browserbase/skills](https://github.com/browserbase/skills) | 2,557 | Company Research + ICP评分 + 事件线索 |

### 核心能力矩阵

| 能力 | 说明 | 天龙现有能力 |
|------|------|------------|
| **ICP评分** | 规模/收入/行业/融资多维度评分 | ❌ 无等价 |
| **批量发现** | 自动发现目标公司 | ❌ 无等价 |
| **事件触发** | 融资/扩张/招聘触发销售机会 | ❌ 无等价 |
| **CRM导出** | Salesforce/HubSpot格式导出 | ❌ 无等价 |

### ICP评分模型

```javascript
const ICP_WEIGHTS = {
  // 基础分 (0-100)
  employee_count: { weight: 0.3, ranges: [
    { min: 50, max: 200, score: 60 },    // SMB
    { min: 201, max: 1000, score: 85 }, // Mid-Market
    { min: 1001, max: Infinity, score: 100 } // Enterprise
  ]},
  // 收入 (美元)
  revenue: { weight: 0.25, ranges: [
    { min: 1000000, max: 10000000, score: 60 },   // $1M-$10M
    { min: 10000001, max: 100000000, score: 85 }, // $10M-$100M
    { min: 100000001, max: Infinity, score: 100 } // $100M+
  ]},
  // 行业匹配
  industry: { weight: 0.2, targets: [
    'Software', 'Technology', 'SaaS', 'Fintech', 'E-commerce'
  ]},
  // 融资阶段
  funding_stage: { weight: 0.15, preferred: ['Series A', 'Series B', 'Series C'] },
  // 技术栈 (使用竞品=低分)
  tech_stack: { weight: 0.1, competitors: ['Salesforce', 'HubSpot'] }
};

// 综合评分
final_score = base_score × (Σ weight × score) / 100
```

### CLI命令

```bash
# 基础公司调研
bash ~/.claude/skills/browserbase-integration/scripts/bb-company-research.sh "目标公司关键词"

# ICP筛选
bash ~/.claude/skills/browserbase-integration/scripts/bb-company-research.sh "AI startup" \
  --icp "employees:50+,revenue:10M+,country:USA,funding:Series A"

# 批量评分
bash ~/.claude/skills/browserbase-integration/scripts/bb-company-research.sh \
  --input companies.csv --output scored_leads.csv

# CRM导出
bash ~/.claude/skills/browserbase-integration/scripts/bb-company-research.sh \
  --export salesforce --input scored_leads.csv
```

### 与现有能力协同

```bash
# B2B调研链路
bb-company-research ICP评分筛选
    ↓
bb-event-prospecting 会议嘉宾发现
    ↓
38-02销售管理 线索跟进
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **38-02销售管理** | V2.0 → V2.1 | ICP评分 + 批量发现 + CRM导出 |

### 版本

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-07 | 初始集成，基于browserbase/skills |
