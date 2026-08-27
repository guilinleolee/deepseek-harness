# JavaScript Code Node 示例 - API 集成

## 概述

使用 Code 节点进行 HTTP 请求、API 调用和外部服务集成。

## HTTP 请求

### 使用内置 HTTP Request

```javascript
// Code 节点通常配合 HTTP Request 节点使用
// 这里展示如何在 Code 节点中准备请求数据

const items = $input.all();

// 准备批量请求的数据
const requests = items.map(item => ({
  json: {
    url: `https://api.example.com/users/${item.json.userId}`,
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${item.json.apiToken}`,
      'Content-Type': 'application/json'
    }
  }
}));

return requests;
```

### 响应数据处理

```javascript
// 处理 HTTP Request 节点的响应
const response = $input.first().json;

// 检查响应状态
if (response.statusCode >= 400) {
  throw new Error(`API Error: ${response.statusCode} - ${response.message}`);
}

// 提取数据
const data = response.data || response;

return [{
  json: {
    success: true,
    data: data,
    timestamp: new Date().toISOString(),
    itemCount: Array.isArray(data) ? data.length : 1
  }
}];
```

### 重试逻辑

```javascript
// 实现指数退避重试
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);

      if (response.ok) {
        return await response.json();
      }

      if (response.status >= 500 && attempt < maxRetries) {
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }

      throw new Error(`HTTP ${response.status}: ${response.statusText}`);

    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }

      const delay = Math.pow(2, attempt) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}

// 使用示例
const items = $input.all();
const results = [];

for (const item of items) {
  try {
    const data = await fetchWithRetry(
      item.json.url,
      { method: 'GET', headers: item.json.headers }
    );
    results.push({ json: { ...item.json, data, success: true } });
  } catch (error) {
    results.push({ json: { ...item.json, error: error.message, success: false } });
  }
}

return results;
```

## API 认证

### Bearer Token

```javascript
const items = $input.all();
const token = 'your-api-token'; // 从环境变量或凭据中获取

const requests = items.map(item => ({
  json: {
    url: 'https://api.example.com/data',
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(item.json.data)
  }
}));

return requests;
```

### API Key

```javascript
const items = $input.all();
const apiKey = 'your-api-key';

const requests = items.map(item => ({
  json: {
    url: `https://api.example.com/search?q=${encodeURIComponent(item.json.query)}`,
    method: 'GET',
    headers: {
      'X-API-Key': apiKey,
      'Accept': 'application/json'
    }
  }
}));

return requests;
```

### OAuth2 签名

```javascript
// 生成 OAuth 1.0 签名
function generateOAuthSignature(url, method, params, consumerKey, consumerSecret) {
  // 简化的 OAuth 签名生成
  // 实际使用时应考虑使用专门的库
  const timestamp = Math.floor(Date.now() / 1000);
  const nonce = Math.random().toString(36).substring(7);

  const paramString = Object.keys(params)
    .sort()
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&');

  const signatureBaseString = `${method}&${encodeURIComponent(url)}&${encodeURIComponent(paramString)}`;
  const signingKey = `${encodeURIComponent(consumerSecret)}&`;

  // 这里应该使用 HMAC-SHA1，简化示例
  const signature = Buffer.from(signatureBaseString).toString('base64');

  return {
    oauth_consumer_key: consumerKey,
    oauth_signature: signature,
    oauth_timestamp: timestamp,
    oauth_nonce: nonce,
    oauth_version: '1.0'
  };
}

const items = $input.all();
const authParams = generateOAuthSignature(
  'https://api.example.com/endpoint',
  'GET',
  { param1: 'value1' },
  $env.OAUTH_CONSUMER_KEY,
  $env.OAUTH_CONSUMER_SECRET
);

const requests = items.map(item => ({
  json: {
    url: 'https://api.example.com/endpoint',
    method: 'GET',
    headers: {
      'Authorization': `OAuth ${Object.entries(authParams).map(([k, v]) => `${k}="${v}"`).join(', ')}`
    }
  }
}));

return requests;
```

## RESTful API 操作

### CRUD 操作

```javascript
// 根据操作类型生成不同的请求
const items = $input.all();

const operationMap = {
  create: { method: 'POST', url: 'https://api.example.com/resources' },
  read: { method: 'GET', url: 'https://api.example.com/resources/{id}' },
  update: { method: 'PUT', url: 'https://api.example.com/resources/{id}' },
  delete: { method: 'DELETE', url: 'https://api.example.com/resources/{id}' }
};

