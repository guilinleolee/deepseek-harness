---
license: UNKNOWN
triggers: ["鐢靛晢杩愯惀", "45-01 电商运营 V2.1"]
---
# 45-01 电商运营 V2.1

## L0: 一句话描述
CRMEB电商全链路运营操盘手册：活动策划 + 数据监控 + 营销配置

## L1: 使用场景
适用于CRMEB电商后台运营管理、营销活动配置（优惠券/拼团/秒杀/分销/积分）、销售数据看板监控、天龙电商协同链路（08发布师→35-02社媒运营→45-01电商运营）等场景。天龙03构建师、35-02社媒运营直接调用。

## L2: 详细文档

### 一、CRMEB后台操作手册

#### 1.1 管理后台路径

```
CRMEB后台地址: https://your-domain.com/admin
默认账号: admin / admin123
```

#### 1.2 核心菜单结构

```
商城管理
├── 商品管理（商品列表/分类/品牌/规格/运费模板）
├── 订单管理（订单列表/退款/批量发货）
├── 用户管理（用户列表/会员等级/用户充值）
├── 营销管理 ⭐核心
│   ├── 优惠券（创建/发放/核销）
│   ├── 拼团（创建活动/团长管理）
│   ├── 秒杀（时段配置/商品管理）
│   ├── 分销（分销商管理/佣金报表）
│   ├── 积分（积分规则/积分商城）
│   └── 满减满折
├── 财务统计（账单明细/充值记录/提现管理）
├── 物流管理（电子面单/物流公司/轨迹查询）
└── 数据统计
    ├── 营业统计（营业额/订单量/客单价）
    ├── 商品统计（销量/收藏/转化率）
    └── 会员统计（新增/活跃/留存）
```

---

### 二、营销活动全配置

#### 2.1 优惠券（Coupons）

##### 2.1.1 优惠券类型

| 类型 | 描述 | 适用场景 |
|------|------|---------|
| 满减券 | 满X元减Y元 | 促进客单价提升 |
| 折扣券 | 商品折扣N% | 清库存/引流量 |
| 兑换券 | 兑换指定商品 | 会员权益/积分兑换 |
| 包邮券 | 免运费 | 降低购买门槛 |

##### 2.1.2 优惠券创建（API方式）

```php
// POST /admin/system/config/save_basics
// 优惠券基础配置
$data = [
    'name' => '新人专享券',
    'type' => 1,                          // 1满减 2折扣 3兑换 4包邮
    'money' => 10,                        // 优惠金额
    'min_price' => 100,                   // 最低消费
    'coupon_type' => 1,                  // 1满减券
    'is_give_subscribe' => 1,            // 关注送券
    'is_give_new' => 1,                 // 新用户送券
    'expire_type' => 1,                 // 1固定时间 2领取后N天
    'expire_day' => 7,                   // 领取后有效期天数
    'coupon_num' => 1000,                // 发放总数量
    'limit_num' => 1,                    // 每人限领数量
    'status' => 1,                       // 1开启
];
```

##### 2.1.3 优惠券发放

```php
// 主动发放给用户
$couponService->give(USER_ID, COUPON_ID);

// 根据标签批量发放
$couponService->giveByTag('new_user', COUPON_ID, [
    'expire_day' => 7,
    'source' => '运营手动发放'
]);
```

##### 2.1.4 优惠券核销查询

```php
// 查询核销情况
$list = $couponService->getUseLogList([
    'coupon_id' => COUPON_ID,
    'start_time' => '2026-01-01',
    'end_time' => '2026-01-31'
]);

// 核心指标
$stats = [
    'send_count'   => $list['send_count'],    // 发放数量
    'use_count'    => $list['use_count'],     // 使用数量
    'use_rate'     => $list['use_count'] / $list['send_count'],  // 核销率
    'amount'       => $list['amount']         // 优惠金额
];
```

---

#### 2.2 拼团活动（GroupBuying）

##### 2.2.1 拼团活动创建

```php
// POST /admin/marketing/store_combination/save
$data = [
    'title' => '【3人团】爆款面膜限时拼',
    'people' => 3,                        // 成团人数
    'price' => 49.9,                      // 拼团价
    'original_price' => 99.9,             // 单买价
    'store_id' => PRODUCT_ID,
    'images' => ['/uploads/1.jpg', '/uploads/2.jpg'],
    'description' => '爆款面膜，3人成团，低至5折',
    'start_time' => '2026-06-01 00:00:00',
    'end_time' => '2026-06-30 23:59:59',
    'stock' => 500,                       // 拼团库存
    'people_num' => 100,                  // 预计成团数
    'is_hot' => 1,                        // 热门推荐
    'status' => 1
];
```

