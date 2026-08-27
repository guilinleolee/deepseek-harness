---
license: UNKNOWN
triggers: ["swoole patterns", "Swoole/Workerman Patterns"]
---
# Swoole/Workerman Patterns

> Swoole是PHP异步协程运行时，Workerman是纯PHP常驻内存框架。CRMEB基于Workerman实现高性能电商后端。本SKILL覆盖HTTP/WebSocket/RPC/Task/Coroutine等核心模式。

## 触发词
`/swoole` `/workerman` `/php-async` `/php-coroutine`

---

## 一、HTTP Server 服务端

### 触发条件
- 场景：需要构建高性能HTTP API服务
- 场景：需要替代传统PHP-FPM架构
- 场景：需要支持WebSocket长连接

### 核心实现

#### 基础HTTP Server

```php
<?php
// Workerman HTTP Server (推荐CRMEB使用)
require_once __DIR__ . '/vendor/autoload.php';

use Workerman\Worker;
use Workerman\Protocols\Http\Request;
use Workerman\Protocols\Http\Response;

$worker = new Worker('http://0.0.0.0:8080');

// 每请求触发
$worker->onMessage = function($connection, Request $request) {
    $path = $request->path();
    $method = $request->method();

    // 路由分发
    $response = match($path) {
        '/api/product/list' => handleProductList($request),
        '/api/order/create' => handleOrderCreate($request),
        '/api/user/info' => handleUserInfo($request),
        default => new Response(404, [], 'Not Found'),
    };

    $connection->send($response);
};

$worker->onWorkerStart = function() {
    echo "Worker started on http://0.0.0.0:8080\n";
};

Worker::runAll();
```

#### Swoole HTTP Server

```php
<?php
// Swoole HTTP Server (高性能场景)
$http = new Swoole\Http\Server('0.0.0.0', 9501);

$http->set([
    'worker_num' => swoole_cpu_num() * 2,
    'task_worker_num' => 4,
    'max_request' => 10000,
    'open_http2_protocol' => true,
    'http_compression' => true,
]);

$http->on('request', function($request, $response) {
    $uri = $request->server['request_uri'];

    // 性能: Swoole协程内直接操作MySQL
    go(function() use ($response, $uri) {
        $mysql = new Swoole\Coroutine\MySQL();
        $mysql->connect([
            'host' => '127.0.0.1',
            'port' => 3306,
            'user' => 'root',
            'password' => 'password',
            'database' => 'crmeb',
        ]);

        $result = $mysql->query("SELECT * FROM eb_store_product LIMIT 10");

        $response->header('Content-Type', 'application/json');
        $response->end(json_encode($result));
    });
});

$http->on('task', function($serv, $taskId, $reactorId, $data) {
    // 异步任务处理
    return $data;
});

$http->on('finish', function($serv, $taskId, $data) {
    // 任务完成回调
});

$http->start();
```

### 进阶变体

#### 中间件模式

```php
<?php
// Workerman 中间件链
class MiddlewareChain {
    private array $middlewares = [];

    public function add(callable $middleware): self {
        $this->middlewares[] = $middleware;
        return $this;
    }

    public function handle(Request $request, callable $core): Response {
        $next = $core;

        // 倒序构建调用链
        for ($i = count($this->middlewares) - 1; $i >= 0; $i--) {
            $middleware = $this->middlewares[$i];
            $currentNext = $next;
            $next = fn($req) => $middleware($req, $currentNext);
        }

        return $next($request);
    }
}

// 使用
$chain = new MiddlewareChain();
$chain->add(new CorsMiddleware())
      ->add(new AuthMiddleware())
      ->add(new RateLimitMiddleware());

$response = $chain->handle($request, fn($req) => handleCore($req));
```

#### 连接池模式

```php
<?php
// Swoole 连接池 (CRMEB商品接口优化)
class ProductConnectionPool {
    private Swoole\Coroutine\Channel $pool;
    private array $config;

    public function __construct(int $size = 20) {
        $this->pool = new Swoole\Coroutine\Channel($size);
        $this->config = [
            'host' => '127.0.0.1',
            'port' => 3306,
            'user' => 'root',
            'password' => '',
            'database' => 'crmeb',
            'charset' => 'utf8mb4',
        ];

        // 预创建连接
        for ($i = 0; $i < $size; $i++) {
            $this->pool->push($this->createConnection());
        }
    }

    private function createConnection(): Swoole\Coroutine\MySQL {
        $mysql = new Swoole\Coroutine\MySQL();
        $mysql->connect($this->config);
        return $mysql;
    }

    public function get(): Swoole\Coroutine\MySQL {
        return $this->pool->pop(5); // 5秒超时
    }

    public function release(Swoole\Coroutine\MySQL $conn): void {
        $this->pool->push($conn);
    }

    public function exec(string $sql, array $params = []): array|false {
        $conn = $this->get();
        try {
            if (empty($params)) {
                return $conn->query($sql);
            }
            $stmt = $conn->prepare($sql);
            return $stmt->execute($params)->fetchAll();
        } finally {
            $this->release($conn);
        }
    }
}
```

