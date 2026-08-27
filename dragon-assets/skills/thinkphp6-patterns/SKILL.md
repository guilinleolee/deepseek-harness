---
license: UNKNOWN
triggers: ["thinkphp6 patterns", "ThinkPHP 6 Patterns"]
---
# ThinkPHP 6 Patterns

> ThinkPHP 6是PHP后端MVC框架，CRMEB基于TP6构建电商业务。本SKILL覆盖路由、中间件、依赖注入、ORM、验证器、异常处理、Facade、多应用等核心模式。

## 触发词
`/thinkphp` `/thinkphp6` `/tp6` `/tp6-middleware` `/tp6-orm`

---

## 一、路由与请求处理

### 触发条件
- 场景：RESTful API设计与路由分组
- 场景：路由中间件、参数约束
- 场景：注解路由、路由缓存

### 核心实现

#### 基础路由

```php
<?php
// app/route.php — 路由定义
use think\facade\Route;

// 单路由
Route::get('product/:id', 'product/detail');
Route::post('order/create', 'order/create');
Route::put('order/:id', 'order/update');
Route::delete('order/:id', 'order/delete');

// 路由分组 (推荐按模块分组)
Route::group('api', function() {
    // 认证路由组
    Route::group('auth', function() {
        Route::post('login', 'auth/login');
        Route::post('register', 'auth/register');
        Route::post('refresh', 'auth/refresh');
        Route::get('logout', 'auth/logout')->middleware(\app\middleware\Auth::class);
    });

    // 商品路由组
    Route::group('product', function() {
        Route::get('list', 'product/list');
        Route::get(':id', 'product/detail');
        Route::post('create', 'product/create')->middleware(\app\middleware\Auth::class);
        Route::put(':id', 'product/update');
        Route::delete(':id', 'product/delete');
    })->middleware([\app\middleware\Cors::class]);

    // 订单路由组 (需要登录)
    Route::group('order', function() {
        Route::post('create', 'order/create');
        Route::get('list', 'order/list');
        Route::get(':id', 'order/detail');
    })->middleware([\app\middleware\Auth::class, \app\middleware\RateLimiter::class]);
});

// 资源路由 (CRUD自动化)
Route::resource('product', 'Product');
// 生成: product/, product/create, product/:id, product/:id/edit, product/:id, product/:id

// 路由别名
Route::alias('product', 'admin/Product');
```

#### 路由中间件

```php
<?php
// 路由级中间件 (app/route.php)
Route::group('api', function() {
    Route::get('user/profile', 'user/profile');
})->middleware([\app\middleware\Cors::class, \app\middleware\Auth::class, \app\middleware\RateLimiter::class]);

// 完整路由定义
Route::post('order/create', 'order/create')
    ->middleware([\app\middleware\Auth::class])
    ->allowCrossDomain()
    ->validate(\app\validate\OrderCreateValidate::class)
    ->layer('cache'); // 结果缓存
```

#### 参数约束与ext

```php
<?php
// 路由变量约束
Route::get('product/:id', 'product/detail')
    ->pattern(['id' => '\d+']); // id必须是数字

Route::get('user/:name', 'user/profile')
    ->pattern(['name' => '[a-zA-Z]+']); // name必须是字母

// 路由ext (URL后缀)
Route::get('article/:id', 'article/detail')
    ->ext('html'); // 支持 /article/1 和 /article/1.html

// 路由域名
Route::domain('api.crmeb.com', function() {
    Route::get('product/list', 'product/list');
});

// 路由分组变量
Route::group('v{version}', function() {
    Route::get('product/list', 'product/list');
})->pattern(['version' => '\d+']);
```

### 进阶变体

#### 注解路由 (PHP8 Attribute)

