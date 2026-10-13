---
license: UNKNOWN
triggers: ["free llm tier router", "free-llm-tier-router"]
---
# free-llm-tier-router

## L0: 一句话描述 (≤15字)
多Provider按任务难度自动路由。

## L1: 使用场景 (50-100字)
当用户需要根据任务复杂度自动选择最优LLM Provider时使用。复杂推理→Claude Opus，简单任务→Haiku，代码→DeepSeek-Coder，预算敏感→免费本地模型。无需手动切换Provider，系统自动匹配。

## L2: 详细文档

### 核心价值
Tier Router 是 free-claude-code 的核心路由引擎，根据**任务类型**和**模型能力**自动选择最优 Provider，实现：
- **成本优化**：简单任务自动路由到免费/低成本模型
- **能力匹配**：复杂任务自动升级到最强模型
- **延迟优化**：本地模型优先，避免网络延迟
- **容错保障**：Provider 故障时自动切换备选

### 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│              free-llm-tier-router 四层路由架构                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Tier 4: SONNET  (Claude 3.5 Sonnet)                     │
│    → 复杂推理、架构设计、长文档分析                        │
│    Provider: OpenRouter / NVIDIA NIM                        │
│                                                             │
│  Tier 3: OPUS    (Claude 3 Opus)                          │
│    → 代码审查、架构决策、安全审计                          │
│    Provider: OpenRouter / NVIDIA NIM                       │
│                                                             │
│  Tier 2: HAUKU  (Claude 3 Haiku)                          │
│    → 快速分类、摘要、简单问答                             │
│    Provider: OpenRouter / DeepSeek                         │
│                                                             │
│  Tier 1: LOCAL   (本地模型)                               │
│    → 离线开发、低延迟、成本敏感                           │
│    Provider: Ollama / LM Studio / llama.cpp                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 四层路由规则

#### Tier 1: LOCAL (本地模型)
**触发关键词**：
- `离线`、`内网`、`无网`、`本地开发`
- `快速`、`简单`、`测试`、`原型`
- `成本`、`预算`、`免费`

**路由模型**：
| Provider | 模型 | 适用场景 |
|----------|------|---------|
| Ollama | `llama3.1:8b` | 通用对话 |
| Ollama | `deepseek-coder:6.7b` | 代码辅助 |
| Ollama | `qwen2.5:7b` | 中文对话 |
| LM Studio | `meta-llama-3.1-8b` | 高性能通用 |
| llama.cpp | `llama-3.1-8b.Q4_K_M` | 极致轻量 |

#### Tier 2: HAUKU (轻量云端)
**触发关键词**：
- `分类`、`标签`、`标记`
- `摘要`、`总结`、`概要`
- `快速回答`、`简单问答`
- `翻译`(简短)、`润色`

**路由模型**：
| Provider | 模型 | 成本 | 延迟 |
|----------|------|------|------|
| DeepSeek | `deepseek-chat-v3-0324` | $0.001/M tok | ~500ms |
| OpenRouter | `anthropic/claude-3-haiku` | $0.001/M tok | ~800ms |

#### Tier 3: OPUS (复杂推理)
**触发关键词**：
- `代码审查`、`架构设计`、`系统设计`
- `安全审计`、`风险评估`
- `复杂分析`、`深度推理`
- `多步骤`、`跨领域`

**路由模型**：
| Provider | 模型 | 成本 | 适用场景 |
|----------|------|------|---------|
| OpenRouter | `anthropic/claude-3-opus` | $0.015/M tok | 最高推理能力 |
| NVIDIA NIM | `claude-3-opus` | 按量计费 | 企业级 |

#### Tier 4: SONNET (平衡推理)
**触发关键词**：
- `代码`、`编程`、`实现`
- `文档撰写`、`报告生成`
- `创意写作`、`头脑风暴`
- `数据分析`、`图表`

**路由模型**：
| Provider | 模型 | 成本 | 适用场景 |
|----------|------|------|---------|
| OpenRouter | `anthropic/claude-3.5-sonnet` | $0.003/M tok | 最佳性价比 |
| DeepSeek | `deepseek-reasoner` | $0.002/M tok | 推理优化 |

### 路由决策算法

