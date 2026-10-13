---
license: UNKNOWN
github_repo: triggerdotdev/trigger.dev
github_hash: 5693b62cfbc03736a28c842d006177dd86fa66b2
last_updated: 2026-04-25
source_type: derived
triggers: ["trigger dev", "trigger-dev"]
---
# trigger-dev

> Trigger.dev集成 - 事件驱动的AI工作流编排平台

## 来源项目

| 项目 | Stars | 核心能力 |
|------|-------|---------|
| [triggerdotdev/trigger.dev](https://github.com/triggerdotdev/trigger.dev) | 14.3k | 事件驱动AI工作流 + 长时任务 + 人类审核 |

## 核心价值

填补天龙引擎在**事件驱动AI工作流编排**的关键空白，实现：
- 长时运行AI任务（无超时限制）
- 人类审核工作流（Waitpoints）
- LLM响应流式处理
- 复杂多步骤AI管道
- 自动重试和检查点恢复

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│ Trigger.dev Architecture                                     │
├─────────────────────────────────────────────────────────────┤
│  Event Sources                                              │
│  ├── Cron Schedules                                        │
│  ├── Webhooks                                              │
│  ├── Manual Triggers                                       │
│  └── AI/LLM Events                                        │
│                    ↓                                        │
│  Task Layer                                                │
│  ├── Long-running Tasks (no timeout)                       │
│  ├── Human-in-the-loop Waitpoints                          │
│  └── LLM Streaming                                        │
│                    ↓                                        │
│  Execution Layer                                            │
│  ├── Checkpointing / Resume                                │
│  ├── Automatic Retries                                     │
│  └── Idempotency                                          │
└─────────────────────────────────────────────────────────────┘
```

## 与paperclip-heartbeat对比

| 维度 | paperclip-heartbeat | Trigger.dev | 选择建议 |
|------|---------------------|-------------|---------|
| **定时任务** | Cron表达式 | 持久化Cron | 简单→heartbeat |
| **长时任务** | 有超时 | 无超时 | 复杂AI→Trigger.dev |
| **人类审核** | 无 | Waitpoints | 审批流程→Trigger.dev |
| **LLM流式** | 无 | 原生支持 | AI响应→Trigger.dev |
| **检查点恢复** | 无 | 自动 | 长任务→Trigger.dev |

## 天龙岗位升级

| 岗位 | 版本 | 新增能力 | 提升 |
|------|------|---------|------|
| **09-02编排协调师** | V8.71 → V8.72 | 事件驱动编排 + 长时任务 | ⭐⭐⭐⭐⭐ |
| **03构建师** | V8.71 → V8.72 | Trigger任务开发 | ⭐⭐⭐⭐ |
| **08发布师** | V8.71 → V8.72 | 部署后自动化工作流 | ⭐⭐⭐⭐ |

## 核心命令速查

```bash
# 安装SDK
npm install @trigger.dev/sdk
# 或
bun add @trigger.dev/sdk

# 初始化项目
npx create-trigger

# 部署
npx trigger.dev deploy

# 本地开发
npx trigger.dev dev
```

## SDK使用示例

### 任务定义

```typescript
import { task } from "@trigger.dev/sdk";

// AI研究任务
export const aiResearchTask = task({
  id: "ai-research",
  run: async (payload: { topic: string; depth: number }) => {
    // 长时运行，无超时
    const research = await conductResearch(payload.topic, payload.depth);

    // 人类审核点
    const approved = await waitForApproval(research.summary);

    if (!approved) {
      return { status: "rejected", reason: "需要更多信息" };
    }

    return { status: "completed", research };
  },
});
```

### LLM流式处理

```typescript
export const streamingAnalysis = task({
  id: "streaming-analysis",
  run: async (payload: { document: string }) => {
    const stream = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [{ role: "user", content: `分析: ${payload.document}` }],
      stream: true,
    });

    for await (const chunk of stream) {
      // 实时更新进度
      await ctx.updateMetadata({ progress: chunk.choices[0]?.delta?.content });
    }
  },
});
```

### 批量触发

```typescript
import { batchTrigger } from "@trigger.dev/sdk";

