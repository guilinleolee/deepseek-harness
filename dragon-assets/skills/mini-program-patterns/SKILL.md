---
license: UNKNOWN
triggers: ["mini program patterns", "mini-program-patterns"]
---
# mini-program-patterns

## L0: 一句话描述
微信小程序 + 多端商城（H5/App/小程序）统一开发模式速查手册

## L1: 使用场景
适用于电商 SaaS 多端分发、CRMEB 系小程序商城开发、ThinkPHP 后端 + 小程序前端联调、微信支付/分享/订阅通知集成等场景。天龙 45-01 电商运营、03 构建师、35-02 社媒运营等岗位直接调用。

## L2: 详细文档

### 一、微信小程序核心架构

#### 1.1 技术栈矩阵

| 终端 | 前端框架 | 后端 | 数据库 | 缓存 |
|------|---------|------|--------|------|
| 微信小程序 | Taro3 / uni-app (Vue3) | ThinkPHP6 | MySQL | Redis |
| 支付宝小程序 | Taro3 / uni-app | ThinkPHP6 | MySQL | Redis |
| H5 (移动端) | Vue3 + Vant | ThinkPHP6 | MySQL | Redis |
| PC 管理端 | Vue3 + Element Plus | ThinkPHP6 | MySQL | Redis |
| App (React Native) | Taro3 / uni-app | ThinkPHP6 | MySQL | Redis |

#### 1.2 分包加载模式（重点）

```javascript
// project.config.json
{
  "appid": "your-appid",
  "setting": {
    "urlCheck": false,
    "es6": true,
    "minified": true
  },
  "packages": ["pages/index/index", "pages/category/category"],
  "subPackages": [
    {
      "root": "pages/subPackage/",
      "pages": [
        "goods/detail",
        "order/confirm",
        "user/wallet"
      ]
    }
  ]
}
```

#### 1.3 插件集成（支付/分享）

```json
// app.json
{
  "plugins": {
    "route-planner": {
      "version": "1.0.0",
      "provider": "wxabcd1234"
    }
  }
}
```

---

### 二、CRMEB 小程序端集成

#### 2.1 模板项目结构

```
crmeb_mp_v6/
├── src/                          # 源码目录
│   ├── api/                      # API 请求封装
│   │   ├── index.js             # 请求基类 (ThinkPHP API)
│   │   ├── user.js              # 用户 API
│   │   ├── product.js            # 商品 API
│   │   └── order.js             # 订单 API
│   ├── utils/                    # 工具函数
│   │   ├── request.js           # axios 风格请求
│   │   ├── auth.js              # 登录态校验
│   │   ├── siteConfig.js        # 站点配置
│   │   └── pay.js               # 微信支付封装
│   ├── components/               # 业务组件
│   │   ├── product-card/
│   │   ├── price-detail/
│   │   └── coupon-picker/
│   ├── pages/                   # 页面
│   │   ├── index/               # 首页
│   │   ├── category/            # 分类
│   │   ├── product/             # 商品详情
│   │   ├── cart/                # 购物车
│   │   ├── order/               # 订单
│   │   ├── user/                # 个人中心
│   │   └── activity/             # 活动页面
│   └── store/                   # 状态管理
│       └── modules/
├── config/
│   └── api.js                   # ThinkPHP API 基础地址
└── package.json
```

#### 2.2 API 请求封装（对接 ThinkPHP6）

```javascript
// src/api/index.js
const baseURL = 'https://api.your-crmeb.com';

class Request {
  constructor() {
    this.baseURL = baseURL;
  }

  request(options) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: this.baseURL + options.url,
        method: options.method || 'GET',
        data: options.data || {},
        header: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + wx.getStorageSync('token')
        },
        success: (res) => {
          if (res.data.code === 200) {
            resolve(res.data.data);
          } else if (res.data.code === 401) {
            // token 过期，跳转登录
            wx.navigateTo({ url: '/pages/login/index' });
          } else {
            wx.showToast({ title: res.data.msg, icon: 'none' });
            reject(res.data);
          }
        },
        fail: reject
      });
    });
  }

  get(url, data) { return this.request({ url, data, method: 'GET' }); }
  post(url, data) { return this.request({ url, data, method: 'POST' }); }
}

export default new Request();
```

#### 2.3 微信支付封装

```javascript
// src/utils/pay.js
import request from '../api/index';

export async function wxPay(orderId) {
  // 1. 向 ThinkPHP 后端发起支付
  const { data: payInfo } = await request.post('/api/pay/wxPay', {
    order_id: orderId,
    pay_channel: 'wechat'
  });

  // 2. 调起微信支付
  const payment = await wx.requestPayment({
    timeStamp: payInfo.timeStamp,
    nonceStr: payInfo.nonceStr,
    package: payInfo.package,
    signType: payInfo.signType,
    paySign: payInfo.paySign
  });

  // 3. 支付结果查询
  if (payment.errMsg === 'requestPayment:ok') {
    await request.post('/api/pay/notify', { order_id: orderId });
    wx.redirectTo({ url: '/pages/order/success' });
  }

  return payment;
}

// 支付结果轮询（兼容部分机型延迟）
export async function pollPayResult(orderId, maxRetry = 5) {
  for (let i = 0; i < maxRetry; i++) {
    const { status } = await request.get('/api/order/status', { order_id: orderId });
    if (status === 'paid') return true;
    await new Promise(r => setTimeout(r, 2000));
  }
  return false;
}
```

