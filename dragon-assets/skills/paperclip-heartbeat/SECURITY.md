# SECURITY.md - Paperclip Heartbeat 心跳调度安全指南

> ⚠️ 本Skill涉及生产环境任务调度，请务必阅读本文档

---

## 🔴 高风险操作

### 修改生产心跳 (heartbeat.ts)

**风险**: 修改心跳配置可能影响生产任务执行

**症状**:
- 任务执行频率改变
- 任务被意外暂停/启用
- 多个任务冲突

**安全操作流程**:
```bash
# 1. 查看当前心跳状态
./heartbeat.sh status

# 2. 先在测试环境验证
./heartbeat.sh add task1 "0 9 * * *" --dry-run

# 3. 应用到生产
./heartbeat.sh add task1 "0 9 * * *" --apply
```

### 删除心跳任务

**风险**: 删除正在运行的任务可能导致数据丢失

**安全操作流程**:
```bash
# 1. 检查任务是否正在运行
./heartbeat.sh status task1

# 2. 如果正在运行，等待完成或强制停止
./heartbeat.sh wait task1 --timeout 300
# 或
./heartbeat.sh force-stop task1

# 3. 删除任务
./heartbeat.sh remove task1
```

---

## 🟡 中风险操作

### 暂停/恢复心跳

**风险**: 暂停可能导致定时任务错过执行

**安全操作流程**:
```bash
# 1. 记录暂停原因
./heartbeat.sh pause task1 --reason "维护中"

# 2. 恢复时检查错过的任务
./heartbeat.sh resume task1 --check-missed

# 3. 如有错过，手动触发
./heartbeat.sh trigger task1
```

### 修改Cron表达式

**风险**: 错误的Cron表达式可能导致任务在错误时间执行

**安全操作流程**:
```bash
# 1. 验证Cron表达式
./heartbeat.sh validate "0 9 * * 1-5"

# 2. 预览接下来5次执行时间
./heartbeat.sh preview "0 9 * * 1-5" --count 5

# 3. 应用
./heartbeat.sh update task1 --cron "0 9 * * 1-5"
```

---

## 📋 心跳状态监控

```bash
# 查看所有心跳状态
/heartbeat-status

# 查看特定任务
/heartbeat-status task1

# 实时监控
/heartbeat-monitor
```

---

## 🐛 常见陷阱

### 陷阱1: Cron表达式错误

**症状**: 任务在错误时间执行

**原因**: Cron表达式理解错误

**解决方案**:
```bash
# 使用在线工具验证
# https://crontab.guru/

# 或使用内置验证
./heartbeat.sh validate "你的表达式"
```

### 陷阱2: 时区问题

**症状**: 任务执行时间与预期不符

**原因**: 服务器时区与本地时区不同

**解决方案**:
```bash
# 检查服务器时区
./heartbeat.sh show-timezone

# 指定时区
./heartbeat.sh add task1 "0 9 * * *" --timezone "Asia/Shanghai"
```

### 陷阱3: 任务重叠

**症状**: 同一任务多次同时执行

**原因**: 上一次执行未完成，新触发又开始

**解决方案**:
```bash
# 启用任务锁
./heartbeat.sh add task1 "*/5 * * * *" --lock

# 或设置超时
./heartbeat.sh add task1 "*/5 * * * *" --timeout 300
```

---

**版本**: 1.0.0
**更新时间**: 2026-03-18