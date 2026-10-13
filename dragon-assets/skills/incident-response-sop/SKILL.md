---
license: UNKNOWN
github_repo: CuriousLearnerDev/Online_tools
github_hash: 1ccce0d74a00b23f5744e6e39da303b4feac8d12
triggers: ["incident response sop", "incident-response-sop"]
---
# incident-response-sop

## L0: 一句话描述 (≤15字)
应急响应标准流程

## L1: 使用场景 (50-100字)
安全事件应急响应标准操作流程，配合17-06应急响应工程师和05安全师，实现从事件发现到恢复的完整应急响应。

## L2: 详细文档

### 来源项目
> [CuriousLearnerDev/Online_tools](https://github.com/CuriousLearnerDev/Online_tools) - 安全工具编排平台

### SOP阶段

| 阶段 | 时限 | 关键动作 |
|------|------|---------|
| **准备阶段** | 日常 | 预案制定、工具准备、团队培训 |
| **发现阶段** | 0-15min | 告警确认、初步研判 |
| **遏制阶段** | 15-60min | 隔离止损、阻断传播 |
| **根除阶段** | 1-24h | 清除后门、修复漏洞 |
| **恢复阶段** | 24-72h | 系统恢复、验证确认 |
| **事后阶段** | 1-4周 | 复盘总结、改进措施 |

### 核心命令速查

```bash
# 应急响应
prepare_check()       # 预案检查
alert_confirm()      # 告警确认
isolate_block()       # 隔离阻断
backdoor_remove()     # 后门清除
system_recover()      # 系统恢复
incident_report()     # 事件报告

# 取证分析
memory_dump()         # 内存取证
disk_acquire()       # 磁盘镜像
log_analyze()        # 日志分析
timeline_build()      # 攻击时间线
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **17-06应急响应工程师** | 新增 | 完整SOP流程执行 |
| **05安全师** | V8.84→V8.91 | 应急响应指挥 |
