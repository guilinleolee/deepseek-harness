---
license: UNKNOWN
github_repo: shadcn-ui/ui
github_hash: cc20c8a79493156476de07c4711ea15522d3c446
last_updated: 2026-04-25
source_type: derived
triggers: ["shadcn component generator", "shadcn-component-generator"]
---
# shadcn-component-generator

> 企业级 UI 组件生成器 - 基于 shadcn/ui 的 60+ 可定制组件

## 核心价值

- **白盒源码**: 组件代码直接复制到项目，完全可控
- **无障碍默认**: 基于 Radix UI，WCAG 2.1 AA 合规
- **类型安全**: 完整 TypeScript 支持
- **主题化**: CSS Variables + Tailwind 集成

## 触发词

```
shadcn组件、生成组件、UI组件、按钮组件、对话框组件、
表单组件、表格组件、卡片组件、导航组件、命令菜单、
数据表格、轮播组件、侧边栏、抽屉组件
```

## 组件清单（60+）

### 基础组件 (20+)

| 组件 | 用途 | 无障碍 |
|------|------|--------|
| `button` | 按钮 | ✅ |
| `input` | 输入框 | ✅ |
| `checkbox` | 复选框 | ✅ Radix |
| `radio-group` | 单选组 | ✅ Radix |
| `select` | 下拉选择 | ✅ Radix |
| `switch` | 开关 | ✅ Radix |
| `slider` | 滑块 | ✅ Radix |
| `textarea` | 多行输入 | ✅ |
| `label` | 标签 | ✅ |
| `form` | 表单 | ✅ React Hook Form |

### 布局组件 (12+)

| 组件 | 用途 | 无障碍 |
|------|------|--------|
| `card` | 卡片 | ✅ |
| `dialog` | 对话框 | ✅ Radix |
| `sheet` | 抽屉 | ✅ Radix |
| `sidebar` | 侧边栏 | ✅ 可组合 |
| `tabs` | 标签页 | ✅ Radix |
| `accordion` | 手风琴 | ✅ Radix |
| `separator` | 分隔线 | ✅ Radix |
| `scroll-area` | 滚动区域 | ✅ Radix |
| `drawer` | 抽屉组件 | ✅ vaul |

### 数据展示 (15+)

| 组件 | 用途 | 无障碍 |
|------|------|--------|
| `table` | 表格 | ✅ |
| `data-table` | 数据表格 | ✅ TanStack Table |
| `badge` | 徽章 | ✅ |
| `avatar` | 头像 | ✅ Radix |
| `calendar` | 日历 | ✅ Radix |
| `chart` | 图表 | ✅ Recharts |
| `progress` | 进度条 | ✅ Radix |
| `skeleton` | 骨架屏 | ✅ |
| `carousel` | 轮播组件 | ✅ Embla |

### 反馈组件 (10+)

| 组件 | 用途 | 无障碍 |
|------|------|--------|
| `alert` | 警告 | ✅ |
| `toast` | 轻提示 | ✅ Sonner |
| `tooltip` | 工具提示 | ✅ Radix |
| `popover` | 弹出框 | ✅ Radix |
| `hover-card` | 悬浮卡片 | ✅ Radix |
| `alert-dialog` | 确认对话框 | ✅ Radix |

### 🆕 高级组件 (5+)

| 组件 | 用途 | 无障碍 | 依赖 |
|------|------|--------|------|
| `command` | 命令菜单 (⌘K) | ✅ | cmdk |
| `data-table` | 高级数据表格 | ✅ | @tanstack/react-table |
| `carousel` | 轮播组件 | ✅ | embla-carousel-react |
| `drawer` | 抽屉组件 | ✅ | vaul |
| `sidebar` | 可组合侧边栏 | ✅ | - |

## 使用方式

### CLI 命令

```bash
# 初始化 shadcn-ui
npx shadcn@latest init

# 添加单个组件
npx shadcn@latest add button
npx shadcn@latest add dialog
npx shadcn@latest add form

# 批量添加组件
npx shadcn@latest add button dialog input select

# 查看所有可用组件
npx shadcn@latest add

# Dry run（预览不安装）
npx shadcn@latest add button --dry-run
```

### 自然语言调用

```
[@设计师] 生成一个登录表单组件
[@构建师] 添加对话框组件到项目
生成一个包含按钮、输入框、选择器的表单
```

## 组件生成示例

### Button 组件

```tsx
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline:
          "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

### Dialog 组件

```tsx
"use client"

import * as React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { X } from "lucide-react"

import { cn } from "@/lib/utils"

const Dialog = DialogPrimitive.Root

const DialogTrigger = DialogPrimitive.Trigger

const DialogPortal = DialogPrimitive.Portal

const DialogClose = DialogPrimitive.Close

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      "fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className
    )}
    {...props}
  />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg",
        className
      )}
      {...props}
    >
      {children}
      <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
        <X className="h-4 w-4" />
        <span className="sr-only">Close</span>
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPortal>
))
DialogContent.displayName = DialogPrimitive.Content.displayName

const DialogHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex flex-col space-y-1.5 text-center sm:text-left",
      className
    )}
    {...props}
  />
)
DialogHeader.displayName = "DialogHeader"

const DialogFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2",
      className
    )}
    {...props}
  />
)
DialogFooter.displayName = "DialogFooter"

const DialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn(
      "text-lg font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
DialogTitle.displayName = DialogPrimitive.Title.displayName

const DialogDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
DialogDescription.displayName = DialogPrimitive.Description.displayName

export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogClose,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
}
```

## 与 Impeccable 协同

```bash
# 先用 shadcn 生成组件
npx shadcn@latest add button dialog form

# 再用 Impeccable 审查设计
/audit button.tsx
/critique dialog.tsx
```

## 相关技能

- `shadcn-theme-builder` - 主题配置
- `shadcn-blocks-generator` - 预制页面区块
- `radix-accessibility` - 无障碍模式
- `impeccable` - 设计审查
- `frontend-patterns` - 前端模式

## 🆕 高级组件详解

### Command（命令菜单）

⌘K 快捷键搜索/命令菜单，支持键盘导航和模糊搜索。

```bash
npx shadcn@latest add command
```

```tsx
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command"

export function CommandMenu() {
  const [open, setOpen] = React.useState(false)

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }

    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="搜索命令..." />
      <CommandList>
        <CommandEmpty>未找到结果</CommandEmpty>
        <CommandGroup heading="建议">
          <CommandItem>
            <Search className="mr-2 h-4 w-4" />
            <span>搜索文档</span>
            <CommandShortcut>⌘F</CommandShortcut>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}
```

### Data Table（高级数据表格）

基于 TanStack Table 的企业级数据表格，支持排序/过滤/分页/列可见性。

```bash
npx shadcn@latest add data-table
```

```tsx
import { DataTable } from "@/components/ui/data-table"
import { columns } from "./columns"

export function UsersTable({ data }: { data: User[] }) {
  return (
    <DataTable
      columns={columns}
      data={data}
      searchKey="name"
      searchPlaceholder="搜索用户名..."
    />
  )
}

// columns.tsx
export const columns: ColumnDef<User>[] = [
  {
    accessorKey: "name",
    header: "姓名",
  },
  {
    accessorKey: "email",
    header: "邮箱",
  },
  {
    accessorKey: "status",
    header: "状态",
    cell: ({ row }) => {
      const status = row.getValue("status")
      return <Badge variant={status === "active" ? "default" : "secondary"}>{status}</Badge>
    },
  },
]
```

### Carousel（轮播组件）

基于 Embla Carousel 的轮播组件，支持自动播放/循环/拖拽。

```bash
npx shadcn@latest add carousel
```

```tsx
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel"

export function ImageCarousel({ images }: { images: string[] }) {
  return (
    <Carousel className="w-full max-w-xs">
      <CarouselContent>
        {images.map((src, index) => (
          <CarouselItem key={index}>
            <img src={src} alt={`Slide ${index + 1}`} className="w-full h-full object-cover" />
          </CarouselItem>
        ))}
      </CarouselContent>
      <CarouselPrevious />
      <CarouselNext />
    </Carousel>
  )
}
```

### Drawer（抽屉组件）

基于 vaul 的抽屉组件，支持手势滑动和嵌套。

```bash
npx shadcn@latest add drawer
```

```tsx
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer"

export function CartDrawer() {
  return (
    <Drawer>
      <DrawerTrigger asChild>
        <Button variant="outline">打开购物车</Button>
      </DrawerTrigger>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>购物车</DrawerTitle>
          <DrawerDescription>查看您的购物车商品</DrawerDescription>
        </DrawerHeader>
        <div className="p-4">
          {/* 购物车内容 */}
        </div>
        <DrawerFooter>
          <Button>结算</Button>
          <DrawerClose asChild>
            <Button variant="outline">取消</Button>
          </DrawerClose>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  )
}
```

### Sidebar（可组合侧边栏）

灵活的可组合侧边栏组件，支持折叠/展开/响应式。

```bash
npx shadcn@latest add sidebar
```

```tsx
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"

export function AppSidebar() {
  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader>
          <h2 className="text-lg font-semibold">我的应用</h2>
        </SidebarHeader>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>导航</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {items.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton asChild>
                      <a href={item.url}>
                        <item.icon />
                        <span>{item.title}</span>
                      </a>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
        <SidebarFooter>
          <p className="text-xs text-muted-foreground">© 2024 我的应用</p>
        </SidebarFooter>
      </Sidebar>
      <main className="flex-1">
        <SidebarTrigger />
        {/* 主内容区 */}
      </main>
    </SidebarProvider>
  )
}
```

## 参考资源

- 官网: https://ui.shadcn.com
- 文档: https://ui.shadcn.com/docs
- 组件: https://ui.shadcn.com/docs/components
- 区块: https://ui.shadcn.com/blocks
- GitHub: https://github.com/shadcn-ui/ui