# 数据源使用指南

## 概述

本指南详细说明各个数据源的使用方法、数据维度、配置要求和成本。

---

## 1. 百度指数

### 基本信息
- **官网**: https://index.baidu.com
- **类型**: 搜索指数平台
- **推荐度**: ⭐⭐⭐

### 数据维度
- ✅ 年龄分布
- ✅ 性别分布
- ✅ 地域分布
- ✅ 兴趣分布

### 配置要求
- 无需 API 密钥
- 需要网页自动化（MCP Chrome DevTools）
- 可能需要处理验证码

### 成本
- 免费

### 使用方法

#### 首次使用
1. 打开浏览器访问 https://index.baidu.com
2. （可选）登录百度账号以获得更完整的数据
3. 数据会自动通过网页爬取获取

#### 后续使用
- cookies 会自动保存，无需重复登录
- 如果提示登录，请在浏览器中登录后重新运行

### 技术实现
```python
# 使用 MCP Chrome DevTools
from scripts.data_sources.source_baidu_index import SourceBaiduIndex

config = {
    'enabled': True,
    'method': 'scrape',
    'timeout': 30000
}

source = SourceBaiduIndex(config, mcp_tools=mcp_tools)
data = await source.fetch_persona_data('企业培训')
```

---

## 2. 抖音指数（巨量算数）

### 基本信息
- **官网**: https://ecom.oceanengine.com
- **类型**: 字节系数据平台
- **推荐度**: ⭐⭐

### 数据维度
- ✅ 年龄分布
- ✅ 性别分布
- ✅ 地域分布
- ✅ 内容偏好
- ✅ 平台分布（抖音、今日头条）

### 配置要求
- 需要登录巨量引擎账号
- 可能需要企业认证
- 首次使用需要手动登录

### 成本
- 免费浏览
- 企业认证需要营业执照

### 使用方法

#### 首次使用
1. 访问 https://ecom.oceanengine.com
2. 注册/登录账号
3. 可能需要企业认证
4. 登录后会自动保存 cookies

#### 后续使用
- cookies 保存后可直接使用
- 如果 cookies 过期，需要重新登录

### 技术实现
```python
from scripts.data_sources.source_douyin_index import SourceDouyinIndex

config = {
    'enabled': True,
    'method': 'scrape',
    'timeout': 30000,
    'cookies': [],  # 会自动保存
    'logged_in': False
}

source = SourceDouyinIndex(config, mcp_tools=mcp_tools)
data = await source.fetch_persona_data('企业培训')

# 如果需要登录
await source.prompt_login(page_idx)
```

---

## 3. 微信指数

### 基本信息
- **官网**: https://mp.weixin.qq.com
- **类型**: 微信生态数据
- **推荐度**: ⭐⭐

### 数据维度
- ✅ 年龄分布
- ✅ 性别分布
- ✅ 地域分布
- ✅ 设备分布

### 配置要求
- 需要微信登录（扫码）
- 需要微信公众平台账号

### 成本
- 免费

### 使用方法

#### 首次使用
1. 访问 https://mp.weixin.qq.com
2. 使用微信扫码登录
3. 登录后会自动保存 cookies

#### 后续使用
- cookies 保存后可直接使用
- 微信登录有效期较长，通常不需要频繁重新登录

### 技术实现
```python
from scripts.data_sources.source_wechat_index import SourceWechatIndex

config = {
    'enabled': True,
    'method': 'scrape',
    'timeout': 40000,
    'cookies': [],
    'logged_in': False
}

source = SourceWechatIndex(config, mcp_tools=mcp_tools)

# 检查是否需要登录
if not source.is_available():
    await source.prompt_login(page_idx)

# 获取数据
data = await source.fetch_persona_data('企业培训')
```

---

## 4. 5118（可选）

### 基本信息
- **官网**: https://www.5118.com
- **API 商城**: https://api.5118.com
- **类型**: SEO 工具平台
- **推荐度**: ⭐⭐⭐⭐⭐

### 数据维度
- ✅ 年龄分布
- ✅ 性别分布
- ✅ 地域分布
- ✅ 搜索趋势
- ✅ 相关关键词

### 配置要求
1. 注册 5118 账号
2. 进入 API 商城：https://api.5118.com
3. 购买关键词 API 接口
4. 获取 API 密钥

