---
license: MIT
name: dragon-commander
version: 2.0.0
description: |
  天龙引擎指挥官 V2。当用户输入 `/command [需求]` 或 `@dragon-commander [任务]` 时，启动 DSH AgentTeams captain 协议：分析需求 → 推荐代理 → 启动 captain → 创建 team → 注册 member → 入队 task。本 V2 版本继承 V1 的 `/command` 入口（指挥官李依依），但内部从"prompt 编排"升级到"DSH AgentTeams 运行时"。
author: 天龙引擎团队
created: 2026-02-26
updated: 2026-08-13
category: documentation
runtime: dsh-agent-teams >= 0.1.13

triggers:
  - "用户提到「dragon-commander」时"
  - "/command [需求]"
  - "@dragon-commander [任务]"
---

# 🐉 天龙引擎指挥官 V2

> **版本说明**：
> - **V2（2026-08-13，当前）**：基于 DSH AgentTeams plugin 运行时。captain 即当前会话，team 状态落盘 `<workspace>/.agent-teams/`。
> - **V1（2026-02-26，legacy）**：纯 prompt 编排，指挥官李依依（一一）只做"代理推荐"，不实际调度。

---

## Usage

```
/command [您的需求描述]
```

或自然语言：

```
@dragon-commander 帮我实现用户登录功能
```

---

## V2 · Captain 启动流程（DSH AgentTeams plugin）

当收到 `/command [需求]` 时，dragon-commander 按以下顺序执行：

### Step 1：需求分析（V1 沿用）
```
1. 🧠 意图识别：用户真实目标
2. 🎯 复杂度判定：simple / medium / complex
3. 📊 置信度评分：0-1
4. 🚦 Gate 检查：意图清晰度 ≥ 0.7 才进入 Step 2
```

### Step 2：能力扫描（FETCH）
```
从能力注册表搜索相关技能：
  - 扫描 agents/*.md（163 个岗位）
  - 扫描 skills/*/SKILL.md（593 个技能）
  - 识别能力缺口（gap）
  - 输出 capabilityMap
```

### Step 3：启动 captain（DSH AgentTeams runtime bridge）
```typescript
// 1. 创建 team（captain = 当前会话）
agent_teams_create({
  name: `dragon-${Date.now()}`,  // 唯一命名
  description: 用户需求摘要,
})

// 2. 注册 member（capability-first 决策）
for (const skill of capabilityMap.requiredSkills) {
  const member = findOptimalAgent(skill)
  agent_teams_add_member({
    name: member.id,
    template: `agents/${member.file}`,
  })
}

// 3. 入队 task（DAG）
for (const task of dispatchBoard.tasks) {
  agent_teams_create_task({
    subject: task.subject,
    owner: task.owner,
    dependencies: task.dependencies,
  })
}
```

### Step 4：执行监控（mailbox）
- 不 poll task 状态
- 收 mailbox 消息：`task started` / `task done` / `task failed`
- 失败 → `agent_teams_reassign_task(assignee="captain")` 接管

### Step 5：综合输出
- 所有 task completed → captain 综合产出
- 输出归档路径：`<workspace>/.agent-teams/<team>/final-report.md`
- 用户可见活动面板：DSH Web UI activity panel

---

## V2 与 V1 的关键差异

| 维度 | V1（prompt 编排）| V2（DSH AgentTeams runtime）|
|---|---|---|
| 推荐代理 | 仅输出推荐名单 | **实际启动 captain** |
| 并行执行 | 串行模拟 | 真并行（多个 sub-agent）|
| 任务状态 | 不可见 | `<workspace>/.agent-teams/<team>/` 落盘 |
| 任务依赖 | prompt 描述 | 显式 `dependencies` DAG |
| 失败恢复 | 无 | `agent_teams_reassign_task` + cold recovery |
| 通信协议 | 文件 / JSON 模拟 | mailbox（持久化消息队列）|
| 可视化 | 文本报告 | DSH Web UI activity panel |

---

## V2 示例（DSH AgentTeams plugin 实跑）

### 示例 1：分析项目架构
```
/command 分析这个项目的架构

→ dragon-commander 启动 captain
→ 创建 team "dragon-arch-analysis"
→ 注册 2 个 member:
  - architect-member (template: agents/02-architect.md)
  - investigator-member (template: agents/01-investigator.md)
→ 入队 3 个 task:
  - T1: 模块依赖图 (owner: investigator)
  - T2: 架构决策记录 (owner: architect) [depends: T1]
  - T3: 综合架构报告 (owner: architect) [depends: T1, T2]
→ 等所有 task completed
→ 输出最终报告 + 活动面板链接
```

