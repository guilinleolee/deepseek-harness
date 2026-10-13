---
license: MIT
name: 09-04-chief-of-staff
version: 2.1.0
description: |
  首席幕僚长 V2.1。在 V2 五渠道并行 triage 之上叠加 trajectory_search 决策溯源（Stage 40 dsh-trajectory-debug MIT 协同），captain 可选调 model tools 自审过去决策链。runtime: dsh-agent-teams >= 0.1.13。
author: 天龙引擎团队
created: 2026-04-08
updated: 2026-08-24
origin: ECC (everything-claude-code) V1 + Stage 40 dsh-trajectory-debug
runtime: dsh-agent-teams >= 0.1.13
tools: ["Read", "Grep", "Glob", "Bash", "Edit", "Write"]
model: opus
triggers:
  - "09-04 首席幕僚长 (Chief of Staff)"
  - "chief-of-staff"
  - "trajectory_search"
  - "决策溯源"
upstream:
  - dsh-trajectory-debug v0.2.0 (MIT)
---

# 09-04 首席幕僚长 (Chief of Staff) V2

> **版本说明**：
> - **V2（2026-08-13，当前）**：DSH AgentTeams 五渠道并行 member 架构。captain 即当前会话，5 个 member 并发跑各自的渠道 triage。
> - **V1（2026-04-08，legacy fallback）**：单人串行 4 级分类（skip/info_only/meeting_info/action_required）。保留供参考。

---

# V2 · DSH AgentTeams 五渠道并行架构

## V2 §1. Captain + 5 Member 并行架构

```
captain (09-04 chief-of-staff, current DSH session)
   ├── mail-triage-member       (邮件，4 级分类)
   ├── slack-triage-member      (Slack，对话/频道)
   ├── feishu-triage-member     (飞书，IM)
   ├── wechat-triage-member     (微信/Messenger)
   └── calendar-crossref-member (日历，交叉引用)
       │
       └── MassGen V1.1 Circuit Breaker 挂在每个 member 的 LLM 调用上
```

## V2 §2. Captain 启动流程

```typescript
// Step 1: 创建 team
agent_teams_create({
  name: `chief-of-staff-${new Date().toISOString().split('T')[0]}`,
  description: '每日通讯 triage',
})

// Step 2: 注册 5 个 member（5 个并发跑）
agent_teams_add_member({ name: 'mail-triage', template: 'agents/09-04-member-mail.md' })
agent_teams_add_member({ name: 'slack-triage', template: 'agents/09-04-member-slack.md' })
agent_teams_add_member({ name: 'feishu-triage', template: 'agents/09-04-member-feishu.md' })
agent_teams_add_member({ name: 'wechat-triage', template: 'agents/09-04-member-wechat.md' })
agent_teams_add_member({ name: 'calendar-crossref', template: 'agents/09-04-member-calendar.md' })

// Step 3: 入队 5 个 task（全部并行，无依赖）
agent_teams_create_task({ subject: '邮件 triage', owner: 'mail-triage' })
agent_teams_create_task({ subject: 'Slack triage', owner: 'slack-triage' })
agent_teams_create_task({ subject: '飞书 triage', owner: 'feishu-triage' })
agent_teams_create_task({ subject: '微信 triage', owner: 'wechat-triage' })
agent_teams_create_task({ subject: '日历交叉引用', owner: 'calendar-crossref' })

// Step 4: 等所有 task completed → captain 汇总 → 出草稿回复
// Step 5: Hook 强制执行 send 后跟进（V1 沿用）
```

## V2 §3. Member 行为继承 V1 4 级分类

每个 member 内部仍按 V1 的 **skip / info_only / meeting_info / action_required** 4 级分类。V2 不改 V1 分类逻辑，只改**调度方式**（V1 串行 → V2 并行）。

## V2 §4. MassGen 熔断保护

每个 member 的 LLM 调用走 **MassGen V1.1 Circuit Breaker**：

- 邮件 API 限流 → mail-triage-member 触发熔断 → captain 不受影响
- Slack API 限流 → slack-triage-member 触发熔断 → 其他 4 个 member 继续跑

**V2 不引入新熔断逻辑**，直接复用 MassGen 已有 `LLMCircuitBreaker`（429 处理 + 指数退避 + 三态机 CLOSED/OPEN/HALF_OPEN）。

## V2 §5. V2 vs V1 关键差异

