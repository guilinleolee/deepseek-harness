# ER图参考指南

## 1. 适用场景

ER图（Entity-Relationship Diagram）用于展示数据实体及其相互关系，适用于数据库设计、概念建模、系统分析等场景。

| 场景 | 典型框架 |
|------|---------|
| 数据库设计 | 表结构→关系→约束 |
| 概念建模 | 业务实体→属性→关联 |
| 系统分析 | 数据流→实体→关系 |
| API设计 | 资源建模→实体映射 |

## 2. 设计原则

- **目标密度**: 4/10（清晰实体边界）
- **实体形状**: 矩形分三行（表头/主键/属性）
- **accent使用**: 主键用accent强调，外键用link色
- **布局**: 从左到右或从上到下
- **连接**: Crow's Foot基数表示法

## 3. 组件类型

### 实体表（Entity Table）

```html
<!-- 实体容器 -->
<rect x="100" y="100" width="180" height="135" rx="4" fill="var(--paper-2)"
  stroke="var(--ink)" stroke-width="1.5"/>

<!-- 表头 -->
<rect x="100" y="100" width="180" height="28" rx="4,4,0,0"
  fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
<text x="190" y="119" text-anchor="middle" font-size="11" font-weight="600"
  fill="var(--ink)">User</text>

<!-- 分隔线 -->
<line x1="100" y1="128" x2="280" y2="128" stroke="var(--ink)" stroke-width="1"/>

<!-- 主键行 -->
<rect x="100" y="128" width="180" height="24" fill="var(--paper)"
  stroke="var(--ink)" stroke-width="1"/>
<text x="115" y="144" font-size="9" fill="var(--accent)">🔑</text>
<text x="128" y="144" font-size="9" fill="var(--ink)">id</text>
<text x="245" y="144" text-anchor="end" font-size="8" fill="var(--muted)">INT PK</text>

<!-- 普通属性行 -->
<rect x="100" y="152" width="180" height="24" fill="var(--paper)"
  stroke="var(--ink)" stroke-width="1"/>
<text x="115" y="168" font-size="9" fill="var(--ink)">email</text>
<text x="245" y="168" text-anchor="end" font-size="8" fill="var(--muted)">VARCHAR</text>

<!-- 外键行 -->
<rect x="100" y="176" width="180" height="24" fill="var(--paper)"
  stroke="var(--ink)" stroke-width="1"/>
<text x="115" y="192" font-size="9" fill="var(--link)">🔗</text>
<text x="128" y="192" font-size="9" fill="var(--ink)">role_id</text>
<text x="245" y="192" text-anchor="end" font-size="8" fill="var(--muted)">INT FK</text>

<!-- 底部圆角修正 -->
<rect x="100" y="200" width="180" height="8" fill="var(--paper-2)"
  stroke="var(--ink)" stroke-width="1" stroke-dasharray="0,180"/>
<path d="M 100 208 L 100 200 L 280 200 L 280 208" stroke="var(--ink)"
  stroke-width="1" fill="none"/>
```

### Crow's Foot基数表示

```html
<!-- 一对多 (1:N) -->
<line x1="280" y1="168" x2="380" y2="168" stroke="var(--ink)" stroke-width="1.5"/>
<!-- Crow's Foot -->
<line x1="380" y1="160" x2="380" y2="176" stroke="var(--ink)" stroke-width="1.5"/>
<line x1="380" y1="160" x2="395" y2="168" stroke="var(--ink)" stroke-width="1.5"/>
<line x1="380" y1="176" x2="395" y2="168" stroke="var(--ink)" stroke-width="1.5"/>

<!-- 多对多 (N:M) -->
<line x1="280" y1="300" x2="380" y2="300" stroke="var(--ink)" stroke-width="1.5"/>
<!-- Crow's Foot 左 -->
<line x1="280" y1="292" x2="280" y2="308" stroke="var(--ink)" stroke-width="1.5"/>
<line x1="265" y1="292" x2="280" y2="300" stroke="var(--ink)" stroke-width="1.5"/>
<line x1="265" y1="308" x2="280" y2="300" stroke="var(--ink)" stroke-width="1.5"/>
<!-- Crow's Foot 右 -->
<line x1="380" y1="292" x2="380" y2="308" stroke="var(--ink)" stroke-width="1.5"/>
<line x1="380" y1="292" x2="395" y2="300" stroke="var(--ink)" stroke-width="1.5"/>
<line x1="380" y1="308" x2="395" y2="300" stroke="var(--ink)" stroke-width="1.5"/>

<!-- 一对一 (1:1) -->
<line x1="280" y1="120" x2="380" y2="120" stroke="var(--ink)" stroke-width="1.5"/>
<!-- 单线 -->
<line x1="380" y1="115" x2="390" y2="120" stroke="var(--ink)" stroke-width="1.5"/>
<line x1="390" y1="115" x2="380" y2="120" stroke="var(--ink)" stroke-width="1.5"/>
<!-- 单线 -->
<line x1="280" y1="115" x2="270" y2="120" stroke="var(--ink)" stroke-width="1.5"/>
<line x1="270" y1="115" x2="280" y2="120" stroke="var(--ink)" stroke-width="1.5"/>
```

## 4. 连接线规范

### 基数关系线

