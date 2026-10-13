# retro-check Hook

> **复盘触发器** — 确保每次发布后都进行T+3d和T+7d复盘。

## 触发时机

两种触发模式:

1. **定时触发**: 会话启动时检查 (`sessionStart`)
2. **事件触发**: 内容发布时自动创建复盘提醒

## 复盘时间线

```
发布日(T+0)
    │
    ├── 创建复盘任务
    │   - T+3d首次复盘
    │   - T+7d最终复盘
    │
    ▼
T+3d (首次复盘)
    │
    ├── 填写复盘模板
    ├── 偏差分析
    ├── 更新Rubric观察
    └── 触发Rubric验证检查
    │
    ▼
T+7d (最终复盘)
    │
    ├── 填写最终评分
    ├── 预测准确度统计
    ├── 学习价值评估
    └── 归档签字
```

## 检查逻辑

### T+3d检查

```python
def check_t3d_retro():
    """检查T+3d复盘是否完成"""
    pending = get_pending_retros("T+3d")

    for item in pending:
        days_since_publish = (today() - item.publish_date).days

        if days_since_publish >= 3:
            if item.retro_status == "pending":
                return {
                    "status": "overdue",
                    "item": item,
                    "message": f"内容 {item.publish_id} 已发布{days_since_publish}天,首次复盘逾期"
                }

        if days_since_publish >= 5:
            return {
                "status": "critical_overdue",
                "item": item,
                "message": f"内容 {item.publish_id} 已发布{days_since_publish}天,复盘严重逾期"
            }

    return {"status": "ok"}
```

### T+7d检查

```python
def check_t7d_retro():
    """检查T+7d最终复盘是否完成"""
    pending = get_pending_retros("T+7d")

    for item in pending:
        days_since_publish = (today() - item.publish_date).days

        if days_since_publish >= 7:
            if item.final_retro_status == "pending":
                return {
                    "status": "overdue",
                    "item": item,
                    "message": f"内容 {item.publish_id} 已发布{days_since_publish}天,最终复盘逾期"
                }

    return {"status": "ok"}
```

## 提醒消息格式

### T+3d首次复盘提醒

```
📋 复盘提醒 (T+3d)

内容: 2026-05-22-01 [抖音] 职场沟通
发布日期: 2026-05-22
距发布: 3天 ⏰ 今天应该复盘

请使用复盘模板完成首次复盘:
  python3 skills/cheat-on-content/hooks/retro-check.py retro --id 2026-05-22-01 --type t3d
```

### T+7d最终复盘提醒

```
📋 复盘提醒 (T+7d)

内容: 2026-05-18-01 [小红书] 效率工具
发布日期: 2026-05-18
距发布: 7天 ⏰ 今天应该最终复盘

请使用复盘模板完成最终复盘:
  python3 skills/cheat-on-content/hooks/retro-check.py retro --id 2026-05-18-01 --type t7d
```

## 发布锁定规则

根据铁律，复盘完成前不能发布新内容:

```
🔒 发布锁定

当前状态: Buffer=3/5

⚠️ 您有 2 个待复盘内容尚未完成:
- 2026-05-22-01 [抖音] 职场沟通 (T+3d逾期)
- 2026-05-22-02 [小红书] 效率工具 (T+3d逾期)

根据铁律，完成复盘前不能发布新内容。

请先完成复盘:
  python3 skills/cheat-on-content/hooks/retro-check.py retro-all --pending-only
```

### 例外情况

如果Buffer充足(≥3)且确实需要发布，可以申请临时解锁:

```bash
python3 skills/cheat-on-content/hooks/retro-check.py unlock-temp --reason "紧急蹭热点" --duration "24h"
```

## 复盘完成流程

```python
def complete_retro(publish_id: str, retro_type: str):
    """完成复盘"""
    item = get_publish_item(publish_id)

    if retro_type == "T+3d":
        item.retro_status = "completed"
        item.t3d_completed_date = today()
        item.t3d_completed_by = current_user()
    elif retro_type == "T+7d":
        item.final_retro_status = "completed"
        item.t7d_completed_date = today()
        item.t7d_completed_by = current_user()
        item.archived = True

    save(item)

    # 触发Rubric验证
    trigger_rubric_verification(publish_id)
```

## 使用方式

```bash
# 检查所有待复盘内容
python3 skills/cheat-on-content/hooks/retro-check.py status

# 完成T+3d复盘
python3 skills/cheat-on-content/hooks/retro-check.py retro --id 2026-05-22-01 --type t3d

# 完成T+7d最终复盘
python3 skills/cheat-on-content/hooks/retro-check.py retro --id 2026-05-18-01 --type t7d

# 完成所有待复盘
python3 skills/cheat-on-content/hooks/retro-check.py retro-all --pending-only

# 创建新发布时自动创建复盘任务
python3 skills/cheat-on-content/hooks/retro-check.py schedule --id 2026-05-25-01 --publish-date 2026-05-25
```

## 配置

```json
{
  "retro": {
    "t3d_reminder_days": [3, 4, 5],
    "t7d_reminder_days": [7, 8, 9],
    "lock_publish_until_t3d": true,
    "temp_unlock_requires_reason": true,
    "temp_unlock_max_duration_hours": 24
  }
}
```