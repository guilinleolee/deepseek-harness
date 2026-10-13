---
license: UNKNOWN
triggers: ["overseas pricing strategy", "overseas-pricing-strategy"]
---
# overseas-pricing-strategy

## L0: 一句话描述 (≤15字)

**海外定价策略：全球化定价优化与本地化策略**

---

## L1: 使用场景 (50-100字)

**适用场景**：全球化SaaS产品定价、跨国订阅制设计、按地区/国家差异化定价、海外市场定价测试、汇率风险管理、支付方式适配。**触发关键词**：`overseas-pricing`、`海外定价`、`全球化`、`USD定价`、`区域定价`、`pay-what-you-want`

---

## L2: 详细文档

### 核心能力矩阵

| 能力 | 版本 | 说明 |
|------|------|------|
| 全球化定价策略 | V1.0 | 全球市场定价矩阵与本地化策略 |
| 区域差异化定价 | V1.0 | PPP购买力平价+区域折扣体系 |
| 支付方式适配 | V1.0 | 全球支付网关+本地化支付方式 |
| 定价实验设计 | V1.0 | A/B测试+价格敏感度分析 |
| 汇率风险管理 | V1.0 | 动态汇率+价格调整机制 |
| 竞争定价监控 | V1.0 | 竞品全球定价追踪与分析 |

---

### 全球化定价策略矩阵

```
┌─────────────────────────────────────────────────────────────┐
│                    全球定价策略矩阵                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Tier 1: 美元基准市场 (USD Anchor)                        │
│  ├── 适用: 美国、加拿大、澳大利亚、英国                   │
│  ├── 策略: 全价Premium定位                               │
│  └── 心理价位: $9/$29/$99/月                             │
│                                                             │
│  Tier 2: 欧洲市场 (EUR Regional)                         │
│  ├── 适用: 德国、法国、西班牙、意大利                   │
│  ├── 策略: EUR定价，略低于USD等值                       │
│  └── 心理价位: €9/€25/€89/月                            │
│                                                             │
│  Tier 3: 发展中国家 (PPP Discount)                       │
│  ├── 适用: 印度、巴西、印尼、越南、尼日利亚            │
│  ├── 策略: PPP购买力平价折扣（40-70% off）            │
│  └── 心理价位: $3/$10/$30/月                            │
│                                                             │
│  Tier 4: 中国市场 (CNY Local)                            │
│  ├── 适用: 中国大陆                                     │
│  ├── 策略: CNY本地定价+国内支付                       │
│  └── 心理价位: ¥29/¥99/¥399/月                         │
│                                                             │
│  Tier 5: Pay-What-You-Want (PWYW)                      │
│  ├── 适用: 新兴市场、低收入国家                        │
│  ├── 策略: 建议价+最低价+免费选项                      │
│  └── 心理价位: $1起                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 区域定价折扣体系

```yaml
购买力平价(PPP)折扣计算:
  USD基准价格: $29/月

  Tier 1 (美国/英国/加拿大):
    折扣: 0% (基准)
    本地价格: $29

  Tier 2 (德国/法国/日本):
    折扣: 10-15%
    本地价格: €25-26

  Tier 3 (印度):
    PPP比率: 0.27 (世界银行2024)
    折扣: 65-75%
    本地价格: ₹299-399

  Tier 4 (巴西):
    PPP比率: 0.38
    折扣: 55-65%
    本地价格: R$49-69

  Tier 5 (中国):
    PPP比率: 0.42
    折扣: 50-60%
    本地价格: ¥59-79

定价心理策略:
  锚定效应:
    - 高价锚: 显示USD原价，对比本地折扣
    - 心理锚: 9.99 vs 10，差1分钱差异大

  数字迷信:
    - 西方: 9结尾（$9.99）
    - 中国: 8结尾（¥99）
    - 日本: 000结尾（¥9,800）

  支付方式心理:
    - 分期付款降低感知成本
    - 年付享折扣（20-30%）
```

---

### 支付方式全球适配矩阵

```yaml
支付网关选择:
  Stripe Global:
    支持: 135+货币
    本地支付方式:
      - SEPA (欧洲)
      - BACS (英国)
      - ACH (美国)
      - 当地银行卡

  Paddle:
    优势: 增值税自动化合规
    支持: 全球+税务处理

  区域支付特供:
    中国:
      - 支付宝(Alipay)
      - 微信支付(WeChat Pay)
      - 银联卡

    印度:
      - UPI (统一支付接口)
      - Paytm
      - PhonePe

    东南亚:
      - GrabPay
      - GoPay
      - Boost

    拉丁美洲:
      - MercadoPago
      - Boleto
      - OXXO

    中东:
      - CashU
      - OneCard

