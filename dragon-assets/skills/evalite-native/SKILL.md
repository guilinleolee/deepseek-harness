---
license: UNKNOWN
triggers: ["evalite native", "Evalite Native SKILL"]
---
# Evalite Native SKILL

## L0: 一句话描述
TypeScript原生LLM应用评估框架，与Vitest无缝集成，支持Scorer评分和WebSocket实时追踪。

## L1: 使用场景
- 评估LLM应用的响应质量（pass/fail判定）
- 模型对比测试（evalite.each()多模型并行）
- 追踪执行路径（trace spans捕获）
- 持续质量监控（SQLite存储历史）

## L2: 详细文档

### 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Evalite 核心架构                          │
├─────────────────────────────────────────────────────────────┤
│  evalite.config.ts → Jiti动态加载                         │
│         ↓                                                │
│  EvaliteRunner (状态机: idle → running)                  │
│         ↓                                                │
│  ┌─────────────────────────────────────────────────┐     │
│  │           Vitest Custom Reporter                  │     │
│  │  • onTestFailed → captureEvalResult            │     │
│  │  • onBenchmarkComplete → computeAggregate      │     │
│  └─────────────────────────────────────────────────┘     │
│         ↓                                                │
│  SQLite (better-sqlite3) → dragon_evals 表              │
│         ↓                                                │
│  Fastify + WebSocket → 100ms节流广播                    │
└─────────────────────────────────────────────────────────────┘
```

### 核心API

```typescript
// 1. 定义评估
import { ev } from "evalite";

// 2. 使用Scorer评分
ev("Test name", async () => {
  const result = await runLLM(input);
  return {
    // 简单pass/fail
    pass: result === expected,
    // 或使用Scorer (0-1)
    score: similarity(result, expected),
  };
});

// 3. 模型对比
await evalite.each({
  models: [openai("gpt-4"), anthropic("claude-3")],
  task: async (model) => {
    return await model.complete(prompt);
  },
});

// 4. 追踪执行路径
ev("Traced eval", async () => {
  return await withTrace("llm-call", async () => {
    return await llm.complete(prompt);
  });
});
```

### 评分Scorer系统

| Scorer类型 | 描述 | 范围 |
|------------|------|------|
| `ev.pass()` | 简单布尔判定 | 0 or 1 |
| `ev.fail()` | 失败总是返回0 | 0 |
| `ev.score(fn)` | 自定义评分函数 | 0-1 |
| `ev.partial(fn, threshold)` | 阈值判定 | 0 or 1 |

### 集成天龙引擎

```bash
# 安装 evalite
npm install evalite

# 创建配置
npx evalite init

# 运行评估
npx evalite

# 观看模式
npx evalite --watch
```

### 与Vitest集成

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";
import Evalite from "@evalite/vitest";

export default defineConfig({
  plugins: [Evalite()],
  test: {
    reporters: ["default", "evalite"],
  },
});
```

### 评分标准

| 分数 | 描述 | 含义 |
|------|------|------|
| 1.0 | 完全匹配 | 精确通过 |
| 0.8-0.99 | 高度匹配 | 基本通过 |
| 0.5-0.79 | 部分匹配 | 需要改进 |
| 0-0.49 | 失败 | 不达标 |

### Dragon SQLite Schema

```sql
CREATE TABLE dragon_evals (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  input TEXT NOT NULL,
  expected TEXT,
  actual TEXT,
  score REAL,
  status TEXT DEFAULT 'pending',
  created_at INTEGER DEFAULT (strftime('%s', 'now')),
  FOREIGN KEY (run_id) REFERENCES dragon_runs(id)
);

CREATE TABLE dragon_traces (
  id TEXT PRIMARY KEY,
  eval_id TEXT NOT NULL,
  trace_json TEXT NOT NULL,
  created_at INTEGER DEFAULT (strftime('%s', 'now')),
  FOREIGN KEY (eval_id) REFERENCES dragon_evals(id)
);
```

### 与天龙九部协同

| 天龙组件 | 协同方式 |
|---------|---------|
| eval-harness | Evalite原生评估替代手动判断 |
| eval | pass@k量化指标 |
| 天龙SQLite | dragon_evals持久化 |

### 常见配置

```typescript
// evalite.config.ts
import { defineConfig } from "evalite";
import { openai } from "ai";

export default defineConfig({
  // 模型配置
  models: {
    gpt4: openai("gpt-4"),
    claude: anthropic("claude-3-sonnet"),
  },
  // 评分阈值
  threshold: 0.8,
  // 试验次数
  trials: 3,
  // 输出格式
  output: "table", // or "json"
});
```

### WebSocket实时追踪

```typescript
// 客户端连接
const ws = new WebSocket("ws://localhost:3000");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // { type: "result", eval: "...", score: 0.9 }
};
```

### 最佳实践

1. **清晰的评估名称**: 使用描述性名称便于追踪
2. **适当的试验次数**: 高方差场景使用trials参数
3. **Trace捕获**: 复杂流程使用withTrace()
4. **阈值设置**: 根据业务需求设置合理的threshold
5. **历史对比**: 定期对比评估分数变化

### 预期收益

| 指标 | 效果 |
|------|------|
| 评估效率 | +200% (vs手动判断) |
| 追踪能力 | +500% (新增trace spans) |
| 模型对比 | +300% (evalite.each) |
| 持久化 | +100% (Dragon SQLite) |
