# 天龙引擎上游同步策略 V1.0

> **问题**：天龙引擎 759 skills + 174 agents + 82 hooks + 126 commands + 16 plugins + 30 个 memory 主题文件，大量从 GitHub 上游（nuwa 29.6k⭐ / cangjie 6.2k⭐ / darwin 5.3k⭐ / a-stock-data 7.5k⭐ / global-stock-data 1.2k⭐ / anysearch 4.4k⭐ / xhs-visual-director 1k⭐ ...）下载而来。**上游一旦升级，本地如何跟上？**
>
> **结论**：天龙引擎已建 **3 层防护**（CI + 资产层 + 文件系统层），但 **agents/commands/hooks/plugins 暂无自动化指纹**，需在战术层补充 1 个同步 prompt 闭环。
>
> **更新日期**：2026-08-06 · 配套：[`prompts/local-sync-upstream.md`](../prompts/local-sync-upstream.md)

---

## 🛡 三层防护架构

```
┌──────────────────────────────────────────────────────────┐
│ L1 · CI / 应用层 · sync-dragon.py                        │
│   • 触发：GitHub Actions cron 每天 02:00 UTC            │
│   • 检测：远程 VERSION vs 本地 VERSION                    │
│   • 下载：BIBLE.md + cross-ai-replication-prompt.md       │
│   • 同步：Cursor ~/.cursor/rules/dragon-engine.mdc         │
│           Claude Code CLAUDE.md（注入块）                 │
│           Codex ~/.codex/prompts/dragon-engine.md         │
│   • 局限：只同步 2 份 spec，**不动 skills/agents/**       │
│   文档：scripts/sync-dragon.py + .github/workflows/sync.yml│
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ L2 · 资产层 · skill-updater V1.0                          │
│   • 触发：人工 bash scripts/scan.sh（每周一次）            │
│   • 扫描：递归所有 SKILL.md frontmatter 的 source/upstream│
│   • 比对：git ls-remote + REST API + README/release       │
│   • 报告：🟢 跳过 / 🟡 推荐更新 / 🔴 失败                │
│   • 强约束：**report-only 默认，不动源文件**               │
│   • 局限：**只扫 SKILL.md，不扫 agents/commands/hooks**    │
│   文档：skills/skill-updater/SKILL.md + design.md         │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ L3 · 文件系统层 · 18 junction + sync-dragon-to-codex.ps1  │
│   • 真源：D:\知识库\天龙引擎\workspace\skills\            │
│   • 桥接：workspace/.claude/skills/ → 18 个 junction     │
│   • 同步：每日 sync-dragon-to-codex.ps1 增量推 CODEX      │
│   • 局限：**真源在 D 盘，GitHub master 不是真源**         │
│   文档：memory/dragon-engine-source-consolidation.md      │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ ⚠️ 缺口层 · 需要补的                                     │
│   • agents/174 个 frontmatter 无 upstream 指纹             │
│   • commands/126 个 frontmatter 无 upstream 指纹           │
│   • hooks/82 个 frontmatter 无 upstream 指纹               │
│   • plugins/16 个 frontmatter 无 upstream 指纹             │
│   • mcp/ 缺统一 registry                                   │
│   • LICENSE 变更监控（MIT → AGPL 关键）                    │
│   → 用 [`prompts/local-sync-upstream.md`](../prompts/local-sync-upstream.md) │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 现状盘点 · 哪些资产有上游同步机制？

| 资产类型 | 数量 | 同步机制 | 指纹来源 | 缺口 |
|---------|------|---------|---------|------|
| **SKILL.md**（含 73 个 muapi 镜像） | 759 | skill-updater ⭐ | frontmatter `source`/`upstream` | ✅ 已覆盖 |
| **BIBLE.md + cross-ai prompt** | 2 | sync-dragon.py ⭐ | VERSION + 文件内容 | ✅ 已覆盖 |
| **agents** | 174 | ❌ 无 | （无 frontmatter 规范） | 🔴 缺 |
| **commands** | 126 | ❌ 无 | （无 frontmatter 规范） | 🔴 缺 |
| **hooks** | 82 | ❌ 无 | （无 frontmatter 规范） | 🔴 缺 |
| **plugins** | 16 | ❌ 无 | （无 frontmatter 规范） | 🔴 缺 |
| **memory 主题文件** | 49 | 人工 | （无） | 🟡 半 |
| **ip-profiles** | 3 | 人工 | （无） | 🟡 半 |
| **mcp 配置文件** | 1（mcp-list.md） | 人工 | （无） | 🟡 半 |
| **junction 桥接** | 18 | sync-dragon-to-codex.ps1 ⭐ | workspace/.claude/skills/ | ✅ 已覆盖 |

---

## 🚨 5 大具体缺口 + 风险

### 缺口 1 · agents/commands/hooks/plugins 无上游指纹

**风险**：nuwa-skill AGENT.md（29.6k⭐）改了格式、cangjie-skill HANDOFF.md（6.2k⭐）改了协议、darwin-skill PRODUCT.md（5.3k⭐）改了流程——**天龙本地 agents/ 不会有任何提示**。

**修复方案**：
- A. **短期**：用 [`prompts/local-sync-upstream.md`](../prompts/local-sync-upstream.md) 人工跑
- B. **中期**：扩展 skill-updater V1.1 支持 `.md` 文件 frontmatter 扫描（已存 roadmap）
- C. **长期**：把 agents/commands/hooks 也升级为"skill-like"结构（含 frontmatter）

### 缺口 2 · skill-updater 默认 report-only

**风险**：扫到 20 个落后 50+ commits 的 skill，但天龙不会自动更新。**报告 ≠ 修复**。

**修复方案**：
- A. **短期**：人工读 reports/ 报告 → 决定哪些需要追 → 手动 `git fetch + merge` 或重装
- B. **中期**：skill-updater V2 加 `--apply` 选项（需校验 LICENSE 不变 + 测试通过）

### 缺口 3 · sync-dragon.py 只同步 2 份 spec

**风险**：GitHub master 改了其它 skill / hook / 命令，**永远不会传到本地**。

**修复方案**：
- A. **短期**：升级流程由 `local-upgrade.md` prompt 驱动（已存在）
- B. **中期**：sync-dragon.py 加 `--mirror-skills` 模式，仅 mirror 完整上游 SKILL.md（不覆盖本地定制）

### 缺口 4 · LICENSE 变更无监控

**风险**：上游从 MIT 改 AGPL → 天龙本地使用触犯协议。**这是最高风险**。

**修复方案**：
- A. **短期**：skill-updater 报告已含 `archived` + `license` 字段（阶段 30 红线 10 项）
- B. **中期**：加 LICENSE delta 报警（commit message 含 "license" → 立即 review）

### 缺口 5 · 上游"重大变更"无通知

**风险**：上游 main branch 改名 / 仓库迁移 / archive → skill-updater 静默失败。

**修复方案**：
- A. **短期**：skill-updater 已能检测 archive（🔴 标记）
- B. **中期**：加 GitHub Watch API 订阅 41 个上游仓库 → release / archive 通知

---

## 🎯 用户场景对应的同步动作

### 场景 1 · "我想知道天龙引擎哪些 skill 落后了"

```bash
# 用 skill-updater 一键扫描
bash ~/projects/c--Users-li--claude/dragon-engine/skills/skill-updater/scripts/scan.sh \
  --root "c:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine"

