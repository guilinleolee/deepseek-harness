---
license: UNKNOWN
name: 03builder-03
version: 1.0.0
description: |
  代码施工：根据蓝图编写高质量、防御性的生产级代码。Invoke the 03builder agent to implement features based on architectural plans.
  设计接口时使用 Design It Twice 方法论，开发时遵循 TDD 垂直切片开发。
  PHP开发使用 Swoole/Workerman 异步模式，ThinkPHP6 框架遵循 ORM+Services+Repository 分层规范。
author: 天龙引擎团队
created: 2026-02-26
updated: 2026-05-11
category: development
integrations:
  - mattpocock-tdd (TDD垂直切片开发)
  - mattpocock-design-an-interface (Design It Twice接口设计)
  - emil-design-eng (动画决策框架)
  - swoole-patterns (PHP异步开发)
  - thinkphp6-patterns (ThinkPHP6核心模式)
triggers:
  - "用户提到「03builder 03构建师」时"
---

# 03构建师 (Builder)

## 核心职责
**代码施工**：严格执行架构师定义的原子化计划，遵循 **TDD (测试驱动开发)** 铁律，编写符合"深度防御工程"规范的高质量代码。PHP 开发遵循 Swoole/Workerman 异步模式，ThinkPHP6 开发遵循 Services+Repository 分层规范。

## 工程规范 (Engineering Standards)
- **TDD 铁律**: 严禁在未看到测试失败的情况下编写生产代码。
- **任务原子化**: 每个子任务必须在 2-5 分钟内完成，包含明确的 Commit 动作。
- **防御性编码**: 强制执行 Early Return，API 必设 timeout=30，DB 操作必包裹 try-except。
- **PHP异步规范**: IO密集型使用协程，CPU密集型使用进程池，异常通过 set_exception_handler 统一捕获。
- **ThinkPHP6规范**: Controller→Services→Repository 分层，Services 单例模式，Model 只做数据映射。

## TDD 垂直切片方法论

### 垂直切片 vs 水平切片

| 方法 | 描述 | 适用场景 |
|------|------|---------|
| **垂直切片 (Vertical Slices)** | 从头到尾实现一个用户故事 | 优先功能完整性 |
| **水平切片 (Horizontal Slices)** | 先实现所有层的一个模块 | 优先技术架构 |

> **推荐**：优先使用垂直切片，快速交付用户价值。

### 三阶段循环 (RED-GREEN-REFACTOR)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. RED (写一个失败的测试)                                    │
│    - 从用户视角写测试                                       │
│    - 测试应该失败，证明功能不存在                           │
│    - 不要mock太多东西                                       │
├─────────────────────────────────────────────────────────────┤
│ 2. GREEN (快速让测试通过)                                   │
│    - 用最简单的方式让测试通过                               │
│    - 可以有重复代码                                        │
│    - 不要追求完美                                          │
├─────────────────────────────────────────────────────────────┤
│ 3. REFACTOR (重构)                                         │
│    - 消除重复代码                                          │
│    - 改善代码结构                                          │
│    - 确保测试仍然通过                                      │
└─────────────────────────────────────────────────────────────┘
```

### 追踪弹 (Tracer Bullet) 工作流

适用于新项目或需要建立信心的场景：

```bash
# 1. 写一个端到端测试
# 2. 运行测试，看到它失败
# 3. 逐步实现，从外到内
#    - Controller/Handler → Service → Repository
# 4. 每次只让一个断言通过
# 5. 重复直到功能完成
```

### 测试结构模板

```typescript
// 1. 导入被测模块
import { calculate } from './calculator';

// 2. 描述测试组
describe('calculator', () => {
  // 3. 描述具体行为
  describe('add', () => {
    // 4. 写一个会失败的测试
    it('adds two numbers', () => {
      const result = calculate('2 + 2');
      expect(result).toBe(4);
    });
  });
});
```

### 常见反模式

| 反模式 | 问题 | 解决 |
|--------|------|------|
| 过度Mock | 测试不反映真实使用 | 只mock外部依赖 |
| 测试实现细节 | 重构破坏测试 | 测试行为而非实现 |
| 一次性写太多测试 | 难以调试 | 每次只写一个测试 |

---

## PHP 异步开发 (Swoole/Workerman)

### 一、HTTP Server

#### Workerman 多进程模式

```php
// Workerman HTTP Server
use Workerman\Worker;
use Workerman\Protocols\Http\Request;
use Workerman\Protocols\Http\Response;

