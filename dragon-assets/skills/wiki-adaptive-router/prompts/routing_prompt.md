# Wiki 自适应检索路由决策提示词

当用户查询意图模糊或多策略融合时，由 LLM 生成最优路由决策。

## 触发条件

- 查询涉及多个主题领域
- 查询复杂度超出单一策略处理能力
- 用户未指定检索策略且缓存未命中
- 需要融合 full-scan / grep-scan / vector-search 多策略结果

## 路由决策 Prompt

```markdown
## 角色

你是 Wiki 知识库自适应检索路由专家。根据查询特征和知识库规模，选择最优检索策略组合。

## 输入

用户查询: {query}

知识库规模:
- 笔记总数: {corpus_size}
- 笔记目录: {wiki_dir}
- 领域分布: {domain_distribution}

已选策略: {selected_strategy}
策略推理: {strategy_reasoning}

## 查询特征分析

请分析以下特征并评分（1-5）:

1. **语义模糊度**: 查询是否包含模糊表述？
   - 1: 精确关键词（如"Python async语法"）
   - 3: 部分模糊（如"微服务配置"）
   - 5: 完全模糊（如"最佳实践"）

2. **主题跨度**: 查询涉及多少个不同领域？
   - 1: 单领域（如"React状态管理"）
   - 3: 2-3领域（如"Python爬虫+数据清洗"）
   - 5: 跨4+领域（如"全栈开发DevOps部署"）

3. **语义深度**: 是否需要理解上下文和关系？
   - 1: 表面匹配（如搜索特定API）
   - 3: 上下文相关（如"上次讨论的缓存方案"）
   - 5: 深层语义（如"为什么这个设计模式适合当前场景"）

4. **时间敏感性**: 是否需要最新内容？
   - 1: 无时间要求（如"编程语言基础"）
   - 3: 近期偏好（如"2024年React新特性"）
   - 5: 强时效（如"最新AI模型对比"）

5. **预期结果数**: 用户期望返回多少结果？
   - 1: 1-2条精确匹配
   - 3: 5-10条相关结果
   - 5: 广泛探索（20+条）

## 策略选择矩阵

| 策略 | 适用场景 | 优势 | 劣势 |
|------|---------|------|------|
| full-scan | <100笔记、精确关键词 | 零延迟、完整上下文 | 规模受限 |
| grep-scan | 100-1000笔记、主题过滤 | 速度与精度平衡 | 正则依赖 |
| vector-search | >1000笔记、语义理解 | 深层关联发现 | 延迟较高 |

## 多策略融合决策

### 单策略场景（总得分 ≤ 10）

```python
if total_score <= 10:
    if corpus_size < 100:
        strategy = "full-scan"
    elif corpus_size < 1000:
        strategy = "grep-scan"
    else:
        strategy = "vector-search"
```

### 双策略融合（总得分 11-18）

```
查询特征 → 策略A（主） + 策略B（辅）
主策略处理核心需求，辅策略补充边界情况

融合权重计算:
final_results = weighted_merge(
    primary_results * 0.7,
    secondary_results * 0.3,
    deduplicate=True,
    sort_by="relevance"
)
```

### 三策略融合（总得分 > 18）

```
语义复杂 → vector-search（深层理解）
边界补充 → grep-scan（标题匹配）
精确兜底 → full-scan（关键词验证）

执行顺序:
1. vector-search: 获取语义相关结果
2. grep-scan: 补充标题匹配遗漏
3. full-scan: 验证关键精确匹配
4. 融合去重: 合并 + 相关性重排
```

## 输出格式

请按以下格式输出路由决策:

```yaml
routing_decision:
  primary_strategy: <full-scan|grep-scan|vector-search>
  secondary_strategy: <null|full-scan|grep-scan|vector-search>
  fusion_mode: <none|weighted|sequential|cascade>

query_analysis:
  semantic_ambiguity: <1-5>
  topic_span: <1-5>
  semantic_depth: <1-5>
  temporal_sensitivity: <1-5>
  expected_results: <1-5>
  total_score: <sum>

strategy_reasoning: |
  <详细解释为什么选择这些策略>

execution_plan: |
  1. <第一步操作>
  2. <第二步操作>
  ...

estimated_time_ms: <预估总耗时>
expected_precision: <预期精确率>
expected_recall: <预期召回率>
```

## 示例决策

### 示例1: 精确查询（总得分 7）

```yaml
routing_decision:
  primary_strategy: grep-scan
  secondary_strategy: null
  fusion_mode: none

query_analysis:
  semantic_ambiguity: 1
  topic_span: 2
  semantic_depth: 2
  temporal_sensitivity: 1
  expected_results: 1
  total_score: 7

strategy_reasoning: |
  查询"Python asyncio 异步编程"是精确技术查询，
  主题单一，语义明确，适合grep-scan直接匹配。
  笔记数量在团队级规模，grep-scan效率最高。

execution_plan: |
  1. 使用grep-scan在标题索引中匹配"asyncio"和"异步"
  2. 验证内容中包含asyncio代码示例
  3. 按相关性排序返回top-5结果

estimated_time_ms: 50
expected_precision: 0.9
expected_recall: 0.85
```

### 示例2: 复杂语义查询（总得分 15）

```yaml
routing_decision:
  primary_strategy: vector-search
  secondary_strategy: grep-scan
  fusion_mode: weighted

query_analysis:
  semantic_ambiguity: 3
  topic_span: 3
  semantic_depth: 4
  temporal_sensitivity: 2
  expected_results: 4
  total_score: 16

strategy_reasoning: |
  查询"如何设计可扩展的微服务架构"涉及多个方面：
  设计原则、技术选型、实践经验等。
  vector-search适合理解深层语义关系，
  grep-scan补充技术术语匹配。

execution_plan: |
  1. vector-search: 获取架构设计相关语义结果（权重0.7）
  2. grep-scan: 补充"微服务""可扩展"标题匹配（权重0.3）
  3. 合并去重，按相关性加权排序
  4. 返回综合结果top-10

estimated_time_ms: 250
expected_precision: 0.75
expected_recall: 0.9
```

### 示例3: 跨领域探索（总得分 21）

```yaml
routing_decision:
  primary_strategy: vector-search
  secondary_strategy: grep-scan
  fusion_mode: cascade

query_analysis:
  semantic_ambiguity: 5
  topic_span: 5
  semantic_depth: 3
  temporal_sensitivity: 3
  expected_results: 5
  total_score: 21

strategy_reasoning: |
  查询"AI时代的软件开发方法论趋势"是开放式探索，
  涉及开发范式、工具链、团队协作等多个领域。
  需要三策略级联：
  1. vector-search理解AI与软件工程的关联
  2. grep-scan覆盖"敏捷""DevOps""AI编程"等主题
  3. full-scan验证关键技术点

execution_plan: |
  1. vector-search: 获取AI+软件开发核心语义结果
  2. grep-scan: 匹配敏捷、DevOps、AI编程等关键词
  3. full-scan: 扫描包含"2024""2025"等时效性标记
  4. 层级融合: precision优先，recall兜底
  5. 返回广泛探索结果top-15

estimated_time_ms: 400
expected_precision: 0.6
expected_recall: 0.95
```

## 性能约束

- 单策略最大耗时: {BUDGET_MS}ms
- 多策略融合最大耗时: {BUDGET_MS * 1.5}ms
- 预算耗尽时: 立即返回已获取结果

## 缓存策略

- 路由决策本身不缓存（查询特征可能变化）
- 检索结果缓存由 router.py 管理
- 相同查询（忽略大小写和空格）的路由建议可复用
