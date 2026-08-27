# Evalite Native 技能定义

## 技能元信息

| 字段 | 值 |
|------|-----|
| **名称** | evalite-native |
| **版本** | V1.0 |
| **类型** | LLM应用评估框架 |
| **来源** | mattpocock/evalite |
| **依赖** | Node.js 18+, Vitest, better-sqlite3 |

## 触发条件

- 评估LLM应用响应质量
- 模型对比测试
- 追踪执行路径和trace spans
- 持续质量监控
- 生成pass@k量化指标

## 执行流程

### Phase 1: 安装配置

```bash
# 安装 evalite
npm install evalite

# 创建配置文件
npx evalite init
```

### Phase 2: 定义评估

```typescript
// evalite.config.ts
import { defineConfig } from "evalite";
import { openai } from "ai";

export default defineConfig({
  models: {
    gpt4: openai("gpt-4"),
  },
  threshold: 0.8,
  trials: 3,
});
```

### Phase 3: 编写评估用例

```typescript
// evals/example.test.ts
import { ev } from "evalite";
import { openai } from "ai";

const model = openai("gpt-4");

ev("Test name", async () => {
  const result = await model.chat.completions.create({
    messages: [{ role: "user", content: "What is 2+2?" }],
  });
  return {
    pass: result.choices[0].message.content === "4",
    score: result.choices[0].message.content === "4" ? 1 : 0,
  };
});
```

### Phase 4: 运行评估

```bash
# 运行评估
npx evalite

# 观看模式
npx evalite --watch
```

## 与 Vitest 集成

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

## Scorer 系统

| Scorer | 描述 | 范围 |
|--------|------|------|
| `ev.pass()` | 简单布尔判定 | 0 or 1 |
| `ev.fail()` | 失败总是返回0 | 0 |
| `ev.score(fn)` | 自定义评分函数 | 0-1 |
| `ev.partial(fn, threshold)` | 阈值判定 | 0 or 1 |

## Dragon SQLite Schema

```sql
CREATE TABLE dragon_runs (
  id TEXT PRIMARY KEY,
  started_at INTEGER NOT NULL,
  completed_at INTEGER,
  eval_name TEXT NOT NULL,
  status TEXT NOT NULL
);

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

## 天龙协同

| 天龙组件 | 协同方式 |
|---------|---------|
| eval-harness | Evalite原生评估替代手动判断 |
| eval | pass@k量化指标 |
| 天龙SQLite | dragon_evals持久化 |

## 输出格式

```bash
# JSON格式输出
npx evalite --output json

# 表格格式输出
npx evalite --output table
```

## 最佳实践

1. **清晰的评估名称**: 使用描述性名称便于追踪
2. **适当的试验次数**: 高方差场景使用trials参数
3. **Trace捕获**: 复杂流程使用withTrace()
4. **阈值设置**: 根据业务需求设置合理的threshold
5. **历史对比**: 定期对比评估分数变化
