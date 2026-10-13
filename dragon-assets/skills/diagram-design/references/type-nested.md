# 嵌套图参考指南

## 1. 适用场景

嵌套图（Nested Diagram）用于展示层级包含关系或递归结构，适用于文件系统、目录结构、JSON树形、组织架构等场景。

| 场景 | 典型框架 |
|------|---------|
| 文件系统 | 根目录→子目录→文件 |
| 组织架构 | 公司→部门→团队→成员 |
| 代码结构 | 模块→类→方法→变量 |
| 配置层级 | 全局→环境→本地覆盖 |
| 菜单树 | 一级菜单→二级菜单→操作项 |

## 2. 设计原则

- **目标密度**: 4/10（清晰层级边界）
- **节点形状**: 顶层容器rx=8/子容器rx=4/孙容器rx=2
- **accent使用**: 当前展开路径用accent强调
- **布局**: 树形展开或网格平铺
- **连接**: 嵌套关系用矩形嵌套表达

## 3. 组件类型

### 顶层容器

```html
<rect x="100" y="60" width="500" height="360" rx="8" fill="var(--paper-2)"
  stroke="var(--ink)" stroke-width="1.5"/>
<text x="130" y="85" font-size="12" font-weight="600" fill="var(--ink)">根节点</text>
```

### 子容器

```html
<rect x="120" y="100" width="460" height="80" rx="4" fill="var(--paper)"
  stroke="var(--ink)" stroke-width="1"/>
<text x="135" y="120" font-size="11" fill="var(--ink)">▶ 子节点</text>
```

### 孙容器

```html
<rect x="140" y="185" width="420" height="60" rx="2" fill="var(--accent)" opacity="0.1"
  stroke="var(--accent)" stroke-width="1"/>
<text x="155" y="205" font-size="10" fill="var(--accent)">▷ 当前展开项</text>
```

### 文件/叶子项

```html
<!-- 文件节点（无子项） -->
<rect x="160" y="250" width="380" height="30" rx="2" fill="var(--paper)"
  stroke="var(--ink)" stroke-width="0.75"/>
<text x="175" y="270" font-size="9" fill="var(--ink)">📄 文件名.ext</text>
```

### 树形连接线（文件夹展开样式）

```html
<!-- 展开指示线 -->
<path d="M 130 140 L 130 260" stroke="var(--ink)" stroke-width="0.75"
  stroke-dasharray="3,2" fill="none"/>
<!-- 子项横线 -->
<line x1="130" y1="200" x2="155" y2="200" stroke="var(--ink)" stroke-width="0.75"/>
<!-- 展开箭头 -->
<text x="120" y="124" font-size="9" fill="var(--muted)">▼</text>
```

## 4. 连接线规范

### 嵌套边界线

```html
<!-- 父容器边框（粗） -->
<rect x="100" y="60" width="500" height="360" rx="8"
  fill="none" stroke="var(--ink)" stroke-width="1.5"/>

<!-- 子容器边框（中） -->
<rect x="120" y="100" width="460" height="80" rx="4"
  fill="none" stroke="var(--ink)" stroke-width="1"/>

<!-- 孙容器边框（细） -->
<rect x="140" y="185" width="420" height="60" rx="2"
  fill="var(--accent)" opacity="0.1" stroke="var(--accent)" stroke-width="1"/>
```

### 树形展开线

```html
<!-- 垂直展开线 -->
<line x1="145" y1="220" x2="145" y2="380" stroke="var(--ink)" stroke-width="0.75"/>

<!-- 水平分支线 -->
<line x1="145" y1="260" x2="170" y2="260" stroke="var(--ink)" stroke-width="0.75"/>

<!-- 展开/折叠图标 -->
<text x="125" y="115" font-size="10" fill="var(--muted)">▶</text>
<text x="125" y="195" font-size="10" fill="var(--accent)">▼</text>
```

### 引用连线（跨容器引用）

```html
<path d="M 400 140 L 400 300 L 550 300" stroke="var(--link)"
  stroke-width="1" stroke-dasharray="4,2" fill="none"/>
<text x="460" y="240" font-size="9" fill="var(--link)">→ 引用</text>
```

## 5. 层级布局

### 坐标计算规则

假设画布宽度 W = 700，高度 H = 500：

- 画布: 700 × 500
- 根容器: x=100, y=60, w=500, h=360, rx=8
- 子容器: x=120, y=100, w=460, h=80, rx=4, 间距15
- 孙容器: x=140, y=190, w=420, h=60, rx=2, 间距10
- 叶子项: x=160, y=255, w=380, h=30, rx=2, 间距10

### 层级坐标映射

| 层级 | 形状 | X | Y | W | H | rx | 说明 |
|------|------|---|---|---|---|---|------|
| L0根 | 矩形 | 100 | 60 | 500 | 360 | 8 | 顶层容器 |
| L1子 | 矩形 | 120 | 100 | 460 | 80 | 4 | 第一层子节点 |
| L2孙 | 矩形 | 140 | 190 | 420 | 60 | 2 | accent强调 |
| L3曾孙 | 矩形 | 160 | 260 | 400 | 30 | 2 | 叶子项 |

