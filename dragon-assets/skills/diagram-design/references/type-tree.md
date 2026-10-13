# 树形图参考指南

## 1. 适用场景

树形图（Tree Diagram）用于展示层级递进关系或组织结构，适用于决策树、分类体系、组织架构等场景。

| 场景 | 典型框架 |
|------|---------|
| 决策分析 | 根节点→分支条件→叶节点决策 |
| 分类体系 | 根类→子类→细分类 |
| 组织架构 | CEO→部门→团队→成员 |
| 技术架构 | 系统→子系统→模块→组件 |
| 知识图谱 | 主题→子主题→知识点 |

## 2. 设计原则

- **目标密度**: 4/10（清晰层级）
- **节点形状**: 根节点用椭圆，叶节点用椭圆，中间节点用矩形
- **accent使用**: 关键路径节点用accent强调
- **布局**: 从上到下或从左到右
- **连接**: L形分支线（垂直+水平段）

## 3. 组件类型

### 根节点

```html
<ellipse cx="400" cy="50" rx="50" ry="22" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="400" y="54" text-anchor="middle" font-size="11" font-weight="600" fill="var(--ink)">根节点</text>
```

### 普通节点（矩形）

```html
<rect x="360" y="120" width="80" height="30" rx="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<text x="400" y="139" text-anchor="middle" font-size="10" fill="var(--ink)">决策A</text>
```

### 叶节点（椭圆）

```html
<ellipse cx="400" cy="310" rx="35" ry="16" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<text x="400" y="314" text-anchor="middle" font-size="9" fill="var(--ink)">结果1</text>
```

### accent节点

```html
<rect x="360" y="120" width="80" height="30" rx="4" fill="var(--accent)" opacity="0.15" stroke="var(--accent)" stroke-width="2"/>
<text x="400" y="139" text-anchor="middle" font-size="10" font-weight="600" fill="var(--accent)">关键节点</text>
```

## 4. 连接线规范

### L形分支连接

```html
<!-- 从根节点到子节点（单分支） -->
<path d="M 400 72 V 100 H 400" stroke="var(--ink)" stroke-width="1" fill="none"/>

<!-- 从父节点到多个子节点 -->
<path d="M 400 150 V 180 H 280" stroke="var(--ink)" stroke-width="1" fill="none"/>
<path d="M 400 150 V 180 H 520" stroke="var(--ink)" stroke-width="1" fill="none"/>
```

### 多层级L形连接

```html
<!-- L1到L2层：垂直下行 -->
<path d="M 400 150 V 180" stroke="var(--ink)" stroke-width="1" fill="none"/>

<!-- L2到L3层：水平延伸 + 垂直下行 -->
<path d="M 400 180 V 210 H 280" stroke="var(--ink)" stroke-width="1" fill="none"/>
<path d="M 400 180 V 210 H 520" stroke="var(--ink)" stroke-width="1" fill="none"/>

<!-- L3到L4层（虚线） -->
<path d="M 400 270 V 300 H 240" stroke="var(--ink)" stroke-width="1" stroke-dasharray="3,3" fill="none"/>
```

## 5. 层级布局

### 坐标计算规则

假设画布宽度 W = 800，高度 H = 450，根节点居中于顶部：

- 画布: 800 × 450
- 根节点: (400, 50)
- L1层节点: y = 150，x 均匀分布
- L2层节点: y = 210
- L3层节点: y = 270
- 叶节点层: y = 310
- 层间距: 60px

### 节点层级坐标

| 层级 | 节点形状 | X坐标 | Y坐标 | 说明 |
|------|---------|-------|-------|------|
| 根节点 | 椭圆rx=50 ry=22 | 居中 | 50 | rx=8, 强调色边框 |
| L1 | 矩形80×30 | 均匀分布 | 150 | rx=4 |
| L2 | 矩形80×30 | 均匀分布 | 210 | rx=4 |
| L3 | 矩形80×30 | 均匀分布 | 270 | rx=4, 可选虚线 |
| 叶节点 | 椭圆rx=35 ry=16 | 均匀分布 | 310 | rx=4 |

### 比例原则

- 画布宽高比约 16:9 或 4:3
- 节点间距均匀，避免交叉
- 分支线不交叉
- 叶节点在同一水平线上（可选）

## 6. 命名规范

### 颜色变量

