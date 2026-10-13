# 时序图参考指南

## 1. 适用场景

时序图（Sequence Diagram）用于展示系统组件之间的消息交互顺序，适用于API调用流程、系统交互、微服务通信等场景。

| 场景 | 典型框架 |
|------|---------|
| API调用时序 | 客户端→网关→服务→数据库 |
| 微服务交互 | 服务A→消息队列→服务B→缓存 |
| 用户操作流程 | UI→业务层→数据层→外部API |
| 协议交互 | 客户端→TLS→服务端→数据库 |

## 2. 设计原则

- **目标密度**: 4/10（清晰参与者和消息）
- **参与者**: 顶部矩形标签，底部生命线
- **accent使用**: 当前交互路径用accent强调
- **布局**: 从上到下，左到右
- **连接**: 消息箭头（实心/空心/虚线）

## 3. 组件类型

### 参与者（Participant）

```html
<!-- 参与者标签 -->
<rect x="120" y="60" width="100" height="40" rx="4"
  fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="170" y="85" text-anchor="middle" font-size="11" font-weight="600"
  fill="var(--ink)">Client</text>

<!-- 参与者2 -->
<rect x="320" y="60" width="100" height="40" rx="4"
  fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="370" y="85" text-anchor="middle" font-size="11" font-weight="600"
  fill="var(--ink)">Server</text>

<!-- 参与者3（accent当前活跃） -->
<rect x="520" y="60" width="100" height="40" rx="4"
  fill="var(--accent)" opacity="0.15" stroke="var(--accent)" stroke-width="2"/>
<text x="570" y="85" text-anchor="middle" font-size="11" font-weight="600"
  fill="var(--accent)">Database</text>
```

### 生命线（Lifeline）

```html
<!-- 垂直虚线 -->
<line x1="170" y1="100" x2="170" y2="400" stroke="var(--ink)"
  stroke-width="1" stroke-dasharray="4,4"/>

<!-- 生命线2 -->
<line x1="370" y1="100" x2="370" y2="400" stroke="var(--ink)"
  stroke-width="1" stroke-dasharray="4,4"/>

<!-- 生命线3 -->
<line x1="570" y1="100" x2="570" y2="400" stroke="var(--ink)"
  stroke-width="1.5" stroke-dasharray="4,4"/>
```

### 激活条（Activation）

```html
<!-- 激活条（实心矩形） -->
<rect x="162" y="160" width="16" height="40"
  fill="var(--accent)" opacity="0.2" stroke="var(--accent)" stroke-width="1"/>

<!-- 嵌套激活（表示调用栈） -->
<rect x="162" y="210" width="16" height="30"
  fill="var(--ink)" opacity="0.15"/>
```

### 消息箭头

```html
<defs>
  <!-- 实心箭头（同步消息） -->
  <marker id="solid-arrow" markerWidth="10" markerHeight="10"
    refX="9" refY="5" orient="auto">
    <path d="M 0 0 L 10 5 L 0 10 Z" fill="var(--ink)"/>
  </marker>

  <!-- 空心箭头（异步消息） -->
  <marker id="hollow-arrow" markerWidth="10" markerHeight="10"
    refX="9" refY="5" orient="auto">
    <path d="M 0 0 L 10 5 L 0 10 Z" fill="none" stroke="var(--ink)" stroke-width="1"/>
  </marker>

  <!-- 点线箭头（返回消息） -->
  <marker id="dot-arrow" markerWidth="8" markerHeight="8"
    refX="7" refY="4" orient="auto">
    <circle cx="4" cy="4" r="3" fill="var(--muted)"/>
  </marker>
</defs>

<!-- 同步消息（实心箭头） -->
<line x1="170" y1="140" x2="370" y2="140"
  stroke="var(--ink)" stroke-width="1.5"
  marker-end="url(#solid-arrow)"/>
<text x="270" y="135" text-anchor="middle" font-size="9" fill="var(--ink)">GET /api</text>

<!-- 异步消息（空心箭头） -->
<line x1="370" y1="200" x2="570" y2="200"
  stroke="var(--ink)" stroke-width="1.5"
  marker-end="url(#hollow-arrow)"/>
<text x="470" y="195" text-anchor="middle" font-size="9" fill="var(--ink)">Query</text>

<!-- 返回消息（点线箭头） -->
<line x1="570" y1="250" x2="170" y2="250"
  stroke="var(--muted)" stroke-width="1" stroke-dasharray="2,2"
  marker-end="url(#dot-arrow)"/>
<text x="370" y="245" text-anchor="middle" font-size="9" fill="var(--muted)">Result</text>
```

