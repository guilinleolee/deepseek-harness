# 同步天龙引擎上游资产 · Prompt 模板 V1.0

> **用法**：把下面【🎯 Prompt（直接复制 ↓）】整段粘到 Claude Code / Claude Desktop / CODEX 的新会话第一条 user message。
> **目的**：让 AI **自己**执行天龙引擎完整上游同步（skill-updater + agents/commands/hooks/plugins + LICENSE 监控 + 报告）。
> **配套**：
> - 战略层：[docs/upstream-sync-strategy.md](../docs/upstream-sync-strategy.md)
> - 软链接：[prompts/local-codex-symlink.md](local-codex-symlink.md) / [prompts/local-claude-symlink.md](local-claude-symlink.md)
> - 升级：[prompts/local-upgrade.md](local-upgrade.md)
> - 日常：[prompts/local-replicate.md](local-replicate.md)
>
> **前置**：本机已装 Python ≥ 3.10 + Node.js ≥ 18 + git + curl。

---

## 🎯 Prompt（直接复制 ↓）

```
你是天龙引擎上游同步工程师。我要你执行一次完整的上游同步：检查所有 GitHub 上游资产（755 skills + 174 agents + 82 hooks + 126 commands + 16 plugins + 30 memory）的版本差异、LICENSE 变化、仓库状态（active / archived），生成可读报告，并提示我哪些需要手动更新。

【路径常量】
  • 天龙引擎真主树根：C:\Users\li\.claude\projects\dragon-engine
  • 同步核心脚本：%DRAGON_ROOT%\skills\skill-updater\scripts\scan.sh
  • 同步 spec 脚本：%DRAGON_ROOT%\scripts\sync-dragon.py
  • 健康检查脚本：%DRAGON_ROOT%\scripts\skill-admin.py
  • 合规巡检脚本：%DRAGON_ROOT%\.claude\skills\neat-freak\scripts\conformance_cron.py
  • 工作环境：Windows 10 Pro + Git Bash + Python 3.10 + Node 18

【步骤 1 · 现状勘察】
  1.1 校验天龙基线：
      cat "C:\Users\li\.claude\projects\dragon-engine\VERSION"
      cat "C:\Users\li\.claude\projects\dragon-engine\STATUS.md" | head -10
  1.2 看上次同步时间：
      ls -lt "C:\Users\li\.claude\projects\dragon-engine\skills\skill-updater\reports" | head -5
  1.3 检查 GitHub 连通性：
      curl -sI https://api.github.com | head -3
  1.4 输出"基线报告"：当前版本 / 上次同步时间 / 网络状态

【步骤 2 · VERSION 同步（已有机制 · 跑通即可）】
  2.1 检查远程 VERSION：
      PYTHONIOENCODING=utf-8 python "C:\Users\li\.claude\projects\dragon-engine\scripts\sync-dragon.py" --check
  2.2 如有新版（remote > local），跑完整同步：
      PYTHONIOENCODING=utf-8 python "C:\Users\li\.claude\projects\dragon-engine\scripts\sync-dragon.py"
      期望：本地 VERSION 更新到远程 + 2 份 spec 下载到 output/sync-V{x_y}/ + 推到 Cursor/Claude/Codex
  2.3 输出 VERSION 同步报告：本地 vs 远程 + 是否升级

【步骤 3 · skill-updater 全盘扫描（核心 · SKILL.md 上游指纹）】
  3.1 跑 skill-updater 扫描天龙真主树（report-only · 默认安全）：
      PYTHONIOENCODING=utf-8 bash "C:\Users\li\.claude\projects\dragon-engine\skills\skill-updater\scripts\scan.sh" \
        --root "c:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine" \
        --format tsv
      期望：输出 reports/scan-YYYYMMDD-HHMMSS.tsv + 终端表格
  3.2 解析报告，按"上游指纹"分四档：
      • 🟢 跳过（无更新）：SKILL.md frontmatter 的 last_updated 与 GitHub commit 同
      • 🟡 推荐更新：本地落后 N commits（看 commits_behind 字段）
      • 🔴 失败：上游 archived / license 变了 / repo 迁移 / network fail
      • 🟣 本地定制：SKILL.md frontmatter 无 source 字段
  3.3 生成"🟡 推荐更新"清单（按 commits_behind 倒序）：
      head -30 "C:\Users\li\.claude\projects\dragon-engine\skills\skill-updater\reports\scan-"*.tsv \
        | awk -F'\t' '$2 == "🟡"' | sort -t$'\t' -k4 -n -r
  3.4 生成"🔴 失败"清单（最优先 · 可能 LICENSE 变更或 archive）：
      awk -F'\t' '$2 == "🔴"' "C:\Users\li\.claude\projects\dragon-engine\skills\skill-updater\reports\scan-"*.tsv
  3.5 输出"🟡 + 🔴 同步清单"，标记每个建议的更新策略：
      • 策略 A · rebase（保留天龙定制 + 同步上游 fix）：天龙对 skill 有 fork 改动时
      • 策略 B · mirror 重装（丢弃天龙定制）：纯上游使用场景
      • 策略 C · frontmatter only（轻量）：只追 SKILL.md frontmatter

【步骤 4 · agents/commands/hooks/plugins 上游指纹（缺口 · 手工）】
  ⚠️ skill-updater 只扫 SKILL.md。以下资产类型需要**手工验证上游**：

  4.1 agents/174 个 · 检查 frontmatter：
      grep -l "^source:" "C:\Users\li\.claude\projects\dragon-engine\agents\*.md" 2>/dev/null \
        | head -20
      期望：至少 nuwa-skill / cangjie-skill / darwin-skill 等应有 source 字段
      如有 frontmatter：抽 source URL → curl 比对最新 commit
      如无 frontmatter：标记为"🟣 本地定制"或"🟡 缺上游指纹"

  4.2 commands/126 个 · 扫 frontmatter：
      grep -l "^source:" "C:\Users\li\.claude\projects\dragon-engine\commands\*.md" 2>/dev/null \
        | head -20
      处理同 4.1

  4.3 hooks/82 个 · 扫 hooks.json：
      cat "C:\Users\li\.claude\projects\dragon-engine\hooks\hooks.json" \
        | python -c "import json,sys; cfg=json.load(sys.stdin); \
        print('Hooks with source:', [k for k,v in cfg.items() if 'source' in str(v)])"
      标记无 source 的 hook → 人工补 frontmatter

  4.4 plugins/16 个 · 扫 README.md：
      grep -l "^source:" "C:\Users\li\.claude\projects\dragon-engine\plugins"/*/README.md 2>/dev/null \
        | head -10
      处理同 4.1

  4.5 输出"4 类资产指纹覆盖率"表：
      • agents: 174 个 / 有 source 的 X 个 / 缺指纹的 Y 个
      • commands: 126 个 / 有 source 的 X 个 / 缺指纹的 Y 个
      • hooks: 82 个 / 有 source 的 X 个 / 缺指纹的 Y 个
      • plugins: 16 个 / 有 source 的 X 个 / 缺指纹的 Y 个

【步骤 5 · LICENSE 变更监控（最高风险 · 关键）】
  5.1 列出所有 skill 的 LICENSE 字段：
      PYTHONIOENCODING=utf-8 bash "C:\Users\li\.claude\projects\dragon-engine\skills\skill-updater\scripts\scan.sh" \
        --format tsv \
        2>/dev/null \
        | awk -F'\t' 'NR>1 {print $1"\t"$5}' \
        | sort -u
  5.2 比对每个 skill 的 local_license vs remote_license：
      • 同：无变更
      • 不同（特别是 MIT → AGPL）：立即标记 🔴，需人工 review
  5.3 列出 🔴 LICENSE 变更清单：
      awk -F'\t' '$5 != $6' "C:\Users\li\.claude\projects\dragon-engine\skills\skill-updater\reports\scan-"*.tsv
      期望：通常应为空（无变更）；如有命中 → 立即停，提示用户

【步骤 6 · 仓库状态监控（上游 archive / 改名）】
  6.1 从 skill-updater 报告抽所有 upstream URL：
      awk -F'\t' 'NR>1 {print $7}' "C:\Users\li\.claude\projects\dragon-engine\skills\skill-updater\reports\scan-"*.tsv \
        | sort -u | head -30
  6.2 用 GitHub API 检查每个仓库的 archived / default_branch：
      python - << 'PYEOF'
      import urllib.request, json
      repos = ["guilinleolee/dragon-engine", "alchaincyf/nuwa-skill", "kangarooking/cangjie-skill",
              "alchaincyf/darwin-skill", "simonlin1212/a-stock-data",
              "simonlin1212/global-stock-data", "simonlin1212/anysearch"]
      for r in repos:
          try:
              data = json.loads(urllib.request.urlopen(f"https://api.github.com/repos/{r}", timeout=10).read())
              flag = "🟢" if not data["archived"] else "🔴 ARCHIVED"
              print(f"{flag} {r} default_branch={data['default_branch']} stars={data['stargazers_count']}")
          except Exception as e:
              print(f"⚠️  {r} 查询失败: {e}")
      PYEOF
  6.3 列出 🔴 archived 仓库（如果命中 → 立刻通知用户）：
      上一步输出中找 🔴 行

【步骤 7 · 健康指标总览（每周看一次）】
  7.1 数据质量：
      PYTHONIOENCODING=utf-8 python "C:\Users\li\.claude\projects\dragon-engine\scripts\skill-admin.py"
      期望：A<800 / B<600 / C==0 / D==0 / E<100
  7.2 合规巡检：
      PYTHONIOENCODING=utf-8 python "C:\Users\li\.claude\projects\dragon-engine\.claude\skills\neat-freak\scripts\conformance_cron.py" 2>&1 | head -20
      期望：exit=0 PASS
  7.3 CJK 文件名：
      PYTHONIOENCODING=utf-8 python "C:\Users\li\.claude\projects\dragon-engine\scripts\check-cjk-filenames.py"
      期望：0 corrupted
  7.4 输出"5 大健康指标"汇总表

【步骤 7.5 · ⚡ 快速自动 apply 模式（新 · V1.1）】
  ⚠️ **本步骤只在你使用"自动 apply 模式部署"时跑**——即已部署 cron_daily.sh / deploy_daily.ps1 / GitHub Actions apply job。

  7.5.1 验证自动 apply 部署状态：
      - GitHub Actions: 查 https://github.com/guilinleolee/dragon-engine/actions/workflows/sync.yml
      - 本地 cron: `crontab -l | grep cron_daily.sh`
      - Windows Task: `Get-ScheduledTask -TaskName "skill-updater daily apply"`
  7.5.2 触发一次手动 apply（同步策略决策）：
      # GitHub Actions 手动触发
      # → workflow_dispatch → apply=true → max_behind=100

      # 或本地手动跑
      bash "C:\Users\li\.claude\projects\dragon-engine\skills\skill-updater\scripts\cron_daily.sh"
  7.5.3 跑完后：
      - 查 logs/cron-daily-*.log 看 PASS/FAIL
      - 查 logs/apply-*.log 看 APPLIED/SKIPPED/FAILED 数
      - 失败时已自动发邮件通知（需 SMTP 配置）
  7.5.4 完整部署文档：[skills/skill-updater/references/DEPLOYMENT.md](../skills/skill-updater/references/DEPLOYMENT.md)

【步骤 8 · 同步执行（按清单逐步更新）】
  ⚠️ **report-only 默认 · 实际更新需用户逐项确认**

  8.1 列出建议更新清单（按优先级）：
      🔴 紧急：
        • LICENSE 变更（如有）→ 立即 review + 决定保留/移除
        • 上游 archived → 决定 fork / 移除
      🟡 推荐（按 commits_behind 倒序）：
        • 落后 50+ commits → 优先策略 A rebase
        • 落后 10-50 commits → 策略 C frontmatter only
        • 落后 1-10 commits → 策略 C frontmatter only
      🟢 跳过：无更新

  8.2 用户确认后，按策略执行：
      # 策略 A · rebase
      cd "C:\Users\li\.claude\projects\dragon-engine\skills\<skill-name>"
      git remote add upstream https://github.com/<owner>/<repo>.git 2>/dev/null
      git fetch upstream
      git rebase upstream/main
      PYTHONIOENCODING=utf-8 bash tests/smoke.sh  # 必须 PASS

      # 策略 B · mirror 重装
      rm -rf "C:\Users\li\.claude\projects\dragon-engine\skills\<skill-name>"
      npx degit <owner>/<repo>/skills/<skill-name> "C:\Users\li\.claude\projects\dragon-engine\skills\<skill-name>"

      # 策略 C · frontmatter only
      curl -sL https://raw.githubusercontent.com/<owner>/<repo>/main/SKILL.md \
        > "C:\Users\li\.claude\projects\dragon-engine\skills\<skill-name>/SKILL.md"

  8.3 每更新一个 skill，必须跑 smoke test：
      PYTHONIOENCODING=utf-8 bash "C:\Users\li\.claude\projects\dragon-engine\skills\async-task-pattern\tests\smoke.sh"
      期望：20/20 PASS

  8.4 更新后重跑 skill-updater，确认状态从 🟡 → 🟢：
      PYTHONIOENCODING=utf-8 bash "C:\Users\li\.claude\projects\dragon-engine\skills\skill-updater\scripts\scan.sh" \
        --only <skill-name> --format tsv

【步骤 9 · 同步报告输出】
  跑完后输出：
  1. VERSION 同步：本地 V2.5 → 远程 V2.5（无需升级）/ 已升级到 V2.6
  2. skill-updater 扫描：755 个 SKILL.md / 🟢 N 个 / 🟡 M 个 / 🔴 K 个 / 🟣 P 个
  3. 4 类资产指纹覆盖率：agents/commands/hooks/plugins 各 X 个有 source / Y 个缺
  4. LICENSE 监控：🔴 紧急变更 0 个（健康）/ K 个（需 review）
  5. 仓库状态：🔴 archived 0 个（健康）/ K 个
  6. 健康指标：5 项全绿 / X 项黄 / Y 项红
  7. **下次同步建议**：用户下月应跑这个 prompt 一次；高频任务用 skill-updater cron
```

