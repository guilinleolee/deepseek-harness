# buffer-manager

> **Buffer管理器** — 管理内容创作Buffer，防止过度发布。

## 核心概念

**Buffer**: 允许同时进行的"未完成复盘"内容量
- **初始值**: 5
- **最大值**: 5
- **最小值**: 0
- **限制**: Buffer为0时不能发布新内容

## Buffer规则

| 事件 | Buffer变化 | 规则 |
|------|-----------|------|
| 内容发布(Ship) | -1 | 开始一个内容周期，锁定Buffer |
| 内容制作完成(Shoot) | +1 | 完成制作，准备发布，Buffer恢复 |
| T+3d首次复盘完成 | 0 | 不增加Buffer，但解锁发布资格 |
| T+7d最终复盘完成 | 0 | 不增加Buffer，完成归档 |

## 关键理解

**Buffer不是"发布配额"，而是"未完成复盘的上限"**

- 发布后Buffer减1，表示"还有1个内容等待复盘"
- 完成复盘后Buffer不变，但"解锁"了新的发布资格
- Buffer耗尽意味着"有太多内容还没复盘"

## 使用方式

### 查看Buffer状态

```bash
# 查看当前Buffer
python3 skills/cheat-on-content/tools/buffer-manager.py status

# 详细视图
python3 skills/cheat-on-content/tools/buffer-manager.py status --verbose
```

### 输出示例

```
Buffer: ████████░░ 4/5

状态: 🟢 正常

已发布待复盘:
┌─────────────────────────────────────────────────────────────┐
│ #1 2026-05-24-01 [抖音] 职场沟通     T+1d 状态: 🟢正常 │
├─────────────────────────────────────────────────────────────┤
│ #2 2026-05-23-01 [小红书] 效率工具   T+2d 状态: 🟢正常 │
├─────────────────────────────────────────────────────────────┤
│ #3 2026-05-22-01 [微博] AI趋势       T+3d 状态: 🟡待复盘 │
├─────────────────────────────────────────────────────────────┤
│ #4 2026-05-22-02 [抖音] 时间管理     T+3d 状态: 🔴逾期   │
└─────────────────────────────────────────────────────────────┘

提示: 请尽快完成T+3d复盘以解锁发布资格
```

### 事件操作

```bash
# 发布内容 (Ship) - Buffer -1
python3 skills/cheat-on-content/tools/buffer-manager.py ship \
  --id 2026-05-25-01 \
  --platform 抖音 \
  --topic "职场沟通技巧"

# 制作完成 (Shoot) - Buffer +1
python3 skills/cheat-on-content/tools/buffer-manager.py shoot \
  --id 2026-05-25-02

# 完成T+3d复盘 - 解锁发布资格
python3 skills/cheat-on-content/tools/buffer-manager.py complete-t3d \
  --id 2026-05-22-01

# 完成T+7d复盘 - 完成归档
python3 skills/cheat-on-content/tools/buffer-manager.py complete-t7d \
  --id 2026-05-18-01
```

### 发布检查

```bash
# 检查是否可以发布
python3 skills/cheat-on-content/tools/buffer-manager.py can-publish

# 强制检查（包含警告）
python3 skills/cheat-on-content/tools/buffer-manager.py can-publish --strict
```

### 发布锁定消息

当Buffer=0时:

```
❌ Buffer已耗尽，无法发布新内容

当前Buffer: 0/5
状态: 🔴 耗尽

根据铁律，您需要先完成T+3d复盘才能继续发布。

待复盘内容 (4个):
  🔴 2026-05-22-01 [微博] AI趋势     T+3d 逾期2天
  🔴 2026-05-22-02 [抖音] 时间管理   T+3d 逾期2天
  🟡 2026-05-23-01 [小红书] 效率工具 T+3d 明天到期
  🟡 2026-05-24-01 [抖音] 职场沟通   T+3d 后天到期

建议操作:
  1. 立即完成逾期复盘: python3 .../buffer-manager.py complete-t3d --id 2026-05-22-01
  2. 查看所有待复盘: python3 .../buffer-manager.py pending
```

