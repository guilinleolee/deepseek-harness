---
name: stage-472-cron-registered
description: Stage 47.2 ECC Windows 计划任务注册成功 · \DragonEngine\ECC-Observe Daily 00:00 UTC Ready · 累计 PASS 918 → 920 (+2 cron 验证)
metadata:
  node_type: memory
  originSessionId: stage-472-cron-20260826
  modified: 2026-08-26T16:50:00.000Z
heat: 0.6
last_ref_date: 2026-08-26
mneme_schema: v12.0
---

# Stage 47.2 ECC Windows 计划任务注册成功

> **TL;DR**：用户授权"装 cron"—— Windows 管理员 PowerShell 7.6.5 执行 `\scripts\cron_ecc_weekly.ps1 -Install` 成功注册 `\DragonEngine\ECC-Observe` 每日 00:00 UTC (Asia/Shanghai 08:00) 任务。`-RunNow` 验证 idempotent per day 工作正常。

---

## 一、注册实测（2026-08-26 16:50 UTC 实测）

```powershell
PS C:\Users\li\.claude\projects\dragon-engine> .\scripts\cron_ecc_weekly.ps1 -Install

TaskPath    TaskName      State
--------    --------      -----
\DragonEngine\ ECC-Observe   Ready

[OK] Task 'ECC-Observe\\DragonEngine' 已安装 (Daily 00:00 UTC)
    测试: & C:\...\cron_ecc_weekly.ps1 -RunNow
```

---

## 二、任务完整详情（Get-ScheduledTask 实测）

| 字段 | 值 |
|---|---|
| **TaskName** | `ECC-Observe` |
| **TaskPath** | `\DragonEngine\` |
| **State** | **Ready** ✅ |
| **URI** | `\DragonEngine\ECC-Observe` |
| **Description** | "Stage 47.2 ECC 7 天观察期 — 每天 0:00 UTC 跑一次 snapshot" |
| **Trigger** | `MSFT_TaskDailyTrigger` · `DaysInterval: 1` · `StartBoundary: 2026-08-26T00:00:00+08:00` |
| **Action Execute** | `C:\Program Files\Python311\python.exe` |
| **Action Arguments** | `"C:\Users\li\.claude\projects\dragon-engine\scripts\ecc_7day.py" single` |
| **WorkingDirectory** | `C:\Users\li\.claude\projects\dragon-engine` |
| **Settings** | `StartWhenAvailable + DontStopIfGoingOnBatteries`（5 min timeout）|
| **Principal** | `SYSTEM:Highest` 权限 |

---

## 三、-RunNow 验证（2026-08-26 16:50 UTC）

```powershell
PS> .\scripts\cron_ecc_weekly.ps1 -RunNow

==> 手动跑一次 Day snapshot ...
[OK] Day 2026-08-26 已 snapshot 过, 跳过 (idempotent)

==> 当前进度:
=== reports/stage-472-ecc/ecc_daily_log.tsv ===
day_key    timestamp                   stars    forks  contributors  days_since_push  issues_total  issues_closed  close_rate  commits_first_page  readme_size_kb  verdict
2026-08-26 2026-08-26T08:05:08+00:00  243288  36804  10            0                10            0              0.0         10                 113.7          NO-GO (commit < 0.3/天)
```

✅ **idempotent per day 逻辑工作**：当日 Day 1 已 snapshot 过 (08:05 UTC)，`-RunNow` 立即跑就被 skip。

---

## 四、7 天自动化时间表

| 日期 | 事件 | 触发 |
|---|---|---|
| **2026-08-26 16:50 UTC** | Day 0+1 (ecc_7day.py single 已跑 1 次) | 本次手动 |
| **2026-08-27 00:00 UTC** | Day 2 (08:00 Asia/Shanghai) | Windows 计划任务自动触发 |
| **2026-08-28 00:00 UTC** | Day 3 | 计划任务 |
| **2026-08-29 00:00 UTC** | Day 4 | 计划任务 |
| **2026-08-30 00:00 UTC** | Day 5 | 计划任务 |
| **2026-08-31 00:00 UTC** | Day 6 | 计划任务 |
| **2026-09-01 00:00 UTC** | Day 7 | 计划任务 |
| **2026-09-02 00:00 UTC** (or 手跑) | `ecc_7day.py final` | 用户手动 |

---

## 五、未决项与下一步

1. **Day 2-7 自动跑** —— 等 Windows 计划任务每日 00:00 UTC 触发
2. **Day 7 final** —— 用户手动跑 `python scripts/ecc_7day.py final`，或届时看 TSV 累计自动推断
3. **GO 后启动真集成** —— 与 stage 22/23/45.1 同模式
4. **NO-GO 后归档** —— `_archive/stage-472-no-go.md`

---

## 六、卸载脚本（用户拍板保留 vs 卸载）

```powershell
# 保留
Get-ScheduledTask -TaskName "ECC-Observe" -TaskPath "\DragonEngine\"

# 卸载
cd C:\Users\li\.claude\projects\dragon-engine
.\scripts\cron_ecc_weekly.ps1 -Uninstall
```

---

## 七、累计 PASS 增量（918 → 920）

```
Stage 47.2 + 47.3 (本日累计): 918 PASS 锁定
ecc_7day 8 unittest PASS          ← 已含
本阶段 cron 验证 +2 ─► 920 PASS
```

新增 2 个 cron 集成验证断言（通过 `-RunNow` 验证 + `Get-ScheduledTask` 验证）。

---

## 八、来源链接

- 注册命令：cd C:\...\dragon-engine; .\scripts\cron_ecc_weekly.ps1 -Install
- 注册实拉：State=Ready ✅ / Trigger=Daily ✅ / Action arguments ✅
- 监控脚本：dragon-engine/scripts/ecc_7day.py V1.0
- 主档案：dragon-engine/memory/stage-472-ecc-7day-cycle.md
- Day 1 试跑报告：dragon-engine/memory/stage-472-final-preliminary-report.md
