---
license: UNKNOWN
triggers: ["java ecommerce patterns", "Java电商全链路运营模式 SKILL.md"]
---
# Java电商全链路运营模式 SKILL.md

## L0: 一句话描述 (≤15字)
Java/JVM电商全链路运营技能包

## L1: 使用场景 (50-100字)
当需要进行Java/JVM技术栈的电商系统调研、代码审查、架构设计或运营开发时，调用本Skill。覆盖Spring Boot/Spring Cloud生态下营销、积分、会员、分销、订单、支付、物流完整链路的技术实现与架构模式。

## L2: 详细文档

---

## 1. Java技术栈速查

### 核心技术栈对应关系

| PHP/Workerman (CRMEB) | Java/JVM (本Skill) |
|----------------------|-------------------|
| ThinkPHP6 | Spring Boot 3.x / Spring Cloud Alibaba |
| Workerman / Swoole | Undertow / Netty (非阻塞I/O) |
| Redis (Queue/缓存) | Redis + Redisson (分布式锁) / RedisTemplate |
| MySQL QueryBuilder | JPA (Hibernate) / MyBatis-Plus |
| Vue.js/Taro | Vue3 + Element Plus / UniApp |
| RabbitMQ | RocketMQ (阿里系) / Kafka (高并发) |
| Redis Lua | Redisson Lua Script |

### Spring Boot项目结构

```
src/main/java/com/ecommerce/
├── controller/          # REST API控制器 (@RestController)
├── service/            # 业务逻辑 (@Service)
├── repository/         # 数据访问 (JPA Repository / MyBatis Mapper)
├── entity/             # 实体类 (@Entity / @Data)
├── dto/                # 数据传输对象
├── config/            # 配置类 (@Configuration)
├── scheduler/         # 定时任务 (@Scheduled)
├── kafka/             # 消息队列 (@KafkaListener)
├── redis/             # 缓存操作 (RedisTemplate)
└── common/            # 通用类 (Result, Constants)
```

### 核心依赖 (pom.xml)

```xml
<dependencies>
    <!-- Spring Boot Starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-redis</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>

    <!-- 数据库 -->
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
    </dependency>

    <!-- Redis + Redisson (分布式锁) -->
    <dependency>
        <groupId>org.redisson</groupId>
        <artifactId>redisson-spring-boot-starter</artifactId>
    </dependency>

    <!-- 消息队列 -->
    <dependency>
        <groupId>org.apache.rocketmq</groupId>
        <artifactId>rocketmq-spring-boot-starter</artifactId>
    </dependency>

    <!-- 微服务 -->
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
    </dependency>
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-sentinel</artifactId>
    </dependency>

    <!-- 工具 -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
    </dependency>
    <dependency>
        <groupId>cn.hutool</groupId>
        <artifactId>hutool-all</artifactId>
    </dependency>
</dependencies>
```

---

## 2. 营销活动体系

### 优惠券表结构 (JPA Entity)

```java
@Entity
@Table(name = "sys_coupon")
@Data
public class Coupon {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;           // 优惠券名称
    private Integer type;          // 1满减券 2折扣券 3无门槛券
    private BigDecimal minPrice;   // 最低消费
    private BigDecimal couponPrice; // 优惠金额
    private BigDecimal discount;    // 折扣率 (0.8=8折)
    private Integer total;          // 发放总量
    private Integer remain;          // 剩余数量
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private Integer status;         // 1未发布 2已发布 3已领完 4已过期

    @Column(name = "product_range")
    private Integer productRange;  // 1全场通用 2指定商品 3指定分类
    @Column(name = "category_ids")
    private String categoryIds;    // 指定分类ID (逗号分隔)
    @Column(name = "product_ids")
    private String productIds;      // 指定商品ID
}
```

### 优惠券领取 (Service层)