# 输出：reports/scan-YYYYMMDD-HHMMSS.tsv + 终端表格
# 期望：🟢 多数 / 🟡 少量落后 / 🔴 几个失败（archived 或 network）
```

### 场景 2 · "我看到 5 个 skill 落后了，怎么更新？"

```bash
# 1. 读 reports/*.tsv 找落后 skill
# 2. 逐个手动更新（天龙自研的不动；上游的有 3 种策略）
cat reports/scan-*.tsv | awk -F'\t' '$2 == "🟡"'  # 推荐更新

# 3. 策略 A：rebase 上游（保留天龙定制 + 同步上游 fix）
cd skills/<skill-name>
git remote add upstream https://github.com/<owner>/<repo>.git  # 已有就跳过
git fetch upstream
git rebase upstream/main  # 或 merge

# 4. 策略 B：mirror 重装（丢弃天龙定制）
rm -rf skills/<skill-name>
npx degit <owner>/<repo>/skills/<skill-name> skills/<skill-name>

# 5. 策略 C：只升级 SKILL.md frontmatter（轻量）
curl -sL https://raw.githubusercontent.com/<owner>/<repo>/main/SKILL.md > skills/<skill-name>/SKILL.md
```

### 场景 3 · "天龙引擎新版本发布了，我想跟"

```bash
# 用 sync-dragon.py 检测
PYTHONIOENCODING=utf-8 python scripts/sync-dragon.py --check
# 输出：本地 V2.5 vs 远程 V2.6 → 升级

# 完整同步（下载 2 份 spec + 推到 Cursor/Claude/Codex）
PYTHONIOENCODING=utf-8 python scripts/sync-dragon.py
```

### 场景 4 · "我想定期自动巡检，不漏掉任何上游更新"

```bash
# 三种部署方式（任选其一）：

