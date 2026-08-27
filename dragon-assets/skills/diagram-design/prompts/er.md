# ER Diagram Prompt

## 适用场景
数据库设计、实体关系、数据模型、概念数据模型

## 设计原则
- **目标密度**: 4/10（清晰关系）
- **实体数量**: 约5-7个实体
- **accent使用**: 主键用accent强调
- **关系线**: Crow's foot表示基数

## 颜色Tokens（minimal-light）
```css
--paper: #ffffff;
--ink: #1a1a2e;
--muted: #6b7280;
--paper-2: #f8fafc;
--accent: #3b82f6;
--link: #2563eb;
```

## 颜色Tokens（minimal-dark）
```css
--paper: #0f172a;
--ink: #f1f5f9;
--muted: #94a3b8;
--paper-2: #1e293b;
--accent: #60a5fa;
--link: #93c5fd;
```

## 颜色Tokens（full-editorial）
```css
--paper: #fefefe;
--ink: #18181b;
--muted: #71717a;
--paper-2: #f4f4f5;
--accent: #e11d48;
--link: #be123c;
```

## 字体Tokens
```css
--title: 'Instrument Serif', Georgia, serif;
--node-name: 'Inter', system-ui, sans-serif;
--sublabel: 'JetBrains Mono', 'Fira Code', monospace;
```

## 实体表模板

```html
<!-- 实体表头 -->
<rect x="X" y="Y" width="160" height="30" rx="4,4,0,0" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="X+80" y="Y+20" text-anchor="middle" font-family="var(--node-name)" font-size="13" font-weight="600" fill="var(--ink)">EntityName</text>

<!-- 属性行 -->
<rect x="X" y="Y+30" width="160" height="24" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<text x="X+15" y="Y+46" font-family="var(--node-name)" font-size="11" fill="var(--ink)">🔑 id: UUID</text>

<rect x="X" y="Y+54" width="160" height="24" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<text x="X+15" y="Y+70" font-family="var(--node-name)" font-size="11" fill="var(--ink)">  name: VARCHAR</text>

<rect x="X" y="Y+78" width="160" height="24" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/>
<text x="X+15" y="Y+94" font-family="var(--node-name)" font-size="11" fill="var(--ink)">  email: VARCHAR</text>

<!-- 主键样式 -->
<rect x="X" y="Y+30" width="160" height="24" fill="var(--accent)" opacity="0.1" stroke="var(--accent)" stroke-width="1"/>
<text x="X+15" y="Y+46" font-family="var(--node-name)" font-size="11" fill="var(--accent)">🔑 id: UUID</text>

<!-- 外键样式 -->
<text x="X+15" y="Y+94" font-family="var(--node-name)" font-size="11" fill="var(--link)">🔗 user_id: UUID</text>
```

## Crow's Foot关系模板

```html
<!-- 一对多 (1:N) -->
<!-- 一端：单线 -->
<line x1="X1" y1="Y1" x2="X2" y2="Y2" stroke="var(--ink)" stroke-width="1.5"/>
<!-- 多端：Crow's foot -->
<line x1="X2-10" y1="Y2-8" x2="X2" y2="Y2" stroke="var(--ink)" stroke-width="1.5"/>
<line x1="X2-10" y1="Y2+8" x2="X2" y2="Y2" stroke="var(--ink)" stroke-width="1.5"/>
<line x1="X2-15" y1="Y2" x2="X2" y2="Y2" stroke="var(--ink)" stroke-width="1.5"/>

<!-- 多对多 (N:M) -->
<!-- 两端都是Crow's foot -->
<!-- ... -->

<!-- 一对一 (1:1) -->
<line x1="X1" y1="Y1" x2="X2" y2="Y2" stroke="var(--ink)" stroke-width="1.5"/>
<line x1="X1+5" y1="Y1-5" x2="X1" y2="Y1" stroke="var(--ink)" stroke-width="1.5"/>
<line x1="X1+5" y1="Y1+5" x2="X1" y2="Y1" stroke="var(--ink)" stroke-width="1.5"/>
```

## 关系标签模板

```html
<!-- 关系标签 -->
<text x="标签X" y="标签Y" font-family="var(--node-name)" font-size="10" fill="var(--muted)" text-anchor="middle">has_many</text>
```

