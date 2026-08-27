---
license: UNKNOWN
triggers: ["curriculum auto designer", "自适应课程设计师 (Curriculum Auto-Designer)"]
---
# 自适应课程设计师 (Curriculum Auto-Designer)

## L0: 一句话描述
基于知识图谱自动生成个性化学习路径，动态调整难度和进度

## L1: 使用场景
当用户需要系统学习某个领域时，自动分析知识结构、评估用户水平、生成最优学习路径

## L2: 详细文档

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ 自适应课程设计师 - 基于知识图谱的智能课程生成                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🗺️ 知识图谱构建                                           │
│  ├── 概念节点：核心概念及属性                              │
│  ├── 依赖边：先修关系、学习顺序                            │
│  ├── 难度边：复杂度、抽象程度                             │
│  └── 应用边：使用场景、实战项目                           │
│                                                             │
│  🎯 路径规划算法                                           │
│  ├── 最短路径：最小学习量到达目标                         │
│  ├── 最优路径：平衡难度和效率                             │
│  ├── 稳健路径：冗余设计容错                               │
│  └── 探索路径：发现新领域                                 │
│                                                             │
│  🔄 动态调整                                               │
│  ├── 实时评估：学习效果监控                               │
│  ├── 难度调节：适应用户节奏                               │
│  ├── 路径重规划：遇到困难时调整                           │
│  └── 加速机制：快速掌握者跳级                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### DSPy Signature

```python
class CurriculumDesigner(dspy.Signature):
    """设计个性化学习路径"""
    topic: str = dspy.InputField(desc="用户想学习的领域/主题")
    user_level: str = dspy.InputField(desc="用户当前水平: beginner/intermediate/advanced")
    user_goals: list[str] = dspy.InputField(desc="学习目标列表")
    time_constraint: str = dspy.InputField(desc="时间约束: daily_time, total_weeks")
    curriculum: dict = dspy.OutputField(desc="完整课程设计")
    knowledge_graph: dict = dspy.OutputField(desc="该领域的知识图谱")
    assessment_plan: list[dict] = dspy.OutputField(desc="评估计划")
    milestones: list[dict] = dspy.OutputField(desc="关键里程碑")


class AdaptivePathPlanner(dspy.Signature):
    """动态调整学习路径"""
    current_progress: dict = dspy.InputField(desc="当前学习进度")
    assessment_results: list[dict] = dspy.InputField(desc="评估结果")
    difficulty_feedback: str = dspy.InputField(desc="用户反馈: too_easy/just_right/too_hard")
    adjusted_path: dict = dspy.OutputField(desc="调整后的学习路径")
    skip_recommendations: list[str] = dspy.OutputField(desc="建议跳过的已掌握内容")
    extra_practice: list[str] = dspy.OutputField(desc="建议加强的薄弱环节")
```

### 知识图谱结构

```yaml
knowledge_graph:
  nodes:
    - id: "concept_001"
      name: "基础概念"
      type: "prerequisite"
      difficulty: 1
      learning_time: 30  # minutes
      essential: true     # 必学
      tags: ["fundamentals", "required"]

    - id: "concept_002"
      name: "进阶概念"
      type: "core"
      difficulty: 3
      learning_time: 60
      essential: true
      prerequisites: ["concept_001"]
      tags: ["core", "important"]

    - id: "concept_003"
      name: "高级主题"
      type: "advanced"
      difficulty: 5
      learning_time: 120
      essential: false  # 可选
      prerequisites: ["concept_002"]
      tags: ["advanced", "optional"]

  edges:
    - from: "concept_001"
      to: "concept_002"
      type: "prerequisite"
      weight: 1.0

    - from: "concept_002"
      to: "concept_003"
      type: "prerequisite"
      weight: 0.8

    - from: "concept_001"
      to: "concept_003"
      type: "alternative"  # 可选路径
      weight: 0.3
```

### 路径规划算法

```python
class PathPlanner:
    """学习路径规划器"""

    def plan_path(self, topic, user_level, goals, constraints):
        # 1. 构建知识图谱
        kg = self.build_knowledge_graph(topic)

        # 2. 评估用户水平
        level_nodes = self.map_level_to_nodes(user_level, kg)

        # 3. 识别目标节点
        target_nodes = self.identify_targets(goals, kg)

        # 4. 计算最优路径
        # 支持多种策略
        if constraints.get("speed_priority"):
            path = self.dijkstra_shortest(kg, level_nodes, target_nodes)
        elif constraints.get("depth_priority"):
            path = self.deep_first(kg, level_nodes, target_nodes)
        elif constraints.get("balanced"):
            path = self.balanced_astar(kg, level_nodes, target_nodes)
        else:
            path = self.default_strategy(kg, level_nodes, target_nodes)

        # 5. 注入里程碑和评估点
        curriculum = self.inject_milestones(path, constraints)

        return curriculum

    def dijkstra_shortest(self, kg, start, targets):
        """最短路径 - 最小学习量"""
        # 优先选择最短路径
        # 适合时间紧迫的场景
        pass

    def deep_first(self, kg, start, targets):
        """深度优先 - 打牢基础"""
        # 先学透再前进
        # 适合需要扎实基础的场景
        pass

    def balanced_astar(self, kg, start, targets):
        """平衡A* - 难度平滑过渡"""
        # 考虑难度梯度
        # 适合稳步学习的场景
        pass
```

