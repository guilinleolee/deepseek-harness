---
license: UNKNOWN
---

# CRMEB电商运营模式 SKILL.md

## L0: 一句话描述 (≤15字)
CRMEB电商全链路运营模式速查手册

## L1: 使用场景 (50-100字)
适用场景：电商平台营销活动配置、优惠券/满减/拼团/秒杀等活动搭建、积分/会员/分销体系设计、订单/支付/物流全流程开发。触发关键词：CRMEB电商、商城运营、营销活动配置。

## L2: 详细文档

### 一、CRMEB技术栈速查

```
┌─────────────────────────────────────────────────────────────┐
│ CRMEB技术栈                                              │
├─────────────────────────────────────────────────────────────┤
│ 后端框架: ThinkPHP 6 v7.1-7.4                          │
│ 异步服务: Workerman / Swoole                            │
│ 前端技术: Vue.js (Admin) + H5/小程序/APP             │
│ 数据库: MySQL 5.7-8.0                                   │
│ 缓存: Redis 7.0                                        │
│ 消息队列: Redis Queue / RabbitMQ                        │
│ 部署: Docker Compose                                   │
└─────────────────────────────────────────────────────────────┘
```

### 二、营销活动体系

#### 2.1 优惠券/满减券

**数据库表结构**:
```sql
-- 优惠券表
CREATE TABLE `eb_store_coupon` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL DEFAULT '' COMMENT '优惠券名称',
  `coupon_type` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1满减券 2折扣券',
  `money` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT '优惠金额/折扣率',
  `min_price` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT '最低消费金额',
  `coupon_price` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT '优惠券面值',
  `start_time` int(11) NOT NULL DEFAULT 0 COMMENT '开始时间',
  `end_time` int(11) NOT NULL DEFAULT 0 COMMENT '结束时间',
  `total_count` int(11) NOT NULL DEFAULT 0 COMMENT '发放总数',
  `remain_count` int(11) NOT NULL DEFAULT 0 COMMENT '剩余数量',
  `is_limit` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否限量 1不限 2限量',
  `limit_count` int(11) NOT NULL DEFAULT 1 COMMENT '限领数量',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1正常 2未开启 3已失效',
  `add_time` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 用户领取记录表
CREATE TABLE `eb_store_coupon_user` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL DEFAULT 0 COMMENT '用户ID',
  `cid` int(11) NOT NULL DEFAULT 0 COMMENT '优惠券ID',
  `coupon_id` int(11) NOT NULL DEFAULT 0 COMMENT '同cid冗余',
  `add_time` int(11) NOT NULL DEFAULT 0,
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1未使用 2已使用 3已过期',
  `use_time` int(11) NOT NULL DEFAULT 0 COMMENT '使用时间',
  `order_id` int(11) NOT NULL DEFAULT 0 COMMENT '使用订单ID',
  PRIMARY KEY (`id`),
  KEY `uid` (`uid`),
  KEY `cid` (`cid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**Service层核心代码**:
```php
<?php
// app/common/repositories/store/coupon/CouponRepository.php
declare(strict_types=1);

namespace app\common\repositories\store\coupon;

use app\common\repositories\BaseRepository;
use app\common\dao\store\coupon\CouponDao;
use app\common\dao\store\coupon\CouponUserDao;
use app\services\order\OrderServices;
use app\interfaces\coupon\CouponValidateInterface;

class CouponRepository extends BaseRepository
{
    protected CouponDao $couponDao;
    protected CouponUserDao $couponUserDao;

    public function __construct(CouponDao $couponDao, CouponUserDao $couponUserDao)
    {
        $this->couponDao = $couponDao;
        $this->couponUserDao = $couponUserDao;
    }

    /**
     * 校验优惠券是否可用
     */
    public function validateCoupon(int $uid, int $couponId, float $orderPrice): CouponValidateInterface
    {
        $coupon = $this->couponDao->get($couponId);
        if (!$coupon) {
            throw new ApiException(10001, '优惠券不存在');
        }

        // 状态校验
        if ($coupon->status != 1) {
            throw new ApiException(10002, '优惠券未开启或已失效');
        }

        // 时间校验
        $now = time();
        if ($coupon->start_time > $now) {
            throw new ApiException(10003, '优惠券活动未开始');
        }
        if ($coupon->end_time < $now) {
            throw new ApiException(10004, '优惠券已过期');
        }

        // 库存校验
        if ($coupon->is_limit == 2 && $coupon->remain_count <= 0) {
            throw new ApiException(10005, '优惠券已领完');
        }

        // 用户领取记录校验
        $userCoupon = $this->couponUserDao->getUserCoupon($uid, $couponId);
        if (!$userCoupon) {
            throw new ApiException(10006, '您还未领取该优惠券');
        }
        if ($userCoupon->status != 1) {
            throw new ApiException(10007, '该优惠券已使用或已过期');
        }

        // 金额门槛校验
        if ($orderPrice < $coupon->min_price) {
            throw new ApiException(10008, '订单金额未达优惠券使用门槛');
        }

        return new CouponValidateResult($coupon, $userCoupon);
    }

    /**
     * 领取优惠券
     */
    public function receiveCoupon(int $uid, int $couponId): bool
    {
        $coupon = $this->couponDao->get($couponId);
        if (!$coupon) {
            throw new ApiException(10001, '优惠券不存在');
        }

        // 检查限领数量
        $receivedCount = $this->couponUserDao->getUserReceivedCount($uid, $couponId);
        if ($receivedCount >= $coupon->limit_count) {
            throw new ApiException(10009, '该优惠券每人限领' . $coupon->limit_count . '张');
        }

        // 限量检查
        if ($coupon->is_limit == 2 && $coupon->remain_count <= 0) {
            throw new ApiException(10005, '优惠券已领完');
        }

        // 开启事务
        return $this->transaction(function () use ($uid, $couponId, $coupon) {
            // 减少库存
            if ($coupon->is_limit == 2) {
                $this->couponDao->decRemainCount($couponId);
            }
            // 创建领取记录
            $this->couponUserDao->create([
                'uid' => $uid,
                'cid' => $couponId,
                'coupon_id' => $couponId,
                'add_time' => time(),
                'status' => 1,
            ]);
            return true;
        });
    }

    /**
     * 计算订单优惠金额（满减券）
     */
    public function calculateDiscount(float $orderPrice, object $coupon): float
    {
        if ($coupon->coupon_type == 1) {
            // 满减券：直接返回面值，但不超过订单金额
            return min(bcsub((string)$orderPrice, '0.01', 2), $coupon->money);
        } else {
            // 折扣券：按折扣率计算
            $discount = bcmul((string)$orderPrice, bcdiv((string)$coupon->money, '100', 4), 2);
            return min($discount, bcsub((string)$orderPrice, '0.01', 2));
        }
    }
}

class CouponValidateResult implements CouponValidateInterface
{
    public function __construct(public object $coupon, public object $userCoupon) {}
    public function getDiscount(float $orderPrice): float
    {
        return app()->make(CouponRepository::class)->calculateDiscount($orderPrice, $this->coupon);
    }
}
```

