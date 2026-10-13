# Python Code Node 示例 - API 集成

## 概述

使用 Python Code 节点进行 HTTP 请求、API 调用和外部服务集成。

## HTTP 请求

### 使用 requests 库

```python
import requests
import json

# 准备请求参数
url = 'https://api.example.com/users'
headers = {
    'Authorization': f"Bearer {$env.API_TOKEN}",
    'Content-Type': 'application/json'
}

# 发送 GET 请求
response = requests.get(url, headers=headers)

# 检查响应状态
if response.status_code == 200:
    data = response.json()

    # 处理数据
    result = [{
        "json": {
            "success": True,
            "data": data,
            "count": len(data) if isinstance(data, list) else 1
        }
    }]
else:
    result = [{
        "json": {
            "success": False,
            "error": f"HTTP {response.status_code}: {response.text}",
            "status_code": response.status_code
        }
    }]

return result
```

### POST 请求

```python
import requests

# 准备数据
items = $input.all()

results = []
for item in items:
    url = 'https://api.example.com/data'
    payload = {
        'name': item.json.get('name'),
        'email': item.json.get('email'),
        'metadata': item.json
    }

    response = requests.post(
        url,
        json=payload,
        headers={
            'Authorization': f"Bearer {$env.API_TOKEN}",
            'Content-Type': 'application/json'
        }
    )

    results.append({
        "json": {
            "original_data": item.json,
            "response_data": response.json() if response.status_code == 201 else None,
            "success": response.status_code == 201,
            "status_code": response.status_code
        }
    })

return results
```

### 处理重试逻辑

```python
import requests
import time

def fetch_with_retry(url, options, max_retries=3):
    """带重试的请求函数"""
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.request(**options)

            if response.ok:
                return response.json()

            # 服务器错误，尝试重试
            if response.status_code >= 500 and attempt < max_retries:
                wait_time = 2 ** attempt  # 指数退避
                time.sleep(wait_time)
                continue

            # 其他错误直接返回
            return {
                "error": f"HTTP {response.status_code}",
                "message": response.text
            }

        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                return {"error": str(e)}
            time.sleep(2 ** attempt)

    return {"error": "Max retries exceeded"}

# 使用
items = $input.all()

results = []
for item in items:
    data = fetch_with_retry(
        item.json.get('url'),
        {
            'method': 'GET',
            'url': item.json.get('url'),
            'headers': {'Authorization': f"Bearer {$env.API_TOKEN}"}
        }
    )
    results.append({"json": {**item.json, "fetched_data": data}})

return results
```

## API 认证

### Bearer Token

```python
import requests

class BearerTokenAuth:
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r

# 使用
auth = BearerTokenAuth($env.API_TOKEN)

response = requests.get(
    'https://api.example.com/protected',
    auth=auth
)

return [{"json": response.json()}]
```

### API Key

```python
import requests

# Header 方式
headers = {
    'X-API-Key': $env.API_KEY,
    'Accept': 'application/json'
}

response = requests.get(
    'https://api.example.com/data',
    headers=headers
)

return [{"json": response.json()}]
```

### OAuth2 流程

```python
import requests
import base64

def get_oauth_token(client_id, client_secret, token_url):
    """获取 OAuth2 访问令牌"""
    # 编码凭据
    credentials = base64.b64encode(
        f"{client_id}:{client_secret}".encode()
    ).decode()

    headers = {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        token_data = response.json()
        return token_data.get('access_token')

    raise Exception(f"Failed to get token: {response.text}")

# 使用
token = get_oauth_token(
    $env.OAUTH_CLIENT_ID,
    $env.OAUTH_CLIENT_SECRET,
    'https://auth.example.com/oauth/token'
)

# 使用令牌请求数据
response = requests.get(
    'https://api.example.com/data',
    headers={'Authorization': f'Bearer {token}'}
)

return [{"json": response.json()}]
```

## RESTful API 操作

### CRUD 操作

```python
import requests

class RESTClient:
    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }

    def create(self, resource, data):
        response = requests.post(
            f'{self.base_url}/{resource}',
            json=data,
            headers=self.headers
        )
        return response.json()

    def read(self, resource, item_id):
        response = requests.get(
            f'{self.base_url}/{resource}/{item_id}',
            headers=self.headers
        )
        return response.json()

    def update(self, resource, item_id, data):
        response = requests.put(
            f'{self.base_url}/{resource}/{item_id}',
            json=data,
            headers=self.headers
        )
        return response.json()

    def delete(self, resource, item_id):
        response = requests.delete(
            f'{self.base_url}/{resource}/{item_id}',
            headers=self.headers
        )
        return response.status_code == 204

# 使用
client = RESTClient(
    'https://api.example.com',
    $env.API_TOKEN
)

items = $input.all()

results = []
for item in items:
    operation = item.json.get('operation', 'read')
    resource = item.json.get('resource', 'items')
    item_id = item.json.get('id')

    try:
        if operation == 'create':
            result = client.create(resource, item.json.get('data'))
        elif operation == 'read':
            result = client.read(resource, item_id)
        elif operation == 'update':
            result = client.update(resource, item_id, item.json.get('data'))
        elif operation == 'delete':
            success = client.delete(resource, item_id)
            result = {'deleted': success}

        results.append({
            "json": {
                "operation": operation,
                "success": True,
                "result": result
            }
        })
    except Exception as e:
        results.append({
            "json": {
                "operation": operation,
                "success": False,
                "error": str(e)
            }
        })

return results
```