```php
<?php
// app/controller/v2/Product.php
#[Route('api/v1/product')]
class ProductController extends BaseController
{
    #[Route('GET list')]
    public function list(Request $request): Json
    {
        $page = $request->param('page/d', 1);
        $limit = $request->param('limit/d', 10);

        return json(['list' => [], 'count' => 0]);
    }

    #[Route('GET :id')]
    #[Param('id', 'id', 'require|number')]
    public function detail(int $id): Json
    {
        return json(['id' => $id]);
    }

    #[Route('POST create')]
    #[Middleware(\app\middleware\Auth::class)]
    public function create(Request $request): Json
    {
        return json(['code' => 0, 'msg' => '创建成功']);
    }
}
```

#### 路由缓存 (生产环境)

```php
<?php
// app/route.php
// 生产环境开启路由缓存 (需禁用)
// Route::config('route', ['url_route_cache' => runtime_path('route.php')]);

// 闭包路由 (简单场景)
Route::get('version', function() {
    return json(['version' => '2.0.0', 'env' => app()->environment()]);
});
```

### CRMEB适配

```php
<?php
// CRMEB app/route/api.php 参考
use think\facade\Route;

// API v2版本
Route::group('v2', function() {
    // 商城模块
    Route::group('store', function() {
        // 商品
        Route::get('product/list', 'crmeb.StoreProduct/list');
        Route::get('product/detail/:id', 'crmeb.StoreProduct/detail');
        Route::get('product/hot', 'crmeb.StoreProduct/hot');
        Route::get('product/banner', 'crmeb.StoreProduct/bannerList');

        // 分类
        Route::get('category/list', 'crmeb.StoreCategory/list');
        Route::get('category/tree', 'crmeb.StoreCategory/tree');

        // 购物车
        Route::get('cart/list', 'crmeb.StoreCart/list');
        Route::post('cart/add', 'crmeb.StoreCart/add');
        Route::post('cart/del', 'crmeb.StoreCart/del');

        // 订单
        Route::post('order/create', 'crmeb.StoreOrder/create');
        Route::get('order/list', 'crmeb.StoreOrder/list');
    })->middleware([\app\middleware\Cors::class, \app\middleware\ApiAuth::class]);
});
```

### 验证检查点

- [ ] 路由分发正确，HTTP方法匹配
- [ ] 中间件按顺序执行
- [ ] 参数约束生效
- [ ] 路由分组prefix正确

---

## 二、中间件

### 触发条件
- 场景：认证授权、日志记录、CORS跨域
- 场景：限流、参数处理、错误捕获
- 场景：多租户上下文传递

### 核心实现

#### 全局中间件

```php
<?php
// app/middleware.php 全局中间件注册
return [
    \app\middleware\Init::class,      // 初始化
    \app\middleware\Cors::class,     // CORS跨域
    \app\middleware\Log::class,      // 请求日志
];
```

#### 认证中间件

```php
<?php
// app/middleware/Auth.php
class Auth extends Middleware
{
    public function handle($request, \Closure $next)
    {
        $token = $request->header('Authorization')
            ?: $request->param('token', '');

        if (!$token) {
            return json(['code' => 401, 'msg' => '请先登录'])->code(401);
        }

        // Token验证 (JWT/自定义)
        $payload = \app\common\Jwt::verify($token);
        if (!$payload) {
            return json(['code' => 401, 'msg' => 'Token无效或已过期'])->code(401);
        }

        // 注入用户上下文
        $request->uid = $payload['uid'];
        $request->user = UserModel::find($payload['uid']);

        return $next($request);
    }
}
```

#### 限流中间件

```php
<?php
// app/middleware/RateLimiter.php (基于Redis滑动窗口)
class RateLimiter extends Middleware
{
    public function handle($request, \Closure $next, int $maxRequests = 60, int $window = 60)
    {
        $key = 'rate_limit:' . $this->getClientKey($request);

        $redis = app()->cache->getStore()->handler();
        $current = $redis->incr($key);

        if ($current === 1) {
            $redis->expire($key, $window);
        }

        if ($current > $maxRequests) {
            return json([
                'code' => 429,
                'msg' => '请求过于频繁，请稍后再试',
                'retry_after' => $redis->ttl($key),
            ])->code(429);
        }

        $response = $next($request);

        // 添加限流头
        $response->header([
            'X-RateLimit-Limit' => $maxRequests,
            'X-RateLimit-Remaining' => max(0, $maxRequests - $current),
        ]);

        return $response;
    }

    private function getClientKey($request): string {
        return md5($request->ip() . ':' . ($request->uid ?? 'guest'));
    }
}
```

