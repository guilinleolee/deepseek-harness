// cover-question-bank.mjs · XHS 8 问题库
// 阶段 22 V2.1 · 2026-07-20
//
// 8 问决策：风格 / 人物 / 表情 / 素材 / 背景 / 字体 / 字色 / 标题
// 约束：一次只问一题，用户已提供则跳过。

/**
 * 8 问题库 + 选项 + 跳步规则
 */
export const QUESTION_BANK = [
  {
    id: "style",
    label: "选择封面风格",
    required: true,
    options: [
      { id: "xhs-press-top",     name: "爆款大字压顶风",     desc: "顶部超大标题，人物居中，强钩子" },
      { id: "xhs-split-impact",  name: "巨字拆分冲击风",     desc: "2-4 词块铺满，概念/能力/方法论" },
      { id: "xhs-qa-popular",    name: "小白科普问答风",     desc: "大问号 + 大白话，给小白讲清楚" },
      { id: "xhs-checklist",     name: "教程清单风",         desc: "绿色勾选清单，部署/上手/全流程" },
      { id: "xhs-review-rank",   name: "产品测评榜单风",     desc: "大数字 + 箭头 + 维度标签" },
      { id: "xhs-recommend",     name: "种草推荐风",         desc: "点赞/推荐，emoji + 暖背景" },
      { id: "xhs-collage-intro", name: "贴纸拼贴入门风",     desc: "小卡片拼贴，入门/搭建/组合" },
      { id: "xhs-dark-workflow", name: "黑底效率工作流风",   desc: "Logo 墙 + 清单 + 高饱和标题" }
    ],
    skip_when: pre => pre.style
  },
  {
    id: "figure_1",
    label: "上传人物参考图（图 1）",
    type: "image_upload",
    required: true,
    notes: "必传；不提供默认人物。可上传 1 张人脸照 或 2-3 张同一人物照保持一致性。",
    skip_when: pre => pre.figure_1
  },
  {
    id: "expression",
    label: "人物表情和动作",
    required: true,
    options: [
      { id: "shock",          name: "张嘴震惊",     desc: "测评/反差/发现" },
      { id: "thumb-up",       name: "双手点赞",     desc: "推荐/种草/公开私藏" },
      { id: "point-title",    name: "指向标题",     desc: "教程/认知" },
      { id: "chin-puzzled",   name: "托腮疑惑",     desc: "科普/问题钩子" },
      { id: "fist-confident", name: "举拳自信",     desc: "入门/搭建/行动感" },
      { id: "open-explain",   name: "双手打开讲解", desc: "分享方法" },
      { id: "auto",           name: "交给模型决定" }
    ],
    skip_when: pre => pre.expression
  },
  {
    id: "extra_materials",
    label: "额外素材图数量",
    required: true,
    options: [
      { id: "1",  name: "有 1 张素材图（软件截图/产品图/Logo）" },
      { id: "2",  name: "有 2 张素材图" },
      { id: "3+", name: "有 3 张及以上素材图" },
      { id: "0",  name: "没有素材图（让模型生成）" }
    ],
    skip_when: pre => pre.extra_materials !== undefined && pre.extra_materials !== null
  },
  {
    id: "background",
    label: "背景色调",
    required: true,
    options: [
      { id: "warm-indoor",      name: "室内暖光背景",       desc: "推荐/经验分享" },
      { id: "tech-dark",        name: "黑灰科技海报背景",   desc: "AI/工具/概念科普" },
      { id: "tool-wall-dark",   name: "深色工具墙背景",     desc: "效率流/工具组合" },
      { id: "blurred-software", name: "模糊软件界面背景",   desc: "产品截图作氛围" },
      { id: "saturated-clash",  name: "高饱和撞色背景",     desc: "爆款强钩子" },
      { id: "auto",             name: "交给模型决定" }
    ],
    skip_when: pre => pre.background
  },
  {
    id: "font_style",
    label: "字体风格",
    required: true,
    options: [
      { id: "variety-bold",     name: "综艺超粗黑体",       desc: "默认，最像高点击小红书" },
      { id: "comic-explosive",  name: "漫画爆款标题字",     desc: "震惊/测评/反差" },
      { id: "round-bold",       name: "圆润粗黑体",         desc: "种草/播客/亲切" },
      { id: "tech-bold",        name: "科技感粗黑体",       desc: "AI 工具/效率流" },
      { id: "bold-plus-doodle", name: "粗标题+手写涂鸦",   desc: "主标题粗 + 涂鸦小字" },
      { id: "auto",             name: "交给模型决定" }
    ],
    skip_when: pre => pre.font_style
  },
  {
    id: "font_color",
    label: "字体颜色效果",
    required: true,
    options: [
      { id: "fdffa7-default",             name: "#FDFFA7 填充+粗黑描边",         desc: "默认最强点击感" },
      { id: "white-default",              name: "纯白填充+粗黑描边",             desc: "深色背景更清晰" },
      { id: "mixed-yellow-white",         name: "#FDFFA7/白色混排+粗黑描边",    desc: "关键词用 #FDFFA7" },
      { id: "yellow-with-white-highlight",name: "#FDFFA7+白色高光+粗黑描边",    desc: "短视频爆款标题" },
      { id: "dark-bg-yellow-keyword",     name: "深底白字+#FDFFA7 关键词",      desc: "黑底工作流/测评" },
      { id: "auto",                       name: "交给模型决定" }
    ],
    skip_when: pre => pre.font_color
  },
  {
    id: "title",
    label: "封面标题",
    type: "free_choice_among_candidates",
    required: true,
    candidates_count: 3,
    notes: "主标题 4-10 字，强钩子优先；测评类突出数字；教程类突出低门槛。",
    skip_when: pre => pre.title
  }
];

