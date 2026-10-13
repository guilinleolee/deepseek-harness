---
license: UNKNOWN
github_repo: VoltAgent/awesome-design-md
github_hash: 6dc4def886e9ad4022d616dc2afc2fcdf0056d07
triggers: ["design md assistant", "Design MD Assistant - 设计系统助手"]
---
# Design MD Assistant - 设计系统助手

## L0: 一句话描述 (≤15字)
58家公司设计规范，一键生成匹配UI。

## L1: 使用场景 (50-100字)
当用户需要生成符合特定公司设计风格的前端代码时使用。支持AI工具/开发平台/基础设施/金融/企业/汽车六大领域58个主流产品的设计规范自动匹配和组件代码生成。

## L2: 详细文档

### 来源项目
> [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) - 31.2k Stars AI Coding Agent设计系统仓库

### 核心价值
- 58个知名公司的完整DESIGN.md设计规范
- 设计系统驱动的前端组件自动生成
- 品牌一致性保证（配色/字体/间距/动效）
- AI Coding Agent友好的Markdown格式

### 公司分类索引

```
┌─────────────────────────────────────────────────────────────┐
│ AI & Machine Learning (12)                                   │
├─────────────────────────────────────────────────────────────┤
│ claude, cohere, elevenlabs, minimax, mistral.ai, ollama   │
│ opencode.ai, replicate, runwayml, together.ai, voltagent, x.ai │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Developer Tools & Platforms (14)                               │
├─────────────────────────────────────────────────────────────┤
│ cursor, expo, linear.app, lovable, mintlify, posthog       │
│ raycast, resend, sentry, supabase, superhuman, vercel     │
│ warp, zapier                                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Infrastructure & Cloud (6)                                   │
├─────────────────────────────────────────────────────────────┤
│ clickhouse, composio, hashicorp, mongodb, sanity, stripe   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Fintech & Crypto (4)                                         │
├─────────────────────────────────────────────────────────────┤
│ coinbase, kraken, revolut, wise                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Enterprise & Consumer (7)                                    │
├─────────────────────────────────────────────────────────────┤
│ airbnb, apple, ibm, nvidia, spacex, spotify, uber        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Car Brands (5)                                              │
├─────────────────────────────────────────────────────────────┤
│ bmw, ferrari, lamborghini, renault, tesla                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Design & Productivity (10)                                   │
├─────────────────────────────────────────────────────────────┤
│ airtable, cal, clay, figma, framer, intercom               │
│ miro, notion, pinterest, webflow                          │
└─────────────────────────────────────────────────────────────┘
```

### 使用方法

#### 方式1: 自然语言直接生成（推荐）

```
用户: "用Stripe风格做一个支付页面"
天龙引擎 → 加载Stripe DESIGN.md → 提取设计规范 → 生成React组件
```

#### 方式2: 命令行工具

```bash
# 列出所有可用公司
design-md list

# 查看公司设计系统预览
design-md preview stripe

# 匹配公司风格
design-md match "vercel" --task "landing-page"

# 生成组件代码
design-md generate --company stripe --component "pricing-table"
```

#### 方式3: 自然语言触发

```
[@设计师] 用Linear风格设计一个项目管理看板
[@设计师] 创建一个Vercel风格的首页
[@设计师] 用Stripe风格实现支付表单组件
```

### DESIGN.md 结构说明

每个DESIGN.md包含9个核心部分：

| 部分 | 内容 | 示例 |
|------|------|------|
| **1. Visual Theme** | 视觉主题和氛围 | Warm parchment canvas, editorial layout |
| **2. Color Palette** | 配色系统 | Primary, Secondary, Semantic, Neutrals |
| **3. Typography Rules** | 字体规范 | Font family, Hierarchy, Principles |
| **4. Component Stylings** | 组件样式 | Buttons, Cards, Inputs, Navigation |
| **5. Layout Principles** | 布局原则 | Spacing, Grid, Whitespace |
| **6. Depth & Elevation** | 深度系统 | Shadows, Borders, Elevation levels |
| **7. Do's and Don'ts** | 设计规范 | 设计禁区和建议 |
| **8. Responsive Behavior** | 响应式设计 | Breakpoints, Collapsing |
| **9. Agent Prompt Guide** | AI提示词指南 | 快速参考和示例 |