```java
@Service
@RequiredArgsConstructor
public class CouponService {

    private final CouponRepository couponRepository;
    private final CouponUserRepository couponUserRepository;
    private final RedisTemplate<String, String> redisTemplate;

    private static final String COUPON_STOCK_KEY = "coupon:stock:";

    /**
     * 优惠券领取 — 双检锁防超卖
     * 等价于 PHP: CouponRepository::receiveCoupon()
     */
    @Transactional
    public void receiveCoupon(Long couponId, Long userId) {
        // 1. 校验优惠券
        Coupon coupon = couponRepository.findById(couponId)
            .orElseThrow(() -> new BizException("优惠券不存在"));

        if (coupon.getStatus() != 2) {
            throw new BizException("优惠券未发布");
        }
        if (LocalDateTime.now().isAfter(coupon.getEndTime())) {
            throw new BizException("优惠券已过期");
        }

        // 2. 校验是否已领取
        if (couponUserRepository.existsByCouponIdAndUserId(couponId, userId)) {
            throw new BizException("已领取过该优惠券");
        }

        // 3. Redis原子扣库存 (Lua脚本保证原子性)
        String stockKey = COUPON_STOCK_KEY + couponId;
        Long stock = redisTemplate.opsForValue().decrement(stockKey);
        if (stock == null || stock < 0) {
            // 恢复库存
            redisTemplate.opsForValue().increment(stockKey);
            throw new BizException("优惠券已领完");
        }

        // 4. 保存领取记录
        CouponUser couponUser = new CouponUser();
        couponUser.setCouponId(couponId);
        couponUser.setUserId(userId);
        couponUser.setStatus(0); // 0未使用 1已使用 2已过期
        couponUser.setCreateTime(LocalDateTime.now());
        couponUserRepository.save(couponUser);
    }

    /**
     * 计算最优优惠券
     * 等价于 PHP: CouponRepository::calculateDiscount()
     */
    public BigDecimal calculateDiscount(Long userId, List<CartItem> cartItems) {
        List<CouponUser> availableCoupons =
            couponUserRepository.findByUserIdAndStatus(userId, 0);

        List<CouponUser> usable = availableCoupons.stream()
            .filter(c -> c.getStartTime().isBefore(LocalDateTime.now()))
            .filter(c -> c.getEndTime().isAfter(LocalDateTime.now()))
            .toList();

        BigDecimal maxDiscount = BigDecimal.ZERO;
        for (CouponUser cu : usable) {
            Coupon coupon = couponRepository.findById(cu.getCouponId()).orElse(null);
            if (coupon == null) continue;

            // 满减金额计算
            BigDecimal cartTotal = cartItems.stream()
                .map(CartItem::getTotalPrice)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

            if (cartTotal.compareTo(coupon.getMinPrice()) >= 0) {
                if (coupon.getType() == 1) {
                    maxDiscount = maxDiscount.max(coupon.getCouponPrice());
                } else if (coupon.getType() == 2) {
                    BigDecimal discount = cartTotal.multiply(
                        BigDecimal.ONE.subtract(coupon.getDiscount()));
                    maxDiscount = maxDiscount.max(discount);
                }
            }
        }
        return maxDiscount;
    }
}
```

### 优惠券Controller

```java
@RestController
@RequestMapping("/api/coupon")
@RequiredArgsConstructor
public class CouponController {

    private final CouponService couponService;

    @GetMapping("/list")
    public Result<List<Coupon>> list() {
        return Result.ok(couponService.getAvailableCoupons());
    }

    @PostMapping("/receive/{id}")
    public Result<Void> receive(@PathVariable Long id,
                                 @RequestHeader("userId") Long userId) {
        couponService.receiveCoupon(id, userId);
        return Result.ok();
    }

    @GetMapping("/my")
    public Result<List<CouponUser>> myCoupons(@RequestHeader("userId") Long userId) {
        return Result.ok(couponService.getMyCoupons(userId));
    }
}
```

### Redis Lua防超卖脚本

```lua
-- coupon_stock.lua: 原子扣库存
local stock = redis.call('GET', KEYS[1])
if stock == false then
    return -1  -- 库存未初始化
end
if tonumber(stock) <= 0 then
    return 0   -- 库存不足
end
return redis.call('DECR', KEYS[1])  -- 原子扣减
```

---

## 3. 积分体系

### 积分变动记录表

```java
@Entity
@Table(name = "user_point_log")
@Data
public class UserPointLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long userId;
    private Integer point;           // 变动积分 (正数增加/负数扣减)
    private Integer balance;        // 变动后余额
    private Integer source;         // 1订单赠送 2每日签到 3管理员调整 4订单退回
    private String remark;
    private String orderSn;        // 关联订单号
    private LocalDateTime createTime;
}
```

### 积分Service

