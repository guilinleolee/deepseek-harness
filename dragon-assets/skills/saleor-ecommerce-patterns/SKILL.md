---
license: UNKNOWN
triggers: ["saleor ecommerce patterns", "Saleor 电商框架模式 SKILL.md"]
---
# Saleor 电商框架模式 SKILL.md

## L0
Python GraphQL电商引擎，headless多渠道商务

## L1
Python/Django GraphQL-first headless电商，App扩展生态，多渠道商务，多语言多货币。适合Python技术栈团队，电商核心模块需GraphQL API的企业，与Medusa形成Python/JS技术栈互补。

## L2
Saleor是开源headless电商平台，GraphQL API优先，多渠道商务原生支持。核心模块含产品目录/订单/支付/客户/配送。App Framework通过manifest扩展dashboard，无需fork代码。与Medusa对比：GraphQL-native vs REST+GraphQL，Python vs TypeScript，多渠道商务原生。

---

## 1. 框架速查

### 核心定位

| 属性 | 值 |
|------|-----|
| **Stars** | 22,900+ |
| **License** | BSD-3-Clause |
| **主语言** | Python 99.2% |
| **框架** | Django + Graphene |
| **前端** | React Dashboard |
| **API** | GraphQL (APIv1 / APIv2 New Behavior) |

### Saleor vs Medusa 技术栈对比

| 维度 | Saleor | Medusa |
|------|--------|--------|
| **后端语言** | Python | TypeScript/Node.js |
| **ORM** | Django ORM | Typeorm/MedusaService |
| **API风格** | GraphQL-first | REST + 可选GraphQL |
| **核心架构** | Django App | Module Service |
| **前端** | React Dashboard | Next.js Starter |
| **App扩展** | manifest.json | Plugin System |
| **多渠道** | First-class Channel | 多store实例 |
| **Webhook安全** | HMAC-SHA256 | 自定义签名 |

---

## 2. 核心架构

### 系统分层

```
┌─────────────────────────────────────────────────────┐
│                  Saleor Platform                     │
├─────────────────────────────────────────────────────┤
│  React Dashboard ( storefront-dashboard )            │
├─────────────────────────────────────────────────────┤
│  Saleor App SDK ( @saleor/app-sdk )                │
│  ├── AppBridge    (Dashboard→App通信)              │
│  ├── API Handler  (App→Saleor API)               │
│  ├── Protected Views (Dashboard嵌入)              │
│  ├── Webhook Utils (Webhook订阅)                  │
│  ├── Settings Manager (App配置存储)              │
│  └── APL (Auth Persistence Layer)                  │
├─────────────────────────────────────────────────────┤
│  GraphQL API ( Graphene-Django )                   │
│  ├── APIv1  (legacy)                             │
│  ├── APIv2  (New Behavior, 2024+)               │
│  └── Subscriptions (实时订阅)                     │
├─────────────────────────────────────────────────────┤
│  Django Core Apps                                  │
│  ├── product (目录/变体/分类)                    │
│  ├── order (订单/发货/退款)                      │
│  ├── checkout (购物车/结账)                      │
│  ├── warehouse (库存/仓库)                        │
│  ├── shipping (配送方式)                          │
│  ├── payment (支付/Transaction)                   │
│  ├── account (客户/地址/权限)                    │
│  └── channel (渠道/定价/货币)                    │
├─────────────────────────────────────────────────────┤
│  Django ORM + PostgreSQL                          │
└─────────────────────────────────────────────────────┘
```

### App Framework vs Medusa Plugin System

```
┌──────────────────┬──────────────────────┬──────────────────┐
│ 维度             │ Saleor App          │ Medusa Plugin     │
├──────────────────┼──────────────────────┼──────────────────┤
│ 注册方式          │ manifest.json        │medusa-config.js  │
│ Dashboard集成    │ ✅ 原生嵌入          │ ❌ 无             │
│ 安装方式          │ Dashboard UI/App市场 │ npm install      │
│ 权限模型         │ OAuth 2.0 + 细粒度  │ API Key          │
│ 配置存储         │ Settings Manager     │ Plugin config     │
│ Webhook订阅      │ manifest声明         │ subscribe()方法   │
│ 前端扩展         │ ✅ 支持              │ ❌ 无             │
│ 测试方式         │ Mocked APL           │ TestService       │
└──────────────────┴──────────────────────┴──────────────────┘
```

---