#### CORS中间件

```php
<?php
// app/middleware/Cors.php
class Cors extends Middleware
{
    public function handle($request, \Closure $next)
    {
        if ($request->isOptions()) {
            return json(['msg' => 'ok'])->code(204)
                ->header([
                    'Access-Control-Allow-Origin' => '*',
                    'Access-Control-Allow-Methods' => 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers' => 'Authorization, Content-Type, X-Requested-With, Token',
                    'Access-Control-Max-Age' => 86400,
                ]);
        }

        $response = $next($request);

        return $response->header([
            'Access-Control-Allow-Origin' => '*',
            'Access-Control-Allow-Credentials' => 'true',
        ]);
    }
}
```

### 进阶变体

#### 多租户中间件

```php
<?php
// app/middleware/Tenant.php
class Tenant extends Middleware
{
    public function handle($request, \Closure $next)
    {
        $tenantId = $request->header('X-Tenant-Id')
            ?: $request->param('tenant_id', 0);

        if (!$tenantId) {
            return json(['code' => 400, 'msg' => '缺少租户标识'])->code(400);
        }

        $tenant = TenantModel::find($tenantId);
        if (!$tenant || $tenant->status !== 1) {
            return json(['code' => 403, 'msg' => '租户不存在或已禁用'])->code(403);
        }

        // 注入租户上下文
        $request->tenantId = $tenantId;
        $request->tenant = $tenant;

        // 租户数据隔离
        Db::setConfig([
            'prefix' => "t_{$tenantId}_",
        ]);

        return $next($request);
    }
}
```

### CRMEB适配

```php
<?php
// CRMEB app/middleware/ApiAuth.php
class ApiAuth extends Middleware
{
    public function handle($request, \Closure $next)
    {
        $token = $request->header('token') ?: $request->param('token', '');

        if (!$token) {
            return json(['code' => 410, 'msg' => '请登录'])->code(401);
        }

        // CRMEB Token验证 (基于Redis)
        $userInfo = app()->cache->get("user_info:{$token}");
        if (!$userInfo) {
            return json(['code' => 401, 'msg' => '登录已过期'])->code(401);
        }

        $userInfo = is_array($userInfo) ? $userInfo : json_decode($userInfo, true);

        $request->uid = $userInfo['uid'];
        $request->userInfo = $userInfo;

        // 刷新Token有效期
        app()->cache->set("user_info:{$token}", $userInfo, 7 * 86400);

        return $next($request);
    }
}
```

### 验证检查点

- [ ] 中间件顺序正确
- [ ] 认证中间件正确拦截未登录请求
- [ ] 限流头正确返回
- [ ] CORS预检请求正常处理

---

## 三、依赖注入与服务容器

### 触发条件
- 场景：业务逻辑解耦
- 场景：服务单例化
- 场景：工厂模式与依赖注入

### 核心实现

#### 服务绑定

```php
<?php
// app/provider.php 服务容器绑定
use app\common\repositories\ProductRepository;
use app\common\repositories\OrderRepository;

return [
    // 接口绑定实现
    'ProductRepository' => ProductRepository::class,
    'OrderRepository' => OrderRepository::class,

    // 单例绑定 (业务Service推荐)
    'UserServices' => \app\services\user\UserServices::class,
    'ProductServices' => \app\services\product\ProductServices::class,
    'OrderServices' => \app\services\order\OrderServices::class,
];
```

#### Services层设计