### 核心命令速查

```bash
# 设计系统操作
design-md list                          # 列出所有公司
design-md search "stripe"              # 搜索公司
design-md preview "linear"             # 预览设计系统
design-md extract "https://stripe.com" # 从网站提取设计规范

# 组件生成
design-md generate --company stripe --component "checkout-form"
design-md generate --company claude --component "pricing-table"
design-md generate --company vercel --component "landing-page"

# 批量操作
design-md batch --file companies.txt --output ./generated/
design-md export --company stripe --format tailwind
```

### 与现有技能协同矩阵

| 现有技能 | 协同方式 | 效果 |
|---------|---------|------|
| **Impeccable (V8.11)** | 基础设计审查 + Design MD生成 | 设计质量+100% |
| **Mondo海报 (V8.32)** | 品牌风格 + Mondo艺术家 | 设计风格扩展 |
| **baoyu-cover-image** | 公司设计规范 → 封面生成 | 品牌一致性 |
| **ppt-generator** | 设计系统 → PPT主题 | 品牌视觉统一 |
| **smart-illustrator** | 公司配色 → 配图生成 | 品牌调性匹配 |
| **pptx** | 设计系统 → PPT组件 | 品牌风格复用 |

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **13-01 设计师** | V10.5 → V10.6 | Design MD驱动设计系统生成 |
| **03-01 内容创作师** | V1.0 → V1.1 | 品牌设计规范提取 |

### 典型使用场景

#### 场景1: 竞品分析报告
```
用户: "分析Stripe和PayPal的支付表单设计差异"
[@设计师] 加载两者的DESIGN.md → 对比分析 → 生成对比报告
```

#### 场景2: 新产品设计
```
用户: "做一个类似Linear的项目管理工具"
[@设计师] 加载Linear DESIGN.md → 生成匹配UI组件 → 确保品牌一致性
```

#### 场景3: 设计系统迁移
```
用户: "把我们官网改成Stripe风格"
[@设计师] 提取Stripe规范 → 逐页面迁移 → 保持设计一致性
```

#### 场景4: 组件库构建
```
用户: "创建一套Vercel风格的React组件库"
[@设计师] 加载Vercel DESIGN.md → 批量生成组件 → 组件库完成
```

### 文件结构

```
design-md-assistant/
├── SKILL.md                              # 本文件
├── README.md                              # 使用指南
├── design-md/
│   ├── ai-ml/                           # AI/ML公司 (12个)
│   │   ├── claude/DESIGN.md
│   │   ├── stripe/DESIGN.md
│   │   └── ...
│   ├── developer-tools/                  # 开发工具 (14个)
│   ├── infrastructure/                   # 基础设施 (6个)
│   ├── fintech/                         # 金融科技 (4个)
│   ├── enterprise/                      # 企业/消费 (7个)
│   ├── car-brands/                     # 汽车品牌 (5个)
│   └── design-productivity/            # 设计工具 (10个)
├── scripts/
│   ├── list-companies.js              # 列出公司
│   ├── preview.js                       # 设计预览
│   ├── match-company.js               # 公司匹配
│   └── generate-component.js           # 组件生成
└── prompts/
    ├── design-extraction.md           # 设计提取提示词
    └── component-generation.md         # 组件生成提示词
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-08 | 初始集成，58个公司设计规范 |

### 注意事项

1. **首次使用**: 加载DESIGN.md可能需要2-3秒
2. **设计规范**: 严格按照DESIGN.md生成，不要自行发挥
3. **组件粒度**: 建议一次生成一个组件，确保设计一致性
4. **自定义场景**: 如需混合多种风格，先加载多个DESIGN.md再组合