## 3. GraphQL API层

### APIv2 (New Behavior)

Saleor 4.0+引入APIv2 "New Behavior"，重大变更：

```python
# APIv1: 嵌套查询
query {
  product(id: "xxx") {
    name
    variants {
      name
      stock {
        quantity
      }
    }
  }
}

# APIv2: 扁平化关联查询
query {
  product(id: "xxx") {
    name
    variants {
      name
    }
  }
  stock(filter: { variants: ["xxx"] }) {
    quantity
  }
}
```

### Webhook EventPayload

```python
from saleor.webhook.payloads import generate_product_payload

payload = generate_product_payload(product_instance)
# → JSON payload含product + variants + attributes + images + category
```

### Subscription类型

```python
# 定义subscription查询
SUBSCRIPTION_PRODUCT_CREATED = """
  subscription {
    event {
      ... on ProductCreated {
        product {
          id
          name
          thumbnail { url }
        }
      }
    }
  }
"""

# 注册到manifest
"subscriptions": {
  "Product.created": SUBSCRIPTION_PRODUCT_CREATED
}
```

---

## 4. App Framework

### manifest.json 结构

```json
{
  "id": "app-saleor-stripe",
  "version": "1.0.0",
  "name": "Saleor Stripe Integration",
  "permissions": ["HANDLE_PAYMENTS", "MANAGE_ORDERS"],
  "appUrl": "https://stripe-app.example.com",
  "tokenTargetUrl": "https://stripe-app.example.com/api/register",
  "extensions": [
    {
      "name": "Stripe Payment Gateway",
      "type": "PAYMENT_GATEWAY",
      "target": "CHECKOUT",
      "file": "https://stripe-app.example.com/extension.js"
    },
    {
      "name": "Order Actions",
      "type": "PRODUCT_MOVEMENT",
      "target": "ORDER_DETAILS",
      "file": "https://stripe-app.example.com/order-actions.js"
    }
  ],
  "webhooks": [
    {
      "name": "Order Created",
      "asyncEvents": ["ORDER_CREATED"],
      "query": "subscription { event { ... on OrderCreated { order { id } } } }",
      "targetUrl": "https://stripe-app.example.com/webhooks/order"
    }
  ],
  "settingsUrl": "https://stripe-app.example.com/settings",
  "redirectUrl": "https://stripe-app.example.com/finish",
  "author": "Your Company"
}
```

### 部署类型对比

| 类型 | 说明 | Dashboard可见 |
|------|------|-------------|
| **Dashboard App** | 在Dashboard侧边栏显示 | ✅ |
| **Channel App** | 绑定到特定Channel | ✅ (Channel级别) |
| **Private App** | API Token访问 | ❌ (API-only) |

### App安装流程

```
1. App发起OAuth 2.0 Authorization Request
2. Saleor验证后显示授权确认页
3. 用户点击"Approve" → 重定向到App的tokenTargetUrl
4. App收到临时auth code → 交换为正式token
5. App通过token访问API
6. Dashboard App显示在侧边栏
```

---

## 5. App SDK组件

### 安装

```bash
npm install @saleor/app-sdk
```

### AppBridge (Dashboard↔App通信)

```typescript
import { createAppBridge, AppBridge } from "@saleor/app-sdk/app-bridge";

// Dashboard中获取App Token
const appBridge: AppBridge = createAppBridge({
  saleorApiUrl: window.__SALEOR_API_URL__,
  token: window.__SALEOR_APP_TOKEN__,
});

// 通知Dashboard打开对话框
appBridge.dispatch({
  type: "OPEN_RAW_DIALOG",
  payload: { title: "Configure Stripe", children: <ConfigForm /> },
});

// 监听Dashboard事件
appBridge.subscribe("cfg", (event) => {
  console.log("Config changed:", event.payload);
});

// 订阅Notification
appBridge.subscribe("notification", (event) => {
  // 显示toast
});
```

### API Handler

```typescript
import { createClient } from "@saleor/app-sdk/api-client";

// 创建GraphQL客户端
const client = createClient({
  saleorApiUrl: "https://example.saleor.cloud/graphql/",
  token: "app-token-xxx",
});

// 执行GraphQL查询
const { data } = await client.query(`
  query GetProduct($id: ID!) {
    product(id: $id) {
      id
      name
      pricing {
        priceRange {
          start { gross { amount currency } }
        }
      }
    }
  }