```java
@Service
@RequiredArgsConstructor
public class PointService {

    private final UserPointLogRepository pointLogRepository;
    private final UserRepository userRepository;
    private final RedisTemplate<String, String> redisTemplate;

    private static final String USER_POINT_KEY = "user:point:";

    /**
     * 积分增减 — 等价于 PHP UserPointRepository::changePoint()
     */
    @Transactional
    public void changePoint(Long userId, Integer point, Integer source, String remark) {
        // 1. Redis原子增减
        String pointKey = USER_POINT_KEY + userId;
        Long newBalance = redisTemplate.opsForValue().increment(pointKey, point);

        if (newBalance == null || newBalance < 0) {
            // 扣减时余额不足，回滚Redis
            redisTemplate.opsForValue().increment(pointKey, -point);
            throw new BizException("积分不足");
        }

        // 2. 持久化DB
        Integer dbBalance = userRepository.findPointByUserId(userId);
        if (dbBalance == null) dbBalance = 0;

        UserPointLog log = new UserPointLog();
        log.setUserId(userId);
        log.setPoint(point);
        log.setBalance(dbBalance + point);
        log.setSource(source);
        log.setRemark(remark);
        log.setCreateTime(LocalDateTime.now());
        pointLogRepository.save(log);

        // 3. 更新用户表积分
        userRepository.updatePoint(userId, dbBalance + point);
        return;
    }

    /**
     * 订单完成赠送积分
     * 等价于 PHP UserPointRepository::order_give_point()
     */
    public void givePointByOrder(Long userId, String orderSn, BigDecimal orderPrice) {
        // 订单金额100元=1积分
        int givePoint = orderPrice.divide(BigDecimal.valueOf(100), 0, RoundingMode.DOWN).intValue();
        if (givePoint > 0) {
            changePoint(userId, givePoint, 1, "订单 " + orderSn + " 赠送积分");
        }
    }

    /**
     * 获取积分余额 (缓存优先)
     */
    public Integer getPointBalance(Long userId) {
        String pointKey = USER_POINT_KEY + userId;
        String cached = redisTemplate.opsForValue().get(pointKey);
        if (cached != null) {
            return Integer.parseInt(cached);
        }
        Integer dbBalance = userRepository.findPointByUserId(userId);
        if (dbBalance == null) dbBalance = 0;
        redisTemplate.opsForValue().set(pointKey, String.valueOf(dbBalance), 1, TimeUnit.HOURS);
        return dbBalance;
    }
}
```

---

## 4. 会员体系与成长值

### 会员等级表

```java
@Entity
@Table(name = "user_level")
@Data
public class UserLevel {

    @Id
    private Integer id;
    private String name;           // 青铜/白银/黄金/铂金/钻石
    private Integer grade;          // 等级数值 1-5
    private Integer experience;     // 升级所需成长值
    private BigDecimal discount;   // 享受折扣率
    private Integer pointBack;       // 积分返还比例 (%)
}
```

### 会员Service

```java
@Service
@RequiredArgsConstructor
public class MemberService {

    private final UserRepository userRepository;
    private final UserLevelRepository userLevelRepository;
    private final PointService pointService;

    /**
     * 成长值增加并检测升级
     * 等价于 PHP: MemberRepository::addExperience()
     */
    @Transactional
    public void addExperience(Long userId, Integer exp) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new BizException("用户不存在"));

        Integer oldLevel = user.getLevel();
        Integer newExp = user.getExperience() + exp;
        Integer newLevel = calculateLevel(newExp);

        user.setExperience(newExp);
        user.setLevel(newLevel);
        userRepository.save(user);

        // 检测升级
        if (newLevel > oldLevel) {
            UserLevel level = userLevelRepository.findByGrade(newLevel)
                .orElseThrow();
            // 发送升级通知 (RocketMQ异步)
            // rocketMQTemplate.convertAndSend("shop.topic.member", "member:upgrade", ...);
        }
    }

    private Integer calculateLevel(Integer exp) {
        List<UserLevel> levels = userLevelRepository.findAllOrderByGradeDesc();
        for (UserLevel level : levels) {
            if (exp >= level.getExperience()) {
                return level.getGrade();
            }
        }
        return 1;
    }
}
```

---

## 5. 分销/裂变体系

### 分销关系表

```java
@Entity
@Table(name = "agent")
@Data
public class Agent {

    @Id
    private Long userId;        // 分销员ID (复用userId作主键)
    private Long上级Id;         // 上级分销员ID
    private String agents;      // 链路: "1,2,3"  (自己id,上级id,上上级id
    private Integer price;      // 累计佣金 (单位: 分)
    private Integer freezePrice; // 冻结佣金
    private Integer status;     // 1待审核 2已通过 3已拒绝
}
```

### 分销佣金结算Service

