# Integration Guide · 天龙引擎集成到其它 AI 应用

> 把天龙引擎 (dragon-engine) 的资源挂载到 Claude Code / Cursor / Continue
> 等其它 AI 应用，让它们能直接复用天龙引擎的 skills / agents / commands /
> hooks。本指南覆盖三种集成方式：Junction（推荐）/ Copy / Mount，并说明每种
> 方式的优缺点与适用场景。

> **更新**: 2026-08-06 · **作者**: 天龙引擎 - 指挥官李依依

> 本次更新：5.3 节改为 Continue 1.x 正确 schema（customCommands + invokable frontmatter）

---

## 1. 三种集成方式对比

| 方式 | 同步性 | 磁盘占用 | 风险 | 推荐度 |
|------|--------|---------|------|--------|
| **Junction 软链** | 实时同步 | 0 | 低（不会动源） | ★★★★★ |
| **Copy 复制** | 需手动 | 双倍 | 高（两边可能不一致） | ★★ |
| **Mount 挂载** | 实时 | 0 | 高（依赖 OS） | ★ |

**Junction 是 NTFS 自带的目录硬链（不需要开发者模式）**——天龙引擎的
所有目标资源都是目录，完美匹配。本仓库默认推荐 Junction。

---

## 2. Junction 软链（Windows 推荐）

### 2.1 一键挂载

仓库根目录运行：

```bash
# 全部 4 类资源挂载到 ~/.claude/（Claude Code 主用）
make link-claude

# 挂载到 ~/.cursor/dragon-engine/（Cursor 浏览用）
make link-cursor

# 挂载到 ~/.continue/slash_commands/commands/（Continue 用）
make link-continue

# 查看挂载状态
make link-status

# 卸载（不影响源）
make unlink
```

Windows 上每个 make target 实际调用对应的 PowerShell 脚本（见 `scripts/`）。

### 2.2 行为细节

- **Junction 不需要 admin 或开发者模式**（mklink /J / PowerShell `New-Item -ItemType Junction`）
- **Junction 只对目录有效**，本仓库 4 类资源（skills/agents/commands/hooks）都是目录，完美匹配
- **删除 Junction 不影响源**（rm ~/.claude/skills 不会碰 dragon-engine/skills）
- **Junction 的路径是绝对路径**，移动 dragon-engine 后需要重新挂载
- **Claude Code 自动识别 Junction**——不需要重启，会在下次 session 生效

### 2.3 已存在同名目录怎么办？

`link-claude.ps1` 默认**拒绝覆盖**非 Junction 的目录。例如：

```
[WARN] C:\Users\li\.claude\skills exists but is NOT a junction/symlink.
       Back it up first, then run this script again.
```

**解决步骤**：
1. 备份：`mv ~/.claude/skills ~/.claude/skills.bak`
2. 重跑：`make link-claude`
3. 如需恢复原内容：`rm ~/.claude/skills && mv ~/.claude/skills.bak ~/.claude/skills`

### 2.4 Dry-run

