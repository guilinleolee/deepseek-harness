// xhs-template-renderer.mjs · XHS 8 套模板 → 最终 prompt
// 阶段 22 V2.1 · 2026-07-20
//
// 调用 gpt-image-2-prompt-library/templates/xhs/styles/<id>.md
// 提取 L3 可执行 Prompt 代码块 + 替换占位符 + 注入博主元数据

import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { homedir } from "node:os";

const TEMPLATE_DIR_CANDIDATES = [
  resolve(homedir(), ".claude/skills/gpt-image-2-prompt-library/templates/xhs/styles"),
  resolve(process.cwd(), "skills/gpt-image-2-prompt-library/templates/xhs/styles"),
  resolve(process.cwd(), "../skills/gpt-image-2-prompt-library/templates/xhs/styles"),
  resolve(process.cwd(), "../../skills/gpt-image-2-prompt-library/templates/xhs/styles")
];

async function findTemplateDir() {
  for (const dir of TEMPLATE_DIR_CANDIDATES) {
    if (existsSync(join(dir, "01-press-top.md"))) return dir;
  }
  throw new Error(`找不到 XHS 模板目录，尝试路径: ${TEMPLATE_DIR_CANDIDATES.join(", ")}`);
}

/**
 * 从风格 markdown 中提取 L3 可执行 prompt（第一个代码块）
 * @param {string} markdown
 * @returns {string}
 */
export function extractPromptBlock(markdown) {
  // 匹配 ``` 包裹的第一个代码块（greedy? lazy: 取最近 ```）
  const matches = [...markdown.matchAll(/```[a-zA-Z]*\n([\s\S]*?)\n```/g)];
  if (!matches.length) throw new Error("模板中未找到 prompt 代码块");
  return matches[0][1].trim();
}

/**
 * 替换占位符（支持 [占位符] 和 [占位符，例如：默认值] 两种格式）
 * @param {string} tpl
 * @param {object} params
 * @param {object} profile
 * @returns {string}
 */
export function substitutePlaceholders(tpl, params, profile) {
  const map = buildSubstitutionMap(params, profile);

  return tpl.replace(/\[([^\]]+)\]/g, (match, content) => {
    // 处理 "[占位符，例如：默认值]" 形式
    const key = content.split("，")[0].split(",")[0].trim();

    // 1. 先查主 map
    if (map[key] !== undefined) return map[key];
    if (map[content.trim()] !== undefined) return map[content.trim()];

    // 2. 查二级 sub-option map
    if (SUB_OPTION_MAP[key]) return SUB_OPTION_MAP[key](params);
    if (SUB_OPTION_MAP[content.trim()]) return SUB_OPTION_MAP[content.trim()](params);

    return match;
  });
}