const requests = items.map(item => {
  const operation = item.json.operation || 'read';
  const config = operationMap[operation];

  if (!config) {
    throw new Error(`Unknown operation: ${operation}`);
  }

  let url = config.url;
  if (item.json.id) {
    url = url.replace('{id}', item.json.id);
  }

  return {
    json: {
      url,
      method: config.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${$env.API_TOKEN}`
      },
      body: ['POST', 'PUT'].includes(config.method) ? JSON.stringify(item.json.data) : undefined
    }
  };
});

return requests;
```

### GraphQL 查询

```javascript
// 准备 GraphQL 请求
const items = $input.all();

const query = `
  query GetUser($userId: ID!) {
    user(id: $userId) {
      id
      name
      email
      posts {
        id
        title
        createdAt
      }
    }
  }
`;

const requests = items.map(item => ({
  json: {
    url: 'https://api.example.com/graphql',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${$env.GRAPHQL_TOKEN}`
    },
    body: JSON.stringify({
      query,
      variables: {
        userId: item.json.userId
      }
    })
  }
}));

return requests;
```

### 处理分页

```javascript
// 处理 API 分页响应
async function fetchAllPages(baseUrl, options) {
  const allItems = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const url = `${baseUrl}?page=${page}&per_page=100`;
    const response = await fetch(url, options);
    const data = await response.json();

    allItems.push(...data.items);

    hasMore = data.items.length === 100 && data.hasMore;
    page++;
  }

  return allItems;
}

// 使用
const baseUrl = 'https://api.example.com/items';
const options = {
  headers: {
    'Authorization': `Bearer ${$env.API_TOKEN}`
  }
};

const allItems = await fetchAllPages(baseUrl, options);

return [{
  json: {
    totalItems: allItems.length,
    items: allItems
  }
}];
```

## Webhook 处理

### 验证 Webhook 签名

```javascript
// 验证 HMAC 签名（如 GitHub webhook）
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const hmac = crypto.createHmac('sha256', secret);
  const digest = hmac.update(payload).digest('hex');
  const trustedSignature = `sha256=${digest}`;

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(trustedSignature)
  );
}

const webhookData = $input.first();
const body = JSON.stringify(webhookData.json);
const signature = webhookData.headers['x-hub-signature-256'];
const secret = $env.WEBHOOK_SECRET;

if (!verifyWebhookSignature(body, signature, secret)) {
  throw new Error('Invalid webhook signature');
}

return [{
  json: {
    verified: true,
    data: webhookData.json
  }
}];
```

### 处理不同事件类型

```javascript
// 根据 webhook 事件类型路由
const webhook = $input.first().json;
const eventType = webhook.headers['x-github-event'] || webhook.event;

const eventHandlers = {
  push: () => [{
    json: {
      type: 'push',
      repository: webhook.repository.full_name,
      ref: webhook.ref,
      commits: webhook.commits.length,
      pusher: webhook.pusher.name
    }
  }],

  pull_request: () => [{
    json: {
      type: 'pull_request',
      action: webhook.action,
      repository: webhook.repository.full_name,
      prNumber: webhook.pull_request.number,
      title: webhook.pull_request.title
    }
  }],

  issues: () => [{
    json: {
      type: 'issues',
      action: webhook.action,
      repository: webhook.repository.full_name,
      issueNumber: webhook.issue.number,
      title: webhook.issue.title
    }
  }]
};

const handler = eventHandlers[eventType];
if (handler) {
  return handler();
}

return [{ json: { type: 'unknown', event: eventType } }];
```

## API 速率限制处理

```javascript
// 处理速率限制
async function fetchWithRateLimit(url, options) {
  let retries = 0;
  const maxRetries = 5;

  while (retries < maxRetries) {
    const response = await fetch(url, options);

    const rateLimitRemaining = parseInt(response.headers.get('X-RateLimit-Remaining') || '0');
    const rateLimitReset = parseInt(response.headers.get('X-RateLimit-Reset') || '0');

    if (rateLimitRemaining <= 1) {
      const waitTime = Math.max(0, rateLimitReset * 1000 - Date.now());
      await new Promise(resolve => setTimeout(resolve, waitTime));
      continue;
    }

    if (response.ok) {
      return await response.json();
    }

    if (response.status === 429) {
      const retryAfter = parseInt(response.headers.get('Retry-After') || '60');
      await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
      retries++;
      continue;
    }

    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  throw new Error('Max retries exceeded');
}
```

## 相关文档

- [数据转换示例](data-transformation.md)
- [Python Code Node 示例](../python/python-examples.md)
- [API 最佳实践](../api-best-practices.md)