require_once __DIR__ . '/vendor/autoload.php';

$worker = new Worker('http://0.0.0.0:8080');
$worker->count = 4; // CPU核数

$worker->onMessage = function($connection, Request $request) {
    $path = $request->path();
    $method = $request->method();

    if ($path === '/api/products' && $method === 'GET') {
        $data = ProductServices::getInstance()->lists($request->get());
        $connection->send(new Response()->withHeaders([
            'Content-Type' => 'application/json',
            'Access-Control-Allow-Origin' => '*',
        ])->withBody(json_encode(['code' => 0, 'data' => $data])));
    } else {
        $connection->send(new Response(404, [], json_encode(['code' => 404, 'msg' => 'Not Found'])));
    }
};

Worker::runAll();
```

#### Swoole HTTP Server

```php
// Swoole HTTP Server
$server = new Swoole\Http\Server('0.0.0.0', 8080);
$server->set([
    'worker_num' => 4,
    'task_worker_num' => 2,
    'enable_coroutine' => true,
]);

$server->on('Request', function($request, $response) {
    $path = $request->server['path_info'];
    [$controller, $action] = explode('/', trim($path, '/')) ?: ['index', 'index'];
    $instance = container()->get(ucfirst($controller) . 'Controller');
    $result = $instance->$action($request);
    $response->header('Content-Type', 'application/json; charset=utf-8');
    $response->end(json_encode($result));
});

$server->start();
```

#### 中间件模式

```php
// 请求中间件链
function pipeline(array $middlewares, callable $handler) {
    return array_reduce(
        array_reverse($middlewares),
        fn($next, $mw) => fn($ctx) => $mw($ctx, $next),
        $handler
    );
}

$pipe = pipeline([
    fn($ctx, $next) => Timer::after(1, fn() => $next($ctx)), // 超时保护
    fn($ctx, $next) => LogServices::before($ctx, $next),           // 日志记录
    fn($ctx, $next) => AuthServices::verify($ctx, $next),           // 认证
], fn($ctx) => Handler::dispatch($ctx));

$pipe(['request' => $request]);
```

#### 连接池模式

```php
// ProductConnectionPool (复用DB连接)
class ProductConnectionPool {
    private PDO $pdo;
    private array $cached = [];

    public function __construct() {
        $this->pdo = new PDO(
            'mysql:host=127.0.0.1;port=3306;dbname=crmeb',
            'root', '',
            [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
        );
    }

    public function getProduct(int $id): ?array {
        if (isset($this->cached[$id])) return $this->cached[$id];
        $stmt = $this->pdo->prepare('SELECT * FROM eb_store_product WHERE id=?');
        $stmt->execute([$id]);
        $this->cached[$id] = $stmt->fetch(PDO::FETCH_ASSOC);
        return $this->cached[$id];
    }
}
```

---

### 二、WebSocket Server

#### Workerman WebSocket 心跳保活

```php
use Workerman\Worker;
use Workerman\Timer;

$worker = new Worker('websocket://0.0.0.0:8282');
$worker->onWorkerStart = function() {
    Timer::add(55, function() {
        foreach($this->worker->connections as $conn) {
            if ($conn->lastPingTime < time() - 60) {
                $conn->close();
            } else {
                $conn->send('ping');
            }
        }
    });
};

$worker->onMessage = function($conn, $data) {
    $conn->lastPingTime = time();
    $msg = json_decode($data, true);
    switch ($msg['type'] ?? '') {
        case 'auth':
            $token = AuthServices::generateToken($msg['uid']);
            $conn->uid = $msg['uid'];
            $conn->send(json_encode(['type' => 'auth_ok', 'token' => $token]));
            break;
        case 'subscribe':
            $conn->room = $msg['room'];
            $conn->send(json_encode(['type' => 'subscribed', 'room' => $msg['room']]));
            break;
    }
};

Worker::runAll();
```

#### Swoole 群组消息

```php
$server->on('Message', function($ws, $frame) {
    $data = json_decode($frame->data, true);
    $room = $data['room'] ?? 'global';
    $server->join($room);
    foreach($server->connections as $fd) {
        if ($ws->isEstablished($fd)) {
            $server->push($fd, json_encode([
                'type' => 'broadcast',
                'room' => $room,
                'content' => $data['content'],
                'from' => $frame->fd
            ]));
        }
    }
});
```

#### CRMEB 订单状态推送

```php
// QueueServices::orderPaid() — 订单支付成功时WebSocket推送
public static function orderPaid(int $orderId): void {
    $order = StoreOrderServices::getInstance()->get($orderId);
    // 1. 更新订单状态
    StoreOrderServices::getInstance()->paid($orderId);
    // 2. 扣减库存
    StoreProductServices::getInstance()->decStock($order->cartInfo);
    // 3. 发送WebSocket通知
    $ws = new Swoole\WebSocket\Server('0.0.0.0', 8282);
    $ws->push($order->uid, json_encode([
        'type' => 'order_paid',
        'order_id' => $orderId,
        'amount' => $order->pay_price
    ]));
    // 4. 发送订阅消息
    SubscribeServices::sendPaidNotice($order);
}
```

---

### 三、RPC 服务调用

#### RPC Server

```php
// Swoole RPC Server
$server->on('Receive', function($server, $fd, $reactorId, $data) {
    $packet = json_decode($data, true);
    $service = $packet['service'];
    $method = $packet['method'];
    $params = $packet['params'] ?? [];

    try {
        $instance = container()->get($service);
        $result = $instance->$method(...$params);
        $server->send($fd, json_encode(['code' => 0, 'data' => $result]));
    } catch (\Throwable $e) {
        $server->send($fd, json_encode(['code' => $e->getCode(), 'msg' => $e->getMessage()]));
    }
});
```

#### RPC Client (带连接池)

```php
class RpcClient {
    private array $pools = [];