// 批量执行多个AI任务
const results = await batchTrigger({
  tasks: [
    { task: "ai-research", payload: { topic: "AI Agents" } },
    { task: "ai-research", payload: { topic: "LLM Optimization" } },
    { task: "ai-research", payload: { topic: "RAG Systems" } },
  ],
  concurrency: 3, // 最多3个并行
});
```

### 人类审核工作流

```typescript
export const approvalWorkflow = task({
  id: "approval-workflow",
  run: async (payload: { content: string; type: string }) => {
    // 生成内容
    const content = await generateContent(payload);

    // 创建审核点
    const review = await ctx.waitFor("content-review", {
      type: "approval",
      data: { content },
      timeout: 60 * 60 * 24, // 24小时超时
    });

    if (review.status === "approved") {
      // 发布内容
      return await publishContent(content);
    } else {
      return { status: "rejected", feedback: review.feedback };
    }
  },
});
```

## 天龙集成模式

### 模式1：复杂AI研究（推荐）

```typescript
// 天龙研究任务 + Trigger长时执行
import { task } from "@trigger.dev/sdk";

export const dragonResearchTask = task({
  id: "dragon-deep-research",
  run: async (payload: { query: string; sources: string[] }) => {
    // Step 1: 研究规划
    const plan = await plannerAgent(payload.query);

    // Step 2: 并行采集
    const results = await Promise.all(
      plan.subqueries.map((sq: string) => searchAndExtract(sq))
    );

    // Step 3: 人类审核
    const approved = await ctx.waitFor("research-review", {
      type: "approval",
      data: { plan, preliminaryResults: results },
    });

    if (!approved) {
      return { status: "needs_revision", feedback: approved.feedback };
    }

    // Step 4: 综合报告
    return await synthesizerAgent(plan, results);
  },
});
```

### 模式2：发布前审核

```typescript
// 自动化发布 + 人类审批
export const releaseWorkflow = task({
  id: "dragon-release-workflow",
  run: async (payload: { changes: string[]; env: string }) => {
    // 自动化测试
    const testResults = await runTests();
    if (!testResults.passed) {
      return { status: "test_failed", errors: testResults.errors };
    }

    // 安全扫描
    const securityReport = await securityScan(payload.changes);
    if (securityReport.critical > 0) {
      return { status: "security_issue", issues: securityReport.critical };
    }

    // 人类审批
    const approval = await ctx.waitFor("release-approval", {
      type: "approval",
      data: { testResults, securityReport, changes: payload.changes },
    });

    if (approval.status === "approved") {
      return await deployToEnv(payload.env);
    }

    return { status: "rejected", reason: approval.reason };
  },
});
```

## 与现有天龙能力协同

| 天龙组件 | Trigger.dev | 协同效果 |
|---------|------------|---------|
| **paperclip-heartbeat** | 基础调度 | 简单任务→heartbeat, 复杂AI→Trigger |
| **simstudio-api** | 工作流执行 | Sim可视化→Trigger执行 |
| **reactflow-workflow** | 编排设计 | ReactFlow→Trigger任务 |
| **e2b-sandbox** | 代码执行 | Trigger任务→E2B安全执行 |

## 部署与配置

```bash
# 环境变量
export TRIGGER_API_KEY="your-api-key"

# 本地开发
npx trigger.dev dev

# 部署
npx trigger.dev deploy --env production

# 查看日志
npx trigger.dev logs
```

## 预期收益

| 指标 | V8.71 | V8.72 | 提升 |
|------|-------|-------|------|
| **AI任务执行时长** | 有超时限制 | 无限制 | **质的飞跃** |
| **人类审核流程** | 手动 | 自动化Waitpoint | **+300%** |
| **LLM流式处理** | 无 | 原生支持 | **新增能力** |
| **检查点恢复** | 无 | 自动 | **+200%** |
| **AI工作流编排** | 基础 | 企业级 | **质的飞跃** |

## 技能文件

- [skills/trigger-dev/SKILL.md](skills/trigger-dev/SKILL.md)
- [skills/trigger-dev/scripts/trigger_client.ts](skills/trigger-dev/scripts/trigger_client.ts)
- [skills/trigger-dev/templates/workflows.ts](skills/trigger-dev/templates/workflows.ts)