---

### 三、多端统一架构（Taro3 方案）

#### 3.1 Taro3 多端配置

```javascript
// config/index.js
module.exports = {
  mini: {
    common: {
      compilePath: 'src/pages/**'
    }
  },
  h5: {
    publicPath: '/',
    output: 'dist/h5',
    staticDirectory: 'static'
  },
  rn: {
    output: 'dist/app'
  }
};
```

#### 3.2 多端条件编译

```javascript
// 支付渠道条件编译
if (process.env.TARO_ENV === 'weapp') {
  const res = await wx.requestPayment({ /* ... */ });
} else if (process.env.TARO_ENV === 'h5') {
  // H5 调起收银台
  window.location.href = payUrl;
}

// 分享能力条件编译
if (process.env.TARO_ENV === 'weapp') {
  wx.showShareMenu({ withShareTicket: true });
} else if (process.env.TARO_ENV === 'rn') {
  // React Native 原生分享
}
```

#### 3.3 统一登录态

```javascript
// src/utils/auth.js
export function checkLogin() {
  const token = wx.getStorageSync('token');
  if (!token) {
    wx.navigateTo({ url: '/pages/login/index' });
    return false;
  }
  return true;
}

// 小程序登录 → ThinkPHP token 换取
export async function miniLogin() {
  return new Promise((resolve, reject) => {
    wx.login({
      success: async (res) => {
        try {
          const { data } = await request.post('/api/login/mini', {
            code: res.code
          });
          wx.setStorageSync('token', data.token);
          wx.setStorageSync('userInfo', data.userInfo);
          resolve(data);
        } catch (e) {
          reject(e);
        }
      }
    });
  });
}
```

---

### 四、ThinkPHP6 后端接口（小程序端）

#### 4.1 路由设计

```php
// route/mp.php (小程序路由组)
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
    Route::post('pay/notify', 'mp.Pay/notify');  // 微信支付回调
    Route::get('pay/status', 'mp.Pay/status');   // 支付状态轮询

    // 分享
    Route::get('share/config', 'mp.Share/config');
})->middleware(\app\http\middleware\CheckMiniToken::class);
```

#### 4.2 微信支付回调（重点）

```php
// app/admin/controller/mp/Pay.php
namespace app\mp\controller\mp;

use app\services\PayServices;
use WeChatPay\Crypto;
use WeChatPay\Util\PemUtil;

class Pay extends BaseController
{
    protected PayServices $payServices;

    public function notify()
    {
        $xml = file_get_contents('php://input');
        $data = xml_to_array($xml);

        if ($data['return_code'] !== 'SUCCESS') {
            return '<xml><return_code><![CDATA[FAIL]]></return_code></xml>';
        }

        // 签名验证
        $sign = Crypto::sign(
            'SHA256',
            $this->buildSignString($data),
            PemUtil::fromPemFileByteString(config('wechat.wechat_mp_key'))
        );

        if ($sign !== $data['sign']) {
            return '<xml><return_code><![CDATA[FAIL]]></return_code></xml>';
        }

        // 业务处理：更新订单状态
        $this->payServices->updateOrderPaid($data['out_trade_no']);

        return '<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>';
    }

    private function buildSignString(array $data): string
    {
        ksort($data);
        $signStr = '';
        foreach ($data as $k => $v) {
            if ($k !== 'sign' && $v !== '' && !is_array($v)) {
                $signStr .= $k . '=' . $v . '&';
            }
        }
        return $signStr . 'key=' . config('wechat.wechat_mp_key');
    }
}
```

---

### 五、社交分享与裂变

#### 5.1 微信分享卡片配置

```javascript
// src/pages/product/detail.js
onShareAppMessage() {
  return {
    title: this.productInfo.store_name,
    path: `/pages/product/detail?id=${this.productId}&spread_id=${wx.getStorageSync('uid')}`,
    imageUrl: this.productInfo.image
  };
},

onShareTimeline() {
  return {
    title: `${this.productInfo.store_name} - 仅 ¥${this.productInfo.price}`,
    query: `id=${this.productId}&spread_id=${wx.getStorageSync('uid')}`
  };
}
```

#### 5.2 裂变关系绑定

```javascript
// app.js onLaunch
onLaunch(options) {
  if (options.query.spread_id) {
    wx.setStorageSync('spread_id', options.query.spread_id);
  }
}

// 下单时传递推广人 ID
async function createOrder(cartIds, spreadId) {
  return request.post('/api/order/create', {
    cart_ids: cartIds,
    spread_id: spreadId || wx.getStorageSync('spread_id')
  });
}
```

#### 5.3 订阅消息（重要！触达用户）