### 自调用（Self-Invocation）

```html
<!-- 自调用框（折叠生命线） -->
<rect x="362" y="180" width="16" height="60"
  fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<line x1="370" y1="180" x2="370" y2="240" stroke="var(--ink)"
  stroke-width="0.75"/>
<!-- 自调用标签 -->
<text x="400" y="200" font-size="9" fill="var(--ink)">validate()</text>
```

## 4. 连接线规范

### 消息类型对照

| 类型 | 线型 | 箭头 | 说明 | 使用场景 |
|------|------|------|------|---------|
| **同步消息** | 实线 | 实心三角 | 调用→等待响应 | API调用、函数调用 |
| **异步消息** | 实线 | 空心三角 | 发送→不等待 | 事件驱动、消息队列 |
| **返回消息** | 虚线 | 点线圆 | 响应结果 | 函数返回值 |
| **创建消息** | 实线 | 实心三角 | 创建实例 | new Object() |
| **销毁消息** | 实线 | X | 销毁实例 | 资源释放 |

### 消息格式

```html
<!-- 带参数的同步消息 -->
<line x1="170" y1="160" x2="370" y2="160"
  stroke="var(--ink)" stroke-width="1.5"
  marker-end="url(#solid-arrow)"/>
<text x="240" y="155" font-size="9" fill="var(--ink)">login(user, pass)</text>

<!-- 带返回值的消息 -->
<line x1="370" y1="300" x2="170" y2="300"
  stroke="var(--muted)" stroke-width="1" stroke-dasharray="2,2"
  marker-end="url(#dot-arrow)"/>
<text x="270" y="295" font-size="9" fill="var(--muted)">Token</text>
```

## 5. 层级布局

### 坐标计算规则

假设画布宽度 W = 800，高度 H = 450，参与者宽度 PW = 100：

- 画布: 800 × 450
- 参与者数量: 4个（最大6个）
- 参与者X: 120, 320, 520, 720（间距200px）
- 生命线: 参与者中心X
- 消息层级间距: 40px
- 激活条宽度: 16px

### 参与者布局

| 参与者 | X坐标 | 说明 |
|--------|-------|------|
| Client | 120 | 左侧发起者 |
| Gateway | 320 | 第二参与者 |
| Server | 520 | 第三参与者 |
| Database | 720 | 右侧终点 |

### 消息时序

| 消息序号 | 类型 | 起点 | 终点 | Y坐标 | 标签 |
|----------|------|------|------|-------|------|
| 1 | 同步 | Client | Gateway | 140 | GET /api |
| 2 | 同步 | Gateway | Server | 200 | Forward |
| 3 | 异步 | Server | Database | 260 | Query |
| 4 | 返回 | Database | Server | 300 | Result |
| 5 | 返回 | Server | Gateway | 340 | Response |
| 6 | 返回 | Gateway | Client | 380 | JSON |

### 比例原则

- 画布宽高比约 16:9 或 8:5
- 参与者间距均匀（200px，最少150px）
- 消息垂直间距一致（40px）
- 参与者标签对齐顶部
- 激活条宽度一致（16px）

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
--async-color: #8b5cf6;
--return-color: #6b7280;

/* minimal-dark */
--paper: #0f172a;
--ink: #f1f5f9;
--muted: #94a3b8;
--paper-2: #1e293b;
--accent: #60a5fa;
--link: #93c5fd;
--async-color: #a78bfa;
--return-color: #94a3b8;

