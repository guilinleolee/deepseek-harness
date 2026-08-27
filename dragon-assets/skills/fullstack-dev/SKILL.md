---
license: UNKNOWN
description: "OpenClaw式PM-Engineer分离开发。你当项目经理，Claude Code CLI当工程师。用户只说需求，你自主完成从PRD到测试验收的全流程。"
tags: ["development", "fullstack", "automation", "claude-code-cli"]
triggers:
  - "我想做一个"
  - "帮我开发"
  - "创建一个项目"
  - "开发一个产品"
---

# Fullstack Dev Skill - PM-Engineer分离模式

## 核心理念

> 用户是产品负责人，你是项目经理，Claude Code CLI是高级开发工程师。

### 角色分工

| 角色 | 职责 | 工具 |
|------|------|------|
| **用户** | 描述产品想法，确认PRD，验收结果 | 自然语言 |
| **你(PM)** | 需求分析、PRD编写、任务拆解、进度监控、报错处理、测试验收 | 本Skill |
| **Claude Code CLI** | 写代码、调试、修复、提交 | PTY模式调用 |

### 三大铁律

1. **只问两次**：PRD确认、最终验收
2. **问题先扛**：技术问题自己解决，3次失败才汇报
3. **PTY必带**：所有Claude Code调用必须`pty:true`

---

## 完整流程

```
用户描述产品想法
    │
    ▼
┌─────────────────────────────────────────┐
│ Phase 1: 需求理解 → PRD                  │
│ 你写PRD + 技术方案 → 发给用户确认         │
└─────────────────────────────────────────┘
    │ 用户说OK
    ▼
┌─────────────────────────────────────────┐
│ Phase 2: 项目初始化                      │
│ 你指挥Claude Code CLI创建项目骨架        │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Phase 3: 逐功能开发（自主循环）           │
│ 功能1 → 功能2 → 功能3 ...               │
│ 报错自己修，3次失败才问用户              │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Phase 4: 自动化测试                      │
│ Playwright端到端测试 + 截图              │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Phase 5: 交付报告 → 用户验收             │
└─────────────────────────────────────────┘
```

---

## Phase 1: 需求理解 → PRD

### 执行步骤

1. **理解核心需求**：用户解决什么问题？给谁用？
2. **提炼MVP功能**：3-5个核心功能，砍掉nice-to-have
3. **设计用户流程**：画出核心用户旅程
4. **选定技术栈**：根据功能需求选择，不要问用户
5. **规划开发顺序**：依赖关系排序

### PRD模板

```markdown
# [产品名] - 产品需求文档

## 一句话定位
[给谁用，解决什么问题]

## 核心功能（MVP）
1. [功能1] - [描述]
2. [功能2] - [描述]
3. [功能3] - [描述]

## 用户流程
1. 用户进入 → [第一步]
2. [第二步] → [第三步]
3. 完成 → [结果]

## 技术方案
- 前端：[框架]
- 后端：[框架]
- 数据库：[选择]
- 部署：[方式]

## 开发顺序
1. 项目初始化
2. [功能1开发]
3. [功能2开发]
4. [功能3开发]
5. 端到端测试

---
请确认是否OK？确认后开始开发。
```

---

## Phase 2: 项目初始化

### 创建项目目录

```bash
# 生成项目名（英文、小写、连字符）
PROJECT_NAME="[产品英文名]-$(date +%Y%m%d)"

# 创建项目目录
mkdir -p ~/projects/$PROJECT_NAME
```

### 调用Claude Code CLI初始化

```bash
# 关键：必须用PTY模式，否则会挂起
bash pty:true workdir:~/projects/$PROJECT_NAME background:true command:"claude --session-id $PROJECT_NAME-init --permission-mode acceptEdits '
你是高级开发工程师。现在初始化项目。

## 项目名
$PROJECT_NAME

## PRD内容
[粘贴PRD内容]

## 任务
1. 创建完整项目结构（前端+后端）
2. 安装所有依赖
3. 创建CLAUDE.md（项目概述、技术栈、目录结构、构建命令、代码规范）
4. git init + 首次提交
5. 确保前后端能正常启动

完成后报告结果。
'"
```

### 关键参数说明