    public function call(string $service, string $method, array $params = []) {
        $pool = $this->getPool($service);
        $conn = $pool->get();
        try {
            $data = json_encode(['service' => $service, 'method' => $method, 'params' => $params]);
            $conn->send($data);
            $response = $conn->recv();
            return json_decode($response, true);
        } finally {
            $pool->put($conn);
        }
    }
}
```

---

### 四、Task/Async Task

#### Swoole TaskWorker

```php
$server->on('Task', function($server, $task) {
    $data = $task->data;
    switch ($data['type']) {
        case 'send_sms':
            return SmsService::send($data['mobile'], $data['content']);
        case 'export_excel':
            return ExportService::generate($data['params']);
        case 'batch_notify':
            return BatchNotifyService::notify($data['uids'], $data['content']);
        default:
            return null;
    }
});

$server->on('Finish', function($server, $taskId, $data) {
    TaskCallbackServices::handle($taskId, $data);
});
```

#### Redis 队列驱动 (Workerman)

```php
use Workerman\Redis\Client as RedisClient;

$redis = new RedisClient('redis://127.0.0.1:6379');

$worker = new Worker();
$worker->onWorkerStart = function() {
    $redis->subscribe(['order_paid_queue'], function($channel, $msg) {
        $data = json_decode($msg, true);
        QueueServices::process($data);
    });
};

$worker->onMessage = function($conn, $data) {
    // 生产者：入队
    QueueServices::enqueue('order_paid_queue', $data);
};

Worker::runAll();
```

---

### 五、Coroutine 协程

#### Swoole WaitGroup 并发查询 (商品详情优化 500ms→80ms)

**适用场景**：商品详情页需要同时查询：商品主数据、分类路径、商品属性、评论数、是否收藏

```php
// 商品详情页 (优化后: 500ms→80ms)
public function detail(int $id): array {
    return go(function() use ($id) {
        $wg = new Swoole\Coroutine\WaitGroup();

        $product = $category = $attrs = $replyCount = $userFav = null;

        go(function() use ($wg, &$product, $id) {
            defer($wg->done());
            $product = $this->model->find($id);
        });
        go(function() use ($wg, &$category, $product) {
            defer($wg->done());
            if ($product) $category = CategoryService::getPath($product->cate_id);
        });
        go(function() use ($wg, &$attrs, $id) {
            defer($wg->done());
            $attrs = ProductAttrServices::getAttrs($id);
        });
        go(function() use ($wg, &$replyCount, $id) {
            defer($wg->done());
            $replyCount = ProductReplyServices::count($id);
        });
        go(function() use ($wg, &$userFav, $id) {
            defer($wg->done());
            $userFav = UserCollectServices::isFav(uid(), $id);
        });

        $wg->wait(); // 等待全部完成

        return [
            'product'    => $product,
            'category'   => $category,
            'attrs'      => $attrs,
            'reply_count'=> $replyCount,
            'user_fav'   => $userFav
        ];
    });
}
```

#### Swoole Channel 并发池

```php
// Channel实现并发池，控制最大并发数
$pool = new Swoole\Coroutine\Channel(10); // 最多10个并发
for ($i = 0; $i < 20; $i++) {
    go(function() use ($pool, $i) {
        $pool->push($i);
        usleep(random_int(100000, 500000));
        $v = $pool->pop();
        echo "Task $v done\n";
    });
}
```

#### CRMEB 商品列表协程并发

```php
// 商品列表 (使用Swoole\Coroutine\WaitGroup)
public function lists(array $params): array {
    return go(function() use ($params) {
        $wg = new Swoole\Coroutine\WaitGroup();

        $page = $params['page'] ?? 1;
        $limit = $params['limit'] ?? 10;

        $products = $categories = $swipe = null;

        go(function() use ($wg, &$products, $page, $limit) {
            defer($wg->done());
            $products = StoreProductServices::getInstance()->list($page, $limit);
        });
        go(function() use ($wg, &$categories) {
            defer($wg->done());
            $categories = CategoryServices::getAll();
        });
        go(function() use ($wg, &$swipe) {
            defer($wg->done());
            $swipe = ProductSwipeServices::getRecommend();
        });

        $wg->wait();

        return [
            'list'       => $products,
            'categories' => $categories,
            'swipe'      => $swipe
        ];
    });
}
```

---

### 六、Timer 定时器

#### Workerman Crontab

```php
use Workerman\Worker;
use Workerman\Timer;

require_once __DIR__ . '/vendor/autoload.php';

$worker = new Worker();
$worker->onWorkerStart = function() {
    // 每分钟: 清理过期Token
    Timer::add(60, function() {
        TokenServices::cleanExpired();
    });

    // 每小时: 更新热门商品缓存
    Timer::add(3600, function() {
        CacheServices::refresh('hot_products', fn() => ProductServices::getHotProducts());
    });

    // 每日凌晨: 生成报表
    Timer::add(86400, function() {
        ReportServices::daily();
    });
};

Worker::runAll();
```

#### CRMEB CrontabServices

```php
// app/services/crontab/CrontabServices.php
class CrontabServices {
    public static function everyMinute(): void {
        // 订单自动关闭 (30分钟未支付)
        self::autoCloseOrder();
        // 佣金自动结算
        self::autoBrokerage();
    }

