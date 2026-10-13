---
name: skill-updater
description: >
全天龙引擎 GitHub 上游 skill 批量更新检查器 · 扫描 ~/.claude 下所有 SKILL.md,
根据 frontmatter 的 source / upstream 字段批量比对 GitHub 上游 commit / tag / release,
生成可读报告（推荐/跳过/失败三档）。**report-only：默认不改任何文件**。
Use when user says "更新天龙引擎", "更新 GitHub skill", "skill 升级",
"检查 skill 更新", "刷新技能", "refresh skills", "update skills",
"天龙引擎下所有 GitHub 下载的技能".
version: 1.0.0
author: 天龙引擎集成
license: MIT
last_updated: 2026-07-20
depends: []
upstream: []
downstream: - 22 个历史阶段的全部天龙 skill（被扫描对象）
- github-to-skills V1.1（姊妹：负责"创建"，本 skill 负责"更新"）
references: - references/contract.md — frontmatter 字段契约（解析规则）
- references/conventions.md — 天龙资产登记规范（V1.1.1 防"无 source"）
- design.md — 架构 + 数据契约 + License 红线 + 失败模式 + Roadmap
triggers: ["skill updater", "skill-updater · V1.0 天龙引擎集成版"]
---

# skill-updater · V1.0 天龙引擎集成版

> **核心理念**：本 skill 是天龙引擎的 **"体检器 + 雷达"**，**不写任何文件**。它扫描 `~/.claude` 下所有 `SKILL.md`，从 frontmatter 抽出 `source` / `upstream` 字段，对 GitHub 上游做 `git ls-remote` + REST API + README/release 抓取，输出一份"哪些 skill 落后了几个 commit / 哪个被原作者 archive 了 / 哪个 license 变了"的报告。
>
> 累计验证：**本地 dry-run 5/5 PASS**（扫描当前活跃路径 5 个 skill + 报告生成 0 fail）

## L0: 一句话描述 (≤15字)

**skill 上游报告器**

## L1: 使用场景 (50-100字)

当用户说"更新天龙引擎"、"更新所有 GitHub 下载的技能"、"refresh skills"、"check for skill updates"等任意变体时使用本 skill。**先检查天龙引擎下是否已存在对应 skill**（避免重复创建），然后扫描所有 SKILL.md，比对 GitHub 上游，输出**人类可读表格 + TSV 双格式报告**，**默认 report-only，不动文件**。

## L2: 详细文档

### 核心能力

| # | 能力 | 备注 |
|---|------|------|
| 1 | **全盘扫描** | 递归扫描 `~/.claude` 下所有 `SKILL.md`（可白名单/黑名单目录） |
| 2 | **frontmatter 解析** | 抽出 `name` / `version` / `last_updated` / `source` / `upstream` 5 个关键字段 |
| 3 | **GitHub 上游比对** | `git ls-remote` 拉 HEAD/tags + REST API 查 `license` / `archived` / 默认分支 + README/release 抓取 |
| 4 | **三档建议** | 🟢 跳过（无更新）/ 🟡 推荐更新（落后 N commits）/ 🔴 失败（仓库被删/改 license/network 故障） |
| 5 | **本地定制识别** | 无 `source` URL 的 skill → 标记 🟣 本地定制（不上游比对） |
| 6 | **双格式输出** | 终端表格（给人看）+ `.tsv`（给脚本用，自动留档） |
| 7 | **report-only 强约束** | 默认 `--dry-run`；任何写盘动作仅限 reports/ 子目录，**不动 skill 源文件** |

### 使用示例

```bash
# 1) 默认扫描（report-only + 终端表格 + reports/*.tsv）
bash scripts/scan.sh

# 2) 限制只扫天龙活跃路径（最快）
bash scripts/scan.sh --root "c:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine"

# 3) 多根目录扫描
bash scripts/scan.sh \
  --root "c:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine" \
  --root "c:/Users/li/.claude/projects/dragon-engine"

# 4) 仅输出某个上游的 skill 状态（如只看 guizang）
bash scripts/scan.sh --only guizang

# 5) 跳过网络（只看本地存在性 + frontmatter 解析）
bash scripts/scan.sh --no-network

# 6) 输出 JSON（替代 TSV）
bash scripts/scan.sh --format json
```

### 报告样例（终端表格）

```
=== skill-updater · 扫描报告 · 2026-07-20 14:23:01 ===
扫描根: ~/.claude
扫描到 SKILL.md: 5   上游比对: 5   本地定制: 0   失败: 0

| 状态 | skill 名                 | 本地 version | 上游 HEAD   | 落后 commits | 上游 license | 备注 |
|------|--------------------------|--------------|-------------|--------------|--------------|------|
| 🟢   | nano-banana-brief        | 1.0.0        | abc1234     | 0            | MIT          | 与上游同步 |
| 🟡   | cinema-director-laoli    | 1.0.0        | def5678     | 3            | MIT          | 落后 3 commits,推荐 review |
| 🟡   | guizang-social-card-skill| (未登记)     | 9a8b7c6     | ?            | AGPL-3.0 ⚠️  | license 已变,需人工评估 |
| 🟣   | blogger-hologram-to-poster| (本地定制)  | -           | -            | -            | 无 source URL,跳过上游比对 |
| 🔴   | (某 skill)               | 0.9.0        | 404         | -            | -            | 上游仓库已删或改名 |
```