### CRMEB适配

```php
<?php
// CRMEB应用场景: 商品列表接口
// 文件: app/api/controller/v2/StoreProduct.php 参考实现

// 路由注册 (route/api.php)
use Workerman\Router;
Router::post('/api/product/list', [ProductController::class, 'list']);

// 控制器
class ProductController {
    public function list(Request $request) {
        $page = (int)$request->get('page', 1);
        $limit = (int)$request->get('limit', 10);

        // 协程并发查询 (Swoole)
        go(function() use ($page, $limit) {
            $wg = new Swoole\Coroutine\WaitGroup();

            $products = null;
            $count = null;

            $wg->add();
            go(function() use (&$products, $page, $limit, $wg) {
                defer($wg->done());
                $products = $this->productService->list($page, $limit);
            });

            $wg->add();
            go(function() use (&$count, $wg) {
                defer($wg->done());
                $count = $this->productService->count();
            });

            $wg->wait();

            return json(['list' => $products, 'count' => $count]);
        });
    }
}
```

### 验证检查点

- [ ] Worker进程正常启动，无致命错误
- [ ] 路由分发正确，404处理正常
- [ ] 中间件链按顺序执行
- [ ] 连接池无泄漏，超时可正确回收
- [ ] 压测: QPS > 5000 (Workerman) / QPS > 15000 (Swoole)

---

## 二、WebSocket Server 长连接

### 触发条件
- 场景：实时聊天、客服消息推送
- 场景：订单状态实时通知
- 场景：直播间弹幕、在线人数统计

### 核心实现

#### Workerman WebSocket

```php
<?php
// Workerman WebSocket Server
require_once __DIR__ . '/vendor/autoload.php';

use Workerman\Worker;
use Workerman\Connection\TcpConnection;
use Workerman\Protocols\Websocket;

$worker = new Worker('websocket://0.0.0.0:8282');
$worker->count = 4; // 多进程

// 存储: fd => user_id
global $fdMap;
$fdMap = [];

$worker->onWebSocketConnect = function($connection, $httpBuffer) {
    // 握手验证
    $token = $_GET['token'] ?? '';
    if (!$this->validateToken($token)) {
        $connection->close('Unauthorized');
    }
};

$worker->onMessage = function($connection, $data) {
    global $fdMap;

    $message = json_decode($data, true);

    switch ($message['type']) {
        case 'auth':
            // 绑定用户
            $fdMap[$connection->id] = $message['user_id'];
            $connection->send(json_encode(['type' => 'auth_ok']));
            break;

        case 'chat':
            // 消息转发
            $targetFd = $this->findFdByUserId($message['to_uid']);
            if ($targetFd) {
                $targetFd->send(json_encode([
                    'type' => 'chat',
                    'from_uid' => $fdMap[$connection->id],
                    'content' => $message['content'],
                    'time' => time(),
                ]));
            }
            break;

        case 'ping':
            $connection->send(json_encode(['type' => 'pong']));
            break;
    }
};

$worker->onClose = function($connection) {
    global $fdMap;
    unset($fdMap[$connection->id]);
};

Worker::runAll();
```

#### Swoole WebSocket

