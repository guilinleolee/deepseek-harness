#!/usr/bin/env python3
"""
Math Visualizer CLI - 数学概念可视化命令行工具
用法: python math_viz_cli.py <command> [args]
"""
import argparse
import json
import re
import sys
import math
from pathlib import Path
from typing import Optional, List, Dict, Tuple

try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

VIS_DIR = Path.home() / ".claude" / "math_visualizations"
TEMPLATES_DIR = Path.home() / ".claude" / "math_viz_templates"


class FunctionPlotter:
    """函数图像绘制器"""

    PLOT_TYPES = ["line", "scatter", "bar", "surface", "parametric", "polar"]
    FEATURES = ["critical_points", "asymptotes", "derivative", "integral", "roots", "extrema"]

    def __init__(self):
        self._ensure_dirs()

    def _ensure_dirs(self):
        VIS_DIR.mkdir(parents=True, exist_ok=True)
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    def plot_2d(
        self,
        function: str,
        x_range: Tuple[float, float] = (-10, 10),
        features: Optional[List[str]] = None,
        output_path: Optional[str] = None,
        fmt: str = "html",
        title: Optional[str] = None,
        color: str = "#636EFA"
    ) -> Dict:
        """绘制2D函数图像"""
        if features is None:
            features = []

        if not MATPLOTLIB_AVAILABLE and not PLOTLY_AVAILABLE:
            return {"status": "error", "message": "请安装 matplotlib 或 plotly: pip install matplotlib plotly"}

        try:
            x_min, x_max = x_range
            if PLOTLY_AVAILABLE:
                return self._plot_2d_plotly(function, x_min, x_max, features, output_path, fmt, title, color)
            else:
                return self._plot_2d_matplotlib(function, x_min, x_max, features, output_path, title, color)
        except Exception as e:
            return {"status": "error", "message": f"绘图失败: {str(e)}"}

    def _parse_function(self, func_str: str) -> str:
        """标准化函数表达式"""
        func = func_str.lower().strip()
        func = re.sub(r'\^', '**', func)
        func = re.sub(r'(\d)([a-z])', r'\1*\2', func)
        func = re.sub(r'([a-z])([a-z])', r'\1*\2', func)
        func = re.sub(r'\*\s*\*\*', '**', func)
        return func

    def _safe_eval_function(self, x: np.ndarray, func_str: str) -> np.ndarray:
        """安全计算函数值"""
        safe_func = self._parse_function(func_str)
        safe_names = {
            'x': x, 'np': np, 'math': math,
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
            'log': np.log, 'ln': np.log, 'exp': np.exp,
            'sqrt': np.sqrt, 'abs': np.abs, 'pi': np.pi, 'e': np.e,
            'arcsin': np.arcsin, 'arccos': np.arccos, 'arctan': np.arctan,
            'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
        }
        y = eval(safe_func, {"__builtins__": {}}, safe_names)
        if isinstance(y, (int, float)):
            y = np.full_like(x, y)
        return y

    def _find_critical_points(self, x: np.ndarray, y: np.ndarray, threshold: float = 0.01) -> List[Tuple]:
        """寻找极值点和零点"""
        points = []
        for i in range(1, len(y) - 1):
            if abs(y[i]) < threshold and abs(y[i]) < min(abs(y[i-1]), abs(y[i+1])):
                points.append(('root', round(x[i], 3), round(y[i], 3)))
        eps = (x[1] - x[0]) * 5
        for i in range(1, len(y) - 1):
            if i < eps or i >= len(y) - eps:
                continue
            if y[i-1] < y[i] > y[i+1]:
                points.append(('max', round(x[i], 3), round(y[i], 3)))
            elif y[i-1] > y[i] < y[i+1]:
                points.append(('min', round(x[i], 3), round(y[i], 3)))
        return points[:10]

    def _plot_2d_plotly(
        self, func_str: str, x_min: float, x_max: float,
        features: List[str], output_path: Optional[str], fmt: str, title: Optional[str], color: str
    ) -> Dict:
        """使用Plotly绘制2D图像"""
        x = np.linspace(x_min, x_max, 2000)
        y = self._safe_eval_function(x, func_str)
        y = np.nan_to_num(y, nan=0.0, posinf=1e10, neginf=-1e10)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=func_str, line=dict(color=color, width=2)))

        if 'roots' in features or 'critical_points' in features:
            cp = self._find_critical_points(x, y)
            for cp_type, cx, cy in cp:
                color_map = {'root': 'green', 'max': 'red', 'min': 'blue'}
                fig.add_trace(go.Scatter(
                    x=[cx], y=[cy], mode='markers+text',
                    marker=dict(color=color_map.get(cp_type, 'gray'), size=10),
                    text=[f"{cp_type}: ({cx}, {cy})"], textposition="top center",
                    showlegend=False
                ))

        if 'derivative' in features:
            dx = (x[1] - x[0])
            dy = np.gradient(y, dx)
            fig.add_trace(go.Scatter(x=x, y=dy, mode='lines', name="导数", line=dict(dash='dash', width=1.5)))

        fig.update_layout(
            title=title or f"f(x) = {func_str}",
            xaxis_title="x",
            yaxis_title="f(x)",
            hovermode="x unified",
            template="plotly_white"
        )

        if output_path:
            if fmt == 'html':
                fig.write_html(output_path)
            elif fmt == 'png':
                fig.write_image(output_path, width=1200, height=600)
            elif fmt == 'svg':
                fig.write_image(output_path, format='svg', width=1200, height=600)
            return {"status": "success", "path": output_path, "description": self._describe_plot(func_str, x, y)}
        else:
            return {"status": "success", "html": fig.to_html(full_html=False), "description": self._describe_plot(func_str, x, y)}

    def _plot_2d_matplotlib(
        self, func_str: str, x_min: float, x_max: float,
        features: List[str], output_path: Optional[str], title: Optional[str], color: str
    ) -> Dict:
        """使用Matplotlib绘制2D图像"""
        x = np.linspace(x_min, x_max, 1000)
        y = self._safe_eval_function(x, func_str)
        y = np.nan_to_num(y, nan=0.0, posinf=1e10, neginf=-1e10)

        plt.figure(figsize=(12, 6))
        plt.plot(x, y, color=color, linewidth=2, label=f"f(x) = {func_str}")
        plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
        plt.axvline(0, color='gray', linestyle='--', linewidth=0.8)
        plt.title(title or f"f(x) = {func_str}", fontsize=14)
        plt.xlabel("x", fontsize=12)
        plt.ylabel("f(x)", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return {"status": "success", "path": output_path}
        else:
            tmp = str(VIS_DIR / "temp_plot.png")
            plt.savefig(tmp, dpi=150, bbox_inches='tight')
            plt.close()
            return {"status": "success", "path": tmp}

    def _describe_plot(self, func_str: str, x: np.ndarray, y: np.ndarray) -> str:
        """描述图像关键特征"""
        desc = []
        y_clipped = np.clip(y, -1e6, 1e6)
        cp = self._find_critical_points(x, y_clipped)

        if cp:
            roots = [f"({cx},{cy})" for ct, cx, cy in cp if ct == 'root']
            extrema = [f"{ct}({cx},{cy})" for ct, cx, cy in cp if ct in ('max', 'min')]
            if roots:
                desc.append(f"零点: {', '.join(roots[:3])}")
            if extrema:
                desc.append(f"极值: {', '.join(extrema[:3])}")

        y_max, y_min = np.max(y_clipped), np.min(y_clipped)
        x_at_max, x_at_min = x[np.argmax(y_clipped)], x[np.argmin(y_clipped)]
        desc.append(f"最大值: {y_max:.3f} at x={x_at_max:.2f}")
        desc.append(f"最小值: {y_min:.3f} at x={x_at_min:.2f}")
        return " | ".join(desc) if desc else "无显著特征"

    def plot_3d(
        self,
        expression: str,
        x_range: Tuple[float, float] = (-5, 5),
        y_range: Tuple[float, float] = (-5, 5),
        output_path: Optional[str] = None,
        fmt: str = "html"
    ) -> Dict:
        """绘制3D曲面图"""
        if not PLOTLY_AVAILABLE:
            return {"status": "error", "message": "3D图需要plotly: pip install plotly"}

        try:
            x = np.linspace(x_range[0], x_range[1], 100)
            y = np.linspace(y_range[0], y_range[1], 100)
            X, Y = np.meshgrid(x, y)

            safe_names = {
                'np': np, 'math': math, 'x': X, 'y': Y,
                'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                'log': np.log, 'exp': np.exp, 'sqrt': np.sqrt,
                'abs': np.abs, 'pi': np.pi, 'e': np.e,
            }
            Z = eval(self._parse_function(expression), {"__builtins__": {}}, safe_names)
            Z = np.nan_to_num(Z, nan=0.0)

            fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z, colorscale='Viridis')])
            fig.update_layout(
                title=f"z = {expression}",
                scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'),
                margin=dict(l=0, r=0, t=40, b=0)
            )

            if output_path:
                if fmt == 'html':
                    fig.write_html(output_path)
                else:
                    fig.write_image(output_path, width=1200, height=800)
                return {"status": "success", "path": output_path}
            else:
                return {"status": "success", "html": fig.to_html(full_html=False)}
        except Exception as e:
            return {"status": "error", "message": f"3D绘图失败: {str(e)}"}

    def multi_plot(
        self,
        functions: List[str],
        x_range: Tuple[float, float] = (-10, 10),
        output_path: Optional[str] = None,
        fmt: str = "html",
        colors: Optional[List[str]] = None
    ) -> Dict:
        """在同一坐标系绘制多个函数"""
        if colors is None:
            colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3"]

        x = np.linspace(x_range[0], x_range[1], 2000)
        fig = go.Figure() if PLOTLY_AVAILABLE else None

        for i, func_str in enumerate(functions):
            try:
                y = self._safe_eval_function(x, func_str)
                y = np.nan_to_num(y, nan=0.0, posinf=1e10, neginf=-1e10)
                color = colors[i % len(colors)]
                if PLOTLY_AVAILABLE and fig:
                    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=func_str, line=dict(color=color, width=2)))
                elif MATPLOTLIB_AVAILABLE:
                    plt.figure(figsize=(12, 6)) if i == 0 else None
                    plt.plot(x, y, color=color, linewidth=2, label=func_str)
            except Exception:
                continue

        if PLOTLY_AVAILABLE and fig:
            fig.update_layout(title="多函数对比", xaxis_title="x", yaxis_title="f(x)", hovermode="x unified")
            if output_path:
                fig.write_html(output_path) if fmt == 'html' else fig.write_image(output_path, width=1200, height=600)
                return {"status": "success", "path": output_path}
            return {"status": "success", "html": fig.to_html(full_html=False)}
        elif MATPLOTLIB_AVAILABLE:
            plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.title("多函数对比")
            if output_path:
                plt.savefig(output_path, dpi=150)
                plt.close()
                return {"status": "success", "path": output_path}
            return {"status": "success", "path": str(VIS_DIR / "multi_plot.png")}
        return {"status": "error", "message": "请安装 matplotlib 或 plotly"}


