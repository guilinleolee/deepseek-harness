// recipe-rules.mjs · 博主全息 → guizang 版式选择
// 阶段 19 V2.0 · 12 类版式（覆盖 28 个版本）
//
// 决策依据（按优先级）：
//   1. dim_7_writing_style.matched_template（如「知识区」→ Editorial M01/M07）
//   2. dim_8_ip_visual.spec.style_keywords + 风格家族（editorial/swiss）
//   3. 默认 fallback

/**
 * RECIPE_RULES — 12 类版式选择规则
 *  - matched_templates: 博主全息里 matched_template 字段的关键词
 *  - style_keywords: dim_8_ip_visual.spec.style_keywords 关键词
 *  - family: 'editorial' | 'swiss'
 *  - recipe: guizang 版式 ID (M01-M16 / S01-S12)
 *  - reason: 选择理由
 *  - weight: 匹配权重
 */
export const RECIPE_RULES = [
  // ───── Editorial 8 类 ─────
  { matched_templates: ["知识区", "知识", "科普", "教学", "教程"],
    family: "editorial", recipe: "M01", name: "Magazine Issue Cover",
    reason: "知识类博主通常需要杂志风封面", weight: 3 },
  { matched_templates: ["知识区", "总结", "年终", "回顾", "盘点"],
    family: "editorial", recipe: "M07", name: "Closing Note",
    reason: "年终总结/盘点需要 4-6 ledger items 收束", weight: 2 },
  { matched_templates: ["旅行", "户外", "生活方式"],
    family: "editorial", recipe: "M16", name: "Image-Led Cover",
    reason: "旅行/户外博主需要图主导的封面", weight: 3 },
  { matched_templates: ["文艺", "文化", "艺术", "设计", "读书"],
    family: "editorial", recipe: "M03", name: "Editorial Essay Split",
    reason: "文艺/文化博主需要 essay split 版式", weight: 2 },
  { matched_templates: ["情感", "故事", "叙事", "体验"],
    family: "editorial", recipe: "M04", name: "Pull Quote / Thesis",
    reason: "情感/叙事需要 pull quote 收束", weight: 2 },
  { matched_templates: ["职场", "方法论", "工具", "生产力"],
    family: "editorial", recipe: "M14", name: "Vertical Pipeline",
    reason: "职场/方法论博主适合纵向 pipeline", weight: 2 },
  { matched_templates: ["测评", "对比", "评测"],
    family: "editorial", recipe: "M15", name: "Before / After",
    reason: "测评博主适合 before/after 版式", weight: 2 },
  { matched_templates: ["清单", "购物", "种草"],
    family: "editorial", recipe: "M05", name: "Checklist / Buying Guide",
    reason: "清单/种草博主适合 checklist", weight: 2 },

  // ───── Swiss 4 类 ─────
  { matched_templates: ["商务", "企业", "工具", "测评", "方法论", "数码", "财经"],
    family: "swiss", recipe: "S01", name: "Accent Cover",
    reason: "商务/工具/财经博主适合 Swiss accent cover", weight: 3 },
  { matched_templates: ["数据", "报告", "研究"],
    family: "swiss", recipe: "S10", name: "H-Bar Chart",
    reason: "数据/报告博主适合 Swiss 数据图", weight: 3 },
  { matched_templates: ["警告", "避雷", "反诈", "新闻"],
    family: "swiss", recipe: "S05", name: "Trap / Warning Rows",
    reason: "警告类博主适合 Swiss S05", weight: 2 },
  { matched_templates: ["工作流", "架构", "系统"],
    family: "swiss", recipe: "S06", name: "Pipeline / Architecture",
    reason: "工作流/架构博主适合 Swiss S06", weight: 2 },
];

/**
 * select_recipe: 根据博主全息推断 guizang 版式
 * @param {object} profile - 9 维博主全息
 * @param {{ family: 'editorial'|'swiss' }} choice - 已选 theme（来自 palette-rules）
 * @returns {{ recipe: string, name: string, reason: string, source: string }}
 */
export function selectRecipe(profile, choice) {
  const matchedTemplate = (profile.matched_template || "").toLowerCase();
  const styleKeywords = (profile.dim_8_ip_visual?.spec?.style_keywords || []).map(s => s.toLowerCase());

  let best = null;

  for (const rule of RECIPE_RULES) {
    if (rule.family !== choice.family) continue; // 只匹配同 family

    // 计算 matched_template 关键词命中数
    let score = 0;
    for (const mt of rule.matched_templates) {
      if (matchedTemplate.includes(mt.toLowerCase())) score += rule.weight;
    }
    // style_keywords 命中（弱匹配）
    for (const sk of styleKeywords) {
      for (const mt of rule.matched_templates) {
        if (sk.includes(mt.toLowerCase())) score += 1;
      }
    }

    if (score > 0 && (!best || score > best.score)) {
      best = { ...rule, score, source: "matched_template" };
    }
  }

  if (!best) {
    // 默认 fallback
    if (choice.family === "swiss") {
      best = { recipe: "S01", name: "Accent Cover", family: "swiss",
               reason: "Swiss 默认封面", score: 0, source: "default" };
    } else {
      best = { recipe: "M01", name: "Magazine Issue Cover", family: "editorial",
               reason: "Editorial 默认封面", score: 0, source: "default" };
    }
  }

  delete best.score;
  return best;
}

/**
 * 为一篇 5-6 页 carousel 推荐一套版式组合
 * @returns {string[]} recipe IDs
 */
export function suggestCarousel(recipe) {
  if (recipe.family === "swiss") {
    // Swiss 5 页：S01 cover + S02 two signals + S03 data + S05 trap + S07 takeaway
    return ["S01", "S02", "S03", "S05", "S07"];
  }
  // Editorial 5 页：M01 cover + M03 essay + M07 closing + M14 pipeline + M04 pull quote
  return ["M01", "M03", "M07", "M14", "M04"];
}