```php
<?php
// Swoole WebSocket + Redis发布订阅 (推荐生产环境)
$server = new Swoole\WebSocket\Server('0.0.0.0', 8282);

$server->set([
    'worker_num' => 4,
    'task_worker_num' => 2,
]);

// fd映射表
$server->userMap = []; // [fd => uid]

$server->on('open', function($server, $req) {
    $token = $req->get['token'] ?? '';
    $userId = $this->auth($token);
    if ($userId) {
        $server->userMap[$req->fd] = $userId;
        $server->send($req->fd, json_encode(['type' => 'connected']));
    } else {
        $server->close($req->fd);
    }
});

$server->on('message', function($server, $frame) {
    $data = json_decode($frame->data, true);

    // 通过Redis Pub/Sub广播到所有Worker
    Redis::publish('ws:broadcast', json_encode([
        'from_fd' => $frame->fd,
        'from_uid' => $server->userMap[$frame->fd],
        'data' => $data,
    ]));
});

$server->on('task', function($server, $task) {
    $data = json_decode($task->data, true);

    // 广播消息
    foreach ($server->connections as $fd) {
        if ($server->isEstablished($fd)) {
            $server->send($fd, json_encode($data['data']));
        }
    }

    return "broadcast_done";
});

$server->start();
```

### 进阶变体

#### 心跳保活

```php
<?php
// WebSocket心跳检测
$worker->onWorkerStart = function() {
    // 定时器: 每30秒检查连接
    Timer::add(30, function() use (&$connections) {
        foreach ($connections as $fd => $lastPing) {
            if (time() - $lastPing > 90) {
                // 超时断开
                Connection::close($fd);
                unset($connections[$fd]);
            }
        }
    });
};

// 客户端需每60秒发送一次心跳
```

#### 群组消息

```php
<?php
// 群组聊天室
class GroupManager {
    private static array $groups = []; // [group_id => [fd => info]]

    public static function join(int $groupId, int $fd, array $userInfo): void {
        self::$groups[$groupId][$fd] = $userInfo;
    }

    public static function leave(int $groupId, int $fd): void {
        unset(self::$groups[$groupId][$fd]);
    }

    public static function broadcast(int $groupId, array $message, int $excludeFd = 0): void {
        foreach (self::$groups[$groupId] ?? [] as $fd => $info) {
            if ($fd !== $excludeFd) {
                Server::$instance->send($fd, json_encode($message));
            }
        }
    }

    public static function members(int $groupId): array {
        return array_values(self::$groups[$groupId] ?? []);
    }
}
```

### CRMEB适配

```php
<?php
// CRMEB场景: 订单状态推送
// 用户下单后，后端通过WebSocket推送订单状态变更

// 触发时机: app/services/order/OrderServices.php
public function createOrder($data) {
    $order = $this->orderRepository->create($data);

    // 异步通知用户
    Task::deliver(new OrderPushTask($order->user_id, 'order_created', [
        'order_id' => $order->id,
        'order_no' => $order->order_no,
        'amount' => $order->pay_price,
    ]));

    return $order;
}

// OrderPushTask.php
class OrderPushTask implements TaskInterface {
    public function execute() {
        $fd = UserFdMap::getFd($this->userId);
        if ($fd) {
            Server::$instance->send($fd, json_encode([
                'type' => $this->eventType,
                'data' => $this->payload,
            ]));
        }
    }
}
```

### 验证检查点

- [ ] WebSocket握手成功，无跨域问题
- [ ] 多进程下fd映射表一致性
- [ ] 心跳机制正常工作，断线正确清理
- [ ] 消息延迟 < 100ms (同机器)
- [ ] 1000并发连接无内存泄漏

---

## 三、RPC远程过程调用

### 触发条件
- 场景：微服务间同步调用
- 场景：跨语言服务通信
- 场景：需要高性能内部RPC

### 核心实现

```php
<?php
// Workerman RPC Server
class RpcServer {
    private Worker $worker;

    public function register(string $name, callable $handler): self {
        $this->services[$name] = $handler;
        return $this;
    }

    public function start(int $port = 9502): void {
        $this->worker = new Worker("tcp://0.0.0.0:{$port}");
        $this->worker->onMessage = function($conn, $data) {
            $request = json_decode($data, true);

            $service = $request['service'] ?? '';
            $method = $request['method'] ?? '';
            $params = $request['params'] ?? [];

            try {
                $result = call_user_func_array(
                    $this->services["$service.$method"] ?? $this->services[$service],
                    $params
                );
                $response = ['code' => 0, 'data' => $result];
            } catch (Throwable $e) {
                $response = ['code' => $e->getCode(), 'msg' => $e->getMessage()];
            }

            $conn->send(json_encode($response));
        };
        Worker::runAll();
    }
}

// 注册服务
$rpc = new RpcServer();
$rpc->register('ProductService.list', fn($page, $limit) => ProductService::list($page, $limit));
$rpc->register('ProductService.detail', fn($id) => ProductService::detail($id));
$rpc->start(9502);
```