### 成本
- 按调用次数计费：¥0.003-0.01/次
- 建议购买套餐：1000 次 ≈ ¥3-10

### API 示例
```bash
# 获取年龄分布
curl "https://api.5118.com/keyword/age_distribution?apikey=YOUR_KEY&keyword=企业培训"

# 获取性别分布
curl "https://api.5118.com/keyword/gender_distribution?apikey=YOUR_KEY&keyword=企业培训"
```

### 配置文件
```json
{
  "5118": {
    "enabled": true,
    "method": "api",
    "api_key": "your_api_key_here",
    "base_url": "https://api.5118.com"
  }
}
```

---

## 数据源选择策略

### 快速分析（<30秒）
```
--source=baidu
```

### 全面分析（<60秒）
```
--source=baidu,douyin
```

### 深度分析（<90秒）
```
--source=baidu,douyin,wechat
```

### 完整分析（需要所有配置）
```
--source=all
```

---

## 数据质量对比

| 维度 | 百度指数 | 抖音指数 | 微信指数 | 5118 |
|------|----------|----------|----------|------|
| 年龄准确性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 地域准确性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 内容偏好 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 数据时效性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 获取难度 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 获取速度 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 常见问题

### Q1: 为什么优先使用百度指数？
A: 百度指数数据全面、无需登录、稳定性较好，是最容易获取的数据源。

### Q2: 抖音指数/微信指数需要企业认证吗？
A: 抖音指数建议企业认证以获得更完整的数据，但个人账号也可使用部分功能。微信指数只需要微信登录即可。

### Q3: 如何处理爬取失败？
A: 系统会自动降级到可用的数据源。如果所有数据源都失败，会提示用户检查配置。

### Q4: 可以只使用 API 数据源吗？
A: 可以，配置时只启用 5118 API 即可。API 方式速度快但需要付费。

### Q5: 数据多久更新一次？
A: 各平台数据更新频率不同：
- 百度指数：每日更新
- 抖音指数：每日更新
- 微信指数：每日更新
- 5118 API：实时数据

### Q6: 批量查询会被限制吗？
A: 是的，建议控制查询频率：
- 单个关键词间隔至少 30 秒
- 避免同时查询多个关键词
- 使用 API 可以提高并发限制

### Q7: 如何保存登录状态？
A: 首次登录后，cookies 会自动保存到 `~/.persona-extractor/cookies.json`。

---

## 最佳实践

### 1. 数据源组合
```
# 推荐：百度 + 抖音
覆盖搜索和短视频两个主要渠道

# 补充：添加微信
覆盖社交平台数据

# 完整：全部数据源
获得最全面的分析
```

### 2. 关键词选择
- ✅ 使用具体行业词（如"SaaS软件"）
- ✅ 使用品牌词（如"华为手机"）
- ✅ 使用产品词（如"在线教育平台"）
- ❌ 避免过于宽泛的词（如"生活"、"美食"）
- ❌ 避免过于冷门的词（可能没有数据）

### 3. 结果验证
- 至少使用 2 个数据源进行交叉验证
- 关注数据异常值
- 结合业务场景解读数据
- 定期更新数据以获取最新趋势

---

## 配置文件示例

### `~/.persona-extractor/config.json`
```json
{
  "data_sources": {
    "baidu_index": {
      "enabled": true,
      "method": "scrape",
      "priority": 1
    },
    "douyin_index": {
      "enabled": true,
      "method": "scrape",
      "priority": 2
    },
    "wechat_index": {
      "enabled": true,
      "method": "scrape",
      "priority": 3
    },
    "5118": {
      "enabled": false,
      "method": "api",
      "api_key": "your_5118_api_key",
      "priority": 0
    }
  },
  "scraper": {
    "headless": true,
    "timeout": 30000,
    "delay_min": 2000,
    "delay_max": 5000,
    "max_retries": 3
  },
  "output": {
    "directory": "~/persona-reports",
    "format": "both"
  }
}
```

### `~/.persona-extractor/cookies.json`
```json
{
  "baidu": {
    "url": "https://index.baidu.com",
    "cookies": [
      {
        "name": "BDUSS",
        "value": "xxx",
        "domain": ".baidu.com"
      }
    ]
  },
  "douyin": {
    "url": "https://ecom.oceanengine.com",
    "cookies": []
  },
  "wechat": {
    "url": "https://mp.weixin.qq.com",
    "cookies": []
  }
}
```
