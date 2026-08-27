---
license: UNKNOWN
triggers: ["superset auth manager", "superset-auth-manager"]
---
# superset-auth-manager

## 元数据
- **版本**: 1.0.0
- **创建日期**: 2026-03-19
- **匹配岗位**: 全部天龙岗位（认证基础设施）
- **依赖**: requests, python-jose[cryptography]

## 概述
Apache Superset JWT认证管理器，为天龙引擎提供统一的认证Token管理，支持Token自动刷新、Guest Token生成、多租户认证。

## 核心能力

### 1. JWT Token 管理
```python
# 获取访问Token
POST /api/v1/security/login
{
    "username": "admin",
    "password": "admin",
    "provider": "db"
}

# 返回
{
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
}
```

### 2. Token 自动刷新
- Token 过期前 5 分钟自动刷新
- 缓存 Token 到本地，避免重复登录
- 多进程安全 Token 共享

### 3. Guest Token 生成
```python
# 生成嵌入式仪表板的 Guest Token
POST /api/v1/security/guest_token/
{
    "user": {"username": "guest"},
    "resources": [{"type": "dashboard", "id": "1"}],
    "rls": []  # 行级安全规则
}
```

## 命令接口

### CLI 命令
```bash
# 登录 Superset
/superset-auth login --url https://superset.example.com --username admin

# 检查认证状态
/superset-auth status

# 刷新 Token
/superset-auth refresh

# 生成 Guest Token
/superset-auth guest-token --dashboard-id 1

# 登出
/superset-auth logout
```

### 自然语言触发
- "登录 Superset"
- "检查 Superset 认证状态"
- "生成 Superset Guest Token"

## 使用示例

### Python API
```python
from superset_auth import SupersetAuth

# 初始化认证管理器
auth = SupersetAuth(
    base_url="https://superset.example.com",
    username="admin",
    password="admin"
)

# 获取 Token
token = auth.get_access_token()

# 生成 Guest Token
guest_token = auth.create_guest_token(
    dashboard_id=1,
    username="viewer",
    rls=[{"clause": "department = 'sales'"}]
)

# 使用 Token 调用 API
headers = auth.get_headers()
response = requests.get(f"{base_url}/api/v1/dashboard/", headers=headers)
```

### 与天龙岗位集成

#### 17-01 数据分析师
```python
# 自动认证并创建仪表板
auth = SupersetAuth.from_env()  # 从环境变量读取配置
dashboard_api = DashboardAPI(auth)
```

#### 64-01 量化研究员
```python
# 为策略报告生成嵌入 Token
guest_token = auth.create_guest_token(
    dashboard_id="strategy_dashboard",
    username="investor",
    rls=[{"clause": f"strategy_id = '{strategy_id}'"}]
)
```

## 配置

### 环境变量
```bash
SUPERSET_BASE_URL=https://superset.example.com
SUPERSET_USERNAME=admin
SUPERSET_PASSWORD=admin
SUPERSET_PROVIDER=db  # db, ldap, oauth
```

### 配置文件 (~/.superset/config.json)
```json
{
    "base_url": "https://superset.example.com",
    "auth": {
        "provider": "db",
        "username": "admin",
        "password_env": "SUPERSET_PASSWORD"
    },
    "cache": {
        "token_file": "~/.superset/token_cache.json",
        "refresh_threshold_minutes": 5
    }
}
```

## 安全考虑

1. **Token 缓存加密**: Token 本地缓存使用 AES-256 加密
2. **密码不存储**: 密码仅用于初始登录，不持久化
3. **HTTPS 强制**: 所有 API 调用强制 HTTPS
4. **Token 过期**: 默认 1 小时过期，支持自动刷新

## 错误处理

| 错误码 | 描述 | 处理方式 |
|--------|------|---------|
| 401 | Token 过期 | 自动刷新后重试 |
| 403 | 权限不足 | 抛出 PermissionDeniedError |
| 429 | 请求过多 | 指数退避重试 |
| 500 | 服务器错误 | 重试 3 次后抛出 |

## 文件结构
```
skills/superset-auth-manager/
├── SKILL.md
├── scripts/
│   ├── superset_auth.py      # 核心认证类
│   ├── token_manager.py      # Token 缓存管理
│   └── cli.py                # CLI 工具
└── docs/
    ├── api-reference.md
    └── security-best-practices.md
```

## 依赖安装
```bash
pip install requests python-jose[cryptography] cryptography
```

## 版本历史
- **1.0.0** (2026-03-19): 初始版本，支持 JWT 认证、Token 刷新、Guest Token