    public static function everyDay(): void {
        // 清理7天前日志
        LogServices::clean(7);
        // 统计昨日GMV
        StatServices::dailyReport();
    }
}
```

---

### 七、Process 进程管理

#### Workerman 多进程

```php
use Workerman\Worker;

$worker = new Worker();
$worker->count = 4; // 4个进程

$worker->onMessage = function($conn, $data) {
    $conn->send('Hello ' . $data);
};

Worker::runAll();
```

#### Swoole 进程池 (CPU密集型)

```php
$pool = new Swoole\Process\Pool(4);
$pool->on('Message', function($pool, $workerId, $data) {
    $pool->getMessage($workerId); // 获取消息
    $result = ImageProcessServices::compress($data); // CPU密集型任务
    $pool->write($result);
});
$pool->start();
```

#### CRMEB ExportProcess (导出大文件)

```php
// 导出百万级数据时不阻塞主进程
class ExportProcess {
    public static function handle(array $params): void {
        $process = new Swoole\Process(function(Swoole\Process $proc) use ($params) {
            $file = fopen($params['path'], 'w');
            $offset = 0;
            $limit = 5000;

            while (true) {
                $data = StoreOrderServices::getInstance()
                    ->where('id', '>', $offset)
                    ->order('id')
                    ->limit($limit)
                    ->select()
                    ->toArray();

                if (empty($data)) break;

                foreach ($data as $row) {
                    fputcsv($file, self::formatRow($row));
                    $offset = $row['id'];
                }

                $proc->wakeup(); // 通知进度
            }

            fclose($file);
        });

        Swoole\Process::spawn($process);
    }
}
```

---

### 八、IPC 进程间通信

#### Swoole 消息队列

```php
// 生产者
$queue = new Swoole\Coroutine\Channel(100);
$queue->push(['type' => 'order_paid', 'data' => $orderData]);

// 消费者 (独立进程)
go(function() use ($queue) {
    while (true) {
        $msg = $queue->pop();
        if ($msg['type'] === 'order_paid') {
            QueueServices::orderPaid($msg['data']);
        }
    }
});
```

#### Workerman MessageBus

```php
// Workerman MessageBus (多进程事件通知)
Bus::publish('user.upgrade', ['uid' => $uid, 'level' => $newLevel]);

Bus::subscribe('user.upgrade', function($data) {
    UserStatServices::increment($data['uid'], 'level_upgrades');
    NotificationServices::send($data['uid'], '恭喜升级');
});
```

---

### 九、错误处理与防御式编程

#### Swoole 全局异常

```php
// 在 WorkerStart 中注册全局异常处理
$server->on('WorkerStart', function($server, $workerId) {
    set_exception_handler(function(\Throwable $e) use ($server, $workerId) {
        LogServices::error('Worker异常', [
            'worker_id' => $workerId,
            'message'   => $e->getMessage(),
            'file'      => $e->getFile(),
            'line'      => $e->getLine(),
            'trace'     => $e->getTraceAsString()
        ]);

        if (!$server->taskworker) {
            // Worker进程: 重启当前进程
            $server->reload();
        }
    });
});
```

#### CRMEB 异常处理

```php
// 自定义异常处理
set_exception_handler(function(\Throwable $e) {
    $code = $e instanceof BusinessException ? $e->getCode() : 500;

    if (request()->isAjax()) {
        return json([], $code, $e->getMessage());
    }

    if (app()->environment('local')) {
        throw $e; // 本地环境抛出详细错误
    }

    // 生产环境: 记录日志，返回友好页面
    LogServices::error($e->getMessage(), $e->getTrace());
    abort(500, '系统异常');
});
```

#### 防御式编程规范

| 场景 | 防御手段 |
|------|---------|
| API调用 | `try-catch` 包裹，`timeout=30` |
| 数据库 | `try-catch` 包裹，`transaction` 事务回滚 |
| 文件操作 | `is_file/exists` 前置检查 |
| 用户输入 | `htmlspecialchars/filter_var` 过滤 |
| 空值访问 | `$result ?? []`，`isset($arr['key'])` |
| 并发竞态 | `Swoole\Coroutine\WaitGroup`，`Redis原子操作` |

---

## ThinkPHP6 核心模式

### 一、路由与请求处理

#### 注解路由

```php
// 自动路由到 Controller
// Route::get('/product/:id', 'product/detail');

// 完整路由定义
Route::group('api', function() {
    Route::get('product/list', 'product/lists');
    Route::get('product/:id', 'product/detail');
    Route::post('order/create', 'order/create');
    Route::post('cart/add', 'cart/add');
})->middleware(ApiAuth::class);
```

#### 路由缓存 (生产环境)

```php
// 缓存路由定义 (生产环境)
if (app()->environment('production')) {
    Route::cache('route.cache');
}
```

#### CRMEB v2 API 路由

```php
// app/route/mp.php — 小程序路由组
use think\facade\Route;

Route::group('api', function() {
    // 认证
    Route::post('login/mini', 'mp.Login/miniLogin');
    Route::post('login/wxMobile', 'mp.Login/wxMobile');

    // 商品
    Route::get('product/list', 'mp.Product/lists');
    Route::get('product/detail/:id', 'mp.Product/detail');

    // 购物车
    Route::get('cart/lists', 'mp.Cart/lists');
    Route::post('cart/add', 'mp.Cart/add');
    Route::post('cart/del', 'mp.Cart/del');

    // 订单
    Route::post('order/create', 'mp.Order/create');
    Route::get('order/lists', 'mp.Order/lists');

    // 支付
    Route::post('pay/wxPay', 'mp.Pay/wxPay');
    Route::post('pay/notify', 'mp.Pay/notify'); // 微信支付回调

    // 分享配置
    Route::get('share/config', 'mp.Share/config');
})->middleware(\app\http\middleware\CheckMiniToken::class);
```

---

### 二、中间件

#### 全局中间件注册

```php
// app/middleware.php
return [
    \app\http\middleware\LoadLangPack::class,
    \app\http\middleware\Cors::class,
];
```

#### 限流中间件 (Redis滑动窗口)

```php
class RateLimit {
    public function handle($request, \Closure $next) {
        $key = 'rate:' . $request->ip();
        $limit = 60; // 60次/分钟
        $window = 60;

        $count = Cache::redis()->inc($key);
        if ($count === 1) Cache::redis()->expire($key, $window);

        if ($count > $limit) {
            return json([], 429, '请求过于频繁');
        }

        return $next($request);
    }
}
```

#### CORS 中间件

```php
class Cors {
    public function handle($request, \Closure $next) {
        if ($request->isOptions()) {
            return response('', 204, [
                'Access-Control-Allow-Origin'  => '*',
                'Access-Control-Allow-Methods' => 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers' => 'Authorization,Content-Type,X-Token',
                'Access-Control-Max-Age'      => '86400'
            ]);
        }

        $response = $next($request);
        $response->header([
            'Access-Control-Allow-Origin' => '*',
        ]);
        return $response;
    }
}
```

#### ApiAuth 中间件 (Redis Token 校验)

```php
class CheckMiniToken {
    public function handle($request, \Closure $next) {
        $token = $request->header('X-Token')
            ?? $request->param('token')
            ?? $request->cookie('token');

        if (!$token) {
            return json([], 401, '请先登录');
        }

        $cacheKey = 'user_token:' . md5($token);
        $userInfo = Cache::redis()->get($cacheKey);

        if (!$userInfo) {
            return json([], 401, 'Token已过期');
        }

        // 续期 (滑动过期)
        Cache::redis()->expire($cacheKey, 604800); // 7天

        $request->uid = $userInfo['uid'];
        return $next($request);
    }
}
```

---

### 三、依赖注入与服务容器

#### Services 层单例模式

```php
// 正确的Services层 — 单例+依赖注入
namespace app\services;

class StoreProductServices {
    private StoreProduct $productModel;
    private StoreCategoryServices $categoryServices;