### frontmatter 字段契约

| 字段 | 用途 | 必填? | 解析规则 |
|------|------|------|---------|
| `name` | skill 主键 | ✅ | kebab-case,直接用 |
| `version` | 本地版本号 | ✅ | 用于报告"本地版本列" |
| `last_updated` | 本地最后更新日 | ✅ | 用于判断"是否很久没动了"(默认 >180 天标 🔴) |
| `source` | 上游 GitHub URL 或本地路径 | ⭕ | 解析 URL → 提取 owner/repo;本地路径则标 🟣 |
| `upstream` | 借调的子模块清单(描述性) | ⭕ | 仅做完整性提示,**不**用来比对 |
| `license` | 本地登记的 license | ⭕ | 与上游 license 比对,**不一致 → 🔴** |

详见 [references/contract.md](references/contract.md) §字段抽取伪代码。

### 三档建议判定逻辑

```
🟢 跳过:   无 source URL            (本地定制)
         | 上游 HEAD == 本地 last_updated commit (完全同步)
         | 上游落后 < 1 commit       (微小变动,可忽略)

🟡 推荐:   上游落后 1-10 commits    (有更新但量不大)
         | 上游落后 >10 commits 但 < 90 天 (累积更新,值得 review)
         | 上游 license 一致 + 仅 patch 版本变动

🔴 失败:   上游仓库 404 / archived  (原作者已删/冻结)
         | 上游 license 变更         (如 MIT → AGPL,触发合规告警)
         | 本地 last_updated >180 天前 (长期未维护,即便上游有更新也建议人工 review)
         | 网络故障 / API 限流       (重试 3 次后仍失败)

🟣 本地:   无 source 字段           (天龙自研,无上游比对)
         | source 字段是本地路径     (本地引用,无需比对)
```

### 安全护栏 (强制)

1. **不动文件**: 除 `reports/` 子目录外,**绝不**改任何 SKILL.md 或 skill 文件
2. **网络只读**: 所有 `curl` / `git ls-remote` 走只读操作;**不 clone**、**不 fetch**、**不 pull**
3. **Token 透明**: 如设 `GITHUB_TOKEN` 环境变量,优先用(提高 rate limit);如无,fallback 到 anonymous(60 req/h)
4. **失败透明**: 任何上游请求失败必须在报告中显示,绝不静默跳过
5. **License 红线**: 上游 license 与本地不一致时,**红色 + ⚠️ 必读告警**

详见 [design.md §License 红线](design.md)。

### 协同矩阵

| 上下游 | 关系 |
|--------|------|
| ↔ github-to-skills V1.1 | 姊妹 skill:它负责"创建"(GitHub → skill),本 skill 负责"更新"(skill → GitHub) |
| ↔ skill-manager (如果存在) | skill-manager 负责生命周期 hook;本 skill 是其上游输入源 |
| ↓ 22 个天龙历史阶段 skill | 本 skill 的扫描对象 |

### 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| **V1.0** | **2026-07-20** | **首版:全盘扫描 + GitHub ls-remote/API/README 三层抓取 + 三档建议 + report-only** |
| **V1.1** | **2026-07-21** | **扩到 3 类资产（SKILL + agents + marketplaces）+ owner 推断** |
| **V1.1.1** | **2026-07-21** | **防"未来无 source"软约束:conventions.md + make_source.py + 报告缺 source 清单** |
| **V1.1.2** | **2026-07-21** | **autofill source 混合模式 + ⚠️ git URL credential 泄露检测 + 天龙仓库黑名单** |
| **V1.1.3** | **2026-07-21** | **--target-root 单根扫描 + INTEGRATED_SKILLS 集成版列表 + git 深度检测** |

### 注意事项

1. **Git Bash only**:`scan.sh` 用 bash 写就;Windows cmd.exe 跑不通
2. **Python 依赖**:`gh_fetch.py` + `parse_skill.py` 用纯标准库 (`urllib` + `re` + `json`);不需要 `requests` / `pyyaml` —— 最大限度降低集成成本
3. **首次运行慢**:默认会抓 5 个 skill 的 GitHub README,可能耗时 5-15 秒;可加 `--no-readme` 跳过
4. **reports/ 子目录**:每次运行会在 skill 同目录的 `reports/` 下生成 `report-YYYYMMDD-HHMMSS.tsv`,**不污染 skill 源目录**
5. **whitelist/blacklist**:见 [design.md §配置约定](design.md)