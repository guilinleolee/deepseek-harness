---
license: UNKNOWN
triggers: ["gbrain external api lookup", "GBrain External API Lookup"]
---
# GBrain External API Lookup
# 外部API查询 — Brain优先原则 + READ→ENRICH→WRITE循环

## L0: 一句话描述
Brain优先查询约定：任何外部API调用前必须先检查Brain，确保知识内化而非重复查询。

## L1: 使用场景

### 核心触发场景
- **API调用前检查**: 任何外部API调用前先查Brain
- **信息吸收**: 对话中提及新信息时吸收到Brain
- **背景知识补充**: 回答前补充相关背景
- **被动充实**: 不打断对话的后台充实

### 天龙九部适用
- **01调研师**: 调研前先检查Brain已有知识
- **00分析师**: 决策前补充相关背景
- **07记录师**: 持续监听并吸收知识
- **09-02编排协调师**: 编排时确保上下文完整

## L2: 详细文档

### 核心能力

GBrain External API Lookup 实现**Brain优先约定**：

```
┌─────────────────────────────────────────────────────────────┐
│           GBrain External API Lookup 架构                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🔍 Brain-First Lookup (铁律)                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 外部API调用前:                                       │   │
│  │ 1. 查Brain是否有相关信息                            │   │
│  │ 2. 确认信息是否足够新鲜 (< 7天)                    │   │
│  │ 3. 如需更新，再调用外部API                          │   │
│  │ 4. 调用后必须写回Brain                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  📝 READ → ENRICH → WRITE 循环                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 每次信息进入时:                                     │   │
│  │ READ:   读取相关现有Brain页面                       │   │
│  │ ENRICH: 整合新旧信息                                │   │
│  │ WRITE:  写回Brain (带来源标注)                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  🔄 Ambient Enrichment (被动充实)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 原则: 不打断对话，不阻塞响应                         │   │
│  │ 方式: 后台子Agent异步充实                           │   │
│  │ 时机: 对话结束后自动触发                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Brain-First Lookup 流程

```yaml
brain_first_lookup:
  step_1: "查询Brain"
    action: "hybrid_search(entity_or_topic)"
    threshold: 0.6

  step_2: "新鲜度检查"
    action: "check_timestamp(page.updated_at)"
    threshold: "7d"  # 超过7天需要刷新

  step_3: "决策"
    branch:
      - condition: "brain_has_sufficient_info"
        action: "USE_BRAIN"
      - condition: "stale_but_has_base"
        action: "USE_BRAIN_THEN_REFRESH_ASYNC"
      - condition: "no_info OR need_deep_research"
        action: "CALL_EXTERNAL_API"

  step_4: "外部API调用 (如需要)"
    action: "perplexity_search OR web_search OR linkedin_lookup"

  step_5: "写回Brain"
    action: "put_page() with [Source: api_name]"
    sync: "immediately"  # 同步写回

  step_6: "交叉引用"
    action: "add_backlinks()"
```

### READ→ENRICH→WRITE 循环

```markdown
## 输入信号示例

用户: "我想了解关于OpenAI最新发布模型的信息"

## READ 阶段
- 查询Brain: "OpenAI"
- 发现: memory/companies/openai 有页面
- 更新时间: 2026-04-10 (8天前，陈旧)

## ENRICH 阶段
- 当前信息: GPT-4发布于2026-03
- 用户需求: 最新发布模型
- 差距: 需要获取2026-04信息

## WRITE 阶段
- 调用外部API获取最新信息
- 整合到现有页面
- 保存带来源标注: [Source: perplexity.ai, 2026-04-18]
- 更新时间戳

## 交叉引用
- 检查: 谁提到了OpenAI?
- 更新: 相关实体的backlinks
```

### Ambient Enrichment (被动充实)

```yaml
ambient_enrichment:
  # 不打断对话
  interrupt_threshold: 0  # 永远不阻塞

  # 后台子Agent
  spawn_subagent: true
  subagent_priority: "low"
  subagent_timeout: "5min"

  # 触发条件
  triggers:
    - "new_person_mentioned"
    - "new_company_mentioned"
    - "stale_entity (>7d)"
    - "new_technology_discussed"

  # 行为模式
  behavior:
    log_to_console: false    # 不打印到控制台
    notify_on_complete: false # 不通知用户
    persist_results: true    # 持久化结果

  # 异步循环
  async_loop:
    enabled: true
    post_conversation: true   # 对话结束后执行
    batch_size: 3            # 每次最多3个实体
    delay_between: 30s         # 实体间延迟
```

### 来源优先级铁律

```yaml
source_precedence:
  # 优先级从高到低
  priority_1: "user_direct"           # 用户直接陈述
  priority_2: "compiled_truth"         # 编译后的真相(会议记录)
  priority_3: "timeline_events"       # 时间线事件
  priority_4: "external_sources"       # 外部来源

  # 冲突处理
  conflict_resolution:
    newer_wins: true
    user_over_external: true
    external_requires_citation: true

  # 引用标注格式
  citation_format: "[Source: {name}, {url}, {date}]"
