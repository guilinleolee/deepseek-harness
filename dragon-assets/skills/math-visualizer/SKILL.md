---
license: UNKNOWN
triggers: ["math visualizer", "Math Visualizer - 数学概念可视化"]
---
# Math Visualizer - 数学概念可视化

## L0: 一句话 (≤15字)
数学公式/概念 → 动画/图示可视化

## L1: 使用场景 (50-100字)

### 触发词
- 画图说明 / 可视化
- animation / 数学动画
- 图形化解释 / 图示
- 让我看看 / 这个公式什么意思

### 适用场景
- 理解抽象数学概念
- 展示函数图像/变换
- 算法流程可视化
- 证明过程图解
- 概念关联图

### 不适用
- 纯文字解释足够的情况
- 复杂数值计算
- 需要交互的动态场景

## L2: 详细文档

### 核心能力

```python
class ConceptVisualizer(dspy.Signature):
    """将数学概念转化为可视化"""
    concept: str = dspy.InputField(desc="数学概念或公式")
    concept_type: str = dspy.InputField(
        desc="类型: function/algorithm/proof/geometry/algebra/statistics"
    )
    audience: str = dspy.InputField(
        desc="受众: beginner/intermediate/advanced",
        default="intermediate"
    )

    visualization_type: str = dspy.OutputField(
        desc="推荐可视化类型"
    )
    description: str = dspy.OutputField(desc="可视化描述")
    animation_script: str = dspy.OutputField(desc="动画代码(Manim/Plotly)")


class FunctionPlotter(dspy.Signature):
    """函数图像绘制"""
    function: str = dspy.InputField(desc="函数表达式, 如 y=x^2")
    x_range: tuple = dspy.InputField(
        desc="x轴范围",
        default=(-10, 10)
    )
    features: list = dspy.InputField(
        desc="特征标注: critical_points/asymptotes/derivative",
        default=[]
    )

    plot_code: str = dspy.OutputField(desc="Plotly/Manim代码")
    description: str = dspy.OutputField(desc="图像关键特征说明")


class AlgorithmFlowchart(dspy.Signature):
    """算法流程图生成"""
    algorithm: str = dspy.InputField(desc="算法名称或伪代码")
    detail_level: str = dspy.InputField(
        desc="详细程度: high/medium/low",
        default="medium"
    )

    flowchart: str = dspy.OutputField(desc="Mermaid/Markdown流程图")
    key_steps: list = dspy.OutputField(desc="关键步骤列表")
    time_complexity: str = dspy.OutputField(desc="时间复杂度分析")
```

### 可视化类型

| 类型 | 工具 | 输出格式 | 示例 |
|------|------|---------|------|
| **函数图像** | Plotly/Matplotlib | HTML/PNG | y=sin(x), 3D曲面 |
| **几何图形** | Manim/Plotly | MP4/GIF | 圆/三角形/变换 |
| **流程图** | Mermaid | SVG/MD | 算法流程 |
| **概念图** | Mermaid | SVG/MD | 知识点关联 |
| **动画** | Manim | MP4/GIF | 证明过程/变换 |
| **表格** | Markdown | MD/HTML | 数据对比 |

### 使用示例

```bash
# ===== 命令行使用 =====
math-viz plot "y = x^2" --range -5 5 --output plot.html
math-viz plot "y = sin(x)" --3d --animate
math-viz animate "gradient_descent" --duration 10

# ===== 概念解释 =====
math-viz explain "链式法则" --type proof --level beginner
math-viz explain "反向传播" --type algorithm --level intermediate

# ===== 导出格式 =====
math-viz plot "f(x)" --format html    # 交互式HTML
math-viz plot "f(x)" --format png     # 静态图片
math-viz plot "f(x)" --format mp4    # 动画视频
```

### 内置模板

```yaml
模板库:
  函数图像:
    - basic-plot: 基础函数图
    - multi-function: 多函数对比
    - parametric: 参数方程
    - 3d-surface: 3D曲面

  几何动画:
    - triangle-proof: 三角形证明
    - circle-theorem: 圆幂定理
    - transformation: 几何变换

  算法流程:
    - gradient-descent: 梯度下降
    - backprop: 反向传播
    - knn: K近邻
    - sorting: 排序算法
```

### Python API

```python
from math_visualizer import FunctionPlotter, ConceptExplainer, MermaidDiagram

# 1. 函数图像
plotter = FunctionPlotter()
result = plotter.plot(
    function="y = x**2 * np.exp(-x**2)",
    x_range=(-3, 3),
    features=["critical_points", "derivative"],
    output="gaussian.html"
)
print(result.description)

# 2. 概念可视化
explainer = ConceptExplainer()
viz = explainer.explain(
    concept="反向传播",
    concept_type="algorithm",
    audience="intermediate"
)
print(viz.animation_script)  # Manim代码

# 3. 流程图
diagram = MermaidDiagram()
flowchart = diagram.algorithm_flowchart(
    algorithm="梯度下降",
    steps=[
        ("初始化", "随机初始化参数θ"),
        ("计算梯度", "∇J(θ) = ∂J/∂θ"),
        ("更新参数", "θ = θ - α∇J(θ)"),
        ("收敛判断", "||∇J(θ)|| < ε?")
    ]
)
print(flowchart)  # Mermaid代码
```

### Manim动画示例

```python
# 反向传播动画脚本
from manim import *

class BackpropVisualization(Scene):
    def construct(self):
        # 创建网络节点
        input_layer = VGroup(*[
            Circle() for _ in range(3)
        ]).arrange(RIGHT)

        output_layer = VGroup(*[
            Circle() for _ in range(2)
        ]).arrange(RIGHT, buff=2)

        # 绘制连接线
        connections = VGroup(*[
            Line(input_layer[i], output_layer[j])
            for i in range(3) for j in range(2)
        ])

        # 动画: 前向传播
        self.play(Create(input_layer))
        self.play(Create(output_layer))
        self.play(Create(connections))

        # 显示梯度反向流动
        self.play(
            *[FadeToColor(line, RED)
              for line in connections],
            run_time=2
        )
```

### 与学习师集成

```yaml
学习师工作流:
  讲解阶段:
    - 公式可视化 → math-visualizer
    - 算法流程图 → 生成Mermaid图
    - 几何动画 → 生成Manim动画

  理解验证:
    - 动态展示 → 辅助讲解
    - 变换过程 → 深度理解
```

### 工具依赖

```yaml
依赖工具:
  plotting:
    - plotly (交互式图表)
    - matplotlib (静态图像)
    - manim (动画生成)

  diagramming:
    - mermaid-cli (流程图)

  rendering:
    - kaleido (Plotly导出PNG)
```

### 质量标准

1. **准确性**: 数学表达正确无误
2. **美观性**: 配色/布局专业
3. **可读性**: 标注清晰易懂
4. **性能**: 图像生成 < 5秒

### 自检清单

- [ ] 数学公式渲染正确
- [ ] 图像清晰可读
- [ ] 动画流畅
- [ ] 支持多种导出格式
- [ ] 与Manim集成完成