```python
# tier_router.py - 核心路由逻辑
import re
from dataclasses import dataclass
from typing import Literal

Tier = Literal["local", "haiku", "sonnet", "opus"]

@dataclass
class RouteConfig:
    provider: str
    model: str
    base_url: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    latency_ms: int
    capabilities: list[str]

TIER_CONFIGS: dict[Tier, list[RouteConfig]] = {
    "local": [
        RouteConfig("ollama", "llama3.1:8b", "http://localhost:11434", 0, 0, 50, ["chat", "code"]),
        RouteConfig("lmstudio", "meta-llama-3.1-8b", "http://localhost:1234/v1", 0, 0, 80, ["chat", "code"]),
        RouteConfig("llamacpp", "llama-3.1-8b-instruct", "http://localhost:8080/v1", 0, 0, 100, ["chat"]),
    ],
    "haiku": [
        RouteConfig("deepseek", "deepseek-chat-v3-0324", "https://api.deepseek.com", 0.001, 0.001, 500, ["chat", "fast"]),
        RouteConfig("openrouter", "anthropic/claude-3-haiku", "https://openrouter.ai/api/v1", 0.001, 0.001, 800, ["chat", "fast"]),
    ],
    "sonnet": [
        RouteConfig("openrouter", "anthropic/claude-3.5-sonnet", "https://openrouter.ai/api/v1", 0.003, 0.015, 1200, ["chat", "code", "analysis"]),
        RouteConfig("deepseek", "deepseek-reasoner", "https://api.deepseek.com", 0.002, 0.008, 1000, ["reasoning", "analysis"]),
    ],
    "opus": [
        RouteConfig("openrouter", "anthropic/claude-3-opus", "https://openrouter.ai/api/v1", 0.015, 0.075, 2000, ["reasoning", "analysis", "code", "security"]),
        RouteConfig("nvidia", "claude-3-opus", "https://integrate.api.nvidia.com/v1", 0.01, 0.05, 1500, ["reasoning", "analysis", "code", "security"]),
    ],
}

# 关键词匹配规则
TIER_KEYWORDS: dict[Tier, list[str]] = {
    "local": ["离线", "内网", "本地", "快速", "简单", "免费", "成本", "预算", "测试", "原型"],
    "haiku": ["分类", "标签", "摘要", "总结", "概要", "快速回答", "简单问答", "翻译"],
    "sonnet": ["代码", "编程", "实现", "文档", "报告", "创意", "头脑风暴", "分析", "图表", "代码审查"],
    "opus": ["架构", "系统设计", "安全审计", "风险评估", "复杂推理", "深度推理", "跨领域", "复杂分析"],
}

def classify_tier(prompt: str) -> Tier:
    """根据 prompt 内容分类到对应 Tier"""
    prompt_lower = prompt.lower()

    # 优先级从高到低检查
    if any(kw in prompt_lower for kw in TIER_KEYWORDS["opus"]):
        return "opus"
    if any(kw in prompt_lower for kw in TIER_KEYWORDS["sonnet"]):
        return "sonnet"
    if any(kw in prompt_lower for kw in TIER_KEYWORDS["haiku"]):
        return "haiku"
    if any(kw in prompt_lower for kw in TIER_KEYWORDS["local"]):
        return "local"

    # 默认: sonnet (平衡选择)
    return "sonnet"

def select_provider(tier: Tier, available_providers: list[str]) -> RouteConfig:
    """从可用 Provider 中选择最优配置"""
    configs = TIER_CONFIGS[tier]

    # 按优先级过滤可用 Provider
    for config in configs:
        if config.provider in available_providers:
            return config

    # 降级策略: 尝试其他 Tier
    fallback_tiers = ["sonnet", "haiku", "local"]
    for fallback_tier in fallback_tiers:
        if fallback_tier == tier:
            continue
        for config in TIER_CONFIGS[fallback_tier]:
            if config.provider in available_providers:
                return config

    raise ValueError(f"No available provider for tier {tier}")
```

### 6大 Provider 支持

| Provider | 端点 | 模型示例 | 费用 | 特点 |
|----------|------|---------|------|------|
| **OpenRouter** | openrouter.ai/api/v1 | Claude/Haiku/GPT-4o | 按量计费 | 聚合 100+ 模型 |
| **NVIDIA NIM** | integrate.api.nvidia.com | Claude 3 Opus/Haiku | 企业定价 | 低延迟高可用 |
| **DeepSeek** | api.deepseek.com | DeepSeek-V3/Reasoner | $0.002/M | 推理优化 |
| **Ollama** | localhost:11434 | llama3.1/DeepSeek-Coder | **免费** | 本地离线 |
| **LM Studio** | localhost:1234 | Meta-Llama/Mistral | **免费** | 高性能本地 |
| **llama.cpp** | localhost:8080 | GGUF 量化模型 | **免费** | 极致轻量 |

### 安装配置

#### 方式一: 自动安装 (推荐)
```bash
cd ~/.claude/skills/free-llm-tier-router
bash scripts/setup.sh
```

#### 方式二: 手动配置
```bash
# 1. 安装依赖
uv pip install httpx pydantic python-dotenv

# 2. 配置环境变量
cp configs/.env.example .env
# 编辑 .env 填入 API Key

# 3. 配置 Provider (至少选择一个)
# OpenRouter: https://openrouter.ai/keys
# DeepSeek: https://platform.deepseek.com/api_keys
# NVIDIA: https://org.nvidia.com/
```

#### 环境变量配置
```bash
# .env 文件示例
ANTHROPIC_AUTH_TOKEN=freecc
ANTHROPIC_BASE_URL=http://localhost:8082

# Provider API Keys (至少配置一个)
OPENROUTER_API_KEY=sk-or-v1-xxxxx
DEEPSEEK_API_KEY=sk-xxxxx
NVIDIA_API_KEY=nvapi-xxxxx

# 默认路由策略
DEFAULT_TIER=sonnet
FALLBACK_ENABLED=true
LOCAL_PROVIDER=ollama
```

