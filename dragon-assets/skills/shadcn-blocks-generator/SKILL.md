---
license: UNKNOWN
name: shadcn-blocks-generator
description: 预制页面区块生成器 - 基于 shadcn/ui 的 20+ 企业级页面区块
github_repo: shadcn-ui/ui
github_hash: cc20c8a79493156476de07c4711ea15522d3c446
last_updated: 2026-04-25
source_type: marketplace
triggers: ["shadcn blocks generator", "shadcn-blocks-generator"]
---

# shadcn-blocks-generator

> 预制页面区块生成器 - 基于 shadcn/ui 的 20+ 企业级页面区块

## 核心价值

- **即用区块**: Hero/Features/Pricing/CTA/Dashboard 等开箱即用
- **响应式默认**: 所有区块自动适配移动端/平板/桌面
- **主题兼容**: 完美支持 shadcn/ui 6种主题预设
- **组合式设计**: 区块可自由组合构建完整页面

## 触发词

```
页面区块、Hero区块、定价区块、功能区块、CTA区块、
仪表板区块、着陆页区块、预制组件、页面模板
```

## 区块清单

### Hero 区块 (4种)

| 区块 | 用途 | 特性 |
|------|------|------|
| `hero-centered` | 居中Hero | 标题+副标题+CTA按钮 |
| `hero-split` | 分屏Hero | 左文字+右图片 |
| `hero-gradient` | 渐变Hero | 动态渐变背景 |
| `hero-video` | 视频Hero | 背景视频+叠加文字 |

### Features 区块 (3种)

| 区块 | 用途 | 特性 |
|------|------|------|
| `features-grid` | 功能网格 | 3/4列功能卡片网格 |
| `features-icons` | 图标功能 | 带Lucide图标的功能列表 |
| `features-tabs` | 标签功能 | Tab切换展示功能 |

### Pricing 区块 (3种)

| 区块 | 用途 | 特性 |
|------|------|------|
| `pricing-cards` | 定价卡片 | 3列定价卡片对比 |
| `pricing-table` | 定价表格 | 功能对比表格 |
| `pricing-toggle` | 切换定价 | 月付/年付切换 |

### CTA 区块 (3种)

| 区块 | 用途 | 特性 |
|------|------|------|
| `cta-simple` | 简单CTA | 标题+按钮 |
| `cta-image` | 图片CTA | 左文字+右图片 |
| `cta-gradient` | 渐变CTA | 渐变背景+CTA |

### Dashboard 区块 (4种)

| 区块 | 用途 | 特性 |
|------|------|------|
| `dashboard-header` | 仪表板头部 | 导航+用户信息 |
| `dashboard-stats` | 数据统计 | KPI卡片网格 |
| `dashboard-charts` | 图表区 | Recharts图表 |
| `dashboard-table` | 数据表格 | TanStack Table |

### Testimonials 区块 (2种)

| 区块 | 用途 | 特性 |
|------|------|------|
| `testimonials-cards` | 评价卡片 | 用户评价网格 |
| `testimonials-carousel` | 评价轮播 | 滚动评价展示 |

### Footer 区块 (2种)

| 区块 | 用途 | 特性 |
|------|------|------|
| `footer-simple` | 简单页脚 | 链接+版权 |
| `footer-multi` | 多列页脚 | 多列链接+社交媒体 |

## 使用方式

### CLI 命令

```bash
# 添加单个区块
npx shadcn@latest add https://ui.shadcn.com/registry/default/block/hero-centered.json

# 批量添加区块
npx shadcn@latest add \
  https://ui.shadcn.com/registry/default/block/hero-centered.json \
  https://ui.shadcn.com/registry/default/block/features-grid.json \
  https://ui.shadcn.com/registry/default/block/pricing-cards.json

# 使用 npx shadcn-ui-blocks（推荐）
npx shadcn-ui-blocks add hero-centered
npx shadcn-ui-blocks add hero features pricing  # 批量添加
```

### 自然语言调用

```
[@设计师] 生成一个Hero区块，包含标题和CTA按钮
[@构建师] 添加定价区块到项目
生成一个完整的着陆页，包含Hero、Features、Pricing、CTA
```

### 代码示例

#### Hero Centered 区块

```tsx
import { Button } from "@/components/ui/button"

export function HeroCentered() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex flex-col items-center space-y-4 text-center">
          <div className="space-y-2">
            <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
              构建你的下一个想法
            </h1>
            <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
              使用我们现代化的组件库，快速构建美观、响应式的应用程序。
            </p>
          </div>
          <div className="space-x-4">
            <Button>立即开始</Button>
            <Button variant="outline">了解更多</Button>
          </div>
        </div>
      </div>
    </section>
  )
}
```

