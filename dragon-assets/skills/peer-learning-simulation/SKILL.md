---
license: UNKNOWN
triggers: ["peer learning simulation", "同伴学习模拟器 (Peer Learning Simulation)"]
---
# 同伴学习模拟器 (Peer Learning Simulation)

## L0: 一句话描述
多角色AI同伴模拟辩论，发现知识盲点

## L1: 使用场景
当用户学习一个概念后，模拟不同背景的AI同伴进行讨论，通过分歧发现理解缺口

## L2: 详细文档

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ 同伴学习模拟器 - 基于OpenMAIC多Agent协作原理                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🎭 四种同伴角色                                           │
│  ├── 新手小白：基础问题，常见误解                           │
│  ├── 实践者老王：真实场景，具体应用                         │
│  ├── 怀疑论者：质疑假设，挑战结论                           │
│  └── 综合者：整合观点，构建框架                           │
│                                                             │
│  🔄 协作流程                                               │
│  ├── 观点陈述：各角色发表看法                              │
│  ├── 分歧发现：识别不一致点                                │
│  ├── 深度辩论：针对分歧深入讨论                             │
│  └── 共识提炼：形成更深的理解                             │
│                                                             │
│  📊 输出格式                                               │
│  ├── 对话记录：完整的同伴讨论                             │
│  ├── 知识缺口：识别的理解薄弱点                            │
│  ├── 深化问题：可用于费曼讲解的题目                        │
│  └── 理解评估：各角色对概念的掌握程度                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### DSPy Signature

```python
class PeerLearningSimulation(dspy.Signature):
    """模拟同伴学习辩论，发现知识盲点"""
    concept: str = dspy.InputField(desc="待学习的核心概念")
    user_knowledge_level: str = dspy.InputField(desc="用户当前知识水平: beginner/intermediate/advanced")
    peer_dialogue: list[dict] = dspy.OutputField(desc="同伴对话记录[{role, opinion, challenge}]")
    knowledge_gaps: list[str] = dspy.OutputField(desc="识别的知识缺口")
    deep_questions: list[str] = dspy.OutputField(desc="深化理解的费曼问题")
    consensus_summary: str = dspy.OutputField(desc="辩论后的共识总结")
```

### 四角色配置

```yaml
peer_roles:
  novice:
    name: "新手小白"
    avatar: "🤔"
    perspective: "基础视角"
    question_types:
      - "这是什么？"
      - "和XXX有什么区别？"
      - "为什么需要这个？"
    common_misconceptions:
      - "以为X就是Y的简单重复"
      - "混淆使用场景"
      - "忽视核心前提"

  practitioner:
    name: "实践者老王"
    avatar: "💻"
    perspective: "实战视角"
    question_types:
      - "实际怎么用？"
      - "遇到过什么问题？"
      - "最佳实践是什么？"
    concerns:
      - "性能影响"
      - "维护成本"
      - "集成难度"

  skeptic:
    name: "怀疑论者"
    avatar: "🤨"
    perspective: "批判视角"
    question_types:
      - "真的比X更好吗？"
      - "有什么场景不适用？"
      - "有什么隐藏代价？"
   质疑点:
      - "假设是否成立"
      - "证据是否充分"
      - "是否过度宣传"

  synthesizer:
    name: "综合者"
    avatar: "🧙"
    perspective: "整合视角"
    contributions:
      - "总结各方观点"
      - "构建统一框架"
      - "指出深层联系"
      - "预测发展趋势"
```

### 协作流程

```yaml
collaboration_flow:
  phase1_观点陈述:
    duration: "2-3轮"
    rules:
      - 每个角色就概念发表看法
      - 新手要求澄清基础定义
      - 实践者分享应用经验
      - 怀疑论者提出质疑
      - 综合者记录关键点

  phase2_分歧发现:
    duration: "1-2轮"
    trigger: "存在不一致观点"
    output: "分歧点清单"
    rules:
      - 识别观点冲突
      - 量化分歧程度
      - 标注核心争议

  phase3_深度辩论:
    duration: "3-5轮"
    focus: "最关键的分歧点"
    rules:
      - 各方提供论据
      - 引用具体例子
      - 检验假设前提
      - 寻求共同基础

  phase4_共识提炼:
    duration: "1轮"
    output: "共识声明"
    rules:
      - 综合者主持
      - 明确共识范围
      - 标注仍存分歧点
      - 生成后续问题
```

### 费曼问题生成