const SUB_OPTION_MAP = {
  // —— 位置类 ——
  "左侧/右侧/中下方":                 p => resolvePositionLRC(p) || "中下方",
  "左侧/右侧":                       p => resolvePositionLRC(p, true) || "右侧",
  "左下/右下/中央":                   p => p.position_3way === "left-bottom" ? "左下"
                                              : p.position_3way === "right-bottom" ? "右下" : "中央",
  "左/右":                           p => p.position_lrc === "left" ? "左侧" : "右侧",
  "顶部/底部":                       p => p.position_vertical === "bottom" ? "底部" : "顶部",

  // —— 清单内容类 ——
  "清单1，例如：从 0 安装":           p => getListItem(p, 0),
  "清单2，例如：一键部署":           p => getListItem(p, 1),
  "清单3，例如：跑通第一个案例":      p => getListItem(p, 2),

  "标签1，例如：文科生也能懂":        p => getQALabel(p, 0),
  "标签2，例如：3 分钟看完":          p => getQALabel(p, 1),
  "标签3，例如：不需要任何基础":      p => getQALabel(p, 2),

  "卡片1，例如：Cursor 截图":         p => getCardItem(p, 0),
  "卡片2，例如：Claude Code logo":    p => getCardItem(p, 1),
  "卡片3，例如：终端命令截图":        p => getCardItem(p, 2),
  "卡片4，例如：人物头像贴纸":        p => getCardItem(p, 3),
  "卡片5，例如：流程图截图":          p => getCardItem(p, 4),

  "收益1，例如：每天省 2 小时":       p => getEfficiencyItem(p, 0),
  "收益2，例如：所有笔记自动归档":    p => getEfficiencyItem(p, 1),
  "收益3，例如：一键同步到多平台":    p => getEfficiencyItem(p, 2),

  // —— 多选项类（基于表情/动作/背景） ——
  "具体表情：张嘴震惊/认真测评/眉毛上扬":   p => pickFromExpression(p, "测评"),
  "具体表情：托腮疑惑/认真解释/微微睁大眼睛": p => pickFromExpression(p, "科普"),
  "具体表情：微笑推荐/双手点赞/认真安利":   p => pickFromExpression(p, "推荐"),
  "具体表情：自信得意/兴奋入门/认真推荐":   p => pickFromExpression(p, "入门"),
  "具体表情：张嘴兴奋/双手打开/惊讶推荐":   p => pickFromExpression(p, "效率"),

  "具体动作：食指指向清单/竖大拇指/手掌朝向标题": p => pickGesture(p, "tutorial"),
  "手部动作：单手托腮/手指轻点脸侧/指向上方标题":  p => pickGesture(p, "qa"),
  "具体动作：手指指向数字/手掌推向产品卡片/侧身看向榜单": p => pickGesture(p, "review"),
  "具体动作：单手举拳/手指向上/手掌托起小卡片":     p => pickGesture(p, "intro"),
  "具体动作：双手展开讲解/指向 Logo 墙/惊讶张手":   p => pickGesture(p, "workflow"),
  "双手指向上方/双手举起/双手打开":                p => pickGesture(p, "intro"),

  "背景描述，例如：浅色工作台/叠加贴纸的干净背景/室内一角": p => p.background || "浅色工作台",

  // —— 通用「软件截图/产品图/Logo」类 ——
  "软件界面/产品截图/教程结果图":           p => "教程结果图",
  "主题相关产品卡片/软件 Logo/工具图标":    p => "工具卡片",
  "主题相关工具图标/流程图标/头像贴纸":     p => "流程图标",
  "主题相关软件 Logo/工具界面/工作流卡片":  p => "工作流卡片",
  "主题相关 emoji/喇叭/键盘/闪电/工具图标": p => "闪电",

  // —— 复合文本 ——
  "底部强化短句，例如：跟着做，小白也能搞定": p => "跟着做，小白也能搞定",
  "推荐理由短句，例如：亲测好用":            p => "亲测好用",

  // —— 颜色选项 ——
  "紫色/#FDFFA7/白色":                p => "#FDFFA7",

  // —— press-top 副标题 ——
  "副标题":                           p => p.subtitle || "实操干货",

  // —— split-impact 词块 ——
  "原标题":                           p => p.title || "核心概念",
  "词块1":                            p => getTitleBlock(p, 0),
  "词块2":                            p => getTitleBlock(p, 1),
  "词块3":                            p => getTitleBlock(p, 2),
  "词块4":                            p => getTitleBlock(p, 3),
  "2/3/4":                            p => "3",
  "N, 2-4":                           p => "3",
  "具体表情 + 夸张动作":              p => pickGesture(p, "intro") || "双手打开"
};

function getTitleBlock(p, idx) {
  // 优先用 title_blocks 自定义,否则把 title 按字符切分
  if (Array.isArray(p.title_blocks) && p.title_blocks[idx]) return p.title_blocks[idx];
  const title = p.title || "核心概念";
  const len = title.length;
  if (len <= 4) return title;
  // 按 2-4 字拆分
  const parts = [];
  for (let i = 0; i < len; i += 2) parts.push(title.slice(i, i + 2));
  return parts[idx] || parts[parts.length - 1] || title;
}

function resolvePositionLRC(p, twoOnly = false) {
  const v = p.position_lrc;
  if (twoOnly) return v === "left" ? "左侧" : v === "right" ? "右侧" : null;
  return v === "left" ? "左侧" : v === "right" ? "右侧" : v === "center-bottom" ? "中下方" : null;
}

function getListItem(p, idx) {
  const map = {
    install:   ["一键安装", "环境配置", "跑通 Demo"],
    deploy:    ["一键部署", "自动更新", "监控告警"],
    tools:     ["工具选择", "组合配置", "跑通流程"],
    efficiency: ["省时省力", "自动归档", "一键同步"]
  };
  const items = map[p.list_topic] || map.install;
  return items[idx] || items[idx % items.length];
}

function getQALabel(p, idx) {
  const map = {
    beginner: ["小白也能懂", "3 分钟看完", "不需要基础"],
    ai:       ["AI 新趋势", "GPT 也能用", "免费体验"]
  };
  const labels = map[p.qa_labels] || map.beginner;
  return labels[idx] || labels[idx % labels.length];
}

function getCardItem(p, idx) {
  const map = {
    "ai-agents": ["ChatGPT", "Claude Code", "Cursor", "Replit", "v0.dev"],
    "dev-tools": ["VS Code", "Terminal", "Git", "Docker", "Postman"],
    "study":     ["Anki", "Notion", "Obsidian", "Roam", "Logseq"]
  };
  const items = map[p.card_topic] || map["ai-agents"];
  return items[idx] || items[idx % items.length];
}

