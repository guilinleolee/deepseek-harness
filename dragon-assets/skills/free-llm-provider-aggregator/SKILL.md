---
license: UNKNOWN
github_repo: cheahjs/free-llm-api-resources
github_hash: b67cfc61f7663b822d0f860f554f5afd4a2bec4a
triggers: ["free llm provider aggregator", "Free LLM Provider Aggregator - 零成本AI推理资源聚合"]
---
# Free LLM Provider Aggregator - 零成本AI推理资源聚合

## 来源
> [cheahjs/free-llm-api-resources](https://github.com/cheahjs/free-llm-api-resources) - 16,644 Stars 免费LLM API资源聚合

github:
  repo: cheahjs/free-llm-api-resources
  hash: b67cfc61f7663b822d0f860f554f5afd4a2bec4a
  date: "2026-04-25"
  note: Local天龙 skill - provider matrix based on upstream data

## 核心价值
实现**零成本AI推理**，聚合14个免费提供商 + 15个试用额度提供商，让AI调用从付费变为免费。

## 免费提供商矩阵

### P0级（推荐优先使用）

| 提供商 | 配额 | 模型 | 延迟 | 特点 |
|--------|------|------|------|------|
| **Groq** | 14400请求/天 | DeepSeek R1, QwQ-32B, Llama 3.3 70B | **100-500ms** | 超低延迟推理 |
| **Google AI Studio** | 250K tokens/分钟 | Gemini 2.5 Pro, Gemini 2.0 Flash | 中等 | 多模态支持 |
| **OpenRouter** | 50请求/天 | 25+免费模型 | 中等 | 多模型对比 |

### P1级（次优选择）

| 提供商 | 配额 | 模型 | 延迟 | 特点 |
|--------|------|------|------|------|
| **Cerebras** | 1M tokens/天 | Llama 3.3 70B | 低 | 大批量处理 |
| **Cloudflare Workers AI** | 100K请求/天 | Llama 3.1, Mistral | 低 | 边缘部署 |
| **Mistral Free** | 1B tokens/月 | Mistral 7B, Mixtral | 中等 | 开源模型 |

### P2级（备选）

| 提供商 | 配额 | 模型 | 延迟 | 特点 |
|--------|------|------|------|------|
| **NVIDIA NIM** | 4500 tokens | Llama 3.1, Mistral | 中等 | GPU优化 |
| **GitHub Models** | Copilot订阅 | GPT-4o, o1-preview | 中等 | 高质量 |
| **Cohere** | 1000次/月 | Command R+ | 中等 | 企业级 |

## 使用方式

### API调用

```javascript
const { selectWithFreePriority, selectWithLatencyPriority } = require('../shared/ai-router.js');

// 成本优先（默认）
const provider = selectWithFreePriority();
// → { name: 'groq', type: 'zero-token', priority: 'P0', cost: 0 }

// 延迟优先
const fastProvider = selectWithLatencyPriority();
// → { name: 'groq', estimatedLatency: '100-500ms', cost: 0 }
```

## 使用场景

### 场景1: 大批量内容生成
```yaml
目标: 生成1000篇营销文案
策略:
  1. 主提供商: Cerebras (1M tokens/天)
  2. 备用: Groq (14400请求/天)
  3. 成本: $0
```

### 场景2: 实时对话
```yaml
目标: 客服机器人实时响应
策略:
  1. 主提供商: Groq (100-500ms)
  2. 备用: Cloudflare Workers AI
  3. 延迟: <500ms
```

## 相关技能
- [smart-provider-router](../smart-provider-router/SKILL.md) - 智能路由选择
- [ai-router.js](../shared/ai-router.js) - V5.0 AI路由器

## 版本
- V1.0 (2026-03-23) - 初始版本，聚合14+15个提供商