---

## 🔧 4 种策略对比

| 策略 | 适用场景 | 命令 | 风险 |
|------|---------|------|------|
| **策略 A · rebase** | 天龙对 skill 有 fork 改动 | `git fetch upstream + rebase` | 低（保留天龙定制） |
| **策略 B · mirror 重装** | 纯上游使用，无天龙定制 | `npx degit` | 中（丢本地 fix） |
| **策略 C · frontmatter only** | 只想升级 SKILL.md frontmatter | `curl + 重定向` | 低（轻量） |
| **策略 D · 全量重 git clone** | 大版本升级 / 上游 archive 迁移 | `rm -rf + git clone` | 高（重新评估） |

---

## ⚠️ 关键注意点

1. **skill-updater 默认 report-only** —— 扫到落后 ≠ 自动更新，必须人工 review + 跑步骤 8
2. **LICENSE 变更最高优先级** —— 步骤 5 是关键，MIT → AGPL 变更需立即处理
3. **agents/commands/hooks/plugins 缺口** —— skill-updater 不扫，需要步骤 4 手工验证
4. **每更新一个 skill 跑 smoke test** —— 步骤 8.3 不能省
5. **junction 真源在 D 盘** —— workspace 真源改了，GitHub master 不知道（详见 dragon-engine-source-consolidation.md）
6. **GitHub Token 可选** —— 有 GH_TOKEN / GITHUB_TOKEN 环境变量可避免 rate limit（匿名 60 req/h）
7. **同步后必须 git commit** —— `git add . && git commit -m "chore(sync): 同步 X 个 skill 上游"`

