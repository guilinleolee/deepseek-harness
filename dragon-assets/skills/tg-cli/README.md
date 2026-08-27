# tg-cli Skill - 天龙引擎集成

> Telegram CLI 工具，支持私有频道访问、本地缓存、高级搜索

## 快速开始

```bash
# 安装
uv tool install kabi-tg-cli

# 首次认证
tg chats  # 输入手机号 + 验证码

# 检查状态
tg status --yaml
tg whoami --yaml
```

## 核心能力

| 能力 | 命令 | 说明 |
|------|------|------|
| **数据获取** | `tg search`, `tg history`, `tg export` | 私有频道访问、完整历史 |
| **高级搜索** | `tg search "Rust\|Golang" --regex` | 正则+时间/发送者过滤 |
| **本地缓存** | `tg refresh`, `tg sync` | SQLite持久化、离线查询 |
| **发送消息** | `tg send CHAT "消息"` | 发送消息到群组/频道 |
| **实时监听** | `tg listen --persist` | 近实时缓存更新 |

## 与 Agent-Reach 的区别

| 维度 | Agent-Reach | tg-cli |
|------|------------|--------|
| **访问范围** | 公开频道 | 私有+公开频道 |
| **认证方式** | 无需登录 | MTProto个人账号 |
| **本地缓存** | 无 | SQLite持久化 |
| **风险等级** | 🟢 低 | 🟠 中 |

## 安全使用指南

### ⚠️ 风险提示

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| 账号封禁 | 🟠 中 | 使用专用账号 |
| 速率限制 | 🟡 低 | 每天仅1-2次同步 |
| 隐私风险 | 🟡 低 | 遵守平台规则 |

### 推荐配置

```bash
# 使用专用账号（非主账号）
# 设置环境变量
export TG_SYNC_LIMIT=50      # 每次最多同步50个聊天
export TG_SYNC_DELAY=1       # 每个聊天间隔1秒

# 使用安全封装器
python skills/tg-cli/tg-cli-wrapper.py refresh --max-chats 50
python skills/tg-cli/tg-cli-wrapper.py search "关键词" --yaml
```

### 安全封装器

`tg-cli-wrapper.py` 提供额外保护：
- ✅ 每日同步次数限制（默认2次）
- ✅ 风险命令确认提示
- ✅ 速率限制参数自动添加
- ✅ 默认 YAML 输出（节省 Token）

## 天龙岗位使用示例

### 01调研师

```bash
# 私有频道研究
tg search "技术架构" -c "ArchGroup" --yaml

# 历史消息分析
tg history "GroupName" -n 1000 --yaml > history.yaml

# 正则搜索
tg search "Rust|Golang|Python" --regex --yaml
```

### 32-01市场研究

```bash
# 竞品群组监控
tg refresh --yaml
tg filter "竞品A,竞品B" --hours 24 --yaml

# 趋势追踪
tg top -c "TargetGroup" --hours 168 --yaml
tg timeline --by day --sync-first
```

### 07记录师

```bash
# 数据归档
tg export "ImportantGroup" -f yaml -o archive.yaml

# 定期同步
# crontab: 0 9 * * * tg refresh --yaml >> /tmp/tg-refresh.log
```

### 35-02社媒运营

```bash
# 发送消息（谨慎使用）
tg send "GroupName" "公告内容"

# 实时监控
tg listen --persist
```

## 输出格式

所有命令支持 `--yaml` 或 `--json`：

```yaml
# 成功响应
ok: true
schema_version: "1"
data:
  - id: 123
    text: "消息内容"
    date: "2026-03-12T10:00:00"

# 错误响应
ok: false
schema_version: "1"
error:
  code: chat_not_found
  message: Chat 'foo' not found in database.
```

## 常见问题

### Q: 与 Agent-Reach 如何选择？

**优先使用 Agent-Reach**（公开频道、无风险），**tg-cli 补充**（私有频道、需要缓存时）。

### Q: 每天同步几次合适？

**推荐 1-2 次**。频繁同步可能触发 Telegram 速率限制。

### Q: 可以用主账号吗？

**不推荐**。建议使用专用账号，避免主账号风险。

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| V8.22 | 2026-03-12 | tg-cli 集成（私有频道访问 + 本地缓存） |