```css
/* minimal-light */
--paper: #ffffff;
--ink: #1a1a2e;
--muted: #6b7280;
--paper-2: #f8fafc;
--accent: #3b82f6;
--link: #2563eb;

/* minimal-dark */
--paper: #0f172a;
--ink: #f1f5f9;
--muted: #94a3b8;
--paper-2: #1e293b;
--accent: #60a5fa;
--link: #93c5fd;

/* full-editorial */
--paper: #fefefe;
--ink: #18181b;
--muted: #71717a;
--paper-2: #f4f4f5;
--accent: #e11d48;
--link: #be123c;
```

### 元素ID命名

```html
<g id="tree-container">          <!-- 主容器组 -->
  <g id="root-node">            <!-- 根节点 -->
  <g id="level-1">              <!-- L1层节点组 -->
  <g id="node-1a">              <!-- L1子节点 -->
  <g id="level-2">              <!-- L2层节点组 -->
  <g id="node-2a">              <!-- L2子节点 -->
  <g id="leaf-nodes">           <!-- 叶节点组 -->
  <g id="branch-lines">        <!-- 分支线组 -->
</g>
```

### 类名约定

```html
<div class="tree">
  <div class="tree-root">
  <div class="tree-level level-1">
    <div class="tree-node node-regular">
    <div class="tree-node node-accent">
  <div class="tree-level level-2">
  <div class="tree-leaf">
  <div class="tree-branch">
```

## 7. 常见布局模式

### 决策树

```
                          ┌─────────────┐
                          │   根决策    │
                          └──────┬──────┘
              ┌───────────────┴┐           └───────────────┐
         ┌────▼────┐                              ┌────▼────┐
         │  条件A  │                              │  条件B  │
         └────┬────┘                              └────┬────┘
      ┌───────┴───────┐                       ┌───────┴───────┐
  ┌───▼───┐       ┌───▼───┐               ┌───▼───┐       ┌───▼───┐
  │ 执行A │       │ 执行B │               │ 执行C │       │ 执行D │
  └───────┘       └───────┘               └───────┘       └───────┘

根节点：椭圆（rx=50 ry=22）
L1节点：矩形（rx=4）
叶节点：椭圆（rx=35 ry=16）
accent：关键分支用accent强调
```

### 组织架构

```
                         ┌───────────────┐
                         │     CEO      │
                         └───────┬───────┘
                    ┌──────────┼──────────┐
                ┌───▼───┐  ┌───▼───┐  ┌───▼───┐
                │  CTO  │  │  CFO  │  │  COO  │
                └───┬───┘  └───┬───┘  └───┬───┘
               ┌────┼────┐        │         │
           ┌───▼─┐┌───▼─┐    ┌───▼─┐  ┌───▼─┐
           │ Dev ││ QA │    │ FIN │  │ OPS │
           └─────┘└─────┘    └─────┘  └─────┘
```

### 知识分类

```
                     ┌────────────────┐
                     │    知识主题    │ ← 根节点椭圆
                     └───────┬────────┘
                   ┌─────────┼─────────┐
               ┌───▼───┐┌───▼───┐┌───▼───┐
               │ 技术  ││ 商业  ││ 设计  │ ← L1矩形节点
               └───┬───┘└───┬───┘└───┬───┘
              ┌────┼────┐    │        │
          ┌───▼─┐┌───▼─┐┌───▼─┐  ┌───▼─┐
          │前端 ││后端 ││架构 │  │产品 │ ← L2叶节点椭圆
          └─────┘└─────┘└─────┘  └─────┘
```

### 节点强调策略

| 节点类型 | 典型策略 | 推荐强调色 |
|---------|---------|-----------|
| 根节点 | 强调色背景 | `--paper-2` 填充 + 粗边框 |
| 关键分支 | accent边框 | `--accent` 填充opacity=0.15 + stroke-width=2 |
| 终端叶节点 | 普通样式 | `--paper` 填充 |
| 决策节点 | 边框强调 | `--accent` 粗边框 |

### 标签密度控制

- **根节点**: 1个主标签，字号11px，粗体
- **L1层节点**: 1个标签，字号10px
- **L2层节点**: 1个标签，字号10px
- **叶节点**: 1个标签，字号9px
- 分支线不标注（通过节点位置隐式表达关系）

## 8. 质量检查清单

- [ ] 节点数量合理（不超过20个节点）
- [ ] 根节点居中或靠上
- [ ] L形连接线无交叉
- [ ] 节点间距均匀
- [ ] 叶节点在同一水平线（可选）
- [ ] accent节点正确使用强调色
- [ ] 分支线粗细一致（1px）
- [ ] 节点标签不超出边界
- [ ] WCAG AA对比度（文字4.5:1，图形3:1）
- [ ] SVG响应式，viewBox设置正确
- [ ] 整体布局居中，四周留白均衡