`, { id: "UHJvZHVjdDoxMA==" });
```

### Settings Manager

```typescript
import { createSettingsManager } from "@saleor/app-sdk/settings-manager";

const settingsManager = createSettingsManager(authData);

// 读取设置
const stripePubKey = await settingsManager.get("stripePublicKey");

// 写入设置
await settingsManager.set("stripePublicKey", "pk_live_xxx");

// 删除设置
await settingsManager.delete("stripePublicKey");

// 批量操作
await settingsManager.setMultiple({
  "stripePubKey": "pk_live_xxx",
  "stripeMode": "live",
  "webhookSecret": "whsec_xxx",
});
```

### APL (Auth Persistence Layer)

```typescript
import { createAPL } from "@saleor/app-sdk/APL";

// 快速开始(开发模式)
const apl = createAPL({
  name: "dev-env",
});

// 生产环境用数据库APL
const apl = createAPL({
  type: "db",
  // 或 cloud, vercel, hersoku 等
});

// 获取已注册App列表
const apps = await apl.getAll();

// 获取特定App
const app = await apl.get({ domain: "example.saleor.cloud", appId: "app-id" });

// 注册新App
await apl.register({
  saleorApiUrl: "https://example.saleor.cloud/graphql/",
  token: "app-token-xxx",
  domain: "example.saleor.cloud",
  appId: "app-id",
  businessUser: { email: "dev@example.com", id: "user-id" },
});
```

---

## 6. Webhook系统

### 24+ Async Events

```python
# Product events
"PRODUCT_CREATED"
"PRODUCT_UPDATED"
"PRODUCT_DELETED"
"PRODUCT_METADATA_UPDATED"

# Variant events
"VARIANT_CREATED"
"VARIANT_UPDATED"
"VARIANT_DELETED"
"VARIANT_METADATA_UPDATED"

# Order events
"ORDER_CREATED"
"ORDER_CONFIRMED"
"ORDER_FULLY_PAID"
"ORDER_FULFILLED"
"ORDER_CANCELLED"
"ORDER_REFUNDED"
"ORDER_METADATA_UPDATED"

# Checkout events
"CHECKOUT_CREATED"
"CHECKOUT_UPDATED"
"CHECKOUT_FULLY_PAID"

# Customer events
"CUSTOMER_CREATED"
"CUSTOMER_UPDATED"
"CUSTOMER_DELETED"

# Fulfillment events
"FULFILLMENT_CREATED"
"FULFILLMENT_TRACKING_NUMBER_UPDATED"

# Account events
"ACCOUNT_CONFIRMATION_REQUESTED"
"ACCOUNT_PASSWORD_RESET_REQUESTED"
```

### Sync vs Async Webhooks

| 类型 | 行为 | 响应时间要求 | 使用场景 |
|------|------|-------------|---------|
| **Sync** | 阻塞请求，等待响应 | 必须快速返回 | 支付验证，价格计算，库存检查 |
| **Async** | 异步队列，不阻塞 | 无限制 | 发送邮件，更新外部系统，触发CI流程 |

### HMAC-SHA256 Webhook签名

```python
import hmac
import hashlib

WEBHOOK_SECRET = "whsec_xxx"

def verify_webhook_signature(request_body: bytes, signature: str) -> bool:
    """验证Webhook payload签名"""
    expected_signature = hmac.new(
        key=WEBHOOK_SECRET.encode(),
        msg=request_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(f"sha256={expected_signature}", signature)

# Django View处理Webhook
@csrf_exempt
def stripe_webhook(request):
    body = request.body
    signature = request.headers.get("Saleor-Topic-Signature", "")

    if not verify_webhook_signature(body, signature):
        return JsonResponse({"error": "Invalid signature"}, status=401)

    event = json.loads(body)
    event_type = event.get("type")

    if event_type == "ORDER_FULLY_PAID":
        # 发货处理
        pass

    return JsonResponse({"status": "ok"})
```

### Webhook EventMapping (Payload生成)

```python
from saleor.webhook.event_types import WebhookEventAsyncType
from saleor.webhook.payloads import (
    generate_order_payload,
    generate_product_payload,
    generate_checkout_payload,
)

# 选择性字段
def generate_custom_order_payload(order: "Order", kwargs: dict) -> dict:
    return {
        "id": order.id,
        "status": order.status,
        "total": {
            "gross": order.total_gross_amount,
            "currency": order.currency,
        },
        "user_email": order.user_email,
        "lines": [
            {
                "sku": line.variant.sku,
                "quantity": line.quantity,
                "product_name": line.variant.display_product(),
            }
            for line in order.lines.all()
        ],
    }
```

