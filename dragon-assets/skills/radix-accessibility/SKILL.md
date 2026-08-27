---
license: UNKNOWN
github_repo: dequelabs/axe-core
github_hash: ea7202c6bf1a6166c878dbf19bb5454372b61fae
last_updated: 2026-04-25
source_type: derived
triggers: ["radix accessibility", "radix-accessibility"]
---
# radix-accessibility

> Radix UI 无障碍设计模式 - WCAG 2.1 AA 合规组件库

## 核心价值

- **WCAG 2.1 AA 合规**: 自动满足无障碍标准
- **键盘导航**: 完整键盘操作支持
- **屏幕阅读器**: ARIA 属性自动管理
- **焦点管理**: 智能焦点陷阱和恢复

## 触发词

```
无障碍、可访问性、a11y、WCAG、键盘导航、屏幕阅读器、
ARIA、焦点管理、无障碍审计
```

## Radix UI 原则

### 1. 无障碍优先

所有组件默认满足:
- ✅ WCAG 2.1 AA 标准
- ✅ WAI-ARIA 设计模式
- ✅ 键盘导航规范
- ✅ 屏幕阅读器兼容

### 2. 无样式设计

```tsx
// Radix 提供行为，你提供样式
import * as Dialog from "@radix-ui/react-dialog"

<Dialog.Root>
  <Dialog.Trigger className="your-styles">Open</Dialog.Trigger>
  <Dialog.Portal>
    <Dialog.Overlay className="your-overlay-styles" />
    <Dialog.Content className="your-content-styles">
      <Dialog.Title>Title</Dialog.Title>
      <Dialog.Description>Description</Dialog.Description>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

### 3. 组合式 API

```tsx
// 完全控制组件结构
<Dialog.Root>
  <Dialog.Trigger />
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title />
      <Dialog.Description />
      <Dialog.Close />
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

## 无障碍模式

### 1. 键盘导航

| 组件 | 快捷键 |
|------|--------|
| Dialog | Escape 关闭 |
| Menu | Arrow keys 导航, Enter 选择 |
| Tabs | Arrow keys 切换, Home/End 首尾 |
| Select | Arrow keys 选择, Enter 确认 |
| Combobox | Arrow keys + Enter 选择 |

### 2. 焦点管理

```tsx
// 自动焦点陷阱
<Dialog.Content>
  {/* 焦点被限制在 Dialog 内 */}
  <input />
  <button>Submit</button>
</Dialog.Content>

// 焦点恢复
<Dialog.Close>
  {/* 关闭后焦点回到触发元素 */}
</Dialog.Close>
```

### 3. ARIA 属性

```tsx
// Radix 自动管理 ARIA
<Dialog.Root>
  <Dialog.Trigger
    aria-haspopup="dialog"  // 自动添加
    aria-expanded="false"   // 自动管理
  >
    Open
  </Dialog.Trigger>
  <Dialog.Content
    role="dialog"           // 自动添加
    aria-modal="true"       // 自动添加
    aria-labelledby="..."   // 自动关联 Title
  >
    <Dialog.Title id="...">Title</Dialog.Title>
  </Dialog.Content>
</Dialog.Root>
```

## 组件清单

### 交互组件

| 组件 | 无障碍特性 |
|------|-----------|
| Accordion | 展开/折叠键盘导航 |
| Alert Dialog | 焦点陷阱, Escape 关闭 |
| Checkbox | 混合状态支持 |
| Collapsible | 展开/折叠状态 |
| Combobox | 自动完成, 键盘选择 |
| Context Menu | 右键菜单导航 |
| Dialog | 模态, 焦点陷阱 |
| Dropdown Menu | 键盘导航, 搜索 |
| Hover Card | 悬浮信息 |
| Menubar | 菜单栏导航 |
| Navigation Menu | 导航结构 |
| Popover | 弹出内容 |
| Progress | 进度条 |
| Radio Group | 单选导航 |
| Scroll Area | 虚拟滚动 |
| Select | 下拉选择 |
| Slider | 滑块调节 |
| Switch | 开关状态 |
| Tabs | 标签页切换 |
| Toast | 通知提示 |
| Toggle | 切换按钮 |
| Toggle Group | 按钮组 |
| Toolbar | 工具栏 |
| Tooltip | 工具提示 |

