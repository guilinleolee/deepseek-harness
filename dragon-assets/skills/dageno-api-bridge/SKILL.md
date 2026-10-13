---
license: UNKNOWN
triggers: ["dageno api bridge", "DAGENO-API-BRIDGE SKILL"]
---
# DAGENO-API-BRIDGE SKILL

> **Version**: V1.0
> **Category**: GEO Content Generation / API Bridge
> **Dependencies**: geo-content-generator (dageno_client.py)
> **天龙引擎版本**: V8.87+

---

## 一句话描述 (L0)

连接GEO Agent与Dageno API服务，实现AI搜索机会发现和引用数据获取的桥接技能。

---

## 使用场景 (L1)

当需要以下操作时使用本技能：

1. **GEO机会发现** - 分析主题发现AI搜索引擎优化机会
2. **Fanout获取** - 获取特定机会的传播路径列表
3. **引用数据获取** - 获取权威来源的引用数据和上下文
4. **机会分析** - 对发现的机会进行结构化分析
5. **引用增强** - 基于真实引用数据增强内容权威性

**触发关键词**：
- "GEO机会"、"AI搜索优化"、"dageno"
- "发现引用"、"获取权威来源"、"机会分析"
- "优化AI引用"、"RAG增强"

---

## 详细文档 (L2)

### 1. 核心能力

#### 1.1 三层API接口

| 方法 | 端点 | 功能 | 返回数据 |
|------|------|------|----------|
| `discover_opportunities` | `/opportunities` | 发现GEO机会 | 机会ID、类型、查询量 |
| `get_fanouts` | `/opportunities/{id}/fanouts` | 获取传播路径 | Fanout列表、平台分布 |
| `get_citations` | `/fanouts/{id}/citations` | 获取引用数据 | 引用URL、来源权威性、上下文 |

#### 1.2 环境配置

```bash
# 设置Dageno API密钥（注意：环境变量名为DAGEN0含数字0）
export DAGEN0_API_KEY="your-api-key"

# 或在代码中直接传入
client = DagenoClient(api_key="your-api-key")
```

#### 1.3 Mock数据回退

当未设置API密钥时，自动使用Mock数据进行开发和测试：
- 3个模拟GEO机会（"best AI models 2024"、"how do neural networks work"、"what is RAG"）
- 每个机会包含多个Fanout（学术博客、技术社区、产品文档）
- 每个Fanout包含引用数据（来源URL、权威评分、上下文片段）

---

### 2. SKILL目录结构

```
dageno-api-bridge/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── dageno_bridge.py      # 核心桥接脚本
│   └── dageno_analyzer.py     # 机会分析脚本
├── prompts/
│   ├── opportunity_discovery.md    # 机会发现提示词
│   ├── citation_analysis.md        # 引用分析提示词
│   └── fanout_mapping.md          # Fanout映射提示词
└── templates/
    ├── geo_opportunity_report.md   # 机会分析报告模板
    └── citation_context.md          # 引用上下文模板
```

---

### 3. 核心脚本

#### 3.1 dageno_bridge.py

桥接脚本封装三层API调用：

```python
from dageno_bridge import DagenoBridge

bridge = DagenoBridge()

# 1. 发现GEO机会
opportunities = bridge.discover_opportunities("RAG optimization", limit=10)

# 2. 获取Fanout列表
fanouts = bridge.get_fanouts(opportunities[0]['id'])

# 3. 获取引用数据
citations = bridge.get_citations(fanouts[0]['id'], limit=20)

# 4. 完整工作流
result = bridge.full_workflow("LLM evaluation metrics", limit=5)
```

#### 3.2 dageno_analyzer.py

机会分析脚本提供：
- 机会重要性评分
- 来源权威性分析
- 内容Gap识别
- 引用密度计算

---

### 4. 与GEO Agent协同

```
┌─────────────────────────────────────────────────────────────┐
│                  GEO Agent V2.0 工作流                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: 机会发现 (dageno-api-bridge)                    │
│  ├── discover_opportunities() → TOP机会列表                │
│  └── get_fanouts() → 传播路径分析                        │
│                                                             │
│  Phase 2: 引用获取 (dageno-api-bridge)                    │
│  ├── get_citations() → 权威引用数据                      │
│  └── 上下文片段 → 内容增强素材                            │
│                                                             │
│  Phase 3: 内容创作 (geo-content-generator)                │
│  ├── 基于真实引用撰写 → 增强权威性                       │
│  └── 嵌入[comparison][decision engine] → 必须元素        │
│                                                             │
│  Phase 4: 质量审核 (outputquality-contract)               │
│  ├── 5层质量门控 → L2引用质量审核                        │
│  └── AI痕迹检测 → L5人类可读审核                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 5. 核心命令

```bash
# 机会发现
python ~/.claude/skills/dageno-api-bridge/scripts/dageno_bridge.py \
  discover "RAG optimization" --limit 10

# Fanout获取
python ~/.claude/skills/dageno-api-bridge/scripts/dageno_bridge.py \
  fanouts <opportunity_id>

# 引用获取
python ~/.claude/skills/dageno-api-bridge/scripts/dageno_bridge.py \
  citations <fanout_id> --limit 20

# 完整工作流
python ~/.claude/skills/dageno-api-bridge/scripts/dageno_bridge.py \
  workflow "LLM evaluation" --limit 5

# 机会分析
python ~/.claude/skills/dageno-api-bridge/scripts/dageno_analyzer.py \
  analyze <opportunity_id>
```

---

### 6. 输出格式

#### 6.1 GEO机会数据

```json
{
  "opportunity_id": "op_xxx",
  "topic": "RAG optimization",
  "query_volume": 15000,
  "opportunity_type": "informational",
  "fanouts": [
    {
      "fanout_id": "fn_xxx",
      "platform": "academic_blog",
      "title": "RAG Best Practices",
      "citation_count": 25
    }
  ]
}
```

#### 6.2 引用数据

```json
{
  "citation_id": "ct_xxx",
  "url": "https://example.com/article",
  "source_type": "research_paper",
  "authority_score": 0.85,
  "context_snippet": "Key findings from the study show...",
  "cited_by_count": 150
}
```

---

### 7. 集成方式

#### 7.1 天龙引擎调用

```bash
# 通过GEO Agent使用
[@GEO Agent] 使用dageno-api-bridge发现"AI Agent框架"相关的GEO机会

# 直接调用脚本
python ~/.claude/skills/dageno-api-bridge/scripts/dageno_bridge.py \
  workflow "AI Agent framework comparison"
```

#### 7.2 Python API集成

```python
from dageno_api_bridge import DagenoBridge, DagenoAnalyzer

# 初始化
bridge = DagenoBridge(api_key=os.getenv("DAGEN0_API_KEY"))
analyzer = DagenoAnalyzer()

# 完整流程
opportunities = bridge.discover_opportunities("machine learning", limit=10)
fanouts = bridge.get_fanouts(opportunities[0]['id'])
citations = bridge.get_citations(fanouts[0]['id'], limit=20)

# 分析
analysis = analyzer.analyze_opportunity(opportunities[0], citations)
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-10 | 初始版本，基于dageno_client.py封装 |

---

## 相关SKILL

- **geo-content-generator**: GEO内容生成器，使用本技能获取的数据进行创作
- **outputquality-contract**: GEO内容质量审核，验证引用权威性
- **seo-content**: SEO内容质量审核