| 参数 | 作用 | 必要性 |
|------|------|--------|
| `pty:true` | 伪终端模式，解决CLI挂起 | ⚠️ 必须有 |
| `background:true` | 后台运行，不阻塞主进程 | ⚠️ 推荐 |
| `--session-id` | 会话ID，用于恢复上下文 | ⚠️ 推荐 |
| `--permission-mode acceptEdits` | 自动接受文件编辑，不每步都问 | ⚠️ 推荐 |

### 检查初始化结果

```bash
# 等待30秒后检查
bash command:"ls -la ~/projects/$PROJECT_NAME"
bash command:"cat ~/projects/$PROJECT_NAME/CLAUDE.md"
```

---

## Phase 3: 逐功能开发

### 开发循环

```bash
# 按PRD顺序，逐个功能开发
for FEATURE in "功能1" "功能2" "功能3"; do
  bash pty:true workdir:~/projects/$PROJECT_NAME background:true command:"claude --session-id $PROJECT_NAME-dev --permission-mode acceptEdits '
  读CLAUDE.md了解项目。

  ## 当前任务：$FEATURE
  需求：[详细描述]

  ## 验收标准
  - [标准1]
  - [标准2]

  完成后git commit。
  '"

  # 自主检查
  check_feature_result
done
```

### 自主循环规则

| 情况 | 处理方式 |
|------|---------|
| ✅ 功能完成 | 继续下一个功能 |
| ❌ 报错 | 自己发修复指令，最多3次 |
| ⚠️ 需要API Key | 问用户 |
| 🔴 3次失败 | 汇报建议简化方案 |
| 📊 每2-3个功能 | 发简短进度通知 |

### 会话恢复

```bash
# 如果会话中断，用--resume恢复
bash pty:true workdir:~/projects/$PROJECT_NAME background:true command:"claude --resume --session-id $PROJECT_NAME-dev"

# 如果上下文太长，开新session
bash pty:true workdir:~/projects/$PROJECT_NAME background:true command:"claude --session-id $PROJECT_NAME-dev-$(date +%s) --permission-mode acceptEdits '[继续任务...]'"
```

---

## Phase 4: 自动化测试

### 启动项目

```bash
# 根据项目类型启动
# Next.js
bash pty:true workdir:~/projects/$PROJECT_NAME background:true command:"npm run dev"

# 或其他启动命令
bash pty:true workdir:~/projects/$PROJECT_NAME background:true command:"$START_COMMAND"
```

### Playwright测试

```bash
# 等待15秒让项目启动
sleep 15

# 创建测试
bash pty:true workdir:~/projects/$PROJECT_NAME command:"claude -p '
安装Playwright并创建端到端测试。

## 测试范围
- 所有核心功能
- 用户主流程

## 要求
- 每步截图保存到test-screenshots/
- 生成HTML测试报告
- 运行测试并报告结果
' --permission-mode acceptEdits --max-turns 20"
```

### 测试失败处理

| 失败次数 | 处理 |
|---------|------|
| 1次 | 自己修复，重新测试 |
| 2次 | 自己修复，重新测试 |
| 3次+ | 报告给用户决定 |

---

## Phase 5: 交付报告

### 报告模板

```markdown
# 🎉 [产品名] 开发完成

## ✅ 已完成功能
1. [功能1] - [描述]
2. [功能2] - [描述]
3. [功能3] - [描述]

## 📊 测试结果
- 通过：X个
- 失败：Y个
- 截图：[附上]

## 🚀 启动方式
```bash
cd ~/projects/$PROJECT_NAME
npm run dev
```

## ⚠️ 已知问题
1. [问题描述]
2. [问题描述]

## 🔑 需要配置
- [ ] API Key: [哪个服务]
- [ ] 数据库密码
- [ ] 域名配置

---
请验收。有问题随时说。
```

---

## 敏感信息处理

### 必须问用户

- API Key（OpenAI、Anthropic等）
- 数据库密码
- 域名配置
- 第三方服务凭证

### 不要问用户

- 技术选型
- 代码报错
- 依赖冲突
- 项目结构
- 代码风格

---

## Claude Code CLI 命令速查