```

### CLI 命令

```bash
# Brain-First 查询
python ~/.claude/skills/gbrain-external-api-lookup/scripts/api_lookup.py brain-first "OpenAI最新模型"
python ~/.claude/skills/gbrain-external-api-lookup/scripts/api_lookup.py brain-first "Sarah Chen背景" --freshness-check 7d

# 直接外部查询 (不推荐，应通过brain-first)
python ~/.claude/skills/gbrain-external-api-lookup/scripts/api_lookup.py external "OpenAI" --api perplexity
python ~/.claude/skills/gbrain-external-api-lookup/scripts/api_lookup.py external "技术趋势" --api web_search

# READ→ENRICH→WRITE 循环
python ~/.claude/skills/gbrain-external-api-lookup/scripts/api_learn_loop.py absorb --topic "AI Agent最新进展"
python ~/.claude/skills/gbrain-external-api-lookup/scripts/api_learn_loop.py absorb --entity "person/sarah-chen"

# 被动充实任务
python ~/.claude/skills/gbrain-external-api-lookup/scripts/api_learn_loop.py ambient --session-id "session-2026-04-18-001"
python ~/.claude/skills/gbrain-external-api-lookup/scripts/api_learn_loop.py ambient --stale-entities --older-than 7d

# 来源检查
python ~/.claude/skills/gbrain-external-api-lookup/scripts/api_learn_loop.py cite-check --entity "company/openai"
python ~/.claude/skills/gbrain-external-api-lookup/scripts/api_learn_loop.py stale --threshold 30d
```

## 与天龙引擎协同

### 天龙引擎集成配置

```yaml
# gbrain-external-api-lookup/config.yaml

api_lookup:
  brain_first:
    enabled: true
    mandatory: true     # 铁律: 外部API前必须先查Brain
    freshness_threshold: "7d"

  external_apis:
    perplexity:
      enabled: true
      priority: 1      # 首选深度研究
    web_search:
      enabled: true
      priority: 2
    linkedin:
      enabled: true
      priority: 3      # 仅用于人员信息
      auth_required: true
    twitter:
      enabled: false  # 默认禁用，需显式启用
      priority: 4

  learn_loop:
    read_first: true
    enrich_merge: true   # 新旧合并而非覆盖
    write_sync: true     # 同步写回
    cite_required: true

  ambient:
    enabled: true
    interrupt: false     # 永远不打断
    subagent_enabled: true
    batch_size: 3
    delay: 30s

# 天龙引擎集成
tianlong_integration:
  attached_role: "07-scribe"
  triggers:
    - "查一下"
    - "lookup"
    - "enrich"
    - "background"
    - "补充背景"
    - "了解一下"
  always_on:
    - "READ_ENRICH_WRITE_LOOP"
    - "AMBIENT_ENRICHMENT"
  upstream:
    - gbrain-hybrid-search
    - gbrain-entity-enrich
  downstream:
    - gbrain-daily-briefing    # 充实结果进入简报
    - gbrain-identity-audit      # 身份相关发现触发审计

  # 被动充实配置
  passive_enrichment:
    enabled: true
    post_session: true
    threshold_mentions: 3      # 提及3次以上才充实
    stale_refresh: true         # 自动刷新陈旧实体
```

### 组织架构映射

| 天龙 Agent | 协同方式 | 协同内容 |
|-----------|---------|---------|
| 01调研师 | Brain-First | 调研前查Brain，减少重复API调用 |
| 00分析师 | 背景补充 | 决策前自动补充相关背景 |
| 07记录师 | 执行核心 | READ→ENRICH→WRITE循环执行者 |
| 09-02编排协调师 | 编排辅助 | 批量充实任务编排 |

### 情报闭环

```
gbrain-external-api-lookup (外部API查询)
    ↓
    ├── [Brain已有] → 直接使用 (节省API调用)
    └── [Brain无/陈旧] → 外部API → Brain写回
            ↓
        gbrain-entity-enrich (如发现新实体)
            ↓
        gbrain-daily-briefing (充实结果进入简报)
```

## 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| API调用节省 | 0 | 40% | +40% |
| 知识留存率 | 瞬时 | 持久 | 质的飞跃 |
| 来源可溯率 | 无 | 100% | 质的飞跃 |
| 对话连贯性 | 打断充实 | 后台异步 | +300% |

## 铁律清单

1. **Brain-First铁律**: 任何外部API调用前必须先查Brain
2. **来源铁律**: 外部获取信息必须标注`[Source: api_name]`
3. **写回铁律**: 调用外部API后必须写回Brain
4. **非打断铁律**: 充实永远不阻塞对话响应
5. **链接铁律**: 提及有页面实体必须建立双向backlink

## 技能文件

- [SKILL.md](SKILL.md) - 本文件
- [config.yaml](config.yaml) - 配置文件
- [scripts/api_lookup.py](scripts/api_lookup.py) - API查询CLI
- [scripts/api_learn_loop.py](scripts/api_learn_loop.py) - READ→ENRICH→WRITE循环CLI
- [prompts/brain_first_template.md](prompts/brain_first_template.md) - Brain-First提示词
