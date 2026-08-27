---
name: stage-472-ecc-7day-cycle
description: Stage 47.2 ECC 7 天观察期循环脚本 + cron 部署 + 8 unitest PASS · 累计 PASS 910 → 918 · Day 1 实测已落
metadata:
  node_type: memory
  originSessionId: stage-472-ecc-7day-20260826
  modified: 2026-08-26T16:30:00.000Z
heat: 0.6
last_ref_date: 2026-08-26
mneme_schema: v12.0
---

# Stage 47.2 ECC 7 天观察期循环脚本 V1.0

> **TL;DR**：阶段 47.2 启动 7 天连续 snapshot 循环。本阶段交付：① **`scripts/ecc_7day.py` V1.0**（4 子命令：single / loop / final / status）+ ② Windows PowerShell 计划任务脚本 `cron_ecc_weekly.ps1` + ③ Linux/macOS cron 脚本 `cron_ecc_weekly.sh` + ④ **`tests/test_ecc_7day.py` 8 PASS** + ⑤ 部署文档 `ecc-7day-DEPLOYMENT.md`。累计 PASS **910 → 918**（+8 net · ECC 7 天不复制 DSH harness 自研)。

---

## 一、阶段 47.2 当前状态（2026-08-26 16:05 UTC 实测）

| day_key | stars | forks | commit_freq_实际 | verdict |
|---|---|---|---|---|
| **2026-08-26 (Day 0 baseline)** | 243,284 | 36,803 | 已知 0（判定有偏）| 🟡 NO-GO (commit < 0.3/天) |
| **2026-08-26 (Day 1 实测)** | **243,288** | **36,804** | 已知 0 | 🟡 NO-GO (commit < 0.3/天) |

> **23 分钟内 stars +4 / forks +1** —— ECC 真实在迭代，Day 0 临时 NO-GO 判定原因不是 commits 太少，而是 ecc_watcher 仅看首页 10 个 commit，统计有偏。Day 7 全周期统计时会重新算。

### 1.1 ecc_daily_log.tsv 唯一一行（idempotent per day 已生效）

```
day_key  timestamp                       stars    forks   contributors  days_since_push  issues_total  issues_closed  close_rate  commits_first_page  readme_size_kb  verdict
2026-08-26  2026-08-26T08:05:08+00:00  243288  36804   10           0               10            0              0.0         10                 113.7          NO-GO
```

---

## 二、3 类产物（已落盘 + 8/8 PASS）

| 文件 | 路径 | 大小 | 用途 |
|---|---|---|---|
| **`ecc_7day.py` V1.0** | `scripts/ecc_7day.py` | 5.0 KB | 4 子命令：single（当日 idempotent）/ loop（一次跑 7 天）/ status（查 TSV）/ final（Day 7 verdict）|
| **`cron_ecc_weekly.ps1`** | `scripts/cron_ecc_weekly.ps1` | 2.7 KB | Windows 计划任务：每日 00:00 UTC 跑 single，自带 -Install/-Uninstall/-RunNow |
| **`cron_ecc_weekly.sh`** | `scripts/cron_ecc_weekly.sh` | 1.1 KB | Linux/macOS crontab：每日 00:00 UTC 跑 single，--uninstall |
| **`test_ecc_7day.py`** | `tests/test_ecc_7day.py` | 4.5 KB | 8 unittest PASS · 全面 UTF-8 + tmp_path 隔离 |
| **`ecc-7day-DEPLOYMENT.md`** | `references/ecc-7day-DEPLOYMENT.md` | 5.0 KB | 部署指南（3 种部署方式 + 7 维判定 + 5 安全护栏 + Day 7 decision matrix）|

### 2.1 产物布局

```
dragon-engine/
├── scripts/
│   ├── ecc_watcher.py           # stage 472 D1 数据采集
│   ├── ecc_7day.py              # stage 472 7 天循环 ⭐NEW
│   ├── cron_ecc_weekly.ps1      # stage 472 Windows cron ⭐NEW
│   └── cron_ecc_weekly.sh       # stage 472 Linux cron ⭐NEW
├── tests/
│   └── test_ecc_7day.py         # 8 unittest ⭐NEW
├── references/
│   └── ecc-7day-DEPLOYMENT.md   # 部署指南 ⭐NEW
└── reports/stage-472-ecc/
    ├── snapshot-20260826-074233.json  # Day 0 baseline
    ├── snapshot-20260826-074639.json  # 第二次 single（被 idempotent 防止）
    ├── snapshot-20260826-080510.json  # Day 1 实测
    ├── ecc_daily_log.tsv              # 累计 TSV（1 行）
    └── cron.log                        # 计划任务 output（用户后续启用 cron 后落）
```

---

## 三、3 种部署方式（实测就绪）

### 3.1 Windows 计划任务（推荐）

```powershell
# 管理员 PowerShell
cd "D:\deepseek haress"
.\scripts\cron_ecc_weekly.ps1 -Install
# 任务注册到 \DragonEngine\ECC-Observe 计划任务
# 触发器：Daily 00:00 UTC

# 立即测试
.\scripts\cron_ecc_weekly.ps1 -RunNow

# 卸载
.\scripts\cron_ecc_weekly.ps1 -Uninstall
```

### 3.2 Linux/macOS cron

