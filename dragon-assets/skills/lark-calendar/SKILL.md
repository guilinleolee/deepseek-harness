---
license: UNKNOWN
triggers: ["lark calendar", "Lark Calendar Skill"]
---
# Lark Calendar Skill

> 飞书/Lark 日历操作能力 - 日历/事件管理、空闲状态查询

## 核心能力

| 能力 | 功能 | 使用场景 |
|------|------|---------|
| **日历管理** | 创建/删除/更新日历 | 日程管理 |
| **事件管理** | 创建/更新/删除事件 | 会议安排 |
| **参会人管理** | 添加/移除参会人 | 会议协调 |
| **空闲查询** | 查询空闲时间 | 日程协调 |

## 安装要求

```bash
npm install -g openclaw
node --version  # >= 22
```

## 配置

### 飞书开放平台权限

- `calendar:calendar` - 日历操作
- `calendar:calendar:readonly` - 日历只读
- `calendar:event` - 事件操作

### 环境变量

```bash
export LARK_APP_ID="your_app_id"
export LARK_APP_SECRET="your_app_secret"
```

## 命令参考

### 日历管理

```bash
# 创建日历
/lark-calendar create --name "项目日历" --description "项目相关日程"

# 获取日历列表
/lark-calendar list

# 更新日历
/lark-calendar update --calendar-id "cal_xxx" --name "新名称"

# 删除日历
/lark-calendar delete --calendar-id "cal_xxx"
```

### 事件管理

```bash
# 创建事件
/lark-calendar create-event --calendar-id "cal_xxx" \
  --summary "项目评审会" \
  --start "2026-03-15T14:00:00" \
  --end "2026-03-15T15:00:00"

# 创建全天事件
/lark-calendar create-event --calendar-id "cal_xxx" \
  --summary "项目上线日" \
  --all-day \
  --date "2026-03-20"

# 更新事件
/lark-calendar update-event --event-id "evt_xxx" \
  --summary "延期会议" \
  --start "2026-03-15T16:00:00"

# 删除事件
/lark-calendar delete-event --event-id "evt_xxx"

# 查询事件
/lark-calendar query-events --calendar-id "cal_xxx" \
  --start "2026-03-01" \
  --end "2026-03-31"
```

### 参会人管理

```bash
# 添加参会人
/lark-calendar add-attendees --event-id "evt_xxx" \
  --attendees '["ou_xxx", "ou_yyy"]'

# 移除参会人
/lark-calendar remove-attendees --event-id "evt_xxx" \
  --attendees '["ou_xxx"]'

# 查询参会人空闲时间
/lark-calendar query-free-time --attendees '["ou_xxx", "ou_yyy"]' \
  --start "2026-03-15T09:00:00" \
  --end "2026-03-15T18:00:00"
```

## Python API

```python
from lark_calendar import LarkCalendar

# 初始化
calendar = LarkCalendar(app_id, app_secret)

# 创建日历
cal_id = calendar.create(name="项目日历", description="项目相关日程")

# 创建事件
event_id = calendar.create_event(
    calendar_id=cal_id,
    summary="项目评审会",
    start="2026-03-15T14:00:00",
    end="2026-03-15T15:00:00",
    attendees=["ou_xxx", "ou_yyy"],
    location="会议室A",
    reminder=15  # 15分钟前提醒
)

# 查询事件
events = calendar.query_events(
    calendar_id=cal_id,
    start="2026-03-01",
    end="2026-03-31"
)

# 查询空闲时间
free_slots = calendar.query_free_time(
    attendees=["ou_xxx", "ou_yyy"],
    start="2026-03-15T09:00:00",
    end="2026-03-15T18:00:00"
)

# 自动安排会议
best_slot = calendar.find_best_slot(
    attendees=["ou_xxx", "ou_yyy", "ou_zzz"],
    duration=60,  # 1小时
    date_range=("2026-03-15", "2026-03-16"),
    work_hours=(9, 18)
)
```

## 天龙岗位映射

| 岗位 | 使用场景 | 匹配度 |
|------|---------|--------|
| **08 发布师** | 发布时间安排、里程碑管理 | ⭐⭐⭐⭐⭐ |
| **90-01 人力资源总监** | 面试安排、培训日程 | ⭐⭐⭐⭐⭐ |
| **50-01 产品策划** | 迭代规划、评审安排 | ⭐⭐⭐⭐ |
| **01 调研师** | 用户访谈安排 | ⭐⭐⭐⭐ |

## 使用示例

### 示例1：自动安排会议

```python
# 智能安排项目评审会
best_slot = calendar.find_best_slot(
    attendees=["张三", "李四", "王五"],
    duration=90,
    date_range=("2026-03-15", "2026-03-17"),
    work_hours=(10, 18),  # 10点-18点
    avoid_lunch=True
)

# 自动创建会议
calendar.create_event(
    calendar_id="cal_xxx",
    summary="项目评审会",
    start=best_slot["start"],
    end=best_slot["end"],
    attendees=best_slot["available_attendees"]
)
```

### 示例2：发布日程管理

```python
# 创建发布日历
release_cal = calendar.create(name="V8.33发布日程")

# 添加里程碑
milestones = [
    {"summary": "代码冻结", "date": "2026-03-18", "all_day": True},
    {"summary": "测试完成", "date": "2026-03-20", "all_day": True},
    {"summary": "正式发布", "date": "2026-03-22", "all_day": True}
]

for m in milestones:
    calendar.create_event(calendar_id=release_cal, **m)
```

### 示例3：面试安排

```python
# 自动安排面试
interview_slots = calendar.schedule_interviews(
    candidate="候选人A",
    interviewers=["技术官", "产品经理", "HR"],
    duration=60,
    date_range=("2026-03-15", "2026-03-16")
)
```

## 事件属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `summary` | string | 事件标题 |
| `description` | string | 事件描述 |
| `start` | datetime | 开始时间 |
| `end` | datetime | 结束时间 |
| `all_day` | boolean | 是否全天 |
| `location` | string | 地点 |
| `attendees` | list | 参会人ID列表 |
| `reminder` | int | 提醒时间（分钟） |
| `recurrence` | string | 重复规则 |

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| 1.0.0 | 2026-03-14 | 初始版本，支持日历/事件管理、空闲查询 |