---

## 7. 数据模型

### Product变体层级

```
Product
├── Category (多对多)
├── ProductMedia (多对多 images)
├── ProductType (定义了属性组)
├── Attribute (可分配到ProductType)
├── ProductVariant
│   ├── AttributeValue (变体级别属性)
│   ├── Warehouse → Stock
│   └── ProductChannelListing (per-channel定价)
└── ProductChannelListing (per-channel可见性/SEO)
```

### Channel模型 (多渠道商务核心)

```python
# Channel = 销售平台/店铺/市场
Channel.objects.create(
    slug="us-market",
    name="US Market",
    default_country="US",
    currency_code="USD",
)

# per-channel定价
ProductChannelListing.objects.create(
    product=product,
    channel=us_channel,
    visible_in_listings=True,
    is_published=True,
    publication_date="2024-01-01",
    pricing=ProductPricingInfo(
        price_range={
            "min": Money(29.99, "USD"),
            "max": Money(49.99, "USD"),
        }
    ),
)

# per-channel库存
Stock.objects.create(
    warehouse=warehouse_us,
    product_variant=variant,
    quantity=100,
    quantity_allocated=10,
)
```

### Order状态机

```
DRAFT → UNCONFIRMED → PARTIALLY_RESERVED → RESERVED →
  → CONFIRMED → PARTIALLY_FULFILLED → FULFILLED
                      ↓
               CANCELLED (任意阶段可取消)

REFUNDED (FULFILLED之后)
CLAIMED (已完成的订单可创建Claim)
```

### Checkout流程

```
Checkout
├── Lines (购物车商品)
├── ShippingAddress
├── BillingAddress
├── ShippingMethod
├── Payment (→ Transaction → Action)
│
├── → COMPLETE → Order (自动创建)
│
└── → ABANDONED (超时未结算)
```

---

## 8. 认证与权限

### App OAuth 2.0 Flow

```
┌────────────┐                    ┌─────────────┐
│   App     │                    │ Saleor     │
└─────┬──────┘                    └──────┬──────┘
      │                                  │
      │ 1. 发起OAuth请求                 │
      │ GET /dashboard/authorize/      │
      │ ?redirectUrl=xxx&useEmailScope=true
      │ ──────────────────────────────▶│
      │                                  │
      │ 2. 用户授权页面                  │
      │ ◀────────────────────────────────│
      │                                  │
      │ 3. 用户点击Approve               │
      │ ──────────────────────────────▶│
      │                                  │
      │ 4. 重定向到App的tokenTargetUrl   │
      │ ?code=auth_code_xxx             │
      │ ◀────────────────────────────────│
      │                                  │
      │ 5. 用code换token                │
      │ POST /dashboard/connect/        │
      │ { code, grant_type }           │
      │ ──────────────────────────────▶│
      │                                  │
      │ 6. 返回token                     │
      │ { token, saleor_api_url }       │
      │ ◀────────────────────────────────│
```

### 权限矩阵

| Permission | 读取 | 写入 | 删除 | 范围 |
|------------|------|------|------|------|
| MANAGE_PRODUCTS | ✅ | ✅ | ✅ | 全部产品 |
| MANAGE_ORDERS | ✅ | ✅ | ✅ | 全部订单 |
| MANAGE_USERS | ✅ | ✅ | ✅ | 全部客户 |
| MANAGE_SETTINGS | ✅ | ✅ | ✅ | 全局设置 |
| HANDLE_PAYMENTS | ✅ | ✅ | ❌ | 支付相关 |
| MANAGE_SHIPPING | ✅ | ✅ | ✅ | 配送相关 |
| MANAGE_GIFT_CARD | ✅ | ✅ | ✅ | 礼品卡 |
| MANAGE_PLUGINS | ✅ | ✅ | ✅ | App/Plugin |

### JWT Token结构

```python
# JWT Payload
{
  "iss": "saleor",
  "exp": 1735689600,
  "iat": 1735603200,
  "type": "TOKEN",
  "permissions": ["MANAGE_ORDERS", "MANAGE_PRODUCTS"],
  "user_id": "VXNlcjox",
  "auth_date": "2025-01-01",
}
```

