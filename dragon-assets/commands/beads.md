---
name: beads
description: beads - 天龙任务跟踪命令
invokable: true
---
# /beads - 天龙任务跟踪命令

分布式、基于Git的图形化任务跟踪器，专为AI Agent设计。

## 使用方式

```bash
/beads-init              # 初始化beads项目
/beads-status            # 查看任务状态
/beads-ready             # 列出可执行任务
/beads-create "任务标题"  # 创建新任务
/beads-claim <id>        # 认领任务
/beads-done <id>         # 完成任务
```

## 功能说明

### 1. 任务初始化

```bash
bd init              # 标准初始化
bd init --stealth    # 隐身模式（不在主仓库提交）
bd init --contributor # 贡献者模式（fork仓库）
```

### 2. 任务创建

```bash
bd create "实现用户认证" -p 0   # 创建P0优先级任务
bd create "编写测试" -p 1      # 创建P1优先级任务
```

### 3. 依赖管理

```bash
bd dep add bd-b2c3 bd-a1b2    # 添加依赖：b2c3依赖a1b2
bd dep remove bd-b2c3 bd-a1b2 # 移除依赖
```

### 4. 任务认领

```bash
bd update bd-a1b2 --claim     # 原子认领任务
bd update bd-a1b2 --done      # 标记完成
```

## 核心特性

| 特性 | 说明 |
|------|------|
| **Dolt数据库** | 版本控制SQL，支持分支和合并 |
| **Hash IDs** | bd-a1b2 格式，多Agent无冲突 |
| **依赖图** | 任务依赖关系可视化 |
| **记忆衰减** | 压缩旧任务，节省上下文 |
| **层级支持** | Epic → Task → Sub-task |

## 与TodoWrite协同

```
TodoWrite: 会话内任务跟踪（短期）
beads: 跨会话任务持久化（长期）

工作流:
1. 新任务先进入beads（持久化）
2. 当前会话任务同步到TodoWrite（执行）
3. 完成后更新beads状态
```

## 天龙岗位映射

| 岗位 | 用途 |
|------|------|
| 02架构师 | 任务依赖图设计 |
| 03构建师 | 原子任务认领 |
| 08发布师 | 任务状态跟踪 |
| 04验证师 | 阻塞任务识别 |

## 安装

```bash
# curl安装
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash

# npm安装
npm install -g @beads/bd

# Homebrew安装
brew install beads
```

## 示例工作流

```bash
# 1. 创建Epic
bd create "实现用户认证系统" -p 0

# 2. 创建子任务
bd create "设计认证架构" -p 1
bd create "实现登录API" -p 1

# 3. 添加依赖
bd dep add bd-b2c3 bd-a1b2  # 登录API依赖架构设计

# 4. 查看可执行任务
bd ready

# 5. 认领并执行
bd update bd-a1b2 --claim
# ... 执行任务 ...
bd update bd-a1b2 --done
```