    // 通过容器注入Model依赖
    public function __construct(
        StoreProduct $productModel,
        StoreCategoryServices $categoryServices = null
    ) {
        $this->productModel = $productModel;
        $this->categoryServices = $categoryServices
            ?? app()->make(StoreCategoryServices::class);
    }

    // 禁止 new XxxServices()
    public static function getInstance(): static {
        return app()->make(static::class);
    }

    public function lists(array $params): array {
        $where = [];
        if (!empty($params['cate_id'])) {
            $where[] = ['cate_id', '=', $params['cate_id']];
        }
        return $this->productModel->where($where)->select()->toArray();
    }

    public function detail(int $id): ?array {
        return $this->productModel->find($id);
    }
}
```

#### Repository 模式

```php
// Repository — 隔离数据访问
interface ProductRepositoryInterface {
    public function find(int $id): ?array;
    public function list(array $filters): array;
}

class ProductRepository implements ProductRepositoryInterface {
    public function find(int $id): ?array {
        return StoreProduct::find($id)?->toArray();
    }

    public function list(array $filters): array {
        $model = StoreProduct::where('is_del', 0);
        if (!empty($filters['keyword'])) {
            $model->whereLike('store_name', '%' . $filters['keyword'] . '%');
        }
        return $model->page($filters['page'] ?? 1, $filters['limit'] ?? 10)->select()->toArray();
    }
}

// Services依赖Repository
class ProductServices {
    public function __construct(private ProductRepositoryInterface $repo) {}