##### 2.2.2 拼团状态管理

```php
// 拼团状态枚举
const GROUP_STATUS = [
    0 => '待付款',        // 开团/参团后等待付款
    1 => '拼团中',        // 已付款，等待成团
    2 => '拼团成功',      // 已成团，等待发货
    3 => '拼团失败',      // 未成团，自动退款
    4 => '已取消'         // 手动取消
];

// 查询拼团列表
$groupService->getList([
    'status' => 2,            // 拼团成功的
    'start_time' => '2026-01-01',
    'end_time' => '2026-01-31'
]);
```

##### 2.2.3 拼团数据看板

| 指标 | SQL/查询方式 | 优化建议 |
|------|------------|---------|
| 开团数 | `COUNT(*) WHERE status>=0` | 引导老带新 |
| 成团率 | 成团数/开团数 | 低于60%需优化价格 |
| 参团转化率 | 参团人数/访问人数 | 低于3%优化曝光 |
| 客单价 | 拼团GMV/订单数 | 提升关联销售 |
| 亏损率 | (原价-拼团价)/原价 | 建议不超40% |

---

#### 2.3 秒杀活动（Seckill）

##### 2.3.1 秒杀时段配置

```php
// 秒杀时段表（store_seckill_time）
$timeSlots = [
    ['time' => '00:00', 'title' => '凌晨场'],
    ['time' => '10:00', 'title' => '早场'],
    ['time' => '12:00', 'title' => '午间场'],
    ['time' => '15:00', 'title' => '下午场'],
    ['time' => '20:00', 'title' => '黄金场'],
    ['time' => '22:00', 'title' => '深夜场'],
];
```

##### 2.3.2 秒杀商品管理

```php
// POST /admin/marketing/store_seckill_product/save
$data = [
    'product_id' => PRODUCT_ID,
    'time_id' => TIME_SLOT_ID,
    'price' => 19.9,            // 秒杀价
    'original_price' => 59.9,    // 原价
    'stock' => 100,              // 秒杀库存
    'sales' => 0,                 // 真实销量
    'limit_num' => 1,            // 每人限购数量
    'start_time' => '2026-06-01',
    'end_time' => '2026-06-18'
];
```

##### 2.3.3 秒杀风控脚本

```bash
# 查看秒杀实时库存（Redis）
redis-cli -n 3 GET "seckill_stock_{product_id}_{time_id}"
redis-cli -n 3 DECR "seckill_stock_{product_id}_{time_id}"

# 查看秒杀订单
redis-cli -n 3 LRANGE "seckill_order_{product_id}_{time_id}" 0 -1

# 手动关闭异常秒杀
php think seckill:close-product {product_id}
```

---

#### 2.4 分销管理（Distribution）

##### 2.4.1 分销层级配置

```php
// 分销层级表（system_distribtion_level）
$levels = [
    1 => ['name' => '青铜分销商', 'brokerage_rate' => 5],
    2 => ['name' => '白银分销商', 'brokerage_rate' => 8],
    3 => ['name' => '黄金分销商', 'brokerage_rate' => 12],
    4 => ['name' => '钻石分销商', 'brokerage_rate' => 15],
];
```

##### 2.4.2 分销佣金规则

```php
// /admin/marketing/store_brokerage_order/index
// 分销订单查询
$brokerageService->getOrderList([
    'brokerage_type' => 1,          // 1自购 2返利
    'status' => 1,                   // 1已结算 2待结算
    'start_time' => '2026-01-01',
    'end_time' => '2026-01-31'
]);
```

##### 2.4.3 分销佣金报表

| 指标 | 计算方式 | 运营阈值 |
|------|---------|---------|
| 分销GMV占比 | 分销订单GMV/总GMV | >15%健康 |
| 佣金支出率 | 佣金总额/分销GMV | <10%健康 |
| 顶级分销商数 | 分销商等级=4的数量 | 月增>10% |
| 邀请转化率 | 成为分销商/注册用户 | >5% |

---

#### 2.5 积分体系（Points）

##### 2.5.1 积分规则配置

```php
// /admin/system/config/save_basics
$pointRules = [
    'integral_rule' => [
        'sign_day1' => 5,           // 第1天签到积分
        'sign_day3' => 10,         // 连续3天签到
        'sign_day7' => 20,         // 连续7天签到
        'order_back' => '1',       // 订单返积分比例(%)
        'order_give' => 1,        // 消费1元返积分
    ],
    'integral_rate' => 0.01        // 积分抵现比例 100积分=1元
];
```

##### 2.5.2 积分商城