**Controller层**:
```php
<?php
// app/adminapi/v1/marketing/CouponController.php
declare(strict_types=1);

namespace app\adminapi\v1\marketing;

use app\adminapi\lists\marketing\CouponLists;
use app\adminapi\requests\marketing\CouponRequest;
use app\common\repositories\store\coupon\CouponRepository;
use crmeb\services\FormBuilder;
use builderapolis\BaseAdminController;

class CouponController extends BaseAdminController
{
    protected CouponRepository $repository;

    public function __construct(CouponRepository $repository)
    {
        $this->repository = $repository;
    }

    /**
     * 优惠券列表
     */
    public function index(): array
    {
        return app(CouponLists::class)->selectList($this->request->params([
            'title', 'status', 'coupon_type', 'dateRange'
        ]));
    }

    /**
     * 创建优惠券表单
     */
    public function create(): array
    {
        $form = FormBuilder::create([
            FormBuilder::input('title', '优惠券名称', '')->required(),
            FormBuilder::select('coupon_type', '券类型', 1)
                ->setOptions([
                    ['value' => 1, 'label' => '满减券'],
                    ['value' => 2, 'label' => '折扣券'],
                ]),
            FormBuilder::number('coupon_price', '优惠金额/折扣率', 0)->min(0)->required(),
            FormBuilder::number('min_price', '最低消费金额', 0)->min(0)->required(),
            FormBuilder::dateTimeRange('search_time', '活动时间')->required(),
            FormBuilder::number('total_count', '发放总量', 0)->min(0),
            FormBuilder::number('remain_count', '剩余数量', 0)->min(0),
            FormBuilder::number('limit_count', '限领数量', 1)->min(1),
            FormBuilder::radio('is_limit', '是否限量', 1)
                ->setOptions([
                    ['value' => 1, 'label' => '不限量'],
                    ['value' => 2, 'label' => '限量'],
                ]),
            FormBuilder::radio('status', '状态', 1)
                ->setOptions([
                    ['value' => 1, 'label' => '正常'],
                    ['value' => 2, 'label' => '未开启'],
                ]),
        ])->setTitle('创建优惠券');

        return $form->build();
    }

    /**
     * 保存优惠券
     */
    public function save(CouponRequest $request): array
    {
        $data = $request->post();
        $data['add_time'] = time();
        $data['remain_count'] = $data['total_count'] ?? 0;
        $coupon = $this->repository->create($data);

        return ['id' => $coupon->id];
    }

    /**
     * 核销优惠券
     */
    public function verify(string $couponId): array
    {
        $couponUser = $this->repository->getCouponUserInfo((int)$couponId);
        if (!$couponUser) {
            throw new ApiException(10010, '优惠券记录不存在');
        }
        if ($couponUser->status != 1) {
            throw new ApiException(10011, '优惠券状态不可用');
        }

        $this->repository->useCoupon($couponUser->uid, $couponUser->id, $couponUser->order_id);
        return ['id' => $couponUser->id];
    }
}
```