## 示例：电商ER图
```html
<svg viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --paper: #ffffff;
      --ink: #1a1a2e;
      --muted: #6b7280;
      --paper-2: #f8fafc;
      --accent: #3b82f6;
      --link: #2563eb;
    }
    text { font-family: 'Inter', system-ui, sans-serif; }
  </style>
  <rect width="800" height="500" fill="var(--paper)"/>

  <!-- 标题 -->
  <text x="400" y="30" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">电商数据库 ER 图</text>

  <!-- User 实体 -->
  <rect x="50" y="80" width="150" height="120" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="125" y="100" text-anchor="middle" font-size="13" font-weight="600" fill="var(--ink)">User</text>
  <line x1="50" y1="108" x2="200" y2="108" stroke="var(--ink)" stroke-width="1"/>
  <text x="60" y="125" font-size="10" fill="var(--accent)">🔑 id: UUID</text>
  <text x="60" y="145" font-size="10" fill="var(--ink)">  name: VARCHAR</text>
  <text x="60" y="165" font-size="10" fill="var(--ink)">  email: VARCHAR</text>
  <text x="60" y="185" font-size="10" fill="var(--ink)">  created_at</text>

  <!-- Order 实体 -->
  <rect x="320" y="80" width="150" height="120" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="395" y="100" text-anchor="middle" font-size="13" font-weight="600" fill="var(--ink)">Order</text>
  <line x1="320" y1="108" x2="470" y2="108" stroke="var(--ink)" stroke-width="1"/>
  <text x="330" y="125" font-size="10" fill="var(--accent)">🔑 id: UUID</text>
  <text x="330" y="145" font-size="10" fill="var(--link)">🔗 user_id: UUID</text>
  <text x="330" y="165" font-size="10" fill="var(--ink)">  total: DECIMAL</text>
  <text x="330" y="185" font-size="10" fill="var(--ink)">  status: VARCHAR</text>

  <!-- Product 实体 -->
  <rect x="590" y="80" width="150" height="120" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="665" y="100" text-anchor="middle" font-size="13" font-weight="600" fill="var(--ink)">Product</text>
  <line x1="590" y1="108" x2="740" y2="108" stroke="var(--ink)" stroke-width="1"/>
  <text x="600" y="125" font-size="10" fill="var(--accent)">🔑 id: UUID</text>
  <text x="600" y="145" font-size="10" fill="var(--ink)">  name: VARCHAR</text>
  <text x="600" y="165" font-size="10" fill="var(--ink)">  price: DECIMAL</text>
  <text x="600" y="185" font-size="10" fill="var(--ink)">  stock: INT</text>

  <!-- 关系线 User -> Order -->
  <line x1="200" y1="140" x2="320" y2="140" stroke="var(--ink)" stroke-width="1.5"/>
  <line x1="310" y1="132" x2="320" y2="140" stroke="var(--ink)" stroke-width="1.5"/>
  <line x1="310" y1="148" x2="320" y2="140" stroke="var(--ink)" stroke-width="1.5"/>
  <line x1="315" y1="140" x2="310" y2="140" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="260" y="135" text-anchor="middle" font-size="9" fill="var(--muted)">1:N</text>

  <!-- OrderItem 实体 -->
  <rect x="320" y="280" width="150" height="100" rx="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="395" y="300" text-anchor="middle" font-size="13" font-weight="600" fill="var(--ink)">OrderItem</text>
  <line x1="320" y1="308" x2="470" y2="308" stroke="var(--ink)" stroke-width="1"/>
  <text x="330" y="325" font-size="10" fill="var(--accent)">🔑 id: UUID</text>
  <text x="330" y="345" font-size="10" fill="var(--link)">🔗 order_id: UUID</text>
  <text x="330" y="365" font-size="10" fill="var(--link)">🔗 product_id: UUID</text>

  <!-- 关系线 Order -> OrderItem -->
  <line x1="395" y1="200" x2="395" y2="280" stroke="var(--ink)" stroke-width="1.5"/>
  <line x1="387" y1="270" x2="395" y2="280" stroke="var(--ink)" stroke-width="1.5"/>
  <line x1="403" y1="270" x2="395" y2="280" stroke="var(--ink)" stroke-width="1.5"/>
  <line x1="395" y1="275" x2="395" y2="280" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="410" y="245" font-size="9" fill="var(--muted)">1:N</text>
</svg>
```

## 质量检查清单
- [ ] 实体数量 ≤ 7
- [ ] 主键清晰标记（🔑）
- [ ] 外键清晰标记（🔗）
- [ ] Crow's foot关系正确
- [ ] WCAG AA对比度
