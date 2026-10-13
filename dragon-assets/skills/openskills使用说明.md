# OpenSkills 使用说明

## 简介

OpenSkills 是 AI 编码助手的通用技能加载器，用于管理和安装各种技能包（skills）。

## 核心命令

### 1. 查看帮助

```bash
openskills --help
openskills <command> --help
```

### 2. 列出已安装的技能

```bash
openskills list
```

显示所有已安装的全局和项目级技能。

### 3. 安装技能

```bash
# 从 GitHub 安装
openskills install <username/repo>

# 从 Git URL 安装
openskills install <git-url>
```

### 4. 同步技能索引 ⭐

```bash
openskills sync
```

**重要**：此命令会更新 `AGENTS.md` 文件，将已安装的技能索引写入其中。这是让 Claude Code 能够发现和使用技能的关键步骤。

- 交互式操作，会预先选中当前已安装的技能状态
- 建议在安装新技能后运行

### 5. 读取技能内容

```bash
openskills read <skill-name>
```

将技能内容输出到 stdout（供 AI 代理使用）。

### 6. 管理技能（交互式）

```bash
openskills manage
```

交互式管理（移除）已安装的技能。

### 7. 移除技能

```bash
# 脚本模式
openskills remove <skill-name>
openskills rm <skill-name>
```

移除指定技能（脚本使用，交互式请用 `manage`）。

## 常用工作流程

### 安装新技能

```bash
# 1. 安装技能
openskills install username/skill-repo

# 2. 同步索引（让 Claude 发现新技能）
openskills sync
```

### 查看所有可用技能

```bash
openskills list
```

## 技能存储位置

- **全局技能**：`~/.openskills/`
- **项目技能**：`<project>/.openskills/`

## 注意事项

1. 安装新技能后务必运行 `openskills sync` 生成索引
2. 技能需要在 `AGENTS.md` 中注册才能被 Claude Code 识别
3. 使用 `openskills manage` 可以安全地移除不需要的技能
