---
license: UNKNOWN
---

# SaaS Quick Builder - 超级个体SaaS快速构建

## L0: 一句话描述
一周上线MVP！TypeScript + Next.js + Stripe + Supabase 完整技术栈。

## L1: 使用场景

适用场景：
- 独立开发者快速构建SaaS MVP
- 超级个体全栈技术方案
- 快速原型验证商业想法

触发关键词：
- "快速构建SaaS"
- "技术栈推荐"
- "Next.js SaaS"
- "Stripe集成"
- "MVP技术方案"

## L2: 详细文档

### 技术栈选择

```
┌─────────────────────────────────────────────────────────────┐
│                   SaaS Quick Builder ⭐ 一周MVP技术栈         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  前端框架: Next.js 14 (App Router)                        │
│  ├── React Server Components                               │
│  ├── Server Actions                                       │
│  └── TypeScript strict mode                              │
│                                                             │
│  样式方案: TailwindCSS + shadcn/ui                       │
│  ├── 原子化CSS                                           │
│  ├── 组件库shadcn/ui                                     │
│  └── 深色模式支持                                         │
│                                                             │
│  数据库: Supabase                                          │
│  ├── PostgreSQL                                          │
│  ├── Row Level Security (RLS)                            │
│  ├── Auth (邮箱 + 社交登录)                              │
│  ├── Storage (文件上传)                                   │
│  └── Realtime (实时功能)                                 │
│                                                             │
│  支付: Stripe                                             │
│  ├── Checkout (结账页面)                                  │
│  ├── Customer Portal (客户门户)                            │
│  ├── Webhooks (支付回调)                                  │
│  └── Usage-based Billing (用量计费)                       │
│                                                             │
│  邮件: Resend + React Email                               │
│  ├── 交易邮件                                            │
│  └── 营销邮件                                            │
│                                                             │
│  部署: Vercel                                            │
│  ├── 自动部署                                            │
│  ├── Edge Functions                                      │
│  └── Analytics                                          │
│                                                             │
│  监控: Sentry + Vercel Analytics                        │
│  ├── 错误追踪                                            │
│  └── 性能监控                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 项目结构

```
saas-mvp/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── signup/page.tsx
│   │   └── forgot-password/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── settings/page.tsx
│   │   └── billing/page.tsx
│   ├── (marketing)/
│   │   ├── page.tsx
│   │   ├── pricing/page.tsx
│   │   └── blog/[slug]/page.tsx
│   ├── api/
│   │   ├── webhooks/stripe/route.ts
│   │   └── auth/[...nextauth]/route.ts
│   ├── layout.tsx
│   └── globals.css
├── components/
│   ├── ui/ (shadcn components)
│   ├── landing/
│   ├── dashboard/
│   └── auth/
├── lib/
│   ├── supabase/
│   │   ├── client.ts
│   │   ├── server.ts
│   │   └── middleware.ts
│   ├── stripe/
│   │   ├── client.ts
│   │   ├── server.ts
│   │   └── webhooks.ts
│   └── utils.ts
├── types/
│   └── index.ts
├── .env.local
├── .env.example
├── tailwind.config.ts
├── next.config.js
├── package.json
└── tsconfig.json
```

### Stripe集成核心代码

```typescript
// lib/stripe/server.ts
import Stripe from 'stripe';

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
  typescript: true,
});

// 创建结账会话
export async function createCheckoutSession({
  priceId,
  customerId,
  successUrl,
  cancelUrl,
}: {
  priceId: string;
  customerId?: string;
  successUrl: string;
  cancelUrl: string;
}) {
  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    payment_method_types: ['card'],
    line_items: [{ price: priceId, quantity: 1 }],
    ...(customerId && { customer: customerId }),
    success_url: successUrl,
    cancel_url: cancelUrl,
    subscription_data: {
      metadata: { userId: 'to-be-set' },
    },
  });
  return session;
}

// 创建客户门户会话
export async function createPortalSession(customerId: string, returnUrl: string) {
  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: returnUrl,
  });
  return session;
}

// Webhook处理
export async function handleSubscriptionWebhook(event: Stripe.Event) {
  switch (event.type) {
    case 'checkout.session.completed':
      // 激活订阅
      break;
    case 'customer.subscription.updated':
      // 更新订阅状态
      break;
    case 'customer.subscription.deleted':
      // 取消订阅
      break;
    case 'invoice.payment_failed':
      // 支付失败
      break;
  }
}
```

### Supabase集成核心代码

```typescript
// lib/supabase/server.ts
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          } catch {
            // Server Component中无法设置cookies
          }
        },
      },
    }
  );
}

// RLS策略示例
/*
-- 用户只能访问自己的数据
CREATE POLICY "Users can only access their own data"
ON public.user_data
FOR ALL
USING (auth.uid() = user_id);

-- 订阅用户可以访问高级功能
CREATE POLICY "Subscribers can access premium features"
ON public.features
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.subscriptions
    WHERE user_id = auth.uid()
    AND status = 'active'
  )
);
*/
```

### Next.js App Router最佳实践

```typescript
// app/(dashboard)/layout.tsx
import { redirect } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    redirect('/login');
  }

  return (
    <div className="flex h-screen">
      <Sidebar user={user} />
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}

