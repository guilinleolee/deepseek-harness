# buffer-guard Hook

> **Buffer管理器** — 管理内容创作Buffer，防止过度发布。

## 核心概念

**Buffer**: 允许同时进行的"未完成复盘"内容量
- **初始值**: 5
- **限制**: Buffer为0时不能发布新内容

## Buffer规则

| 事件 | Buffer变化 | 说明 |
|------|-----------|------|
| 内容发布(Ship) | -1 | 开始一个内容周期，锁定Buffer |
| 内容制作完成(Shoot) | +1 | 制作完成，准备发布，Buffer恢复 |
| T+3d首次复盘完成 | 0 | 不增加Buffer，但解锁发布资格 |
| T+7d最终复盘完成 | 0 | 不增加Buffer，完成归档 |

## 关键理解

**Buffer不是"发布配额"，而是"未完成复盘的上限"**

- 发布后Buffer减1，表示"还有1个内容等待复盘"
- 完成复盘后Buffer不变，但"解锁"了新的发布资格
- Buffer耗尽意味着"有太多内容还没复盘"

## 触发时机

`preToolUse` — 在执行发布相关操作前检查Buffer

## 检查逻辑

```python
def check_buffer_for_publish():
    """检查是否可以发布"""
    current = get_buffer()

    if current <= 0:
        return {
            "allowed": False,
            "message": f"Buffer已耗尽({current}/5)，无法发布新内容",
            "reason": "太多内容尚未复盘",
            "pending_retro_count": get_pending_retro_count(),
            "suggestion": "请先完成T+3d复盘"
        }

    return {"allowed": True, "current": current}
```

## Buffer变更事件

### Ship (发布内容)

```python
def on_publish(publish_id: str):
    """发布内容时调用"""
    current = decrement_buffer()
    create_retro_schedule(publish_id)  # 自动创建复盘任务

    log_event({
        "event_type": "BUFFER_CHANGE",
        "change_type": "Ship",
        "previous_value": current + 1,
        "new_value": current,
        "reason": f"发布内容 {publish_id}"
    })
```

### Shoot (制作完成)

```python
def on_shoot_complete(publish_id: str):
    """内容制作完成时调用"""
    current = increment_buffer()

    log_event({
        "event_type": "BUFFER_CHANGE",
        "change_type": "Shoot",
        "previous_value": current - 1,
        "new_value": current,
        "reason": f"内容 {publish_id} 制作完成"
    })
```

## 可视化状态

### Buffer状态条

```
Buffer: ████████░░ 4/5

已发布待复盘:
- 2026-05-24-01 [抖音] 职场沟通 (T+1d)
- 2026-05-23-01 [小红书] 效率工具 (T+2d)
```

### 状态颜色

| Buffer值 | 状态 | 颜色 |
|---------|------|------|
| 5 | 空闲 | 🟢 绿色 |
| 3-4 | 正常 | 🟢 绿色 |
| 1-2 | 警告 | 🟡 黄色 |
| 0 | 耗尽 | 🔴 红色 |

## Buffer预警

当Buffer ≤ 2时，发布提醒:

```
⚠️ Buffer偏低

当前Buffer: 2/5
状态: 🟡 警告

提示: 您的Buffer即将耗尽。建议先完成部分复盘再发布新内容。

当前待复盘: 3个
建议优先完成:
1. 2026-05-22-01 [抖音] 职场沟通 (T+3d逾期)
2. 2026-05-22-02 [小红书] 效率工具 (T+2d)
```

## 使用方式

```bash
# 查看当前Buffer状态
python3 skills/cheat-on-content/hooks/buffer-guard.py status

# 手动调整Buffer(仅用于修正错误)
python3 skills/cheat-on-content/hooks/buffer-guard.py set --value 4 --reason "修正计算错误"

# 查看Buffer历史
python3 skills/cheat-on-content/hooks/buffer-guard.py history --days 30

# 导出Buffer统计
python3 skills/cheat-on-content/hooks/buffer-guard.py export --output buffer_stats.csv
```

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
    "auto_create_retro_on_ship": true
  }
}
```

## 数据存储

Buffer状态存储在:

```
~/.claude/skills/cheat-on-content/state/
├── buffer.json          # 当前Buffer值
└── buffer-history.jsonl # Buffer变更历史
```

```json
{
  "current": 4,
  "max": 5,
  "updated": "2026-05-25T14:30:00",
  "updated_by": "天龙引擎"
}
```