    public function getProduct(int $id): ?array {
        return $this->repo->find($id);
    }
}
```

---

### 四、ORM 与数据库

#### 模型定义

```php
class StoreProduct extends BaseModel {
    protected $table = 'eb_store_product';
    protected $pk = 'id';

    // 自动时间戳
    protected $autoWriteTimestamp = true;
    protected $createTime = 'add_time';
    protected $updateTime = 'update_time';

    // 类型转换
    protected $type = [
        'price'      => 'float',
        'stock'      => 'integer',
        'sales'      => 'integer',
        'add_time'   => 'timestamp',
    ];

    // 软删除
    use SoftDelete;
    protected $deleteTime = 'is_del';
    protected $defaultSoftDelete = 1;

    // 关联
    public function category() {
        return $this->belongsTo(StoreCategory::class, 'cate_id');
    }
}
```

#### 关联查询

```php
// 预加载避免N+1
$products = StoreProduct::with(['category', 'sku'])
    ->where('is_del', 0)
    ->select();

// hasWhere 复杂条件
$products = StoreProduct::hasWhere('category', ['id' => $cateId])
    ->select();
```

#### 分页

```php
// 简洁分页
$list = StoreProduct::page($page, $limit)->select();
$count = StoreProduct::count();

// 获取分页数据+总数
$paginate = StoreProduct::where($where)
    ->paginate(['list_rows' => $limit, 'page' => $page]);

return ['list' => $paginate->items(), 'total' => $paginate->total()];
```

#### 模型事件

```php
// 模型事件: 创建/更新/删除自动触发
class StoreOrder extends BaseModel {
    protected static function onBeforeInsert(StoreOrder $model) {
        $model->order_no = generate_order_no(); // 自动生成订单号
    }