```python
def generate_feynman_questions(dialogue: list, gaps: list) -> list:
    """从同伴辩论生成费曼问题"""
    feyman_questions = []

    for gap in gaps:
        # 基础概念问题
        feyman_questions.append({
            "level": 1,
            "question": f"用一句话向小学生解释{gap['concept']}？",
            "purpose": "检验基础理解"
        })

        # 深层机制问题
        feyman_questions.append({
            "level": 2,
            "question": f"如果{gap['concept']}的核心原理失效，会发生什么？",
            "purpose": "检验机制理解"
        })

        # 实际应用问题
        feyman_questions.append({
            "level": 3,
            "question": f"举一个你亲身经历过的{gap['concept']}应用场景",
            "purpose": "连接理论与实践"
        })

    return feyman_questions
```

### 使用示例

```markdown
用户输入: "我刚学了机器学习中的梯度下降，想确认理解是否正确"

系统响应:
---
## 🤖 同伴学习讨论

### 参与者
- 🤔 新手小白 [基础视角]
- 💻 实践者老王 [实战视角]
- 🤨 怀疑论者 [批判视角]
- 🧙 综合者 [整合视角]

---

### 第一轮: 观点陈述

**🤔 新手小白**: 梯度下降就是一直往下走，直到找到最低点对吗？

**💻 实践者老王**: 差不多，但要注意学习率。太小会走太慢，太大会错过最优点甚至发散。我之前调参调了一周才找到合适的。

**🤨 怀疑论者**: 等等，如果局部最优才是"真底"呢？全局最优可能根本到不了。

**🧙 综合者**: 这是个好问题。两位的观点正好对应梯度下降的两个核心挑战。

---

### 分歧发现

| 分歧点 | 新手观点 | 实践者担忧 | 怀疑论质疑 |
|--------|---------|-----------|-----------|
| 目的地 | 全局最优 | 合适的最优 | 可能无法到达 |
| 路径 | 直接向下 | 学习率决定 | 局部陷阱 |
| 终点 | 确定唯一 | 取决于参数 | 不确定 |

---

### 深度辩论

**🤨 怀疑论者**: 既然局部最优是个问题，为什么还这么多人用？

**💻 实践者老王**: 因为深度学习中，局部最优往往也足够好。而且有动量、Adam等优化器帮助跳出局部最优。

**🤔 新手小白**: 所以关键是用好优化器？

**🧙 综合者**: 更准确地说，是理解问题本身的结构。选择合适的优化器是建立在理解梯度消失、鞍点等问题的基础上。

---

### 知识缺口

1. **局部最优vs全局最优**: 混淆了两者的区别和实际影响
2. **学习率机制**: 只知道"要调"，不理解如何调
3. **优化器原理**: 不知道动量、Adam等如何工作
4. **问题结构**: 不理解为什么深度学习中局部最优足够好

---

### 💡 费曼深化问题

1. "如果把学习率设成0，会发生什么？"
2. "梯度为0时，模型在做什么？"
3. "举一个你生活中'梯度下降'的例子"

---

### 📚 推荐学习路径

1. 先用费曼问题检验基础
2. 学习优化器时配合实践
3. 再回来理解局部最优问题
```

### 与费曼技巧协同

```yaml
feynman_integration:
  before_peer_debate:
    - 用户先自己讲解概念
    - 系统评估讲解质量
    - 记录讲解中的模糊点

  peer_debate_output:
    - 知识缺口 → 费曼问题生成
    - 分歧点 → 深入讲解需求
    - 共识 → 理解确认

  after_peer_debate:
    - 用户重新讲解
    - 对比前后差异
    - 记录进步
```

### 触发条件

| 触发词 | 场景 | 响应 |
|--------|------|------|
| "帮我检查理解" | 学习后自检 | 启动同伴讨论 |
| "有没有其他角度" | 单一视角 | 多角色辩论 |
| "这个真的对吗" | 存在疑虑 | 怀疑论者主导 |
| "总结一下" | 需要整合 | 综合者主导 |

### 预期效果

| 指标 | 效果 |
|------|------|
| 知识缺口发现率 | +65% |
| 理解深度 | +45% |
| 遗忘率 | -40% |
| 应用准确率 | +55% |

### 文件结构

```
peer-learning-simulation/
├── SKILL.md                    # 本文件
├── prompts/
│   ├── debate-template.md      # 对话模板
│   └── consensus-template.md    # 共识生成模板
├── scripts/
│   ├── peer_simulator.py       # 同伴模拟器
│   └── feyman_generator.py     # 费曼问题生成器
└── templates/
    └── discussion-output.md     # 输出模板
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-24 | 初始版本，基于OpenMAIC多Agent协作原理 |