### 实用组件

| 组件 | 用途 |
|------|------|
| Aspect Ratio | 宽高比容器 |
| Avatar | 头像 |
| Label | 表单标签 |
| Portal | 传送门 |
| Primitive | 原始组件 |
| Slot | 插槽 |
| Visually Hidden | 视觉隐藏 |

## 使用示例

### 可访问对话框

```tsx
import * as AlertDialog from "@radix-ui/react-alert-dialog"

const AlertDialogDemo = () => (
  <AlertDialog.Root>
    <AlertDialog.Trigger asChild>
      <button>Delete account</button>
    </AlertDialog.Trigger>
    <AlertDialog.Portal>
      <AlertDialog.Overlay className="AlertDialogOverlay" />
      <AlertDialog.Content className="AlertDialogContent">
        <AlertDialog.Title className="AlertDialogTitle">
          Are you absolutely sure?
        </AlertDialog.Title>
        <AlertDialog.Description className="AlertDialogDescription">
          This action cannot be undone. This will permanently delete your
          account and remove your data from our servers.
        </AlertDialog.Description>
        <div style={{ display: 'flex', gap: 25, justifyContent: 'flex-end' }}>
          <AlertDialog.Cancel asChild>
            <button className="Button mauve">Cancel</button>
          </AlertDialog.Cancel>
          <AlertDialog.Action asChild>
            <button className="Button red">Yes, delete account</button>
          </AlertDialog.Action>
        </div>
      </AlertDialog.Content>
    </AlertDialog.Portal>
  </AlertDialog.Root>
)
```

### 可访问标签页

```tsx
import * as Tabs from "@radix-ui/react-tabs"

const TabsDemo = () => (
  <Tabs.Root className="TabsRoot" defaultValue="tab1">
    <Tabs.List className="TabsList" aria-label="Manage your account">
      <Tabs.Trigger className="TabsTrigger" value="tab1">
        Account
      </Tabs.Trigger>
      <Tabs.Trigger className="TabsTrigger" value="tab2">
        Password
      </Tabs.Trigger>
    </Tabs.List>
    <Tabs.Content className="TabsContent" value="tab1">
      <p className="Text">Make changes to your account here.</p>
    </Tabs.Content>
    <Tabs.Content className="TabsContent" value="tab2">
      <p className="Text">Change your password here.</p>
    </Tabs.Content>
  </Tabs.Root>
)
```

## 无障碍审计清单

### 自动检查（axe-core）

```bash
# 安装 axe-core
npm install --save-dev @axe-core/react

# 集成到测试
import { axe } from 'jest-axe'

it('should have no accessibility violations', async () => {
  const { container } = render(<Button />)
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
```

### 手动检查清单

| 检查项 | 通过标准 |
|--------|---------|
| 键盘导航 | Tab/Shift+Tab/Arrow keys 可操作 |
| 焦点可见 | 焦点状态清晰可见 |
| 屏幕阅读器 | VoiceOver/NVDA 可正确朗读 |
| 颜色对比度 | 文字对比度 ≥ 4.5:1 |
| 触控目标 | 最小 44x44px |
| 动画 | 尊重 prefers-reduced-motion |

## 与 shadcn-ui 协同

```bash
# shadcn 组件已内置 Radix UI 无障碍
npx shadcn@latest add dialog  # 自动包含焦点陷阱
npx shadcn@latest add tabs    # 自动包含键盘导航
```

## 相关资源

- Radix UI: https://www.radix-ui.com
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
- WAI-ARIA: https://www.w3.org/WAI/ARIA/apg/
- axe-core: https://github.com/dequelabs/axe-core