    protected static function onAfterUpdate(StoreOrder $model) {
        // 订单状态变更后: 发货通知/退款处理
        event('OrderStatusChanged', [$model]);
    }

    protected static function onAfterDelete(StoreOrder $model) {
        // 删除订单: 恢复库存
        ProductServices::getInstance()->incStock($model->cartInfo);
    }
}
```

---

### 五、验证器与场景

#### 基础验证器

```php
class ProductValidate extends BaseValidate {
    protected $rule = [
        'store_name' => 'require|max:200',
        'cate_id'    => 'require|number|gt:0',
        'price'      => 'require|float|gt:0',
        'stock'      => 'require|integer|egt:0',
        'unit_name'  => 'max:10',
    ];

    protected $message = [
        'store_name.require' => '商品名称不能为空',
        'cate_id.require'    => '请选择商品分类',
        'price.require'      => '商品价格不能为空',
        'price.gt'          => '商品价格必须大于0',
    ];

    // 场景: 创建商品
    public function sceneCreate(): static {
        return $this->only(['store_name', 'cate_id', 'price', 'stock', 'unit_name'])
            ->append('store_name', 'unique:eb_store_product,store_name');
    }

    // 场景: 更新商品
    public function sceneUpdate(): static {
        return $this->only(['store_name', 'cate_id', 'price', 'stock'])
            ->require('id');
    }

    // 场景: 购物车添加
    public function sceneCartAdd(): static {
        return $this->only(['product_id', 'num'])
            ->append('product_id', 'gt:0')
            ->append('num', 'between:1,99');
    }
}
```

#### 控制器调用验证器

```php
// 正确方式
public function save(Request $request) {
    $data = $this->validate($request->post(), ProductValidate::class->sceneCreate());
    $result = ProductServices::getInstance()->create($data);
    return success($result);
}

// 手动验证
$validate = new ProductValidate();
if (!$validate->scene('create')->check($data)) {
    return fail($validate->getError());
}
```

---

### 六、异常处理

#### 自定义异常

```php
// 业务异常
class BusinessException extends \RuntimeException {
    protected $code = 400;
    protected $errorCode;

    public function __construct(string $message = '', int $errorCode = 0) {
        parent::__construct($message);
        $this->errorCode = $errorCode;
    }

    public function getErrorCode(): int {
        return $this->errorCode;
    }
}

// 全局异常捕获
class ExceptionHandle extends \app\base\BaseExceptionHandle {
    public function render($request, \Throwable $e): Response {
        if ($e instanceof BusinessException) {
            return json([], $e->getCode(), $e->getMessage(), $e->getErrorCode());
        }

        if (app()->environment('local')) {
            return json([], 500, $e->getMessage());
        }

        LogServices::error($e->getMessage(), $e->getTrace());
        return json([], 500, '系统异常');
    }
}
```

#### 统一响应函数 (CRMEB核心)

```php
// ThinkPHP6助手函数 — 统一JSON响应格式
function json($data = [], $code = 0, $msg = '', $errorCode = 0): Json {
    return json([
        'code'       => $code,
        'msg'        => $msg ?: ($code == 0 ? 'ok' : 'error'),
        'time'       => time(),
        'error_code' => $errorCode,
        'data'       => $data,
    ]);
}

function success($data = [], $msg = 'ok'): Json {
    return json($data, 0, $msg);
}

function fail($msg = '请求失败', $code = 400, $errorCode = 0): Json {
    return json([], $code, $msg, $errorCode);
}

// ThinkPHP6框架响应 (与TP5兼容)
function json($data = [], $code = 0, $msg = ''): Json {
    $result = is_array($data) ? $data : ['code' => $code, 'msg' => $msg, 'time' => time(), 'data' => []];
    if (!is_array($data)) {
        $result['data'] = $data;
    }
    return json($result);
}
```

---

### 七、Facade 门面

#### 自定义Facade

```php
// 1. 定义门面类
namespace app\facade;

use think\Facade;

class Cache extends Facade {
    protected static function getFacadeClass(): string {
        return 'cache';
    }
}

// 2. 绑定到容器
// app/provider.php
return [
    'cache' => \app\services\CacheServices::class,
];

// 3. 使用
use app\facade\Cache;

Cache::get('product_list');
Cache::set('key', $value, 3600);
Cache::redis()->inc('order_count');
```

#### CRMEB Cache Facade

```php
// Cache服务 (Redis封装)
class CacheServices {
    private $redis;