---

## 9. 支付系统

### Transaction模型 (Saleor 4.0+)

```python
# Transaction替换传统Payment
Transaction.objects.create(
    order=order,
    action_type=TransactionActionType.CHARGE,
    status=TransactionStatus.SUCCESS,
    amount=Money(99.99, "USD"),
    currency="USD",
    gateway_response={
        "pspReference": "stripe_pi_xxx",
        "paymentMethod": "card",
    },
    external_url="https://dashboard.stripe.com/payments/pi_xxx",
    metadata={"stripe_payment_intent": "pi_xxx"},
)
```

### 支付网关集成

```python
# saleor/payment/gateways/stripe/ 接口
class StripeGateway:
    def process_payment(
        payment_information: PaymentData,
        channel_slug: str,
    ) -> GatewayResponse:
        """处理支付"""
        # 调用Stripe API
        pass

    def refund_payment(
        payment_information: PaymentData,
        amount: Decimal,
    ) -> GatewayResponse:
        """退款"""
        pass

    def confirm_payment(
        payment_information: PaymentData,
    ) -> GatewayResponse:
        """确认3DS等"""
        pass

# 支持网关: Stripe, Adyen, Braintree, Razorpay, Mollie, Authorize.net
```

### Action自动化

```python
# 配置自动触发Actions
OrderSettings.objects.create(
    automatic_fulfillment_no_shipping=False,
    mark_as_paid_strategy=MarkAsPaidStrategy.TRANSACTION_FLOW,
    delete_expired_order_after=timedelta(days=90),
    expire_orders_after=timedelta(hours=1),
)
)
```

---

## 10. Saleor Cloud vs 自托管

| 维度 | Saleor Cloud | 自托管 |
|------|------------|--------|
| **基础设施** | 托管，无需运维 | 需Django部署 |
| **扩展部署** | 1-click安装App | 需配置webhook |
| **定价** | 按MRR收费 | 免费开源 |
| **数据库** | 托管(不可见) | PostgreSQL自控 |
| **版本升级** | 自动 | 手动执行migrate |
| **监控** | 内置 | 自建 |
| **扩展性** | 受限于Cloud限制 | 无限扩展 |
| **API限制** | 有速率限制 | 无限制 |
| **适用场景** | 快速启动/小团队 | 定制化/大规模 |

---

## 11. CLI工具

### @saleor/cli

```bash
# 安装
npm install -g @saleor/cli

# 登录
saleor login
saleor logout
saleor whoami

# 环境管理
saleor env list
saleor env create production --from-template saleor-4-0
saleor env switch production
saleor env upgrade --latest

# Trigger Webhook
saleor webhook trigger \
  --event PRODUCT_CREATED \
  --id UHJvZHVjdDox \
  --env production

# App scaffolding
saleor app create "My Stripe App"
```

### Django Management Commands

```bash
# 数据库迁移
python manage.py migrate

# 超级用户
python manage.py createsuperuser

# 导入数据
python manage.py import_products products.csv

# 导出数据
python manage.py export_orders orders.json

# Webhook测试
python manage.py listen_events \
  --app app-id \
  --events ORDER_CREATED,PRODUCT_UPDATED

# 权限检查
python manage.py check_permissions \
  --user email@example.com \
  --permissions MANAGE_ORDERS

# 清理过期数据
python manage.py clearsessions
python manage.py deleteExpiredOrders
```

---

## 12. Saleor vs Medusa 对比分析

### 技术栈选择决策矩阵

| 场景 | 推荐框架 | 原因 |
|------|---------|------|
| Python技术栈 | **Saleor** | 语言一致，减少上下文切换 |
| TypeScript技术栈 | **Medusa** | 语言一致，Next.js生态 |
| GraphQL-first需求 | **Saleor** | 原生GraphQL，APIv2优化 |
| REST API需求 | **Medusa** | REST-native，OpenAPI |
| 强多渠道商务 | **Saleor** | Channel模型first-class |
| 多store/多租户 | **Medusa** | 多store实例隔离 |
| Dashboard生态 | **Saleor** | App市场，原生集成 |
| Plugin扩展 | **Medusa** | Plugin系统灵活 |
| 小型项目 | **Medusa** | 更轻量，Quickstart更快 |
| 企业级定制 | **Saleor** | Django生态，Django Admin |