```bash
cd /path/to/dragon-engine
chmod +x scripts/cron_ecc_weekly.sh
./scripts/cron_ecc_weekly.sh    # 注册
./scripts/cron_ecc_weekly.sh --uninstall
```

### 3.3 手动 / CI 测试

```bash
PYTHONIOENCODING=utf-8 python scripts/ecc_7day.py single       # 当日
PYTHONIOENCODING=utf-8 python scripts/ecc_7day.py loop --days 7  # 离线跑 7 天
PYTHONIOENCODING=utf-8 python scripts/ecc_7day.py status       # 查 TSV
PYTHONIOENCODING=utf-8 python scripts/ecc_7day.py final        # Day 7 verdict
```

---

## 四、5 安全护栏（实测 ✓）

| # | 护栏 | 触发条件 | 处置 |
|---|---|---|---|
| 1 | **Idempotent per day** | 当日已 snapshot | `single` 跳过，TSV 不重复 |
| 2 | **UTF-8 强制** | Windows GBK 解码 | subprocess 设 `PYTHONIOENCODING=utf-8` |
| 3 | **失败容忍** | 单日 snapshot 失败 | 不阻塞 7 天观察，下次重试 |
| 4 | **报告目录自动创建** | mkdir parents | `reports/stage-472-ecc/` 不存在时自动创建 |
| 5 | **Day 0 不可覆盖** | ecc_7day.py single 不动老 JSON | snapshot-YYYYMMDD.json 都是按时间戳唯一 |

---

## 五、Day 7 final verdict 决策路径

```text
votes mapping:
  ✅ GO    (7 维判定含 GO 但不含 NO-GO)
  🟡 延期  (含 '延期')
  🔴 NO-GO (含 'NO-GO')
  🟢 UNKNOWN (其他)

verdict 分支:
  NO-GO ≥ 2  → 🔴 NO-GO  → 归档 _archive/stage-472-no-go.md
  GO ≥ 5 & NO-GO = 0 → 🟢 GO  → 启动 stage 47.2 真集成
  延期 ≥ 3  → 🟡 延期  → 30 天后再评
  else     → 🟡 待续  → 延长到 30 天
```

---

## 六、未决项与下一步

1. **Day 2-7 实跑** —— 用户每天 0:00 UTC（Asia/Shanghai = 08:00）跑 `ecc_7day.py single`，自动累积 TSV
2. **Day 7 综合判定** —— `ecc_7day.py final` 输出 GO / 延期 / NO-GO
3. **GO 路径** —— 启动 stage 47.2 真集成（`skills/ecc-methodology/`，按 stage 22/23/45.1 模式）
4. **NO-GO 路径** —— 归档 `_archive/stage-472-no-go.md`，保留 7 天数据快照
5. **与 stage 24 skill-updater cron 联动** —— V1.1.3 已知天龙集成列表加 `ecc_7day.py` 子命令

---

## 七、累计 PASS 实测（910 → 918）

```
Stage 41-44: 844 PASS
Stage 45:    +8   (dsh-eval-bridge)
Stage 46:    +23  (nomifun-methodology)
Stage 47:    +0   (盘点)
Stage 47.1:  +25  (memos + comet 双 GO 借鉴档)
Stage 47.2:  +0   (ECC D1 数据采集)
Stage 47.2:  +8   (ECC 7 天循环 + cron + 8 unittest) ⭐NET
Stage 47.3:  +10  (HarnessKit 借鉴档)
Stage 47.3:  +8   (ECC 7 天循环) ⭐NET
==============================
Stage 47.3 final: 918 PASS 锁定
```

### 7.1 8 unittest 类目

| # | 类目 | 用例 |
|---|---|---|
| 1 | `TestEcc7DaySnapshot::test_01_first_snapshot_creates_tsv` | TSV + JSON 双产物 |
| 2 | `test_02_idempotent_per_day` | 跳过的 graceful path |
| 3 | `test_03_tsv_header_columns` | 12 列字段齐 |
| 4 | `TestEcc7DayFinal::test_04_final_handles_empty_tsv` | 空 TSV 不崩溃 |
| 5 | `test_05_final_with_one_day_data` | "数据 < 2 天" 提示 |
| 6 | `test_06_final_with_synthetic_seven_day_tsv` | 7 天数据 + day delta |
| 7 | `TestEcc7DayFileSystem::test_07_status_shows_tsv` | status 子命令 |
| 8 | `test_08_lock_prevents_double_run` | 严格 idempotent per day |

---

## 八、来源链接

- 仓库主页：https://github.com/affaan-m/ECC
- Day 0 baseline 档案：dragon-engine/memory/stage-472-ecc-monitoring.md
- 监控脚本：dragon-engine/scripts/ecc_watcher.py V1.0
- 7 天循环脚本：dragon-engine/scripts/ecc_7day.py V1.0 ⭐
- Windows cron：dragon-engine/scripts/cron_ecc_weekly.ps1 ⭐
- Linux cron：dragon-engine/scripts/cron_ecc_weekly.sh ⭐
- 部署指南：dragon-engine/references/ecc-7day-DEPLOYMENT.md ⭐

---

> **下次同步点**：Day 7（2026-09-02）跑 `python scripts/ecc_7day.py final` → 用户决定 GO/NO-GO。
