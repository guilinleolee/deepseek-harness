---
license: UNKNOWN
triggers: ["medusa ecommerce patterns", "Medusa.js 电商框架模式 SKILL.md"]
---
# Medusa.js 电商框架模式 SKILL.md

## L0: 一句话描述 (≤15字)
Medusa.js电商框架工程模式

## L1: 使用场景 (50-100字)
当需要进行TypeScript/Node.js技术栈的电商系统调研、代码审查、架构设计或插件开发时，调用本Skill。覆盖Medusa.js插件开发、Module Service模式、Workflows引擎、DML数据建模、Event Subscriber事件驱动等核心工程模式。

## L2: 详细文档

---

## 1. 框架速查

### 核心技术栈对应关系

| 电商组件 | Medusa.js | Spring Boot (java-ecommerce-patterns) |
|---------|-----------|-------------------------------------|
| 框架定位 | Headless插件化电商中间件 | 全功能B2C/B2B电商平台 |
| 语言生态 | TypeScript/Node.js | Java/Kotlin |
| 许可证 | MIT | Apache 2.0 |
| 订单模块 | `order` Module Service | `mall_order` + 状态机 |
| 支付模块 | Payment Provider插件接口 | `mall_payment` + 微信/支付宝SDK |
| 商品模块 | `product` + `pricing` + `inventory` | `mall_goods` + SKU表 |
| 促销模块 | `promotion` Module Service | `mallCoupon` + 活动规则 |
| 用户模块 | `auth` + `user` + `customer` | `sys_user` + SSO集成 |
| 物流模块 | Fulfillment Provider插件接口 | `mall_shipping` + 快递100集成 |
| 工作流 | Workflows Engine原生 | Camunda/Activiti |
| 数据建模 | DML `model.define()` | JPA Entity + Flyway |
| 扩展方式 | 插件Plugin系统 | Spring Boot Starter |

### Medusa.js核心架构

```
medusa/packages/
├── core/
│   ├── core_flows/          # 核心业务流程（order/cart/...)
│   ├── link/                # Module Link跨模块关联
│   ├── types/               # 共享DTO类型
│   └── utils/               # DML工具、全局辅助
├── modules/
│   ├── cart/               # 购物车
│   ├── product/             # 商品+价格+库存
│   ├── order/               # 订单+处理
│   ├── payment/             # 支付
│   ├── fulfillment/          # 物流履约
│   ├── pricing/             # 动态定价
│   ├── promotion/           # 促销优惠
│   ├── inventory/           # 库存管理
│   ├── auth/               # 认证授权
│   ├── user/                # 用户管理
│   ├── customer/             # 客户管理
│   ├── store/               # 多店铺
│   ├── region/              # 地区/税费
│   ├── currency/            # 多货币
│   ├── sales-channel/       # 销售渠道
│   ├── notification/         # 通知中心
│   └── ...(30+独立模块)
├── workflows-sdk/           # Workflows引擎
├── api/                     # REST API层
└── plugins/                 # 官方插件
```

---

## 2. Module Service模式

### 2.1 创建自定义Module

```typescript
// src/modules/hello-world/service.ts
import { MedusaService } from "@medusajs/framework/utils"
import { Module } from "@medusajs/framework/sdk"
import { MyCustomDTO, MyCustomInput } from "./types"

class HelloWorldModuleService extends MedusaService({
  MyCustom: MyCustomDTO,
  MyRelated: RelatedDTO,
}) {
  async createCustom(data: MyCustomInput): Promise<MyCustomDTO> {
    return await this.create_(data)
  }

  async findCustoms(filter?: any): Promise<MyCustomDTO[]> {
    const [result] = await this.listAndCount_(filter || {})
    return result
  }

  async updateCustom(id: string, data: Partial<MyCustomInput>): Promise<MyCustomDTO> {
    return await this.update_(id, data)
  }

  async deleteCustom(id: string): Promise<void> {
    return await this.atomicPhase_(
      async (manager) => {
        await this.delete_(id, { manager })
      }
    )
  }
}

export default Module("HELLO_WORLD", {
  service: HelloWorldModuleService,
})
```

### 2.2 注册Module

```typescript
// medusa-config.ts
module.exports = {
  modules: {
    HELLO_WORLD: {
      resolve: "./src/modules/hello-world",
    },
  },
}
```

### 2.3 Module间调用

