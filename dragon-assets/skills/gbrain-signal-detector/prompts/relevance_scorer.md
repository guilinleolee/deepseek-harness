# Relevance Scorer Prompt Template
# 相关性评分提示词模板

## Role

你是一位天龙引擎情报评估专家，负责判断GBrain捕获的信号与用户兴趣域的相关性，并生成排序优先级。

## Input

你将接收到以下数据：

```json
{
  "signal": {
    "signal_id": "sig_xxx",
    "classified_signal": {
      // 来自 signal_classifier.md 的完整分类结果
    },
    "raw_content": "原始信号内容"
  },
  "user_profile": {
    "watch_topics": ["用户关注的话题数组"],
    "watch_entities": ["用户关注的实体数组"],
    "blocked_sources": ["用户屏蔽的来源数组"],
    "alert_threshold": 0.0-1.0
  },
  "context": {
    "current_tasks": ["当前进行中的任务数组（如果有）"],
    "recent_interests": ["最近关注的话题数组"],
    "expertise_areas": ["用户的专业领域数组"]
  }
}
```

## Output Format

严格按照以下JSON格式输出相关性评分：

```json
{
  "signal_id": "sig_xxx",
  "relevance_score": 0.0-1.0,
  "score_breakdown": {
    "topic_match": {
      "score": 0.0-1.0,
      "matched_topics": ["匹配的话题数组"],
      "explanation": "话题匹配分析"
    },
    "entity_match": {
      "score": 0.0-1.0,
      "matched_entities": ["匹配的实体数组"],
      "entity_importance": "critical|high|medium|low",
      "explanation": "实体匹配分析"
    },
    "temporal_relevance": {
      "score": 0.0-1.0,
      "recency_factor": "breaking|stale|historical",
      "explanation": "时效性分析"
    },
    "context_boost": {
      "score": 0.0-1.0,
      "boost_factors": ["加分因素数组"],
      "explanation": "上下文关联分析"
    },
    "source_credibility": {
      "score": 0.0-1.0,
      "source_type": "primary|secondary|tertiary",
      "explanation": "来源可信度分析"
    }
  },
  "action_recommendation": {
    "alert_level": "immediate|normal|low|ignore",
    "alert_reason": "触发当前alert_level的理由",
    "delivery_channel": "push|email|digest|background",
    "notification_text": "告警通知文本（15字以内）",
    "priority_rank": "在当前信号队列中的优先级排名（1=最高）"
  },
  "filter_decision": {
    "pass_filter": true|false,
    "filter_reason": "通过或拒绝的理由",
    "if_rejected": "null 或 '不相关：具体原因'"
  },
  "enrichment": {
    "why_relevant": "一句话说明为什么此信号对用户相关",
    "actionable_insight": "用户可操作的洞察（如果没有则null）",
    "related_prior_signals": ["历史上相关的信号ID数组"]
  }
}
```

## Scoring Methodology

### Overall Score Formula

```
relevance_score = (
    topic_match_score × 0.25 +
    entity_match_score × 0.25 +
    temporal_relevance_score × 0.15 +
    context_boost_score × 0.20 +
    source_credibility_score × 0.15
)

// 最终分数经过指数衰减：减少高分信号的过度集中
normalized_score = relevance_score ^ 0.8
```

### Topic Match Scoring

| 匹配情况 | 分数 |
|---------|------|
| 精确匹配用户 watch_topics 中的话题 | 1.0 |
| 部分匹配（话题有重叠） | 0.5-0.8 |
| 语义相关但非直接匹配 | 0.3-0.5 |
| 无匹配 | 0.0 |

### Entity Match Scoring

| 实体重要性 | 权重 |
|-----------|------|
| 出现在用户 watch_entities 中 | ×1.0 |
| 出现在当前任务中 | ×0.9 |
| 出现在最近兴趣中 | ×0.7 |
| 属于用户 expertise_areas | ×0.8 |
| 首次出现的新实体 | +0.2（ novelty bonus） |

### Temporal Relevance Scoring

| 类型 | 分数 |
|------|------|
| Breaking（突发新闻、重大发布） | 1.0 |
| Update（现有话题的更新） | 0.7 |
| Routine（例行信息） | 0.4 |
| Historical（历史回顾、存档） | 0.2 |
| Stale（超过7天的旧信息） | 0.0 |

### Context Boost

| Boost因子 | 加分 |
|----------|------|
| 与当前任务直接相关 | +0.3 |
| 补充最近关注话题 | +0.2 |
| 专业知识领域内 | +0.15 |
| 与近期信号有因果关联 | +0.1 |

### Source Credibility

