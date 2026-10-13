---
license: UNKNOWN
---

# shadcn-theme-builder

> 主题配置与品牌定制器 - 基于 CSS Variables 和 Tailwind 的设计系统

## 核心价值

- **品牌定制**: 一键配置品牌色彩、字体、圆角
- **多主题支持**: light/dark/system 自动切换
- **CSS Variables**: 运行时主题切换无需重新构建
- **Tailwind 集成**: 与 Tailwind v4 完美配合

## 触发词

```
主题配置、品牌定制、深色模式、设计系统、色彩方案、
主题切换、品牌色彩、自定义主题
```

## 主题结构

### CSS Variables 基础

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
    --chart-1: 12 76% 61%;
    --chart-2: 173 58% 39%;
    --chart-3: 197 37% 24%;
    --chart-4: 43 74% 66%;
    --chart-5: 27 87% 67%;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
    --chart-1: 220 70% 50%;
    --chart-2: 160 60% 45%;
    --chart-3: 30 80% 55%;
    --chart-4: 280 65% 60%;
    --chart-5: 340 75% 55%;
  }
}
```

## 预设主题

### 1. Default（默认）

```css
/* 经典黑白灰 */
--background: 0 0% 100%;
--foreground: 222.2 84% 4.9%;
--primary: 222.2 47.4% 11.2%;
```

### 2. Slate（石板灰）

```css
/* 专业商务风 */
--background: 0 0% 100%;
--foreground: 222.2 84% 4.9%;
--primary: 215 25% 27%;
```

### 3. Gray（中性灰）

```css
/* 极简主义 */
--background: 0 0% 100%;
--foreground: 220 9% 46%;
--primary: 220 9% 46%;
```

### 4. Zinc（锌灰）

```css
/* 现代科技感 */
--background: 0 0% 100%;
--foreground: 240 10% 3.9%;
--primary: 240 5.9% 10%;
```

### 5. Neutral（自然灰）

```css
/* 温和中性 */
--background: 0 0% 100%;
--foreground: 0 0% 3.9%;
--primary: 0 0% 9%;
```

### 6. Stone（石头灰）

```css
/* 暖色调 */
--background: 0 0% 100%;
--foreground: 20 14.3% 4.1%;
--primary: 24 9.8% 10%;
```

## 使用方式

### CLI 命令

```bash
# 初始化时选择主题
npx shadcn@latest init

# 可选主题: default | slate | gray | zinc | neutral | stone
```

### 自然语言调用

```
[@设计师] 配置一个深色主题
[@设计师] 品牌色改为蓝色系
生成一个科技感的主题配置
```

## 品牌定制示例

### 科技蓝色主题

```css
@layer base {
  :root {
    --background: 210 20% 98%;
    --foreground: 222 47% 11%;
    --primary: 217 91% 60%;
    --primary-foreground: 210 40% 98%;
    --accent: 217 91% 60%;
    --accent-foreground: 210 40% 98%;
    --ring: 217 91% 60%;
  }
}
```

### 金融绿色主题

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 142 76% 36%;
    --primary: 142 76% 36%;
    --primary-foreground: 0 0% 100%;
    --accent: 142 76% 36%;
    --accent-foreground: 0 0% 100%;
  }
}
```

### 电商橙色主题

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 20 14% 4%;
    --primary: 24 95% 53%;
    --primary-foreground: 0 0% 100%;
    --accent: 24 95% 53%;
    --accent-foreground: 0 0% 100%;
  }
}
```

## 主题切换实现

### React 实现

```tsx
"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function ModeToggle() {
  const { setTheme } = useTheme()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>
          Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>
          System
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

## Tailwind 配置

```js
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

## 相关技能

- `shadcn-component-generator` - 组件生成
- `radix-accessibility` - 无障碍模式
- `impeccable` - 设计审查

## 参考资源

- 主题文档: https://ui.shadcn.com/docs/theming
- 色彩系统: https://ui.shadcn.com/colors
- Tailwind CSS: https://tailwindcss.com