```javascript
// src/utils/notify.js
const TEMPLATE_IDS = {
  ORDER_PAY: 'AT0001',   // 订单支付通知
  SHIP: 'AT0002',        // 发货通知
  DELIVERY: 'AT0003',    // 收货通知
  REMINDER: 'AT0004',   // 拼团/砍价提醒
  COUPON: 'AT0005'      // 优惠券到账
};

export async function requestSubscribe(type) {
  const tmplId = TEMPLATE_IDS[type];
  const res = await wx.requestSubscribeMessage({
    tmplIds: [tmplId]
  });
  if (res[tmplId] === 'accept') {
    // 保存用户授权状态
    await request.post('/api/user/saveSubscribe', {
      tmpl_id: tmplId,
      status: 1
    });
  }
  return res;
}
```

---

### 六、CRMEB 模板分发机制

#### 6.1 模板市场对接

CRMEB 官方提供小程序源码模板，通过官方渠道获取后：

```bash
# 模板下载
git clone https://github.com/crmeb/CRMEB-MP.git crmeb_mp
cd crmeb_mp && npm install

# 修改 API 地址（ThinkPHP 后端地址）
# src/config/api.js
const requestUrl = 'https://your-thinkphp-api.com';
```

#### 6.2 模板定制化流程

| 阶段 | 任务 | 天龙岗位 |
|------|------|---------|
| 需求分析 | 小程序商城功能拆解（商品/订单/支付/裂变） | 00分析师 |
| 技术调研 | CRMEB 模板能力评估 + ThinkPHP 接口对接方案 | 01调研师 |
| 架构设计 | 多端统一架构设计（Taro3/uni-app） | 02架构师 |
| 前后端联调 | ThinkPHP API 调试 + 小程序端接入 | 03构建师 |
| 支付测试 | 微信支付沙箱全流程测试 | 04验证师 |
| 安全审查 | 支付回调签名/Token 校验/敏感数据加密 | 05安全师 |
| 发布部署 | 小程序审核上架 + H5 域名配置 | 08发布师 |
| 运营配置 | 营销活动（拼团/秒杀/优惠券）配置 | 45-01电商运营 |

---

### 七、核心文件清单

| 文件 | 作用 | CRMEB 路径 |
|------|------|-----------|
| API 基类 | ThinkPHP 请求封装 | `src/api/index.js` |
| 微信支付 | 调起支付 + 回调处理 | `src/utils/pay.js` |
| 登录态 | 小程序 code 换 Token | `src/utils/auth.js` |
| 分享配置 | 朋友圈/好友分享 | `src/pages/*/index.js` |
| 订阅消息 | 模板消息推送授权 | `src/utils/notify.js` |
| 购物车 | 多 SKU 合并下单 | `src/pages/cart/index.js` |
| 订单 | 状态机 + 支付流程 | `src/pages/order/confirm.js` |
| 后端支付回调 | 微信支付异步通知 | `app/mp/controller/Pay.php` |
| 路由注册 | ThinkPHP 小程序路由 | `route/mp.php` |

---

### 八、天龙岗位协同链路

```
00分析师
  ↓ 分析小程序商城需求（商品SKU/营销活动/多端适配）
  ↓
01调研师
  ↓ 调研 CRMEB 模板能力 + 微信小程序审核规范
  ↓ 调研 ThinkPHP6 接口协议 + 微信支付 V3 API
  ↓
02架构师
  ↓ 设计多端统一架构（Taro3 / uni-app）
  ↓ 设计分包加载策略（主包 ≤2MB，分包按功能域）
  ↓
03构建师
  ↓ 前端：Taro3 多端编译 + CRMEB 模板定制
  ↓ 后端：ThinkPHP6 路由 + 微信支付 V3 集成
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
  ↓ 拼团/秒杀/优惠券/分销配置 + 数据看板监控
```

### 九、关键坑点速查

| 坑点 | 原因 | 解决方案 |
|------|------|---------|
| 支付失败（签名错误） | V3 API 签名算法变更 | 使用 `WeChatPay\Crypto` 库，勿用 MD5 |
| 支付回调验签失败 | PEM 格式私钥含 BOM | `openssl_pkey_get_private()` 前 `trim()` |
| 订阅消息发送失败 | 用户未授权或模板已下架 | 授权时保存 `subscribe_status`，用 `消息通知` 模板 |
| 分包加载白屏 | 分包路径错误 | `app.json` 中 `root` 使用相对路径，pages 用完整路径 |
| iOS 支付调起失败 | 微信版本 < 7.0.15 | 引导用户更新微信，检查 `canIUse('requestPayment')` |
| H5 支付跨域 | 微信浏览器限制 | H5 支付需申请 H5 支付资质，域名需 ICP 备案 |
| 分享链接参数丢失 | `onShareAppMessage` 返回的 path 过长 | 使用短链服务或后端生成小程序码 |
| 小程序审核被拒 | 类目与内容不匹配 | 提前确认主体资质，选择正确类目（电商 > 零售/服装） |
