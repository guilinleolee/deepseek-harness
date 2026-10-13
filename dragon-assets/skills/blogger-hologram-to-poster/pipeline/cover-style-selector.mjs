// cover-style-selector.mjs · XHS 真人出镜爆款封面风格决策
// 阶段 22 V2.1 · 2026-07-20
//
// 入口函数 selectCoverStyle() 提供两种模式：
//   1. 交互模式（默认）: 8 问决策流程，逐题让用户选
//   2. 自动模式（autoRecommend=true）: 按博主 9 维启发式推荐

import { askUserSequentially, QUESTION_BANK } from "./cover-question-bank.mjs";
import { renderXHSTemplate } from "./xhs-template-renderer.mjs";

/**
 * XHS 风格 ID 映射表（博主 8 维 → 推荐 XHS 风格）
 * 决策依据（按优先级）:
 *   1. design_style 显式指定（如 xhs_atutun）
 *   2. matched_template 关键词（知识区/旅行/商务/测评 等）
 *   3. dim_7_writing_style.style_name 关键词
 *   4. dim_8_ip_visual.spec.style_keywords 关键词
 *   5. 默认 fallback
 */
const RECOMMEND_RULES = [
  { style: "xhs-checklist",     match: p =>
      p.design_style === "xhs_atutun" ||
      matchAny(p, ["matched_template"], ["教程", "上手", "部署", "全流程", "知识区", "方法论"])
  },
  { style: "xhs-review-rank",   match: p =>
      matchAny(p, ["matched_template", "style_keywords"], ["测评", "横评", "对比", "评测", "商务"])
  },
  { style: "xhs-recommend",     match: p =>
      matchAny(p, ["matched_template", "style_keywords"], ["种草", "推荐", "私藏", "安利", "旅行", "生活方式"])
  },
  { style: "xhs-qa-popular",    match: p =>
      matchAny(p, ["matched_template", "style_keywords"], ["科普", "问答", "小白", "概念", "解释", "金融", "财经"])
  },
  { style: "xhs-dark-workflow", match: p =>
      matchAny(p, ["matched_template", "style_keywords"], ["效率", "工作流", "工具组合", "生产力", "商务"])
  },
  { style: "xhs-collage-intro", match: p =>
      matchAny(p, ["matched_template", "style_keywords"], ["入门", "搭建", "组合", "小队", "团队", "旅行", "户外"])
  },
  { style: "xhs-split-impact",  match: p =>
      matchAny(p, ["style_keywords"], ["方法论", "能力", "概念拆解", "强冲击"]) ||
      p.mood === "强冲击"
  },
  { style: "xhs-press-top",     match: () => true }  // fallback
];

/**
 * 在 profile 的指定字段路径上做关键词匹配
 * @param {object} profile
 * @param {string[]} paths 字段路径（相对 profile 顶层）
 * @param {string[]} keywords
 * @returns {boolean}
 */
function matchAny(profile, paths, keywords) {
  if (!profile) return false;
  for (const path of paths) {
    const value = resolvePath(profile, path);
    if (!value) continue;
    const text = (Array.isArray(value) ? value.join(" ") : String(value)).toLowerCase();
    if (keywords.some(k => text.includes(k.toLowerCase()))) return true;
  }
  return false;
}

function resolvePath(obj, path) {
  return path.split(".").reduce((o, k) => (o ? o[k] : undefined), obj);
}

/**
 * 按博主 9 维自动推荐（无人交互场景）
 * @param {object} profile 博主全息
 * @returns {object} 8 问答案
 */
export function recommendFromProfile(profile) {
  const p = profile || {};
  const matched = RECOMMEND_RULES.find(r => r.match(p));

  return {
    style:           matched.style,
    figure_1:        p.figure_1_url || null,
    expression:      "auto",
    extra_materials: "0",
    background:      "auto",
    font_style:      "variety-bold",
    font_color:      "fdffa7-default",
    title:           p.default_title || null,
    auto_recommended: true
  };
}

/**
 * XHS 风格决策入口
 * @param {object} options
 * @param {object} [options.profile] - 博主全息（autoRecommend 必填）
 * @param {object} [options.preAnswers] - 预填答案（跳过对应问题）
 * @param {boolean} [options.autoRecommend=false] - 自动推荐模式
 * @param {function} [options.askUser] - 自定义单问函数（默认用 inquirer 兼容接口）
 * @returns {Promise<{style: string, params: object, prompt: string, meta: object}>}
 */
export async function selectCoverStyle({
  profile = null,
  preAnswers = {},
  autoRecommend = false,
  askUser = null
} = {}) {
  // 1. 收集答案
  let answers;
  if (autoRecommend) {
    if (!profile) throw new Error("autoRecommend=true requires profile");
    answers = recommendFromProfile(profile);
  } else {
    answers = await askUserSequentially(QUESTION_BANK, preAnswers, askUser);
  }

  // 2. 校验：必填项
  if (!answers.style) throw new Error("风格未选择（Q1 必填）");
  if (!answers.figure_1) {
    if (autoRecommend && !profile?.figure_1_url) {
      throw new Error("自动推荐需要 profile.figure_1_url 或预填 answers.figure_1");
    }
    if (!autoRecommend) throw new Error("图 1 人物参考图必传（Q2 必填）");
  }
  if (!answers.title && !autoRecommend) {
    throw new Error("封面标题必填（Q8 必填）");
  }

  // 3. 套用模板生成 prompt
  const result = await renderXHSTemplate(answers.style, answers, profile || {});

  return {
    style: answers.style,
    params: answers,
    prompt: result.prompt,
    meta: result.meta
  };
}

// 暴露给测试和上层使用
export { RECOMMEND_RULES };