```php
<?php
// app/services/product/StoreProductServices.php (CRUD基类)
class StoreProductServices
{
    protected $repository;

    public function __construct(ProductRepository $repository)
    {
        $this->repository = $repository;
    }

    public function list(array $params): array
    {
        $query = $this->repository->query()
            ->where('is_show', 1)
            ->where('is_del', 0);

        // 分类筛选
        if (!empty($params['cate_id'])) {
            $query->whereIn('cate_id', $this->getCateIds($params['cate_id']));
        }

        // 关键词搜索
        if (!empty($params['keyword'])) {
            $query->where('store_name', 'like', '%' . $params['keyword'] . '%');
        }

        // 价格区间
        if (isset($params['price_min'])) {
            $query->where('price', '>=', $params['price_min']);
        }
        if (isset($params['price_max'])) {
            $query->where('price', '<=', $params['price_max']);
        }

        // 排序
        $orderField = $params['order'] ?? 'sort';
        $orderType = $params['sort'] ?? 'desc';
        $query->order($orderField, $orderType);

        return $query->page($params['page'] ?? 1, $params['limit'] ?? 10)->select()->toArray();
    }

    public function detail(int $id): ?array
    {
        $product = $this->repository->find($id);
        if (!$product || $product['is_del']) {
            return null;
        }

        // 关联数据
        $product['category'] = CategoryServices::get($product['cate_id']);
        $product['attrs'] = ProductAttrServices::getAttrs($id);
        $product['reply'] = ProductReplyServices::getCount($id);

        return $product;
    }

    public function create(array $data): int
    {
        Db::startTrans();
        try {
            $id = $this->repository->create($data);

            // 规格处理
            if (!empty($data['attrs'])) {
                ProductAttrServices::setAttrs($id, $data['attrs']);
            }

            Db::commit();
            return $id;
        } catch (Exception $e) {
            Db::rollback();
            throw $e;
        }
    }
}
```

#### Repository模式

```php
<?php
// app/common/repositories/ProductRepository.php
class ProductRepository
{
    protected $model = StoreProduct::class;

    public function query(): Query
    {
        return Db::name($this->model::tableName())
            ->alias('p')
            ->join('store_category c', 'p.cate_id=c.id', 'LEFT');
    }

    public function find(int $id): ?array
    {
        return $this->query()->find($id);
    }

    public function create(array $data): int
    {
        $data['add_time'] = time();
        $data['add_ip'] = request()->ip();
        return Db::name($this->model::tableName())->insertGetId($data);
    }

    public function update(int $id, array $data): bool
    {
        $data['update_time'] = time();
        return Db::name($this->model::tableName())->where('id', $id)->update($data) !== false;
    }

    public function delete(int $id): bool
    {
        return $this->update($id, ['is_del' => 1, 'delete_time' => time()]);
    }
}
```

### 进阶变体

#### 自动注入

```php
<?php
// 控制器方法参数自动注入
class ProductController extends BaseController
{
    // Request自动注入
    public function detail(Request $request, int $id): Json
    {
        // $request已自动注入
        return json($request->userInfo);
    }

    // Services自动注入
    public function list(StoreProductServices $services): Json
    {
        // $services已自动注入
        return json($services->list(request()->param()));
    }

    // 多个Services
    public function create(StoreProductServices $product, StoreProductAttrServices $attr): Json
    {
        // 两个服务都自动注入
    }
}
```

### CRMEB适配

```php
<?php
// CRMEB app/services/StoreProductServices.php
// TP6单例服务 (每次请求实例化一次)
class StoreProductServices
{
    private static $instance = null;

    public static function getInstance()
    {
        if (!self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    // 静态调用兼容
    public function list(array $params = []): array
    {
        $query = StoreProduct::where('is_show', 1)->where('is_del', 0);

        if (!empty($params['cid'])) {
            $cids = StoreCategoryServices::getInstance()->getChildIds($params['cid']);
            $query->whereIn('cate_id', $cids);
        }

        if (!empty($params['keyword'])) {
            $query->where('store_name', 'like', "%{$params['keyword']}%");
        }

        return $query->page($params['page'] ?? 1, $params['limit'] ?? 10)
            ->order('sort desc, id desc')
            ->select()
            ->toArray();
    }
}

// 静态调用 (兼容旧代码)
StoreProductServices::getInstance()->list($params);
```

