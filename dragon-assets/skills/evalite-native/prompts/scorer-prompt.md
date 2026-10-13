# Scorer 设计提示词

## 概述

Scorer 是 Evalite 评估框架的核心组件，用于量化 LLM 输出的质量。

## Scorer 类型

### 1. ev.pass() - 简单布尔判定

```typescript
ev("评估名称", async () => {
  const result = await llm.complete(prompt);
  return {
    pass: result === expected,  // 返回 true/false
  };
});
```

**适用场景**: 精确匹配、结构验证

### 2. ev.fail() - 总是失败

```typescript
ev("评估名称", async () => {
  return ev.fail();  // 总是返回 0
});
```

**适用场景**: 基准测试、占位符

### 3. ev.score() - 自定义评分

```typescript
ev("评估名称", async () => {
  const result = await llm.complete(prompt);
  return {
    score: similarity(result, expected),  // 返回 0-1 之间的分数
  };
});
```

**评分函数示例**:

```typescript
// 字符串相似度
function stringSimilarity(a: string, b: string): number {
  const levenshtein = (s1: string, s2: string): number => {
    const m = s1.length;
    const n = s2.length;
    const dp: number[][] = Array(m + 1).fill(null)
      .map(() => Array(n + 1).fill(0));

    for (let i = 0; i <= m; i++) dp[i][0] = i;
    for (let j = 0; j <= n; j++) dp[0][j] = j;

    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        if (s1[i - 1] === s2[j - 1]) {
          dp[i][j] = dp[i - 1][j - 1];
        } else {
          dp[i][j] = Math.min(
            dp[i - 1][j] + 1,
            dp[i][j - 1] + 1,
            dp[i - 1][j - 1] + 1
          );
        }
      }
    }
    return dp[m][n];
  };

  const maxLen = Math.max(a.length, b.length);
  if (maxLen === 0) return 1;
  return 1 - levenshtein(a, b) / maxLen;
}

// JSON 相似度
function jsonSimilarity(a: unknown, b: unknown): number {
  const jsonA = JSON.stringify(a);
  const jsonB = JSON.stringify(b);
  if (jsonA === jsonB) return 1;
  if (jsonA === "{}" || jsonA === "[]") return 0;
  return stringSimilarity(jsonA, jsonB);
}

// 语义相似度 (需要嵌入模型)
async function semanticSimilarity(text1: string, text2: string): Promise<number> {
  const embeddings = await embed([
    { model: "text-embedding-3-small", text: text1 },
    { model: "text-embedding-3-small", text: text2 },
  ]);

  const [e1, e2] = embeddings.map(e => e.embedding);
  const dot = e1.reduce((sum, v, i) => sum + v * e2[i], 0);
  const norm1 = Math.sqrt(e1.reduce((sum, v) => sum + v * v, 0));
  const norm2 = Math.sqrt(e2.reduce((sum, v) => sum + v * v, 0));
  return dot / (norm1 * norm2);
}
```

### 4. ev.partial() - 阈值判定

```typescript
ev("评估名称", async () => {
  const result = await llm.complete(prompt);
  return {
    score: result.length / expected.length,  // 先计算分数
  };
});

// 在配置中使用阈值
ev.partial((actual, expected) => {
  const threshold = 0.8;
  return stringSimilarity(actual, expected) >= threshold;
}, threshold);
```

## 评分标准

| 分数 | 描述 | 含义 |
|------|------|------|
| 1.0 | 完全匹配 | 精确通过 |
| 0.8-0.99 | 高度匹配 | 基本通过 |
| 0.5-0.79 | 部分匹配 | 需要改进 |
| 0-0.49 | 失败 | 不达标 |

## 最佳实践

### 1. 使用 trials 提高稳定性

```typescript
// 配置 trials
export default defineConfig({
  trials: 5,  // 重复 5 次，取平均
  threshold: 0.8,
});
```

### 2. 结合 pass 和 score

```typescript
ev("评估名称", async () => {
  const result = await llm.complete(prompt);
  const score = stringSimilarity(result, expected);

  return {
    pass: score >= 0.9,  // 精确判定
    score: score,       // 连续评分
  };
});
```

### 3. 分层评分

```typescript
ev("多维评估", async () => {
  const result = await llm.complete(prompt);

  // 多个维度评分
  const scores = {
    accuracy: checkAccuracy(result),
    completeness: checkCompleteness(result),
    clarity: checkClarity(result),
  };

  // 综合评分
  const finalScore =
    scores.accuracy * 0.4 +
    scores.completeness * 0.3 +
    scores.clarity * 0.3;

  return {
    pass: finalScore >= 0.8,
    score: finalScore,
    details: scores,
  };
});
```

### 4. 模型对比

```typescript
await evalite.each({
  models: [openai("gpt-4"), anthropic("claude-3")],
  task: async (model) => {
    return await model.complete(prompt);
  },
});
```

## 常见 Scorer 模式

```typescript
// 1. 包含关键词
const containsKeywords = (text: string, keywords: string[]) =>
  keywords.every(k => text.includes(k));

// 2. JSON 结构验证
const validateJsonStructure = (json: unknown, schema: object) => {
  // 使用 JSON Schema 验证
  return isValid(json, schema);
};

// 3. 正则匹配
const matchesPattern = (text: string, pattern: RegExp) =>
  pattern.test(text);

// 4. 长度约束
const withinLength = (text: string, min: number, max: number) =>
  text.length >= min && text.length <= max;

// 5. 数学计算
const checkMath = (result: string, expected: number, tolerance = 0.01) => {
  const num = parseFloat(result);
  return Math.abs(num - expected) <= tolerance;
};
```
