---
license: UNKNOWN
github_repo: op7418/Claude-to-IM-skill
github_hash: 536908f5e9bd65a151ca4cb4b08d3fedc1a43b4d
last_updated: 2026-04-25
source_type: derived
triggers: ["qq operations", "QQ Operations Skill"]
---
# QQ Operations Skill

> 基于OpenClaw协议的QQ私聊运营能力，填补天龙引擎QQ平台空白

## 概述

| 属性 | 值 |
|------|-----|
| **名称** | qq-operations |
| **版本** | 1.0.0 |
| **来源** | OpenClaw QQ C2C 协议 |
| **匹配岗位** | 35-02 社媒运营、47-03 IM运营师 |

## 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│                   QQ Operations 架构                          │
├─────────────────────────────────────────────────────────────┤
│  能力层                                                       │
│  ├── 私聊消息：发送、接收、历史记录                           │
│  ├── 群聊消息：群发、群管理、群成员操作                        │
│  ├── 好友管理：添加、删除、分组                               │
│  └── 状态管理：在线状态、签名、头像                           │
├─────────────────────────────────────────────────────────────┤
│  协议层                                                       │
│  ├── OpenClaw Protocol                                       │
│  ├── C2C (Client-to-Client) 通信                             │
│  └── 加密传输                                                │
├─────────────────────────────────────────────────────────────┤
│  存储层                                                       │
│  ├── SQLite 本地缓存                                         │
│  ├── 消息历史持久化                                          │
│  └── 联系人缓存                                              │
└─────────────────────────────────────────────────────────────┘
```

## 安装

```bash
# 安装OpenClaw QQ客户端
pip install openclaw-qq

# 或使用npm
npm install openclaw-qq-client
```

## 认证

```bash
# 扫码登录
qq auth --qrcode

# 账号密码登录（不推荐）
qq auth --username <账号> --password <密码>

# 检查认证状态
qq status
```

## 命令参考

### 消息操作

| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `qq send <user_id> <message>` | 发送私聊消息 | 用户沟通、通知推送 |
| `qq recv --limit 100` | 接收最新消息 | 消息监控 |
| `qq history <user_id> --limit 50` | 查看聊天历史 | 历史追溯 |
| `qq search <keyword>` | 搜索消息 | 内容查找 |

### 群聊操作

| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `qq group list` | 列出所有群组 | 群管理 |
| `qq group send <group_id> <message>` | 发送群消息 | 群发通知 |
| `qq group members <group_id>` | 获取群成员 | 成员分析 |
| `qq group kick <group_id> <user_id>` | 踢出成员 | 群管理 |

### 好友操作

| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `qq friends list` | 列出好友列表 | 联系人管理 |
| `qq friends add <user_id> <reason>` | 添加好友 | 拓展人脉 |
| `qq friends delete <user_id>` | 删除好友 | 清理联系人 |
| `qq friends groups` | 好友分组 | 分类管理 |

### 状态管理

| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `qq status set online` | 设置在线状态 | 状态管理 |
| `qq status set busy` | 设置忙碌状态 | 免打扰 |
| `qq signature set <text>` | 设置个性签名 | 个人展示 |

## JSON输出

所有命令支持 `--json` 参数输出结构化数据：

```bash
# JSON格式输出
qq friends list --json
qq group members <group_id> --json
```

输出示例：
```json
{
  "friends": [
    {
      "user_id": "123456789",
      "nickname": "好友昵称",
      "remark": "备注名",
      "group": "分组名",
      "status": "online"
    }
  ],
  "total": 1,
  "timestamp": "2026-03-18T10:00:00Z"
}
```

## 使用场景

### 场景1：自动化客服

```bash
# 监听消息并自动回复
qq listen --on-message "echo '收到：{message}'"
```

### 场景2：群发通知

```bash
# 向多个群发送通知
for group in $(qq group list --id-only); do
  qq group send $group "重要通知：系统维护中"
done
```

### 场景3：消息采集

```bash
# 采集群消息用于分析
qq history <group_id> --limit 1000 --json > messages.json
```

## 与天龙引擎协同

| 天龙Skill | QQ Operations | 协同效果 |
|-----------|--------------|---------|
| **discord-cli** | qq-operations | Discord + QQ 双平台运营 |
| **tg-cli** | qq-operations | Telegram + QQ 双平台运营 |
| **xiaohongshu-cli** | qq-operations | 小红书内容 + QQ社群传播 |
| **35-02 社媒运营** | qq-operations | QQ社群运营能力补充 |

## 安全注意事项

1. **使用专用账号**：建议使用非主账号进行自动化操作
2. **频率限制**：内置请求间隔，避免触发风控
3. **数据加密**：敏感数据本地加密存储
4. **权限最小化**：只请求必要的API权限

## 配置文件

```yaml
# ~/.qq/config.yaml
auth:
  type: qrcode  # qrcode | password
  session_file: ~/.qq/session.json

storage:
  type: sqlite
  path: ~/.qq/data.db

rate_limit:
  message_interval: 2  # 消息发送间隔（秒）
  max_messages_per_hour: 100

logging:
  level: info
  path: ~/.qq/logs/
```

## Python API

```python
from qq_operations import QQClient

async def main():
    client = QQClient()
    await client.auth_qrcode()

    # 发送消息
    await client.send_message(user_id="123456789", message="你好！")

    # 获取好友列表
    friends = await client.get_friends()
    print(friends)

    # 监听消息
    async for message in client.listen():
        print(f"收到消息：{message}")
```

## 错误处理

| 错误码 | 描述 | 处理建议 |
|--------|------|---------|
| `AUTH_FAILED` | 认证失败 | 重新扫码登录 |
| `RATE_LIMITED` | 频率限制 | 降低请求频率 |
| `USER_NOT_FOUND` | 用户不存在 | 检查用户ID |
| `GROUP_NOT_FOUND` | 群不存在 | 检查群ID |
| `PERMISSION_DENIED` | 权限不足 | 检查账号权限 |

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| 1.0.0 | 2026-03-18 | 初始版本，基于OpenClaw协议 |

---

**来源**: [op7418/Claude-to-IM-skill](https://github.com/op7418/Claude-to-IM-skill) QQ模块
**匹配岗位**: 35-02 社媒运营、47-03 IM运营师