/**
 * 二级子问题：覆盖 8 套模板的二级占位符（V2.2 新增）
 * - position_lrc: 人物位置 left/right/center-bottom（xhs-checklist 等用）
 * - position_vertical: 主标题位置 top/bottom（xhs-recommend 等用）
 * - position_3way: 3 选 1 位置（xhs-review-rank 的 左下/右下/中央）
 * - list_topic: 清单主题（教程安装/部署上线/工具流/效率收益）
 * - card_topic: 卡片主题（开发工具/AI 工具/教程组合）
 * - gesture_specific: 风格特化动作（与 expression 协同）
 * - mood_specific: 风格特化情绪（科普/教程/工具）
 */
export const SUB_QUESTION_BANK = [
  {
    id: "position_lrc",
    label: "人物水平/垂直位置",
    triggers_when: style => ["xhs-checklist", "xhs-review-rank"].includes(style),
    options: [
      { id: "left",        name: "左侧",     desc: "人物靠左，清单靠右" },
      { id: "right",       name: "右侧",     desc: "人物靠右，清单靠左" },
      { id: "center-bottom", name: "中下方", desc: "人物中下方，标题顶部" }
    ],
    default: "right",
    skip_when: pre => pre.position_lrc
  },
  {
    id: "position_vertical",
    label: "主标题位置",
    triggers_when: style => ["xhs-recommend", "xhs-press-top"].includes(style),
    options: [
      { id: "top",    name: "顶部", desc: "顶部大标题压画面" },
      { id: "bottom", name: "底部", desc: "底部标题 + 人物上方" }
    ],
    default: "top",
    skip_when: pre => pre.position_vertical
  },
  {
    id: "position_3way",
    label: "测评场景位置",
    triggers_when: style => style === "xhs-review-rank",
    options: [
      { id: "left-bottom",  name: "左下", desc: "人物左下，数字底部" },
      { id: "right-bottom", name: "右下", desc: "人物右下，数字底部" },
      { id: "center",       name: "中央", desc: "人物中央，强调动作" }
    ],
    default: "center",
    skip_when: pre => pre.position_3way
  },
  {
    id: "list_topic",
    label: "清单主题",
    triggers_when: style => ["xhs-checklist", "xhs-dark-workflow"].includes(style),
    options: [
      { id: "install",  name: "安装上手",  items: ["一键安装", "环境配置", "跑通 Demo"] },
      { id: "deploy",   name: "部署上线",  items: ["一键部署", "自动更新", "监控告警"] },
      { id: "tools",    name: "工具流",    items: ["工具选择", "组合配置", "跑通流程"] },
      { id: "efficiency", name: "效率收益", items: ["省时省力", "自动归档", "一键同步"] }
    ],
    default: "install",
    skip_when: pre => pre.list_topic
  },
  {
    id: "card_topic",
    label: "贴纸卡片主题",
    triggers_when: style => style === "xhs-collage-intro",
    options: [
      { id: "ai-agents",   name: "AI Agent 组合", items: ["ChatGPT", "Claude Code", "Cursor"] },
      { id: "dev-tools",   name: "开发工具",     items: ["VS Code", "Terminal", "Git"] },
      { id: "study",       name: "学习方法",     items: ["Anki", "Notion", "Obsidian"] },
      { id: "auto",        name: "自动（按博主）" }
    ],
    default: "ai-agents",
    skip_when: pre => pre.card_topic
  },
  {
    id: "qa_labels",
    label: "科普问答标签",
    triggers_when: style => style === "xhs-qa-popular",
    options: [
      { id: "beginner",   name: "小白友好",   labels: ["小白也能懂", "3 分钟看完", "不需要基础"] },
      { id: "ai",         name: "AI 工具",     labels: ["AI 新趋势", "GPT 也能用", "免费体验"] },
      { id: "auto",       name: "自动（按博主）" }
    ],
    default: "beginner",
    skip_when: pre => pre.qa_labels
  }
];

