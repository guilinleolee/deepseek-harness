import { ev } from "evalite";

// ============================================================
// 模板: 通用 LLM 评估
// ============================================================

/**
 * 基础问答评估
 */
ev("基础问答", async () => {
  const result = await llm.complete("法国的首都是什么?");
  const pass = result.includes("巴黎");
  return { pass, score: pass ? 1 : 0 };
});

/**
 * 结构化输出评估
 */
ev("JSON 结构输出", async () => {
  const result = await llm.complete(
    "返回一个 JSON 对象，包含 name 和 age 字段"
  );

  try {
    const parsed = JSON.parse(result);
    const hasName = "name" in parsed && typeof parsed.name === "string";
    const hasAge = "age" in parsed && typeof parsed.age === "number";

    return {
      pass: hasName && hasAge,
      score: (hasName ? 0.5 : 0) + (hasAge ? 0.5 : 0),
    };
  } catch {
    return { pass: false, score: 0 };
  }
});

/**
 * 语义相似度评估
 */
function stringSimilarity(a: string, b: string): number {
  const aLower = a.toLowerCase().trim();
  const bLower = b.toLowerCase().trim();

  if (aLower === bLower) return 1;
  if (aLower.includes(bLower)) return 0.8;
  if (bLower.includes(aLower)) return 0.8;

  // 简单的词重叠计算
  const aWords = new Set(aLower.split(/\s+/));
  const bWords = new Set(bLower.split(/\s+/));
  const intersection = new Set([...aWords].filter(x => bWords.has(x)));
  const union = new Set([...aWords, ...bWords]);

  return intersection.size / union.size;
}

// ============================================================
// 模板: 多模型对比评估
// ============================================================

const models = [
  openai("gpt-4"),
  openai("gpt-4-turbo"),
  anthropic("claude-3-sonnet"),
] as const;

for (const model of models) {
  ev(`[${model.modelId}] 基础问答`, async () => {
    const result = await model.complete("解释量子纠缠");
    const pass = result.length > 100 && result.includes("量子");

    return {
      pass,
      score: Math.min(result.length / 500, 1),
    };
  });
}

// ============================================================
// 模板: Trials 多次评估
// ============================================================

ev("数学计算稳定性", async ({ trials }) => {
  const results: number[] = [];

  for (let i = 0; i < trials; i++) {
    const result = await llm.complete("计算: 123 + 456 = ?");
    const numMatch = result.match(/\d+/g);

    if (numMatch) {
      const num = parseInt(numMatch[0]);
      results.push(num === 579 ? 1 : 0);
    } else {
      results.push(0);
    }
  }

  const avgScore = results.reduce((a, b) => a + b, 0) / results.length;

  return {
    pass: avgScore >= 0.8,
    score: avgScore,
  };
});

// ============================================================
// 模板: 分层评分评估
// ============================================================

interface分层评估结果 {
  accuracy: number;
  completeness: number;
  clarity: number;
  finalScore: number;
}

ev("多维评估", async (): Promise<分层评估结果> => {
  const result = await llm.complete(
    "用 100 字介绍人工智能"
  );

  // 准确性: 是否提到 AI 相关概念
  const accuracyKeywords = ["人工智能", "AI", "机器学习", "智能"];
  const accuracyScore = accuracyKeywords.filter(k =>
    result.includes(k)
  ).length / accuracyKeywords.length;

  // 完整性: 字数是否接近目标
  const targetLength = 100;
  const completenessScore = Math.max(
    0,
    1 - Math.abs(result.length - targetLength) / targetLength
  );

  // 清晰度: 句子是否完整
  const sentences = result.split(/[.!?]/);
  const completeSentences = sentences.filter(s => s.trim().length > 10);
  const clarityScore = completeSentences.length / Math.max(sentences.length, 1);

  // 综合评分
  const finalScore =
    accuracyScore * 0.4 +
    completenessScore * 0.3 +
    clarityScore * 0.3;

  return {
    accuracy: accuracyScore,
    completeness: completenessScore,
    clarity: clarityScore,
    finalScore,
  };
});
