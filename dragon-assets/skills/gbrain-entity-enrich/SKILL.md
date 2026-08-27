---
license: UNKNOWN
triggers: ["gbrain entity enrich", "GBrain Entity Enrich"]
---
# GBrain Entity Enrich
# 实体充实引擎 — 层级实体画像 + 7步协议

## L0: 一句话描述
三层实体充实协议（全员/公司/事件），确保每个实体都有完整的画像页面和双向链接。

## L1: 使用场景

### 核心触发场景
- **新实体发现**: 当对话中出现新的关键人物或公司时
- **实体画像更新**: 当实体有新动态需要更新时
- **关系建立**: 当需要建立实体间的关系时
- **批量充实**: 当需要系统性地充实某个领域的实体时

### 天龙九部适用
- **01调研师**: 研究中发现的实体需要及时充实
- **07记录师**: 归档时确保实体关系完整
- **09-02编排协调师**: 编排任务时确保关联实体信息完整

## L2: 详细文档

### 核心能力

GBrain Entity Enrich 实现**层级充实协议**：

```
┌─────────────────────────────────────────────────────────────┐
│           GBrain Entity Enrich 层级充实架构                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Tier 1: 核心圈层 (Inner Circle)                           │
│  ├── 适用: 核心决策者、主要协作者、直接相关方              │
│  ├── 充实深度: 完整 (所有API + 深度调研)                  │
│  ├── API调用: Perplexity + LinkedIn + Twitter              │
│  └── 更新频率: 每次新信息时                                 │
│                                                             │
│  Tier 2: 中间层 (Middle Ring)                             │
│  ├── 适用: 偶尔提及、间接关联                               │
│  ├── 充实深度: 中等 (网页 + 社媒概览)                    │
│  ├── API调用: Web Search + Twitter摘要                      │
│  └── 更新频率: 每周检查一次                                 │
│                                                             │
│  Tier 3: 外围层 (Outer Ring)                              │
│  ├── 适用: 一次提及、背景信息                               │
│  ├── 充实深度: 最小 (仅脑内交叉引用)                       │
│  ├── API调用: 无外部调用                                   │
│  └── 更新频率: 仅在被查询时                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7步充实协议

```yaml
Step 1: 实体识别
  - 从对话/文档中提取所有实体
  - 分类: person | company | event | concept
  - 去重: 检查是否已存在于知识库

Step 2: 层级判定
  - 检查实体是否为核心圈 (inner circle)
  - 判定依据: 直接提及频率、最近活跃度、业务相关性

Step 3: 脑内检查
  - 检索现有页面: get_page(entity_slug)
  - 检查已有信息完整度
  - 确定需要补充的信息点

Step 4: 外部查询
  - Tier 1: Perplexity深度调研 + LinkedIn + Twitter
  - Tier 2: Web Search概览 + Twitter摘要
  - Tier 3: 跳过外部查询

Step 5: 原始数据保存
  - 保存原始API响应到: raw/enrich/{date}/{slug}.json
  - 保留溯源能力
  - Token预算: 原始数据 < 压缩后知识 < 引用

Step 6: 知识写入
  - 按模板格式写入实体页面
  - 包含来源标注: [Source: url]
  - 更新最后修改时间

Step 7: 交叉引用
  - 检查相关实体是否需要更新backlinks
  - 建立双向关系: Entity A ↔ Entity B
  - 触发链接铁律检查
```

### 人物页面模板

```markdown
# {name}

## 状态
[当前职位] @ [当前公司] | 更新于 {date}

## 他们相信什么
[核心信念、观点、方法论]

## 他们在做什么
[当前项目、关注领域]

## 什么激励他们
[动机、目标、驱动力]

## 评估
[对该人物的综合评价，与我们的关系]

## 轨迹
- {date}: [事件描述]
- {date}: [事件描述]

## 关系
- [关联实体]: [关系描述]

## 联系信息 (如适用)
[邮件/社交账号，仅Tier 1且获得授权时]

## 网络
- 同事: [list]
- 合作者: [list]
- 关注: [list]
```

### 公司页面模板

```markdown
# {company_name}

## 状态
[一句话定位] | 更新于 {date}

## 开放线程
[正在进行的项目、关注的问题]

## 轨迹
- {date}: [事件描述]
- {date}: [事件描述]

## 关联实体
- 创始人: [person_slug]
- 投资方: [list]
- 合作伙伴: [list]
```

### 批量充实规则

```yaml
bulk_enrichment:
  # 先小批量测试
  test_batch_size: 3-5
  throttle_api_calls: true
  delay_between_calls: 2s

  # 批量处理
  batch_size: 20
  checkpoint_interval: 10    # 每10个保存一次checkpoint

  # 错误处理
  retry_attempts: 3
  fallback_to_minimal: true  # API失败时降级到Tier 3