### 天龙引擎技术栈互补策略

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 电商框架双引擎架构                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Python团队 ─────────────────────▶ Saleor                   │
│  ├── Django/Python开发者主导                             │
│  ├── 强GraphQL需求                                        │
│  ├── 多渠道商务（Marketplace）                            │
│  └── 企业级安全（OAuth 2.0细粒度权限）                    │
│                                                             │
│  TypeScript团队 ──────────────────▶ Medusa                 │
│  ├── Next.js/React前端主导                               │
│  ├── REST API为主                                        │
│  ├── Plugin灵活扩展                                       │
│  └── 快速MVP（Quickstart 5分钟）                         │
│                                                             │
│  Java/Kotlin团队 ────────────────▶ Spring Boot          │
│  └── java-ecommerce-patterns (V8.89)                      │
│                                                             │
│  PHP团队 ───────────────────────▶ CRMEB                   │
│  └── crmeb-ecommerce-patterns (V8.99)                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 关键差异速查

| 需求 | Saleor方案 | Medusa方案 |
|------|-----------|-----------|
| 新增API端点 | CustomResolver + App Extension | Custom Route + API Router |
| 支付集成 | Transaction + Gateway | Payment Provider Plugin |
| 发送邮件 | App Webhook订阅 | Event Plugin |
| 文件上传 | FileService + CDN | FileService Plugin |
| 实时数据 | GraphQL Subscription | Medusa Live RTK Query |
| 权限控制 | OAuth Scope + Permissions | Auth Middleware |
| 多语言 | Translation models | Medusa Store Config |
| 搜索引擎 | OpenSearch/Django | Medusa Search Plugin |

---

## 13. 技术深潜

### Django App注册

```python
# saleor/__init__.py
INSTALLED_APPS = [
    # Django内置
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 第三方
    "django_prices",
    "django_prices_vatlayer",
    "django_measurement",
    "django_filters",
    "webpack_loader",
    "versatileimagefield",

    # Saleor核心
    "saleor.account",
    "saleor.attribute",
    "saleor.checkout",
    "saleor.discount",
    "saleor.giftcard",
    "saleor.menu",
    "saleor.order",
    "saleor.page",
    "saleor.payment",
    "saleor.product",
    "saleor.seo",
    "saleor.shipping",
    "saleor.site",
    "saleor.tax",
    "saleor.warehouse",
    "saleor.webhook",
    "saleor.channel",
]
```

### Graphene Schema扩展

```python
# Custom mutation
import graphene
from saleor.graphql.schema import GraphQLSchema

class StripePayment(graphene.Mutation):
    class Arguments:
        order_id = graphene.ID(required=True)
        payment_method_id = graphene.String(required=True)

    payment_url = graphene.String()
    status = graphene.String()

    @classmethod
    def mutate(cls, root, info, order_id, payment_method_id):
        # Stripe处理逻辑
        return cls(payment_url="https://...", status="pending")

# 注册到schema
class Mutations(graphene.ObjectType):
    stripe_payment = StripePayment.Field()

# 替换默认schema
GraphQLSchema.query = Query
GraphQLSchema.mutation = Mutations
```

### Event Subscriber模式

```python
from saleor.event_bus import event_types
from saleor.event_bus.subscriptions import EventSubscriber

class SendWelcomeEmailSubscriber(EventSubscriber):
    event_type = event_types.EVENT_ORDER_CREATED
    queue_name = "emails"

    def handle(self, event):
        order_data = event.payload
        user_email = order_data.get("user_email")

        if user_email:
            send_welcome_email.delay(user_email, order_data)
```

---

## 14. 天龙九部集成路径

### 文件路径

```
~/.claude/skills/saleor-ecommerce-patterns/
├── SKILL.md                          # 本文件
├── manifests/                         # App manifest示例
│   ├── stripe-payment.json
│   ├── analytics-app.json
│   └── custom-shipping.json
├── sdk-examples/                     # App SDK示例
│   ├── app-bridge-example.ts
│   ├── api-client-example.ts
│   └── settings-manager-example.ts
├── webhooks/                         # Webhook处理示例
│   ├── stripe_webhook.py
│   ├── inventory_sync.py
│   └── email_notifications.py
├── queries/                          # GraphQL查询示例
│   ├── products.graphql
│   ├── orders.graphql
│   └── checkout.graphql
└── scripts/                          # CLI脚本
    ├── create-app.sh
    ├── trigger-webhook.sh
    └── product-import.sh
```