```php
<?php
// Workerman RPC Client (带连接池)
class RpcClient {
    private array $connections = [];
    private string $host;
    private int $port;
    private int $maxConn = 10;

    public function __construct(string $host, int $port) {
        $this->host = $host;
        $this->port = $port;
    }

    public function __call(string $method, array $params) {
        $conn = $this->getConnection();
        try {
            $conn->send(json_encode([
                'service' => $this->serviceName,
                'method' => $method,
                'params' => $params,
            ]));

            $data = $conn->recv();
            $response = json_decode($data, true);

            if ($response['code'] !== 0) {
                throw new RpcException($response['msg'], $response['code']);
            }

            return $response['data'];
        } finally {
            $this->releaseConnection($conn);
        }
    }

    private function getConnection(): TcpConnection {
        $key = "{$this->host}:{$this->port}";
        if (empty($this->connections)) {
            $conn = new TcpConnection("tcp://{$this->host}:{$this->port}");
            $conn->onClose = fn() => unset($this->connections[$key]);
            return $conn;
        }
        return array_shift($this->connections);
    }

    private function releaseConnection($conn): void {
        $this->connections[] = $conn;
    }
}

// 使用
$rpc = new RpcClient('127.0.0.1', 9502);
$rpc->serviceName = 'ProductService';
$products = $rpc->list(['page' => 1, 'limit' => 10]);
```

### CRMEB适配

```php
<?php
// CRMEB场景: 商品服务独立部署，通过RPC调用
// 服务提供者: product-server

// app/rpc/services/ProductRpcService.php
class ProductRpcService {
    public static function list(array $params): array {
        return Db::name('store_product')
            ->where('is_show', 1)
            ->where('is_del', 0)
            ->page($params['page'], $params['limit'])
            ->select()
            ->toArray();
    }

    public static function detail(int $id): array {
        return Db::name('store_product')
            ->find($id)
            ?: throw new Exception('商品不存在');
    }
}

// 启动RPC Server
$rpc = new RpcServer();
$rpc->register('ProductService.list', [ProductRpcService::class, 'list']);
$rpc->register('ProductService.detail', [ProductRpcService::class, 'detail']);
$rpc->start(9502);
```

### 验证检查点

- [ ] RPC调用延迟 < 5ms (同机器)
- [ ] 服务端异常正确序列化返回
- [ ] 连接池无泄漏
- [ ] 超时机制正常 (建议 3s)

---

## 四、Task/Async Task 异步任务

### 触发条件
- 场景：发送邮件/短信等IO密集型操作
- 场景：批量数据处理
- 场景：日志收集、图片处理

### 核心实现

#### Workerman Task

```php
<?php
// Workerman Task异步任务
use Workerman\Worker;
use Workerman\Timer;

$worker = new Worker('http://0.0.0.0:8080');
$worker->count = 4;

// TaskWorker处理耗时任务
$task = new Worker();
$task->count = 2;
$task->onMessage = function($conn, $data) {
    $job = json_decode($data, true);

    // 执行耗时任务
    $result = $this->processJob($job);

    $conn->send(json_encode(['job_id' => $job['id'], 'result' => $result]));
};
Worker::runAll();
```

#### Swoole Task/TaskWorker

```php
<?php
// Swoole TaskWorker (生产环境推荐)
$server = new Swoole\Http\Server('0.0.0.0', 9501);

$server->set([
    'task_worker_num' => 4,
    'task_ipc_mode' => SWOOLE_TASK_IPC_MSGQUEUE, // 消息队列模式
]);

$server->on('request', function($request, $response) {
    // 投递异步任务
    $taskId = $server->task(['type' => 'send_sms', 'mobile' => '13800138000']);
    $response->end(json_encode(['task_id' => $taskId]));
});

$server->on('task', function($server, $taskId, $reactorId, $data) {
    // 耗时任务在TaskWorker中执行
    switch ($data['type']) {
        case 'send_sms':
            $this->sendSms($data['mobile']);
            break;
        case 'send_email':
            $this->sendEmail($data['email'], $data['content']);
            break;
        case 'image_process':
            $this->processImage($data['path']);
            break;
        case 'batch_export':
            $this->exportData($data['sql'], $data['file']);
            break;
    }

    return "task_done:{$taskId}"; // 返回给finish回调
});

$server->on('finish', function($server, $taskId, $data) {
    echo "Task {$taskId} finished: {$data}\n";
});
```

#### 任务投递类

