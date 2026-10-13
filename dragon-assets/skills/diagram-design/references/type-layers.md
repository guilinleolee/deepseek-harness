# 层级图参考指南

## 1. 适用场景

层级图（Layers Diagram）用于展示具有明确上下级关系的分层结构，适用于系统架构、技术栈展示、协议栈等场景。

| 场景 | 典型框架 |
|------|---------|
| 系统架构 | 表现层→业务层→数据层→基础设施层 |
| OSI七层模型 | 应用层→传输层→网络层→物理层 |
| 技术栈 | 前端框架→状态管理→API层→数据库 |
| 安全架构 | 边界防护→身份认证→数据加密→审计日志 |
| 容器编排 | Pod→Service→Ingress→ConfigMap |

## 2. 设计原则

- **目标密度**: 4/10（清晰层级）
- **层级数量**: 约4-6层，不超过8层
- **accent使用**: 当前层级或关键层用accent强调
- **布局**: 垂直堆叠，高度一致
- **连接**: 层间连接使用箭头或虚线

## 3. 组件类型

### 主容器

```html
<!-- 顶层容器（通常用于标题层） -->
<rect x="100" y="60" width="400" height="45" rx="8"
  fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="300" y="88" text-anchor="middle" font-size="13" font-weight="600"
  fill="var(--ink)">Layer 1</text>
```

### 中间层

```html
<!-- 普通中间层 -->
<rect x="100" y="115" width="400" height="45" rx="4"
  fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<text x="300" y="143" text-anchor="middle" font-size="12"
  fill="var(--ink)">Layer 2</text>
```

### 关键层（accent）

```html
<!-- accent关键层 -->
<rect x="100" y="225" width="400" height="45" rx="4"
  fill="var(--accent)" opacity="0.1" stroke="var(--accent)" stroke-width="2"/>
<text x="300" y="253" text-anchor="middle" font-size="12" font-weight="600"
  fill="var(--accent)">关键层 Key Layer</text>
```

### 协议/技术标签

```html
<!-- 左侧标签（协议名） -->
<text x="60" y="88" text-anchor="end" font-size="10" fill="var(--muted)">HTTP/FTP</text>

<!-- 右侧标签（实现技术） -->
<text x="540" y="88" text-anchor="start" font-size="10" fill="var(--muted)">SMTP/POP</text>
```

### 层间连接箭头

```html
<defs>
  <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M 0 0 L 8 4 L 0 8 Z" fill="var(--ink)"/>
  </marker>
</defs>

<!-- 层间连接线 -->
<line x1="520" y1="100" x2="520" y2="340" stroke="var(--ink)" stroke-width="1" stroke-dasharray="4,2"/>
```

## 4. 连接线规范

### 单层连接

```html
<!-- 垂直连接箭头 -->
<path d="M 520 105 L 520 115" stroke="var(--ink)" stroke-width="1"
  fill="none" marker-end="url(#arrow)"/>
```

### 水平连接

```html
<!-- 层内水平连接 -->
<line x1="100" y1="235" x2="550" y2="235"
  stroke="var(--ink)" stroke-width="1" stroke-dasharray="3,3"/>
```

### 数据流向

```html
<!-- 数据流虚线 -->
<path d="M 150 235 L 150 280 L 200 280" stroke="var(--link)"
  stroke-width="1.5" stroke-dasharray="4,2" fill="none"/>
```

## 5. 层级布局

### 坐标计算规则

假设画布宽度 W = 600，高度 H = 500，层高 LH = 45，层间距 = 10：

- 画布: 600 × 500
- 起始位置: (100, 60)
- 层宽: 400
- 层高: 45
- 层间距: 10
- 每层起始Y: 60 + n × (45 + 10)

### 层级坐标映射

| 层级 | 起始Y | 中心Y | 说明 |
|------|-------|--------|------|
| Layer 7 | 60 | 82 | 顶层（rx=8） |
| Layer 6 | 115 | 137 | 中间层 |
| Layer 5 | 170 | 192 | 中间层 |
| Layer 4 | 225 | 247 | **accent层** |
| Layer 3 | 280 | 302 | 中间层 |
| Layer 2 | 335 | 357 | 中间层 |
| Layer 1 | 390 | 412 | 底层（rx=8） |