```

### CLI 命令

```bash
# 创建/更新人物页面
python ~/.claude/skills/gbrain-entity-enrich/scripts/entity_enricher.py person "Sarah Chen" --tier 1
python ~/.claude/skills/gbrain-entity-enrich/scripts/entity_enricher.py person "John Doe" --source linkedin --source twitter

# 创建/更新公司页面
python ~/.claude/skills/gbrain-entity-enrich/scripts/entity_enricher.py company "OpenAI" --tier 1
python ~/.claude/skills/gbrain-entity-enrich/scripts/entity_enricher.py company "Anthropic" --source perplexity

# 批量充实
python ~/.claude/skills/gbrain-entity-enrich/scripts/entity_enricher.py bulk --input entities.csv --tier 2

# 检查实体状态
python ~/.claude/skills/gbrain-entity-enrich/scripts/entity_enricher.py status --entity "person/sarah-chen"
python ~/.claude/skills/gbrain-entity-enrich/scripts/entity_enricher.py status --stale --older-than 30d

# 关系建立
python ~/.claude/skills/gbrain-entity-enrich/scripts/entity_enricher.py link "person/sarah-chen" --to "company/acme" --relation "co-founder"

# 交叉引用检查
python ~/.claude/skills/gbrain-entity-enrich/scripts/entity_enricher.py cross-ref --entity "person/sarah-chen"
```

### 链接铁律

任何在brain中提及有页面的人物/公司，**必须**创建双向backlink：

```markdown
<!-- 在 person/sarah-chen.md 中 -->
## 关系
- [公司/实体]: [关系描述]

<!-- 同时在 company/acme.md 中 -->
## 关联实体
- Sarah Chen (person/sarah-chen): co-founder
```

违反链接铁律将触发警告。

## 与天龙引擎协同

### 天龙引擎集成配置

```yaml
# gbrain-entity-enrich/config.yaml

enrichment:
  tiers:
    tier1:
      name: "Inner Circle"
      criteria: "direct_mention OR recent_active OR business_critical"
      api_calls: ["perplexity", "linkedin", "twitter"]
      update_frequency: "on_new_info"
    tier2:
      name: "Middle Ring"
      criteria: "occasional_mention OR indirect_relation"
      api_calls: ["web_search", "twitter_summary"]
      update_frequency: "weekly"
    tier3:
      name: "Outer Ring"
      criteria: "single_mention OR background_info"
      api_calls: []
      update_frequency: "on_demand"

  templates:
    person: "prompts/person_template.md"
    company: "prompts/company_template.md"
    event: "prompts/event_template.md"

  bulk_rules:
    test_batch: 5
    batch_size: 20
    checkpoint_interval: 10
    throttle_delay: 2s
    retry_attempts: 3
    fallback_to_minimal: true

# 天龙引擎集成
tianlong_integration:
  attached_role: "01-investigator"
  triggers:
    - "enrich"
    - "create person page"
    - "who is this person"
    - "look up this company"
    - "充实"
    - "人物画像"
    - "公司信息"
  upstream:
    - gbrain-hybrid-search
    - gbrain-multimodal-ingest
  downstream:
    - gbrain-hybrid-search     # 充实后可供检索
    - gbrain-daily-briefing    # 充实结果进入简报
  iron_law:
    enforced: true
    violation_warning: true
    auto_link_on_write: true
```

### 组织架构映射

| 天龙 Agent | 协同方式 | 协同内容 |
|-----------|---------|---------|
| 01调研师 | 上游触发 | 研究中发现新实体时自动充实 |
| 07记录师 | 执行者 | 按模板创建/更新实体页面 |
| 09-02编排协调师 | 编排辅助 | 批量充实任务编排 |

## 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| 实体画像完整度 | 碎片化 | 体系化 | +300% |
| 关系网络覆盖率 | 无 | 100%链接 | 质的飞跃 |
| API调用效率 | 无优化 | 节流+批处理 | +60% |
| 实体召回准确率 | 无分层 | 层级优化 | +200% |

## 技能文件

- [SKILL.md](SKILL.md) - 本文件
- [config.yaml](config.yaml) - 配置文件
- [scripts/entity_enricher.py](scripts/entity_enricher.py) - 充实CLI
- [prompts/person_template.md](prompts/person_template.md) - 人物模板
- [prompts/company_template.md](prompts/company_template.md) - 公司模板
