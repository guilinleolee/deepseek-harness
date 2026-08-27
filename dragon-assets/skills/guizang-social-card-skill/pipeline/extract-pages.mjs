// extract-pages.mjs · 博主 9 维全息 → pages.jsonl（5-6 页 carousel）
// 阶段 19 V2.0
//
// 输出 JSONL 格式（每行一个 page 对象）：
//   {
//     page: 1,
//     recipe: "M01",
//     role: "cover" | "essay" | "closing" | "pipeline" | "pull-quote" | "two-signals" | "data" | "trap" | "takeaway",
//     title: "...",
//     subtitle: "...",
//     body: "...",
//     kicker: "...",
//     lead: "...",
//     ledger: [{ n: "01", title: "...", desc: "..." }, ...],
//     meta: { page: "1 / 5", date: "2026.07" }
//   }

import fs from "node:fs";
import { suggestCarousel } from "./recipe-rules.mjs";

/**
 * 从博主 9 维全息抽取 5-6 页 carousel 计划
 * @param {object} profile - 9 维博主全息
 * @param {object} choice - palette 决策
 * @param {object} recipe - recipe 决策（来自 selectRecipe）
 * @returns {Array<object>} page 数组
 */
export function extractPages(profile, choice, recipe) {
  const recipes = suggestCarousel(recipe);
  const name = profile.blogger_name || profile.blogger_id || "博主";
  const style = profile.dim_7_writing_style || {};
  const vocab = profile.dim_6_vocabulary || {};
  const meta = {
    date: new Date().toISOString().slice(0, 7), // 2026-07
    issue: "Issue 01",
    consent: profile._meta?.consent || {},
  };

  const baseMeta = {
    style_name: style.style_name || "个人风",
    mother_formula: style.mother_formula || "",
    voice_keywords: (style.voice_keywords || []).slice(0, 6),
    top_words: (vocab.top_words || []).slice(0, 6),
    metaphor_library: (style.metaphor_library || []).slice(0, 5),
    emotion_library: style.emotion_library || [],
    closing_patterns: style.closing_patterns || [],
  };

  // 共用：所有 page 都可继承的上下文
  const pages = [];

  // ───── Page 1: Cover ─────
  pages.push({
    page: 1,
    recipe: recipes[0],
    role: "cover",
    kicker: `${name.toUpperCase()} · ${baseMeta.style_name.toUpperCase()}`,
    title: name,
    subtitle: baseMeta.mother_formula || "基于博主全息自动生成",
    lead: `本期 · ${recipes.length} 页 · ${baseMeta.style_name}`,
    body: "",
    meta: { page: `1 / ${recipes.length}`, issue: meta.issue, date: meta.date },
    _ctx: baseMeta,
  });

  // ───── Page 2: Essay / Two Signals ─────
  if (recipes[1] === "M03") {
    pages.push({
      page: 2,
      recipe: "M03",
      role: "essay",
      kicker: "ESSAY · 文风 DNA",
      title: baseMeta.mother_formula || "老李在认真聊一件让他兴奋的事",
      subtitle: "L2 style consistency",
      lead: `标志词：${baseMeta.voice_keywords.slice(0, 3).join(" · ")}`,
      body: [
        `自检 L1 硬规则：${profile.dim_7_writing_style?.self_check_4_layer?.L1_hard_rules || "6 类踩雷词零命中"}`,
        `自检 L3 内容质量：${profile.dim_7_writing_style?.self_check_4_layer?.L3_content_quality || "具体人/场景/花费"}`,
      ].join("\n\n"),
      meta: { page: `2 / ${recipes.length}` },
      _ctx: baseMeta,
    });
  } else {
    // S02 Two Signals: 对比博主的两类内容
    pages.push({
      page: 2,
      recipe: "S02",
      role: "two-signals",
      kicker: "TWO SIGNALS · 两类内容",
      title: "知识区 · 测评区",
      subtitle: "博主双线内容定位",
      lead: `${baseMeta.style_name} 的两个内容方向`,
      body: "",
      meta: { page: `2 / ${recipes.length}` },
      _ctx: baseMeta,
    });
  }

  // ───── Page 3: Pipeline / Data ─────
  if (recipes[2] === "M07") {
    // M07 Closing Note：ledger items 来自 voice_keywords + metaphor_library
    const ledger = baseMeta.voice_keywords.slice(0, 4).map((kw, i) => ({
      n: String(i + 1).padStart(2, "0"),
      title: kw,
      desc: baseMeta.metaphor_library[i] || baseMeta.top_words[i] || "",
    }));
    pages.push({
      page: 3,
      recipe: "M07",
      role: "closing",
      kicker: "LEDGER · 老李会用的 4 个词",
      title: "收束笔记",
      subtitle: "M07 closing note",
      lead: "从母公式看，这是有阅历的人在认真聊。",
      ledger,
      meta: { page: `3 / ${recipes.length}` },
      _ctx: baseMeta,
    });
  } else if (recipes[2] === "S03") {
    pages.push({
      page: 3,
      recipe: "S03",
      role: "data",
      kicker: "DATA LAYER · 内容结构",
      title: "博主全息",
      subtitle: "9 维 schema",
      lead: "声纹 6 + 文风 1 + IP 视觉 1 + 设计风格 1 = 9",
      body: [
        "dim_1 音色 → TTS 复刻",
        "dim_2 语速 → 节奏匹配",
        "dim_3 方言 → 地域特征",
        "dim_4 情绪 → 情感表达",
        "dim_5 韵律 → 抑扬顿挫",
        "dim_6 高频词 → 用词特征",
        "dim_7 文风 → 文字风格",
        "dim_8 IP 视觉 → 人物锚图",
        "dim_9 设计风格 → 海报美学",
      ].join("\n"),
      meta: { page: `3 / ${recipes.length}` },
      _ctx: baseMeta,
    });
  }

  // ───── Page 4: Pipeline / Trap ─────
  if (recipes[3] === "M14") {
    // M14 Vertical Pipeline: rhythm_tools
    const tools = (profile.dim_7_writing_style?.rhythm_tools || []).slice(0, 4);
    pages.push({
      page: 4,
      recipe: "M14",
      role: "pipeline",
      kicker: "WORKFLOW · 写作 4 步",
      title: "老李风节奏工具",
      subtitle: "M14 vertical pipeline",
      lead: "扣主线 · 句式断裂 · 重复强调 · 场景切换",
      pipeline: tools.map((t, i) => ({
        nb: String(i + 1).padStart(2, "0"),
        title: t,
        desc: baseMeta.knowledge_output || "聊着聊着顺手掏出来",
      })),
      meta: { page: `4 / ${recipes.length}` },
      _ctx: baseMeta,
    });
  } else if (recipes[3] === "S05") {
    pages.push({
      page: 4,
      recipe: "S05",
      role: "trap",
      kicker: "WARN · 踩雷词",
      title: "别用这些词",
      subtitle: "M07 L1 hard rules",
      lead: (profile.dim_6_vocabulary?.forbidden_words || []).slice(0, 3).join(" · "),
      trap: (profile.dim_6_vocabulary?.forbidden_words || []).map((w, i) => ({
        nb: String(i + 1).padStart(2, "0"),
        title: w,
        desc: "L1 硬规则：6 类踩雷词零命中",
      })),
      meta: { page: `4 / ${recipes.length}` },
      _ctx: baseMeta,
    });
  }

  // ───── Page 5: Pull Quote / Takeaway ─────
  if (recipes[4] === "M04") {
    pages.push({
      page: 5,
      recipe: "M04",
      role: "pull-quote",
      kicker: "QUOTE · 留给你",
      title: baseMeta.mother_formula || "有阅历的人在认真聊",
      subtitle: "M04 pull quote",
      lead: baseMeta.closing_patterns?.[0] || "在评论区告诉我你的答案。",
      body: "",
      meta: { page: `5 / ${recipes.length}` },
      _ctx: baseMeta,
    });
  } else if (recipes[4] === "S07") {
    pages.push({
      page: 5,
      recipe: "S07",
      role: "takeaway",
      kicker: "TAKEAWAY · 收束",
      title: "三个关键词",
      subtitle: "S07 takeaway ledger",
      lead: "",
      ledger: baseMeta.voice_keywords.slice(0, 3).map((kw, i) => ({
        n: String(i + 1).padStart(2, "0"),
        title: kw,
        desc: baseMeta.metaphor_library[i] || baseMeta.top_words[i] || "",
      })),
      meta: { page: `5 / ${recipes.length}` },
      _ctx: baseMeta,
    });
  }

  // ───── 公众号封面（仅当需要时生成，固定 .wide + .square） ─────
  pages.push({
    page: 6,
    role: "wechat-cover-pair",
    kicker: `${name.toUpperCase()} · WECHAT 21:9 + 1:1`,
    title: name,
    subtitle: `${baseMeta.style_name} · ${meta.date}`,
    lead: `${baseMeta.voice_keywords[0] || "本期要点"}`,
    body: "",
    meta: { page: `5 / 5`, date: meta.date, wide: "21:9", square: "1:1" },
    _ctx: baseMeta,
  });

  return pages;
}

/**
 * 写 pages.jsonl 到磁盘
 */
export function writePages(pages, outPath) {
  const lines = pages.map(p => JSON.stringify(p)).join("\n");
  fs.writeFileSync(outPath, lines + "\n", "utf-8");
  return outPath;
}