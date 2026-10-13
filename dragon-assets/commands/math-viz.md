---
name: math-viz
description: 数学可视化CLI - plot/explain/flowchart/animate/interactive数学概念可视化
invokable: true
---
# /math-viz

基于 `math-visualizer` (Manim) 的数学可视化命令行工具。

## 命令

```bash
D:/Python310/python.exe c:/Users/li/.claude/skills/math-visualizer/scripts/math_viz_cli.py <command> [args]
```

## 子命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `plot` | 绘制函数图像 | `plot "y=sin(x)" --xmin -3.14 --xmax 3.14` |
| `explain` | 解释数学概念 | `explain "导数的几何意义"` |
| `flowchart` | 生成算法流程图 | `flowchart quicksort` |
| `animate` | 生成Manim动画 | `animate "圆面积推导"` |
| `interactive` | 交互式可视化 | `interactive "二次函数"` |

## 天龙引擎调用

```bash
[@03构建师] 使用math-viz绘制y=x^2的函数图像
[@07记录师] 用math-viz解释泰勒展开式的几何意义
[@10-02] 生成牛顿迭代法的流程图
```

## 依赖

```bash
pip install manim numpy matplotlib
```
