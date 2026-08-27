# Architecture Diagram Prompt

## 适用场景
软件架构、系统拓扑、网络架构、微服务架构、云架构

## 设计原则
- **目标密度**: 4/10（清晰组件）
- **组件数量**: 约8-12个
- **accent使用**: 核心组件或关键路径用accent
- **布局**: 分层或网格

## 颜色Tokens（minimal-light）
```css
--paper: #ffffff;
--ink: #1a1a2e;
--muted: #6b7280;
--paper-2: #f8fafc;
--accent: #3b82f6;
--link: #2563eb;
--service: #10b981;
--database: #f59e0b;
--external: #6b7280;
```

## 颜色Tokens（minimal-dark）
```css
--paper: #0f172a;
--ink: #f1f5f9;
--muted: #94a3b8;
--paper-2: #1e293b;
--accent: #60a5fa;
--link: #93c5fd;
--service: #34d399;
--database: #fbbf24;
--external: #64748b;
```

## 颜色Tokens（full-editorial）
```css
--paper: #fefefe;
--ink: #18181b;
--muted: #71717a;
--paper-2: #f4f4f5;
--accent: #e11d48;
--link: #be123c;
--service: #059669;
--database: #d97706;
--external: #71717a;
```

## 字体Tokens
```css
--title: 'Instrument Serif', Georgia, serif;
--node-name: 'Inter', system-ui, sans-serif;
--sublabel: 'JetBrains Mono', 'Fira Code', monospace;
```

## 组件模板

```html
<!-- 服务组件 -->
<rect x="X" y="Y" width="100" height="60" rx="6" fill="var(--service)" opacity="0.1" stroke="var(--service)" stroke-width="2"/>
<text x="X+50" y="Y+25" text-anchor="middle" font-family="var(--node-name)" font-size="11" font-weight="600" fill="var(--service)">服务</text>
<text x="X+50" y="Y+45" text-anchor="middle" font-family="var(--sublabel)" font-size="9" fill="var(--muted)">Service</text>

<!-- 数据库组件 -->
<ellipse cx="X+50" cy="Y+20" rx="40" ry="15" fill="var(--database)" opacity="0.1" stroke="var(--database)" stroke-width="2"/>
<rect x="X+10" y="Y+20" width="80" height="30" fill="var(--database)" opacity="0.1" stroke="var(--database)" stroke-width="2"/>
<ellipse cx="X+50" cy="Y+50" rx="40" ry="15" fill="var(--paper)" stroke="var(--database)" stroke-width="2"/>
<text x="X+50" y="Y+42" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--database)">Database</text>

<!-- 外部系统 -->
<rect x="X" y="Y" width="100" height="60" rx="6" fill="var(--external)" opacity="0.1" stroke="var(--external)" stroke-width="1.5" stroke-dasharray="4,4"/>
<text x="X+50" y="Y+30" text-anchor="middle" font-family="var(--node-name)" font-size="10" fill="var(--muted)">External</text>

<!-- 核心组件（accent） -->
<rect x="X" y="Y" width="100" height="60" rx="6" fill="var(--accent)" opacity="0.15" stroke="var(--accent)" stroke-width="2"/>
<text x="X+50" y="Y+30" text-anchor="middle" font-family="var(--node-name)" font-size="11" font-weight="600" fill="var(--accent)">核心服务</text>
```

## 连接线模板

```html
<!-- 同步调用 -->
<path d="M X1 Y1 L X2 Y2" stroke="var(--link)" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>

<!-- 异步消息 -->
<path d="M X1 Y1 L X2 Y2" stroke="var(--link)" stroke-width="1.5" fill="none" stroke-dasharray="4,2" marker-end="url(#arrow)"/>

<!-- 数据库连接 -->
<path d="M X1 Y1 L X2 Y2" stroke="var(--database)" stroke-width="1.5" fill="none" marker-end="url(#db-arrow)"/>
```

