---
name: obsidian-cli
version: 1.0.0
description: |
  通过 notesmd-cli 操作 Obsidian vault - 创建/搜索/管理笔记，支持无头模式和脚本自动化。
author: 天龙引擎团队
created: 2026-08-16
category: knowledge-management
license: MIT

triggers:
  - "obsidian-cli"
  - "obsidian vault"
  - "笔记管理"
  - "知识库操作"
---

# Obsidian CLI Skill

## L0: 一句话描述 (≤15字)
终端操作 Obsidian 笔记库

## L1: 使用场景 (50-100字)

**适用场景**：
- 自动化笔记创建与归档（每日复盘、会议记录）
- 跨终端搜索 Obsidian vault 内容
- 无 GUI 环境下管理笔记（服务器/CI）
- 与其他天龙技能协同（知识沉淀、日记写作）

**触发关键词**：`/obsidian`、`obsidian笔记`、`创建obsidian笔记`、`搜索obsidian`

## L2: 详细文档

### 安装前置条件

**安装 notesmd-cli**：

```bash
# Windows (需要 Scoop)
scoop bucket add scoop-yakitrak https://github.com/yakitrak/scoop-yakitrak.git
scoop install notesmd-cli

# Mac/Linux (需要 Homebrew)
brew tap yakitrak/yakitrak
brew install yakitrak/yakitrak/notesmd-cli

# 验证安装
notesmd-cli --version
```

**配置 Vault**：

```bash
# 注册 vault
notesmd-cli add-vault /path/to/your-vault --set-default

# 或自动检测（Obsidian 已安装时）
# 打开 vault 后会自动注册
```

---

### 核心命令速查

| 操作 | 命令 | 别名 |
|------|------|------|
| 列出所有 vault | `notesmd-cli list-vaults` | `lv` |
| 搜索文件名 | `notesmd-cli search` | - |
| 搜索内容 | `notesmd-cli search-content "关键词"` | - |
| 打印笔记内容 | `notesmd-cli print "笔记名.md"` | - |
| 创建笔记 | `notesmd-cli create "笔记名.md" --content "内容"` | - |
| 打开笔记 | `notesmd-cli open "笔记名.md"` | - |
| 今日日记 | `notesmd-cli daily --content "内容"` | - |
| 重命名笔记 | `notesmd-cli move "旧名.md" "新名.md"` | - |
| 删除笔记 | `notesmd-cli delete "笔记名.md"` | - |
| 管理 frontmatter | `notesmd-cli frontmatter "笔记.md" --print` | `fm` |

---

### 使用示例

#### 1. 搜索笔记

```bash
# 模糊搜索文件名
notesmd-cli search "项目"

# 搜索笔记内容（JSON 格式输出，用于脚本）
notesmd-cli search-content "待办" --format json --page 1 --page-size 50

# 非交互式搜索
notesmd-cli search-content "关键词" --no-interactive
```

#### 2. 创建笔记

```bash
# 创建空白笔记
notesmd-cli create "新笔记.md"

# 创建带内容的笔记
notesmd-cli create "会议记录.md" --content "# 会议记录

## 日期
2026-08-16

## 要点
- 待办事项1
- 待办事项2

## 行动项
- [ ] 任务1
- [ ] 任务2
"

# 追加内容到现有笔记
notesmd-cli create "日记.md" --content "今日完成：xxx" --append

# 覆盖现有笔记
notesmd-cli create "旧笔记.md" --content "新内容" --overwrite
```

#### 3. 每日日记

```bash
# 打开/创建今日日记
notesmd-cli daily

# 带内容创建
notesmd-cli daily --content "## 今日总结

### 完成
- [x] 任务A
- [x] 任务B

### 待办
- [ ] 任务C
"

# 在编辑器中打开
notesmd-cli daily --editor
```

#### 4. 管理 Frontmatter

```bash
# 查看 frontmatter
notesmd-cli frontmatter "笔记.md" --print

# 添加/修改字段
notesmd-cli frontmatter "笔记.md" --edit --key "tags" --value "[project, important]"
notesmd-cli frontmatter "笔记.md" --edit --key "status" --value "done"

# 删除字段
notesmd-cli frontmatter "笔记.md" --delete --key "draft"
```

#### 5. 笔记操作

```bash
# 在 Obsidian 中打开
notesmd-cli open "笔记.md"

# 在编辑器中打开
notesmd-cli open "笔记.md" --editor

# 重命名（自动更新库内链接）
notesmd-cli move "旧名.md" "新名.md"

# 删除
notesmd-cli delete "无用笔记.md"
```

#### 6. 脚本集成

```bash
# 获取默认 vault 路径
VAULT_PATH=$(notesmd-cli list-vaults --default --path-only)

# 批量创建笔记
for note in "笔记1" "笔记2" "笔记3"; do
  notesmd-cli create "${note}.md" --content "# ${note}"
done

# JSON 输出用于管道处理
notesmd-cli search-content "待办" --format json | jq '.[] | .name'
```

---

### 与其他技能协同

| 协同技能 | 协同方式 |
|---------|---------|
| `obsidian-markdown` | 先用 obsidian-markdown 格式化内容，再用 obsidian-cli 创建笔记 |
| `kepano-obsidian` | 参考 kepano 的模板设计，创建结构化笔记 |
| `06记录师` | 自动生成笔记内容并归档到 Obsidian |
| `daily-briefing` | 将每日简报自动写入日记 |

---

### 配置选项

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `OBSIDIAN_VAULT` | - | 指定默认 vault（覆盖配置） |
| `EDITOR` | `vim` | 默认编辑器（可用 `code`, `nano` 等） |

---

### 注意事项

- ⚠️ **vault 必须先注册**：`add-vault` 后才能操作
- ⚠️ **文件名包含路径时**：使用相对于 vault 根目录的路径
- ⚠️ **链接更新**：`move` 命令会更新库内所有引用
- ⚠️ **Excluded Files**：`search` 和 `search-content` 尊重 Obsidian 的排除设置
- 💡 **无 GUI 环境**：使用 `--editor` 标志，无需 Obsidian 应用

---

### 故障排除

| 问题 | 解决方案 |
|------|---------|
| `command not found` | 确认 notesmd-cli 已安装并加入 PATH |
| `vault not found` | 运行 `notesmd-cli add-vault <path> --set-default` |
| 中文文件名乱码 | 使用英文文件名或 URL 编码路径 |
| 搜索结果为空 | 检查 `.obsidian/app.json` 的 `newFileLocation` 配置 |

---

### 相关技能

- `obsidian-markdown` - Obsidian 格式 Markdown 语法参考
- `kepano-obsidian` - kepano 的 Vault 模板和最佳实践
- `obsidian-bases` - Vault 基础结构设计

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-08-16 | 初始创建，封装 notesmd-cli 核心功能 |