```typescript
// 在Step或Service中注入其他Module
const cartModuleService = container.resolve("cart")
const productService = container.resolve("product")
const inventoryService = container.resolve("inventory")

// 跨Module查询
const products = await productService.listProducts({ tags: ["featured"] })
const inventoryLevels = await inventoryService.listInventoryLevels({
  inventory_item_id: product.variants[0].id,
})
```

---

## 3. Workflows引擎

### 3.1 定义Step

```typescript
// src/workflows/hello-world/steps.ts
import {
  createStep,
  StepResponse,
} from "@medusajs/framework/workflows-sdk"

export const createProductStep = createStep(
  "create-product-step",
  async (input: { title: string; price: number }, { container }) => {
    const productService = container.resolve("product")

    const product = await productService.createProducts({
      title: input.title,
      variants: [{ title: "Default", prices: [{ amount: input.price, currency_code: "usd" }] }],
    })

    return new StepResponse(product, { productId: product.id })
  },
  async (input: { productId: string }, { container }) => {
    const productService = container.resolve("product")
    await productService.deleteProducts(input.productId)
  }
)

export const updateInventoryStep = createStep(
  "update-inventory-step",
  async (input: { variantId: string; quantity: number }, { container }) => {
    const inventoryService = container.resolve("inventory")
    await inventoryService.adjustInventory(input.variantId, input.quantity)
    return new StepResponse({ variantId: input.variantId, quantity: input.quantity })
  }
)
```

### 3.2 定义Workflow

```typescript
// src/workflows/hello-world/index.ts
import {
  createWorkflow,
  WorkflowResponse,
} from "@medusajs/framework/workflows-sdk"
import { createProductStep, updateInventoryStep } from "./steps"

export const publishProductWorkflow = createWorkflow(
  "publish-product",
  (input: { title: string; price: number; quantity: number }) => {
    const product = createProductStep({ title: input.title, price: input.price })

    const inventory = updateInventoryStep({
      variantId: product.variants[0].id,
      quantity: input.quantity,
    })

    return new WorkflowResponse({ product, inventory })
  }
)
```

### 3.3 执行Workflow

```typescript
// 在Route中执行
import { publishProductWorkflow } from "../../workflows/hello-world"
import { MedusaContext, ModulesSDKContext } from "@medusajs/framework/sdk"

export const POST = async (req, res) => {
  const result = await publishProductWorkflow(req.scope).run({
    input: {
      title: "Digital Product",
      price: 999,
      quantity: 100,
    },
  })

  res.json({ result })
}
```

### 3.4 Workflow类型定义

```typescript
// Workflow输入输出类型
export type ProductWorkflowInput = {
  title: string
  price: number
  quantity: number
}

export type ProductWorkflowOutput = {
  product: any
  inventory: any
}

// 使用泛型指定类型
const myWorkflow = createWorkflow<
  WorkflowInput<ProductWorkflowInput>,
  WorkflowResponse<ProductWorkflowOutput>
>("my-workflow", (input) => { ... })
```

---

## 4. Data Model Language (DML)

### 4.1 定义模型

```typescript
// src/modules/hello-world/models/my-custom.ts
import { model } from "@medusajs/framework/utils"

export const DigitalProduct = model.define("digital_product", {
  id: model.id().primaryKey(),
  title: model.text(),
  description: model.text().nullable(),
  price: model.money(),
  cost: model.money().nullable(),
  metadata: model.json().optional(),
  status: model.enum(["draft", "published", "archived"]).default("draft"),

  // 一对多关联
  medias: model.hasMany(() => DigitalProductMedia, {
    mappedBy: "digitalProduct",
  }),

  // 多对多关联
  tags: model.manyToMany({
    entry: () => Tag,
    inverse: () => DigitalProductTag,
    pivotTable: "digital_product_tags",
  }),

  // 级联删除
}).cascades({ delete: ["medias"] })

export const DigitalProductMedia = model.define("digital_product_media", {
  id: model.id().primaryKey(),
  digital_product_id: model.text(),
  digitalProduct: model.belongsTo(() => DigitalProduct, {
    mappedBy: "medias",
  }),
  url: model.text(),
  mime_type: model.text(),
}). indexes([{ on: "digital_product_id", unique: false }])

export const Tag = model.define("tag", {
  id: model.id().primaryKey(),
  value: model.text().unique(),
})
```

### 4.2 模型关系速查

