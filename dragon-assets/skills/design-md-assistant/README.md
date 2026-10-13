# Design MD Assistant

> 天龙引擎 V8.85 - 设计系统智能助手
>
> 基于 [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) (31.2k Stars)

## 核心价值

Design MD Assistant 让天龙引擎能够：
- **58家公司设计系统** 即时访问（Claude, Stripe, Vercel, Figma, Notion...）
- **设计预览** 多格式输出（ASCII/Markdown/JSON/Tailwind）
- **组件生成** 一键生成 React/Vue/HTML 组件
- **设计提取** 从网站 URL 自动创建设计规范

## 功能概览

```
┌─────────────────────────────────────────────────────────────┐
│                    Design MD Assistant                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   58 设计系统   ──▶   设计预览   ──▶   组件生成          │
│   (DESIGN.md)         (4格式)          (3框架)           │
│                                                             │
│   网站 URL  ─────────────▶  设计提取 ──────────▶ DESIGN.md  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

```bash
# 列出所有公司
node scripts/list-companies.js list

# 预览 Stripe 设计系统
node scripts/preview.js preview stripe

# 生成 Stripe 风格按钮组件 (React)
node scripts/generate-component.js generate stripe button react

# 列出所有组件类型
node scripts/generate-component.js list-components

# 列出所有框架
node scripts/generate-component.js list-frameworks
```

## 公司设计系统索引 (58家)

### AI & Machine Learning (12)
| 公司 | 风格描述 |
|------|---------|
| Claude | 温暖的赭石色强调，干净的编辑布局 |
| Cohere | 充满活力的渐变，数据丰富的仪表盘美学 |
| ElevenLabs | 黑暗电影风格，音频波形美学 |
| MiniMax | 大胆的深色界面，霓虹灯强调 |
| Mistral AI | 法国制造的极简主义，紫色色调 |
| Ollama | 终端优先，单色简约 |
| OpenCode AI | 开发者为中心的深色主题 |
| Replicate | 干净的白色画布，代码优先 |
| RunwayML | 电影深色 UI，媒体丰富布局 |
| Together AI | 技术风格，蓝图设计 |
| VoltAgent | 虚空黑画布，翡翠绿强调，终端原生 |
| xAI | 朴素单色，未来主义极简主义 |

### Developer Tools & Platforms (14)
| 公司 | 风格描述 |
|------|---------|
| Cursor | AI 优先代码编辑器，时尚的深色界面 |
| Expo | React Native 平台，深色主题，代码中心 |
| Linear | 超极简，精确，紫色强调 |
| Lovable | 俏皮的渐变，友好的开发者美学 |
| Mintlify | 干净的绿色强调，阅读优化 |
| PostHog | 刺猬品牌俏皮，开发者友好的深色 UI |
| Raycast | 时尚的深色 Chrome，充满活力的渐变强调 |
| Resend | 极简深色主题，等宽强调 |
| Sentry | 深色仪表盘，数据密集，粉紫色强调 |
| Supabase | 深色翡翠主题，代码优先 |
| Superhuman | 高级深色 UI，键盘优先，紫色光晕 |
| Vercel | 黑白精确，Geist 字体 |
| Warp | 现代终端，基于块的命令 UI |
| Zapier | 温暖的橙色，友好的插图驱动 |

### Infrastructure & Cloud (6)
| 公司 | 风格描述 |
|------|---------|
| ClickHouse | 黄色强调，技术文档风格 |
| Composio | 现代深色与丰富多彩的集成图标 |
| HashiCorp | 企业干净，黑白 |
| MongoDB | 绿色叶子品牌，开发者文档焦点 |
| Sanity | 红色强调，内容优先编辑布局 |
| Stripe | 签名紫色渐变，300 字重优雅 |

### Fintech & Crypto (4)
| 公司 | 风格描述 |
|------|---------|
| Coinbase | 干净的蓝色标识，信任焦点 |
| Kraken | 紫色强调的深色 UI，数据密集仪表盘 |
| Revolut | 时尚的深色界面，渐变卡片 |
| Wise | 明亮的绿色强调，友好清晰 |

### Enterprise & Consumer (7)
| 公司 | 风格描述 |
|------|---------|
| Airbnb | 温暖的珊瑚色强调，摄影驱动，圆润 UI |
| Apple | 高级留白，SF Pro，电影级图像 |
| IBM | Carbon 设计系统，结构化蓝色调色板 |
| NVIDIA | 绿黑色能量，技术力量美学 |
| SpaceX | 朴素黑白，满版图像，未来主义 |
| Spotify | 深色上的鲜艳绿色，粗体字，专辑艺术驱动 |
| Uber | 大胆黑白，紧凑字体，城市能量 |

### Car Brands (5)
| 公司 | 风格描述 |
|------|---------|
| BMW | 深色 premium 表面，精确德国工程 |
| Ferrari | 明暗对比黑白编辑， Ferrari 红 |
| Lamborghini | 真正的黑色大教堂，金色强调 |
| Renault | 生动极光渐变，零半径按钮 |
| Tesla | 激进减法，电影摄影 |

### Design & Productivity (10)
| 公司 | 风格描述 |
|------|---------|
| Airtable | 多彩，友好，结构化数据美学 |
| Cal.com | 干净的 neutral UI，开发者导向简约 |
| Clay | 有机形状，柔和渐变，艺术指导 |
| Figma | 鲜艳的多色，俏皮但专业 |
| Framer | 大胆黑色和蓝色，运动优先 |
| Intercom | 友好的蓝色调色板，对话式 UI |
| Miro | 明亮黄色强调，无限画布美学 |
| Notion | 温暖的极简主义，衬线标题，柔和表面 |
| Pinterest | 红色强调，砖石网格，图像优先 |
| Webflow | 蓝色强调，精致营销网站美学 |

## CLI 命令详解

### 1. list-companies.js - 公司索引

```bash
# 列出所有公司（按分类）
node scripts/list-companies.js list

