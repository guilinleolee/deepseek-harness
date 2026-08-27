---
name: dragon-engine-source-consolidation
description: 天龙引擎 4 路散落目录 → 单源 (workspace) 合并 · 2026-08-03 完成
metadata: 
  node_type: memory
  type: project
  originSessionId: b1effcb7-744c-4253-93b1-7392af6e8a64
  modified: 2026-08-03T15:25:02.672Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# 天龙引擎单源架构 · 2026-08-03

> **Why**: 原 4 路散落(`A` V8-restored git repo / `B` 空壳 dragon-engine / `C` D:\知识库\天龙引擎\workspace 真源 1072 skills / `D` ~/.claude/skills 18 项),Claude Code 调用机制不清晰,Codex 同步脚本还指向已空壳的 B 路径。
>
> **How to apply**: 一切天龙资产以 C 为真源,D 仅作个人增强;V8-restored (A) 留作历史归档不再写入;Codex 同步走 C。

## 单源架构(已生效)

| 角色 | 路径 | 状态 |
|---|---|---|
| **真源** | `D:\知识库\天龙引擎\workspace\skills\` | ✅ 写入一切 |
| **Claude Code 入口** | `D:\知识库\天龙引擎\workspace\.claude\skills\` | ✅ 16 个 junction 桥接到真源 |
| **Codex 同步目标** | `C:\Users\li\.codex\skills\lib-*` | ✅ 通过 sync 脚本每日同步 |
| **个人增强层**(不动) | `C:\Users\li\.claude\skills\` | ✅ 18 项 voxcpm/gpt-image-2 等 |

## 18 个核心 junction(workspace/.claude/skills/) · v1.2

```
anysearch · a-stock-data-bridge · apocdata-bridge · async-task-pattern
baoyu-xhs-images · blogger-fingerprint-registry · blogger-hologram-to-poster
cinema-director-laoli · generative-media-skills · guizang-social-card-skill
html-anything-bridge · huashu-design · khazix-writer · laoli-writer
multi-platform-publisher · nano-banana-brief · skill-updater
trading-agents-astock-wrapper
```

`blogger-hologram-to-poster` 用的是变体 `SKILL-cover-style-selector.md`,不是 bug。

## sync-dragon-to-codex.ps1 v1.2 修复

| 问题 | 修复 |
|---|---|
| 1. 源码指向已空壳 `dragon-engine/skills` | 改为 `workspace\.claude\skills` |
| 2. `Test-Path` 中文路径 PS5 解析失败 | 改 `[System.IO.Directory]::Exists` |
| 3. 脚本文件无 BOM,PS 当 GBK 读 UTF-8 中文 | 加 UTF-8 BOM(`EF BB BF`) |
| 4. 单引号防 PS 表达式替换中文 | `$source = 'D:\知识库\...'` |
| 5. Codex 缺 lib-<name> 目录时不会新建 | 新增"主动发现"段:遍历 workspace,缺则新建 lib-<name> |

脚本路径: `C:\Users\li\.claude\projects\sync-dragon-to-codex.ps1` · 跑法: `双击 sync-dragon-to-codex.bat` 或任务计划

## 合并结果(2026-08-03 v1.2 已完成)

### 从 A(V8-restored)合并到 C

| 类型 | A 独有 | 已复制到 C | 时间 |
|---|---|---|---|
| agents | 6 项(v104 finance × 3 + aihot/neat-freak/hv-analysis) | ✅ 全部 | 23:24 |
| skills | 2 项(apocdata-bridge + trading-agents-astock-wrapper) | ✅ 全部(44+46 项) | 23:24 |
| skills/.claude | 1 项(gitnexus,无 SKILL.md,跳过) | — | — |

### 从 B(dragon-engine 空壳)合并到 C

之前误判 B 为空壳(中文路径 bash 编码问题)。**B 不是空壳**,有 3 个 skill 真实内容。**但 C 已包含 B 全部内容**(0 缺口),无需复制。

### 最终覆盖核验

```
A skills/ 178 → C 178 (0 缺口) ✅
A agents/ 333 → C 333 (0 缺口) ✅
B skills/ 3   → C 3   (0 缺口) ✅
```

C 是唯一真源,可安全删除 A 和 B。

### junction 升级

workspace/.claude/skills 从 16 → **18 个**,新增:
- `apocdata-bridge`(27 阶段 Apache-2.0)
- `trading-agents-astock-wrapper`(25.2 阶段 Apache-2.0)

Codex 端 lib-* 同步 17/18 命中(blogger-hologram-to-poster 是 SKILL.md 变体)。

## 未解决(P1 - 用户自助)

以下删除操作因沙箱权限被拒,需用户在 PowerShell 手动执行:

```powershell
# V8-restored/settings.json 里的 API token 泄露(sk-cp-...)— 已撤销 + 本地脱敏
# 1. 线上撤销: minimaxi.com 控制台废弃该 token
# 2. 本地删除 ~/.claude/projects/dragon-engine-V8-restored/.git 重新 git init
Remove-Item "C:\Users\li\.claude\plugins\blocklist.json.e6df4aab78d03330.tmp" -Force
Remove-Item "C:\Users\li\.claude\摸鱼绿公众号封面.png" -Force
Remove-Item "C:\Users\li\.claude\skills\gpt-image-2-bridge" -Force   # 死链
```

## 团队分发下一步(候选)

- 把 `D:\知识库\天龙引擎\workspace\agents/`、`audit/`、`ip-profiles/_template/`、`workspace/00-INDEX.md` 一起发布到 GitHub
- 当前 16 junction 是生产子集,GitHub 仓应含完整 1072 + 9 audit 文档
- 见 [[apache-attribution-statements]] 给桥接 skill 加 NOTICE