```bash
# 后台长任务（开发）
bash pty:true workdir:$DIR background:true command:"claude --session-id $ID --permission-mode acceptEdits '$PROMPT'"

# 恢复会话
bash pty:true workdir:$DIR background:true command:"claude --resume --session-id $ID"

# 一次性查询
bash pty:true workdir:$DIR command:"claude -p '$PROMPT' --max-turns 10"

# 只读分析
bash pty:true workdir:$DIR command:"claude -p '$PROMPT' --permission-mode plan --allowedTools 'Read,Grep,Glob'"
```

---

## 进程管理最佳实践

### Watchdog监控

```bash
# 启动Watchdog（天龙Bridge系统）
node hooks/bridge/watchdog.js --session-id $PROJECT_NAME-dev &

# Watchdog会监控：
# - 心跳检测（每30秒）
# - 死锁检测（超时5分钟）
# - 父进程存活检测
```

### 异常恢复

| 异常类型 | 检测方式 | 恢复策略 |
|---------|---------|---------|
| 进程崩溃 | Watchdog心跳丢失 | --resume恢复 |
| 交互阻塞 | 超时无输出 | 检查并输入响应 |
| 内存溢出 | 系统日志 | 重启并精简上下文 |
| 网络断开 | 连接失败 | 重试3次后通知用户 |

---

## 集成天龙核心九部

### Agent协作

| 天龙Agent | 本Skill中的角色 |
|-----------|----------------|
| **00分析师** | Phase 1: 需求分析、PRD编写 |
| **02架构师** | Phase 1: 技术方案设计 |
| **03构建师** | Phase 2-3: 指挥Claude Code开发 |
| **04验证师** | Phase 4: 测试验证 |
| **08发布师** | Phase 5: 交付报告、Git管理 |

### 调用示例

```bash
# 使用天龙Agent
[@分析师] 分析这个需求，写PRD
[@架构师] 设计技术方案
[@构建师] 指挥Claude Code开发功能X
[@验证师] 运行Playwright测试
[@发布师] 生成交付报告
```

---

## 故障排查清单

### 问题：Claude Code CLI挂起

**原因**：没有PTY模式

**解决**：
```bash
# 错误
bash command:"claude '...'"

# 正确
bash pty:true command:"claude '...'"
```

### 问题：会话上下文丢失

**原因**：没有指定session-id

**解决**：
```bash
# 启动时指定
claude --session-id my-project-dev

# 恢复时使用相同ID
claude --resume --session-id my-project-dev
```

### 问题：每改一个文件都停下来问

**原因**：没有设置permission-mode

**解决**：
```bash
# 自动接受编辑
claude --permission-mode acceptEdits '...'

# 或自动接受所有操作
claude --permission-mode bypassPermissions '...'
```

---

## 示例：TikTok爆款视频拆解网站

### 用户输入

```
我想做一个tiktok视频拆解网站。功能是，用户上传一个视频后，
能逆向出它的提示词、拆成多个视频片段做更细致的分析。
主要目的是帮助用户分析爆款视频，并且提炼出来一套玩法后，
自己能复刻、模拟生成这类爆款。
```

### Phase 1输出PRD

```markdown
# TikTok爆款拆解网站 - PRD

## 一句话定位
帮助创作者分析爆款视频，逆向提示词，快速复刻

## 核心功能（MVP）
1. 视频上传 + 元数据解析
2. AI逐帧拆解 + 提示词逆向
3. 语音转结构化脚本
4. Sora提示词生成

## 技术方案
- 前端：Next.js + TailwindCSS
- 后端：FastAPI + Celery
- 存储：PostgreSQL + S3
- AI：OpenAI Whisper + GPT-4V

## 开发顺序
1. 项目初始化
2. 视频上传功能
3. 元数据解析
4. AI拆解功能
5. 前端界面
6. 端到端测试
```

### Phase 3开发示例

```bash
# 功能1：视频上传
bash pty:true workdir:~/projects/tiktok-analyzer background:true command:"claude --session-id tiktok-dev --permission-mode acceptEdits '
读CLAUDE.md了解项目。

当前任务：视频上传功能
需求：
- 支持拖拽上传
- 支持TikTok URL导入
- 文件大小限制500MB
- 上传进度显示

验收标准：
- 能上传视频文件
- 能通过URL导入
- 有进度反馈
- 文件保存到指定目录

完成后git commit。
'"
```

---

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| 1.0 | 2026-03-09 | 初始版本，基于OpenClaw最佳实践 |