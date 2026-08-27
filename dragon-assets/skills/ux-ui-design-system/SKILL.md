---
license: UNKNOWN
triggers: ["ux ui design system", "ux-ui-design-system"]
---
# ux-ui-design-system

## L0: 一句话描述 (≤15字)
UX/UI开发设计系统，基于prompts.chat UX Developer角色

## L1: 使用场景 (50-100字)

**适用场景**：
- 产品界面设计与用户体验优化
- 前端组件开发与设计系统构建
- 交互原型设计与用户流程梳理
- 设计规范文档与组件库建设

**触发关键词**：`/ux-ui`、`/design-system`、`/interface-design`

## L2: 详细文档

### 来源
基于 prompts.chat UX/UI Developer角色扩展，融合设计系统最佳实践。

### 核心能力

#### 1. UX设计原则

```
I want you to act as a UX/UI developer.
You will design a user-friendly and visually appealing web interface.
Make the website intuitive and easy to navigate.
```

**设计原则**：
- **可用性优先**：用户目标导向，最小认知负担
- **一致性**：视觉语言、交互模式全局统一
- **反馈及时**：每个操作都有明确的状态反馈
- **容错性强**：防止用户犯错，允许轻松恢复

#### 2. 设计系统组件

| 组件类型 | 核心要素 | 设计检查点 |
|---------|---------|-----------|
| **导航组件** | 顶部导航、侧边栏、面包屑 | 可达性、层级清晰 |
| **表单组件** | 输入框、选择器、按钮 | 状态完整、错误提示 |
| **数据展示** | 表格、卡片、列表 | 信息层次、加载状态 |
| **反馈组件** | 弹窗、Toast、气泡 | 时机合适、不打断流 |
| **容器组件** | 模态框、抽屉、折叠面板 | 层级管理、关闭便捷 |

#### 3. 设计流程

```
Phase 1: 需求分析
├── 用户画像定义
├── 用户旅程地图
└── 核心任务识别

Phase 2: 信息架构
├── 内容组织
├── 导航结构
└── 页面层级

Phase 3: 交互设计
├── 用户流程
├── 交互原型
└── 状态定义

Phase 4: 视觉设计
├── 视觉层级
├── 色彩系统
├── 字体规范
└── 组件样式

Phase 5: 设计评审
├── 可用性测试
├── 可访问性检查
└── 设计走查
```

#### 4. 设计检查清单

| 维度 | 检查项 | 权重 |
|------|--------|------|
| **功能性** | 核心流程完整、交互逻辑正确 | 30% |
| **易用性** | 学习成本低、效率高、错误少 | 25% |
| **可访问性** | WCAG 2.1 AA标准、色盲友好 | 20% |
| **视觉设计** | 品牌一致、层次清晰、美观度 | 15% |
| **性能** | 首屏加载、响应速度、流畅度 | 10% |

### 使用示例

```bash
# 设计一个登录页面
/ux-ui design login --type modal --brand default

# 审查现有界面
/ux-ui audit "https://example.com"

# 构建设计系统
/ux-ui design-system --framework react --style modern
```

### 与其他技能协同

| 协同技能 | 协同方式 |
|---------|---------|
| `taste-3dial` | 设计参数调优 |
| `impeccable` | 设计审查与打磨 |
| `frontend-patterns` | 代码实现 |

### 常用框架适配

| 框架 | 组件库 | 设计工具 |
|------|--------|---------|
| React | shadcn/ui, Ant Design | Figma |
| Vue | Element Plus, Naive UI | Figma |
| Tailwind | Headless UI | Figma |
| Next.js | Radix UI | Figma |

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-05-06 | 初始创建，基于prompts.chat UX Developer |

## 参考资源

- [prompts.chat UX/UI Developer](https://github.com/f/prompts.chat)
- [Ant Design](https://ant.design/)
- [shadcn/ui](https://ui.shadcn.com/)
- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/)
