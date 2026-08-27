# 流程图参考指南

## 1. 适用场景

流程图（Flowchart）用于展示线性或分支的操作步骤，适用于业务流程、算法流程、决策流程等场景。

| 场景 | 典型框架 |
|------|---------|
| 业务流程 | 申请→审批→执行→归档 |
| 算法流程 | 输入→处理→判断→输出 |
| 决策流程 | 条件判断→分支处理→汇总 |
| 用户旅程 | 发现→考虑→购买→使用 |

## 2. 设计原则

- **目标密度**: 4/10（清晰节点边界）
- **节点形状**: 端点(椭圆)/处理(矩形)/判断(菱形)/连接器(圆形)
- **accent使用**: 当前节点用accent强调
- **布局**: 从上到下或从左到右
- **连接**: 带箭头的实线

## 3. 组件类型

### 端点（开始/结束）

```html
<!-- 开始节点 -->
<ellipse cx="200" cy="60" rx="45" ry="22" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="200" y="65" text-anchor="middle" font-size="11" font-weight="600" fill="var(--ink)">开始</text>

<!-- 结束节点 -->
<ellipse cx="200" cy="380" rx="45" ry="22" fill="var(--paper)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="200" y="385" text-anchor="middle" font-size="11" font-weight="600" fill="var(--ink)">结束</text>
```

### 处理节点（矩形）

```html
<!-- 普通处理 -->
<rect x="150" y="120" width="100" height="45" rx="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<text x="200" y="148" text-anchor="middle" font-size="11" fill="var(--ink)">处理步骤</text>

<!-- accent处理（当前步骤） -->
<rect x="150" y="200" width="100" height="45" rx="4" fill="var(--accent)" opacity="0.1" stroke="var(--accent)" stroke-width="2"/>
<text x="200" y="228" text-anchor="middle" font-size="11" font-weight="600" fill="var(--accent)">当前步骤</text>
```

### 判断节点（菱形）

```html
<polygon points="200,290 260,325 200,360 140,325" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<text x="200" y="322" text-anchor="middle" font-size="10" fill="var(--ink)">是否?</text>
```

### 连接器（圆形）

```html
<!-- 小圆点连接器 -->
<circle cx="200" cy="170" r="5" fill="var(--ink)"/>

<!-- 分支连接器 -->
<circle cx="200" cy="290" r="6" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<text x="200" y="294" text-anchor="middle" font-size="8" fill="var(--muted)">1</text>
```

## 4. 连接线规范

### 直实线（普通流程）

```html
<!-- 垂直连接线 -->
<line x1="200" y1="165" x2="200" y2="200" stroke="var(--ink)" stroke-width="1.5"/>

<!-- 水平连接线 -->
<line x1="250" y1="325" x2="340" y2="325" stroke="var(--ink)" stroke-width="1.5"/>

<!-- 箭头端 -->
<polygon points="340,325 330,320 330,330" fill="var(--ink)"/>
```

### 虚线（返回/循环）

```html
<path d="M 150 230 L 80 230 L 80 60 L 155 60" stroke="var(--ink)" stroke-width="1" stroke-dasharray="5,3" fill="none"/>
<polygon points="155,60 148,55 148,65" fill="var(--ink)"/>
```

### 判断分支线

```html
<!-- 是分支（右侧） -->
<line x1="260" y1="325" x2="340" y2="325" stroke="var(--ink)" stroke-width="1.5"/>
<text x="290" y="315" font-size="9" fill="var(--accent)">是</text>

<!-- 否分支（下方） -->
<line x1="200" y1="360" x2="200" y2="400" stroke="var(--ink)" stroke-width="1.5"/>
<text x="212" y="385" font-size="9" fill="var(--muted)">否</text>
```

## 5. 层级布局

### 坐标计算规则

假设画布宽度 W = 500，高度 H = 450：

- 画布: 500 × 450
- 节点宽度: 100px
- 节点高度: 45px
- 判断节点: 80×70px（菱形）
- 垂直间距: 55px
- 水平间距: 90px

### 节点层级坐标

| 层级 | 形状 | X坐标 | Y坐标 | 说明 |
|------|------|-------|-------|------|
| 开始 | 椭圆rx=45 ry=22 | 居中 | 60 | 顶部入口 |
| L1处理 | 矩形100×45 | 居中 | 120 | rx=4 |
| L2判断 | 菱形80×70 | 居中 | 200 | 菱形判断 |
| L3A处理 | 矩形100×45 | 居中偏右 | 290 | 是分支 |
| L3B处理 | 矩形100×45 | 居中偏左 | 290 | 否分支 |
| L4汇总 | 矩形100×45 | 居中 | 360 | 合并处理 |
| 结束 | 椭圆rx=45 ry=22 | 居中 | 420 | 底部出口 |

### 比例原则