```java
@Service
@RequiredArgsConstructor
public class DistributionService {

    private final AgentRepository agentRepository;
    private final UserRepository userRepository;
    private final PointService pointService;
    private final RedissonClient redissonClient;

    private static final BigDecimal[] COMMISSION_RATES = {
        BigDecimal.valueOf(0.10),  // 一级佣金 10%
        BigDecimal.valueOf(0.05),   // 二级佣金 5%
        BigDecimal.valueOf(0.02)   // 三级佣金 2%
    };

    /**
     * 订单完成后结算佣金 — 等价于 PHP AgentRepository::backOrderBrokerage()
     * 使用Redisson分布式锁防止重复结算
     */
    @Transactional
    public void settleOrderCommission(String orderSn, Long buyerId, BigDecimal orderPrice) {
        RLock lock = redissonClient.getLock("settle:commission:" + orderSn);
        try {
            if (!lock.tryLock(0, 10, TimeUnit.SECONDS)) {
                throw new BizException("结算中，请勿重复操作");
            }

            // 查找购买者的分销链路
            Agent agent = agentRepository.findById(buyerId).orElse(null);
            if (agent == null || agent.getStatus() != 2) {
                return; // 非分销员订单不结算
            }

            String[] agentIds = agent.getAgents().split(",");
            BigDecimal[] rates = COMMISSION_RATES;

            for (int i = 0; i < Math.min(agentIds.length, rates.length); i++) {
                Long agentId = Long.parseLong(agentIds[i]);
                if (agentId.equals(buyerId)) continue; // 不结算给自己

                BigDecimal commission = orderPrice.multiply(rates[i]);

                // 创建佣金冻结记录
                Brokeragefreeze freeze = new Brokeragefreeze();
                freeze.setUserId(buyerId);
                freeze.setAgentId(agentId);
                freeze.setPrice(commission.intValue());
                freeze.setOrderSn(orderSn);
                freeze.setStatus(1); // 1冻结中 2已解冻 3已退款
                freeze.setCreateTime(LocalDateTime.now());
                brokerageFreezeRepository.save(freeze);
            }
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }

    /**
     * 订单收货后解冻佣金 — 等价于 PHP AgentRepository::unfreeze()
     */
    @Transactional
    public void unfreezeCommission(String orderSn) {
        List<Brokeragefreeze> list = brokerageFreezeRepository.findByOrderSn(orderSn);
        for (Brokeragefreeze freeze : list) {
            if (freeze.getStatus() != 1) continue; // 非冻结状态跳过

            freeze.setStatus(2); // 已解冻
            freeze.setUnlockTime(LocalDateTime.now());
            brokerageFreezeRepository.save(freeze);

            // 增加分销员可提现佣金
            userRepository.addBrokerage(freeze.getAgentId(), freeze.getPrice());
        }
    }
}
```

---

## 6. 订单管理

### 订单表

```java
@Entity
@Table(name = "store_order")
@Data
public class StoreOrder {

    @Id
    private String orderId;        // 订单号 (雪花算法生成)
    private Long userId;
    private String realName;       // 收货人姓名
    private String phone;          // 收货人电话
    private String address;        // 收货地址
    private BigDecimal totalPrice; // 订单总价
    private BigDecimal payPrice;   // 实际支付
    private BigDecimal couponPrice;// 优惠券减免
    private BigDecimal commission;  // 佣金金额
    private Integer payType;       // 1微信 2支付宝 3余额
    private Integer status;        // -1已取消 0待支付 1待发货 2待收货 3已完成 4已退款
    private Integer deliveryType;  // 1快递 2到店 3同城配送
    private String deliveryId;     // 快递单号
    private String payTime;
    private String deliveryTime;
    private String receiveTime;
    private LocalDateTime createTime;
}
```