#### 2.2 拼团/团购

**数据库表结构**:
```sql
-- 拼团活动表
CREATE TABLE `eb_store_combination` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL DEFAULT 0 COMMENT '商品ID',
  `title` varchar(255) NOT NULL DEFAULT '' COMMENT '活动标题',
  `people` int(11) NOT NULL DEFAULT 2 COMMENT '拼团人数',
  `price` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT '拼团价格',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态 1开启 2关闭',
  `start_time` int(11) NOT NULL DEFAULT 0,
  `end_time` int(11) NOT NULL DEFAULT 0,
  `stock` int(11) NOT NULL DEFAULT 0 COMMENT '活动库存',
  `sold_count` int(11) NOT NULL DEFAULT 0 COMMENT '已售数量',
  `browse` int(11) NOT NULL DEFAULT 0 COMMENT '浏览量',
  `add_time` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 拼团记录表
CREATE TABLE `eb_store_combination_order` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `combination_id` int(11) NOT NULL DEFAULT 0 COMMENT '拼团活动ID',
  `order_id` int(11) NOT NULL DEFAULT 0 COMMENT '订单ID',
  `uid` int(11) NOT NULL DEFAULT 0 COMMENT '用户ID',
  `nickname` varchar(64) NOT NULL DEFAULT '' COMMENT '用户昵称',
  `people` int(11) NOT NULL DEFAULT 2 COMMENT '拼团人数',
  `price` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT '拼团价',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1进行中 2拼团成功 3拼团失败',
  `is_founder` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1团长 2团员',
  `stop_time` int(11) NOT NULL DEFAULT 0 COMMENT '结束时间',
  `add_time` int(11) NOT NULL DEFAULT 0,
  `take_count` int(11) NOT NULL DEFAULT 0 COMMENT '已参与人数',
  PRIMARY KEY (`id`),
  KEY `combination_id` (`combination_id`),
  KEY `uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**拼团Service核心逻辑**:
```php
<?php
// app/common/repositories/store/combination/CombinationRepository.php
declare(strict_types=1);

namespace app\common\repositories\store\combination;

use app\common\repositories\BaseRepository;
use app\common\dao\store\combination\CombinationDao;
use app\common\dao\store\combination\CombinationOrderDao;

class CombinationRepository extends BaseRepository
{
    protected CombinationDao $combinationDao;
    protected CombinationOrderDao $combinationOrderDao;

    /**
     * 开团
     */
    public function openCombination(int $uid, int $combinationId, int $orderId): object
    {
        $combination = $this->combinationDao->get($combinationId);
        if (!$combination || $combination->status != 1) {
            throw new ApiException(20001, '拼团活动不存在或已关闭');
        }

        $now = time();
        if ($combination->start_time > $now || $combination->end_time < $now) {
            throw new ApiException(20002, '拼团活动未开始或已结束');
        }

        if ($combination->stock <= 0) {
            throw new ApiException(20003, '拼团库存不足');
        }

        return $this->transaction(function () use ($uid, $combination, $orderId) {
            // 减少活动库存
            $this->combinationDao->decStock($combination->id);
            $this->combinationDao->incSoldCount($combination->id);

            // 创建拼团记录（团长）
            return $this->combinationOrderDao->create([
                'combination_id' => $combination->id,
                'order_id' => $orderId,
                'uid' => $uid,
                'people' => $combination->people,
                'price' => $combination->price,
                'status' => 1,
                'is_founder' => 1,
                'stop_time' => time() + (24 * 3600), // 24小时过期
                'add_time' => time(),
                'take_count' => 1,
            ]);
        });
    }

    /**
     * 参团
     */
    public function joinCombination(int $uid, int $combinationOrderId, int $orderId): object
    {
        $combinationOrder = $this->combinationOrderDao->get($combinationOrderId);

        if (!$combinationOrder || $combinationOrder->status != 1) {
            throw new ApiException(20004, '拼团不存在或已结束');
        }

        if ($combinationOrder->stop_time < time()) {
            throw new ApiException(20005, '拼团已过期');
        }

        // 检查是否已参加过此团
        $exists = $this->combinationOrderDao->existsByUidAndOrderId($combinationOrderId, $uid);
        if ($exists) {
            throw new ApiException(20006, '您已参与此拼团');
        }

        return $this->transaction(function () use ($uid, $combinationOrder, $orderId) {
            // 更新参团人数
            $this->combinationOrderDao->incTakeCount($combinationOrder->id);

            // 创建参团记录（团员）
            $order = $this->combinationOrderDao->create([
                'combination_id' => $combinationOrder->combination_id,
                'order_id' => $orderId,
                'uid' => $uid,
                'people' => $combinationOrder->people,
                'price' => $combinationOrder->price,
                'status' => 1,
                'is_founder' => 2,
                'stop_time' => $combinationOrder->stop_time,
                'add_time' => time(),
                'take_count' => 1,
            ]);

            // 检查是否成团
            $this->checkCombinationSuccess($combinationOrder->id);

            return $order;
        });
    }

    /**
     * 检查拼团是否成功
     */
    protected function checkCombinationSuccess(int $combinationOrderId): void
    {
        $combinationOrder = $this->combinationOrderDao->get($combinationOrderId);
        $allOrders = $this->combinationOrderDao->getByCombinationId($combinationOrder->combination_id);

        $totalPeople = array_sum(array_column($allOrders, 'take_count'));

        if ($totalPeople >= $combinationOrder->people) {
            // 成团成功
            foreach ($allOrders as $order) {
                $this->combinationOrderDao->update($order->id, ['status' => 2]);
                // 触发订单支付成功（后续发货流程）
                event('OrderPaySuccess', $order->order_id);
            }
        }
    }

    /**
     * 关闭超时未成团的订单
     */
    public function closeTimeoutCombination(): int
    {
        $list = $this->combinationOrderDao->getExpiredList(time());
        $count = 0;
        foreach ($list as $item) {
            $this->transaction(function () use ($item) {
                $this->combinationOrderDao->update($item->id, ['status' => 3]);
                // 退款逻辑
                app()->make(OrderRefundServices::class)->refund($item->order_id, '拼团超时自动退款');
                // 恢复库存
                $this->combinationDao->incStock($item->combination_id);
            });
            $count++;
        }
        return $count;
    }
}
```