#### Features Grid 区块

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Cloud, Cog, Shield } from "lucide-react"

const features = [
  {
    title: "云端部署",
    description: "一键部署到全球CDN，自动扩展。",
    icon: Cloud,
  },
  {
    title: "安全可靠",
    description: "企业级安全，数据加密传输。",
    icon: Shield,
  },
  {
    title: "灵活配置",
    description: "高度可定制，满足各种需求。",
    icon: Cog,
  },
]

export function FeaturesGrid() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 bg-muted/50">
      <div className="container mx-auto px-4 md:px-6">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title}>
              <CardHeader>
                <feature.icon className="h-10 w-10 mb-2 text-primary" />
                <CardTitle>{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
```

#### Pricing Cards 区块

```tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

const plans = [
  {
    name: "入门版",
    price: "¥99",
    description: "适合个人用户",
    features: ["5个项目", "10GB存储", "邮件支持"],
  },
  {
    name: "专业版",
    price: "¥299",
    description: "适合小型团队",
    features: ["无限项目", "100GB存储", "优先支持", "API访问"],
    popular: true,
  },
  {
    name: "企业版",
    price: "联系我们",
    description: "适合大型企业",
    features: ["无限一切", "专属客户经理", "定制集成", "SLA保障"],
  },
]

export function PricingCards() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32">
      <div className="container mx-auto px-4 md:px-6">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {plans.map((plan) => (
            <Card key={plan.name} className={plan.popular ? "border-primary" : ""}>
              <CardHeader>
                {plan.popular && (
                  <span className="text-xs text-primary font-medium">最受欢迎</span>
                )}
                <CardTitle>{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{plan.price}</div>
                <ul className="mt-4 space-y-2">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center text-sm">
                      <span className="mr-2">✓</span>
                      {feature}
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter>
                <Button className="w-full" variant={plan.popular ? "default" : "outline"}>
                  开始使用
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
```

## 完整页面组合示例

### 着陆页组合

```tsx
import { HeroCentered } from "@/components/blocks/hero-centered"
import { FeaturesGrid } from "@/components/blocks/features-grid"
import { PricingCards } from "@/components/blocks/pricing-cards"
import { TestimonialsCards } from "@/components/blocks/testimonials-cards"
import { CtaSimple } from "@/components/blocks/cta-simple"
import { FooterSimple } from "@/components/blocks/footer-simple"

export default function LandingPage() {
  return (
    <main>
      <HeroCentered />
      <FeaturesGrid />
      <PricingCards />
      <TestimonialsCards />
      <CtaSimple />
      <FooterSimple />
    </main>
  )
}
```

### 仪表板页面组合

```tsx
import { DashboardHeader } from "@/components/blocks/dashboard-header"
import { DashboardStats } from "@/components/blocks/dashboard-stats"
import { DashboardCharts } from "@/components/blocks/dashboard-charts"
import { DashboardTable } from "@/components/blocks/dashboard-table"

export default function DashboardPage() {
  return (
    <main>
      <DashboardHeader />
      <DashboardStats />
      <DashboardCharts />
      <DashboardTable />
    </main>
  )
}
```

## 与现有技能协同

| 技能 | 协同方式 |
|------|---------|
| **shadcn-component-generator** | 区块 → 组件组合 |
| **shadcn-theme-builder** | 区块自动应用主题 |
| **impeccable** | 区块生成 → /audit → /polish |
| **frontend-patterns** | 区块 + React模式 |
| **marketing-skills** | 区块 → 营销页面生成 |

## 响应式断点

| 断点 | 宽度 | 区块行为 |
|------|------|---------|
| `sm` | 640px | 单列布局 |
| `md` | 768px | 2列布局 |
| `lg` | 1024px | 3-4列布局 |
| `xl` | 1280px | 最大宽度 |

## 主题兼容

所有区块支持 shadcn/ui 的 6 种主题预设：

- `default` - 经典黑白灰
- `slate` - 专业商务风
- `gray` - 极简主义
- `zinc` - 现代科技感
- `neutral` - 温和中性
- `stone` - 暖色调

## 参考资源

- 官方区块: https://ui.shadcn.com/blocks
- 组件文档: https://ui.shadcn.com/docs/components
- 主题配置: https://ui.shadcn.com/docs/theming
- GitHub: https://github.com/shadcn-ui/ui