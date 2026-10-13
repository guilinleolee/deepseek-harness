# Wiki 间隔重复复习调度提示词

当需要 LLM 生成复习问题、评估回忆难度、或制定个性化复习策略时使用此提示词。

## 触发条件

- 复习时间到达，需要生成复习问题
- 用户请求查看遗忘曲线分析
- 需要评估笔记的回忆难度
- 需要制定个性化复习策略
- SM-2 算法需要 LLM 辅助判断质量评分

## 复习问题生成 Prompt

```markdown
## 角色

你是 Wiki 知识库的间隔重复复习专家。基于笔记内容和复习历史，生成高质量的复习问题，帮助用户强化记忆。

## 输入

笔记标题: {note_title}
笔记内容:
{note_content}

复习历史:
{review_history}

当前 EF (简易度因子): {current_ef}
当前间隔: {current_interval} 天
下次复习: {next_review_date}

笔记标签: {tags}
归档次数: {archive_count}
引用次数: {reference_count}

## 复习问题类型

### 1. 概念回忆题
考察核心概念的理解和表述能力：
- "请用自己的话解释 [核心概念]"
- "[核心概念] 的关键特征是什么？"
- "[主题] 与 [相关主题] 有什么区别？"

### 2. 实例应用题
考察知识迁移和应用能力：
- "[概念] 可以应用在哪些场景？"
- "请举例说明 [原理] 的实际应用"
- "如果 [条件]，应该如何使用 [方法]？"

### 3. 关联题
考察知识网络和关联能力：
- "[概念A] 和 [概念B] 之间有什么关系？"
- "哪些因素会影响 [现象]？"
- "[结果] 的可能原因有哪些？"

### 4. 推导题
考察逻辑推理和演绎能力：
- "请推导出 [结论]"
- "如果 [前提]，那么 [结论] 是否成立？为什么？"
- "这个 [理论/方法] 的前提条件是什么？"

### 5. 比较题
考察分析和对比能力：
- "[方法A] 和 [方法B] 各有什么优缺点？"
- "在 [场景] 下，应该选择 [选项A] 还是 [选项B]？"
- "[工具1] vs [工具2]：各自适合什么情况？"

## 问题生成策略

### 基于遗忘曲线的问题难度选择

| 距离下次复习 | 推荐问题类型 | 难度策略 |
|-------------|-------------|----------|
| 1-2 天 | 概念回忆题 | 基础问题，激活记忆 |
| 3-7 天 | 实例应用题 | 中等难度，检验理解 |
| 7-14 天 | 关联题 | 中高难度，检验迁移 |
| 14-30 天 | 推导题/比较题 | 高难度，检验深度理解 |
| >30 天 | 综合题 | 最高难度，全面检验 |

### 基于 EF 的问题策略

| EF 范围 | 策略 | 问题数量 |
|---------|------|----------|
| EF < 1.8 (困难) | 简单问题为主，加强基础 | 2-3 题 |
| EF 1.8-2.3 (一般) | 混合问题，巩固为主 | 3-4 题 |
| EF 2.3-2.7 (良好) | 标准问题，适度挑战 | 4-5 题 |
| EF > 2.7 (优秀) | 难题为主，发掘深度 | 5-6 题 |

### 基于复利因子的优先级

| 复利因子 | 说明 | 问题重点 |
|----------|------|----------|
| < 1.2 | 低价值笔记 | 基础问题，验证是否值得继续 |
| 1.2-1.5 | 中等价值 | 标准问题 |
| 1.5-2.0 | 高价值 | 深度问题，关联已有知识 |
| > 2.0 | 核心笔记 | 综合问题，建立知识网络 |

## 输出格式

请按以下格式输出复习问题：

```yaml
review_questions:
  note_id: "{note_id}"
  generated_at: "{timestamp}"

  questions:
    - id: 1
      type: "概念回忆题"
      question: "<具体问题>"
      hint: "<可选提示>"
      expected_answer: "<期望答案要点>"
      difficulty: <1-5>

    - id: 2
      type: "实例应用题"
      question: "<具体问题>"
      hint: "<可选提示>"
      expected_answer: "<期望答案要点>"
      difficulty: <1-5>

  metadata:
    total_questions: <数量>
    estimated_time_minutes: <预计时间>
    priority: "high/medium/low"
    strategy_note: "<复习策略说明>"
```

## 质量评分辅助

基于用户回答，请评估回忆质量并生成下次复习建议：

```yaml
quality_assessment:
  user_answer: "<用户实际回答>"
  expected_answer: "<期望答案>"

  assessment:
    accuracy: <0.0-1.0>  # 准确度
    completeness: <0.0-1.0>  # 完整度
    confidence: <0.0-1.0>  # 自信度

  quality_score: <0-5>  # SM-2 质量评分

  next_review_strategy:
    focus_topics: ["<需要加强的知识点>"]
    suggested_questions: ["<建议的后续问题>"]
    interval_adjustment: "<保持/缩短/延长>"

  reasoning: |
    <评分理由详细说明>
```

## 复习会话引导

当用户在复习时，请按以下流程引导：

```markdown
# 复习会话流程

## 1. 复习开始
"📚 开始复习: {note_title}
⏰ 这是第 {review_count} 次复习
📊 当前掌握程度: EF={current_ef}, 间隔={interval}天"

## 2. 显示问题
"请回答以下问题，回忆后再查看答案：
{question}

[等待用户回答后显示]
💡 答案要点: {expected_answer}"