/**
 * 按已选风格获取需要回答的 sub-questions
 * @param {string} style 风格 ID
 * @returns {Array} 子问题列表
 */
export function getSubQuestionsForStyle(style) {
  return SUB_QUESTION_BANK.filter(q => !q.triggers_when || q.triggers_when(style));
}

/**
 * 顺序询问用户（一次一题，跳过已答；含二级子问题）
 * @param {Array} questionBank 问题库
 * @param {object} preAnswers 预填答案
 * @param {function} [customAsk] 自定义单问函数
 * @returns {Promise<object>} 完整答案（含 sub-answers）
 */
export async function askUserSequentially(questionBank, preAnswers = {}, customAsk = null) {
  const answers = { ...preAnswers };
  const ask = customAsk || defaultAsk;

  // 1. 主问题（Q1-Q8）
  for (const q of questionBank) {
    if (q.skip_when?.(answers)) continue;
    const promptText = formatQuestionPrompt(q);
    const answer = await ask(q, promptText, answers);
    answers[q.id] = answer;
  }

  // 2. 二级子问题（基于已选 style 触发）
  if (answers.style) {
    const subs = getSubQuestionsForStyle(answers.style);
    for (const q of subs) {
      if (q.skip_when?.(answers)) continue;
      const promptText = formatQuestionPrompt(q);
      const answer = await ask(q, promptText, answers);
      answers[q.id] = answer;
    }
  }

  return answers;
}

function formatQuestionPrompt(q) {
  let text = `\n【${q.label}】\n`;
  if (q.notes) text += q.notes + "\n";
  if (q.options) {
    q.options.forEach((opt, i) => {
      text += `  ${i + 1}. ${opt.name}${opt.desc ? " — " + opt.desc : ""}\n`;
    });
  }
  return text;
}

/**
 * 默认问询（CLI 占位实现；生产替换为 inquirer / UI / API）
 */
async function defaultAsk(question, promptText, _answers) {
  if (question.type === "image_upload") {
    throw new Error("图片上传需要自定义 askUser；预填 figure_1 跳过此问。");
  }
  if (question.type === "free_choice_among_candidates") {
    throw new Error(`自由候选需要自定义 askUser；预填 title 跳过此问。问题: ${question.label}`);
  }
  // 默认实现：打印 prompt，期望调用方通过 preAnswers 预填
  console.warn(`[XHS-DECISION] ${promptText}`);
  console.warn("[XHS-DECISION] 请通过 preAnswers 预填或实现自定义 askUser");
  return null;
}