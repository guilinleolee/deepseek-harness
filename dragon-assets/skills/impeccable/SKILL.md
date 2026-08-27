---
github_repo: pbakaus/impeccable
github_hash: 346ce25952a6d4150433e8fb1369cb59571ebc30
last_updated: 2026-04-25
source_type: derived
triggers: ["impeccable", "Impeccable - 前端设计语言扩展"]
---
# Impeccable - 前端设计语言扩展

> 来源: [pbakaus/impeccable](https://github.com/pbakaus/impeccable)
> 版本: V1.0
> 集成日期: 2026-03-09

## 核心价值

Impeccable 是构建在 Anthropic 官方 frontend-design 技能之上的设计语言扩展，提供：
- **17个导向命令** - 精细化设计工作流
- **7个领域参考** - 系统化设计知识
- **反模式库** - 避免"AI味"设计

## 天龙岗位升级映射

| 天龙岗位 | 匹配度 | 核心收益 |
|----------|--------|---------|
| **13-01 设计师** | ⭐⭐⭐⭐⭐ | 完整设计工作流：审查→优化→打磨 |
| **06 审查师** | ⭐⭐⭐⭐⭐ | /audit + /critique 设计审查能力 |
| **03 构建师** | ⭐⭐⭐⭐ | 前端实现质量、响应式、动效 |
| **02 架构师** | ⭐⭐⭐⭐ | 设计系统标准化、组件提取 |
| **07 记录师** | ⭐⭐⭐ | UX写作、文案澄清 |

## 17个导向命令

### 质量审查 (2个)
| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `/audit` | 技术质量检查 | A11y、性能、主题、响应式 |
| `/critique` | UX设计评审 | 视觉层次、信息架构、情感共鸣 |

### 优化打磨 (5个)
| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `/normalize` | 设计系统对齐 | 统一设计规范 |
| `/polish` | 发布前打磨 | 最后质量检查 |
| `/optimize` | 性能优化 | 加载速度、渲染、包大小 |
| `/harden` | 边缘情况处理 | 错误处理、i18n、边界值 |
| `/distill` | 简化设计 | 去除不必要复杂度 |

### 设计增强 (5个)
| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `/animate` | 添加动效 | 目的性动画、微交互 |
| `/colorize` | 色彩策略 | 战略性配色 |
| `/bolder` | 放大设计 | 让无聊设计更有冲击力 |
| `/quieter` | 收敛设计 | 让过于激进的设计更平衡 |
| `/delight` | 愉悦体验 | 添加惊喜时刻 |

### 内容与组件 (3个)
| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `/clarify` | 文案澄清 | 改善UX文案、错误消息 |
| `/extract` | 组件提取 | 提取可复用组件到设计系统 |
| `/adapt` | 响应式适配 | 跨设备、跨平台适配 |

### 流程 (2个)
| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `/onboard` | 新手引导设计 | 设计引导流程 |
| `/teach-impeccable` | 一次性设置 | 建立项目设计上下文 |

## 7个领域参考

| 参考文件 | 内容 |
|---------|------|
| `typography.md` | 字体选择、配对、加载策略 |
| `color-and-contrast.md` | OKLCH色彩、调色板、暗色模式 |
| `spatial-design.md` | 网格、节奏、容器查询 |
| `motion-design.md` | 时序、缓动、减少动效 |
| `interaction-design.md` | 表单、焦点、加载模式 |
| `responsive-design.md` | 移动优先、流式设计、容器查询 |
| `ux-writing.md` | 标签、错误消息、空状态 |

## 反模式库（避免AI味设计）

### ❌ 字体反模式
- 过度使用 Inter、Roboto、Arial、Open Sans
- 用等宽字体作为"技术感"的偷懒表达
- 标题上方放置大圆角图标

### ❌ 色彩反模式
- 使用"AI配色"：深色背景+青色/紫色渐变+霓虹强调
- 纯黑(#000)或纯白(#fff)
- 有色背景上使用灰色文字（用背景色深浅代替）
- 渐变文字用于"冲击感"

### ❌ 布局反模式
- 万物皆卡片
- 卡片嵌套卡片
- 相同大小的卡片网格
- "英雄指标"布局：大数字+小标签+渐变强调

### ❌ 动效反模式
- 弹性或弹性缓动（过时）
- 动画布局属性（width/height/padding）
- 用 transform 和 opacity 代替

### ❌ 装饰反模式
- 无目的的玻璃态效果
- 单侧粗边框装饰
- 无意义的迷你图表
- 通用圆角矩形+阴影

## 使用示例

### 设计审查工作流
```bash
# 1. 技术质量检查
/audit checkout-form

# 2. UX设计评审
/critique checkout-form

# 3. 优化问题
/normalize checkout-form   # 对齐设计系统
/optimize checkout-form    # 性能优化
/polish checkout-form      # 最终打磨
```

### 设计增强工作流
```bash
# 让无聊设计更有冲击力
/bolder landing-page

# 添加动效
/animate navigation

# 添加愉悦时刻
/delight onboarding
```

### 组件提取工作流
```bash
# 提取可复用组件
/extract button-variants

# 响应式适配
/adapt dashboard
```

## 与现有技能协同

| 天龙技能 | 协同方式 |
|---------|---------|
| `frontend-design` | Impeccable 是其扩展，引用相同参考文件 |
| `react-ui-patterns` | /extract 可提取 React 组件模式 |
| `ui-ux-designer` | 共享设计审查能力 |
| `code-reviewer` | /audit 增加设计审查维度 |

## 安装位置

```
~/.claude/skills/impeccable/
├── SKILL.md              # 本文件
├── .claude/skills/       # 18个子技能
│   ├── frontend-design/  # 核心设计技能
│   │   ├── SKILL.md
│   │   └── reference/    # 7个参考文件
│   ├── audit/SKILL.md
│   ├── critique/SKILL.md
│   ├── normalize/SKILL.md
│   ├── polish/SKILL.md
│   ├── optimize/SKILL.md
│   ├── harden/SKILL.md
│   ├── distill/SKILL.md
│   ├── animate/SKILL.md
│   ├── colorize/SKILL.md
│   ├── bolder/SKILL.md
│   ├── quieter/SKILL.md
│   ├── delight/SKILL.md
│   ├── clarify/SKILL.md
│   ├── extract/SKILL.md
│   ├── adapt/SKILL.md
│   ├── onboard/SKILL.md
│   └── teach-impeccable/SKILL.md
└── README.md
```

## 参考链接

- [impeccable.style](https://impeccable.style) - 官网
- [GitHub](https://github.com/pbakaus/impeccable) - 源码
- [Agent Skills Specification](https://agentskills.io/specification) - 标准