```html
<!-- 关系标签 -->
<rect x="320" y="155" width="40" height="26" rx="3" fill="var(--paper)"
  stroke="var(--ink)" stroke-width="1"/>
<text x="340" y="172" text-anchor="middle" font-size="9" fill="var(--ink)">1:N</text>

<!-- 虚线弱关系 -->
<line x1="200" y1="400" x2="300" y2="400" stroke="var(--ink)"
  stroke-width="1" stroke-dasharray="5,3"/>

<!-- 关系动词标注 -->
<text x="450" y="350" font-size="10" fill="var(--muted)">belongs_to</text>
<text x="450" y="365" font-size="10" fill="var(--muted)">has_many</text>
```

## 5. 层级布局

### 坐标计算规则

假设画布宽度 W = 900，高度 H = 500，实体宽 EW = 180，实体高 EH = 135：

- 画布: 900 × 500
- 实体间距: 100px
- 关系标签: 40×26px，rx=3
- 基数符号: 15×16px

### 实体坐标映射

| 位置 | X坐标 | Y坐标 | 说明 |
|------|-------|-------|------|
| 左上 | 100 | 60 | 第一个实体 |
| 右上方 | 360 | 60 | 一对多关系右方 |
| 右下方 | 360 | 280 | 多对多关系右方 |
| 下方 | 100 | 350 | 弱实体/子实体 |

### 比例原则

- 画布宽高比约 9:5 或 2:1
- 实体宽度一致（180px）
- 实体高度根据属性数量动态调整
- 关系线不交叉
- 关系标签居中放置

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
<g id="er-container">           <!-- 主容器组 -->
  <g id="entity-user">         <!-- 用户实体 -->
  <g id="entity-order">        <!-- 订单实体 -->
  <g id="entity-product">      <!-- 产品实体 -->
  <g id="entity-role">         <!-- 角色实体 -->
  <g id="relationship-1n">     <!-- 一对多关系 -->
  <g id="relationship-nm">     <!-- 多对多关系 -->
  <g id="cardinality-notation"><!-- 基数符号 -->
</g>
```

### 类名约定

```html
<div class="er">
  <div class="entity">
    <div class="entity-header">表名</div>
    <div class="entity-row entity-row-pk">🔑 主键</div>
    <div class="entity-row">普通属性</div>
    <div class="entity-row entity-row-fk">🔗 外键</div>
  </div>
  <div class="relationship">
    <div class="cardinality">1:N</div>
  </div>
</div>
```

## 7. 常见布局模式

### 经典电商ER图

```
┌─────────────┐         ┌─────────────┐
│   User      │ 1:N   │   Order     │
│─────────────│────────│─────────────│
│🔑 id        │        │🔑 id        │
│   email     │        │🔗 user_id   │
│   name      │        │🔗 addr_id   │
│🔗 role_id  │        │   total     │
│   created   │        │   status   │
└─────────────┘        └──────┬──────┘
       │                     │
       │ 1:N                 │ N:M
       ▼                     ▼
┌─────────────┐        ┌─────────────┐
│   Role     │        │OrderItem    │
│─────────────│        │─────────────│
│🔑 id       │        │🔑 id       │
│   name     │        │🔗 order_id │
│   level    │        │🔗 prod_id  │
└─────────────┘        │   qty      │
                       └──────┬──────┘
                              │
                              │ N:1
                              ▼
                       ┌─────────────┐
                       │  Product    │
                       │─────────────│
                       │🔑 id       │
                       │   name     │
                       │   price    │
                       └─────────────┘

Crow's Foot 基数表示:
1:N  → 一对多（用户拥有多个订单）
N:M  → 多对多（订单包含多个商品，通过中间表）
1:1  → 一对一（可选，用户与档案）
```

### 基数表示对照表

| 符号 | 含义 | SVG实现 |
|------|------|---------|
| `|—<` | 一对多 | 单线 + Crow's Foot |
| `>—<` | 多对多 | Crow's Foot + Crow's Foot |
| `|—|` | 一对一 | 单线 + 单线 |
| `>—|` | 可选一对一 | 圆弧 + 单线 |

### 强调策略

| 元素类型 | 典型策略 | 推荐强调色 |
|---------|---------|-----------|
| 主键行 | 🔑符号+accent色 | `--accent` |
| 外键行 | 🔗符号+link色 | `--link` |
| 弱实体 | 虚线边框 | `stroke-dasharray` |
| 继承实体 | 顶部双线 | `--paper-2`填充 |

### 标签密度控制

- **表头**: 1个标签，字号11px，粗体
- **主键**: 🔑符号+名称，字号9px
- **属性**: 名称+类型，字号9px/8px
- **关系**: 基数符号（1:N/N:M/1:1），字号9px

## 8. 质量检查清单

- [ ] 实体数量合理（不超过15个主要实体）
- [ ] 表头、表名居中或左对齐
- [ ] 主键用🔑符号标注
- [ ] 外键用🔗符号标注
- [ ] Crow's Foot基数表示正确
- [ ] 关系线不交叉
- [ ] 实体宽度一致
- [ ] 外键引用关系清晰
- [ ] 关系标签（1:N/N:M/1:1）标注正确
- [ ] 虚线表示弱关系
- [ ] WCAG AA对比度（文字4.5:1，图形3:1）
- [ ] SVG响应式，viewBox设置正确
- [ ] 整体布局居中，四周留白均衡