#### 2.3 秒杀/限时折扣

```php
<?php
// app/common/repositories/store/seckill/SeckillRepository.php
declare(strict_types=1);

namespace app\common\repositories\store\seckill;

class SeckillRepository extends BaseRepository
{
    /**
     * 秒杀价格计算（基于Redis原子操作防超卖）
     */
    public function flashPurchase(int $uid, int $seckillId, int $productId, int $count): array
    {
        $seckill = $this->getSeckillInfo($seckillId, $productId);
        $now = time();

        // 时间窗口校验
        if ($now < $seckill['start_time'] || $now > $seckill['end_time']) {
            throw new ApiException(30001, '秒杀活动未开始或已结束');
        }

        // Redis原子扣库存（Lua脚本保证原子性）
        $redis = app()->redis;
        $stockKey = "seckill:{$seckillId}:{$productId}:stock";
        $userKey = "seckill:{$seckillId}:{$productId}:uid:{$uid}";

        // Lua脚本：原子扣库存+限购检查
        $script = <<<'LUA'
local stock = redis.call('GET', KEYS[1])
if not stock then return -1 end
if tonumber(stock) < tonumber(ARGV[1]) then return -2 end

local limit = redis.call('GET', KEYS[2])
if limit then
    if tonumber(limit) + tonumber(ARGV[1]) > tonumber(ARGV[2]) then
        return -3
    end
end

redis.call('DECRBY', KEYS[1], ARGV[1])
redis.call('INCRBY', KEYS[2], ARGV[1])
return 1
LUA;

        $result = $redis->eval($script, 2, $stockKey, $userKey, $count, $seckill['buy_limit']);

        if ($result == -1) {
            throw new ApiException(30002, '库存信息不存在');
        }
        if ($result == -2) {
            throw new ApiException(30003, '库存不足');
        }
        if ($result == -3) {
            throw new ApiException(30004, '超出限购数量');
        }

        return [
            'seckill_price' => $seckill['price'],
            'count' => $count,
            'total' => bcmul($seckill['price'], (string)$count, 2),
        ];
    }

    /**
     * 预热秒杀：将库存写入Redis
     */
    public function preloadSeckill(int $seckillId): void
    {
        $list = $this->seckillProductDao->getAllBySeckillId($seckillId);
        $redis = app()->redis;

        foreach ($list as $item) {
            $stockKey = "seckill:{$seckillId}:{$item->product_id}:stock";
            $redis->set($stockKey, $item->stock);
        }
    }
}
```

### 三、积分体系

```sql
-- 积分记录表
CREATE TABLE `eb_user_point` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL DEFAULT 0 COMMENT '用户ID',
  `point` int(11) NOT NULL DEFAULT 0 COMMENT '积分变动（正负）',
  `balance` int(11) NOT NULL DEFAULT 0 COMMENT '变动后余额',
  `type` varchar(32) NOT NULL DEFAULT '' COMMENT '类型: order/gift/sign/recharge/refund',
  `mark` varchar(255) NOT NULL DEFAULT '' COMMENT '说明',
  `order_id` int(11) NOT NULL DEFAULT 0 COMMENT '关联订单ID',
  `add_time` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `uid` (`uid`),
  KEY `add_time` (`add_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