### 天龙九部协作矩阵

| 天龙岗位 | Saleor集成点 | 协作方式 |
|---------|------------|---------|
| **00分析师** | 架构选型 | Saleor vs Medusa技术栈对比分析 |
| **01调研师** | 技术摸底 | Django/GraphQL源码考古，App SDK调用链 |
| **02架构师** | 系统设计 | Saleor GraphQL API架构，Channel多渠道模型 |
| **03构建师** | 代码开发 | Django App开发，manifest.json配置，App SDK集成 |
| **04验证师** | 测试验证 | App SDK测试，Django单元测试，Webhook集成测试 |
| **05安全师** | 安全审查 | OAuth 2.0安全，HMAC-SHA256签名验证，权限审查 |
| **06审查师** | 代码审查 | Django最佳实践，GraphQL N+1查询优化 |
| **07记录师** | 文档沉淀 | Saleor SKILL.md更新，App开发模式沉淀 |
| **08发布师** | 部署发布 | Saleor Cloud vs自托管决策，Docker部署 |

---

## 15. 研究空白与PoC推荐

### 需进一步研究的空白

| 空白 | 研究方向 | 优先级 |
|------|---------|--------|
| **Saleor App市场** | App store生态规模，变现模式 | 🟡 中 |
| **Saleor x AI** | LLM驱动的产品推荐，智能客服 | 🔴 高 |
| **Checkout定制化** | APIv2 Checkout mutations深度测试 | 🟡 中 |
| **Subscription API** | 订阅电商模式实现路径 | 🟡 中 |
| **多仓库库存** | Stock→Warehouse→ShippingZone调度逻辑 | 🟢 低 |
| **Tax计算** | Avatax/Vertex集成，多州税务 | 🟢 低 |
| **迁移路径** | Shopify/Magento迁移到Saleor工具 | 🟢 低 |

### 推荐PoC

```bash
# PoC 1: Saleor App SDK快速开发
# 目标：验证App SDK三组件(AppBridge/API/Settings)集成
# 工期: 2天
# 依赖: saleor-ecommerce-patterns

# PoC 2: Saleor Webhook↔Stripe集成
# 目标: 实现ORDER_FULLY_PAID → 自动触发Stripe退款
# 工期: 3天
# 依赖: saleor-ecommerce-patterns + stripe-sdk

# PoC 3: Saleor GraphQL Subscription实时通知
# 目标: 验证Subscription API推送订单状态到前端
# 工期: 2天
# 依赖: saleor-ecommerce-patterns + websocket
```

---

## 16. 关键资源

### 官方仓库

| 资源 | URL |
|------|-----|
| **Saleor Core** | https://github.com/saleor/saleor |
| **Dashboard** | https://github.com/saleor/saleor-dashboard |
| **Storefront** | https://github.com/saleor/saleor-storefront |
| **App SDK** | https://github.com/saleor/saleor-app-sdk |
| **CLI** | https://github.com/saleor/cli |
| **App Examples** | https://github.com/saleor/app-sdk/tree/main/apps |

### 文档

| 资源 | URL |
|------|-----|
| **Docs** | https://docs.saleor.io/ |
| **API Reference** | https://docs.saleor.io/api-reference |
| **App SDK Docs** | https://github.com/saleor/saleor-app-sdk |
| **Blog** | https://saleor.io/blog/ |

### 社区

| 资源 | URL |
|------|-----|
| **Discord** | https://discord.gg/saleor |
| **StackOverflow** | saleor-platform tag |
| **GitHub Discussions** | saleor/saleor/discussions |
| **Saleor Cloud** | https://cloud.saleor.io/ |

### 视频

| 资源 | 平台 |
|------|------|
| **Saleor Conf 2024** | YouTube (keynotes + deep dives) |
| **App SDK Walkthrough** | YouTube |
| **GraphQL Deep Dive** | Saleor Blog |

### 版本

| 版本 | 发布时间 | 核心特性 |
|------|---------|---------|
| **Saleor 4.0** | 2022 | APIv2, Transaction, Webhook Subscriptions |
| **Saleor 4.1** | 2023 | New Dashboard, App SDK 1.0 |
| **Saleor 4.2** | 2023 | Product Media, Promotions |
| **Saleor 4.3** | 2024 | App Marketplace, Order Digital Content |
| **Saleor 4.4** | 2024 | Channel Promotion, Checkout Extensions |