# 列出特定分类
node scripts/list-companies.js list ai-ml
node scripts/list-companies.js list developer-tools

# 搜索公司
node scripts/list-companies.js search stripe
node scripts/list-companies.js search "design system"

# 获取公司设计文件路径
node scripts/list-companies.js get stripe

# 导出所有公司 JSON
node scripts/list-companies.js all
```

### 2. preview.js - 设计预览

```bash
# ASCII 艺术预览（默认）
node scripts/preview.js preview stripe

# Markdown 格式
node scripts/preview.js preview claude markdown

# JSON 格式
node scripts/preview.js preview vercel json

# Tailwind CSS 配置
node scripts/preview.js preview figma tailwind

# 对比两个设计系统
node scripts/preview.js compare stripe paypal
```

### 3. generate-component.js - 组件生成

```bash
# 列出所有组件类型
node scripts/generate-component.js list-components

# 列出所有框架
node scripts/generate-component.js list-frameworks

# 生成组件
node scripts/generate-component.js generate stripe button react
node scripts/generate-component.js generate claude card vue
node scripts/generate-component.js generate vercel input html
```

**支持的组件类型：**
- button - 交互按钮
- card - 内容容器卡片
- input - 表单输入字段
- navigation - 导航栏/菜单
- pricing-table - 定价比较
- form - 多字段表单
- hero - 落地页英雄区
- footer - 页面页脚
- modal - 对话框覆盖
- sidebar - 侧边导航面板

**支持的框架：**
- react - React (.tsx)
- vue - Vue (.vue)
- html - HTML + CSS

## 设计系统结构

每个 DESIGN.md 文件包含 9 个标准部分：

```markdown
# {Company} Design System

## Visual Theme
[2-3 句描述整体美学]

## Color Palette
| Token | Value | Usage |
|-------|-------|-------|
| primary | #XXXXXX | 主要品牌颜色 |

## Typography Rules
- Font Family: "Primary Font", fallback
- Headings: {sizes}
- Body: {size}/{line-height}

## Component Stylings
### Buttons
[详细按钮样式，包含所有状态]

### Cards
[卡片组件规格]

### Inputs
[输入字段规格]

### Navigation
[导航规格]

### Forms
[表单样式]

## Layout Principles
- Grid: {columns} columns
- Spacing Scale: {values}
- Breakpoints: {values}

## Depth & Elevation
- Shadows: [list with values]
- Borders: [styles]

## Motion & Animation
- Transitions: {duration} {easing}
- Animations: [patterns observed]

## Do's and Don'ts
### Do
- [positive patterns]

### Don't
- [patterns to avoid]

