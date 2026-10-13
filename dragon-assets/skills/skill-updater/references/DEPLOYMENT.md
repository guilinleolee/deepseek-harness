# skill-updater 部署文档 V2.0 · 自动 apply 模式

> **状态**：V1.1 增量 · 2026-08-06
> **变更**：从"周度报告"升级为"每日自动 apply（含 4 道 gate + 邮件 + 回滚）"
> **配套脚本**：`scan.sh` / `apply.py` / `notify_email.py` / `cron_daily.sh` / `deploy_daily.ps1`

## 一、3 种部署方式（任选 1-3，叠加冗余）

| 方式 | 脚本 | 频率 | 部署难度 | 适用 |
|------|------|------|---------|------|
| **GitHub Actions** | `.github/workflows/sync.yml` | 每天 02:00 + 09:00 UTC | ⭐ 零配置 | 主（云端）|
| **Linux/Mac cron** | `scripts/cron_daily.sh` | 每天 09:00 本地时间 | ⭐⭐ 简单 | 备用 |
| **Windows Task Scheduler** | `scripts/deploy_daily.ps1` + `deploy_daily.bat` | 每天 09:00 | ⭐⭐⭐ 中等 | 备用 |

> **推荐组合**：GitHub Actions 主 + 本地 cron 兜底（双保险）。

---

## 二、GitHub Actions 部署（推荐）

### 步骤 1：配置 SMTP Secrets（重要！）

1. 打开 GitHub 仓库 → Settings → Secrets and variables → Actions
2. 添加以下 secrets（邮箱配置）：

| Secret | 值（示例） | 说明 |
|--------|----------|------|
| `SMTP_HOST` | `smtp.gmail.com` | SMTP 服务器 |
| `SMTP_PORT` | `587` | SMTP 端口 |
| `SMTP_USER` | `your-bot@gmail.com` | 发件邮箱 |
| `SMTP_PASS` | `xxxx-xxxx-xxxx-xxxx` | 应用专用密码（不是登录密码）|
| `NOTIFY_FROM` | `your-bot@gmail.com` | 发件人（默认 = SMTP_USER）|
| `NOTIFY_TO` | `you@example.com` | 收件人（多个用 `,` 分隔）|

### 步骤 2：确认 workflow 已更新

✅ `.github/workflows/sync.yml` 已包含 `apply` job，含 4 道 gate + 邮件 + 自动 commit。
无需额外配置，push 到 master 后自动每天 02:00 + 09:00 UTC 跑。

### 步骤 3：手动触发（可选）

```bash
# 在 GitHub 网页操作：
# Actions → sync-dragon → Run workflow → 勾选 apply=true + max_behind=100
```

---

## 三、Linux/Mac Cron 部署

```bash
# 1. 编辑 crontab
crontab -e

# 2. 添加（每天 09:00 本地时间）
0 9 * * * cd /path/to/dragon-engine && bash skills/skill-updater/scripts/cron_daily.sh >> logs/cron-daily.log 2>&1

# 3. 配置 SMTP（写到 ~/.bashrc 或 cron 环境）
echo 'export SMTP_HOST=smtp.gmail.com' >> ~/.bashrc
echo 'export SMTP_PORT=587' >> ~/.bashrc
echo 'export SMTP_USER=your-bot@gmail.com' >> ~/.bashrc
echo 'export SMTP_PASS=xxxx-xxxx-xxxx-xxxx' >> ~/.bashrc
echo 'export NOTIFY_FROM=your-bot@gmail.com' >> ~/.bashrc
echo 'export NOTIFY_TO=you@example.com' >> ~/.bashrc
```

> ⚠️ cron 进程的 env 不继承 shell env，必须在 crontab 内 export 或用 `EnvironmentFile`。

---

## 四、Windows Task Scheduler 部署

### 步骤 1：准备脚本

- `scripts/cron_daily.sh`（Git Bash 跑）
- `scripts/deploy_daily.ps1`（PowerShell 封装）
- `scripts/deploy_daily.bat`（双击运行器）

### 步骤 2：手动测试

```cmd
:: 双击 deploy_daily.bat 测试
:: 或在 cmd 跑：
powershell -ExecutionPolicy Bypass -File "C:\Users\li\.claude\projects\dragon-engine\skills\skill-updater\scripts\deploy_daily.ps1"
```

### 步骤 3：创建任务计划

1. 打开"任务计划程序"（Task Scheduler）
2. 创建任务（不要"创建基本任务"）：
   - **常规**：
     - 名称：`skill-updater daily apply`
     - 用户：当前用户
     - "使用最高权限运行"：✅
   - **触发器**：
     - 新建 → 每天 → 09:00:00
   - **操作**：
     - 新建 → `powershell.exe`
     - 参数：`-ExecutionPolicy Bypass -File "C:\Users\li\.claude\projects\dragon-engine\skills\skill-updater\scripts\deploy_daily.ps1"`
   - **条件**：
     - "只有在计算机使用交流电源时才启动"：❌（笔记本场景）
     - "唤醒计算机运行此任务"：✅