---

## 🛠 4 种调度方式（任选）

| 方式 | 命令 | 频率 | 适用 |
|------|------|------|------|
| **手动（一次性）** | 跑本 prompt 8 步 | 月度 | 完整 review |
| **Linux cron** | `0 9 * * 1 cd ~/... && bash scripts/scan.sh` | 每周一 9 点 | 自动化 |
| **Windows Task Scheduler** | 见 skill-updater/references/DEPLOYMENT.md | 每周日 03:00 | 自动化 |
| **GitHub Actions** | 已配 .github/workflows/sync.yml | 每天 02:00 UTC | CI 级（仅 VERSION + 2 spec） |

---

## ❓ FAQ

**Q：跑完这个 prompt 多久？**
A：步骤 1-7（勘察+报告）约 10 分钟；步骤 8（实际更新）取决于清单大小，每 skill 约 5 分钟。**月度全量同步预留 1-2 小时**。

**Q：能跳过步骤 2/3/4/5/6/7 直接跑步骤 8 吗？**
A：不能。1-7 是勘察，**不勘察直接更新会出大事**（特别是 LICENSE 变更和上游 archive）。

**Q：skill-updater 报告里 🔴 是什么意思？**
A：3 种情况：① 上游 archived（不能跟）② license 变了（合规风险）③ network fail（重试）。第 3 种最多见。

**Q：怎么知道某个 skill 是"天龙定制"还是"纯上游"？**
A：看 SKILL.md frontmatter 有无 `source` 字段。无 → 🟣 本地定制；有 → 上游可追。

**Q：rebase 冲突怎么办？**
A：天龙对上游的 fork 改动（SKILL.md frontmatter、LICENSE、README）通常是冲突点。手动保留天龙改动 + 上游 fix。

**Q：sync-dragon.py 与 skill-updater 区别？**
A：sync-dragon.py 同步 2 份 spec（BIBLE + cross-ai prompt）+ 推到 Cursor/Claude/Codex；skill-updater 扫描 755 SKILL.md 上游指纹。**两者互补，都跑**。

**Q：能完全自动化吗？**
A：P0 阶段不能（按 roadmap P4 季度才有 skill-updater V2 --apply）。现在必须人工 review。

**Q：什么时候该升级天龙整个版本？**
A：当本地 VERSION < 远程 VERSION 时跑 `local-upgrade.md`；当上游大版本 breaking change 时跑 `local-upgrade.md`。

---

🤖 Generated by [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