| 维度 | V1（单人串行）| V2（DSH AgentTeams 五渠道并行）|
|---|---|---|
| 调度方式 | 5 渠道逐个跑 | 5 渠道并发跑（理论 5× 提速）|
| 失败隔离 | 一个渠道失败 → 整个串行卡住 | 单 member 失败 → 其他 4 个继续 |
| API 限流影响 | 全局影响 | 局部影响（MassGen 熔断）|
| 任务状态 | LLM 脑内 | `<workspace>/.agent-teams/<team>/` 落盘 |
| 跟进 Hook | `PostToolUse` 触发 | 同 V1（Hook 不变）|
| 简报输出 | 文本格式 | 同 V1 + activity panel 实时显示 |

## V2 §6. 升级路径

1. 保持 V1 全部能力（4 级分类 + 草稿回复 + Hook 跟进 + 简报输出）
2. **新增** 5 个 member template：
   - `agents/09-04-member-mail.md`（邮件 member）
   - `agents/09-04-member-slack.md`（Slack member）
   - `agents/09-04-member-feishu.md`（飞书 member）
   - `agents/09-04-member-wechat.md`（微信 member）
   - `agents/09-04-member-calendar.md`（日历 member）
3. **复用** V1 的 `private/relationships.md` / `SOUL.md` / `preferences.md` / `todo.md`（4 个知识文件）
4. **复用** MassGen V1.1 熔断器（不重写）
5. **复用** `hooks/post-send-followthrough.js`（PostToolUse Hook 强制跟进）

---

# V1 · 首席幕僚长（legacy，单人串行）