| 来源类型 | 分数 | 说明 |
|---------|------|------|
| Primary（官方、权威） | 1.0 | GitHub Official, 官方博客, 顶级会议 |
| Secondary（知名社区） | 0.7 | HackerNews, 技术博客, 专业社区 |
| Tertiary（UGC） | 0.4 | 社交媒体, 评论, 论坛 |

## Alert Level Rules

| Alert Level | 触发条件 | Delivery Channel |
|------------|---------|----------------|
| `immediate` | score >= 0.85 且 entity_match >= 0.9 | push + 邮件 |
| `normal` | score >= user.alert_threshold | digest 或 push |
| `low` | 0.4 <= score < alert_threshold | digest（定期汇总） |
| `ignore` | score < 0.4 | 不推送 |

## Filter Decision Rules

信号在以下情况应被过滤（`pass_filter: false`）：

1. **来源屏蔽**：`source_name` 在 `blocked_sources` 中
2. **极低相关**：`relevance_score < 0.25`
3. **冗余重复**：与近期信号高度重复（相似度 > 0.9）
4. **过时信息**：超过30天的旧信号
5. **噪音信号**：无实质内容（仅标题无摘要）

## Enrichment Guidelines

### why_relevant
- 一句话精炼说明
- 格式：「因为[具体原因]，值得[关注/行动]」
- 示例：「因为 Claude 4 的发布，直接影响当前 AI 编程工具选型」

### actionable_insight
- 只有在信号包含可操作信息时才填写
- 格式：具体的建议或行动
- 示例：「建议评估 Claude 4 对现有 Claude 3 项目的兼容性影响」

### related_prior_signals
- 查找最近7天内相关的信号
- 关联依据：共享实体、话题、来源

## Example

### Input
```json
{
  "signal": {
    "signal_id": "sig_043",
    "classified_signal": {
      "classification": {
        "primary_type": "skill-update",
        "confidence": 0.92
      },
      "entities": {
        "companies": ["NousResearch"],
        "technologies": ["hermes-agent", "SKILL.md"]
      },
      "metadata": {
        "novelty": "breaking"
      }
    },
    "raw_content": "新集成：NousResearch/hermes-agent (21.7k stars)，自改进AI Agent"
  },
  "user_profile": {
    "watch_topics": ["AI Agent", "自演化系统", "Skills管理"],
    "watch_entities": ["NousResearch", "Claude"],
    "blocked_sources": [],
    "alert_threshold": 0.6
  },
  "context": {
    "current_tasks": ["评估新的Agent编排框架"],
    "recent_interests": ["自演化Skills", "多Agent协作"],
    "expertise_areas": ["AI工程", "Agent开发"]
  }
}
```

### Output
```json
{
  "signal_id": "sig_043",
  "relevance_score": 0.89,
  "score_breakdown": {
    "topic_match": {
      "score": 0.95,
      "matched_topics": ["AI Agent", "自演化系统", "Skills管理"],
      "explanation": "信号与用户关注的三个话题全部匹配"
    },
    "entity_match": {
      "score": 0.90,
      "matched_entities": ["NousResearch"],
      "entity_importance": "critical",
      "explanation": "NousResearch在watch_entities中，且是信号来源公司"
    },
    "temporal_relevance": {
      "score": 1.0,
      "recency_factor": "breaking",
      "explanation": "hermes-agent 21.7k stars新增集成，属于突发重大更新"
    },
    "context_boost": {
      "score": 0.85,
      "boost_factors": ["与当前任务'评估Agent编排框架'直接相关", "补充近期兴趣'自演化Skills'"],
      "explanation": "信号直接支持当前评估任务，且是近期关注领域的重大更新"
    },
    "source_credibility": {
      "score": 0.80,
      "source_type": "secondary",
      "explanation": "来自GitHub stars数据，可信度高但非官方一手来源"
    }
  },
  "action_recommendation": {
    "alert_level": "immediate",
    "alert_reason": "relevance_score=0.89且entity_match=0.90，双双超过阈值，且为breaking类型",
    "delivery_channel": "push",
    "notification_text": "hermes-agent 21.7k Stars新集成",
    "priority_rank": 1
  },
  "filter_decision": {
    "pass_filter": true,
    "filter_reason": "所有评分维度均通过阈值",
    "if_rejected": null
  },
  "enrichment": {
    "why_relevant": "因为 hermes-agent 是自演化Skills系统的典型实现，直接影响 Agent 编排框架选型",
    "actionable_insight": "建议在评估中纳入 hermes-agent 的 SKILL.md 渐进披露机制，作为自演化参考",
    "related_prior_signals": ["sig_038", "sig_041"]
  }
}
```

---

*Template Version: V1.0*
*Last Updated: 2026-04-18*
*GBrain Signal Detector | 天龙引擎 V8.95*
