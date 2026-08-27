---
license: UNKNOWN
github_repo: cheahjs/free-llm-api-resources
github_hash: b67cfc61f7663b822d0f860f554f5afd4a2bec4a
triggers: ["smart provider router", "Smart Provider Router - 智能提供商路由"]
---
# Smart Provider Router - 智能提供商路由

## 来源
> 基于 [cheahjs/free-llm-api-resources](https://github.com/cheahjs/free-llm-api-resources) 的智能路由实现

github:
  repo: cheahjs/free-llm-api-resources
  hash: b67cfc61f7663b822d0f860f554f5afd4a2bec4a
  date: "2026-04-25"
  note: Local天龙 skill - 5 routing modes

## 核心价值
根据任务特征**自动选择最优AI提供商**，实现成本、延迟、质量的智能平衡。

## 路由策略

### 5大路由模式

| 模式 | 优先级 | 适用场景 | 推荐提供商 |
|------|--------|---------|-----------|
| **Cost-First** | 成本 > 延迟 > 质量 | 大批量任务 | Groq > Cerebras > Cloudflare |
| **Latency-First** | 延迟 > 成本 > 质量 | 实时交互 | Groq > Cloudflare > Mistral |
| **Quality-First** | 质量 > 成本 > 延迟 | 高质量输出 | GitHub Models > Google Studio |
| **Reasoning-First** | 推理能力 | 数学/逻辑 | Groq (DeepSeek R1) > OpenRouter |
| **Quota-Round** | 配额轮换 | 长时间任务 | 多提供商轮换 |

## API使用

### 基础路由

```javascript
const router = require('../shared/ai-router.js');

// 成本优先（默认）
const provider = router.selectWithFreePriority();
// → { name: 'groq', type: 'zero-token', priority: 'P0', cost: 0 }

// 延迟优先
const fast = router.selectWithLatencyPriority();
// → { name: 'groq', estimatedLatency: '100-500ms', cost: 0 }
```

### 高级路由

```javascript
// 任务类型路由
const reasoning = router.selectWithFreePriority({
  taskType: 'reasoning',  // 推理任务
  minQuality: 0.8         // 最低质量要求
});
// → { name: 'groq', model: 'deepseek-r1-distill-llama-70b' }

// 多模态路由
const multimodal = router.selectWithFreePriority({
  taskType: 'multimodal'  // 多模态任务
});
// → { name: 'googleStudio', model: 'gemini-2.0-flash' }
```

## 路由决策树

```
任务到达
    │
    ├── 需要推理？ ────────────────── Groq (DeepSeek R1)
    │
    ├── 需要多模态？ ──────────────── Google AI Studio
    │
    ├── 需要低延迟？ ──────────────── Groq (100-500ms)
    │
    ├── 需要大批量？ ──────────────── Cerebras (1M tokens)
    │
    ├── 需要高质量？ ──────────────── GitHub Models
    │
    └── 默认成本优先 ──────────────── Groq > Cerebras > Cloudflare
```

## 性能指标

| 指标 | 值 |
|------|-----|
| 路由决策延迟 | <10ms |
| Fallback切换时间 | <100ms |
| 零成本覆盖率 | 95%+ |
| 平均响应延迟 | 100-500ms |

## 相关技能
- [free-llm-provider-aggregator](../free-llm-provider-aggregator/SKILL.md) - 提供商聚合
- [ai-router.js](../shared/ai-router.js) - V5.0 路由实现

## 版本
- V1.0 (2026-03-23) - 初始版本，支持5大路由模式