合规要求:
  欧盟: VAT MOSS申报
  英国: VAT数字服务
  印度: GST合规
  巴西: ISS/ICMS
```

---

### AI提示词模板

#### 全球化定价策略提示词

```markdown
# Role: 全球定价策略分析师

# 产品信息
- 产品名称: {product_name}
- 当前定价: {current_pricing}
- 目标市场: {target_markets}
- 核心价值: {core_value}
- 竞品定价: {competitor_pricing}

# 区域市场分析
1. Tier 1市场（美/英/澳）:
   - 本地消费能力: {purchasing_power}
   - 竞品价格区间: {price_range_tier1}
   - 推荐定价: {recommended_tier1}

2. Tier 2市场（欧/日）:
   - PPP折扣空间: {ppp_discount}
   - 本地竞品: {local_competitors}
   - 推荐定价: {recommended_tier2}

3. Tier 3市场（印/巴/东南亚）:
   - PPP比率: {ppp_ratio}
   - 支付方式: {payment_methods}
   - 推荐定价: {recommended_tier3}

# 输出要求
## 定价矩阵
| 市场 | 本地货币 | USD等值 | 折扣率 | 支付方式 |
|------|---------|---------|--------|----------|
| 美国 | $29 | $29 | 0% | Stripe |
| 德国 | €26 | $28 | 3% | SEPA |
| 印度 | ₹399 | $4.80 | 83% | UPI |

## 实施建议
- 定价测试策略
- 支付网关配置
- 税务合规
- 汇率风险管理
```

#### 定价A/B测试设计提示词

```markdown
# Role: 定价实验设计师

# 产品信息
- 产品: {product_name}
- 当前价格: {current_price}
- 测试假设: {test_hypothesis}

# 测试设计
## Test 1: 价格点测试
- Control: $29/月
- Variant A: $39/月（+34%）
- Variant B: $19/月（-34%）

## Test 2: 锚定测试
- Control: $29/月
- Variant: 显示$49原价，折扣价$29

## Test 3: 付款周期测试
- Control: 月付$29
- Variant A: 年付$290（-17%）
- Variant B: 季付$79（-9%）

# 关键指标
- 主要: MRR转化率
- 次要: 试用→付费转化率
- 监控: 流失率变化

# 输出要求
## 测试时间
- 最小样本: {min_sample}
- 测试周期: {test_duration}
- 统计显著性: 95%置信区间

## 预期结果分析
- 最佳价格点
- 收入最大化
- 长期LTV影响
```

---

### 命令调用

```bash
# 全球定价策略分析
overseas-pricing analyze --product "SaaS工具" --markets "US,DE,IN,CN"

# 区域定价计算
overseas-pricing calculate --base-price 29 --region "India" --method ppp

# 定价测试设计
overseas-pricing experiment --product "AI工具" --type "price-point"

# 支付方式配置
overseas-pricing payment --region "China" --methods "alipay,wechatpay,unionpay"

# 竞品定价追踪
overseas-pricing competitor --product "AI写作" --markets "global"

# 汇率风险管理
overseas-pricing forex --base-currency USD --target-currencies "EUR,GBP,JPY,CNY,INR"
```

---

### MCP工具调用

```bash
# 全球化定价分析
mcp__pricing__global_strategy "SaaS产品" --markets US,DE,IN,CN,BR --model ppp

# 区域折扣计算
mcp__pricing__regional_discount --base-price 29 --region "India" --factors purchasing_power,competition,local_competitors

# 支付方式推荐
mcp__pricing__payment_methods --region "Southeast Asia" --currency auto

# 定价实验设计
mcp__pricing__experiment --product "AI写作助手" --test-types "price_point,anchoring,billing_cycle"

# 竞品全球定价监控
mcp__pricing__competitor_tracking --product "AI工具" --markets global --update-frequency weekly

# 汇率风险报告
mcp__pricing__forex_risk --currencies USD,EUR,GBP,JPY --exposure 100000
```

---

### 与其他技能协同

| 技能 | 协同方式 | 效果 |
|------|---------|------|
| `vertical-saas-builder` | 垂直SaaS定价策略 | Phase 1-4差异化全球定价 |
| `monetization-seven-swords` | 七剑→海外文案 | 本地化转化文案 |
| `shell-site-generator` | 站点→区域定价页 | 本地化落地页 |
| `pricing-page-generator` | 定价页面→全球版 | 多货币定价展示页 |

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-05 | 初始版本，全球化定价策略完整技能 |

---

**版本**: v1.0
**最后更新**: 2026-05-05
**技能类型**: 全球化定价策略
