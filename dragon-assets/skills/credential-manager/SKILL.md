---
license: UNKNOWN
triggers: ["credential manager", "Credential Manager Skill"]
---
# Credential Manager Skill

> API Key 安全存储 + 环境变量管理 + 密钥轮换
> 借鉴自 Huginn Credentials Store 设计理念

## 核心价值

| 维度 | 数据 |
|------|------|
| **定位** | 天龙引擎凭证集中管理中心 |
| **核心能力** | 加密存储 + ENV 注入 + 密钥轮换 + 审计日志 |
| **借鉴来源** | Huginn Credentials Store |
| **优先级** | ⭐⭐⭐ 高优先级 |

## 功能矩阵

| 功能 | 说明 | 命令 |
|------|------|------|
| **加密存储** | AES-256-GCM 加密 API Keys | `cred-store add` |
| **ENV 注入** | 安全注入到环境变量 | `cred-inject` |
| **密钥轮换** | 自动轮换密钥 + 回滚支持 | `cred-rotate` |
| **审计日志** | 完整访问记录 | `cred-audit` |
| **多后端** | 文件/1Password/HashiCorp Vault | `cred-backend` |

## 快速开始

```bash
# 存储新凭证
cred-store add openai "sk-xxx" --tag "production"
cred-store add github "ghp_xxx" --tag "ci"

# 注入到环境变量
source <(cred-inject openai github)

# 轮换密钥
cred-rotate openai --new "sk-yyy"

# 审计日志
cred-audit --last 30 --format table
```

## 核心命令

```bash
# 凭证管理
cred-store add <name> <value> [--tag] [--expires]
cred-store list [--tag] [--format json|table]
cred-store get <name> [--export]
cred-store delete <name> [--force]

# 环境变量
cred-inject <name>...          # 输出 export 语句
cred-inject --all             # 注入所有凭证

# 密钥轮换
cred-rotate <name> --new <value>
cred-rollback <name> --to <version>

# 审计
cred-audit [--user] [--action] [--days]
cred-audit --export csv > audit.csv
```

## 凭证分类

| 类别 | 示例 | 标签 |
|------|------|------|
| **AI Provider** | OpenAI, Anthropic, DeepSeek | `provider:ai` |
| **Social Media** | Twitter, 小红书, 微信公众号 | `platform:social` |
| **Cloud** | AWS, GCP, Azure | `cloud:aws` |
| **Database** | PostgreSQL, MongoDB | `db:postgres` |
| **CI/CD** | GitHub Token, CI Secrets | `ci:github` |

## 安全特性

```
┌─────────────────────────────────────────────────────────────┐
│ 凭证安全架构                                                  │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: AES-256-GCM 加密存储                               │
│ Layer 2: 主密钥 PBKDF2 派生（100,000 迭代）                  │
│ Layer 3: 访问审计日志（不可篡改）                             │
│ Layer 4: 自动过期机制                                        │
│ Layer 5: 轮换回滚支持                                        │
└─────────────────────────────────────────────────────────────┘
```

## 与 Dragon Gateway 协同

```yaml
# Dragon Gateway 可调用 credential-manager
dragon-gateway:
  credentials:
    load_from: ~/.claude/credentials.vault
  environment:
    inject_automatically: true
```

## 与其他 Skill 协同

| Skill | 协同方式 |
|-------|---------|
| **paperclip-ticket** | 凭证访问作为工单事件 |
| **dragon-gateway** | API Key 自动注入 |
| **ai-router** | Provider Keys 安全加载 |

## 实现文件

- [skills/credential-manager/scripts/cred-store.sh](skills/credential-manager/scripts/cred-store.sh) - 主脚本
- [skills/credential-manager/scripts/crypto.sh](skills/credential-manager/scripts/crypto.sh) - 加密模块
- [skills/credential-manager/scripts/audit.sh](skills/credential-manager/scripts/audit.sh) - 审计模块

## 使用示例

```bash
# 天龙引擎自然语言调用
[@01调研师] 使用 credential-manager 存储我的 OpenAI API Key
[@07记录师] 从 credential-manager 加载所有社交媒体凭证

# 自动化场景
# 在 ~/.bashrc 中添加
echo 'source <(cred-inject --auto)' >> ~/.bashrc
```

## 预期收益

| 指标 | 提升 |
|------|------|
| **凭证安全性** | +95%（加密存储） |
| **管理效率** | +300%（集中管理） |
| **审计透明度** | 100%（完整日志） |
| **密钥轮换** | +500%（自动化） |

## 安装

```bash
# 初始化
cred-store init --path ~/.claude/credentials.vault

# 设置主密码（首次）
cred-store setup

# 验证安装
cred-store doctor
```