/* full-editorial */
--paper: #fefefe;
--ink: #18181b;
--muted: #71717a;
--paper-2: #f4f4f5;
--accent: #e11d48;
--link: #be123c;
--async-color: #7c3aed;
--return-color: #71717a;
```

### 元素ID命名

```html
<g id="sequence-container">         <!-- 主容器组 -->
  <g id="participants">             <!-- 参与者组 -->
    <g id="participant-client">     <!-- Client参与者 -->
    <g id="participant-server">     <!-- Server参与者 -->
    <g id="participant-database">   <!-- Database参与者 -->
  <g id="lifelines">               <!-- 生命线组 -->
    <g id="lifeline-client">        <!-- Client生命线 -->
  <g id="activations">             <!-- 激活条组 -->
    <g id="activation-client-1">     <!-- Client激活条1 -->
  <g id="messages">                 <!-- 消息组 -->
    <g id="message-1-sync">         <!-- 同步消息1 -->
    <g id="message-2-async">       <!-- 异步消息2 -->
    <g id="message-3-return">       <!-- 返回消息3 -->
  <g id="markers">                 <!-- 箭头标记定义 -->
</g>
```

### 类名约定

```html
<div class="sequence">
  <div class="sequence-participant">
    <div class="participant-label">Client</div>
    <div class="lifeline"></div>
    <div class="activation"></div>
  </div>
  <div class="sequence-message message-sync">
    <div class="message-arrow"></div>
    <div class="message-label">GET /api</div>
  </div>
  <div class="sequence-message message-async"></div>
  <div class="sequence-message message-return"></div>
</div>
```

## 7. 常见布局模式

### 经典API调用时序

```
  Client      Gateway      Server      Database
    │           │           │            │
    │──GET /api─▶│           │            │   ← 同步消息
    │           │──Forward──▶│            │   ← 同步消息
    │           │           │──Query────▶│   ← 异步消息
    │           │           │◀─Result────│   ← 返回消息
    │           │◀─Response─│            │   ← 返回消息
    │◀─JSON────│           │            │   ← 返回消息
    │           │           │            │
```

### 微服务异步时序

```
  API GW      Queue       Service A    Service B
    │           │           │            │
    │─Publish─▶│           │            │   ← 异步发布
    │           │─Dequeue─▶│            │   ← 异步消费
    │           │           │─Process──▶│   ← 异步处理
    │           │◀─Done─────│            │   ← 回调
    │◀─ACK─────│           │            │   ← 确认
```

### 自调用时序

```
  Service
    │
    │──call()──▶
    │            ├─validate()
    │            ├─transform()
    │            └─persist()
    │◀─result───
    │
```

### 消息强调策略

| 消息类型 | 线型 | 颜色 | 箭头样式 | 使用场景 |
|---------|------|------|---------|---------|
| 同步请求 | 实线 | `--ink` | 实心三角 | 函数调用 |
| 异步发送 | 实线 | `--async-color` | 空心三角 | 事件发布 |
| 返回响应 | 虚线 | `--muted` | 点线圆 | 返回值 |
| 当前交互 | 实线 | `--accent` | 实心三角 | 当前分析路径 |
| 创建实例 | 实线 | `--accent` | 实心三角 | new操作 |

### 标签密度控制

- **参与者标签**: 1个标签，字号11px，粗体
- **消息标签**: 1个标签，字号9px，置于消息线上方
- **自调用标签**: 1个标签，字号9px，置于框内
- 激活条不标注（隐式表达调用深度）

## 8. 质量检查清单

- [ ] 参与者数量不超过6个
- [ ] 参与者标签居中，字号11px，粗体
- [ ] 生命线为垂直虚线，间距均匀
- [ ] 同步消息用实线+实心箭头
- [ ] 异步消息用实线+空心箭头
- [ ] 返回消息用虚线+点线箭头
- [ ] 消息间距均匀（40px）
- [ ] 激活条宽度一致（16px）
- [ ] 当前交互路径用accent颜色强调
- [ ] WCAG AA对比度（文字4.5:1，图形3:1）
- [ ] SVG响应式，viewBox设置正确
- [ ] 整体布局居中，四周留白均衡