### 示例 2：实现用户登录
```
/command 帮我实现用户登录功能

→ captain 启动
→ 注册 5 个 member:
  - architect, builder-be, builder-fe, validator, security-reviewer
→ 入队 6 个 task:
  - T1: 架构设计 (architect)
  - T2: API 实现 (builder-be) [depends: T1]
  - T3: 前端实现 (builder-fe) [depends: T1]
  - T4: 测试用例 (validator) [depends: T2, T3]
  - T5: 安全审查 (security-reviewer) [depends: T4]
  - T6: 部署 (publisher) [depends: T5]
→ 综合报告 + 部署链接
```

### 示例 3：代码审查
```
/command 检查这段代码有没有问题

→ captain 启动
→ 注册 3 个 member:
  - code-reviewer, security-reviewer, validator
→ 入队 4 个 task:
  - T1: 代码风格审查 (code-reviewer)
  - T2: 安全审查 (security-reviewer) [与 T1 并行]
  - T3: 测试覆盖 (validator) [depends: T1, T2]
  - T4: 综合审查报告 (scribe) [depends: T3]
```

### 示例 4：编写 API 文档
```
/command 帮我写一份 API 文档

→ captain 启动
→ 注册 2 个 member:
  - investigator (查现有代码), scribe (写文档)
→ 入队 3 个 task:
  - T1: 提取 API 接口 (investigator)
  - T2: 起草文档 (scribe) [depends: T1]
  - T3: 校对 + 排版 (scribe) [depends: T2]
```

---

## Output（V2 实时输出格式）

```
╔══════════════════════════════════════════════════════════╗
║          🐉 天龙引擎指挥官 V2 (DSH AgentTeams)              ║
╠══════════════════════════════════════════════════════════╣
║  📋 需求分析                                                ║
║    ├─ 原始输入：分析这个项目的架构                          ║
║    ├─ 复杂度：complex                                        ║
║    ├─ 置信度：92%                                            ║
║    └─ Gate PASS：意图清晰                                   ║
║                                                           ║
║  🎯 Captain 启动                                           ║
║    ├─ Team: dragon-arch-analysis                            ║
║    ├─ Members: 2 (architect + investigator)                  ║
║    └─ Tasks: 3 (含 DAG)                                     ║
║                                                           ║
║  📊 实时进度 (Web UI 活动面板)                               ║
║    T1 模块依赖图     ✅ completed                            ║
║    T2 架构决策       🔵 in_progress (member: architect)    ║
║    T3 综合报告       ⏸ waiting (depends: T1, T2)           ║
║                                                           ║
║  📂 团队状态: <workspace>/.agent-teams/dragon-arch-analysis/║
╚══════════════════════════════════════════════════════════╝
```

---

## 关键约束

1. **workspace 路径含空格**：当前 workspace = `D:\deepseek haress`。V2 写入 `<workspace>/.agent-teams/`，必须 path-safe（首次验证）。
2. **member 数量上限**：`maxMembers: 8`（DSH plugin 默认）。复杂任务建议 ≤ 6 member。
3. **task 队列上限**：无显式限制，但建议 ≤ 20 task（DAG 复杂度可控）。
4. **captain 模型继承**：member 沿用 captain 模型。异构 LLM 路由需显式 `provider/model`。
5. **失败接管**：单 task 失败 → captain 自动接管（attempt_id 重置）；连续 3 次失败 → ESCALATE 升级。

---

## Related commands

- `/agents` - 查看所有可用代理
- `/status` - 查看系统状态
- `/agent-info <id>` - 查看代理详细信息
- `/agent-teams [任务]` - DSH AgentTeams plugin 直接入口

---

## 版本历史

| 版本 | 日期 | 协议 |
|---|---|---|
| V2.0.0 | 2026-08-13 | DSH AgentTeams plugin runtime |
| V1.0.0 | 2026-02-26 | Prompt 编排（仅推荐，不实际调度）|

---

## 参考资料

- **DSH AgentTeams 上游**：[NanmiCoder/dsh-agent-teams](https://github.com/NanmiCoder/dsh-agent-teams)
- **天龙集成报告**：`analysis/dsh-agent-teams-upgrade-analysis.md`
- **09-02 编排协调师 V9.09**：`agents/09-02-orchestrator.md`（V9.09 Runtime Bridge 详细协议）