- 画布宽高比约 5:4 或 4:3
- 节点间距均匀（55px）
- 判断分支清晰（是/否标注）
- 汇合点用连接器圆点
- 循环路径用虚线

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
--true-branch: #22c55e;
--false-branch: #f97316;

/* minimal-dark */
--paper: #0f172a;
--ink: #f1f5f9;
--muted: #94a3b8;
--paper-2: #1e293b;
--accent: #60a5fa;
--link: #93c5fd;
--true-branch: #4ade80;
--false-branch: #fb923c;

/* full-editorial */
--paper: #fefefe;
--ink: #18181b;
--muted: #71717a;
--paper-2: #f4f4f5;
--accent: #e11d48;
--link: #be123c;
--true-branch: #16a34a;
--false-branch: #ea580c;
```

### 元素ID命名

```html
<g id="flowchart-container">     <!-- 主容器组 -->
  <g id="start-node">            <!-- 开始节点 -->
  <g id="process-step-1">        <!-- 处理节点 -->
  <g id="decision-1">           <!-- 判断节点 -->
  <g id="branch-yes">           <!-- 是分支 -->
  <g id="branch-no">            <!-- 否分支 -->
  <g id="connector-1">          <!-- 连接器 -->
  <g id="flow-line-1">          <!-- 连接线 -->
  <g id="end-node">             <!-- 结束节点 -->
</g>
```

### 类名约定

```html
<div class="flowchart">
  <div class="flowchart-start">开始</div>
  <div class="flowchart-process">处理步骤</div>
  <div class="flowchart-decision">判断条件</div>
  <div class="flowchart-branch branch-yes">是分支</div>
  <div class="flowchart-branch branch-no">否分支</div>
  <div class="flowchart-connector"></div>
  <div class="flowchart-line"></div>
  <div class="flowchart-end">结束</div>
</div>
```

## 7. 常见布局模式

### 线性流程

```
                      ┌─────────────┐
                      │    开始     │ ← 椭圆rx=45 ry=22
                      └──────┬──────┘
                             ▼
                      ┌─────────────┐
                      │  处理步骤1   │ ← 矩形100×45 rx=4
                      └──────┬──────┘
                             ▼
                      ┌─────────────┐
                      │  处理步骤2   │
                      └──────┬──────┘
                             ▼
                      ┌─────────────┐
                      │    结束     │
                      └─────────────┘
```

### 判断分支流程

```
                      ┌─────────────┐
                      │    开始     │
                      └──────┬──────┘
                             ▼
                       ◇─────────◇
                       │  是否?  │    ← 菱形80×70
                       ◇────┬────◇
                    是/      \否
              ┌──────────┐    ┌──────────┐
              │ 分支处理A │    │ 分支处理B │
              └────┬─────┘    └────┬─────┘
                   \            /
                    \          /
                      ┌──────┴──────┐
                      │    汇总     │
                      └──────┬──────┘
                             ▼
                      ┌─────────────┐
                      │    结束     │
                      └─────────────┘
```

### 循环返回流程

```
                      ┌─────────────┐
                      │    开始     │
                      └──────┬──────┘
                             ▼
                      ┌─────────────┐
                      │  处理步骤   │
                      └──────┬──────┘
                             ▼
                       ◇─────────◇
                       │  继续?   │
                       ◇────┬────◇
                    是/      \否
                   ┌──┴──┐    ┌──────────┐
                   │循环 │    │    结束   │
                   └──┬──┘    └──────────┘
                      │ ↑
                      └─┘   ← 虚线返回
```

### 节点强调策略

| 节点类型 | 典型策略 | 推荐强调色 |
|---------|---------|-----------|
| 当前处理 | accent半透明+粗边框 | `--accent` stroke-width=2 |
| 是分支 | 绿色标签 | `--true-branch` |
| 否分支 | 橙色标签 | `--false-branch` |
| 循环返回 | 虚线箭头 | `stroke-dasharray="5,3"` |

### 标签密度控制

- **端点**: 1个标签，字号11px，粗体
- **处理节点**: 1个标签，字号11px
- **判断节点**: 1个标签，字号10px
- **分支标注**: 是/否字号9px，颜色区分
- **连接线**: 不标注（通过位置隐式表达）

## 8. 质量检查清单

- [ ] 节点数量合理（不超过20个节点）
- [ ] 端点有开始和结束
- [ ] 处理节点用矩形rx=4
- [ ] 判断节点用菱形，标注是/否
- [ ] 连接线有箭头方向
- [ ] 循环返回用虚线
- [ ] 判断分支清晰标注
- [ ] 节点间距均匀（55px）
- [ ] accent强调当前处理步骤
- [ ] WCAG AA对比度（文字4.5:1，图形3:1）
- [ ] SVG响应式，viewBox设置正确
- [ ] 整体布局居中，四周留白均衡