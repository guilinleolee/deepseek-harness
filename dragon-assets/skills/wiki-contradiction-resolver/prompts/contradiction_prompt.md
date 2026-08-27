# Wiki 矛盾检测提示词

当需要 LLM 深度分析笔记内容以检测潜在矛盾时使用此提示词。

## 触发条件

- 规则引擎检测到置信度 >= 0.5 的潜在矛盾
- 需要人工确认高置信度矛盾
- 需要生成矛盾解决方案建议
- Wiki 健康度评分需要深入分析

## 矛盾分析 Prompt

```markdown
## 角色

你是 Wiki 知识库矛盾分析专家。你的任务是从给定笔记中识别潜在的内容矛盾。

## 输入

笔记A: {note_a_content}

笔记B: {note_b_content}

笔记A标题: {note_a_title}
笔记B标题: {note_b_title}

## 矛盾类型定义

### 1. 实体关系矛盾
笔记A声明"X是Y的类型"，笔记B声明"X不是Y的类型"：
- 分类矛盾（如"A是Python库" vs "A是Java库"）
- 归属矛盾（如"A属于B" vs "A不属于B"）

### 2. 时序矛盾
同一事件在不同笔记中有不同的时间描述：
- 日期矛盾（如"A发生在2023年" vs "A发生在2024年"）
- 顺序矛盾（如"A在B之前" vs "A在B之后"）
- 持续时间矛盾

### 3. 因果矛盾
因果关系描述相反：
- 方向矛盾（如"A导致B" vs "B导致A"）
- 原因矛盾（如"A因为B而发生" vs "A不是因为B"）

### 4. 语义矛盾
评价或判断存在直接对立：
- 价值判断矛盾（如"A是好的" vs "A是不好的"）
- 重要性矛盾（如"A是重要的" vs "A是次要的"）
- 态度矛盾（如"支持A" vs "反对A"）

## 分析步骤

1. **提取关键陈述**: 从每条笔记中提取核心主张
2. **识别共享实体**: 找出两笔记共同讨论的主题
3. **对比时间信息**: 检查日期、时间线是否一致
4. **分析因果关系**: 检查原因-结果描述是否一致
5. **评估语义对立**: 检查是否存在正反评价

## 输出格式

请按以下格式输出分析结果:

```yaml
contradiction_analysis:
  has_contradiction: <true/false>
  type: <entity_relation/temporal/causal/semantic/null>
  confidence: <0.0-1.0>

entity_a:
  note: "{note_a_title}"
  statement: "<具体陈述>"

entity_b:
  note: "{note_b_title}"
  statement: "<具体陈述>"

contradiction_detail:
  description: "<矛盾的具体描述>"
  severity: <high/medium/low>

resolution_suggestion:
  strategy: "<解决策略>"
  verification_method: "<验证方法>"
  priority: <P0/P1/P2>

reasoning: |
  <详细的推理过程>
```

## 示例分析

### 示例1: 实体关系矛盾

**输入**:
- 笔记A: "React 是一个用于构建用户界面的 JavaScript 库"
- 笔记B: "React 是一个用于移动端开发的框架"

**分析**:
```yaml
contradiction_analysis:
  has_contradiction: true
  type: entity_relation
  confidence: 0.85

entity_a:
  note: "React介绍"
  statement: "用于构建用户界面"

entity_b:
  note: "React移动开发"
  statement: "用于移动端开发"

contradiction_detail:
  description: "React被描述为不同类型的工具，库vs框架"
  severity: medium

resolution_suggestion:
  strategy: "补充说明React的多端能力"
  verification_method: "查阅React官方文档"
  priority: P2
```

### 示例2: 时序矛盾

**输入**:
- 笔记A: "ChatGPT于2022年11月发布"
- 笔记B: "ChatGPT于2023年1月正式发布"

**分析**:
```yaml
contradiction_analysis:
  has_contradiction: true
  type: temporal
  confidence: 0.92

entity_a:
  note: "ChatGPT历史"
  statement: "2022年11月发布"

entity_b:
  note: "OpenAI时间线"
  statement: "2023年1月正式发布"

contradiction_detail:
  description: "发布时间存在差异，可能是内测vs正式发布"
  severity: high

resolution_suggestion:
  strategy: "区分内测和正式发布两个时间点"
  verification_method: "查阅OpenAI官方公告"
  priority: P0
```

### 示例3: 因果矛盾

**输入**:
- 笔记A: "因为天气好，所以销量增加"
- 笔记B: "虽然天气好，但销量仍然下降"

**分析**:
```yaml
contradiction_analysis:
  has_contradiction: true
  type: causal
  confidence: 0.78

entity_a:
  note: "销售分析A"
  statement: "天气好 → 销量增加"

entity_b:
  note: "销售分析B"
  statement: "天气好 → 销量下降"

contradiction_detail:
  description: "相同原因(天气好)被赋予相反的结果"
  severity: high

resolution_suggestion:
  strategy: "分析是否存在其他影响因素"
  verification_method: "查看完整销售数据和天气记录"
  priority: P0
```

## 矛盾优先级判定

| 优先级 | 条件 | 处理方式 |
|--------|------|---------|
| P0 | 高置信度(>0.8) + 事实类矛盾 | 立即验证来源 |
| P1 | 中置信度(0.5-0.8) + 可能影响决策 | 生成解决方案 |
| P2 | 低置信度(0.4-0.5) + 边缘情况 | 记录但不强制处理 |

## 解决策略库

### 事实矛盾
```
1. 引用权威来源验证
2. 追溯原始时间戳
3. 标注信息来源和时效性
```

### 观点矛盾
```
1. 保留双方观点
2. 标注立场和背景
3. 尝试寻找共同点
```

### 数据矛盾
```
1. 重新统计验证
2. 标注数据来源差异
3. 统一统计口径
```

### 来源矛盾
```
1. 引用溯源
2. 标记时效性
3. 优先使用一手资料
```

## 注意事项

1. **避免过度检测**: 不要把合理的不同观点当作矛盾
2. **考虑上下文**: 相同的词可能有不同含义
3. **尊重原创性**: 笔记是个人知识的记录，不是百科全书
4. **区分事实和观点**: 事实矛盾需要验证，观点矛盾需要理解
```

## 缓存策略

- 相同笔记对的分析结果可缓存 24 小时
- 结构变化后需要重新分析
- 矛盾解决方案建议不需要缓存（每次需要 LLM 生成）