### 预警提示

当Buffer≤2时:

```
⚠️ Buffer偏低

当前Buffer: 2/5
状态: 🟡 警告

提示: 您的Buffer即将耗尽。建议先完成部分复盘再发布新内容。

当前待复盘: 3个
建议优先完成:
  1. 2026-05-22-01 [微博] AI趋势 (T+3d逾期)
  2. 2026-05-22-02 [抖音] 时间管理 (T+3d逾期)
```

### 历史记录

```bash
# 查看Buffer历史
python3 skills/cheat-on-content/tools/buffer-manager.py history --days 30

# 导出统计
python3 skills/cheat-on-content/tools/buffer-manager.py export \
  --output buffer_stats.csv
```

## Buffer变更日志

```jsonl
{"timestamp":"2026-05-25T10:00:00","event":"BUFFER_CHANGE","type":"Ship","previous":5,"new":4,"reason":"发布内容 2026-05-25-01","user":"天龙引擎"}
{"timestamp":"2026-05-25T14:00:00","event":"BUFFER_CHANGE","type":"Shoot","previous":4,"new":5,"reason":"内容 2026-05-25-02 制作完成","user":"天龙引擎"}
{"timestamp":"2026-05-25T15:00:00","event":"RETRO_COMPLETE","type":"T+3d","publish_id":"2026-05-22-01","buffer_before":4,"buffer_after":4,"status":"unlocked","user":"天龙引擎"}
```

## 手动调整

```bash
# 手动调整Buffer（仅用于修正错误）
python3 skills/cheat-on-content/tools/buffer-manager.py set \
  --value 4 \
  --reason "修正计算错误"

# 重置Buffer（谨慎使用）
python3 skills/cheat-on-content/tools/buffer-manager.py reset \
  --confirm "我确认要重置Buffer"
```

## 状态颜色

| Buffer值 | 状态 | 颜色 | 说明 |
|---------|------|------|------|
| 5 | 空闲 | 🟢 绿色 | Buffer充足，可正常发布 |
| 3-4 | 正常 | 🟢 绿色 | Buffer正常 |
| 1-2 | 警告 | 🟡 黄色 | Buffer偏低，建议完成复盘 |
| 0 | 耗尽 | 🔴 红色 | 无法发布，必须先完成复盘 |

## 配置

```json
{
  "buffer": {
    "initial": 5,
    "min": 0,
    "max": 5,
    "ship_decrement": 1,
    "shoot_increment": 1,
    "warning_threshold": 2,
    "critical_threshold": 0,
    "auto_create_retro_on_ship": true,
    "auto_unlock_on_t3d": true,
    "auto_archive_on_t7d": true
  }
}
```

## 数据存储

```
~/.claude/skills/cheat-on-content/
├── state/
│   ├── buffer.json              # 当前Buffer值
│   ├── buffer-history.jsonl     # Buffer变更历史
│   └── pending-retros.json      # 待复盘队列
├── content/
│   └── YYYY-MM/
│       └── YYYY-MM-DD-XX.json   # 内容详情
└── logs/
    └── buffer-events.jsonl     # 所有Buffer事件
```

### buffer.json 格式

```json
{
  "current": 4,
  "max": 5,
  "updated": "2026-05-25T14:30:00",
  "updated_by": "天龙引擎",
  "pending_count": 1,
  "overdue_count": 0
}
```

### pending-retros.json 格式

```json
{
  "pending_retros": [
    {
      "publish_id": "2026-05-24-01",
      "platform": "抖音",
      "topic": "职场沟通",
      "publish_date": "2026-05-24",
      "t3d_due_date": "2026-05-27",
      "t7d_due_date": "2026-05-31",
      "t3d_status": "pending",
      "t7d_status": "pending",
      "days_since_publish": 1,
      "is_overdue": false
    }
  ],
  "updated": "2026-05-25T14:30:00"
}
```