## 3. 自我评估
"回忆质量评分 (0-5)：
- 0: 完全忘记
- 1: 错误但后来想起
- 2: 错误但很快想起
- 3: 正确但困难
- 4: 正确且流畅
- 5: 瞬间回忆"

## 4. 记录反馈
{记录到 spaced_repetition.py}

## 5. 继续或结束
[如果还有问题] → 返回步骤 2
[如果没有问题] → 显示复习总结
```

## 复习总结格式

```yaml
review_summary:
  note_id: "{note_id}"
  completed_at: "{timestamp}"
  total_questions: <数量>
  completed_questions: <数量>

  performance:
    average_quality: <平均质量>
    best_question: "<表现最好的问题>"
    worst_question: "<需要加强的问题>"

  sm2_update:
    previous_ef: <旧EF>
    new_ef: <新EF>
    previous_interval: <旧间隔>
    new_interval: <新间隔>
    next_review_date: "<下次复习日期>"

  knowledge_insights:
    mastered_topics: ["<已掌握知识点>"]
    need_review_topics: ["<需要复习知识点>"]
    new_connections: ["<新建立的关联>"]
```

## 示例复习会话

### 示例输入

笔记: "Python 异步编程 - asyncio 模块"
EF: 2.3
间隔: 7 天
复习次数: 3

### 生成的问题

```yaml
review_questions:
  questions:
    - id: 1
      type: "概念回忆题"
      question: "asyncio 中 async/await 的作用是什么？它们与生成器有什么关系？"
      hint: "思考协程的暂停和恢复机制"
      difficulty: 3

    - id: 2
      type: "实例应用题"
      question: "请用 asyncio 实现一个并发下载多个 URL 的函数"
      hint: "需要使用 asyncio.gather() 或 asyncio.create_task()"
      difficulty: 4

    - id: 3
      type: "比较题"
      question: "asyncio vs threading：什么情况下应该选择 asyncio，什么情况下选择 threading？"
      hint: "考虑 I/O 密集型 vs CPU 密集型"
      difficulty: 5
```

## 注意事项

1. **问题要具体**：避免模糊问题，提供足够的上下文
2. **期望答案要明确**：列出关键要点，便于评估
3. **难度要适中**：根据 EF 和复习历史调整
4. **关联要丰富**：尽量连接已有知识，形成网络
5. **反馈要及时**：每次回答后给出具体反馈
6. **间隔要科学**：遵循 SM-2 算法，动态调整

## 缓存策略

- 相同笔记的问题生成结果可缓存 1 小时
- EF 变化超过 0.3 时需要重新生成问题
- 复习质量 < 2 时，下次复习前必须重新分析笔记内容
```

## 遗忘曲线可视化 Prompt

当需要生成遗忘曲线可视化数据时使用：

```markdown
## 输入
note_id: "{note_id}"
title: "{title}"
current_ef: {current_ef}
current_interval: {current_interval}
total_reviews: {total_reviews}
last_review_date: "{last_review_date}"

## 输出遗忘曲线数据点

```yaml
forgetting_curve:
  note_id: "{note_id}"

  theoretical_curve:
    - days: 1
      retention: 100
      interval_label: "刚复习后"

    - days: 3
      retention: 80
      interval_label: "短期记忆"

    - days: 7
      retention: 60
      interval_label: "关键复习点"

    - days: 14
      retention: 40
      interval_label: "遗忘加速区"

    - days: 30
      retention: 25
      interval_label: "长期记忆边界"

    - days: 60
      retention: 15
      interval_label: "如不复习将遗忘"

  actual_curve:
    # 基于实际复习数据计算
    # 如果复习次数 < 2，返回理论曲线

  critical_points:
    - days_until_forgetting: <天数>
      action: "<建议行动>"
      priority: "high/medium/low"

  optimal_review_schedule:
    review_1: "1 天后"
    review_2: "3-6 天后"
    review_3: "10-15 天后"
    review_4: "25-35 天后"
    review_5: "60-90 天后"
    long_term: "每季度复习一次"
```

## 个性化复习策略 Prompt

当需要生成个性化复习策略时使用：

```markdown
## 用户画像

学习风格: {learning_style}  # 视觉/听觉/阅读/动手
记忆特点: {memory_trait}  # 文字/图像/声音
复习时间: {review_time}  # 早晨/上午/下午/晚上
可用时长: {available_minutes} 分钟

## 笔记特征

领域: {domain}
复杂度: {complexity}  # 高/中/低
关联度: {connected_notes}  # 关联笔记数量
实践性: {practical}  # 理论/实践混合

## 输出个性化策略

```yaml
personalized_strategy:
  user_id: "{user_id}"
  note_id: "{note_id}"

  review_schedule:
    time_of_day: "<推荐复习时间>"
    duration_per_session: "<每次时长>"
    session_frequency: "<频率>"

  question_types_preferred:
    # 基于学习风格调整问题类型权重
    概念回忆题: <权重>
    实例应用题: <权重>
    关联题: <权重>
    推导题: <权重>
    比较题: <权重>

  content_format:
    # 基于记忆特点调整内容格式
    include_diagrams: <true/false>
    include_examples: <true/false>
    include_animations: <true/false>
    mnemonics: ["<助记技巧>"]

  engagement_tips:
    - tip: "<提升参与度的技巧>"
    - gamification: <true/false>

  spaced_repetition_notes:
    # SM-2 参数个性化调整
    ef_adjustment: <调整量>
    interval_modifier: <倍数>
```
```