### 使用方法

#### CLI 路由命令
```bash
# 基本路由测试
python scripts/tier_router.py route "帮我写一段 Python 代码"

# 指定 Tier
python scripts/tier_router.py route --tier opus "设计一个微服务架构"

# 查看所有可用 Provider
python scripts/tier_router.py status

# 路由到指定 Provider
python scripts/tier_router.py direct --provider openrouter --model claude-3.5-sonnet "Hello"
```

#### 自然语言触发
```
用户: 帮我写一个快速排序算法
路由: 识别关键词"快速"、"算法" → 判断复杂度
     → 路由到本地 Ollama (Tier 1 LOCAL)
     → 响应时间 ~500ms, 成本 $0

用户: 设计一个高可用的消息队列系统
路由: 识别关键词"设计"、"架构"、"高可用"
     → 路由到 OpenRouter Claude Opus (Tier 4 OPUS)
     → 响应时间 ~2s, 成本 ~$0.02
```

#### Python SDK 使用
```python
from tier_router import TierRouter, Tier

router = TierRouter()

# 自动路由
result = router.chat("帮我写一个快速排序算法")
print(f"路由 Tier: {result.tier}")
print(f"使用 Provider: {result.provider}/{result.model}")
print(f"Token 消耗: {result.input_tokens} in + {result.output_tokens} out")

# 强制指定 Tier
result = router.chat(
    "设计微服务架构",
    tier=Tier.OPUS,
    fallback=True  # Tier 不可用时降级
)

# 批量路由
tasks = [
    "翻译这段话",
    "代码审查这段代码",
    "设计系统架构",
]
results = router.batch_chat(tasks)
for r in results:
    print(f"[{r.tier}] {r.provider}/{r.model}: {r.summary}")
```

### 性能监控

```bash
# 查看路由统计
python scripts/tier_router.py stats

# 输出示例:
# === Tier Router Statistics ===
# Total Requests: 1,234
#
# By Tier:
#   LOCAL:   456 (37%) ████████████████████
#   HAIKU:   234 (19%) ██████████
#   SONNET:  389 (32%) ████████████████
#   OPUS:    155 (13%) ██████
#
# By Provider:
#   Ollama:       456 (37%)
#   DeepSeek:      312 (25%)
#   OpenRouter:   466 (38%)
#
# Cost Summary:
#   Total: $12.34
#   Saved (LOCAL): $98.76 vs OpenAI
#   Savings Rate: 89%
```

### 故障切换策略

```
┌─────────────────────────────────────────────────────────────┐
│                  故障切换流程                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Primary Provider 失败                                  │
│     ↓                                                       │
│  2. 检查 fallback 配置                                     │
│     ↓                                                       │
│  3. 尝试同 Tier 其他 Provider                               │
│     ↓                                                       │
│  4. 降级到更低 Tier (如果 fallback=true)                  │
│     ↓                                                       │
│  5. 降级到本地模型 (最后保障)                             │
│     ↓                                                       │
│  6. 返回结果或报错                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 与 free-llm-local-bridge 协同

```
┌─────────────────────────────────────────────────────────────┐
│              天龙引擎 LLM 路由三层架构                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 3: Tier Router  (免费策略层)                         │
│    → free-llm-tier-router ⭐本技能                         │
│    → 根据任务复杂度自动路由到最优 Tier                       │
│                                                             │
│  Layer 2: Provider Bridge (本地模型层)                      │
│    → free-llm-local-bridge ⭐已创建                       │
│    → Ollama / LM Studio / llama.cpp 本地推理               │
│                                                             │
│  Layer 1: Claude Code (应用层)                             │
│    → ANTHROPIC_BASE_URL=http://localhost:8082             │
│    → 自动使用 Tier Router 路由                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 文件结构

```
free-llm-tier-router/
├── SKILL.md                      # 本文件
├── scripts/
│   ├── setup.sh                  # 安装脚本
│   ├── tier_router.py             # 核心路由引擎
│   ├── provider_check.py          # Provider 健康检查
│   └── stats.py                   # 统计报告
└── configs/
    ├── .env.example              # 环境变量模板
    ├── .env.nvidia               # NVIDIA NIM 配置
    ├── .env.openrouter           # OpenRouter 配置
    └── .env.deepseek             # DeepSeek 配置
```

### 预期收益

| 指标 | 无路由 | 有 Tier Router | 提升 |
|------|--------|-----------------|------|
| **成本节省** | 全部使用 Claude | 自动用免费本地 | **90%+** |
| **平均延迟** | 1500ms | 优化路由 | **-60%** |
| **Provider 覆盖** | 手动切换 | 自动 6 Provider | **+500%** |
| **容错能力** | 单点故障 | 自动切换 | **质的飞跃** |

### 触发命令

```bash
# Tier Router 命令
/tier-route "任务描述"           # 自动路由
/tier-status                      # 查看 Provider 状态
/tier-stats                       # 查看路由统计
/tier-tier --tier opus "任务"    # 强制指定 Tier

# 与本地桥接协同
/free-bridge status               # 查看本地 Provider
/free-bridge bench                # 基准测试
```
