# log-event Hook

> 记录所有内容事件到事件日志，用于追踪全生命周期和偏差分析。

## 触发时机

`postToolUse` 或 `userPromptSubmit`

## 事件类型

| 事件类型 | 触发条件 | 记录内容 |
|----------|----------|----------|
| **预测提交** | 用户提交预测表单 | 日期、时间、平台、7维度分、总分、预测人 |
| **内容发布** | 发布内容到平台 | 发布ID、平台、时间、话题、标签 |
| **首次复盘(T+3d)** | 发布满72小时 | 7维度实际分、偏差分析、核心洞察 |
| **最终复盘(T+7d)** | 发布满7天 | 最终评分、预测准确度、学习价值 |
| **Rubric更新** | 观察被数据否定 | 观察内容、被否定的原因、新结论 |
| **Buffer变更** | Buffer值变化 | 变更类型(Ship/Shoot)、变更后值、原因 |

## 事件日志格式

```json
{
  "event_id": "evt_YYYYMMDD_HHMMSS_ms",
  "event_type": "PREDICTION_SUBMIT|CONTENT_PUBLISH|RETRO_FIRST|RETRO_FINAL|RUBRIC_UPDATE|BUFFER_CHANGE",
  "timestamp": "YYYY-MM-DD HH:MM:SS",
  "session_id": "sess_XXXXX",
  "data": {
    // 事件类型相关数据
  },
  "metadata": {
    "source": "hook",
    "version": "1.0"
  }
}
```

## 事件存储

路径: `~/.claude/skills/cheat-on-content/logs/events.jsonl`

每条事件追加写入一行JSONL格式。

## 示例事件

```json
{"event_id":"evt_20260525_143022_001","event_type":"PREDICTION_SUBMIT","timestamp":"2026-05-25 14:30:22","session_id":"sess_abc123","data":{"publish_id":"2026-05-25-01","platform":"抖音","topic":"职场沟通","dimensions":{"ER":7,"SR":8,"HP":6,"QL":7,"NA":7,"AB":6,"SAT":7},"total_score":7.1,"predictor":"天龙引擎","confidence":"高"},"metadata":{"source":"log-event-hook","version":"1.0"}}
```

## Buffer状态追踪

Buffer变更也记录到独立日志:

路径: `~/.claude/skills/cheat-on-content/logs/buffer-log.jsonl`

```json
{"event_id":"evt_20260525_143100_002","event_type":"BUFFER_CHANGE","timestamp":"2026-05-25 14:31:00","data":{"change_type":"Ship","previous_value":5,"new_value":4,"reason":"发布内容到抖音"},"metadata":{"source":"log-event-hook","version":"1.0"}}
```

## 使用方式

```bash
# 查询事件
python3 skills/cheat-on-content/hooks/log-event.py query --type PREDICTION_SUBMIT --since "2026-05-01"

# 统计事件
python3 skills/cheat-on-content/hooks/log-event.py stats --days 30

# 导出CSV
python3 skills/cheat-on-content/hooks/log-event.py export --output events.csv
```