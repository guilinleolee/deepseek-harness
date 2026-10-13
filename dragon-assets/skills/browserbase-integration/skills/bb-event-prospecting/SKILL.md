# Browserbase Event Prospecting

## L0: 一句话描述 (≤15字)
会议演讲嘉宾线索发现

## L1: 使用场景 (50-100字)
适用于发现行业会议演讲嘉宾、建立KOL关系、挖掘销售机会。当需要找到目标客户的决策者、获取高质量销售线索时，使用Event Prospecting。自动发现会议演讲嘉宾、公司高管、行业KOL，生成可操作的联系信息和社会关系图谱。

## L2: 详细文档

### 来源项目
| 项目 | Stars | 核心能力 |
|------|-------|---------|
| [browserbase/skills](https://github.com/browserbase/skills) | 2,557 | Event Prospecting + KOL发现 + 关系图谱 |

### 核心能力矩阵

| 能力 | 说明 | 天龙现有能力 |
|------|------|------------|
| **会议发现** | 行业会议自动发现和追踪 | ❌ 无等价 |
| **嘉宾提取** | 演讲嘉宾信息自动提取 | ❌ 无等价 |
| **KOL图谱** | 演讲者关系网络构建 | ❌ 无等价 |
| **联系发现** | LinkedIn/Twitter联系信息 | ❌ 无等价 |

### 会议发现参数

```javascript
const EVENT_SOURCES = {
  // 国际会议
  major_conferences: [
    { name: 'SaaStr Annual', sector: 'SaaS', frequency: 'Annual' },
    { name: 'Dreamforce', sector: 'Cloud/SaaS', frequency: 'Annual' },
    { name: 'Web Summit', sector: 'Tech', frequency: 'Annual' },
    { name: 'Collision', sector: 'Tech', frequency: 'Annual' }
  ],
  // 追踪关键词
  track_keywords: [
    'founder', 'ceo', 'cto', 'vp engineering',
    'head of product', 'director of sales'
  ],
  // 优先行业
  priority_sectors: [
    'SaaS', 'Fintech', 'E-commerce', 'AI/ML',
    'Cybersecurity', 'Cloud Infrastructure'
  ]
};
```

### CLI命令

```bash
# 发现行业会议嘉宾
bash ~/.claude/skills/browserbase-integration/scripts/bb-event-prospect.sh "AI Agent"

# 追踪特定会议
bash ~/.claude/skills/browserbase-integration/scripts/bb-event-prospect.sh \
  --event "SaaStr 2026" --track-speakers

# 生成KOL图谱
bash ~/.claude/skills/browserbase-integration/scripts/bb-event-prospect.sh \
  --kol-network "Fintech" --output kol_graph.json

# 批量联系发现
bash ~/.claude/skills/browserbase-integration/scripts/bb-event-prospect.sh \
  --input speakers.csv --find-contacts --output outreach.csv
```

### 与现有能力协同

```bash
# 会议销售链路
bb-event-prospecting 会议嘉宾发现
    ↓
bb-company-research 公司背景调研
    ↓
38-02销售管理 销售跟进
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **38-02销售管理** | V2.1 → V2.2 | 会议嘉宾发现 + KOL图谱 + 联系发现 |
| **32-01市场研究** | V10.1 → V10.2 | 行业KOL追踪 + 会议情报 |

### 版本

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-07 | 初始集成，基于browserbase/skills |