# 方式 A · Linux cron（每早 9 点）
0 9 * * * cd ~/projects/c--Users-li--claude/dragon-engine && \
  bash skills/skill-updater/scripts/scan.sh >> logs/scan.log 2>&1

# 方式 B · Windows Task Scheduler（每周日 03:00）
# 见 skills/skill-updater/references/DEPLOYMENT.md

# 方式 C · GitHub Actions（仓库级别）
# 已配 .github/workflows/sync.yml · 每天 02:00 UTC
```

### 场景 5 · "我想把所有上游资产 + agents + commands + hooks + plugins 都同步"

→ 用 [`prompts/local-sync-upstream.md`](../prompts/local-sync-upstream.md) —— 这是补"缺口 1 + 缺口 4"的完整战术 prompt。

---

## ⚙️ 4 种上游同步策略对比

| 策略 | 适用 | 风险 | 频率 |
|------|------|------|------|
| **rebase** | 自研 skill + 上游 fix | 低（保留天龙定制） | 月度 |
| **mirror 重装** | 纯上游 skill（无定制） | 中（丢本地 fix） | 季度 |
| **frontmatter only** | 仅追 SKILL.md frontmatter | 低（轻量） | 周度 |
| **全量重 git clone** | 大版本升级 / 上游 archive 后迁移 | 高（重新评估） | 年度 |

---

## 📈 健康指标（每周看一次）

```bash
# 1. 数据质量（skill-admin）
python scripts/skill-admin.py
# 期望：A<800 / B<600 / C==0 / D==0 / E<100

# 2. 上游同步延迟（skill-updater）
bash skills/skill-updater/scripts/scan.sh --no-network | grep -c "🟡"
# 期望：< 20 个推荐更新

# 3. LICENSE 合规（conformance）
python .claude/skills/neat-freak/scripts/conformance_cron.py
# 期望：exit=0 PASS（5 项校验 4 PASS + 1 预期 WARN）

# 4. 版本对齐（sync-dragon）
python scripts/sync-dragon.py --check
# 期望：本地 VERSION >= 远程 VERSION

# 5. CJK 文件名（防止 GBK 误读）
python scripts/check-cjk-filenames.py
# 期望：0 corrupted
```

---

## 🛠 路线图（按优先级）

| 阶段 | 内容 | 预计 | 状态 |
|------|------|------|------|
| **P0 已完成** | L1 sync-dragon.py + sync.yml | — | ✅ |
| **P0 已完成** | L2 skill-updater V1.0 | — | ✅ |
| **P0 已完成** | L3 18 junction + sync-dragon-to-codex.ps1 | — | ✅ |
| **P1 立即可做** | 写 `prompts/local-sync-upstream.md` | 半天 | ✅ |
| **P2 1 周内** | skill-updater V1.1 支持 .md frontmatter | 2 天 | 🔴 TODO |
| **P2 1 周内** | agents/commands/hooks 加 frontmatter 规范 | 3 天 | 🔴 TODO |
| **P3 1 月内** | sync-dragon.py 加 `--mirror-skills` | 1 周 | 🔴 TODO |
| **P3 1 月内** | LICENSE delta 报警（GitHub Watch API） | 1 周 | 🔴 TODO |
| **P4 季度** | skill-updater V2 加 `--apply`（自动更新） | 1 月 | 🔴 TODO |
| **P4 季度** | 上游 41 仓库 GitHub Watch 订阅 | 半天 | 🔴 TODO |

---

## 📚 相关文档

| 文档 | 用途 |
|------|------|
| [prompts/local-sync-upstream.md](../prompts/local-sync-upstream.md) | ⭐ **完整同步上游资产的 prompt 模板（补缺口 1+4）** |
| [prompts/local-upgrade.md](../prompts/local-upgrade.md) | 升级天龙时同步 |
| [prompts/local-replicate.md](../prompts/local-replicate.md) | 日常任务 |
| [prompts/local-codex-symlink.md](../prompts/local-codex-symlink.md) | CODEX 软链接配置 |
| [prompts/local-claude-symlink.md](../prompts/local-claude-symlink.md) | Claude Desktop 软链接配置 |
| [skills/skill-updater/SKILL.md](../skills/skill-updater/SKILL.md) | 上游同步 skill 详细文档 |
| [scripts/sync-dragon.py](../scripts/sync-dragon.py) | VERSION + 2 spec 同步脚本 |
| [memory/dragon-engine-source-consolidation.md](../memory/dragon-engine-source-consolidation.md) | 4 路散落目录 → 单源架构 |

---

🤖 Generated by [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