### 订单Service

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
    private final CouponService couponService;
    private final PointService pointService;
    private final DistributionService distributionService;

    /**
     * 创建订单 — 等价于 PHP StoreOrderRepository::createOrder()
     * 使用乐观锁防止重复提交
     */
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public StoreOrder createOrder(CreateOrderDTO dto) {
        // 1. 幂等校验
        String idempotentKey = "order:idempotent:" + dto.getUserId() + ":" + dto.getCartIds();
        if (!redisTemplate.opsForValue().setIfAbsent(idempotentKey, "1", 30, TimeUnit.MINUTES)) {
            throw new BizException("订单正在创建中，请勿重复提交");
        }

        try {
            // 2. 校验价格 (防篡改)
            List<CartItem> cartItems = cartService.getCartItems(dto.getCartIds());
            BigDecimal totalPrice = cartItems.stream()
                .map(CartItem::getTotalPrice)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

            // 3. 计算优惠券
            BigDecimal couponPrice = BigDecimal.ZERO;
            if (dto.getCouponId() != null) {
                couponPrice = couponService.calculateDiscount(dto.getUserId(), cartItems);
            }

            // 4. 生成订单
            StoreOrder order = new StoreOrder();
            order.setOrderId(IdUtil.getSnowflakeNextStr()); // 雪花算法订单号
            order.setUserId(dto.getUserId());
            order.setTotalPrice(totalPrice);
            order.setPayPrice(totalPrice.subtract(couponPrice));
            order.setCouponPrice(couponPrice);
            order.setStatus(0); // 待支付
            order.setCreateTime(LocalDateTime.now());

            StoreOrder saved = orderRepository.save(order);

            // 5. 发送RocketMQ延迟消息 (15分钟检查未支付自动取消)
            rocketMQTemplate.asyncSend("order.topic.delay",
                OrderDelayMessage.builder().orderId(saved.getOrderId()).build(),
                new MessageBuilder().withDelayTimeLevel(2).build());

            return saved;
        } finally {
            redisTemplate.delete(idempotentKey);
        }
    }

    /**
     * 订单支付成功回调
     */
    @Transactional
    public void paySuccess(String orderId) {
        StoreOrder order = orderRepository.findById(orderId)
            .orElseThrow(() -> new BizException("订单不存在"));

        order.setStatus(1); // 待发货
        order.setPayTime(LocalDateTime.now());
        orderRepository.save(order);

        // 发送RocketMQ: 扣减库存、赠送积分、计算佣金
        rocketMQTemplate.syncSend("order.topic.pay",
            OrderPayMessage.builder()
                .orderId(orderId)
                .userId(order.getUserId())
                .orderPrice(order.getPayPrice())
                .build());
    }
}
```

### 延迟消息消费 (订单超时取消)

```java
@Component
@RequiredArgsConstructor
public class OrderDelayConsumer {

    private final OrderRepository orderRepository;

    @RocketMQMessageListener(
        topic = "order.topic.delay",
        consumerGroup = "order-delay-consumer-group",
        delayLevel = 2  // 延迟级别: 2=5秒, 可配置更长时间
    )
    public void onDelayMessage(OrderDelayMessage msg) {
        StoreOrder order = orderRepository.findById(msg.getOrderId()).orElse(null);
        if (order != null && order.getStatus() == 0) {
            // 超时未支付，取消订单
            order.setStatus(-1);
            orderRepository.save(order);
            // 退还优惠券
            // couponUserRepository.updateStatus(order.getUserId(), order.getCouponId(), 0);
        }
    }
}
```

---

## 7. 支付集成

### 支付回调Controller

```java
@RestController
@RequestMapping("/api/pay")
@RequiredArgsConstructor
public class PaymentController {

    private final OrderService orderService;
    private final WechatPayTemplate wechatPayTemplate;

    /**
     * 微信支付下单
     */
    @PostMapping("/wechat")
    public Result<WechatPayResponse> wechatPay(@RequestBody PayRequest req,
                                                @RequestHeader("userId") Long userId) {
        StoreOrder order = orderService.getOrderById(req.getOrderId());
        WechatPayResponse response = wechatPayTemplate.unifiedOrder(
            WechatPayRequest.builder()
                .outTradeNo(order.getOrderId())
                .totalFee(order.getPayPrice().multiply(BigDecimal.valueOf(100)).intValue())
                .body("商品订单支付")
                .notifyUrl("https://api.example.com/pay/wechat/notify")
                .build()
        );
        return Result.ok(response);
    }

    /**
     * 微信支付回调
     */
    @PostMapping("/wechat/notify")
    public String wechatNotify(HttpServletRequest request) {
        try {
            // 1. 解析回调报文
            JSONObject json = wechatPayTemplate.parseNotify(request);
            String orderId = json.getString("out_trade_no");
            String transactionId = json.getString("transaction_id");

            // 2. 校验签名 (微信平台证书)
            // 3. 校验金额

            // 4. 订单支付成功
            orderService.paySuccess(orderId);

            return wechatPayTemplate.successReply(); // 返回SUCCESS
        } catch (Exception e) {
            return wechatPayTemplate.failReply();
        }
    }

    /**
     * 余额支付
     */
    @PostMapping("/balance")
    @Transactional
    public Result<Void> balancePay(@RequestBody PayRequest req,
                                    @RequestHeader("userId") Long userId) {
        StoreOrder order = orderService.getOrderById(req.getOrderId());

        // 扣减余额
        pointService.changePoint(userId,
            -order.getPayPrice().multiply(BigDecimal.valueOf(100)).intValue(),
            5, "余额支付订单 " + order.getOrderId());

        // 订单支付成功
        orderService.paySuccess(order.getOrderId());
        return Result.ok();
    }
}
```

### 微信支付模板 (简化实现)

```java
@Component
public class WechatPayTemplate {