    public function __construct() {
        $this->redis = new \Redis();
        $this->redis->connect('127.0.0.1', 6379);
        $this->redis->select(3); // DB3
    }

    public function get(string $key) {
        return json_decode($this->redis->get($key), true);
    }

    public function set(string $key, $value, int $ttl = 0): bool {
        $value = is_array($value) ? json_encode($value) : $value;
        if ($ttl > 0) {
            return $this->redis->setex($key, $ttl, $value);
        }
        return $this->redis->set($key, $value);
    }
}
```

---

### 八、多应用与模块化

#### 目录结构

```
app/
├── admin/          # 管理后台
│   ├── controller/
│   │   └── marketing/
│   │       ├── StoreProduct.php
│   │       ├── StoreOrder.php
│   │       └── StoreCoupons.php
│   ├── middleware/
│   │   └── AdminAuth.php
│   └── services/
│       ├── ProductServices.php
│       └── OrderServices.php
├── api/            # API接口
│   ├── controller/
│   │   └── mp/
│   │       ├── Product.php
│   │       ├── Order.php
│   │       └── Pay.php
│   └── middleware/
│       └── CheckMiniToken.php
├── wap/             # H5移动端
│   └── controller/
└── common/          # 公共代码
    ├── BaseController.php
    ├── BaseModel.php
    ├── BaseValidate.php
    └── functions.php
```

#### 多应用路由

```php
// admin应用路由
// route/admin.php
Route::group('admin', function() {
    Route::post('login', 'login/index');
    Route::get('product/list', 'product/lists');
})->middleware(AdminAuth::class);

// mp应用路由
// route/mp.php
Route::group('mp', function() {
    Route::post('login/mini', 'login/miniLogin');
    Route::get('product/list', 'product/lists');
})->middleware(CheckMiniToken::class);
```

---

## 施工流程 (Workflow)

1. **确认失败**: 运行测试确保其按预期失败（红色）。
2. **最小实现**: 编写最少量的代码使测试通过（绿色）。
3. **两阶段审查**:
   - **合规审查**: 确保代码不多不少，完全匹配 Spec。
   - **质量审查**: 检查代码美感、安全性与性能。
4. **持久化演化**: 更新 `evolution.json` 记录本项目特有的模式。

---

## 天龙岗位协同链路

```
00分析师
  ↓ 分析需求（商品SKU/营销活动/多端适配）
  ↓
01调研师
  ↓ 调研 CRMEB 模板能力 + ThinkPHP6 接口协议
  ↓ 调研 Swoole/Workerman 异步模式
  ↓
02架构师
  ↓ 设计多端统一架构（Taro3 / uni-app）
  ↓ 设计异步IO分层（协程/进程池）
  ↓
03构建师 ⭐本SKILL
  ↓ 前端：Taro3 多端编译 + CRMEB 模板定制
  ↓ 后端：ThinkPHP6 路由 + Swoole/Workerman 异步 + 微信支付 V3
  ↓
04验证师
  ↓ 支付全流程测试（沙箱环境）
  ↓ 多端兼容性测试（iOS/Android/鸿蒙）
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
45-01电商运营
  ↓ 活动策划（优惠券/拼团/秒杀/分销）+ 数据看板监控
```

---

## 执行指令

立刻通过 `/03构建师` 或调用 `Task` 工具（指定 `subagent_type: 03builder`）开始施工。
