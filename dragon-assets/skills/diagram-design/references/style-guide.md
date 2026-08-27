# Diagram Design Style Guide

## 品牌定位

> **Every node earns its place.**
> Every visual element must justify its existence. Complexity is the enemy of clarity.

`diagram-design` 是面向文档创作者的专业图表生成工具——让非设计师也能产出符合编辑级美学标准的 SVG 图表。核心理念：**精确、克制、可信**。

---

## 颜色语义系统

### 全局 Tokens（三套变体）

#### minimal-light（默认 · 白底文档）
```css
--paper: #ffffff;     /* 画布背景 */
--ink: #1a1a2e;       /* 主文字/线条 */
--muted: #6b7280;      /* 辅助标签/次要信息 */
--paper-2: #f8fafc;   /* 卡片/容器背景 */
--accent: #3b82f6;     /* 当前项/高亮/关键路径 */
--link: #2563eb;       /* 连接线（数据流/调用） */
```

#### minimal-dark（深色主题）
```css
--paper: #0f172a;
--ink: #f1f5f9;
--muted: #94a3b8;
--paper-2: #1e293b;
--accent: #60a5fa;
--link: #93c5fd;
```

#### full-editorial（报告/杂志风格）
```css
--paper: #fefefe;
--ink: #18181b;
--muted: #71717a;
--paper-2: #f4f4f5;
--accent: #e11d48;     /* 红色强调，编辑感 */
--link: #be123c;
```

### 字体 Tokens
```css
--title: 'Instrument Serif', Georgia, serif;  /* 图表标题 */
--node-name: 'Inter', system-ui, sans-serif;   /* 节点名称 */
--sublabel: 'JetBrains Mono', 'Fira Code', monospace;  /* 英文标注/数值 */
```

### 类型专属 Tokens

| 图表类型 | 专属 Token | 语义 |
|---------|-----------|------|
| **2x2四象限** | `--quadrant-tl/tr/bl/br` | 四宫格填色 |
| **金字塔/漏斗** | `--level-1` ~ `--level-6` | 层级渐变（深→浅） |
| **韦恩图** | `--circle-a/b/c` | 交集圆形 |
| **架构图** | `--service` / `--database` / `--external` | 节点类型 |

---

## 布局原则

### 容器留白
- viewBox 建议宽度 600-700px，高度按内容比例
- 主容器与边缘至少 40-60px 间距
- 多元素时使用网格对齐，避免自由落位

### 网格系统
- 2x2 图：主容器 stroke-width=2，中线 stroke-width=1
- 层级图：每层高度一致，垂直间距固定
- 架构图：组件间距 ≥ 20px

### 密度控制
- **目标密度**：4/10（清晰象限 / 清晰层级）
- 组件数量上限：架构图 12 个、流程图 15 个、时序图 8 个参与者
- 超出时拆分为多图

---

## 排版规范

### 字号梯度
- 图表标题：14-16px，`font-weight: 600`
- 节点名称：11-12px，`font-weight: 500-600`
- 轴标签/图例：9-10px，`fill: var(--muted)`
- 数值标注：9px，`font-family: var(--sublabel)`

### 对齐规则
- `text-anchor="middle"` 用于水平居中
- `text-anchor="end"` 用于右对齐（如轴标签）
- 中文优先宋体/系统默认，英文用 `sans-serif`

### 文本换行
- SVG `<text>` 不支持自动换行，长文本用 `<tspan dy="...">` 手动分行
- 建议单行字符数 ≤ 20

---

## 交互与动画

### 悬停效果（可选）
```css
rect:hover { fill: var(--paper-2); transition: fill 0.2s; }
```
仅在 `<style>` 标签内声明，SVG 本身无 JS 依赖。

### 动画规范
- 使用 CSS `@keyframes` 而非 SMIL
- 持续时间 ≤ 0.5s，缓动 `ease-out`
- `prefers-reduced-motion` 媒体查询尊重用户偏好

---

## WCAG 无障碍标准

### 对比度要求
| 元素 | 最小对比度 |
|------|-----------|
| 主文字（正常，<18px 普通字 / <14px 粗体） | **4.5:1** |
| 大字（≥18px 普通字 / ≥14px 粗体） | **3:1** |
| 图形组件（边框/填充区域） | **3:1** |

### 检查流程
1. 提取所有 fill / stroke 值（CSS 变量需解析为实际色值）
2. 背景 `--paper` 固定为 `#ffffff`（light）或 `#0f172a`（dark）
3. 计算文字与背景的对比度
4. `< 4.5:1` 触发警告，`--ink` 回退色为 `#374151`（#0f172a 背景上）

### 增强建议
- `<title>` + `<desc>` 标签提升屏幕阅读器支持
- `<role="img">` 显式标注
- 颜色区分 + 形状/纹理/文字三重区分，避免仅靠颜色传达信息

---

## 组件设计模式

### 矩形（最常用）
```svg
<rect x="X" y="Y" width="W" height="H" rx="4"
      fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/>
```
- `rx` 圆角：小组件 2-4px，大容器 6-8px
- 填充透明度 `opacity="0.1"` 用于背景标识区

### 圆形/椭圆（韦恩图、树节点）
```svg
<ellipse cx="X" cy="Y" rx="R" ry="R"
      fill="var(--accent)" opacity="0.15"
      stroke="var(--accent)" stroke-width="2"/>
```

### 连接线
```svg
<!-- 实线（同步调用/数据流） -->
<path d="M X1 Y1 L X2 Y2"
      stroke="var(--link)" stroke-width="1.5" fill="none"
      marker-end="url(#arrow)"/>

<!-- 虚线（异步/可选依赖） -->
<path d="M X1 Y1 L X2 Y2"
      stroke="var(--link)" stroke-width="1.5" fill="none"
      stroke-dasharray="4,2"/>
```

### 箭头标记
```svg
<defs>
  <marker id="arrow" markerWidth="8" markerHeight="8"
           refX="7" refY="4" orient="auto">
    <path d="M 0 0 L 8 4 L 0 8 Z" fill="var(--ink)"/>
  </marker>
</defs>
```

---

## 图表选择指南

| 需求场景 | 推荐类型 |
|---------|---------|
| 展示系统拓扑、组件关系 | **架构图** |
| 展示分层结构、包含关系 | **嵌套图** |
| 展示层级递进、优先级、漏斗转化 | **金字塔/漏斗图** |
| 展示分类对比、双维度分析 | **2x2四象限** |
| 展示分类对比、四宫格布局 | **顾问2x2矩阵** |
| 展示交集重叠、概念关系 | **韦恩图** |
| 展示数据流、步骤过程 | **流程图** |
| 展示时间序列、里程碑事件 | **时间线** |
| 展示参与者和消息交互 | **时序图** |
| 展示状态流转、有限自动机 | **状态机图** |
| 展示泳道分工、并行流程 | **泳道图** |
| 展示层级归属、树形结构 | **树图** |
| 展示数据库实体和关系 | **ER图** |
| 展示协议分层、OSI模型 | **层级图** |

---

## 质量检查清单

- [ ] viewBox 尺寸合理，内容无裁剪
- [ ] 四象限/层级对称（视觉平衡）
- [ ] 所有文字可读，对比度 ≥ 4.5:1
- [ ] 连接线无交叉或重叠
- [ ] 图例完整，与图中元素一一对应
- [ ] 图表标题存在且居中
- [ ] 坐标轴标签清晰（方向、高低含义）
- [ ] 类型专属 Tokens 正确使用
- [ ] `prompts/` 目录有对应的 AI 指令模板
- [ ] 纯 HTML+SVG，零 JS 依赖