| 关系 | DML语法 |
|------|---------|
| 主键 | `model.id().primaryKey()` |
| 文本 | `model.text()`, `model.text().nullable()` |
| 数字 | `model.bigInteger()`, `model.float()`, `model.integer()` |
| 金额 | `model.money()` → `{ currency_code, amount }` |
| 枚举 | `model.enum(["A","B"]).default("A")` |
| JSON | `model.json()`, `model.json().optional()` |
| 时间戳 | `model.dateTime()` |
| 布尔 | `model.boolean().default(true)` |
| 一对多 | `model.hasMany(() => Child, { mappedBy: "parent" })` |
| 多对一 | `model.belongsTo(() => Parent, { mappedBy: "children" })` |
| 多对多 | `model.manyToMany({ entry: () => Tag, pivotTable: "pivot_table" })` |
| 级联删除 | `.cascades({ delete: ["children"] })` |

---

## 5. Event Subscriber事件驱动

### 5.1 定义Subscriber

```typescript
// src/subscribers/hello-world.ts
export default class HelloWorldSubscriber {
  handle = async (data: any, { container }: { container: any }) => {
    const logger = container.resolve("logger")
    const notificationService = container.resolve("notification")
    const eventBusService = container.resolve("eventBus")

    logger.info(`Order placed: ${data.id}`)

    await notificationService.send({
      to: data.customer_email,
      template: "order-confirmation",
      data: { order: data },
    })
  }

  // 单事件
  event = "order.placed"

  // 或多事件数组
  // events = ["order.placed", "order.updated"]
}
```

### 5.2 事件类型速查

| 事件 | 触发时机 | 常见用途 |
|------|---------|---------|
| `order.placed` | 订单创建 | 发货通知、库存扣减 |
| `order.updated` | 订单更新 | 状态同步 |
| `order.canceled` | 订单取消 | 库存回滚、支付退款 |
| `order.completed` | 订单完成 | 积分发放、评价提醒 |
| `cart.created` | 购物车创建 | 购物车提醒 |
| `cart.updated` | 购物车更新 | 促销计算 |
| `product.created` | 商品创建 | 搜索引擎索引 |
| `customer.created` | 客户创建 | CRM同步、欢迎邮件 |
| `payment.captured` | 支付成功 | 触发履约流程 |
| `payment.refunded` | 退款完成 | 财务对账 |

---

## 6. Scheduled Jobs定时任务

### 6.1 定义Job

```typescript
// src/jobs/sync-inventory.ts
export default async function syncInventoryJob(container: any) {
  const logger = container.resolve("logger")
  const inventoryService = container.resolve("inventory")
  const productService = container.resolve("product")

  logger.info("Starting inventory sync...")

  const products = await productService.listProducts({
    status: ["published"],
  })

  for (const product of products) {
    for (const variant of product.variants) {
      const externalStock = await fetchExternalInventory(variant.sku)
      await inventoryService.updateInventoryLevels(variant.id, {
        stocked_quantity: externalStock,
      })
    }
  }

  logger.info(`Synced ${products.length} products`)
}

// Cron表达式: "0 0 * * *" = 每天午夜
export const config = {
  name: "sync-inventory-daily",
  schedule: "0 0 * * *",
}
```

### 6.2 Cron表达式速查

| Cron | 含义 |
|------|------|
| `0 * * * *` | 每小时 |
| `0 0 * * *` | 每天午夜 |
| `0 0 * * 0` | 每周日午夜 |
| `0 0 1 * *` | 每月1号午夜 |
| `*/15 * * * *` | 每15分钟 |
| `0 9-17 * * 1-5` | 工作日9点到17点每小时 |

---

## 7. 自定义API路由

### 7.1 创建路由

```typescript
// src/api/store/hello-world/route.ts
import { MedusaStore } from "@medusajs/framework/http"
import { Request, Response } from "express"

@MedusaStore()
export class HelloWorldStoreController {
  // Store API: GET /store/hello-world
  @Get("")
  async list(
    @Req() req: Request,
    @Res() res: Response
  ) {
    const productService = req.scope.resolve("product")

    const [products, count] = await productService.listAndCountProducts({
      limit: 10,
    })

    res.json({ products, count })
  }
}

// src/api/admin/hello-world/route.ts
import { MedusaAdmin } from "@medusajs/framework/http"

@MedusaAdmin()
export class HelloWorldAdminController {
  @Get("/stats")
  async getStats(@Req() req: Request, @Res() res: Response) {
    const orderService = req.scope.resolve("order")
    const productService = req.scope.resolve("product")

    const [orders, orderCount] = await orderService.listAndCountOrders()
    const [products, productCount] = await productService.listAndCountProducts()

    res.json({
      total_orders: orderCount,
      total_products: productCount,
      total_revenue: orders.reduce((sum, o) => sum + o.total, 0),
    })
  }
}
```