### 标签位置

| 标签位置 | X坐标 | Y计算 |
|---------|-------|--------|
| 左侧标签 | X - 40 | 中心Y |
| 右侧标签 | X + 层宽 + 40 | 中心Y |

### 比例原则

- 画布宽高比约 6:5 或 4:3
- 层级条高度一致（40-50px）
- 层级条水平居中
- 左右标签对齐各层中心

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
<g id="layers-container">         <!-- 主容器组 -->
  <g id="layer-7">                <!-- 各层级 -->
  <g id="layer-6">
  <g id="layer-5">
  <g id="layer-4-accent">        <!-- accent层 -->
  <g id="layer-3">
  <g id="layer-2">
  <g id="layer-1">
  <g id="left-labels">           <!-- 左侧标签组 -->
  <g id="right-labels">          <!-- 右侧标签组 -->
  <g id="connections">           <!-- 连接线组 -->
</g>
```

### 类名约定

```html
<div class="layers">
  <div class="layer layer-top">              <!-- 顶层 -->
  <div class="layer layer-middle">           <!-- 中间层 -->
  <div class="layer layer-accent">           <!-- accent层 -->
  <div class="layer layer-bottom">           <!-- 底层 -->
  <div class="layer-label layer-label-left">
  <div class="layer-label layer-label-right">
```

## 7. 常见布局模式

### OSI七层模型

```
                    OSI七层模型
    ┌─────────────────────────────────────────┐
    │ Layer 7  应用层     Application          │ ← rx=8, accent强调
    ├─────────────────────────────────────────┤
    │ Layer 6  表示层     Presentation         │
    ├─────────────────────────────────────────┤
    │ Layer 5  会话层     Session              │
    ├─────────────────────────────────────────┤
    │ Layer 4  传输层     Transport           │
    ├─────────────────────────────────────────┤
    │ Layer 3  网络层     Network              │
    ├─────────────────────────────────────────┤
    │ Layer 2  数据链路层  Data Link            │
    ├─────────────────────────────────────────┤
    │ Layer 1  物理层     Physical             │ ← rx=8
    └─────────────────────────────────────────┘

左侧标签:         右侧标签:
HTTP/FTP          SMTP/POP
TLS/SSL          MIME
NetBIOS          RPC/SQL
TCP/UDP          SPX
IP               ICMP
MAC              PPP
电信号            光/电
```

### Web应用架构

```
                    Web应用架构
    ┌─────────────────────────────────────────┐
    │       表现层  Presentation              │ ← rx=8, paper-2
    ├─────────────────────────────────────────┤
    │       业务层  Business Logic            │ ← accent强调
    ├─────────────────────────────────────────┤
    │       数据层  Data Access               │
    ├─────────────────────────────────────────┤
    │       基础设施  Infrastructure         │ ← rx=8
    └─────────────────────────────────────────┘

左侧:                          右侧:
HTML/CSS/JS                   React/Vue
REST API                      GraphQL
ORM/Database                  SQL/NoSQL
Cloud Provider                Docker/K8s
```

### 层级强调策略

| 层级位置 | 典型策略 | 推荐强调色 |
|---------|---------|-----------|
| 顶层（入口） | 强调入口层 | `--paper-2` + `--accent`边框 |
| 中间层（核心逻辑） | 强调核心业务层 | `--accent`半透明填充 |
| 底层（基础设施） | 强调基础层 | `--paper-2` 填充 |
| 当前活跃层 | 高亮显示 | `--accent`边框 + 半透明填充 |

## 8. 质量检查清单

- [ ] 层级数量 4-8层，不超过8层
- [ ] 每层高度一致（±2px容差）
- [ ] 层间连接线清晰，不交叉
- [ ] 协议/技术标签左右对齐
- [ ] accent层正确使用强调色
- [ ] 层级rx圆角统一（顶层/底层8px，中间4px）
- [ ] 标题在顶部居中
- [ ] 标签可读性良好
- [ ] WCAG AA对比度（文字4.5:1，图形3:1）
- [ ] viewBox响应式设置正确
- [ ] 整体布局居中，四周留白均衡