// app/api/webhooks/stripe/route.ts
import { headers } from 'next/headers';
import { stripe, handleSubscriptionWebhook } from '@/lib/stripe/server';
import { createClient } from '@/lib/supabase/server';

export async function POST(req: Request) {
  const body = await req.text();
  const signature = headers().get('stripe-signature')!;

  let event;
  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    return new Response('Webhook Error', { status: 400 });
  }

  await handleSubscriptionWebhook(event);

  return new Response(null, { status: 200 });
}
```

### 一周MVP开发计划

```
Day 1: 项目初始化
├── Next.js 14 项目创建
├── TailwindCSS + shadcn/ui 配置
├── Supabase 项目创建
├── Stripe 账户配置
└── GitHub 仓库初始化

Day 2: 认证系统
├── Supabase Auth 配置
├── 登录/注册/忘记密码页面
├── Middleware 路由保护
└── 用户Profile页面

Day 3: 核心功能
├── 数据库Schema设计
├── CRUD API编写
├── RLS策略配置
└── Dashboard页面

Day 4: 支付集成
├── Stripe 产品/价格创建
├── Checkout 页面集成
├── Webhook 处理
├── 客户门户集成
└── 订阅状态显示

Day 5: 邮件系统
├── Resend 配置
├── React Email 模板
├── 欢迎邮件
├── 订阅确认邮件
└── 发票邮件

Day 6: 部署上线
├── Vercel 部署
├── 环境变量配置
├── 域名配置
├── SSL 证书
└── 监控配置

Day 7: 验证发布
├── Product Hunt 准备
├── 社交媒体准备
├── 文档完善
└── 正式发布
```

### 环境变量模板

```bash
# .env.local

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Resend
RESEND_API_KEY=re_xxx

# NextAuth
NEXTAUTH_SECRET=your-secret
NEXTAUTH_URL=http://localhost:3000

# Vercel (自动注入)
# VERCEL_URL
# VERCEL_ENV
```

### 定价页面组件

```tsx
// components/pricing.tsx
const plans = [
  {
    name: 'Starter',
    price: '$9',
    description: 'Perfect for getting started',
    features: ['5 Projects', 'Basic Analytics', 'Email Support'],
    priceId: 'price_xxx',
  },
  {
    name: 'Pro',
    price: '$29',
    description: 'For growing teams',
    features: ['Unlimited Projects', 'Advanced Analytics', 'Priority Support', 'API Access'],
    priceId: 'price_yyy',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: '$99',
    description: 'For large organizations',
    features: ['Everything in Pro', 'Custom Integrations', 'Dedicated Support', 'SLA'],
    priceId: 'price_zzz',
  },
];

export function PricingPage() {
  return (
    <div className="grid md:grid-cols-3 gap-8">
      {plans.map((plan) => (
        <div key={plan.name} className="...">
          <h3>{plan.name}</h3>
          <p>{plan.price}/month</p>
          <ul>
            {plan.features.map((f) => (
              <li key={f}>{f}</li>
            ))}
          </ul>
          <CheckoutButton priceId={plan.priceId} />
        </div>
      ))}
    </div>
  );
}
```

## L3: 扩展内容

### 常用npm包

```bash
# 核心依赖
npm install next@14 react react-dom
npm install typescript @types/react @types/node
npm install tailwindcss postcss autoprefixer
npm install @supabase/supabase-js @supabase/ssr
npm install stripe @stripe/stripe-js
npm install resend @react-email/components
npm install next-auth @auth/supabase-adapter
npm install zod react-hook-form @hookform/resolvers
npm install lucide-react class-variance-authority clsx tailwind-merge

# 开发依赖
npm install -D @types/node
npm install -D tailwindcss-animate
```

### shadcn/ui组件安装

```bash
# 初始化
npx shadcn@latest init

# 常用组件
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add form
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
npx shadcn@latest add avatar
npx shadcn@latest add badge
npx shadcn@latest add tabs
```

### 性能优化建议

```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['images.unsplash.com'],
  },
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
};

module.exports = nextConfig;
```

### SEO优化

```tsx
// app/layout.tsx
export const metadata: Metadata = {
  title: 'Your SaaS Name',
  description: 'The best SaaS for your needs',
  keywords: ['SaaS', 'Productivity', 'Tools'],
  authors: [{ name: 'Your Name' }],
  openGraph: {
    title: 'Your SaaS Name',
    description: 'The best SaaS for your needs',
    url: 'https://yoursaas.com',
    siteName: 'Your SaaS',
    images: ['/og-image.png'],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Your SaaS Name',
    description: 'The best SaaS for your needs',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
  },
};
```