### 7.2 路由前缀速查

| 路由 | 路径前缀 | 权限 |
|------|---------|------|
| Store API | `/store/` | 公开/客户认证 |
| Admin API | `/admin/` | Admin认证 |
| 自定义 | `/` (根路径) | 需手动权限控制 |

---

## 8. Loaders启动初始化

```typescript
// src/loaders/seeder.ts
import { Loader } from "@medusajs/medusa"

export default async function seedData(container: any): Promise<void> {
  const logger = container.resolve("logger")
  const productService = container.resolve("product")
  const userService = container.resolve("user")

  // 检查是否已有数据
  const [existing] = await productService.listAndCountProducts({ limit: 1 })
  if (existing.length > 0) {
    logger.info("Products already seeded, skipping...")
    return
  }

  // 执行种子数据
  await productService.createProducts([
    { title: "Demo Product", status: "published", ... },
  ])

  logger.info("Seed data loaded successfully")
}

export const config: Loader = {
  resolve: "./src/loaders/seeder",
  options: { async: true },
}
```

---

## 9. API认证与权限

### 9.1 获取当前用户

```typescript
// 在Route中获取认证信息
@Get("/me")
async getMe(@Req() req: Request, @Res() res: Response) {
  // req.auth 包含认证信息
  const actorId = req.auth.actor_id        // 用户ID
  const authIdentityId = req.auth.auth_identity_id  // 认证身份ID
  const actorType = req.auth.actor_type    // "user" | "customer" | "integration"

  const customerService = req.scope.resolve("customer")
  const customer = await customerService.retrieveCustomer(authIdentityId)

  res.json({ customer })
}
```

### 9.2 权限控制

```typescript
// 自定义中间件或Auth Subscriber
export default class AuthSubscriber {
  handle = async (data: any, { container }: { container: any }) => {
    const logger = container.resolve("logger")
    const path = data.Path || ""

    // 仅Admin路由需要认证
    if (path.startsWith("/admin")) {
      if (!data.auth) {
        throw new MedusaError(MedusaError.Types.UNAUTHORIZED, "Admin access required")
      }
      if (data.auth.actor_type !== "user") {
        throw new MedusaError(MedusaError.Types.FORBIDDEN, "Admin users only")
      }
    }
  }

  event = "httprouter.authorize"
}
```

---

## 10. 文件存储模块

```typescript
// src/modules/my-storage/service.ts
import { Module } from "@medusajs/framework/sdk"

class MyStorageModuleService {
  async upload(file: Buffer, filename: string, mimeType: string) {
    // 上传到S3/GCS/本地
    const url = await s3Client.upload(file, filename)
    return { url, filename, mimeType }
  }

  async delete(filename: string) {
    await s3Client.delete(filename)
  }
}

export default Module("MY_STORAGE", {
  service: MyStorageModuleService,
})
```

### Provider速查

| Provider | 用途 | 配置Key |
|---------|------|--------|
| `s3` | AWS S3 | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_BUCKET_NAME` |
| `gcloud` | Google Cloud Storage | `GCS_BUCKET_NAME`, `GCS_PROJECT_ID` |
| `local` | 本地文件系统 | `UPLOAD_DISABLE_TOTALSEARCH` |
| `minio` | MinIO对象存储 | 自建S3兼容存储 |

---

## 11. Module Link跨模块关联

```typescript
// src/links/digital-product-order.ts
import { defineLink } from "@medusajs/framework/utils"
import { DigitalProduct } from "../modules/digital-product/models/digital-product"
import { Order } from "@medusajs/framework/core"

export default defineLink({
  [DigitalProduct.name]: {
    order: {
      alias: "digitalOrders",
      linkable: {
        id: {
          entity: "Order",
          primaryKey: "id",
        },
      },
    },
  },
})
```

---

## 12. 插件开发

### 12.1 创建插件

```typescript
// plugins/my-plugin/src/index.ts
import {
  Plugin,
  Logger,
} from "@medusajs/framework/sdk"