    private final RedisTemplate<String, String> redisTemplate;

    private static final String WECHAT_PAY_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder";
    private static final String APP_ID = "wx...";
    private static final String MCH_ID = "...";

    public WechatPayResponse unifiedOrder(WechatPayRequest request) {
        // 1. 构建签名参数
        Map<String, String> params = new TreeMap<>();
        params.put("appid", APP_ID);
        params.put("mch_id", MCH_ID);
        params.put("nonce_str", IdUtil.fastSimpleUUID());
        params.put("out_trade_no", request.getOutTradeNo());
        params.put("total_fee", String.valueOf(request.getTotalFee()));
        params.put("body", request.getBody());
        params.put("notify_url", request.getNotifyUrl());
        params.put("trade_type", "NATIVE");

        // 2. 生成签名
        String sign = generateSign(params);
        params.put("sign", sign);

        // 3. 发送HTTP请求
        String xml = mapToXml(params);
        String response = HttpUtil.post(WECHAT_PAY_URL, xml);

        // 4. 解析返回
        Map<String, String> result = xmlToMap(response);
        if ("SUCCESS".equals(result.get("return_code")) {
            return WechatPayResponse.builder()
                .codeUrl(result.get("code_url"))
                .tradeNo(result.get("prepay_id"))
                .build();
        }
        throw new BizException("微信支付下单失败: " + result.get("return_msg"));
    }

    private String generateSign(Map<String, String> params) {
        String signStr = params.entrySet().stream()
            .map(e -> e.getKey() + "=" + e.getValue())
            .collect(Collectors.joining("&")) + "&key=" + API_KEY;
        return DigestUtil.md5Hex(signStr).toUpperCase();
    }
}
```

---

## 8. 物流与配送

### 物流Service

```java
@Service
@RequiredArgsConstructor
public class DeliveryService {

    private final OrderRepository orderRepository;
    private final RedisTemplate<String, String> redisTemplate;

    /**
     * 同步物流信息
     * 等价于 PHP DeliveryRepository::queryDelivery()
     */
    public DeliveryTrack queryDelivery(String deliveryId) {
        String cacheKey = "delivery:track:" + deliveryId;

        // 1. 缓存查询
        String cached = redisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {
            return JSON.parseObject(cached, DeliveryTrack.class);
        }

        // 2. 调用第三方快递API
        DeliveryTrack track = thirdPartyDeliveryApi.query(deliveryId);

        // 3. 缓存1小时
        redisTemplate.opsForValue().set(cacheKey, JSON.toJSONString(track), 1, TimeUnit.HOURS);
        return track;
    }