function getEfficiencyItem(p, idx) {
  const map = {
    install:   ["从 0 安装", "一键配置", "跑通 Demo"],
    deploy:    ["部署上线", "自动同步", "监控告警"],
    tools:     ["自动选择", "组合跑通", "一键管理"],
    efficiency: ["每天省 2 小时", "所有笔记自动归档", "一键同步到多平台"]
  };
  const items = map[p.list_topic] || map.efficiency;
  return items[idx] || items[idx % items.length];
}

function pickFromExpression(p, topic) {
  // 根据 expression 选最匹配的描述
  const exp = p.expression || "auto";
  const map = {
    测评:   { shock: "张嘴震惊", "thumb-up": "认真测评", "point-title": "眉毛上扬认真测评", default: "认真测评" },
    科普:   { shock: "微微睁大眼睛", "chin-puzzled": "托腮疑惑认真解释", default: "托腮疑惑认真解释" },
    推荐:   { "thumb-up": "双手点赞微笑推荐", shock: "微笑推荐认真安利", default: "微笑推荐认真安利" },
    入门:   { "fist-confident": "自信得意兴奋入门", default: "兴奋入门认真推荐" },
    效率:   { shock: "张嘴兴奋惊讶推荐", default: "张嘴兴奋双手打开" }
  };
  const options = map[topic] || {};
  return options[exp] || options.default || "强烈表情";
}

function pickGesture(p, scene) {
  const exp = p.expression || "auto";
  const map = {
    tutorial:   { "point-title": "食指指向清单", "thumb-up": "竖大拇指", default: "手掌朝向标题" },
    qa:         { "chin-puzzled": "单手托腮", "point-title": "手指轻点脸侧", default: "指向上方标题" },
    review:     { shock: "手指指向数字", default: "手掌推向产品卡片" },
    intro:      { "fist-confident": "单手举拳", "open-explain": "双手打开讲解", default: "手掌托起小卡片" },
    workflow:   { shock: "张嘴兴奋双手打开", "open-explain": "双手展开讲解", default: "指向 Logo 墙惊讶张手" }
  };
  const options = map[scene] || {};
  return options[exp] || options.default || "自然手势";
}

function buildSubstitutionMap(params, profile) {
  return {
    // 标题
    "封面主标题":       params.title || profile.default_title || "默认标题",
    "封面标题":         params.title || profile.default_title || "默认标题",
    "封面标题前半":     splitTitle(params.title || profile.default_title || "默认标题").first,
    "封面标题后半":     splitTitle(params.title || profile.default_title || "默认标题").second,

    // 表情与动作
    "具体表情":         EXPRESSION_MAP[params.expression] || "强烈表情，眼神看向镜头",
    "具体动作":         EXPRESSION_MAP[params.expression] || "自然手势",
    "具体手势和身体姿态": GESTURE_MAP[params.expression] || "双手自然放于胸前",
    "具体表情：张嘴震惊/认真测评/眉毛上扬": EXPRESSION_MAP[params.expression] || "惊讶表情",

    // 背景
    "背景描述":         BG_MAP[params.background] || "主题相关的暖色调场景",
    "深色或中性背景描述": BG_MAP[params.background] || "深色街景",
    "深色/工具界面/模糊工作台": BG_MAP[params.background] || "深色工具墙",
    "深色街景":         "深色街景",
    "深色街景/暗色办公桌/模糊工作场景": "暗色办公桌",
    "黑灰科技海报/模糊软件界面/真实室内/参考素材延展背景": BG_MAP[params.background] || "黑灰科技海报",
    "温暖室内/书架/桌面/生活化场景": BG_MAP[params.background] || "暖色调书桌前",
    "背景描述，例如：暖色调书桌前/模糊软件界面/室内书架场景": BG_MAP[params.background] || "暖色调室内场景",
    "背景描述，例如：暖色调开发桌面/真实开发环境/软件界面截图": BG_MAP[params.background] || "真实开发环境",

    // 装饰
    "主题相关贴纸/emoji/箭头/问号": "主题相关 emoji",
    "主题相关 emoji": "主题相关 emoji",

    // 字体
    "字体风格":         FONT_MAP[params.font_style] || "综艺超粗黑体",
    "字体颜色":         COLOR_MAP[params.font_color] || "#FDFFA7",

    // 清单
    "清单1":             "从 0 开始",
    "清单2":             "一键跑通",
    "清单3":             "实测有效",

    // 卡片
    "卡片1":             "工具卡片 1",
    "卡片2":             "工具卡片 2",
    "卡片3":             "工具卡片 3",
    "卡片4":             "工具卡片 4",
    "卡片5":             "工具卡片 5",

    // 测评
    "测评维度/核心结论": "实测结论",
    "主题相关产品卡片/软件Logo/工具图标": "工具卡片",

    // 推荐
    "推荐理由短句，例如：亲测好用": "亲测好用",
    "主题相关 emoji，例如：笑脸、爱心、喇叭、耳机、星星": "笑脸、爱心、星星",

    // 工具 Logo 墙
    "主题相关软件Logo/工具界面/工作流卡片": "工具 Logo",
    "主题相关 emoji/喇叭/键盘/闪电/工具图标": "闪电"
  };
}