### 课程结构模板

```yaml
curriculum_structure:
  metadata:
    topic: "React进阶"
    target_level: "intermediate"
    total_duration: "8周"
    weekly_commitment: "10小时"

  phases:
    phase1_foundation:
      name: "夯实基础"
      duration: "2周"
      objectives:
        - "掌握React核心概念"
        - "理解虚拟DOM原理"
        - "熟练使用Hooks"
      modules:
        - id: "m1-1"
          name: "React核心回顾"
          type: "review"
          time: 5h
          activities:
            - "概念自测"
            - "费曼讲解练习"
          assessments:
            - "模块测验80%+"
            - "教学演示"

        - id: "m1-2"
          name: "Hooks深入理解"
          type: "core"
          time: 5h
          activities:
            - "useState源码分析"
            - "自定义Hooks开发"
          assessments:
            - "实现3个自定义Hooks"
            - "代码评审"

    phase2_practice:
      name: "实践应用"
      duration: "3周"
      objectives:
        - "独立完成中型项目"
        - "掌握状态管理方案"
        - "性能优化实战"
      modules:
        - id: "m2-1"
          name: "状态管理方案"
          type: "core"
          time: 8h
          activities:
            - "对比Redux/Zustand/Jotai"
            - "项目实战"
          assessments:
            - "项目集成评估"

    phase3_mastery:
      name: "精通进阶"
      duration: "3周"
      objectives:
        - "性能优化专家"
        - "测试覆盖率>80%"
        - "团队协作最佳实践"
      modules:
        - id: "m3-1"
          name: "性能优化"
          type: "advanced"
          time: 6h
          activities:
            - "Profiler分析"
            - "重渲染优化"
            - "代码分割"
```

### 动态调整机制

```python
class AdaptiveEngine:
    """自适应学习引擎"""

    def adjust_path(self, progress, assessments, feedback):
        adjustments = {
            "skip": [],      # 跳过的已掌握内容
            "add": [],       # 补充的薄弱环节
            "extend": [],    # 需要延长的模块
            "accelerate": [] # 可以加速的部分
        }

        for assessment in assessments:
            score = assessment["score"]
            module = assessment["module"]

            if score >= 90:
                # 优秀：检查是否可以加速后续内容
                adjustments["accelerate"].append(module)
                adjustments["skip"].extend(
                    self.find_easy_prerequisites(module)
                )

            elif score >= 70:
                # 良好：正常继续
                pass

            elif score >= 50:
                # 一般：补充练习
                adjustments["add"].extend(
                    self.find_practice_gaps(module)
                )

            else:
                # 不足：延长当前+回退检查
                adjustments["extend"].append(module)
                prerequisites = self.get_prerequisites(module)
                for prereq in prerequisites:
                    prereq_score = self.get_assessment_score(prereq)
                    if prereq_score < 80:
                        adjustments["add"].append(prereq)

        return self.replan_path(adjustments)
```

### 评估体系

```yaml
assessment_system:
  types:
    - type: "diagnostic"
      purpose: "入学评估"
      methods:
        - "概念自测题"
        - "知识图谱定位"
        - "学习历史分析"

    - type: "formative"
      purpose: "过程评估"
      frequency: "每个模块后"
      methods:
        - "快测(5题)"
        - "费曼讲解"
        - "同伴讨论"
        - "实战练习"

    - type: "summative"
      purpose: "阶段评估"
      frequency: "每阶段结束时"
      methods:
        - "项目实战"
        - "综合测验"
        - "教学演示"

    - type: "self_assessment"
      purpose: "自我评估"
      frequency: "每天"
      methods:
        - "学习日志"
        - "信心度打分"
        - "目标完成度"

  metrics:
    - name: "掌握度"
      calculation: "正确率 * 复杂度权重"
      thresholds:
        - mastered: 85
        - proficient: 70
        - developing: 50

    - name: "学习效率"
      calculation: "掌握内容 / 投入时间"
      benchmarks:
        - excellent: 2.0
        - good: 1.5
        - needs_improvement: 1.0
```

### 里程碑设置