    /**
     * 批量发货
     */
    @Transactional
    public void batchDeliver(BatchDeliverDTO dto) {
        for (DeliverItem item : dto.getItems()) {
            StoreOrder order = orderRepository.findById(item.getOrderId())
                .orElseThrow(() -> new BizException("订单不存在: " + item.getOrderId()));

            if (order.getStatus() != 1) {
                continue; // 非待发货状态跳过
            }

            order.setStatus(2); // 待收货
            order.setDeliveryId(item.getDeliveryId());
            order.setDeliveryType(item.getDeliveryType());
            order.setDeliveryTime(LocalDateTime.now());
            orderRepository.save(order);

            // 发送发货通知 (极光/小米PUSH)
            // jPushTemplate.sendPush(pushPayload);
        }
    }
}
```

---

## 9. Spring Cloud Gateway路由注册

### 微服务架构

```
┌─────────────────────────────────────────┐
│           Spring Cloud Gateway           │
│        (统一入口 /api/* 路由)           │
└─────────┬───────────────────┬────────────┘
          │                   │
    ┌─────▼──────┐   ┌──────▼──────┐
    │ UserService │   │OrderService │
    │   :8081    │   │   :8082    │
    └─────────────┘   └─────────────┘
    ┌─────────────┐   ┌─────────────┐
    │PayService  │   │ShopService │
    │   :8083    │   │   :8084   │
    └─────────────┘   └─────────────┘
          │
    ┌─────▼─────────────┐
    │  Nacos Server   │
    │ (注册+配置中心) │
    └─────────────────┘
```

### Gateway配置 (YAML)

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/user/**
          filters:
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 100
                redis-rate-limiter.burstCapacity: 200

        - id: order-service
          uri: lb://order-service
          predicates:
            - Path=/api/order/**
          filters:
            - StripPrefix=1

        - id: pay-service
          uri: lb://pay-service
          predicates:
            - Path=/api/pay/**

  redis:
    host: 127.0.0.1
    port: 6379
    lettuce:
      pool:
        max-active: 20
        max-idle: 10
        min-idle: 5
```

### 服务注册发现 (Nacos)

```java
@SpringBootApplication
@EnableDiscoveryClient
public class OrderServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderServiceApplication.class, args);
    }
}
```

---

## 10. @Scheduled定时任务 + RocketMQ消息队列

### 定时任务配置

```java
@Configuration
@EnableScheduling
public class SchedulerConfig {
    // 默认单线程执行，订单量大的场景需配置线程池
    @Bean
    public TaskScheduler taskScheduler() {
        ThreadPoolTaskScheduler scheduler = new ThreadPoolTaskScheduler();
        scheduler.setPoolSize(10);
        scheduler.setThreadNamePrefix("scheduled-task-");
        scheduler.setWaitForTasksToCompleteOnShutdown(true);
        return scheduler;
    }
}
```

### 定时任务实现

```java
@Component
@RequiredArgsConstructor
public class EcommerceScheduledTasks {

    private final OrderRepository orderRepository;
    private final CouponRepository couponRepository;

    /**
     * 每日0点重置优惠券库存到Redis
     */
    @Scheduled(cron = "0 0 0 * * ?")
    public void resetCouponStock() {
        List<Coupon> coupons = couponRepository.findByStatus(2);
        for (Coupon coupon : coupons) {
            String stockKey = "coupon:stock:" + coupon.getId();
            // 使用Redis SETNX 原子初始化，避免重复设置
            // redisTemplate.opsForValue().setIfAbsent(stockKey, String.valueOf(coupon.getRemain()));
        }
    }

    /**
     * 每小时自动收货 (超时15天未收货)
     */
    @Scheduled(fixedRate = 3600000) // 1小时 = 3600000毫秒
    @Transactional
    public void autoReceiveOrder() {
        LocalDateTime threshold = LocalDateTime.now().minusDays(15);
        List<StoreOrder> orders = orderRepository.findByStatusAndDeliveryTimeBefore(2, threshold);

        for (StoreOrder order : orders) {
            order.setStatus(3); // 已完成
            order.setReceiveTime(LocalDateTime.now());
            orderRepository.save(order);

            // 触发佣金解冻 (RocketMQ)
            // rocketMQTemplate.syncSend("order.topic.receive", order.getOrderId());
        }
    }

    /**
     * 每月1号统计上月分销员佣金并生成报表
     */
    @Scheduled(cron = "0 0 1 1 * ?")
    public void generateCommissionReport() {
        // 读取上月的佣金冻结表，汇总各分销员佣金
    }
}
```

### RocketMQ消息生产与消费

```java
// 生产者: 订单Service
@RequiredArgsConstructor
public class OrderMQProducer {

    private final RocketMQTemplate rocketMQTemplate;

    public void sendPaySuccessMessage(StoreOrder order) {
        OrderMessage msg = OrderMessage.builder()
            .orderId(order.getOrderId())
            .userId(order.getUserId())
            .payPrice(order.getPayPrice())
            .build();

        // 发送事务消息 (半消息+本地事务+回查)
        TransactionSendResult result = rocketMQTemplate.sendMessageInTransaction(
            "order.topic.transaction",
            MessageBuilder.withPayload(msg).build(),
            new OrderTransactionListener(order.getOrderId())
        );
    }
}

// 消费者: 积分/佣金/库存
@Component
@RequiredArgsConstructor
public class OrderMessageConsumer {

    private final PointService pointService;
    private final DistributionService distributionService;
    private final ProductService productService;

