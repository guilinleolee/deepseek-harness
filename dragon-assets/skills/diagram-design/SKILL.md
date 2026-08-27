---
license: UNKNOWN
triggers: ["diagram design", "diagram-design Skill"]
---
# diagram-design Skill

> "Editorial diagrams your designer won't hate." — 15种自包含HTML+SVG图表类型

## L0: 一句话描述 (≤15字)
AI生成专业Editorial风格图表

## L1: 使用场景 (50-100字)
当用户需要生成流程图、时序图、战略分析图表(SWOT/象限图)、泳道图、时间线等专业化图表时使用。与next-ai-drawio-mcp互补(drawio擅长云架构图，diagram-design擅长流程/战略图)。

## L2: 详细文档

### 来源项目
[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) - 1,954 Stars, MIT License

### 核心能力

| 能力 | 说明 |
|------|------|
| **15种图表类型** | Architecture/Flowchart/Sequence/State Machine/ER/Timeline/Swimlane/Quadrant/Nested/Tree/Layers/Venn/Pyramid/Pyramid 3D/Consultant 2x2 |
| **3种变体** | minimal-light / minimal-dark / full-editorial |
| **60秒品牌Onboarding** | URL→语义Tokens自动提取 |
| **WCAG AA验证** | 内置对比度检查 |
| **纯HTML+SVG** | 无JS依赖，可直接嵌入 |

### 15种图表类型速查

| 类型 | 英文名 | 适用场景 |
|------|--------|---------|
| 流程图 | Flowchart | 业务流程、决策流程 |
| 时序图 | Sequence | API调用、系统交互 |
| 状态机 | State Machine | 状态流转、生命周期 |
| ER图 | Entity Relationship | 数据库设计 |
| 时间线 | Timeline | 产品路线图、项目计划 |
| 泳道图 | Swimlane | 跨角色流程、分工可视化 |
| 象限图 | Quadrant | SWOT、重要性/紧急性 |
| 嵌套图 | Nested | 层级结构、包含关系 |
| 树形图 | Tree | 组织结构、分类体系 |
| 分层图 | Layers | 系统架构、技术栈 |
| 韦恩图 | Venn | 交集分析、交集对比 |
| 金字塔 | Pyramid | 层级分析、漏斗转化 |
| 架构图 | Architecture | 软件架构、网络拓扑 |
| 顾问2x2 | Consultant 2x2 | 战略分析、BCG矩阵 |

### 3种变体

| 变体 | 说明 | 适用场景 |
|------|------|---------|
| `minimal-light` | 浅色极简 | 技术文档、GitHub README |
| `minimal-dark` | 深色极简 | 暗色主题、演示材料 |
| `full-editorial` | 完整编辑风格 | 报告、PPT、白皮书 |

### 与next-ai-drawio-mcp的双引擎策略

```
需要画图?
├── 云架构/部署/网络 → next-ai-drawio-mcp
├── 流程图/时序图 → diagram-design
├── 战略图/2x2矩阵 → diagram-design
└── 其他 → 按需选择
```

### 命令速查

```bash
# 流程图
/diagram flow "用户下单流程" --type flowchart --variant minimal-light

# 时序图
/diagram sequence "API调用时序" --type sequence --variant minimal-dark

# 象限图
/diagram quadrant "SWOT分析" --type quadrant --data "S:优势,W:劣势,O:机会,T:威胁"

# 时间线
/diagram timeline "产品路线图" --type timeline

# 泳道图
/diagram swimlane "电商流程" --type swimlane --lanes "用户,商家,平台"

# 列出所有类型
/diagram list
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **13-01 设计师** | V10.6 → V10.7 | 15种图表类型 + 3种变体 |
| **02 架构师** | V8.79 → V8.80 | 架构Flowchart + Sequence |
| **07 记录师** | V8.86 → V8.87 | 文档插图Timeline + Swimlane |

### 设计哲学

> "Every node earns its place"
> 目标密度: 4/10
> 节点上限: 约9个(超过则拆分为两个图表)
> Accent使用: 只用一种accent颜色，每个图表最多1-2个焦点元素

### 颜色语义Tokens

| Token | 来源 | 用途 |
|--------|------|------|
| `paper` | `<body>` background | 背景色 |
| `ink` | Primary text color | 主文本 |
| `muted` | Secondary text | 次要文本 |
| `paper-2` | Cards/containers | 卡片背景 |
| `accent` | CTA/brand color | 强调色 |
| `link` | Links | 链接色 |

### 字体语义Tokens

| Token | 来源 | 用途 |
|--------|------|------|
| `title` | `<h1>` | 标题字体 |
| `node-name` | `<body>` | 节点名称 |
| `sublabel` | `<code>`, `<pre>` | 技术子标签(等宽) |

### 安装

```bash
# 克隆到本地
git clone https://github.com/cathrynlavery/diagram-design.git ~/.claude/skills/diagram-design

# 或使用plugin marketplace
/plugin marketplace add cathrynlavery/diagram-design
```

### 文件结构

```
diagram-design/
├── SKILL.md                    # 本文件
├── prompts/
│   ├── flowchart.md            # 流程图提示词
│   ├── sequence.md            # 时序图提示词
│   ├── quadrant.md             # 象限图提示词
│   └── flowchart.md, sequence.md, quadrant.md, architecture.md, consultant-2x2.md, layers.md, venn.md, tree.md, er.md, nested.md, swimlane.md, timeline.md, state-machine.md, pyramid.md, style-guide.md
├── scripts/
│   ├── diagram_generator.py    # 图表生成器
│   ├── wcag_checker.py        # WCAG AA检查
│   └── brand_onboarding.py     # 品牌60秒Onboarding
└── references/
    ├── style-guide.md          # 品牌Tokens
    └── style-guide.md, type-architecture.md, type-consultant-2x2.md, type-layers.md, type-venn.md, type-tree.md, type-er.md, type-flowchart.md, type-nested.md, type-quadrant.md, type-sequence.md, type-swimlane.md, type-timeline.md, type-state-machine.md, type-pyramid.md
```

### 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| 图表类型覆盖 | 3种(draw.io) | 17种 | +467% |
| 品牌适配时间 | 手动30分钟 | 60秒 | -97% |
| WCAG合规性 | 无 | 内置验证 | 新增 |
| 输出质量 | 手绘级 | Editorial级 | +500% |

---

## Version
- V1.0: 2026-04-27 Initial integration