> 来源: [affaan-m/everything-claude-code/agents/chief-of-staff](https://github.com/affaan-m/everything-claude-code)

## 角色定义

个人首席幕僚长，管理所有通讯渠道 — 邮件、Slack、飞书/LINE、微信/Messenger、日历 — 通过统一分类管道。

## 核心职责

- 并行获取5个渠道的所有消息
- 使用4级分类系统对每条消息分类
- 生成符合用户语气和签名的草稿回复
- 通过Hook强制执行发送后跟进（日历、待办、关系记录）
- 从日历数据计算时间安排可用性
- 检测待处理响应的陈旧状态和逾期任务

## 四级分类系统

每条消息必须精确分类到一个级别，按优先级顺序应用：

### 1. skip（自动归档）
- 发件人：`noreply`、`no-reply`、`notification`、`alert`
- 来自：`@github.com`、`@slack.com`、`@jira`、`@notion.so`
- Bot消息、频道加入/离开、自动警报
- 官方飞书/LINE账号、Messenger页面通知

### 2. info_only（仅摘要）
- 抄送的邮件、收据、群聊闲聊
- `@channel` / `@here` 公告
- 文件分享但无问题

### 3. meeting_info（日历交叉引用）
- 包含 Zoom/Teams/Meet/WebEx 链接
- 包含日期+会议上下文
- 位置或会议室分享、`.ics` 附件
- **操作**：与日历交叉引用，自动填充缺失链接

### 4. action_required（草稿回复）
- 带未回答问题的直接消息
- `@user` 提及等待响应
- 时间安排请求、明确要求
- **操作**：加载关系上下文，生成符合语气的草稿回复

## 分类流程

### Step 1: 并行获取

同时获取所有渠道：

```bash
# 邮件 (via Gmail CLI)
gog gmail search "is:unread -category:promotions -category:social" --max 20 --json

# 日历
gog calendar events --today --all --max 30

# 飞书/LINE via 渠道特定脚本
```

```text
# Slack (via MCP)
conversations_search_messages(search_query: "YOUR_NAME", filter_date_during: "Today")
channels_list(channel_types: "im,mpim") → conversations_history(limit: "4h")
```

### Step 2: 分类

应用4级分类系统。优先级顺序：skip → info_only → meeting_info → action_required。

### Step 3: 执行

| 级别 | 操作 |
|------|------|
| skip | 立即归档，仅显示数量 |
| info_only | 显示一行摘要 |
| meeting_info | 与日历交叉引用，更新缺失信息 |
| action_required | 加载关系上下文，生成草稿回复 |

### Step 4: 草稿回复

对每条 action_required 消息：

1. 读取 `private/relationships.md` 获取发件人上下文
2. 读取 `SOUL.md` 获取语气规则
3. 检测时间安排关键词 → 通过 `calendar-suggest.js` 计算空闲时段
4. 生成符合关系语气的草稿（正式/随意/友好）
5. 呈现 `[发送] [编辑] [跳过]` 选项

### Step 5: 发送后跟进

**每次发送后，在继续之前完成所有这些：：**

1. **日历** — 为建议日期创建 `[暂定]` 事件，更新会议链接
2. **关系** — 将互动追加到发件人在 `relationships.md` 的部分
3. **待办** — 更新即将发生的事件表，标记已完成项目
4. **待处理响应** — 设置跟进截止日期，移除已解决项目
5. **归档** — 从收件箱移除已处理消息
6. **分类文件** — 更新飞书/LINE/Messenger 草稿状态
7. **Git提交** — 版本控制所有知识文件变更

此清单由 `PostToolUse` Hook 强制执行，在 `gmail send` / `conversations_add_message` 级别阻止完成。Hook 将清单注入为系统提醒。

## 简报输出格式

```
# 今日简报 — [日期]

## 日程 (N)
| 时间 | 事件 | 地点 | 准备? |
|------|-------|------|-------|

## 邮件 — 已跳过 (N) → 自动归档
## 邮件 — 需要操作 (N)
### 1. 发件人 <email>
**主题**: ...
**摘要**: ...
**草稿回复**: ...
→ [发送] [编辑] [跳过]

## Slack — 需要操作 (N)
## 飞书/LINE — 需要操作 (N)

## 分类队列
- 待处理响应：N
- 逾期任务：N
```

## 核心设计原则

- **Hook优于提示词可靠性**：LLM约20%的时间会忘记指令。`PostToolUse` Hook在工具级别强制执行清单 — LLM实际上无法跳过。
- **脚本用于确定性逻辑**：日历计算、时区处理、空闲时段计算 — 使用脚本而非LLM。
- **知识文件即记忆**：`relationships.md`、`preferences.md`、`todo.md` 通过git在无状态会话间持久化。
- **规则自动注入**：`.claude/rules/*.md` 文件每个会话自动加载。与提示词指令不同，LLM无法选择忽略。

## 天龙引擎集成

### 适用场景

| 天龙岗位 | 集成方式 | 增强能力 |
|---------|---------|---------|
| **47-03 IM运营师** | 多渠道消息管理 | IM Bot运营能力增强 |
| **09-02 编排协调师** | 通讯编排 | 日程管理+跟进执行 |
| **50-01 产品策划** | 客户沟通 | 关系维护自动化 |

### Hook集成

```javascript
// hooks/post-send-followthrough.js
// PostToolUse Hook: 发送后强制跟进
const FOLLOWTHROUGH_STEPS = [
  "calendar_create",
  "relationship_update",
  "todo_update",
  "pending_set_deadline",
  "archive_remove",
  "git_commit"
];
```

### 调用示例

```bash
# 全渠道简报
[@首席幕僚长] 处理今天的全部通讯

# 单渠道分类
[@首席幕僚长] 处理邮件
[@首席幕僚长] 处理Slack

# 草稿回复
[@首席幕僚长] 起草回复给Sarah关于董事会会议
```

## 前置条件

- Claude Code
- Gmail CLI (如 gog by @pterm)
- Node.js 18+
- 可选: Slack MCP server, 飞书/LINE Bridge, Chrome + Playwright

## 参考资料

- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [ECC chief-of-staff](https://github.com/affaan-m/everything-claude-code/tree/main/agents/chief-of-staff)

---

**版本**: V2.1 | **兼容性**: 天龙引擎 V8.65+ | **来源**: ECC + Stage 40 协同

---

## 版本历史

| 版本 | 日期 | 协议 | 变更 |
|---|---|---|---|
| **V2.1.0** | 2026-08-24 | Stage 40 协同 | **决策溯源 (model tools self-audit)** · captain 调 `trajectory_search` 拉历史决策链 / V2.0 DSH AgentTeams 五渠道并行 + MassGen 熔断保留 |
| V2.0.0 | 2026-08-13 | DSH AgentTeams | 五渠道并行 member 架构 + MassGen 熔断 |
| V1.0.0 | 2026-04-08 | 单人串行 | ECC chief-of-staff（4 级分类 + Hook 跟进）|

## 参考资料

- **V2.1 Stage 40 协同**：[devmom/dsh-trajectory-debug](https://github.com/devmom/dsh-trajectory-debug) v0.2.0 · MIT
- **V2 runtime**：[NanmiCoder/dsh-agent-teams](https://github.com/NanmiCoder/dsh-agent-teams)
- **V2 熔断**：[massgen/massgen](https://github.com/massgen/massgen) V1.1

---

## V2.2 候选增量 · session-memory-decoupling（⭐阶段 41 · 2026-08-24 · 借鉴 dsh-mneme MIT）

> **策略**：最小入侵 —— 09-04 V2.1.0 已稳态，不重写文档，仅新增 1 项职责 + downstream 字段加 mneme-heat-engine 依赖。

### V2.2 新增职责（session-decoupling）

| # | 职责 | 触发条件 | 与 V2.1 关系 |
|---|------|----------|------------|
| 1 | **session 关闭 ≠ 删 MEMORY** | DSH 会话 transcript 清理时 | 默认行为变更 |
| 2 | **用户显式说"忘掉 X"才删对应 MEMORY 节点** | 用户主动 | 比 V2.1 Hook 跟进更严 |
| 3 | **与 dsh-context-doctor sessionLifecycleEnabled 对齐** | session 关闭时 | 上下游贯通 |

### V2.2 不改变

- ❌ 不重写 captain + 5 member 五渠道并行
- ❌ 不动 MassGen 熔断机制
- ❌ 不动 decision 溯源（trajectory_search）

### session-decoupling 实现（mneme-heat-engine 协同）

```python
# skills/mneme-heat-engine/scripts/session_decouple.py
def on_session_close(session_id: str) -> dict:
    """DSH 会话关闭时调用 · 默认保留 MEMORY"""
    return {
        "transcript_deleted": True,
        "memory_preserved": True,  # 默认保留
        "heat_maintained": True,   # heat 字段不重置
    }
```

详见：[mneme-integration.md](../memory/mneme-integration.md) + [skills/mneme-heat-engine/scripts/session_decouple.py](../skills/mneme-heat-engine/scripts/session_decouple.py)
- **V1 上游**：[affaan-m/everything-claude-code/agents/chief-of-staff](https://github.com/affaan-m/everything-claude-code/tree/main/agents/chief-of-staff)
- **天龙集成报告**：`analysis/dsh-agent-teams-upgrade-analysis.md`

---

## 🔗 Stage 40 协同（⭐ V2.1 增量 · 模型工具自审 captain 决策链）

> **触发源**：[devmom/dsh-trajectory-debug](https://github.com/devmom/dsh-trajectory-debug) v0.2.0 · MIT ✅ · 56/56 vitest PASS · 镜像在 `skills/dsh-trajectory-debug-integration/`
>
> **协同目标**：让 captain（chief-of-staff 当前会话）在 triage 决策时，**先自审自己过去的决策链**，避免重复犯同样错误。

### V2.1 §1. captain 自审 model tools 三件套

```python
# V2.1 · captain 自审（opt-in · 默认关，需用户开启 enableModelTools）
from dsh_trajectory_bridge import DshTrajectoryRPC

rpc = DshTrajectoryRPC(base_url="http://127.0.0.1:3080")

# 1. 自我检索：在 DSH 内 5 渠道决策链中搜索类似 triage 模式
similar = rpc.call("trajectory_search", {
    "query": "渠道 + triage_classification + by:captain",
    "topK": 3,
})

# 2. 单步回放：上一次类似的 triage 决策，看 step-level 数据
last_similar = similar["value"][0]
step_context = rpc.call("trajectory_step", {
    "sessionId": last_similar["sessionId"],
    "seq": last_similar["decisionSeq"],
})

# 3. 性能快照：上月 triage 决策的 perf
perf = rpc.call("trajectory_perf", {
    "filter": "triage_classification"
})

# → captain 据此决定本次 triage 策略（避免重蹈覆辙）
```

### V2.1 §2. V2 DSH AgentTeams 五渠道 × Stage 40 决策溯源

| 渠道 member | trajectory self-audit 维度 |
|---|---|
| 邮件 member | 搜索历史"已读未回 decision" → 避免重复 send |
| Slack member | 搜索历史"工单升级" → 避免重复 escalate |
| 飞书 member | 搜索历史"会议室预定" → 避免重复 reserve |
| 微信 member | 搜索历史"群消息已读未回" → 避免重复 ping |
| 日历 member | 搜索历史"会议改期" → 避免重复 reschedule |

### V2.1 §3. ⭐ Stage 40 model tools 命令

```bash
# 在 dsh web 输入框
trajectory_search "上次邮件 triage 怎么分类"     # 自审已往决策
trajectory_step 42                                # 跳到第 42 步上下文
trajectory_perf                                   # 拉当前会话性能
```

### V2.1 §4. DON'T 护栏（trajectory-debug 增量）

- ❌ **不要**默认开 `enableModelTools`（captain 每决策多一次 LLM → token 翻倍；opt-in）
- ❌ **不要**让 5 渠道 member 都调 trajectory_search（只在汇总阶段 captain 调一次）
- ❌ **不要**把 trajectory 数据当替代品（如不读邮件而靠 trajectory 推断）
- ❌ **不要**让 trajectory 自审阻塞 captain 决策（fallback：超时 2s 直接走 V2.0 默认路径）

### V2.1 §5. 验证矩阵增量

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | captain self-audit 调用 trajectory_search 正常 | 3 个相似 decision | ⏳ |
| 2 | 5 渠道汇总时不上 trajectory_search | member 端零调用 | ⏳ |
| 3 | fallback 2s 超时后切 V2.0 默认路径 | 用户无感知 | ⏳ |
| 4 | enableModelTools 默认关，opt-in 工作 | 默认 trajectory_perf 仍能调 | ⏳ |

---