```php
<?php
// Swoole Task投递封装
class Task {
    public static function deliver(string $type, array $data = [], int $timeout = 30): int|false {
        global $server;

        if (!$server) return false;

        return $server->task([
            'type' => $type,
            'data' => $data,
            'timestamp' => time(),
        ], $timeout);
    }

    // CRMEB业务任务
    public static function orderPaid(int $orderId): int {
        return self::deliver('order_paid', ['order_id' => $orderId]);
    }

    public static function sendSms(string $mobile, string $content): int {
        return self::deliver('send_sms', ['mobile' => $mobile, 'content' => $content]);
    }

    public static function batchSendSms(array $mobiles, string $content): int {
        return self::deliver('batch_send_sms', ['mobiles' => $mobiles, 'content' => $content]);
    }
}
```

### 进阶变体

#### 任务队列 (基于Redis)

```php
<?php
// Redis队列驱动 (Swoole/TP6通用)
class AsyncQueue {
    private Redis $redis;

    public function __construct() {
        $this->redis = new Redis();
        $this->redis->connect('127.0.0.1', 6379);
    }

    public function push(string $queue, array $job, int $delay = 0): bool {
        $payload = json_encode([
            'id' => uniqid(),
            'queue' => $queue,
            'payload' => $job,
            'delay' => $delay,
            'timestamp' => time(),
        ]);

        if ($delay > 0) {
            // 延迟队列 (Redis Sorted Set)
            $this->redis->zAdd("queue:delayed", time() + $delay, $payload);
        } else {
            // 立即执行
            $this->redis->rPush("queue:{$queue}", $payload);
        }

        return true;
    }

    // 消费
    public function consume(string $queue, callable $handler, int $timeout = 5): void {
        $result = $this->redis->blPop(["queue:{$queue}"], $timeout);
        if ($result) {
            $job = json_decode($result[1], true);
            $handler($job['payload']);
        }
    }
}
```

### CRMEB适配

```php
<?php
// CRMEB app/services/queue/QueueServices.php 参考实现
class QueueServices {
    // 订单支付成功后处理
    public static function orderPaid(int $orderId): bool {
        $order = OrderServices::detail($orderId);

        // 1. 更新订单状态
        self::push('UpdateOrderStatus', ['id' => $orderId, 'paid_time' => time()]);

        // 2. 扣减库存 (MQ)
        self::push('DecrementStock', ['order_id' => $orderId]);

        // 3. 发送短信通知
        self::push('SendSms', [
            'mobile' => $order->user->phone,
            'template' => 'order_paid',
            'data' => ['order_no' => $order->order_no],
        ]);

        // 4. 积分变动
        self::push('IncScore', ['uid' => $order->uid, 'score' => $order->pay_price]);

        return true;
    }

    // 任务入队
    public static function push(string $name, array $data = []): bool {
        return AsyncQueue::getInstance()->push($name, $data);
    }
}
```

### 验证检查点

- [ ] 任务不丢失 (持久化到Redis)
- [ ] TaskWorker正常消费
- [ ] 任务超时正确处理
- [ ] 批量任务无内存溢出
- [ ] 队列积压告警 (>10000条)

---

## 五、Coroutine协程

### 触发条件
- 场景：需要并发执行多个IO操作
- 场景：替代Callback地狱
- 场景：高并发API请求

### 核心实现

#### Swoole协程并发

```php
<?php
// Swoole协程并发请求 (商品详情页优化)
go(function() {
    $wg = new Swoole\Coroutine\WaitGroup();

    $product = null;
    $comments = null;
    $stock = null;

    // 并发获取商品信息
    $wg->add();
    go(function() use (&$product, $id, $wg) {
        defer($wg->done());
        $product = Db::table('store_product')->find($id);
    });

    // 并发获取评论
    $wg->add();
    go(function() use (&$comments, $id, $wg) {
        defer($wg->done());
        $comments = Db::table('store_product_reply')->where('product_id', $id)->limit(5)->select();
    });

    // 并发获取库存
    $wg->add();
    go(function() use (&$stock, $id, $wg) {
        defer($wg->done());
        $stock = Cache::store('redis')->get("product_stock:{$id}");
    });

    $wg->wait(); // 等待全部完成

    return [
        'product' => $product,
        'comments' => $comments,
        'stock' => $stock,
    ];
});
```

#### Channel管道通信