function splitTitle(title) {
  // 简单分割: 4-10 字标题按 "/" 或空格分割
  const parts = title.split(/[\/／\s]+/);
  if (parts.length >= 2) return { first: parts[0], second: parts.slice(1).join(" ") };
  if (title.length >= 8) {
    const mid = Math.ceil(title.length / 2);
    return { first: title.slice(0, mid), second: title.slice(mid) };
  }
  return { first: title, second: "" };
}

const EXPRESSION_MAP = {
  "shock":          "嘴巴张开，眼睛睁大，震惊表情",
  "thumb-up":       "双手竖大拇指，微笑推荐",
  "point-title":    "右手食指指向上方标题，眼神认真",
  "chin-puzzled":   "单手托腮，眉头微皱，认真疑问",
  "fist-confident": "右手举拳过肩，眼神坚定",
  "open-explain":   "双手在胸前打开，掌心向外",
  "auto":           "由模型决定"
};

const GESTURE_MAP = {
  "shock":          "身体前倾，双手张开在胸前",
  "thumb-up":       "双手竖大拇指，肩膀打开",
  "point-title":    "右手食指向上指，左手自然放",
  "chin-puzzled":   "右手单手托腮，肘部支撑",
  "fist-confident": "右手举拳过肩，左手叉腰",
  "open-explain":   "双手在胸前打开，掌心向外",
  "auto":           "由模型决定"
};

const BG_MAP = {
  "warm-indoor":      "暖色调室内场景，书架或桌面",
  "tech-dark":        "黑灰科技海报背景",
  "tool-wall-dark":   "深色工具墙背景",
  "blurred-software": "模糊软件界面背景",
  "saturated-clash":  "高饱和撞色背景",
  "auto":             "主题相关的暖色调场景"
};

const FONT_MAP = {
  "variety-bold":     "综艺感超粗黑体",
  "comic-explosive":  "漫画爆款标题字",
  "round-bold":       "圆润粗黑体",
  "tech-bold":        "科技感粗黑体",
  "bold-plus-doodle": "粗标题+手写涂鸦",
  "auto":             "综艺超粗黑体"
};

const COLOR_MAP = {
  "fdffa7-default":              "#FDFFA7",
  "white-default":               "#FFFFFF",
  "mixed-yellow-white":          "#FDFFA7 和白色混排",
  "yellow-with-white-highlight": "#FDFFA7 + 白色高光",
  "dark-bg-yellow-keyword":      "深底白字+#FDFFA7 关键词",
  "auto":                        "#FDFFA7"
};

/**
 * 渲染 XHS 模板 → 最终 prompt + 元数据
 * @param {string} styleId 风格 ID（如 "xhs-checklist"）
 * @param {object} params 8 问答案
 * @param {object} profile 博主全息（可空）
 * @returns {Promise<{prompt: string, meta: object}>}
 */
export async function renderXHSTemplate(styleId, params, profile) {
  const templateDir = await findTemplateDir();
  const styleNum = styleIdToNum(styleId);
  const tplPath = join(templateDir, `${styleNum}.md`);

  if (!existsSync(tplPath)) {
    throw new Error(`模板不存在: ${tplPath}`);
  }

  const markdown = await readFile(tplPath, "utf-8");
  const tpl = extractPromptBlock(markdown);
  const prompt = substitutePlaceholders(tpl, params, profile || {});

  const meta = {
    blogger:         profile?.id || "anonymous",
    style_id:        styleId,
    palette:         "#FDFFA7",
    aspect_ratio:    "3:4",
    prompt_length:   prompt.length,
    ip_consent:      profile?.ip_consent_active ? "yes" : "unknown",
    template_source: tplPath,
    timestamp:       new Date().toISOString()
  };

  return { prompt, meta };
}

function styleIdToNum(styleId) {
  // xhs-press-top → 01-press-top
  const map = {
    "xhs-press-top":     "01-press-top",
    "xhs-split-impact":  "02-split-impact",
    "xhs-qa-popular":    "03-qa-popular",
    "xhs-checklist":     "04-checklist",
    "xhs-review-rank":   "05-review-rank",
    "xhs-recommend":     "06-recommend",
    "xhs-collage-intro": "07-collage-intro",
    "xhs-dark-workflow": "08-dark-workflow"
  };
  if (!map[styleId]) throw new Error(`未知 XHS 风格: ${styleId}`);
  return map[styleId];
}