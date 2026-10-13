---
license: UNKNOWN
triggers: ["quiz generator", "Quiz Generator - 智能测验生成"]
---
# Quiz Generator - 智能测验生成

## L0: 一句话 (≤15字)
从任意资料自动生成多类型练习题

## L1: 使用场景 (50-100字)

### 触发词
- 生成练习题 / 出几道题
- quiz / 测试 / 测验
- 检验学习效果 / 考考我

### 适用场景
- 学习后巩固练习
- 知识点掌握度检测
- 考前模拟训练
- 教学备课

### 不适用
- 需要详细讲解的场景（用学习师费曼）
- 已经会做的重复练习
- 开放性研究讨论

## L2: 详细文档

### 核心能力

```python
class QuizGenerator(dspy.Signature):
    """基于给定资料生成多类型练习题"""
    source_content: str = dspy.InputField(desc="学习资料或知识点")
    topic: str = dspy.InputField(desc="测验主题")
    difficulty: str = dspy.InputField(desc="难度: easy/medium/hard")
    num_questions: int = dspy.InputField(desc="题目数量", default=5)
    question_types: list = dspy.InputField(
        desc="题目类型: multiple_choice/short_answer/calculation/proof",
        default=["multiple_choice"]
    )

    questions: list = dspy.OutputField(desc="生成的题目列表")
    answers: list = dspy.OutputField(desc="答案列表")
    explanations: list = dspy.OutputField(desc="解析列表")
```

### 题目类型

| 类型 | 标识 | 说明 | 生成难度 |
|------|------|------|---------|
| **单选题** | `multiple_choice` | 4选项+正确答案 | ⭐ |
| **多选题** | `multiple_select` | 2+正确选项 | ⭐⭐ |
| **简答题** | `short_answer` | 开放性简答 | ⭐⭐ |
| **计算题** | `calculation` | 带计算步骤 | ⭐⭐⭐ |
| **证明题** | `proof` | 数学证明 | ⭐⭐⭐⭐ |
| **判断题** | `true_false` | 对错判断 | ⭐ |

### 生成规则

#### 单选题生成规则
```markdown
1. 选项A-D必须互斥，不能有重叠
2. 干扰项必须是"合理的错误答案"
3. 正确答案位置随机分布
4. 题目不能有歧义
5. 计算题答案唯一
```

#### 难度分级标准

| 难度 | 特征 | 示例 |
|------|------|------|
| **easy** | 单一概念、直接应用 | "梯度下降的公式是？" |
| **medium** | 多个概念、综合应用 | "用梯度下降求解y=x²的最小值" |
| **hard** | 深度理解、创新应用 | "设计一个梯度下降的变体解决鞍点问题" |

### 使用示例

```bash
# CLI生成
quiz-gen "反向传播" --topic 深度学习 --difficulty medium --num 5

# 交互式
quiz-gen interactive

# 导出格式
quiz-gen "transformer" --format json --output quiz.json
quiz-gen "transformer" --format anki --output quiz.apkg
```

### 输出格式

```json
{
  "quiz": {
    "topic": "反向传播算法",
    "difficulty": "medium",
    "created_at": "2026-04-07",
    "questions": [
      {
        "id": 1,
        "type": "multiple_choice",
        "question": "反向传播算法中，梯度从哪一层向前传播？",
        "options": {
          "A": "输出层 → 输入层",
          "B": "输入层 → 输出层",
          "C": "同时向两侧传播",
          "D": "随机传播"
        },
        "answer": "A",
        "explanation": "反向传播从输出层计算损失函数梯度，逐层向前传播直到输入层。"
      },
      {
        "id": 2,
        "type": "calculation",
        "question": "设loss = (y - ŷ)²，y=3, ŷ=1，求∂loss/∂ŷ",
        "answer": "-4",
        "steps": ["∂loss/∂ŷ = 2(y-ŷ)(-1) = 2(3-1)(-1) = -4"],
        "explanation": "链式法则：∂loss/∂ŷ = ∂loss/∂(y-ŷ) × ∂(y-ŷ)/∂ŷ"
      }
    ]
  }
}
```

### 与学习师集成

```yaml
学习师工作流:
  STEP 4 固化:
    - 生成练习题 → quiz-generator
    - 设置复习周期 → sm-2-tracker
    - 记录错题 →错题本
```

### 质量标准

1. **答案准确性**: 100% 正确
2. **选项合理性**: 干扰项不能太明显
3. **解析完整性**: 必须包含为什么选这个
4. **知识点覆盖**: 每道题对应明确知识点
5. **难度一致性**: 同难度题目耗时相近

### 自检清单

- [ ] 每道题有唯一正确答案
- [ ] 干扰项是常见错误
- [ ] 解析能帮助理解
- [ ] 知识点标注清晰
- [ ] 支持导出Anki格式