```php
<?php
// 协程Channel (生产者-消费者模式)
go(function() {
    $ch = new Swoole\Coroutine\Channel(100);

    // 生产者
    go(function() use ($ch) {
        for ($i = 0; $i < 1000; $i++) {
            $ch->push(['id' => $i, 'data' => "item_{$i}"]);
        }
        $ch->close();
    });

    // 消费者 (多个)
    for ($j = 0; $j < 4; $j++) {
        go(function() use ($ch, $j) {
            while (1) {
                $data = $ch->pop();
                if ($data === false) break;
                $this->process($data);
                echo "Worker {$j} processed: {$data['id']}\n";
            }
        });
    }
});
```

#### WaitGroup并发等待

```php
<?php
// 多服务商并发调用 (聚合商品数据)
go(function() use ($productId) {
    $wg = new Swoole\Coroutine\WaitGroup();

    $price = null;
    $stock = null;
    $promotion = null;
    $freight = null;

    $wg->add(4);

    go(function() use (&$price, $productId, $wg) {
        defer($wg->done());
        $price = PriceService::get($productId);
    });

    go(function() use (&$stock, $productId, $wg) {
        defer($wg->done());
        $stock = StockService::get($productId);
    });

    go(function() use (&$promotion, $productId, $wg) {
        defer($wg->done());
        $promotion = PromotionService::getActive($productId);
    });

    go(function() use (&$freight, $productId, $wg) {
        defer($wg->done());
        $freight = FreightService::calculate($productId);
    });

    $wg->wait();

    return [
        'price' => $price,
        'stock' => $stock,
        'promotion' => $promotion,
        'freight' => $freight,
    ];
});
```

### CRMEB适配

```php
<?php
// CRMEB app/services/product/StoreProductServices.php 协程优化参考
class StoreProductServices {
    // 商品详情页 (优化后: 500ms→80ms)
    public function detail(int $id): array {
        return go(function() use ($id) {
            $wg = new Swoole\Coroutine\WaitGroup();

            $product = null;
            $category = null;
            $attrs = null;
            $replyCount = null;
            $userFav = null;

            $wg->add(5);

            go(function() use (&$product, $id, $wg) {
                defer($wg->done());
                $product = $this->model->find($id);
            });

            go(function() use (&$category, $product, $wg) {
                defer($wg->done());
                if ($product) {
                    $category = CategoryService::getPath($product->cate_id);
                }
            });

            go(function() use (&$attrs, $id, $wg) {
                defer($wg->done());
                $attrs = ProductAttrServices::getAttrs($id);
            });

            go(function() use (&$replyCount, $id, $wg) {
                defer($wg->done());
                $replyCount = ProductReplyServices::count($id);
            });

            go(function() use (&$userFav, $id, $wg) {
                defer($wg->done());
                $userFav = UserCollectServices::isFav(uid(), $id);
            });

            $wg->wait();

            return [
                'product' => $product,
                'category' => $category,
                'attrs' => $attrs,
                'reply_count' => $replyCount,
                'user_fav' => $userFav,
            ];
        });
    }
}
```

### 验证检查点

- [ ] 并发查询结果正确 (非竞态条件)
- [ ] WaitGroup::wait()正确等待
- [ ] Channel无死锁 (生产者>消费者)
- [ ] 内存无泄漏

---

## 六、Timer定时器

### 触发条件
- 场景：定时任务 (订单超时关闭、库存释放)
- 场景：心跳检测
- 场景：缓存预热

### 核心实现

```php
<?php
// Workerman Timer 定时任务
require_once __DIR__ . '/vendor/autoload.php';

use Workerman\Worker;
use Workerman\Timer;

$worker = new Worker();
$worker->onWorkerStart = function() {
    // 每小时执行: 检查超时订单
    Timer::add(3600, function() {
        echo "检查超时订单...\n";
        $timeoutOrders = Db::name('store_order')
            ->where('paid_time', 0)
            ->where('add_time', '<', time() - 7200) // 2小时超时
            ->where('status', 0)
            ->select();

        foreach ($timeoutOrders as $order) {
            OrderServices::cancel($order['id'], '超时未支付');
        }
    });

    // 每分钟执行: 库存预警
    Timer::add(60, function() {
        $lowStock = Db::name('store_product_attr')
            ->where('stock', '<', 10)
            ->where('stock', '>', 0)
            ->select();

        if (count($lowStock) > 0) {
            MailService::send('admin@example.com', '库存预警', json_encode($lowStock));
        }
    });

    // 每5分钟: 清理过期Token
    Timer::add(300, function() {
        Db::name('user_token')
            ->where('expire_time', '<', time())
            ->delete();
    });
};

Worker::runAll();
```