## Agent Prompt Guide
[用于生成匹配组件的提示词]
```

## 提示词模板

### design-extraction.md - 从网站提取设计

从网站 URL 自动创建设计规范文档：

```bash
# 使用方法：在 Claude Code 中加载 prompts/design-extraction.md
# 然后分析目标网站 URL
```

### component-generation.md - 组件生成

生成匹配特定公司设计系统的 UI 组件：

```bash
# 使用方法：在 Claude Code 中加载 prompts/component-generation.md
# 然后使用设计令牌生成组件
```

## 与其他天龙引擎技能协同

### 设计系统协同矩阵

| 协同技能 | 协同方式 | 效果 |
|---------|---------|------|
| **13-01 设计师** | DESIGN.md 作为设计系统源 | V10.5 → V10.6 升级 |
| **qiaomu-mondo-poster-design** | DESIGN.md 驱动艺术海报 | 设计风格一致 |
| **ppt-generator** | DESIGN.md 作为 PPT 主题 | 品牌一致性 |
| **smart-illustrator** | DESIGN.md 驱动配图风格 | 设计系统应用 |
| **html-slides** | DESIGN.md 作为幻灯片主题 | 企业风格统一 |
| **lovstudio-any2pdf** | DESIGN.md 文档 PDF 导出 | 专业排版 |
| **remotion-best-practices** | DESIGN.md 驱动视频设计 | 品牌动画 |
| **next-ai-drawio-mcp** | DESIGN.md 驱动图表样式 | 架构图风格 |

### 使用示例

```bash
# 1. 设计师使用 Design MD
[@13-01] 使用 Claude 设计系统创建设计规范
[@13-01] 生成 Figma 风格的定价卡片组件

# 2. 与 Mondo 海报协同
[@13-01] 使用 Stripe 设计系统生成海报
[@13-01] 对比 Stripe 和 Vercel 的设计风格

# 3. 与 PPT 生成协同
[@13-01] 使用 Airbnb 设计系统生成企业 PPT
[@13-01] 应用品牌色彩到演示文稿

# 4. 与 Draw.io 协同
[@02] 生成 Notion 风格的技术架构图
[@02] 使用 Linear 设计系统生成 API 文档图表
```

## 安装与配置

### 依赖

```bash
# 无需额外依赖（纯 Node.js）
node --version  # >= 14.0.0
```

### 结构

```
design-md-assistant/
├── SKILL.md                    # 技能主文档
├── README.md                   # 本文件
├── prompts/                    # 提示词模板
│   ├── design-extraction.md   # 设计提取指南
│   └── component-generation.md # 组件生成指南
├── scripts/                    # CLI 工具
│   ├── list-companies.js      # 公司索引
│   ├── preview.js             # 设计预览
│   └── generate-component.js  # 组件生成
└── design-md/                 # 设计系统存储
    └── {company}/
        └── DESIGN.md          # 各公司设计文件
```

### 更新设计系统

```bash
# 克隆最新 awesome-design-md
git clone https://github.com/VoltAgent/awesome-design-md.git design-md-temp

# 合并到现有目录
cp -r design-md-temp/* design-md/
rm -rf design-md-temp
```

## 设计令牌参考

### 核心令牌

| 令牌 | CSS 变量 | 用途 |
|------|----------|------|
| primary | `--{company}-primary` | 主要操作 |
| secondary | `--{company}-secondary` | 次要操作 |
| text | `--{company}-text` | 正文文本 |
| background | `--{company}-background` | 页面背景 |
| border | `--{company}-border` | 边框和分隔线 |
| radius | `--{company}-radius` | 圆角 |
| shadow-sm | `--{company}-shadow-sm` | 小阴影 |
| shadow-md | `--{company}-shadow-md` | 中阴影 |
| shadow-lg | `--{company}-shadow-lg` | 大阴影 |

### 语义令牌

| 令牌 | 用途 |
|------|------|
| success | 成功状态 |
| warning | 警告状态 |
| error | 错误状态 |
| info | 信息状态 |

## 组件状态

每个组件支持以下状态：

| 状态 | 描述 |
|------|------|
| Default | 正常外观 |
| Hover | 鼠标悬停（颜色、变换） |
| Active/Pressed | 点击中（缩放、颜色） |
| Focus | 键盘焦点（轮廓、环） |
| Disabled | 不可交互（透明度、光标） |
| Loading | 异步状态（微调器、禁用） |
| Error | 验证失败（边框、消息） |
| Success | 操作完成（颜色、图标） |

## 无障碍要求

- 语义 HTML（`<button>`, `<a>`, `<input>`）
- 需要时的 ARIA 标签
- 可见焦点状态
- 颜色对比合规
- 键盘导航
- 屏幕阅读器文本

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-08 | 初始集成，58 公司设计系统 |

## 许可

基于 [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) Apache 2.0 许可。
