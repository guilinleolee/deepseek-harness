---
license: UNKNOWN
triggers: ["shell site generator", "shell-site-generator"]
---
# shell-site-generator

## L0: 一句话描述 (≤15字)

**独立站点：一键生成高转化着陆页**

---

## L1: 使用场景 (50-100字)

**适用场景**：单页着陆页生成、落地页A/B测试、联盟营销页、产品发布页、销售漏斗页、订阅转化页、快速MVP验证页。

**触发关键词**：`shell-site`、`着陆页`、`landing page`、`单页生成`、`高转化`、`联盟营销`

---

## L2: 详细文档

### 核心能力矩阵

| 能力 | 版本 | 说明 |
|------|------|------|
| 站点类型选择 | V1.0 | 6种站点类型智能匹配 |
| 高转化设计 | V1.0 | 转化率优化设计模式 |
| 快速部署 | V1.0 | Vercel/Netlify一键部署 |
| A/B测试支持 | V1.0 | 多变体版本管理 |
| 数据追踪集成 | V1.0 | GA/Plausible追踪代码 |

---

### 站点类型选择矩阵

```
┌─────────────────────────────────────────────────────────────┐
│                   站点类型智能选择                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  类型1: 产品发布页 (Product Launch)                        │
│  ├── 核心元素: Hero + 特性 + 定价 + FAQ                  │
│  ├── 适用: 新产品/功能发布                                  │
│  └── 转化目标: 订阅/下载                                   │
│                                                             │
│  类型2: 联盟营销页 (Affiliate)                              │
│  ├── 核心元素: 评价 + 佣金 + CTA                          │
│  ├── 适用: 联盟推广/推荐计划                                │
│  └── 转化目标: 注册/购买                                   │
│                                                             │
│  类型3: 销售漏斗页 (Sales Funnel)                          │
│  ├── 核心元素: 痛点 + 解决方案 + 证明 + 紧迫 + CTA       │
│  ├── 适用: 直接销售/课程/服务                               │
│  └── 转化目标: 立即购买                                    │
│                                                             │
│  类型4: 订阅转化页 (Subscription)                           │
│  ├── 核心元素: 免费试用 + 方案对比 + FAQ                  │
│  ├── 适用: SaaS订阅/会员服务                                │
│  └── 转化目标: 注册/订阅                                    │
│                                                             │
│  类型5: 内容引流页 (Content Lead)                          │
│  ├── 核心元素: 价值主张 + 内容预览 + CTA                   │
│  ├── 适用: 邮件列表/内容订阅                                 │
│  └── 转化目标: 邮件订阅                                    │
│                                                             │
│  类型6: MVP验证页 (MVP Validation)                         │
│  ├── 核心元素: 概念 + 演示 + 预约                         │
│  ├── 适用: 早期验证/预约登记                                │
│  └── 转化目标: 预约/邮箱                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 高转化设计模式

```yaml
转化率优化设计:
  标题钩子:
    - 痛点驱动: "结束XXX的困扰"
    - 结果驱动: "获得XXX的X个方法"
    - 数字驱动: "X步实现XXX"

  信任元素:
    - 数据背书: "1000+用户验证"
    - 评价引用: "用户原声评价"
    - 媒体背书: "被X媒体报道"
    - 品牌保证: "30天退款保证"

  CTA优化:
    - 紧迫性: "仅剩X个名额"
    - 价值: "免费获取"
    - 行动: "立即开始/立即获取"

  紧迫元素:
    - 价格锚定: "原价X → 现价Y"
    - 倒计时: "优惠截止X日"
    - 稀缺: "仅限前X名"
```

---

### AI提示词模板

#### 站点生成提示词

```markdown
# Role: Shell Site Generator

# 产品信息
- 产品名称：{product_name}
- 产品类型：{product_type}（产品发布/联盟营销/销售漏斗/订阅转化/内容引流/MVP验证）
- 目标用户：{target_audience}
- 核心价值：{core_value}
- 转化目标：{conversion_goal}

# 设计要求
1. 高转化率设计
2. 移动端优先
3. 加载速度<2秒
4. 清晰的CTA

# 输出要求
## 站点结构
- Hero区：标题 + 副标题 + CTA按钮
- 痛点区：目标用户痛点描述
- 解决方案：产品如何解决问题
- 证明区：数据/评价/背书
- 紧迫区：限时优惠/名额有限
- CTA区：最终转化按钮

## 技术要求
- 框架：{framework}（HTML/Tailwind/Next.js）
- 部署：{deployment}（Vercel/Netlify）
- 追踪：{analytics}（GA/Plausible）
```

#### 联盟页专用提示词

```markdown
# Role: Affiliate Landing Page Generator

# 产品信息
- 联盟产品：{affiliate_product}
- 佣金比例：{commission_rate}
- 产品优势：{product_strengths}
- 目标受众：{target_audience}

# 内容要求
1. 突出产品优势和用户收益
2. 真实评价和成功案例
3. 清晰的佣金说明
4. 信任建立元素

# 输出结构
## 评价区
- 3-5个真实用户评价
- 包含头像和名字

## 佣金展示
- 佣金比例说明
- 支付方式
- 提现门槛

## CTA区
- 注册按钮
- 追踪链接
```

---

### 命令调用

```bash
# 生成站点
shell-site generate --type "产品发布" --name "AI写作助手"

# 生成联盟页
shell-site affiliate --product "SaaS工具" --commission "30%"

# 生成销售漏斗页
shell-site funnel --product "课程" --price "999"

# 部署站点
shell-site deploy --platform vercel

# A/B测试版本
shell-site variants --base "landing" --count 3
```

---

### MCP工具调用

```bash
# 站点生成
mcp__shell_site__generate "AI工具" --type product-launch --framework nextjs

# 站点部署
mcp__shell_site__deploy "https://github.com/user/repo" --platform vercel

# 变体管理
mcp__shell_site__variants "landing-page" --create-ab-test

# 转化追踪
mcp__shell_site__analytics "site-id" --event conversion --goal subscribe
```

---

### 与其他技能协同

| 技能 | 协同方式 | 效果 |
|------|---------|------|
| `monetization-seven-swords` | 七剑→站点内容 | 高转化文案 |
| `opc-conversion-loop` | 转化漏斗→站点结构 | 转化优化 |
| `pricing-page-generator` | 定价页面生成 | 完整定价页 |
| `content-intel-cn` | 内容编排→站点文案 | 自动化内容 |

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-05 | 初始版本，独立站点生成器 |

---

**版本**: v1.0
**最后更新**: 2026-05-05
**技能类型**: 站点生成