    @RocketMQMessageListener(
        topic = "order.topic.pay",
        consumerGroup = "order-pay-consumer-group"
    )
    public void onPaySuccess(OrderMessage msg) {
        // 1. 扣减库存
        productService.deductStock(msg.getOrderId());

        // 2. 赠送积分
        pointService.givePointByOrder(msg.getUserId(), msg.getOrderId(), msg.getPayPrice());

        // 3. 结算佣金
        distributionService.settleOrderCommission(msg.getOrderId(), msg.getUserId(), msg.getPayPrice());
    }
}
```

---

## 11. 天龙岗位协同链路

### Java电商开发标准流程

```
用户需求
    ↓
[01调研师] 考古摸底: 阅读现有Java代码 + MySQL表结构
    ↓
[02架构师] 架构设计: Spring Cloud微服务拆分 + 数据库设计
    ↓
┌──────────┬──────────┬──────────┐
↓          ↓          ↓
[03构建师]  [03构建师]  [03构建师]  并行开发: UserService / OrderService / ShopService
│          │          │
└──────────┴──────────┴──────────┘
    ↓
[04验证师] 集成测试: Postman/E2E测试 + 压测
    ↓
[05安全师] 安全审查: SQL注入 + XSS + 接口鉴权
    ↓
[06审查师] 代码审查: JPA审计字段 + 事务隔离 + 并发安全
    ↓
[07发布师] 灰度发布: Argo Rollouts / Kubernetes滚动更新
```

### 各岗位关键检查点

| 岗位 | 检查点 | Java对应 |
|------|--------|---------|
| 01调研师 | MySQL表结构 + JPA实体映射 | @Entity/@Table注解校验 |
| 02架构师 | 微服务边界 + Nacos注册 | @EnableDiscoveryClient |
| 03构建师 | @Transactional + 乐观锁 | @Version注解 |
| 04验证师 | 并发压测 + Redis超卖 | Jmeter + Redis原子扣减 |
| 05安全师 | 接口鉴权 + 签名校验 | JWT + 签名算法 |
| 06审查师 | JPA审计字段 + 事务传播 | @CreatedDate/@ModifiedDate |
| 07发布师 | Docker镜像 + K8s探针 | readinessProbe/livenessProbe |

---

## 12. 常用命令速查

### Maven / Gradle 构建

```bash
# 编译
mvn clean compile

# 打包
mvn clean package -DskipTests

# 本地运行
mvn spring-boot:run

# 构建Docker镜像
mvn spring-boot:build-image

# 运行单元测试
mvn test

# 运行集成测试
mvn verify
```

### Docker Compose (本地开发环境)

```bash
# 启动全套开发环境
docker-compose -f docker-compose-dev.yml up -d

# 查看日志
docker-compose logs -f order-service

# 重启服务
docker-compose restart order-service

# 进入容器
docker exec -it order-service bash

# 常用开发镜像
# MySQL: docker run --name mysql -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 mysql:8.0
# Redis: docker run --name redis -p 6379:6379 redis:7-alpine
# Nacos: docker run --name nacos -p 8848:8848 nacos/nacos-server:v2.2.3
# RocketMQ: docker-compose -f rocketmq-docker-compose.yml up -d
```

### 数据库操作 (JPA/MyBatis-Plus)

```bash
# 生成JPA实体 (JHipster逆向工程)
jhipster import-jdl ./jdl/ecommerce.jdl

# MyBatis-Plus代码生成
java -cp mapper-generator.jar com.example.Generator

# 数据初始化
mysql -h127.0.0.1 -uroot -proot ecommerce < database/init.sql
```

### Kubernetes部署

```bash
# 构建并推送镜像
mvn spring-boot:build-image
docker tag ecommerce-order:latest registry.example.com/ecommerce-order:v1.0
docker push registry.example.com/ecommerce-order:v1.0

# 滚动更新
kubectl rollout restart deployment order-service -n ecommerce
kubectl rollout status deployment order-service -n ecommerce

# 查看Pod日志
kubectl logs -f deployment/order-service -n ecommerce

# 进入Pod调试
kubectl exec -it $(kubectl get pod -l app=order-service -n ecommerce -o name) -n ecommerce -- /bin/sh
```

### Redis常用操作

```bash
# 连接
redis-cli -h 127.0.0.1 -p 6379

# 查看优惠券库存
GET coupon:stock:1

# 查看用户积分
GET user:point:10001

# 手动初始化优惠券库存
SET coupon:stock:1 1000

# 查看分布式锁
KEYS "settle:commission:*"
```

### Spring Boot Actuator (健康检查)

```bash
# 健康检查
curl http://localhost:8081/actuator/health

# 查看环境变量
curl http://localhost:8081/actuator/env

# 刷新配置 (配合@RefreshScope)
curl -X POST http://localhost:8081/actuator/refresh

# 追踪调用链
curl http://localhost:8081/actuator/httptrace
```

### 性能分析

```bash
# Arthas (线上诊断)
java -jar arthas-boot.jar
# 连接后: dashboard / thread / stack / trace

# JMX监控
jconsole pid

# GC日志分析
-verbose:gc -Xloggc:gc.log -XX:+PrintGCDetails
```