## 示例：微服务架构
```html
<svg viewBox="0 0 700 500" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --paper: #ffffff;
      --ink: #1a1a2e;
      --muted: #6b7280;
      --paper-2: #f8fafc;
      --accent: #3b82f6;
      --link: #2563eb;
      --service: #10b981;
      --database: #f59e0b;
      --external: #6b7280;
    }
    text { font-family: 'Inter', system-ui, sans-serif; }
  </style>
  <rect width="700" height="500" fill="var(--paper)"/>

  <!-- 标题 -->
  <text x="350" y="30" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">微服务架构</text>

  <!-- 客户端层 -->
  <rect x="50" y="60" width="600" height="50" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1"/>
  <text x="350" y="90" text-anchor="middle" font-size="11" fill="var(--ink)">客户端 Client</text>
  <text x="100" y="90" text-anchor="middle" font-size="9" fill="var(--muted)">Web App</text>
  <text x="600" y="90" text-anchor="middle" font-size="9" fill="var(--muted)">Mobile</text>

  <!-- API Gateway -->
  <rect x="250" y="130" width="200" height="50" rx="6" fill="var(--accent)" opacity="0.15" stroke="var(--accent)" stroke-width="2"/>
  <text x="350" y="160" text-anchor="middle" font-size="12" font-weight="600" fill="var(--accent)">API Gateway</text>

  <!-- 服务层 -->
  <rect x="80" y="210" width="120" height="60" rx="6" fill="var(--service)" opacity="0.1" stroke="var(--service)" stroke-width="2"/>
  <text x="140" y="240" text-anchor="middle" font-size="11" fill="var(--service)">用户服务</text>

  <rect x="230" y="210" width="120" height="60" rx="6" fill="var(--service)" opacity="0.1" stroke="var(--service)" stroke-width="2"/>
  <text x="290" y="240" text-anchor="middle" font-size="11" fill="var(--service)">订单服务</text>

  <rect x="380" y="210" width="120" height="60" rx="6" fill="var(--service)" opacity="0.1" stroke="var(--service)" stroke-width="2"/>
  <text x="440" y="240" text-anchor="middle" font-size="11" fill="var(--service)">支付服务</text>

  <rect x="530" y="210" width="120" height="60" rx="6" fill="var(--service)" opacity="0.1" stroke="var(--service)" stroke-width="2"/>
  <text x="590" y="240" text-anchor="middle" font-size="11" fill="var(--service)">通知服务</text>

  <!-- 消息队列 -->
  <rect x="80" y="310" width="540" height="40" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1"/>
  <text x="350" y="335" text-anchor="middle" font-size="10" fill="var(--ink)">消息队列 Message Queue</text>

  <!-- 数据层 -->
  <ellipse cx="140" cy="400" rx="40" ry="12" fill="var(--database)" opacity="0.1" stroke="var(--database)" stroke-width="2"/>
  <rect x="100" cy="390" width="80" height="25" fill="var(--database)" opacity="0.1" stroke="var(--database)" stroke-width="2"/>
  <ellipse cx="140" cy="415" rx="40" ry="12" fill="var(--paper)" stroke="var(--database)" stroke-width="2"/>
  <text x="140" y="407" text-anchor="middle" font-size="9" fill="var(--database)">用户DB</text>

  <ellipse cx="290" cy="400" rx="40" ry="12" fill="var(--database)" opacity="0.1" stroke="var(--database)" stroke-width="2"/>
  <rect x="250" cy="390" width="80" height="25" fill="var(--database)" opacity="0.1" stroke="var(--database)" stroke-width="2"/>
  <ellipse cx="290" cy="415" rx="40" ry="12" fill="var(--paper)" stroke="var(--database)" stroke-width="2"/>
  <text x="290" y="407" text-anchor="middle" font-size="9" fill="var(--database)">订单DB</text>

  <ellipse cx="440" cy="400" rx="40" ry="12" fill="var(--database)" opacity="0.1" stroke="var(--database)" stroke-width="2"/>
  <rect x="400" cy="390" width="80" height="25" fill="var(--database)" opacity="0.1" stroke="var(--database)" stroke-width="2"/>
  <ellipse cx="440" cy="415" rx="40" ry="12" fill="var(--paper)" stroke="var(--database)" stroke-width="2"/>
  <text x="440" y="407" text-anchor="middle" font-size="9" fill="var(--database)">支付DB</text>

  <!-- 连接线 -->
  <path d="M 350 110 L 350 130" stroke="var(--ink)" stroke-width="1" marker-end="url(#arrow)"/>
  <path d="M 250 155 L 200 210" stroke="var(--ink)" stroke-width="1" marker-end="url(#arrow)"/>
  <path d="M 350 155 L 290 210" stroke="var(--ink)" stroke-width="1" marker-end="url(#arrow)"/>
  <path d="M 450 155 L 440 210" stroke="var(--ink)" stroke-width="1" marker-end="url(#arrow)"/>
  <path d="M 530 240 L 590 270" stroke="var(--ink)" stroke-width="1" marker-end="url(#arrow)"/>
  <path d="M 140 270 L 140 310" stroke="var(--ink)" stroke-width="1" marker-end="url(#arrow)"/>
  <path d="M 290 270 L 290 310" stroke="var(--ink)" stroke-width="1" marker-end="url(#arrow)"/>
  <path d="M 440 270 L 440 310" stroke="var(--ink)" stroke-width="1" marker-end="url(#arrow)"/>
  <path d="M 140 350 L 140 390" stroke="var(--database)" stroke-width="1" marker-end="url(#arrow)"/>
  <path d="M 290 350 L 290 390" stroke="var(--database)" stroke-width="1" marker-end="url(#arrow)"/>
  <path d="M 440 350 L 440 390" stroke="var(--database)" stroke-width="1" marker-end="url(#arrow)"/>

  <!-- 箭头定义 -->
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M 0 0 L 8 4 L 0 8 Z" fill="var(--ink)"/>
    </marker>
  </defs>
</svg>
```

## 质量检查清单
- [ ] 组件数量 ≤ 12
- [ ] 层级清晰分离
- [ ] 连接线无交叉
- [ ] 数据库符号正确
- [ ] WCAG AA对比度