```php
// 积分商品创建
$integralService->createProduct([
    'title' => '满100积分抵1元优惠券',
    'type' => 2,                   // 1实物 2虚拟 3优惠券
    'price' => 100,                 // 所需积分
    'stock' => 1000,
    'images' => '/uploads/point/1.jpg'
]);
```

---

### 三、销售数据看板

#### 3.1 核心指标体系

| 指标 | 计算公式 | 健康范围 | 预警阈值 |
|------|---------|---------|---------|
| GMV | Σ(订单实付金额) | 趋势增长 | 周环比<-10% |
| 订单数 | COUNT(order_id) | 趋势增长 | 周环比<-15% |
| 客单价 | GMV/订单数 | >行业均值 | <50分位数 |
| 优惠券核销率 | 使用数/发放数 | >30% | <15% |
| 拼团成团率 | 成团数/开团数 | >60% | <40% |
| 分销GMV占比 | 分销GMV/总GMV | >15% | <5% |
| 退款率 | 退款金额/GMV | <5% | >10% |
| 转化率 | 下单UV/访问UV | >3% | <1% |

#### 3.2 仪表板SQL查询

```sql
-- 核心销售报表
SELECT
    DATE(create_time) AS date,
    COUNT(DISTINCT uid) AS buyer_count,
    COUNT(id) AS order_count,
    SUM(pay_price) AS gmv,
    AVG(pay_price) AS avg_price
FROM eb_store_order
WHERE paid=1 AND refund_status IN (0, -1)
  AND create_time BETWEEN '{start}' AND '{end}'
GROUP BY DATE(create_time)
ORDER BY date DESC;

-- 渠道分析
SELECT
    spread_uid,                       -- 推广人ID
    COUNT(*) AS order_count,
    SUM(pay_price) AS gmv,
    SUM(pay_price) * 0.1 AS brokerage -- 10%佣金
FROM eb_store_order
WHERE spread_uid > 0 AND paid=1
GROUP BY spread_uid
ORDER BY gmv DESC
LIMIT 20;

-- 退款分析
SELECT
    DATE(o.create_time) AS date,
    COUNT(DISTINCT o.id) AS refund_count,
    SUM(o.pay_price) AS refund_amount,
    ROUND(SUM(o.pay_price) / (SELECT SUM(pay_price) FROM eb_store_order WHERE paid=1) * 100, 2) AS refund_rate
FROM eb_store_order o
WHERE o.refund_status > 0
GROUP BY DATE(o.create_time);
```

---

### 四、活动策划 SOP

#### 4.1 活动策划五步法

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: 目标设定                                           │
│ ├── GMV提升目标 (e.g. +30%)
│ ├── 拉新目标 (e.g. 新增500用户)
│ └── 激活目标 (e.g. 沉睡用户召回200人)
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: 选品与组货                                        │
│ ├── 引流款 (亏损引流, 占GMV 20%)
│ ├── 利润款 (正常毛利, 占GMV 60%)
│ └── 形象款 (高品质, 占GMV 20%)
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: 玩法设计                                          │
│ ├── 优惠券叠加规则 (是否可与拼团同用)
│ ├── 限时折扣 (秒杀/限时特价)
│ └── 社交裂变 (拼团/邀请有礼)
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: 预热与投放                                        │
│ ├── 预热期 (活动前3天, 社媒/短信通知)
│ ├── 投放预算 (搜索/信息流/社媒)
│ └── 应急预案 (库存不足/系统故障)
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: 复盘与迭代                                        │
│ ├── 核心指标达成率
│ ├── 用户反馈收集
│ └── 活动迭代优化建议
└─────────────────────────────────────────────────────────────┘
```

#### 4.2 活动日历模板

| 月份 | 主题活动 | 营销工具 |
|------|---------|---------|
| 1月 | 新年大促 | 满减+年货礼盒 |
| 2月 | 情人节 | 礼品套装+表白卡 |
| 3月 | 女神节 | 折扣券+限时秒杀 |
| 4月 | 春季焕新 | 新品首发+满减 |
| 5月 | 五一大促 | 优惠券+拼团 |
| 6月 | 618大促 | 全场折扣+红包 |
| 7-8月 | 暑期特惠 | 清仓秒杀+积分加倍 |
| 9月 | 开学季 | 学生专属折扣 |
| 10月 | 国庆中秋 | 礼盒套装+满减 |
| 11月 | 双11预热 | 预售+红包雨 |
| 12月 | 双12+年终 | 最后的冲刺促销 |

---

### 五、天龙岗位协同链路

```
00分析师
  ↓ 分析电商需求（商品SKU/营销活动/多端适配）
  ↓