```php
<?php
// app/common/repositories/store/user/UserPointRepository.php
declare(strict_types=1);

namespace app\common\repositories\store\user;

class UserPointRepository extends BaseRepository
{
    /**
     * 积分变动（原子操作）
     */
    public function changePoint(int $uid, int $point, string $type, string $mark = '', int $orderId = 0): void
    {
        // 乐观锁：检查余额
        $user = $this->userDao->get($uid);
        if ($point < 0 && $user->point + $point < 0) {
            throw new ApiException(40001, '积分不足');
        }

        $this->transaction(function () use ($uid, $point, $user, $type, $mark, $orderId) {
            // 更新用户积分
            $this->userDao->incPoint($uid, $point);
            // 记录流水
            $this->pointDao->create([
                'uid' => $uid,
                'point' => $point,
                'balance' => $user->point + $point,
                'type' => $type,
                'mark' => $mark,
                'order_id' => $orderId,
                'add_time' => time(),
            ]);
            // 触发积分变动事件
            event('UserPointChanged', ['uid' => $uid, 'point' => $point, 'type' => $type]);
        });
    }

    /**
     * 订单完成送积分（1元=1积分）
     */
    public function orderGivePoint(int $uid, float $orderPrice, int $orderId): void
    {
        $point = (int)floor($orderPrice); // 1:1比例
        $this->changePoint($uid, $point, 'order', "订单完成赠送积分", $orderId);
    }

    /**
     * 积分抵钱：100积分=1元
     */
    public function pointToMoney(int $point): float
    {
        return bcdiv((string)$point, '100', 2);
    }
}
```

### 四、会员体系与成长值

```sql
-- 会员等级表
CREATE TABLE `eb_user_level` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL DEFAULT '' COMMENT '等级名称',
  `growth_num` int(11) NOT NULL DEFAULT 0 COMMENT '所需成长值',
  `discount` decimal(4,2) NOT NULL DEFAULT 100.00 COMMENT '会员折扣率',
  `image` varchar(255) NOT NULL DEFAULT '' COMMENT '等级图标',
  `sort` int(11) NOT NULL DEFAULT 0 COMMENT '排序',
  `is_show` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否展示',
  `add_time` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

```php
<?php
// app/common/repositories/store/user/UserLevelRepository.php
declare(strict_types=1);

namespace app\common\repositories\store\user;

class UserLevelRepository extends BaseRepository
{
    /**
     * 成长值变动后检查是否升级
     */
    public function checkLevelUp(int $uid): ?object
    {
        $user = $this->userDao->get($uid);
        $levels = $this->levelDao->getAllLevels(); // 排序后的等级列表

        foreach ($levels as $level) {
            if ($user->growth >= $level->growth_num) {
                if ($user->level_id != $level->id) {
                    $this->userDao->update($uid, ['level_id' => $level->id]);
                    // 触发升级事件
                    event('UserLevelUp', ['uid' => $uid, 'level' => $level]);
                    return $level;
                }
            }
        }
        return null;
    }