### 验证检查点

- [ ] 循环依赖正确检测 (容器会报错)
- [ ] 单例服务只实例化一次
- [ ] Services层正确处理事务

---

## 四、ORM与数据库

### 触发条件
- 场景：关联查询 (一对一/一对多/多对多)
- 场景：预加载与懒加载
- 场景：聚合查询与分组

### 核心实现

#### 模型定义

```php
<?php
// app/model/product/StoreProduct.php
class StoreProduct extends BaseModel
{
    protected $name = 'store_product';
    protected $pk = 'id';

    // 自动时间戳
    protected $autoWriteTimestamp = true;
    protected $createTime = 'add_time';
    protected $updateTime = 'update_time';

    // 类型转换
    protected $type = [
        'price' => 'decimal:2',
        'ot_price' => 'decimal:2',
        'count' => 'integer',
    ];

    // 关联定义
    public function category(): BelongsTo
    {
        return $this->belongsTo(StoreCategory::class, 'cate_id');
    }

    public function attrs(): HasMany
    {
        return $this->hasMany(ProductAttr::class, 'product_id');
    }

    public function reply(): HasMany
    {
        return $this->hasMany(ProductReply::class, 'product_id');
    }

    // 访问器
    public function getPriceAttr($value): float
    {
        return bcdiv($value, 100, 2); // 分->元
    }

    // 修改器
    public function setPriceAttr($value): int
    {
        return (int)bcmul($value, 100, 0); // 元->分
    }
}
```

#### 关联查询

```php
<?php
// 一对多关联查询
$products = StoreProduct::with(['category', 'attrs'])
    ->where('is_show', 1)
    ->select();

// 预加载 + 条件过滤
$products = StoreProduct::with(['attrs' => function($query) {
        $query->where('type', 1);
    }])
    ->select();

// 多对多关联 (带 pivot 字段)
class Product extends Model {
    public function tags(): BelongsToMany
    {
        return $this->belongsToMany(
            Tag::class,
            'product_tag',
            'tag_id',
            'product_id'
        )-> pivot(['sort' => 'sort']); // pivot额外字段
    }
}

// 聚合查询
$stats = OrderModel::where('uid', $uid)
    ->group('status')
    ->columnRaw('status, COUNT(*) as count, SUM(pay_price) as amount');

// hasWhere复杂条件
$hasProducts = Category::hasWhere('products', function($q) {
        $q->where('is_show', 1)->where('stock', '<', 10);
    })
    ->withCount('products as low_stock_count')
    ->select();
```

#### 分页查询

```php
<?php
// 标准分页
$list = StoreProduct::where('is_del', 0)
    ->paginate(['list_rows' => 10, 'page' => $page])
    ->toArray();

// 返回结构
return [
    'list' => $list['data'],
    'page' => $list['current_page'],
    'limit' => $list['per_page'],
    'total' => $list['total'],
    'hasMore' => $list['last_page'] > $list['current_page'],
];

// 手动分页 (大数据量)
$list = Db::name('store_product')
    ->where($where)
    ->page($page, $limit)
    ->order('id desc')
    ->select();
$total = Db::name('store_product')->where($where)->count();
```

### 进阶变体

#### 软删除与全局查询

```php
<?php
// 模型软删除
class StoreProduct extends BaseModel
{
    protected $deleteTime = 'delete_time';

    // 全局查询范围 (自动追加 is_del=0)
    protected function base($query) {
        $query->where('is_show', 1);
    }
}

// 忽略全局范围
$product = StoreProduct::withoutGlobalScope()
    ->find($id);
```

