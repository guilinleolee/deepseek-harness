# AI Content Optimizer

> 基于 LLM 的演示文稿内容优化模块

## 模块定位

本模块集成于 Strategist 阶段，在生成 `design_spec.md` 之前对源文档内容进行智能优化。

## 优化能力

### 1. 标题优化 (Title Optimization)

**目标**: 生成更具吸引力、更专业的幻灯片标题

**输入**: 源文档标题列表
**输出**: 优化后的标题列表 + 评分

**评分维度**:
| 维度 | 权重 | 说明 |
|------|------|------|
| 清晰度 | 25% | 标题是否清晰表达主题 |
| 吸引力 | 25% | 是否有吸引力，激发兴趣 |
| 专业性 | 25% | 措辞是否专业得体 |
| 简洁性 | 25% | 是否简洁，避免冗余 |

**提示词模板**:

```markdown
# 标题优化任务

## 原始标题
{original_titles}

## 优化要求
1. 保持原意，不歪曲内容
2. 提升表达力，增加吸引力
3. 统一风格，与演示场景匹配
4. 长度控制在8-20字

## 输出格式
```json
{
  "optimized": [
    {
      "original": "原始标题",
      "optimized": "优化后标题",
      "score": 85,
      "suggestions": ["建议1", "建议2"]
    }
  ]
}
```

## 2. 内容润色 (Content Polishing)

**目标**: 提升文案质量，使其更专业、更有说服力

**优化维度**:
| 维度 | 说明 | 示例 |
|------|------|------|
| 术语标准化 | 统一专业术语表达 | "AI" vs "人工智能" |
| 句式优化 | 使用更流畅的句式 | 被动→主动 |
| 信息密度 | 精炼冗余表达 | 删除重复内容 |
| 逻辑衔接 | 增强段落间过渡 | 添加过渡句 |

**提示词模板**:

```markdown
# 内容润色任务

## 原始内容
{original_content}

## 优化目标
- 提升专业性：使用标准术语
- 增强可读性：优化句式结构
- 保持简洁：删除冗余表达
- 强化逻辑：增加过渡连接

## 风格要求
- 场景: {scenario}
- 受众: {audience}
- 语气: {tone}

## 输出格式
```json
{
  "polished": "润色后的内容",
  "changes": [
    {
      "original": "原文片段",
      "polished": "润色后片段",
      "reason": "修改原因"
    }
  ],
  "quality_score": 85
}
```

## 3. 结构重组建议 (Structure Suggestions)

**目标**: 基于金字塔原理提供内容结构优化建议

**适用框架**:
| 框架 | 适用场景 | 结构特点 |
|------|----------|----------|
| 金字塔 | 汇报/说服 | 结论先行，分层论证 |
| 叙事线 | 故事讲解 | 起承转合，情感曲线 |
| 流程式 | 操作培训 | 步骤分解，循序渐进 |
| 对比式 | 方案对比 | 双列对比，突出差异 |
| 问题解决 | 方案汇报 | 问题→分析→方案→收益 |

**提示词模板**:

```markdown
# 结构重组建议任务

## 当前内容结构
{current_structure}

## 目标框架
{preferred_framework}

## 分析维度
1. 信息分组是否合理
2. 逻辑顺序是否顺畅
3. 重点是否突出
4. 受众是否容易理解

## 输出格式
```json
{
  "current_assessment": {
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["问题1", "问题2"]
  },
  "suggestions": [
    {
      "type": "reorder|merge|split|add|remove",
      "from": "当前位置",
      "to": "建议位置",
      "reason": "原因说明"
    }
  ],
  "recommended_structure": [
    {
      "section": "章节标题",
      "content_summary": "内容摘要",
      "purpose": "本节目的"
    }
  ],
  "confidence_score": 85
}
```

## 4. 信息密度评估 (Density Evaluation)

**目标**: 评估每页信息密度，提供精简建议

**评估标准**:
| 密度等级 | 每页要点 | 适用场景 |
|----------|----------|----------|
| 极简 | 1-2点 | 演讲高潮、重点强调 |
| 适中 | 3-4点 | 常规演示 |
| 密集 | 5-7点 | 报告、资料 |
| 超密 | 8+点 | 详细参考材料 |

**提示词模板**:

```markdown
# 信息密度评估任务

## 待评估内容
{page_content}

## 评估维度
1. 每页信息量是否适合展示
2. 视觉重量是否均衡
3. 重点是否被稀释
4. 是否有信息过载风险

## 输出格式
```json
{
  "density_level": "适中",
  "current_item_count": 5,
  "recommended_item_count": 3,
  "suggestions": [
    {
      "action": "保留|精简|拆分",
      "item": "具体内容",
      "reason": "原因"
    }
  ],
  "density_score": 70
}
```

## 5. 重点突出建议 (Emphasis Suggestions)

**目标**: 识别关键信息，建议突出方式

**突出方式**:
| 方式 | 说明 | 适用场景 |
|------|------|----------|
| 数据高亮 | 数字放大/颜色强调 | 核心指标 |
| 对比强调 | 前后对比/竞品对比 | 效果展示 |
| 重复强调 | 标题/首尾呼应 | 核心观点 |
| 视觉引导 | 箭头/图标/留白 | 重点指向 |

**提示词模板**:

```markdown
# 重点突出建议任务

## 内容分析
{content}

## 识别重点
请识别以下类型的重点：
1. 核心数据（KPI、增长率、关键指标）
2. 核心观点（主要结论、核心建议）
3. 差异化亮点（竞争优势、独特价值）
4. 情感触发点（痛点、期望、共鸣）

## 输出格式
```json
{
  "key_points": [
    {
      "content": "重点内容",
      "type": "data|opinion|differentiation|emotional",
      "emphasis_suggestion": "强调方式建议",
      "visual_suggestion": "视觉呈现建议"
    }
  ],
  "emphasis_hierarchy": ["第一重点", "第二重点", "..."]
}
```

## 集成指南

### 在 Strategist 中的使用

```python
# 伪代码示例
async def optimize_content(source_content, optimization_options):
    results = {
        "titles": await optimize_titles(source_content.titles),
        "polished_content": await polish_content(source_content.body),
        "structure": await suggest_structure(source_content),
        "density": await evaluate_density(source_content.pages),
        "emphasis": await suggest_emphasis(source_content)
    }

    # 汇总优化建议
    summary = aggregate_optimization(results)

    return OptimizationResult(
        optimized_titles=results["titles"],
        polished_content=results["polished_content"],
        structure_suggestions=results["structure"],
        density_advice=results["density"],
        emphasis_guide=results["emphasis"],
        summary=summary
    )
```

### 优化强度控制

| 场景 | 优化强度 | 说明 |
|------|----------|------|
| 用户未指定 | 轻度 | 仅润色，不改变结构 |
| 用户要求优化 | 中度 | 标题+内容+结构建议 |
| 用户要求重构 | 深度 | 完整结构重组 |

### 约束规则

1. **事实保护**: 不得修改数据、日期、专有名词
2. **风格一致**: 优化后保持原有风格基调
3. **可逆性**: 所有优化建议用户可选择采纳或拒绝
4. **透明性**: 说明每个优化的原因

## 输出集成

优化结果将体现在：
- `design_spec.md` §IX Content Outline（优化后的标题和结构）
- 演讲备注中的优化说明
- 视觉设计的重点标注

---

**版本**: 1.0
**更新日期**: 2026-08-20