### GraphQL 查询

```python
import requests

def execute_graphql_query(query, variables=None):
    """执行 GraphQL 查询"""
    url = 'https://api.example.com/graphql'
    headers = {
        'Authorization': f"Bearer {$env.GRAPHQL_TOKEN}",
        'Content-Type': 'application/json'
    }

    payload = {
        'query': query,
        'variables': variables or {}
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            raise Exception(data['errors'])
        return data.get('data')
    else:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

# 查询示例
query = '''
  query GetUser($userId: ID!) {
    user(id: $userId) {
      id
      name
      email
      posts {
        id
        title
      }
    }
  }
'''

items = $input.all()

results = []
for item in items:
    try:
        user_data = execute_graphql_query(
            query,
            {'userId': item.json.get('userId')}
        )

        results.append({
            "json": {
                "success": True,
                "user": user_data.get('user')
            }
        })
    except Exception as e:
        results.append({
            "json": {
                "success": False,
                "error": str(e)
            }
        })

return results
```

## Webhook 处理

### 验证 Webhook 签名

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    """验证 HMAC 签名"""
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    # 比较签名（使用 hmac.compare_digest 防止时序攻击）
    return hmac.compare_digest(
        signature.replace('sha256=', ''),
        expected_signature
    )

# 使用
webhook_data = $input.first().json
signature = webhook_data.get('signature')
payload = str(webhook_data.get('data'))

if verify_webhook_signature(payload, signature, $env.WEBHOOK_SECRET):
    return [{
        "json": {
            "verified": True,
            "data": webhook_data.get('data')
        }
    }]
else:
    raise Exception('Invalid webhook signature')
```

### 处理不同事件类型

```python
items = $input.all()

event_handlers = {
    'user.created': lambda data: {
        "event": "user.created",
        "user_id": data.get('user_id'),
        "email": data.get('email'),
        "action": "send_welcome_email"
    },
    'user.updated': lambda data: {
        "event": "user.updated",
        "user_id": data.get('user_id'),
        "changes": data.get('changes'),
        "action": "log_changes"
    },
    'user.deleted': lambda data: {
        "event": "user.deleted",
        "user_id": data.get('user_id'),
        "action": "cleanup_user_data"
    }
}

results = []
for item in items:
    event_type = item.json.get('event_type')
    event_data = item.json.get('data', {})

    handler = event_handlers.get(event_type)

    if handler:
        results.append({"json": handler(event_data)})
    else:
        results.append({
            "json": {
                "event": event_type,
                "handled": False,
                "message": "Unknown event type"
            }
        })

return results
```

## 数据同步

### 批量同步

```python
import requests
import time

def batch_sync(items, batch_size=100, endpoint='https://api.example.com/sync'):
    """批量同步数据到 API"""
    headers = {
        'Authorization': f"Bearer {$env.API_TOKEN}",
        'Content-Type': 'application/json'
    }

    results = {
        'total': len(items),
        'synced': 0,
        'failed': 0,
        'errors': []
    }

    # 分批处理
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]

        try:
            response = requests.post(
                endpoint,
                json={'items': batch},
                headers=headers,
                timeout=30
            )

            if response.ok:
                results['synced'] += len(batch)
            else:
                results['failed'] += len(batch)
                results['errors'].append({
                    'batch': i // batch_size,
                    'error': response.text
                })

        except Exception as e:
            results['failed'] += len(batch)
            results['errors'].append({
                'batch': i // batch_size,
                'error': str(e)
            })

        # 避免速率限制
        time.sleep(0.1)

    return results

# 使用
items = $input.all()

# 提取需要同步的数据
sync_items = [item.json for item in items]

# 执行批量同步
sync_results = batch_sync(sync_items, batch_size=50)

return [{
    "json": {
        "sync_complete": True,
        "results": sync_results
    }
}]
```

### 增量同步

```python
import requests
from datetime import datetime, timedelta

def incremental_sync(last_sync_time=None):
    """增量同步数据"""
    headers = {
        'Authorization': f"Bearer {$env.API_TOKEN}",
        'Content-Type': 'application/json'
    }

    # 默认同步最近 24 小时
    if not last_sync_time:
        last_sync_time = datetime.now() - timedelta(days=1)

    params = {
        'modified_since': last_sync_time.isoformat(),
        'limit': 1000
    }

    response = requests.get(
        'https://api.example.com/items',
        headers=headers,
        params=params
    )

    if response.ok:
        data = response.json()
        return {
            'success': True,
            'items': data.get('items', []),
            'count': len(data.get('items', [])),
            'synced_at': datetime.now().isoformat()
        }
    else:
        return {
            'success': False,
            'error': response.text
        }

# 使用
# 从上一次同步时间获取
items = $input.all()
last_sync = items[0].json.get('last_sync_time') if items else None

result = incremental_sync(last_sync)

return [{"json": result}]
```

## 相关文档

- [数据处理示例](data-processing.md)
- [JavaScript Code Node 示例](../javascript/api-integration.md)
- [API 最佳实践](../api-best-practices.md)
