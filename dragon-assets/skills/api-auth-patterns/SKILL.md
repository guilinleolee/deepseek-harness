---
license: UNKNOWN
triggers: ["api auth patterns", "api-auth-patterns Skill"]
---
# api-auth-patterns Skill

## L0: 一句话描述
API认证模式标准化集成包，支持7种认证模式自动检测与代码生成

## L1: 使用场景
- 快速识别API所需的认证方式
- 自动生成认证代码片段
- 认证配置模板复用
- 跨项目认证模式统一

## L2: 详细文档

### 支持的认证模式

| 模式 | 命令 | 适用场景 |
|------|------|---------|
| API Key | `--auth apiKey` | 简单令牌认证 |
| OAuth 2.0 | `--auth OAuth` | 需要授权码流程 |
| JWT | `--auth JWT` | 无状态令牌认证 |
| Bearer Token | `--auth Bearer` | HTTP Bearer认证 |
| Basic Auth | `--auth Basic` | 用户名密码认证 |
| AWS Auth | `--auth AWS` | AWS签名认证 |
| Custom Header | `--auth Header` | 自定义请求头 |

### 功能矩阵

| 功能 | 命令 | 说明 |
|------|------|------|
| 模式检测 | `--detect` | 检测API需要的认证模式 |
| 代码生成 | `--generate` | 生成认证代码 |
| 配置模板 | `--template` | 生成配置模板 |
| 凭证管理 | `--manage` | 凭证存储与管理 |

### 认证流程模式

```
┌─────────────────────────────────────────────────────────────┐
│                    API认证模式选择流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  API Key → 最简单，直接附加到请求头                         │
│     ↓                                                       │
│  Bearer Token → OAuth后获取，令牌方式                       │
│     ↓                                                       │
│  OAuth 2.0 → 完整授权流程，需要回调                         │
│     ↓                                                       │
│  JWT → 无状态令牌，自包含用户信息                           │
│     ↓                                                       │
│  AWS Auth → 云服务签名，复杂但安全                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 使用示例

```bash
# 检测认证模式
python3 scripts/auth_patterns.py --detect "https://api.example.com"

# 生成认证代码
python3 scripts/auth_patterns.py --generate --auth OAuth --lang python

# 生成配置模板
python3 scripts/auth_patterns.py --template --auth apiKey --env development

# 凭证管理
python3 scripts/auth_patterns.py --manage --add --name "Alpha Vantage"
```

### 与天龙岗位协同

| 岗位 | 协同方式 |
|------|---------|
| 01调研师 | API认证数据源发现 |
| 03构建师 | 开发工具API集成 |
| 05安全师 | 安全认证模式审计 |
| 64-01量化研究员 | 金融API认证集成 |

### 数据来源

基于 public-apis/public-apis 认证数据
- apiKey: ~40%
- OAuth: ~10%
- JWT: ~5%
- Bearer: ~15%
- 无认证: ~30%

## Files

- `SKILL.md` - 本文件
- `scripts/auth_patterns.py` - 认证模式引擎
- `data/auth_patterns.json` - 认证模式数据