加 `-DryRun` 看会做什么而不真改：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/link-claude.ps1 -DryRun
```

---

## 3. Copy 复制（备选）

直接复制资源到目标 AI 应用的目录：

```bash
# 把天龙引擎 4 类资源复制到 ~/.claude/
cp -r skills/    ~/.claude/
cp -r agents/    ~/.claude/
cp -r commands/  ~/.claude/
cp -r hooks/     ~/.claude/
```

**适用场景**：
- 跨机器分发（U盘 / Docker 镜像）
- 用户想要"独立副本"（例如修改后不被天龙引擎覆盖）

**缺点**：
- 两边不同步，dragon-engine 更新后需要重新 cp
- 占用双倍磁盘（~50 MB × N 应用）

---

## 4. Mount 挂载（Linux/macOS）

Linux / macOS 可以用 bind mount 或符号链接：

### 4.1 Linux bind mount

```bash
mkdir -p ~/.claude
mount --bind /path/to/dragon-engine/skills   ~/.claude/skills
mount --bind /path/to/dragon-engine/agents   ~/.claude/agents
mount --bind /path/to/dragon-engine/commands ~/.claude/commands
mount --bind /path/to/dragon-engine/hooks    ~/.claude/hooks
```

或者用 fstab 做持久挂载（参考 `/etc/fstab`）。

### 4.2 Linux / macOS symlink

```bash
mkdir -p ~/.claude
ln -s /path/to/dragon-engine/skills   ~/.claude/skills
ln -s /path/to/dragon-engine/agents   ~/.claude/agents
ln -s /path/to/dragon-engine/commands ~/.claude/commands
ln -s /path/to/dragon-engine/hooks    ~/.claude/hooks
```

**注意**：macOS 上 Claude Code 对符号链接的支持可能不一致，Junction 在 Windows / NTFS 上更稳。

---

## 5. 各应用差异

### 5.1 Claude Code

- **资源目录**: `~/.claude/{skills,agents,commands,hooks}/`
- **Junction 支持**: 完整
- **自动加载**: 是（下次 session 生效，无需重启）
- **配置**: `~/.claude/settings.json`（可选，配置 hooks 等）

### 5.2 Cursor

- **资源目录**: `~/.cursor/rules/`
- **规则文件**: `.cursorrules`（项目级）或 `~/.cursor/rules/`（全局）
- **Junction 支持**: 浏览 OK，但 Cursor 对 junction 下的 commands 加载可能不完整
- **用法**: 在项目 `.cursorrules` 写 `@~/.cursor/dragon-engine/CLAUDE.md` 引用天龙引擎提示
- **限制**: Cursor 的命令系统（Commands）与 Claude Code 不互通，需要单独适配

### 5.3 Continue（v1.x，2026-08 更新）

Continue 1.x 的 slash command 系统有 **两条路径**，天龙引擎**双管齐下**保证可用：

#### 5.3.1 路径 A：Junction + frontmatter 自动发现（推荐）

Continue 扫描 `~/.continue/slash_commands/*.md`（**仅顶层，不递归子目录**），读 frontmatter：

```yaml
---
name: 00调研师
description: 考古摸底：在开工前查清现有代码逻辑
invokable: true
---

# /00调研师 (Investigator)
此指令调用 **调研师** 代理…
```

三件套缺一不可：
- `name`（用作 `/<name>` 触发名）
- `description`（UI 提示）
- `invokable: true`（启用为 slash command）

**天龙引擎挂载方式**：

```powershell
# junction 把 commands/ 直接挂到 ~/.continue/slash_commands/ 顶层
# 注意：必须顶层，Continue 不扫子目录
New-Item -ItemType Junction `
  -Path "C:\Users\li\.continue\slash_commands" `
  -Target "C:\Users\li\.claude\projects\dragon-engine\commands"
```

#### 5.3.2 路径 B：config.json customCommands（fallback）

为防止某些 .md 的 frontmatter 损坏或被 Continue 忽略，在
`~/.continue/config.json` 显式注册所有 117 个命令：

```json
{
  "$schema": "https://continue.dev/config-schema/latest.json",
  "customCommands": [
    { "name": "00调研师", "description": "考古摸底：在开工前查清现有代码逻辑" },
    { "name": "01架构师", "description": "01架构师 (Architect)。划定蓝图…" }
  ]
}
```

生成命令：

```bash
python scripts/build-continue-config.py
# 默认输出到 ~/.continue/config.json，含 117 条 customCommands
```

#### 5.3.3 资源目录与限制

- **资源目录**: `~/.continue/{rules,slash_commands,config.json}`
- **Junction 位置**: `~/.continue/slash_commands/` **顶层**（不能是 `commands/` 子目录）
- **不扫子目录**: Continue 不递归，所以 commands/*.md 必须直接出现在顶层
- **INDEX.md 跳过**: 索引文档不当 slash command（脚本自动 skip）
- **frontmatter 修复**: `python scripts/fix-commands-frontmatter.py --apply`
  - 去除历史 `license: UNKNOWN` 污染（109 个文件）
  - 补 `name` / `invokable: true` 字段（117 个文件）

#### 5.3.4 当前注册的命令数

| 类别 | 数量 |
|---|---|
| commands/*.md 顶层总数 | 118 |
| 含 frontmatter 三件套 | 117 |
| 跳过（INDEX.md）| 1 |
| customCommands JSON 条数 | 117 |
| 触发方式 | `/<name>`（如 `/00调研师`、`/architect`）|

---

## 6. 多天龙引擎副本（高级）

如果用户在不同项目用不同版本的天龙引擎：

```bash
# ~/.claude/dragon-engine-v8/  → 老版本（项目 A）
# ~/.claude/dragon-engine-v9/  → 新版本（项目 B）

# 各自 junction 各自的 skills/
ln -s /path/to/v8/skills ~/.claude/dragon-engine-v8
ln -s /path/to/v9/skills ~/.claude/dragon-engine-v9
```

`docs/tools/catalog.md` 第 1 节也提到了 lib 路径的递归扫描，可作为补充。

---

## 7. 卸载 / 清理

```bash
# 删除所有 dragon-engine 软链（不影响源）
make unlink

# 等价 PowerShell
powershell -ExecutionPolicy Bypass -File scripts/unlink.ps1
```

`unlink.ps1` 仅删除由 `link-*.ps1` 创建的 Junction，**绝不**删除任何真实目录。

---

## 8. 故障排查

| 现象 | 可能原因 | 解决 |
|------|---------|------|
| `link-claude` 报 `[WARN] exists but NOT a junction` | `~/.claude/skills` 等已存在真实目录 | 备份后重跑 |
| Junction 创建后 Claude Code 不识别 | session 已启动未刷新 | 重启 Claude Code session |
| `make link-claude` 报权限错误 | 极少见（NTFS 通常不需要） | 用管理员 PowerShell 重跑 |
| 移动 dragon-engine 后 junction 失效 | Junction 是绝对路径 | 删掉旧 junction，重跑 `make link-claude` |

---

## 9. 相关脚本

| 脚本 | 用途 |
|------|------|
| `scripts/link-claude.ps1`   | junction 4 类资源到 `~/.claude/` |
| `scripts/link-cursor.ps1`   | junction dragon-engine 仓库到 `~/.cursor/dragon-engine/` |
| `scripts/link-continue.ps1` | junction commands/ 到 `~/.continue/slash_commands/commands/` |
| `scripts/link-status.ps1`   | 查看 4 个 AI 应用目录的 link 状态 |
| `scripts/unlink.ps1`        | 移除所有 dragon-engine junction |

对应 Make targets：`make link-{claude,cursor,continue,status}` / `make unlink`。

---

## 10. CI / 版本控制

Junction 不会被 git 跟踪（`.gitignore` 默认忽略）。CI 检查在
`.github/workflows/integration-check.yml`：

- 验证 `scripts/link-*.ps1` 语法
- 在 CI runner 上 dry-run 一次
- 检查 scripts/ 目录包含全部 5 个 .ps1 文件

---

*最后更新: 2026-08-06*