### 比例原则

- 画布宽高比约 7:5 或 4:3
- 容器宽度逐层递减（每层-20px边距）
- 容器高度随内容动态调整
- 展开/折叠状态清晰（▼/▶图标）
- 当前路径accent颜色强调

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
--container-border: #d1d5db;

/* minimal-dark */
--paper: #0f172a;
--ink: #f1f5f9;
--muted: #94a3b8;
--paper-2: #1e293b;
--accent: #60a5fa;
--link: #93c5fd;
--container-border: #334155;

/* full-editorial */
--paper: #fefefe;
--ink: #18181b;
--muted: #71717a;
--paper-2: #f4f4f5;
--accent: #e11d48;
--link: #be123c;
--container-border: #d4d4d4;
```

### 元素ID命名

```html
<g id="nested-container">          <!-- 主容器组 -->
  <g id="root-node">              <!-- 根节点 -->
  <g id="level-1">                <!-- L1层节点组 -->
    <g id="child-node-1a">       <!-- L1子节点 -->
  <g id="level-2">                <!-- L2层节点组 -->
    <g id="child-node-2a">       <!-- L2子节点 -->
  <g id="level-3">                <!-- L3层节点组 -->
    <g id="leaf-node-3a">         <!-- L3叶子节点 -->
  <g id="expand-lines">          <!-- 展开连接线组 -->
  <g id="collapse-toggle">       <!-- 展开/折叠按钮 -->
</g>
```

### 类名约定

```html
<div class="nested">
  <div class="nested-root">
    <div class="nested-container nested-container-l1">
      <div class="nested-container nested-container-l2">
        <div class="nested-item nested-item-leaf">
      </div>
    </div>
  </div>
  <div class="nested-expand-line"></div>
</div>
```

## 7. 常见布局模式

### 文件系统树

```
┌─────────────────────────────────────────┐
│ 📁 根目录                          [▼]  │ ← rx=8, paper-2填充
├─────────────────────────────────────────┤
│   ▶ src                               │   ← rx=4, 子容器
│   │   ▶ components                   │
│   │   │   ▶ Button.tsx               │   ← 叶子文件, rx=2
│   │   │   📄 Card.tsx               │
│   │   └── 📄 App.tsx                │
│   └── 📄 index.ts                   │
├─────────────────────────────────────────┤
│   ▶ public                           │
│   │   ▶ assets                      │
│   │   │   📄 logo.png              │
│   │   └── 📄 favicon.ico           │
│   └── 📄 robots.txt                 │
└─────────────────────────────────────────┘
```

### JSON树结构

```
┌─────────────────────────────────────────┐
│ {                                     │ ← JSON根对象
│   "name": "根节点",                   │
│   "children": [                     │
│     { "id": "A", "value": 10 },    │
│     { "id": "B", "children": [...] }│
│   ]                                  │
│ }                                     │
└─────────────────────────────────────────┘
```

### 组织架构嵌套

```
┌─────────────────────────────────────────┐
│ 🚀 公司名称                           │
├─────────────────────────────────────────┤
│   ▶ 技术部                            │
│   │   ├── 前端组                     │
│   │   ├── 后端组                     │
│   │   └── 数据组                     │
│   ├── ▶ 产品部                      │
│   │   ├── 产品设计                   │
│   │   └── 产品运营                   │
│   └── 市场部                         │
└─────────────────────────────────────────┘
```

### 嵌套强调策略

| 层级 | 典型策略 | 推荐强调色 |
|------|---------|-----------|
| 根节点 | 标题+展开按钮 | `--ink`粗体标题 |
| L1子容器 | 展开箭头+rx=4 | 普通边框 |
| L2孙容器 | accent半透明+rx=2 | `--accent` opacity=0.1 |
| 叶子项 | 无子项/字体图标 | `--muted`色 |
| 当前路径 | accent边框+背景 | `--accent` stroke+opacity=0.1 |

### 标签密度控制

- **根节点**: 标题文字，字号12px，粗体
- **L1节点**: ▶+名称，字号11px
- **L2节点**: ▷+名称，字号10px
- **叶子项**: 📄+名称，字号9px
- 间距: 10-15px，视觉连贯

## 8. 质量检查清单

- [ ] 层级深度不超过4层（避免过度嵌套）
- [ ] 根容器rx=8，子容器rx=4，孙容器rx=2
- [ ] 展开/折叠图标清晰（▼/▶）
- [ ] 当前展开路径用accent颜色强调
- [ ] 容器边框宽度逐层递减（1.5→1→0.75）
- [ ] 子项排列整齐，间距均匀
- [ ] 文件/叶子项有明确图标标识
- [ ] WCAG AA对比度（文字4.5:1，图形3:1）
- [ ] SVG响应式，viewBox设置正确
- [ ] 整体布局居中，四周留白均衡