### CRMEB适配

```php
<?php
// CRMEB app/services/crontab/CrontabServices.php
class CrontabServices {
    public static function register(): void {
        // 定时任务注册 (参考 Workerman/Timer)

        // [1] 订单超时取消
        Timer::add(60, function() {
            self::cancelTimeoutOrders();
        }, [], true); // true=只运行一次(单进程场景)

        // [2] 拼团过期检测
        Timer::add(120, function() {
            self::checkPinkExpire();
        }, [], true);

        // [3] 优惠券过期提醒
        Timer::add(3600, function() {
            self::notifyCouponExpire();
        }, [], true);

        // [4] 每日统计
        Timer::add(86400, function() {
            self::dailyStatistics();
        }, [], true);
    }

    private static function cancelTimeoutOrders(): void {
        Db::name('store_order')
            ->where('paid_time', 0)
            ->where('add_time', '<', time() - sysConfig('order_cancel_time') * 60)
            ->chunk(100, function($orders) {
                foreach ($orders as $order) {
                    try {
                        OrderServices::cancel($order['id'], '超时未支付自动取消');
                    } catch (Exception $e) {
                        Log::error("取消订单失败: {$order['id']} - {$e->getMessage()}");
                    }
                }
            });
    }
}
```

### 验证检查点

- [ ] Timer任务不重复执行
- [ ] 定时器内存无泄漏 (Workerman需定期重启Worker)
- [ ] 任务执行时间 < 定时间隔
- [ ] 多进程下定时器正确

---

## 七、Process/进程管理

### 触发条件
- 场景：多进程数据处理
- 场景：守护进程
- 场景：进程池复用

### 核心实现

```php
<?php
// Workerman 自定义进程
use Workerman\Worker;
use Workerman\Process\Process;

$worker = new Worker();
$worker->onWorkerStart = function() {
    // 启动子进程处理队列
    for ($i = 0; $i < 4; $i++) {
        $process = new Process(function($process) {
            // 消费数据处理队列
            while (1) {
                $data = $this->redis->lPop('queue:data_process');
                if ($data) {
                    $this->processData(json_decode($data, true));
                } else {
                    usleep(100000); // 100ms
                }
            }
        });
        Worker::$processMap[$process->pid] = $process;
        $process->start();
    }
};

Worker::runAll();
```

```php
<?php
// Swoole Process池 (CPU密集型任务)
$processPool = new Swoole\Process\Pool(4);

$processPool->on('message', function($pool, $data) {
    // 处理CPU密集型任务
    $result = $this->cpuTask($data);
    $pool->write(json_encode($result));
});

$processPool->on('workerStop', function($pool, $workerId) {
    echo "Worker {$workerId} stopped\n";
});

$processPool->start();

// 投递任务
for ($i = 0; $i < 100; $i++) {
    $processPool->getProcess(($i % 4))->write(json_encode(['task_id' => $i, 'data' => '...']));
}
```

### CRMEB适配

```php
<?php
// CRMEB app/model/system/SystemQueue.php 自定义进程参考
// 用于: 批量数据导入导出、报表生成

class ExportProcess {
    public static function run(): void {
        $worker = new Process(function($process) {
            $redis = new Redis();
            $redis->connect('127.0.0.1', 6379);

            while (1) {
                $task = $redis->lPop('queue:export');
                if (!$task) {
                    sleep(1);
                    continue;
                }

                $taskData = json_decode($task, true);

                try {
                    switch ($taskData['type']) {
                        case 'order_export':
                            self::exportOrder($taskData['params']);
                            break;
                        case 'product_export':
                            self::exportProduct($taskData['params']);
                            break;
                    }

                    // 更新状态
                    $redis->hSet("export:{$taskData['id']}", 'status', 'completed');
                    $redis->hSet("export:{$taskData['id']}", 'completed_time', date('Y-m-d H:i:s'));
                } catch (Exception $e) {
                    $redis->hSet("export:{$taskData['id']}", 'status', 'failed');
                    $redis->hSet("export:{$taskData['id']}", 'error', $e->getMessage());
                }
            }
        });

        $process->start();
    }
}
```

### 验证检查点

- [ ] 子进程正常启动和回收
- [ ] 进程间通信正常
- [ ] 进程异常退出自动重启
- [ ] 无僵尸进程

