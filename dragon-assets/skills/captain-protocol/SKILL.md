---
license: MIT
name: captain-protocol
version: 1.0.0
description: |
  天龙 captain 五件套天龙模板。把 DSH AgentTeams plugin 的 10 个工具封装成 5 个天龙自然语言入口：captain-start / add-members / create-tasks / wait-and-collect / finalize-report。让天龙任何岗位用自然语言触发 AgentTeams，不必手写工具调用。
author: 天龙引擎团队
created: 2026-08-13
updated: 2026-08-13
runtime: dsh-agent-teams >= 0.1.13
references:
  runtime_target: NanmiCoder/dsh-agent-teams
  related_skill: agent-teams-playbook (天龙专属入门)

triggers:
  - "captain protocol"
  - "captain 协议"
  - "天龙 captain 五件套"
---

# Captain Protocol · 天龙 captain 五件套

> **TL;DR**：本 skill 不引入新协议，**封装** DSH AgentTeams 10 个工具为 5 个天龙自然语言入口。

## 与 DSH AgentTeams 工具的映射

| 天龙入口 | DSH AgentTeams 工具 | 用途 |
|---|---|---|
| `captain-start` | `agent_teams_create` | 创建 team |
| `add-members` | `agent_teams_add_member` | 注册 N 个 member |
| `create-tasks` | `agent_teams_create_task` | 入队 N 个 task（含 dependency）|
| `wait-and-collect` | `agent_teams_status` + mailbox 监听 | 等所有 task completed |
| `finalize-report` | `agent_teams_delete`（归档）| 综合产出 + 清理 team |

## 5 个入口的伪代码

### 1. `captain-start <team-name> "<description>"`

```typescript
// 自然语言 → 工具调用
agent_teams_create({
  name: '<team-name>',
  description: '<description>',
})
```

### 2. `add-members <member-list>`

```typescript
// 自然语言 "添加分析师、调研师、构建师 3 个 member"
// 解析为：
const members = [
  { name: 'analyst', template: 'agents/00-analyst.md' },
  { name: 'investigator', template: 'agents/01-investigator.md' },
  { name: 'builder', template: 'agents/03-builder.md' },
]
for (const m of members) {
  agent_teams_add_member(m)
}
```

### 3. `create-tasks <task-spec>`

```typescript
// 自然语言 "T1 调研由 investigator，T2 实现由 builder 依赖 T1，T3 测试由 validator 依赖 T2"
// 解析为：
const tasks = [
  { subject: 'T1 调研', owner: 'investigator', dependencies: [] },
  { subject: 'T2 实现', owner: 'builder', dependencies: ['T1'] },
  { subject: 'T3 测试', owner: 'validator', dependencies: ['T2'] },
]
for (const t of tasks) {
  agent_teams_create_task(t)
}
```

### 4. `wait-and-collect [timeout=300s]`

```typescript
// 默认等所有 task 进入 completed 状态
// 每 10s 调用一次 agent_teams_status
const start = Date.now()
while (Date.now() - start < timeout * 1000) {
  const status = agent_teams_status({ team: '...' })
  const allDone = status.tasks.every(t =>
    t.status === 'completed' || t.status === 'failed'
  )
  if (allDone) break
  await sleep(10_000)
}
return status
```

### 5. `finalize-report <output-path>`

```typescript
// 综合产出
const status = agent_teams_status({ team: '...' })
const report = synthesizeOutputs(status.tasks.map(t => t.output))
writeFileSync(`<output-path>`, report)
// 归档 team
agent_teams_delete({ team: '...' })
```

## 使用示例

### 示例 1：3 个研究员 + 1 个记录员的 research DAG

```
[@captain-protocol] captain-start "competitor-research" "调研 3 个 AI CLI 竞品"
[@captain-protocol] add-members "investigator-a, investigator-b, investigator-c, scribe"
[@captain-protocol] create-tasks "T1:Cursor@investigator-a | T2:Claude Code@investigator-b | T3:Codex CLI@investigator-c | T4:综合报告@scribe@T1,T2,T3"
[@captain-protocol] wait-and-collect 300
[@captain-protocol] finalize-report "./output/competitor-report.md"
```

### 示例 2：架构决策 debate DAG

```
[@captain-protocol] captain-start "monorepo-debate" "monorepo vs polyrepo 辩论"
[@captain-protocol] add-members "advocate-monorepo, advocate-polyrepo, referee"
[@captain-protocol] create-tasks "T1:monorepo@advocate-monorepo | T2:polyrepo@advocate-polyrepo | T3:投票@referee@T1,T2 | T4:决策报告@scribe@T3"
[@captain-protocol] wait-and-collect 600
[@captain-protocol] finalize-report "./output/monorepo-decision.md"
```

## 与其他 skill 的关系

| Skill | 关系 |
|---|---|
| `agent-teams-playbook` | 上游（天龙 AgentTeams 入门手册，参考 4 类 DAG）|
| `dragon-commander` | 横向（captain 启动总入口）|
| `hierarchical-delegation` | 横向（3 层拓扑 captain/lead-member/specialist-member）|
| `convener-protocol` | 上游（多 Agent 辩论协议）|
| `massgen-consensus` | 横向（member 内 LLM 熔断 + 共识）|

## 不做什么

- ❌ **不重写** DSH AgentTeams 工具协议
- ❌ **不引入**新的 task lifecycle
- ❌ **不修改** `<workspace>/.agent-teams/` 目录结构
- ❌ **不替代** dragon-commander 的 `/command` 入口（dragon-commander 在 captain-start 之前做"需求分析 + 代理推荐"，captain-protocol 做"工具调用的自然语言包装"）

## 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| V1.0.0 | 2026-08-13 | 初始版本，封装 DSH AgentTeams 10 工具为 5 个天龙入口 |

## 参考资料

- **DSH AgentTeams 上游**：[NanmiCoder/dsh-agent-teams](https://github.com/NanmiCoder/dsh-agent-teams)
- **天龙入门手册**：`skills/agent-teams-playbook/SKILL.md`
- **天龙指挥官**：`skills/dragon-commander/SKILL.md`
- **天龙集成报告**：`analysis/dsh-agent-teams-upgrade-analysis.md`