#### 模型事件

```php
<?php
class StoreProduct extends BaseModel
{
    protected static function onAfterWrite($model) {
        // 写入后: 更新ES索引
        Event::trigger('ProductUpdated', ['id' => $model->id]);
    }

    protected static function onAfterDelete($model) {
        // 删除后: 清理缓存
        Cache::delete("product:{$model->id}");
    }
}
```

### CRMEB适配

```php
<?php
// CRMEB app/model/product/StoreProduct.php 参考
class StoreProduct extends BaseModel
{
    protected $name = 'store_product';
    protected $pk = 'id';

    protected $autoWriteTimestamp = 'datetime';

    // 关联
    public function category(): BelongsTo
    {
        return $this->belongsTo(StoreCategory::class, 'cate_id', 'id');
    }

    public function reply(): HasMany
    {
        return $this->hasMany(ProductReply::class, 'product_id');
    }

    public function cart(): HasMany
    {
        return $this->hasMany(StoreCart::class, 'product_id');
    }

    // 辅助方法
    public static function search(string $keyword, int $page = 1, int $limit = 20): array
    {
        $query = self::with(['category'])
            ->where('is_del', 0)
            ->where('is_show', 1);

        if ($keyword) {
            $query->where('store_name|keyword', 'like', "%{$keyword}%");
        }

        $list = $query->order('sort desc, id desc')
            ->page($page, $limit)
            ->select();

        foreach ($list as &$item) {
            $item['shop_price'] = $item['price'];
        }

        return $list->toArray();
    }
}
```

### 验证检查点

- [ ] 关联预加载无N+1查询
- [ ] 软删除正确过滤
- [ ] 分页参数安全 (limit防注入)

---

## 五、验证器与场景

### 触发条件
- 场景：用户输入验证
- 场景：多场景验证 (创建/更新)
- 场景：自定义验证规则

### 核心实现

```php
<?php
// app/validate/ProductValidate.php
class ProductValidate extends Validate
{
    protected $rule = [
        'store_name' => 'require|max:200',
        'cate_id'    => 'require|number',
        'price'      => 'require|float|egt:0',
        'ot_price'   => 'float|egt:price',
        'stock'      => 'require|number|egt:0',
        'image'      => 'require|url',
    ];

    protected $message = [
        'store_name.require' => '请填写商品名称',
        'store_name.max'    => '商品名称最多200字符',
        'cate_id.require'   => '请选择商品分类',
        'price.require'     => '请填写商品价格',
        'price.float'       => '价格格式不正确',
        'stock.require'     => '请填写商品库存',
    ];

    // 场景验证
    protected $scene = [
        'create' => ['store_name', 'cate_id', 'price', 'stock', 'image'],
        'update' => ['store_name', 'cate_id', 'price'],
        'search' => ['keyword'],
    ];

    // 自定义验证规则
    protected function checkUnique($value, $rule, $data, $field): bool
    {
        $exists = Db::name('store_product')
            ->where('store_name', $value)
            ->where('is_del', 0)
            ->when(isset($data['id']), fn($q) => $q->where('id', '<>', $data['id']))
            ->find();

        return !$exists;
    }
}
```

```php
<?php
// 控制器中使用验证器
class ProductController extends BaseController
{
    public function create(ProductValidate $validate): Json
    {
        if (!$validate->scene('create')->check(request()->post())) {
            return json(['code' => 400, 'msg' => $validate->getError()]);
        }

        $data = $validate->post();
        $id = StoreProductServices::getInstance()->create($data);

        return json(['code' => 0, 'msg' => '添加成功', 'id' => $id]);
    }

    public function update(ProductValidate $validate): Json
    {
        if (!$validate->scene('update')->check(request()->post())) {
            return json(['code' => 400, 'msg' => $validate->getError()]);
        }

        $data = $validate->post();
        $id = $data['id'];
        unset($data['id']);

        StoreProductServices::getInstance()->update($id, $data);

        return json(['code' => 0, 'msg' => '更新成功']);
    }
}
```