01调研师
  ↓ 调研 CRMEB 模板能力 + 小程序商城规范
  ↓ 调研 ThinkPHP6 接口协议 + 微信支付 V3 API
  ↓
02架构师
  ↓ 设计多端统一架构（Taro3 / uni-app）
  ↓ 设计分包加载策略
  ↓
03构建师
  ↓ 前端：Taro3 多端编译 + CRMEB 模板定制
  ↓ 后端：ThinkPHP6 路由 + 微信支付 V3 集成
  ↓
04验证师
  ↓ 支付全流程测试（沙箱环境）
  ↓ 多端兼容性测试
  ↓ 裂变链路测试（分享→绑定→下单→佣金）
  ↓
05安全师
  ↓ 支付签名验证 + Token 安全 + 敏感数据加密
  ↓
08发布师
  ↓ 小程序提交审核（包大小优化/类目选择/资质合规）
  ↓ H5 域名备案 + SSL 证书配置
  ↓
35-02社媒运营
  ↓ 朋友圈分享文案 + 小程序码生成 + 订阅消息触达
  ↓
45-01电商运营 ⭐本SKILL
  ↓ 活动策划（优惠券/拼团/秒杀/分销）
  ↓ 销售数据看板监控（优惠券核销率/拼团成功率）
  ↓ 运营复盘 + 活动迭代优化
```

---

### 六、常用命令速查

#### 6.1 Redis运维

```bash
# 清理过期缓存（每月1日凌晨执行）
redis-cli -n 3 KEYS "cache_*" | head -1000 | xargs redis-cli -n 3 DEL

# 查看秒杀实时库存
redis-cli -n 3 GET "seckill_stock_123_1"

# 查看拼团缓存
redis-cli -n 3 GET "combination_{order_id}"

# 刷新配置缓存
redis-cli -n 3 DEL "eb_system_config"
```

#### 6.2 定时任务

```bash
# 查看ThinkPHP定时任务
php think

# 手动触发秒杀关闭过期
php think seckill:close-expired

# 手动触发物流轨迹同步
php think delivery:sync-traces

# 手动触发订单自动关闭
php think order:auto-close

# 手动触发积分返利
php think brokerage:auto-return
```

#### 6.3 订单状态流转

```
0(待支付) → 1(已支付) → 2(待收货) → 3(已完成)
    ↓           ↓           ↓
 -1(已取消) -2(退款中) -3(已退款)
```

#### 6.4 日志查看

```bash
# 支付日志
tail -f runtime/log/$(date +Y-m-d).log | grep PayService

# 订单日志
tail -f runtime/log/$(date +Y-m-d).log | grep OrderService

# 秒杀日志
tail -f runtime/log/$(date +Y-m-d).log | grep SeckillService
```

---

### 七、关键坑点速查

| 坑点 | 原因 | 解决方案 |
|------|------|---------|
| 优惠券叠加冲突 | 多券同用导致负金额 | 设置互斥规则，优惠券优先级控制 |
| 拼团库存超卖 | Redis计数未原子化 | 使用DECR原子操作，超卖返回错误 |
| 秒杀价低于成本 | 活动配置校验缺失 | 设置商品成本价校验，超低价禁止提交 |
| 分销佣金重复计算 | 上下级关系变更导致 | 订单创建时锁定分销关系，后续变更不影响已下单 |
| 积分抵现超限 | 未限制积分使用比例 | 设置单次抵现上限（如≤订单金额10%） |
| 退款后积分不扣 | 未处理积分回退逻辑 | 退款时同步执行 pointService->back($order_id) |
| 物流轨迹推送丢失 | 消息队列未持久化 | 使用RabbitMQ持久化队列，ack机制保证送达 |

---

### 八、核心文件清单

| 文件 | 作用 | CRMEB路径 |
|------|------|-----------|
| 优惠券配置 | 优惠券创建/发放/核销 | `app/admin/controller/marketing/StoreCoupons.php` |
| 拼团管理 | 拼团活动/成团/团员 | `app/admin/controller/marketing/StoreCombination.php` |
| 秒杀管理 | 秒杀时段/商品/库存 | `app/admin/controller/marketing/StoreSeckill.php` |
| 分销管理 | 分销商/佣金/提现 | `app/admin/controller/marketing/StoreBrokerage.php` |
| 积分管理 | 积分规则/商城/记录 | `app/admin/controller/marketing/StoreIntegral.php` |
| 销售统计 | 营业/商品/会员统计 | `app/admin/controller/statistics/` |
| 支付服务 | 微信支付/余额支付 | `app/services/PayServices.php` |
| 物流服务 | 电子面单/轨迹推送 | `app/services/DeliveryRepository.php` |