3. 测试 → 右键任务 → "运行"

### 步骤 4：配置 SMTP 环境变量

```powershell
# 系统级别
[System.Environment]::SetEnvironmentVariable("SMTP_HOST", "smtp.gmail.com", "User")
[System.Environment]::SetEnvironmentVariable("SMTP_PORT", "587", "User")
[System.Environment]::SetEnvironmentVariable("SMTP_USER", "your-bot@gmail.com", "User")
[System.Environment]::SetEnvironmentVariable("SMTP_PASS", "xxxx-xxxx-xxxx-xxxx", "User")
[System.Environment]::SetEnvironmentVariable("NOTIFY_TO", "you@example.com", "User")

# 立即生效（重启任务计划程序）
```

---

## 五、4 道合规 Gate

apply.py 跑前会逐项检查：

| Gate | 检查 | 不通过时 |
|------|------|----------|
| **G1 LICENSE 不变** | `local_license == upstream_license` | 跳过 + 通知（合规最高风险）|
| **G2 仓库未 archive** | `upstream_archived == false` | 跳过（不能跟）|
| **G3 last_updated 合理** | 距今 < 500 天 | 跳过（长期未维护）|
| **G4 smoke test PASS** | `async-task-pattern/tests/smoke.sh` | **回滚 + 通知** |

---

## 六、6 种结果状态

| 状态 | 含义 | 后续动作 |
|------|------|----------|
| **APPLIED** | 4 道 gate 全过 + git rebase/merge 成功 + smoke PASS | ✅ 无需干预 |
| **SKIPPED（天龙自研）**| 在 `DRAGON_OWN_SKILLS` 白名单 | 无需干预 |
| **SKIPPED（非 git 仓库）**| 路径不是 git 仓库 | 永久跳过 |
| **SKIPPED（gate 失败）**| G1/G2/G3 任一失败 | 人工 review |
| **FAILED（rebase 失败）**| git rebase 冲突 | 通知 + 人工 merge |
| **FAILED（smoke 失败）**| G4 不通过，已自动 `git reset --hard HEAD` | 通知 + 人工 review |

---

## 七、监控与日志

```bash
# 1. 应用日志
ls -lt skills/skill-updater/logs/apply-*.log | head -10

# 2. 报告历史
ls -lt skills/skill-updater/reports/report-*.tsv | tail -5

# 3. 实时跟随（Linux）
tail -f skills/skill-updater/logs/apply-*.log

# 4. 复制 git 状态（如果 apply 后 git dirty）
cd skills/<name> && git status
```

---

## 八、回滚某次 apply

```bash
# 1. 找应用日志
ls -lt skills/skill-updater/logs/apply-*.log

# 2. 找 apply 过的 skill
grep "APPLIED" logs/apply-20260806-*.log

# 3. 手动回滚
cd skills/<skill-name>
git log --oneline -10  # 找 apply 前的 commit
git reset --hard <commit-hash>
```

---

## 九、常见问题

### Q1：SMTP 认证失败？
A：检查是否用了"应用专用密码"（Gmail 等要求），不是登录密码。

### Q2：apply 跑挂了怎么办？
A：检查 logs/apply-*.log 里 FAILED 的原因；G4 失败时已自动回滚，可直接重跑。

### Q3：GitHub Actions 看不到本地 progress？
A：本来如此。GitHub Actions 跑在云端 Ubuntu，无 access to `D:\知识库\`。本地 cron 是兜底。

### Q4：怎么验证自动 apply 真的生效？
A：在某个 yellow skill 提交一个 commit 到上游 → 第二天查 reports/ + skill 目录的 git log。

### Q5：能暂停 apply 跑只报告吗？
A：
- GitHub Actions：手动跑时 `apply=false`
- 本地 cron：临时 `mv cron_daily.sh cron_daily.sh.bak`

### Q6：天龙自研 skill 在白名单里吗？
A：是。`DRAGON_OWN_SKILLS` 包含 18 个天龙自研 skill + 永远是 SKIPPED。

---

## 十、版本演进

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-07-20 | 纯 report-only scan.sh |
| V1.1 | 2026-08-06 | + apply.py 实际 apply 模式 + 4 gate + 邮件 + 回滚 |
| V2.0 | 2026-08-06 | + cron_daily.sh + deploy_daily.ps1 + GitHub Actions apply job |

---

🤖 Generated by [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com)