### 进阶变体

#### 对象验证器

```php
<?php
// 对象验证 (购物车、商品多属性)
class CartValidate extends Validate
{
    protected $rule = [
        'product_id'  => 'require|number',
        'product_attr_unique' => 'require',
        'cart_num'    => 'require|number|gt:0|elt:99',
    ];

    // 批量验证
    public function checkItems(array $items): bool|array
    {
        foreach ($items as $item) {
            if (!$this->check($item)) {
                return [false, $this->getError(), $item];
            }
        }
        return true;
    }
}
```

### CRMEB适配

```php
<?php
// CRMEB app/validate/StoreProductValidate.php
class StoreProductValidate extends Validate
{
    protected $rule = [
        'store_name'   => 'require|max:200',
        'cate_id'      => 'require|number|egt:1',
        'price'         => 'require|number|gt:0',
        'ot_price'      => 'number|gt:0|egt:price',
        'cost'          => 'number|egt:0',
        'stock'         => 'require|number|egt:0',
        'image'         => 'require|max:256',
        'slider_image'  => 'max:1000',
        'description'   => 'max:10000',
    ];

    protected $message = [
        'store_name.require'  => '请填写商品名称',
        'store_name.max'      => '商品名称不能超过200个字符',
        'cate_id.require'     => '请选择商品分类',
        'price.require'       => '请填写商品价格',
        'price.gt'            => '商品价格必须大于0',
        'ot_price.gt'        => '市场价必须大于商品价格',
        'stock.require'       => '请填写商品库存',
        'stock.egt'          => '库存不能为负数',
    ];

    protected $scene = [
        'add'  => ['store_name', 'cate_id', 'price', 'stock', 'image'],
        'edit' => ['store_name', 'cate_id', 'price', 'image'],
    ];
}
```

### 验证检查点

- [ ] 必填字段正确拦截
- [ ] 类型验证正确
- [ ] 场景切换正确过滤字段
- [ ] 自定义规则正确注册

---

## 六、异常处理

### 触发条件
- 场景：业务异常抛出
- 场景：统一错误响应
- 场景：异常日志与监控

### 核心实现

```php
<?php
// app/exception/Handler.php
class ExceptionHandler extends \think\exception\Handle
{
    public function render($request, Throwable $e): Response
    {
        // API请求返回JSON
        if (request()->isAjax() || request()->isJson()) {
            return $this->renderJson($e);
        }

        // 页面请求返回错误页
        return $this->renderHtml($e);
    }

    private function renderJson(Throwable $e): Json
    {
        $code = 500;
        $msg = '系统错误';

        if ($e instanceof BusinessException) {
            $code = $e->getCode() ?: 400;
            $msg = $e->getMessage();
        } elseif ($e instanceof ValidateException) {
            $code = 422;
            $msg = $e->getMessage();
        } elseif ($e instanceof HttpException) {
            $code = $e->getStatusCode();
            $msg = $e->getMessage() ?: $this->getHttpStatusMessage($code);
        }

        $data = ['code' => $code, 'msg' => $msg];

        if (app()->isDebug()) {
            $data['debug'] = [
                'message' => $e->getMessage(),
                'file' => $e->getFile(),
                'line' => $e->getLine(),
                'trace' => $e->getTraceAsString(),
            ];
        }

        Log::error("Exception: {$e->getMessage()} | {$e->getFile()}:{$e->getLine()}");

        return json($data, $code);
    }
}
```

#### 业务异常

```php
<?php
// app/exception/BusinessException.php
class BusinessException extends Exception
{
    protected int $errCode = 400;

    public function __construct(string $message = '', int $errCode = 400)
    {
        parent::__construct($message);
        $this->errCode = $errCode;
    }

    public function getCode(): int
    {
        return $this->errCode;
    }
}

// 使用
throw new BusinessException('库存不足', 4001);
throw new BusinessException('订单不存在', 4042);
```