---

## 八、进程间通信

### 触发条件
- 场景：主进程向TaskWorker投递任务
- 场景：多进程间共享状态
- 场景：Worker间消息广播

### 核心实现

```php
<?php
// Swoole IPC: 消息队列模式 (生产环境推荐)
$server = new Swoole\Http\Server('0.0.0.0', 9501);

$server->set([
    'task_ipc_mode' => SWOOLE_TASK_IPC_MSGQUEUE, // 消息队列
    'message_queue_key' => ftok(__FILE__, 1),      // 队列key
]);

// 投递任务
$server->task($data);

// TaskWorker接收
$server->on('task', function($server, $taskId, $reactorId, $data) {
    // 从消息队列接收
    return $this->process($data);
});

// 进程间广播 (MessageBus)
$server->on('packet', function($server, $data, $addr) {
    // UDP广播消息到所有Worker
});
```

```php
<?php
// Workerman进程间通信
class MessageBus {
    private static array $channels = [];

    public static function publish(string $channel, $message): void {
        global $worker;

        foreach ($worker->connections as $fd => $conn) {
            $conn->send(json_encode([
                'channel' => $channel,
                'message' => $message,
            ]));
        }
    }
}
```

### 验证检查点

- [ ] 消息队列持久化正常
- [ ] 多Worker消息不丢失
- [ ] 广播性能 (1000连接 < 10ms)

---

## 九、错误处理与防御式编程

### 核心模式

```php
<?php
// Swoole全局异常处理
$http = new Swoole\Http\Server('0.0.0.0', 9501);

$http->on('request', function($request, $response) use ($http) {
    try {
        $result = $this->handleRequest($request);
        $response->header('Content-Type', 'application/json');
        $response->end(json_encode(['code' => 0, 'data' => $result]));
    } catch (ValidationException $e) {
        $response->status(422);
        $response->end(json_encode(['code' => 422, 'msg' => $e->getMessage(), 'errors' => $e->errors()]));
    } catch (BusinessException $e) {
        $response->status(400);
        $response->end(json_encode(['code' => $e->getCode(), 'msg' => $e->getMessage()]));
    } catch (Throwable $e) {
        Log::error("Swoole Error: {$e->getMessage()} | {$e->getFile()}:{$e->getLine()}");
        $response->status(500);
        $response->end(json_encode(['code' => 500, 'msg' => '系统错误']));
    }
});

// Swoole协程内异常捕获
go(function() {
    try {
        $result = CoHttpClient::get('http://example.com/api');
    } catch (Throwable $e) {
        Log::error("Coroutine error: " . $e->getMessage());
        $result = null;
    }
});
```

### CRMEB适配

```php
<?php
// CRMEB app/common.php 全局异常处理
use app\exception\BusinessException;
use app\exception\ValidateException;

set_exception_handler(function(Throwable $e) {
    $code = $e instanceof ValidateException ? 422
             : ($e instanceof BusinessException ? $e->getCode() : 500);

    $response = [
        'code' => $code ?: 500,
        'msg' => $e->getMessage(),
    ];

    if (sysConfig('system_debug')) {
        $response['debug'] = [
            'file' => $e->getFile(),
            'line' => $e->getLine(),
            'trace' => $e->getTraceAsString(),
        ];
    }

    if (defined('IN_WORKERMAN')) {
        global $response;
        $response->status($code);
        $response->end(json_encode($response));
    } else {
        json($response, $code)->send();
        die;
    }
});

// Swoole模式入口
// public/index.php (swoole)
$http = new Swoole\Http\Server('0.0.0.0', 9501);
$http->set(['worker_num' => 4]);

$http->on('request', function($request, $response) {
    // 模拟TP6请求
    ob_start();
    require __DIR__ . '/../route/app.php';
    $content = ob_get_clean();

    $response->end($content);
});

$http->start();
```

### 验证检查点

- [ ] Throwable全部捕获
- [ ] 日志记录完整 (file, line, trace)
- [ ] 生产环境不泄露调试信息
- [ ] 协程内异常不导致Worker崩溃

---

## 参考来源

- **CRMEB源码**: github.com/crmeb/CRMEB — Workerman HTTP Server, WebSocket Server, RPC Server, Task/TaskWorker, Process/ProcessPool, Timer, Coroutine, Channel/WaitGroup
- **Workerman文档**: workerman.net
- **Swoole文档**: wiki.swoole.com