    /**
     * 成长值来源配置
     */
    public function getGrowthRule(string $type): int
    {
        $rules = [
            'order_pay' => 1,    // 每消费1元 = 1成长值
            'order_complete' => 2, // 订单完成额外 = 2成长值
            'sign' => 5,         // 签到 = 5成长值
            'comment' => 3,      // 评价 = 3成长值
        ];
        return $rules[$type] ?? 0;
    }
}
```

### 五、分销/裂变体系

```sql
-- 分销关系表
CREATE TABLE `eb_user_agent` (
  `uid` int(11) unsigned NOT NULL,
  `agent_id` int(11) NOT NULL DEFAULT 0 COMMENT '上级推广人ID',
  `agent_time` int(11) NOT NULL DEFAULT 0 COMMENT '绑定时间',
  `spread` int(11) NOT NULL DEFAULT 0 COMMENT '下级人数',
  `order_count` int(11) NOT NULL DEFAULT 0 COMMENT '订单数',
  `order_price` decimal(12,2) NOT NULL DEFAULT 0.00 COMMENT '订单金额',
  `promotion_time` int(11) NOT NULL DEFAULT 0 COMMENT '成为推广员时间',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1正常 2冻结',
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 分销提现表
CREATE TABLE `eb_store_extract` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL DEFAULT 0 COMMENT '用户ID',
  `extract_number` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT '提现金额',
  `extract_type` varchar(32) NOT NULL DEFAULT '' COMMENT 'bank/alipay/wechat',
  `bank_name` varchar(64) NOT NULL DEFAULT '' COMMENT '开户行',
  `bank_card` varchar(32) NOT NULL DEFAULT '' COMMENT '银行卡号',
  `alipay_account` varchar(64) NOT NULL DEFAULT '' COMMENT '支付宝账号',
  `real_name` varchar(32) NOT NULL DEFAULT '' COMMENT '真实姓名',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1待审核 2已通过 3已拒绝',
  `fail_msg` varchar(255) NOT NULL DEFAULT '' COMMENT '拒绝原因',
  `add_time` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

```php
<?php
// app/common/repositories/store/agent/AgentRepository.php
declare(strict_types=1);

namespace app\common\repositories\store\agent;

class AgentRepository extends BaseRepository
{
    /**
     * 分销佣金结算（订单完成后触发）
     */
    public function settleCommission(int $uid, int $orderId, float $orderPrice): void
    {
        $user = $this->userAgentDao->get($uid);
        if (!$user || $user->status != 1) return; // 非推广员不结算

        $commission = $this->calculateCommission($uid, $orderPrice);
        foreach ($commission as $level => $amount) {
            if ($amount <= 0) continue;

            $this->commissionDao->create([
                'uid' => $uid,
                'order_id' => $orderId,
                'brokerage_price' => $amount,
                'price' => $orderPrice,
                'level' => $level,
                'add_time' => time(),
                'status' => 1,
            ]);
            // 给上级返佣
            $this->sendBrokerageToParent($user->agent_id, $amount, $level);
        }
    }

    /**
     * 计算分销佣金（三级返佣）
     */
    protected function calculateCommission(int $uid, float $orderPrice): array
    {
        // 从配置或商品维度获取返佣比例
        $rate = app()->make(SystemConfigRepository::class)->get('agent_spread_commission', [
            1 => 0.1,   // 一级 10%
            2 => 0.05,  // 二级 5%
            3 => 0.03,  // 三级 3%
        ]);

        return [
            1 => bcmul((string)$orderPrice, (string)($rate[1] ?? 0), 2),
            2 => bcmul((string)$orderPrice, (string)($rate[2] ?? 0), 2),
            3 => bcmul((string)$orderPrice, (string)($rate[3] ?? 0), 2),
        ];
    }

    /**
     * 递归向上级发放佣金
     */
    protected function sendBrokerageToParent(int $agentId, float $amount, int $level): void
    {
        if ($agentId <= 0 || $level > 3) return;

        $parent = $this->userAgentDao->get($agentId);
        if (!$parent || $parent->status != 1) return;

        $this->commissionDao->create([
            'uid' => $parent->uid,
            'brokerage_price' => $amount,
            'level' => $level,
            'status' => 1,
            'add_time' => time(),
        ]);
        $this->userDao->incBrokerage($parent->uid, $amount);

        // 递归二级、三级
        $this->sendBrokerageToParent($parent->agent_id, $amount * 0.5, $level + 1);
    }
}
```

### 六、订单管理

```php
<?php
// app/common/repositories/store/order/StoreOrderRepository.php
declare(strict_types=1);

namespace app\common\repositories\store\order;

class StoreOrderRepository extends BaseRepository
{
    protected OrderDao $orderDao;
    protected OrderServices $orderServices;

    /**
     * 创建订单（含优惠计算）
     */
    public function createOrder(int $uid, array $cartIds, int $couponId = 0): object
    {
        $userInfo = $this->userDao->get($uid);
        $cartList = $this->cartDao->getCartList($uid, $cartIds);

        // 计算商品总价
        $totalPrice = array_sum(array_column($cartList, 'truePrice'));
        $totalNum = array_sum(array_column($cartList, 'cart_num'));

        $discountPrice = 0.00;
        $couponData = null;

        // 优惠券抵扣
        if ($couponId > 0) {
            $couponResult = app()->make(CouponRepository::class)
                ->validateCoupon($uid, $couponId, $totalPrice);
            $discountPrice = $couponResult->getDiscount($totalPrice);
            $couponData = [
                'coupon_id' => $couponId,
                'coupon_price' => $discountPrice,
            ];
        }

        // 会员折扣
        $memberDiscount = $this->calculateMemberDiscount($userInfo, $totalPrice);

        // 运费计算
        $freightPrice = $this->calculateFreight($cartList);

        // 实付金额
        $payPrice = bcsub(bcsub($totalPrice, $discountPrice, 2), $memberDiscount, 2);
        $payPrice = bcadd($payPrice, $freightPrice, 2);

        return $this->transaction(function () use ($uid, $cartList, $totalPrice, $discountPrice, $memberDiscount, $freightPrice, $payPrice, $couponData) {
            // 生成订单号
            $orderId = $this->generateOrderId();
            $orderData = [
                'order_id' => $orderId,
                'uid' => $uid,
                'total_price' => $totalPrice,
                'total_num' => count($cartList),
                'coupon_price' => $couponData['coupon_price'] ?? 0.00,
                'member_price' => $memberDiscount,
                'freight_price' => $freightPrice,
                'pay_price' => max($payPrice, 0.01),
                'paid' => 0,
                'status' => 0,
                'add_time' => time(),
            ];

            $order = $this->orderDao->create($orderData);
            $this->createOrderProduct($order->id, $cartList);
            $this->cartDao->deleteCart($uid, array_column($cartList, 'id'));

            return $order;
        });
    }

    /**
     * 订单号生成
     */
    protected function generateOrderId(): string
    {
        return date('YmdHis') . mt_rand(100000, 999999);
    }

    /**
     * 会员折扣
     */
    protected function calculateMemberDiscount(object $userInfo, float $totalPrice): float
    {
        $level = $this->userLevelDao->get($userInfo->level_id);
        if (!$level || $level->discount >= 100) return 0.00;

        $discount = bcsub('100', (string)$level->discount, 2);
        return bcmul($totalPrice, bcdiv($discount, '100', 4), 2);
    }
}
```

### 七、支付集成

```php
<?php
// app/services/pay/PayServices.php
declare(strict_types=1);

namespace app\services\pay;

use app\common\services\Pay\PayFactory;

class PayServices
{
    /**
     * 发起支付
     */
    public function pay(string $payType, int $orderId, float $totalFee, string $body = '商品订单'): array
    {
        $order = $this->orderDao->get($orderId);
        if ($order->paid == 1) {
            throw new ApiException(50001, '订单已支付');
        }

        $notifyUrl = sys_config('site_url') . '/api/notify/' . $payType;

        return match ($payType) {
            'wechat' => $this->wechatPay($order, $notifyUrl),
            'alipay' => $this->alipayPay($order, $notifyUrl),
            'yue' => $this->balancePay($order),
            default => throw new ApiException(50002, '不支持的支付方式'),
        };
    }

    /**
     * 微信支付
     */
    protected function wechatPay(object $order, string $notifyUrl): array
    {
        $config = [
            'appid' => sys_config('wechat_appid'),
            'mchid' => sys_config('wechat_mchid'),
            'serial_no' => sys_config('wechat_serial_no'),
            'private_key' => sys_config('wechat_private_key'),
        ];

        $pay = PayFactory::create('wechat', $config);

        return $pay->order([
            'out_trade_no' => $order->order_id,
            'description' => '商品订单',
            'amount' => [
                'total' => (int)bcmul((string)$order->pay_price, '100', 0),
                'currency' => 'CNY',
            ],
            'notify_url' => $notifyUrl,
        ]);
    }

    /**
     * 余额支付
     */
    protected function balancePay(object $order): array
    {
        $user = $this->userDao->get($order->uid);

        if (bccomp($user->now_money, $order->pay_price, 2) < 0) {
            throw new ApiException(50003, '余额不足');
        }

        // 原子扣余额
        $this->userDao->decNowMoney($order->uid, $order->pay_price);

        // 触发支付成功
        $this->orderPaidSuccess($order->id);

        return ['type' => 'yue', 'status' => 'paid'];
    }

    /**
     * 支付回调处理
     */
    public function notify(string $payType, array $data): void
    {
        match ($payType) {
            'wechat' => $this->wechatNotify($data),
            'alipay' => $this->alipayNotify($data),
        };
    }

    protected function wechatNotify(array $data): void
    {
        $orderId = $data['out_trade_no'];
        $order = $this->orderDao->getByOrderId($orderId);

        if ($order && $order->paid == 0) {
            $this->transaction(function () use ($order) {
                $this->orderDao->update($order->id, [
                    'paid' => 1,
                    'pay_time' => time(),
                    'transaction_id' => $data['transaction_id'] ?? '',
                ]);
                $this->orderPaidSuccess($order->id);
            });
        }
    }

    /**
     * 支付成功后续处理
     */
    protected function orderPaidSuccess(int $orderId): void
    {
        $order = $this->orderDao->get($orderId);

        // 1. 送积分
        app()->make(UserPointRepository::class)->orderGivePoint(
            $order->uid, $order->total_price, $order->id
        );

        // 2. 会员成长值
        app()->make(UserLevelRepository::class)->changeGrowth(
            $order->uid, 'order_complete', $order->total_price
        );

        // 3. 分销佣金结算
        app()->make(AgentRepository::class)->settleCommission(
            $order->uid, $order->id, $order->total_price
        );

        // 4. 优惠券使用
        if ($order->coupon_id > 0) {
            app()->make(CouponRepository::class)->useCoupon(
                $order->uid, $order->coupon_id, $order->id
            );
        }

        // 5. 事件通知
        event('OrderPaid', $order);
    }
}
```

### 八、物流与配送

```php
<?php
// app/common/repositories/store/delivery/DeliveryRepository.php
declare(strict_types=1);

namespace app\common\repositories\store\delivery;

class DeliveryRepository extends BaseRepository
{
    /**
     * 电子面单打印
     */
    public function createExpressSheet(int $orderId, string $expressCode): array
    {
        $order = $this->orderDao->get($orderId);
        $address = $this->orderAddressDao->getByOrderId($orderId);

        $config = $this->getExpressConfig($expressCode);

        return match ($expressCode) {
            'sf' => $this->sfCreateOrder($config, $order, $address),
            'jd' => $this->jdCreateOrder($config, $order, $address),
            default => $this->kuaidi100CreateOrder($config, $order, $address),
        };
    }

    /**
     * 物流轨迹订阅（推送模式）
     */
    public function subscribeTraces(string $expressCode, string $expressNo): void
    {
        $express = $this->expressDao->getByCode($expressCode);
        $url = "https://poll.kuaidi100.com/poll";

        // 订阅回调
        $callback = sys_config('site_url') . '/api/notify/kuaidi100';

        http()->post($url, [
            'key' => $express->kuaidi100_key,
            'com' => $express->kuaidi100_code,
            'num' => $expressNo,
            'resultv2' => 1,
            'callback_url' => $callback,
        ]);
    }
}
```

### 九、CRMEB路由注册模式

```php
<?php
// app/route.php (ThinkPHP6风格)
declare(strict_types=1);

use think\facade\Route;

// 营销模块路由
Route::group('marketing', function () {
    // 优惠券
    Route::get('coupon/list', 'marketing.Coupon/lists');
    Route::get('coupon/detail/:id', 'marketing.Coupon/detail');
    Route::post('coupon/receive', 'marketing.Coupon/receive');     // 领券
    Route::post('coupon/use', 'marketing.Coupon/use');           // 核销

    // 拼团
    Route::get('combination/list', 'marketing.Combination/lists');
    Route::get('combination/detail/:id', 'marketing.Combination/detail');
    Route::post('combination/open', 'marketing.Combination/open');  // 开团
    Route::post('combination/join/:id', 'marketing.Combination/join'); // 参团

    // 秒杀
    Route::get('seckill/index', 'marketing.Seckill/index');
    Route::post('seckill/purchase', 'marketing.Seckill/purchase'); // 抢购
})->middleware(\app\middleware\OptionalAuthMiddleware::class);

// 管理端路由
Route::group('adminapi', function () {
    Route::group('marketing', function () {
        Route::get('coupon', 'marketing.Coupon/index');
        Route::post('coupon', 'marketing.Coupon/save');
        Route::put('coupon/:id', 'marketing.Coupon/update');
        Route::delete('coupon/:id', 'marketing.Coupon/delete');

        Route::get('combination', 'marketing.Combination/index');
        Route::post('combination', 'marketing.Combination/save');
        Route::get('seckill', 'marketing.Seckill/index');
    });
})->middleware(\app\middleware\AdminAuthMiddleware::class);
```

### 十、ThinkPHP6 + Swoole协程化（性能关键）

```php
<?php
// config/console.php 添加定时任务
declare(strict_types=1);

return [
    'command' => [
        // 关闭超时拼团（每分钟执行）
        'seckill:close-expired' => \app\console\commands\SeckillCloseCommand::class,
        // 物流轨迹同步（每5分钟）
        'delivery:sync-traces' => \app\console\commands\DeliverySyncCommand::class,
    ],
    'schedule' => [
        '* * * * *' => ['seckill:close-expired'],
        '*/5 * * * *' => ['delivery:sync-traces'],
    ],
];

// app/console/commands/SeckillCloseCommand.php
declare(strict_types=1);

namespace app\console\commands;

use app\common\repositories\store\combination\CombinationRepository;
use Illuminate\Console\Command;

class SeckillCloseCommand extends Command
{
    protected $signature = 'seckill:close-expired';
    protected $combinationRepo;

    public function __construct(CombinationRepository $combinationRepo)
    {
        parent::__construct();
        $this->combinationRepo = $combinationRepo;
    }

    public function handle(): int
    {
        $count = $this->combinationRepo->closeTimeoutCombination();
        $this->info("Closed {$count} expired combinations.");
        return 0;
    }
}
```

### 十一、CRMEB与天龙岗位协同链路

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 × CRMEB电商协同链路                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 00分析师 → 电商数据诊断                                    │
│   └── 销售漏斗分析: 浏览→下单→支付→签收                   │
│   └── 转化率问题定位: 哪一步流失最严重                      │
│                                                             │
│ 01调研师 → CRMEB技术调研                                   │
│   └── CRMEB源码考古: 营销模块扩展点                       │
│   └── 电商最佳实践: 拼团/秒杀防超卖方案                   │
│                                                             │
│ 02架构师 → 电商系统架构设计                                │
│   └── 高并发架构: Redis原子操作+Lua脚本                   │
│   └── 事务一致性: 订单+库存+积分原子操作                   │
│                                                             │
│ 03构建师 → ThinkPHP6 CRUD + Swoole协程                    │
│   └── 参照本SKILL的Repository模式实现                       │
│   └── Workerman异步任务: 物流订阅/超时关单                  │
│                                                             │
│ 04验证师 → 电商场景压力测试                                │
│   └── 秒杀并发测试: Redis Lua脚本原子性验证               │
│   └── 积分防刷测试: 幂等性+限流                           │
│                                                             │
│ 05安全师 → 订单安全                                        │
│   └── 支付回调签名验证                                     │
│   └── 优惠券薅羊毛防护: 限领+库存原子扣减                  │
│                                                             │
│ 08发布师 → 灰度发布                                        │
│   └── 新营销活动: 灰度放量→全量                          │
│   └── 规则变更: A/B测试优惠效果                            │
│                                                             │
│ 35-04内容运营 → 商品详情页+营销活动页                     │
│   └── 配合优惠券/拼团/秒杀活动配置                         │
│                                                             │
│ 45-01电商运营 → 活动策划+数据监控                          │
│   └── 参照本SKILL配置营销活动                             │
│   └── 销售数据看板: 优惠券核销率/拼团成功率                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 十二、常用命令速查

```bash
# 清除Redis缓存（活动前准备）
redis-cli KEYS "seckill:*" | xargs redis-cli DEL
redis-cli KEYS "combination:*" | xargs redis-cli DEL

# 查看秒杀库存
redis-cli GET "seckill:{id}:{product_id}:stock"

# 手动关闭超时拼团
cd /www/crmeb && php think seckill:close-expired

# 订单状态流转
# 0待支付 → 1已支付/待发货 → 2待收货 → 3已完成 → -1已取消
```