### CRMEB适配

```php
<?php
// CRMEB app/common.php 统一响应
function json($data = [], $code = 0, $msg = ''): Json
{
    return json([
        'code' => $code,
        'msg' => $msg ?: ($code == 0 ? 'ok' : 'error'),
        'time' => time(),
        'data' => $data,
    ]);
}

// 快捷响应
function success($data = [], $msg = 'ok'): Json
{
    return json($data, 0, $msg);
}

function fail($msg = '请求失败', $code = 400): Json
{
    return json([], $code, $msg);
}

// 控制器中使用
return success($product, '获取成功');
return fail('商品不存在', 404);

// 异常抛出
throw new BusinessException('请先登录', 410);
throw new BusinessException('权限不足', 403);
```

### 验证检查点

- [ ] 所有异常被捕获，不泄露堆栈
- [ ] 日志记录完整
- [ ] 生产环境关闭debug

---

## 七、Facade门面

### 触发条件
- 场景：静态调用服务层
- 场景：Facade替换实现
- 场景：多缓存/日志驱动切换

### 核心实现

```php
<?php
// 定义Facade (app/common.php)
use think\Facade;

Facade::bind([
    'cache'  => \app\common\Cache::class,
    'config' => \app\common\Config::class,
    'wechat' => \app\common\Wechat::class,
]);

// 使用
Cache::get('product_list');
Config::get('system.name');
Wechat::sendTemplate($openid, $template_id, $data);

// 自定义Facade
class Cache extends Facade
{
    protected static function getFacadeClass(): string
    {
        return \app\common\Cache::class;
    }
}
```

### CRMEB适配

```php
<?php
// CRMEB app/common/Cache.php
class Cache
{
    public static function get(string $key, $default = null) {
        $store = config('cache.default');
        return $store === 'redis'
            ? self::redis()->get($key)
            : self::file()->get($key, $default);
    }

    public static function set(string $key, $value, int $ttl = 0): bool {
        $store = config('cache.default');
        return $store === 'redis'
            ? self::redis()->setex($key, $ttl, $value)
            : self::file()->set($key, $value, $ttl);
    }
}

// TP6原生
Cache::get('key');
Db::name('table')->find();
Config::get('app.app_debug');
Route::get('uri', 'controller/action');
Validate::rule(['name' => 'require']);
Log::error('message');
```

### 验证检查点

- [ ] Facade静态调用正确代理到实际类
- [ ] 单元测试时可替换实现

---

## 八、多应用与模块化

### 触发条件
- 场景：多应用架构 (admin/api/wap/h5)
- 场景：应用间共享代码
- 场景：独立应用部署

### 核心实现

```php
<?php
// 目录结构
// app/
// ├── controller/
// │   └── (默认应用)
// ├── admin/        # 管理后台
// │   └── controller/
// ├── api/           # API接口
// │   └── controller/
// ├── wap/           # 手机H5
// │   └── controller/
// └── common/         # 公共代码

// route/app.php 多应用路由
use think\facade\Route;

Route::group('admin', function() {
    Route::get('dashboard', 'admin/dashboard');
    Route::resource('product', 'admin.product');
    Route::resource('order', 'admin.order');
})->middleware(\app\middleware\Auth::class, 'admin');

// 应用中间件配置 (app/admin/middleware.php)
return [
    \app\middleware\AdminAuth::class,
];
```

### 验证检查点

- [ ] 多应用路由分发正确
- [ ] 应用间公共代码无冲突
- [ ] 应用独立配置生效

---

## 参考来源

- **CRMEB源码**: github.com/crmeb/CRMEB — ThinkPHP 6 Route groups, middleware, dependency injection, ORM associations, validators with scenes, custom exception handling, Facade, multi-app
- **ThinkPHP6文档**: www.kancloud.cn/manual/thinkphp6_0