class ConceptExplainer:
    """数学概念可视化解释器"""

    CONCEPT_TYPES = ["function", "algorithm", "proof", "geometry", "algebra", "statistics", "calculus", "probability"]
    AUDIENCE_LEVELS = ["beginner", "intermediate", "advanced"]

    def explain(
        self,
        concept: str,
        concept_type: str = "function",
        audience: str = "intermediate",
        output_path: Optional[str] = None
    ) -> Dict:
        """解释数学概念并生成可视化"""
        viz_info = self._select_visualization(concept, concept_type, audience)

        result = {
            "status": "success",
            "concept": concept,
            "type": concept_type,
            "audience": audience,
            "visualization_type": viz_info["type"],
            "description": viz_info["description"],
            "mermaid_code": viz_info.get("mermaid", ""),
            "latex": viz_info.get("latex", ""),
            "manim_code": viz_info.get("manim", ""),
            "key_points": viz_info.get("key_points", []),
        }

        if output_path:
            self._save_explanation(result, output_path)

        return result

    def _select_visualization(self, concept: str, ctype: str, audience: str) -> Dict:
        """根据概念类型选择可视化方案"""
        concept_lower = concept.lower()
        templates = {
            "链式法则": {
                "type": "animation", "description": "链式法则展示了复合函数的导数计算方法",
                "key_points": ["d/dx[f(g(x))] = f'(g(x)) * g'(x)", "内层先导,外层次之", "应用于复合函数求导"],
                "latex": r"\frac{d}{dx}[f(g(x))] = f'(g(x)) \cdot g'(x)",
                "mermaid": self._mermaid_chain_rule(),
                "manim": self._manim_chain_rule(),
            },
            "反向传播": {
                "type": "animation",
                "description": "反向传播算法通过链式法则计算神经网络梯度",
                "key_points": ["损失函数对各参数的偏导", "从输出层向输入层反向传播误差", "梯度下降更新参数"],
                "latex": r"\frac{\partial L}{\partial w^{(l)}} = \frac{\partial L}{\partial a^{(n)}} \cdot \prod_{i=l}^{n-1} \frac{\partial a^{(i+1)}}{\partial z^{(i)}} \cdot \frac{\partial z^{(l)}}{\partial w^{(l)}}",
                "mermaid": self._mermaid_backprop(),
                "manim": self._manim_backprop(),
            },
            "梯度下降": {
                "type": "animation",
                "description": "梯度下降通过沿函数梯度的负方向迭代寻找最小值",
                "key_points": ["θ := θ - α∇J(θ)", "学习率α控制步长", "收敛条件: ||∇J(θ)|| < ε"],
                "latex": r"\theta_{n+1} = \theta_n - \alpha \nabla J(\theta_n)",
                "mermaid": self._mermaid_gradient_descent(),
                "manim": self._manim_gradient_descent(),
            },
            "泰勒展开": {
                "type": "animation",
                "description": "泰勒展开用无穷多项多项式近似任意函数",
                "key_points": ["f(x) = Σ f⁽ⁿ⁾(a)/n! · (x-a)ⁿ", "a=0时为麦克劳林展开", "收敛半径内无限精确"],
                "latex": r"f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!}(x-a)^n",
                "mermaid": self._mermaid_taylor(),
                "manim": self._manim_taylor(),
            },
            "傅里叶变换": {
                "type": "animation",
                "description": "傅里叶变换将时域信号分解为不同频率的正弦波叠加",
                "key_points": ["任意周期函数可分解为正弦波叠加", "频率域揭示信号的频率组成", "FFT实现O(n log n)复杂度"],
                "latex": r"F(\omega) = \int_{-\infty}^{\infty} f(t) e^{-i\omega t} dt",
                "mermaid": self._mermaid_fourier(),
                "manim": self._manim_fourier(),
            },
            "矩阵乘法": {
                "type": "diagram",
                "description": "矩阵乘法: C = A × B, 其中 C[i,j] = Σ A[i,k] × B[k,j]",
                "key_points": ["行×列对应元素相乘求和", "不满足交换律: AB ≠ BA", "满足结合律: (AB)C = A(BC)"],
                "latex": r"C_{ij} = \sum_{k=1}^{n} A_{ik} B_{kj}",
                "mermaid": self._mermaid_matrix_mult(),
                "manim": "",
            },
            "积分": {
                "type": "animation",
                "description": "积分是导数的逆运算,表示函数曲线下的面积",
                "key_points": ["定积分计算曲线与x轴围成的有向面积", "不定积分是原函数族", "微积分基本定理: ∫ₐᵇ F'(x)dx = F(b) - F(a)"],
                "latex": r"\int_a^b f(x)dx = F(b) - F(a)",
                "mermaid": self._mermaid_integral(),
                "manim": self._manim_integral(),
            },
        }

        for key, template in templates.items():
            if key in concept_lower:
                return template

        return self._generic_concept(concept, ctype, audience)

    def _generic_concept(self, concept: str, ctype: str, audience: str) -> Dict:
        """通用概念模板"""
        return {
            "type": "concept_map",
            "description": f"关于「{concept}」的{lvl(audience)}级解释",
            "key_points": [f"核心概念: {concept}", f"类型: {ctype}", f"适用受众: {audience}"],
            "latex": "",
            "mermaid": self._generic_mermaid(concept, ctype),
            "manim": self._generic_manim(concept),
        }

    def _generic_mermaid(self, concept: str, ctype: str) -> str:
        return f"""```mermaid
graph LR
    A["{concept}"] --> B["核心原理"]
    A --> C["应用场景"]
    A --> D["相关概念"]
    B --> E["定义"]
    B --> F["性质"]
    C --> G["场景1"]
    C --> H["场景2"]
    D --> I["上游概念"]
    D --> J["下游概念"]
```"""

    def _generic_manim(self, concept: str) -> str:
        return f'''from manim import *

class {concept.replace(" ", "")}Visualization(Scene):
    def construct(self):
        title = Text("{concept}").scale(1.5)
        self.play(Write(title))
        self.wait()
'''

    def _mermaid_chain_rule(self) -> str:
        return """```mermaid
graph LR
    A["复合函数<br/>f(g(x))"] --> B["外层f"]
    A --> C["内层g"]
    B --> D["f'(u)"]
    C --> E["g'(x)"]
    D --> F["乘积"]
    E --> F
    F --> G["导数<br/>f'(g(x))·g'(x)"]
```"""

    def _mermaid_backprop(self) -> str:
        return """```mermaid
flowchart TB
    subgraph Forward["前向传播"]
        I["输入层"] --> H1["隐藏层1"]
        H1 --> H2["隐藏层2"]
        H2 --> O["输出层"]
        O --> L["损失L"]
    end
    subgraph Backward["反向传播"]
        L --> dO["∂L/∂O"]
        dO --> dH2["∂L/∂H2"]
        dH2 --> dH1["∂L/∂H1"]
        dH1 --> dW1["更新W1"]
        dH2 --> dW2["更新W2"]
    end
```"""

    def _mermaid_gradient_descent(self) -> str:
        return """```mermaid
flowchart TD
    A["初始化θ₀"] --> B["计算梯度∇J(θ)"]
    B --> C["更新θ = θ - α∇J"]
    C --> D{"收敛判断<br/>||∇J|| < ε?"}
    D -- "否" --> B
    D -- "是" --> E["最优解θ*"]
```"""

    def _mermaid_taylor(self) -> str:
        return """```mermaid
flowchart LR
    A["f(x)"] --> B["在a点展开"]
    B --> C["Σ f⁽ⁿ⁾(a)/n! · (x-a)ⁿ"]
    C --> D["n=0: 常数项"]
    C --> E["n=1: 线性项"]
    C --> F["n=2: 二次项"]
    C --> G["n→∞: 高阶项"]
```"""

    def _mermaid_fourier(self) -> str:
        return """```mermaid
flowchart LR
    A["时域信号f(t)"] --> B["傅里叶变换"]
    B --> C["频率谱F(ω)"]
    C --> D["各频率分量"]
    D --> E["正弦波叠加"]
    E --> A
```"""

    def _mermaid_matrix_mult(self) -> str:
        return """```mermaid
flowchart LR
    A["矩阵A<br/>m×k"] --> AB["A × B"]
    B["矩阵B<br/>k×n"] --> AB
    AB --> C["矩阵C<br/>m×n"]
    C --> D["C[i,j] = ΣA[i,k]·B[k,j]"]
```"""

    def _mermaid_integral(self) -> str:
        return """```mermaid
flowchart LR
    A["f(x)"] --> B["定积分∫ₐᵇf(x)dx"]
    B --> C["原函数F(x)"]
    C --> D["F(b) - F(a)"]
    D --> E["曲线下面积<br/>(有向)"]
```"""

    def _manim_chain_rule(self) -> str:
        return '''from manim import *

class ChainRuleVisualization(Scene):
    def construct(self):
        title = Text("链式法则", font="Noto Sans CJK SC").scale(1.5)
        self.play(Write(title))
        self.wait()

        formula = MathTex(r"\\frac{d}{dx}[f(g(x))] = f'(g(x)) \\cdot g'(x)").scale(1.2)
        self.play(Transform(title, formula))
        self.wait()
'''

    def _manim_backprop(self) -> str:
        return '''from manim import *

class BackpropVisualization(Scene):
    def construct(self):
        input_layer = VGroup(*[Circle(radius=0.3) for _ in range(3)]).arrange(RIGHT, buff=0.5)
        hidden_layer = VGroup(*[Circle(radius=0.3) for _ in range(4)]).arrange(RIGHT, buff=0.5)
        output_layer = VGroup(*[Circle(radius=0.3) for _ in range(2)]).arrange(RIGHT, buff=0.5)

        self.play(Create(input_layer), Create(hidden_layer), Create(output_layer))
        self.wait()
'''

    def _manim_gradient_descent(self) -> str:
        return '''from manim import *

class GradientDescentVisualization(Scene):
    def construct(self):
        axes = Axes(x_range=[-3, 3], y_range=[-1, 5], x_length=10, y_length=6)
        parabola = axes.plot(lambda x: 0.5 * x**2, color=BLUE)
        self.play(Create(axes), Create(parabola))
        self.wait()
'''

    def _manim_taylor(self) -> str:
        return '''from manim import *

class TaylorVisualization(Scene):
    def construct(self):
        axes = Axes(x_range=[-3, 3], y_range=[-2, 5], x_length=10, y_length=6)
        exponential = axes.plot(lambda x: np.exp(x), color=BLUE)
        taylor = axes.plot(lambda x: 1 + x + x**2/2 + x**3/6, color=RED)
        self.play(Create(axes), Create(exponential))
        self.play(Create(taylor))
        self.wait()
'''

    def _manim_fourier(self) -> str:
        return '''from manim import *

class FourierVisualization(Scene):
    def construct(self):
        title = Text("傅里叶变换", font="Noto Sans CJK SC").scale(1.5)
        formula = MathTex(r"F(\\omega) = \\int_{-\\infty}^{\\infty} f(t) e^{-i\\omega t} dt")
        self.play(Write(title))
        self.wait()
'''

    def _manim_integral(self) -> str:
        return '''from manim import *

class IntegralVisualization(Scene):
    def construct(self):
        axes = Axes(x_range=[0, 3], y_range=[0, 9], x_length=10, y_length=6)
        curve = axes.plot(lambda x: x**2, color=BLUE, x_range=[0, 2.5])
        area = axes.get_area(curve, x_range=[0, 2], color=BLUE, opacity=0.3)
        self.play(Create(axes), Create(curve))
        self.play(Create(area))
        self.wait()
'''

    def _save_explanation(self, result: Dict, output_path: str):
        """保存解释结果"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {result['concept']}\n\n")
            f.write(f"**类型**: {result['type']} | **受众**: {result['audience']}\n\n")
            f.write(f"## 描述\n\n{result['description']}\n\n")
            f.write(f"## 关键要点\n\n")
            for point in result.get('key_points', []):
                f.write(f"- {point}\n")
            if result.get('latex'):
                f.write(f"\n## LaTeX公式\n\n```latex\n{result['latex']}\n```\n")
            if result.get('mermaid_code'):
                f.write(f"\n## 图表\n\n{result['mermaid_code']}\n")
            if result.get('manim_code'):
                f.write(f"\n## Manim动画代码\n\n```python\n{result['manim_code']}\n```\n")


class MermaidDiagram:
    """Mermaid图表生成器"""

    def algorithm_flowchart(
        self,
        algorithm: str,
        steps: Optional[List[Tuple[str, str]]] = None,
        detail_level: str = "medium"
    ) -> str:
        """生成算法流程图"""
        algo_lower = algorithm.lower()
        templates = {
            "梯度下降": [
                ("Start", "初始化参数θ和学习率α"),
                ("Compute", "计算损失函数 J(θ)"),
                ("Gradient", "计算梯度 ∇J(θ)"),
                ("Update", "更新 θ ← θ - α∇J(θ)"),
                ("Check", "检查收敛: ||∇J|| < ε?"),
                ("Yes", "输出最优θ*"),
                ("No", "返回Compute"),
            ],
            "反向传播": [
                ("Forward", "前向传播计算输出"),
                ("Loss", "计算损失L = (y-ŷ)²"),
                ("Backward", "从输出层反向传播误差"),
                ("Gradient", "计算各层梯度 ∂L/∂w"),
                ("Update", "更新权重 w ← w - α∂L/∂w"),
                ("Repeat", "重复直到收敛"),
            ],
            "快速排序": [
                ("Pivot", "选择枢轴元素"),
                ("Partition", "划分: 左<枢轴<右"),
                ("Recurse", "递归排序左右两部分"),
                ("Combine", "合并结果"),
            ],
            "K近邻": [
                ("Input", "给定查询点x和K"),
                ("Distance", "计算x到所有点的距离"),
                ("Sort", "排序取最近K个邻居"),
                ("Vote", "多数投票决定类别"),
                ("Output", "输出预测类别"),
            ],
        }

        if steps is None:
            steps = templates.get(algorithm, [
                ("Step1", f"{algorithm}步骤1"),
                ("Step2", f"{algorithm}步骤2"),
                ("Step3", f"{algorithm}步骤3"),
            ])

        lines = ["```mermaid", "flowchart TD"]
        for i, (node_id, desc) in enumerate(steps):
            safe_id = re.sub(r'[^a-zA-Z0-9]', '_', node_id)
            lines.append(f'    {safe_id}["{desc}"]')
            if i > 0:
                prev_id = re.sub(r'[^a-zA-Z0-9]', '_', steps[i-1][0])
                lines.append(f'    {prev_id} --> {safe_id}')

        lines.append("```")
        return "\n".join(lines)

    def concept_map(self, concept: str, relations: List[Tuple[str, str, str]]) -> str:
        """生成概念关联图"""
        lines = ["```mermaid", f'graph LR\n    A["{concept}"]']
        for src, rel, dst in relations:
            lines.append(f'    A --> |"{rel}"| {dst}["{dst}"]')
        lines.append("```")
        return "\n".join(lines)


def lvl(audience: str) -> str:
    return {"beginner": "入门", "intermediate": "进阶", "advanced": "高级"}.get(audience, "基础")


def cmd_plot(args):
    """绘制函数图像"""
    plotter = FunctionPlotter()

    functions = [f.strip() for f in args.functions.split(',')]
    x_range = (args.xmin, args.xmax) if hasattr(args, 'xmin') else (-10, 10)

    if args.format == '3d':
        result = plotter.plot_3d(functions[0], x_range, x_range, args.output, args.format)
    elif len(functions) > 1:
        result = plotter.multi_plot(functions, x_range, args.output, args.format)
    else:
        features = args.features.split(',') if args.features else []
        result = plotter.plot_2d(functions[0], x_range, features, args.output, args.format, args.title)

    if result["status"] == "error":
        print(f"❌ {result['message']}")
        return

    if args.output:
        print(f"✅ 已保存到: {result['path']}")
    if args.format == 'html' and result.get('html'):
        print(f"📊 {result.get('description', '绘制完成')}")
    elif result.get('description'):
        print(f"📊 {result['description']}")


def cmd_explain(args):
    """解释数学概念"""
    explainer = ConceptExplainer()
    result = explainer.explain(args.concept, args.type, args.level, args.output)

    print(f"\n{'='*50}")
    print(f"📐 概念: {result['concept']}")
    print(f"🎯 类型: {result['type']} | 👤 受众: {lvl(result['audience'])}")
    print(f"{'='*50}\n")
    print(f"📝 描述: {result['description']}\n")
    print(f"💡 关键要点:")
    for point in result.get('key_points', []):
        print(f"   • {point}")

    if result.get('latex'):
        print(f"\n📐 LaTeX公式:\n   {result['latex']}")

    if result.get('mermaid_code'):
        print(f"\n📊 Mermaid图表:")
        print(result['mermaid_code'])

    if args.output:
        print(f"\n✅ 已保存到: {args.output}")


def cmd_flowchart(args):
    """生成算法流程图"""
    diagram = MermaidDiagram()

    if args.type == 'algorithm':
        flowchart = diagram.algorithm_flowchart(args.name, detail_level=args.detail)
    else:
        print(f"❌ 不支持的流程图类型: {args.type}")
        return

    print(f"\n📊 {args.name} 流程图\n")
    print(flowchart)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(f"# {args.name} 流程图\n\n{flowchart}")
        print(f"\n✅ 已保存到: {args.output}")


def cmd_animate(args):
    """生成动画代码"""
    explainer = ConceptExplainer()
    result = explainer.explain(args.concept, "algorithm", "intermediate")

    if result.get('manim_code'):
        print(f"\n🎬 {args.concept} Manim动画代码\n")
        print("```python")
        print(result['manim_code'])
        print("```")

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result['manim_code'])
            print(f"\n✅ 已保存到: {args.output}")
    else:
        print(f"❌ 暂无动画支持: {args.concept}")


def cmd_interactive(args):
    """交互式可视化"""
    print("🎨 数学可视化交互模式")
    print("按 Ctrl+C 退出\n")

    while True:
        try:
            print("=" * 50)
            print("1. 绘制函数图像")
            print("2. 解释数学概念")
            print("3. 生成算法流程图")
            print("4. 生成动画代码")
            choice = input("📋 选择功能 (1-4): ").strip()

            if choice == '1':
                func = input("📈 输入函数 (如 y=sin(x)): ").strip()
                xmin = float(input("   x最小值 (默认-10): ").strip() or "-10")
                xmax = float(input("   x最大值 (默认10): ").strip() or "10")
                plotter = FunctionPlotter()
                result = plotter.plot_2d(func, (xmin, xmax), [], None, "html")
                if result["status"] == "success":
                    print(f"✅ {result.get('description', '绘制完成')}")
                else:
                    print(f"❌ {result['message']}")

            elif choice == '2':
                concept = input("📐 输入数学概念: ").strip()
                ctype = input("   类型 (function/algorithm/proof, 默认function): ").strip() or "function"
                level = input("   受众 (beginner/intermediate/advanced, 默认intermediate): ").strip() or "intermediate"
                explainer = ConceptExplainer()
                result = explainer.explain(concept, ctype, level)
                print(f"\n📝 {result['description']}")
                if result.get('latex'):
                    print(f"📐 {result['latex']}")
                if result.get('key_points'):
                    for p in result['key_points']:
                        print(f"  • {p}")

            elif choice == '3':
                algo = input("🔄 输入算法名称: ").strip()
                diagram = MermaidDiagram()
                print(diagram.algorithm_flowchart(algo))

            elif choice == '4':
                concept = input("🎬 输入动画主题: ").strip()
                explainer = ConceptExplainer()
                result = explainer.explain(concept, "algorithm", "intermediate")
                if result.get('manim_code'):
                    print(result['manim_code'])
                else:
                    print("❌ 暂无动画支持")

            print()
        except KeyboardInterrupt:
            print("\n\n👋 退出交互模式")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="Math Visualizer CLI - 数学概念可视化工具")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # plot
    p_plot = subparsers.add_parser("plot", help="绘制函数图像")
    p_plot.add_argument("functions", help="函数表达式，如 y=sin(x) 或 y=x^2,y=cos(x)")
    p_plot.add_argument("--xmin", type=float, default=-10, help="x轴最小值")
    p_plot.add_argument("--xmax", type=float, default=10, help="x轴最大值")
    p_plot.add_argument("--features", "-f", help="特征标注(逗号分隔): critical_points,derivative,roots,extrema")
    p_plot.add_argument("--output", "-o", help="输出路径")
    p_plot.add_argument("--format", choices=["html", "png", "svg", "3d"], default="html", help="输出格式")
    p_plot.add_argument("--title", "-t", help="图表标题")
    p_plot.add_argument("--color", "-c", default="#636EFA", help="线条颜色")

    # explain
    p_exp = subparsers.add_parser("explain", help="解释数学概念")
    p_exp.add_argument("concept", help="数学概念名称")
    p_exp.add_argument("--type", "-t", choices=ConceptExplainer.CONCEPT_TYPES, default="function", help="概念类型")
    p_exp.add_argument("--level", "-l", choices=ConceptExplainer.AUDIENCE_LEVELS, default="intermediate", help="受众水平")
    p_exp.add_argument("--output", "-o", help="输出Markdown路径")

    # flowchart
    p_fc = subparsers.add_parser("flowchart", help="生成算法流程图")
    p_fc.add_argument("name", help="算法名称")
    p_fc.add_argument("--type", choices=["algorithm", "concept"], default="algorithm", help="流程图类型")
    p_fc.add_argument("--detail", choices=["low", "medium", "high"], default="medium", help="详细程度")
    p_fc.add_argument("--output", "-o", help="输出Markdown路径")

    # animate
    p_ani = subparsers.add_parser("animate", help="生成Manim动画代码")
    p_ani.add_argument("concept", help="动画主题")
    p_ani.add_argument("--output", "-o", help="输出Python文件路径")

    # interactive
    subparsers.add_parser("interactive", help="交互式可视化")

    args = parser.parse_args()

    if args.command == "plot":
        cmd_plot(args)
    elif args.command == "explain":
        cmd_explain(args)
    elif args.command == "flowchart":
        cmd_flowchart(args)
    elif args.command == "animate":
        cmd_animate(args)
    elif args.command == "interactive":
        cmd_interactive(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