```yaml
milestones:
  - id: "m1"
    name: "入门证书"
    check:
      - "完成基础阶段"
      - "所有评估>=70%"
      - "完成1个项目"
    reward:
      - "解锁进阶课程"
      - "同伴学习权限"

  - id: "m2"
    name: "实践者认证"
    check:
      - "完成实践阶段"
      - "项目评分>=85%"
      - "代码评审通过"
    reward:
      - "解锁高级主题"
      - "导师指导权限"

  - id: "m3"
    name: "专家认证"
    check:
      - "完成精通阶段"
      - "综合测验>=90%"
      - "教学演示优秀"
    reward:
      - "专家徽章"
      - "教学资格"
```

### 使用示例

```markdown
用户输入: "我想在8周内学会React，目标是可以独立完成中型项目，每周能投入15小时"

## 📚 自适应学习路径生成

### 📊 知识图谱

```
React进阶知识图谱
├── 基础层
│   ├── React核心概念 ★
│   ├── JSX语法 ★
│   └── 组件基础 ★★
│
├── 进阶层
│   ├── Hooks系统 ★★★
│   │   ├── useState ★★
│   │   ├── useEffect ★★★
│   │   └── 自定义Hooks ★★★
│   ├── 状态管理 ★★★
│   │   ├── Context ★★
│   │   └── 状态管理库 ★★★
│   └── 性能优化 ★★★★
│
└── 精通层
    ├── 高级Hooks ★★★★
    ├── 测试 ★★★
    └── 团队协作 ★★★
```

### 🎯 个性化路径

| 周次 | 主题 | 核心内容 | 实践项目 | 评估 |
|------|------|---------|---------|------|
| 1-2 | 夯实基础 | React核心、Hooks回顾 | TodoList | 模块测验 |
| 3-4 | Hooks深入 | 状态、副作用、自定义 | 购物车 | 项目评估 |
| 5-6 | 状态管理 | Context、Zustand | 中型项目 | 代码评审 |
| 7-8 | 性能+项目 | Profiler、测试 | 完整项目 | 综合认证 |

### 📅 详细计划 (第1周)

**周一**
- [ ] 30min: React核心概念自测
- [ ] 60min: 费曼讲解练习
- [ ] 60min: 基础Hooks练习
- [ ] 🍅 番茄钟 x3

**周二**
- [ ] 30min: 昨日回顾
- [ ] 90min: useState深入
- [ ] 30min: 笔记整理
- [ ] 🍅 番茄钟 x3

...

### 🔄 动态调整

基于每周评估自动调整：
- 评估>=85% → 加速进入下一主题
- 评估70-85% → 正常进度
- 评估50-70% → 补充练习
- 评估<50% → 回退巩固+寻求帮助

### 📈 里程碑

| 里程碑 | 时间 | 要求 | 奖励 |
|--------|------|------|------|
| 🏆 入门证书 | 第3周末 | 基础评估>=70% | 解锁进阶 |
| 🎯 实践者 | 第6周末 | 项目>=85% | 解锁高级 |
| ⭐ 专家 | 第8周末 | 综合>=90% | 专家认证 |
```

### 与间隔重复协同

```yaml
spaced_repetition_integration:
  curriculum_designer_output:
    - key_concepts: 提取关键概念
    - difficulty_tags: 标注难度
    - practice_questions: 生成练习题

  spaced_repetition_input:
    - card_generation: 自动生成Anki卡片
    - scheduling: 根据掌握度安排复习
    - interleaving: 交叉复习不同模块

  feedback_loop:
    - review_results: 影响路径调整
    - weak_areas: 触发额外练习
    - mastery_level: 更新掌握度
```

### 触发条件

| 触发词 | 场景 | 响应 |
|--------|------|------|
| "帮我规划学习" | 开始新领域 | 生成完整路径 |
| "我卡住了" | 遇到困难 | 调整难度 |
| "太快了/太慢了" | 反馈调整 | 重规划路径 |
| "想深入X" | 细化主题 | 生成子路径 |

### 预期效果

| 指标 | 效果 |
|------|------|
| 学习效率 | +60% |
| 知识留存 | +75% |
| 目标达成率 | +85% |
| 学习时长 | -30% |

### 文件结构

```
curriculum-auto-designer/
├── SKILL.md                    # 本文件
├── prompts/
│   ├── knowledge-graph-template.md  # 知识图谱生成
│   └── path-planning-template.md    # 路径规划模板
├── scripts/
│   ├── curriculum_generator.py      # 课程生成器
│   ├── knowledge_graph_builder.py  # 知识图谱构建
│   └── adaptive_engine.py         # 自适应引擎
└── templates/
    └── curriculum-output.md         # 输出模板
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-24 | 初始版本，基于知识图谱的智能课程设计 |