class MyPlugin extends Plugin {
  getRoutes() {
    return [
      {
        route: "/plugins/my-plugin/hello",
        method: "get",
        handler: async (req, res) => {
          const logger: Logger = req.scope.resolve("logger")
          logger.info("Plugin route called")
          res.json({ message: "Hello from plugin!" })
        },
      },
    ]
  }
}

export default MyPlugin
```

### 12.2 插件注册与依赖

```typescript
// medusa-config.ts
module.exports = {
  plugins: [
    {
      resolve: "@medusajs/medusa-plugin-file",
      options: {
        upload_tracking: true,
      },
    },
    {
      resolve: "@medusajs/medusa-plugin-payment-stripe",
      options: {
        api_key: process.env.STRIPE_API_KEY,
        webhook_secret: process.env.STRIPE_WEBHOOK_SECRET,
      },
    },
    // 自定义插件
    {
      resolve: "./plugins/my-plugin",
      options: {
        myOption: "value",
      },
      dependencies: ["logger", "eventBusService"],
    },
  ],
}
```

---

## 13. 测试模式

### 13.1 单元测试

```typescript
// src/modules/__tests__/hello-world.spec.ts
import { helloWorldModuleService } from "."
import { ContainerRegistrationKeys } from "@medusajs/framework/utils"

describe("HelloWorldModuleService", () => {
  let service: HelloWorldModuleService
  let container: any

  beforeEach(() => {
    container = {
      resolve: (key: string) => {
        if (key === "logger") return { info: vi.fn() }
        return {}
      },
    }
    service = new helloWorldModuleService(container)
  })

  it("should create a custom entry", async () => {
    const result = await service.create_({ title: "Test", price: 100 })
    expect(result.title).toBe("Test")
  })
})
```

### 13.2 API集成测试

```typescript
// integration-tests/api/__tests__/store/products.spec.ts
import { ModuleRegistrationName } from "@medusajs/framework/utils"
import { api } from "./helpers"

describe("Store API", () => {
  let medusaContainer: any

  beforeEach(() => {
    medusaContainer = global.__MEDUSA_TEST_APP__
  })

  it("should list products", async () => {
    const response = await api.get("/store/products")

    expect(response.status).toBe(200)
    expect(response.data.products).toBeDefined()
    expect(Array.isArray(response.data.products)).toBe(true)
  })

  it("should create a cart and add items", async () => {
    const cart = await api.post("/store/carts", {})
    const cartId = cart.data.cart.id

    const cartItem = await api.post(`/store/carts/${cartId}/line-items`, {
      quantity: 2,
      variant_id: "variant_123",
    })

    expect(cartItem.data.cart.items.length).toBe(1)
  })
})
```

---

## 14. 关键文件路径参考

| 用途 | 路径 |
|------|------|
| 配置文件 | `medusa-config.ts` |
| Module Service | `src/modules/<name>/service.ts` |
| DML模型 | `src/modules/<name>/models/<name>.ts` |
| 自定义路由 | `src/api/<store|admin>/<name>/route.ts` |
| Event Subscriber | `src/subscribers/<name>.ts` |
| Scheduled Jobs | `src/jobs/<name>.ts` |
| Workflow定义 | `src/workflows/<name>/index.ts` |
| Workflow Steps | `src/workflows/<name>/steps.ts` |
| Module Links | `src/links/<name>.ts` |
| Loaders | `src/loaders/<name>.ts` |
| 工具函数 | `packages/core/flow/src/common/` |
| 核心服务 | `packages/modules/<name>/service.ts` |
| 核心模型 | `packages/modules/<name>/models/` |

---

## 15. 天龙引擎协同

| 岗位 | 协同场景 |
|------|---------|
| 01调研师 | Medusa.js源码考古、插件架构分析、Module链路追踪 |
| 02架构师 | Headless电商架构设计、插件化架构评估、多租户扩展方案 |
| 03构建师 | 插件开发、Workflow实现、API路由开发、Module Service开发 |
| 04验证师 | 电商端到端测试、Payment Provider测试、Workflow回滚测试 |
| 05安全师 | Payment API安全、Webhook签名验证、CORS配置审计 |
| 06审查师 | 插件代码审查、Event Subscriber模式审查、数据库迁移审查 |

---

## 16. 参考资料

- 官方文档: https://docs.medusajs.com/
- GitHub: https://github.com/medusajs/medusa
- 插件市场: https://medusajs.com/plugins
- GitHub Stars: 26,900+
- 许可证: MIT
