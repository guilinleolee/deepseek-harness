---
name: blogger-hologram-to-poster-cover-style-selector
description: 博主全息 9 维 → XHS 真人出镜爆款封面 · 8 问决策模块（V2.1 候选）
version: 0.1.0
status: DRAFT · 待 V2.1 集成
parent: blogger-hologram-to-poster V2.0
license: MIT
last_updated: 2026-07-20
---

# Cover Style Selector · V2.1 候选

> **模块定位**:在 blogger-hologram-to-poster V2.0 的 6 页 carousel 之外,补充"**XHS 真人出镜爆款封面**"专用决策模块。
> **对应模板库**:[`gpt-image-2-prompt-library/templates/xhs/`](../../../../skills/gpt-image-2-prompt-library/templates/xhs/)（V1.0,8 套风格）
> **对应色彩指南**:[`gpt-image-2-style-library/references/palette.md`](../../../../skills/gpt-image-2-style-library/references/palette.md)（V1.0）

---

## 与 V2.0 的关系

| 维度 | V2.0 现有 | V2.1 新增（本模块） |
|------|----------|---------------------|
| **输出物** | 6 页 carousel PNG + wechat-cover-pair | **单页 XHS 真人出镜爆款封面** PNG |
| **渲染管线** | guizang (Playwright + Chromium) | gpt-image-2 / hiapi MCP / APIMart |
| **比例** | 3:4（carousel）+ 21:9 + 1:1（wechat） | **3:4（硬约束）** |
| **主色** | 10 套调色板 + 第 9 维 design_style | **`#FDFFA7` 硬约束**（与 V2.0 kraft-paper / editorial / Swiss 解耦） |
| **人物处理** | 抠图+色块 + 文字排版 | **真人参考图**（必传）+ 抠图描边 |
| **决策输入** | 9 维博主全息 + matched_template + style_keywords | 9 维 + **8 问交互流程**（或博主全息自动推荐） |

**关系**:V2.0 carousel 适合**公众号图文 / 知识卡片 / 编辑风格**;V2.1 XHS 模块适合**真人出镜爆款 / 小红书种草 / 教程清单类**。两者互补,不替代。

---

## V2.1 模块组成

### 1. `cover-style-selector.mjs`（决策核心）

```javascript
// dragon-engine/skills/blogger-hologram-to-poster/pipeline/cover-style-selector.mjs
// 伪代码 V2.1 候选

import { readBloggerProfile } from './profile-loader.mjs';
import { QUESTION_BANK } from './cover-question-bank.mjs';
import { renderXHSTemplate } from './xhs-template-renderer.mjs';

/**
 * 8 问决策模块入口
 * @param {object} options
 * @param {string} options.blogger - 博主 ID（如 laoli_bro_2026）
 * @param {object} [options.preAnswers] - 用户已提供的答案（跳过对应问题）
 * @param {boolean} [options.autoRecommend] - 按博主全息 9 维自动推荐（无人交互）
 * @returns {Promise<{style: string, params: object, prompt: string}>}
 */
export async function selectCoverStyle({ blogger, preAnswers = {}, autoRecommend = false }) {
  const profile = await readBloggerProfile(blogger);

  // 1. 自动推荐模式：按博主 9 维启发式
  const answers = autoRecommend
    ? recommendFromProfile(profile)
    : await askUserSequentially(QUESTION_BANK, preAnswers);

  // 2. 套用所选风格模板
  const style = answers.style;
  const params = answers;

  // 3. 渲染最终 prompt
  const prompt = renderXHSTemplate(style, params, profile);

  return { style, params, prompt };
}

/**
 * 按博主 9 维自动推荐（无人交互场景）
 */
function recommendFromProfile(profile) {
  const { dim_6_high_freq, dim_7_style, dim_8_visual, design_style } = profile;

  // Q1: 选风格（按 dim_7 文风 + 设计风格）
  let style;
  if (design_style === 'xhs_atutun' || dim_7_style.includes('教程')) {
    style = 'xhs-checklist';        // 教程文风 → 清单风
  } else if (dim_7_style.includes('测评') || dim_7_style.includes('横评')) {
    style = 'xhs-review-rank';      // 测评文风 → 榜单风
  } else if (dim_7_style.includes('种草') || dim_7_style.includes('推荐')) {
    style = 'xhs-recommend';        // 种草文风 → 推荐风
  } else if (dim_7_style.includes('科普') || dim_7_style.includes('问答')) {
    style = 'xhs-qa-popular';       // 科普文风 → 问答风
  } else if (dim_7_style.includes('效率') || dim_7_style.includes('工作流')) {
    style = 'xhs-dark-workflow';    // 效率文风 → 黑底工作流风
  } else if (dim_6_high_freq.includes('入门') || dim_7_style.includes('搭建')) {
    style = 'xhs-collage-intro';    // 入门/搭建 → 贴纸拼贴
  } else if (dim_8_visual.mood === '强冲击' || dim_8_visual.mood === '方法论') {
    style = 'xhs-split-impact';     // 强冲击 → 巨字拆分
  } else {
    style = 'xhs-press-top';        // 默认：爆款大字压顶
  }

  // Q3-Q7: 从博主 9 维映射
  return {
    style,
    figure_1: profile.figure_1_url || null,  // 博主头像/参考图
    expression: mapExpression(dim_8_visual),
    extra_materials: profile.dim_8_extra_materials || 0,
    background: mapBackground(dim_8_visual),
    font_style: mapFontStyle(design_style),
    font_color: '#FDFFA7-default',          // 默认 #FDFFA7
    title: null                              // 由主 prompt 决定
  };
}
```

### 2. `cover-question-bank.mjs`（8 问题库）

```javascript
// 8 问 + 选项 + 跳步规则
export const QUESTION_BANK = [
  {
    id: 'style',
    label: '选择封面风格',
    options: [
      { id: 'xhs-press-top',     name: '爆款大字压顶风',     desc: '顶部超大标题，人物居中，强钩子标题' },
      { id: 'xhs-split-impact',  name: '巨字拆分冲击风',     desc: '2-4 词块铺满，概念/能力/方法论' },
      { id: 'xhs-qa-popular',    name: '小白科普问答风',     desc: '大问号 + 大白话，给小白讲清楚' },
      { id: 'xhs-checklist',     name: '教程清单风',         desc: '绿色勾选清单，部署/上手/全流程' },
      { id: 'xhs-review-rank',   name: '产品测评榜单风',     desc: '大数字 + 箭头 + 维度标签' },
      { id: 'xhs-recommend',     name: '种草推荐风',         desc: '点赞/推荐，emoji + 暖背景' },
      { id: 'xhs-collage-intro', name: '贴纸拼贴入门风',     desc: '小卡片拼贴，入门/搭建/组合' },
      { id: 'xhs-dark-workflow', name: '黑底效率工作流风',   desc: 'Logo 墙 + 清单 + 高饱和标题' }
    ],
    required: true,
    skip_when: pre => pre.style
  },
  {
    id: 'figure_1',
    label: '上传人物参考图',
    type: 'image_upload',
    required: true,
    skip_when: pre => pre.figure_1,
    notes: '必须上传；不提供默认人物。1 张人脸 或 2-3 张同一人物照'
  },
  {
    id: 'expression',
    label: '人物表情和动作',
    options: [
      { id: 'shock',         name: '张嘴震惊' },
      { id: 'thumb-up',      name: '双手点赞' },
      { id: 'point-title',   name: '指向标题' },
      { id: 'chin-puzzled',  name: '托腮疑惑' },
      { id: 'fist-confident',name: '举拳自信' },
      { id: 'open-explain',  name: '双手打开讲解' },
      { id: 'auto',          name: '交给模型决定' }
    ],
    skip_when: pre => pre.expression
  },
  {
    id: 'extra_materials',
    label: '额外素材图数量',
    options: [
      { id: '1',  name: '有 1 张素材图' },
      { id: '2',  name: '有 2 张素材图' },
      { id: '3+', name: '有 3 张及以上素材图' },
      { id: '0',  name: '没有素材图' }
    ],
    skip_when: pre => pre.extra_materials !== undefined
  },
  {
    id: 'background',
    label: '背景色调',
    options: [
      { id: 'warm-indoor',     name: '室内暖光背景' },
      { id: 'tech-dark',       name: '黑灰科技海报背景' },
      { id: 'tool-wall-dark',  name: '深色工具墙背景' },
      { id: 'blurred-software',name: '模糊软件界面背景' },
      { id: 'saturated-clash', name: '高饱和撞色背景' },
      { id: 'auto',            name: '交给模型决定' }
    ],
    skip_when: pre => pre.background
  },
  {
    id: 'font_style',
    label: '字体风格',
    options: [
      { id: 'variety-bold',    name: '综艺超粗黑体（默认）' },
      { id: 'comic-explosive', name: '漫画爆款标题字' },
      { id: 'round-bold',      name: '圆润粗黑体' },
      { id: 'tech-bold',       name: '科技感粗粗黑体' },
      { id: 'bold-plus-doodle',name: '粗标题+手写涂鸦小字' },
      { id: 'auto',            name: '交给模型决定' }
    ],
    skip_when: pre => pre.font_style
  },
  {
    id: 'font_color',
    label: '字体颜色效果',
    options: [
      { id: 'fdffa7-default',  name: '#FDFFA7 填充+粗黑描边（默认）' },
      { id: 'white-default',   name: '纯白填充+粗黑描边' },
      { id: 'mixed-yellow-white', name: '#FDFFA7/白色混排+粗黑描边' },
      { id: 'yellow-with-white-highlight', name: '#FDFFA7+白色高光+粗黑描边' },
      { id: 'dark-bg-yellow-keyword', name: '深底白字+#FDFFA7 关键词' },
      { id: 'auto',            name: '交给模型决定' }
    ],
    skip_when: pre => pre.font_color
  },
  {
    id: 'title',
    label: '封面标题候选',
    type: 'free_choice_among_candidates',
    candidates_count: 3,
    options_per_round: ['A', 'B', 'C', '重新生成'],
    required: true,
    skip_when: pre => pre.title
  }
];

export async function askUserSequentially(questionBank, preAnswers) {
  const answers = { ...preAnswers };
  for (const q of questionBank) {
    if (q.skip_when?.(answers)) continue;
    answers[q.id] = await askUserOneQuestion(q);  // agent/UI 单问
  }
  return answers;
}
```

### 3. `xhs-template-renderer.mjs`（模板渲染）

```javascript
// 调用 gpt-image-2-prompt-library 的 8 套模板
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

const TEMPLATE_DIR = '~/.claude/skills/gpt-image-2-prompt-library/templates/xhs/styles/';

export async function renderXHSTemplate(styleId, params, profile) {
  // 1. 加载风格模板
  const tplPath = join(TEMPLATE_DIR, `${styleId}.md`);
  const tpl = await readFile(tplPath, 'utf-8');

  // 2. 替换 L3 可执行 Prompt 中的占位符
  let prompt = tpl.match(/```([\s\S]*?)```/)?.[1] || '';  // 提取 code block
  prompt = prompt
    .replaceAll('[封面主标题]',         params.title || profile.dim_7_default_title || '默认标题')
    .replaceAll('[具体表情]',            params.expression ? EXPRESSION_MAP[params.expression] : '强烈表情')
    .replaceAll('[具体手势和身体姿态]',  params.expression ? GESTURE_MAP[params.expression] : '自然手势')
    .replaceAll('[背景描述]',            BG_MAP[params.background] || '主题相关场景')
    .replaceAll('[主题相关贴纸/emoji/箭头/问号]', '主题相关 emoji');

  // 3. 注入博主全息元数据（用于溯源）
  const meta = {
    blogger: profile.id,
    style_id: styleId,
    palette: '#FDFFA7',
    aspect_ratio: '3:4',
    prompt_length: prompt.length,
    ip_consent: profile.ip_consent_active ? 'yes' : 'expired',
    timestamp: new Date().toISOString()
  };

  // 4. 输出
  return {
    style: styleId,
    params,
    prompt,
    meta
  };
}

const EXPRESSION_MAP = {
  shock: '嘴巴张开，眼睛睁大，震惊表情',
  'thumb-up': '双手竖大拇指',
  'point-title': '一只手指向大字或清单',
  'chin-puzzled': '单手托腮，表情认真疑问',
  'fist-confident': '单手举拳或握拳',
  'open-explain': '双手在脸旁或胸前展开',
  auto: '由模型决定'
};

const GESTURE_MAP = {
  shock: '嘴巴张开，眼睛睁大，身体前倾',
  'thumb-up': '双手竖大拇指，肩膀打开',
  'point-title': '右手食指向上指，左手自然放',
  'chin-puzzled': '右手单手托腮，肘部支撑',
  'fist-confident': '右手举拳过肩，左手叉腰',
  'open-explain': '双手在胸前打开，掌心向外',
  auto: '由模型决定'
};

const BG_MAP = {
  'warm-indoor': '暖色调室内场景，书架或桌面',
  'tech-dark': '黑灰科技海报背景',
  'tool-wall-dark': '深色工具墙背景',
  'blurred-software': '模糊软件界面背景',
  'saturated-clash': '高饱和撞色背景',
  auto: '主题相关场景'
};
```

### 4. 与 V2.0 publisher 集成

V2.0 publisher.py 支持 batch 入表,本模块输出 PNG 后可复用：

```javascript
// to-xhs-publisher.mjs
import { exec } from 'node:child_process';

export async function publishToXHS(pngPath, meta) {
  const taskJsonl = formatTaskForPublisher(pngPath, meta);
  await fs.writeFile('tasks-xhs.jsonl', taskJsonl + '\n', { encoding: 'utf-8' });

  return new Promise((resolve, reject) => {
    exec('python scripts/publisher.py batch tasks-xhs.jsonl --platform xhs',
      { cwd: 'dragon-engine/skills/guizang-social-card-skill/' },
      (err, stdout) => {
        if (err) return reject(err);
        resolve({ success: true, stdout });
      }
    );
  });
}
```

---

## 自动推荐映射表（博主 9 维 → XHS 风格）

| 博主特征 | 推荐 XHS 风格 |
|---------|--------------|
| 设计风格 = `xhs_atutun` 或 文风含"教程" | `xhs-checklist` 教程清单 |
| 文风含"测评" / "横评" | `xhs-review-rank` 测评榜单 |
| 文风含"种草" / "推荐" / "私藏" | `xhs-recommend` 种草推荐 |
| 文风含"科普" / "问答" / "小白" | `xhs-qa-popular` 科普问答 |
| 文风含"效率" / "工作流" / "工具组合" | `xhs-dark-workflow` 黑底工作流 |
| 文风含"入门" / "搭建" / "组合" | `xhs-collage-intro` 贴纸拼贴 |
| 视觉情绪 = 强冲击 / 方法论 | `xhs-split-impact` 巨字拆分 |
| 默认（无匹配） | `xhs-press-top` 爆款大字压顶 |

---

## 触发场景

1. **35-02 / 35-06 输出小红书爆款封面** → 调本模块
2. **博主新入驻,设计风格 = xhs_atutun** → 自动套用本模块 8 问
3. **博客文章 → 多平台素材 pipeline** 中,小红书分支调本模块
4. **API 批量生成**:`autoRecommend: true`,无人交互

---

## V2.1 集成 checklist

- [ ] `cover-style-selector.mjs` 落盘（V2.0 基础上扩展）
- [ ] `cover-question-bank.mjs` 落盘
- [ ] `xhs-template-renderer.mjs` 落盘
- [ ] `to-xhs-publisher.mjs` 落盘
- [ ] 单元测试:8 风格 × 3 博主类型 = 24 个用例
- [ ] 端到端 dry-run:laoli_bro_2026 + design_style=xhs_atutun → PNG + tasks-xhs.jsonl
- [ ] 接入 35-06 V1.3 第 10 维 UGC 视频化(generative-media-skills/ugc-video-factory)

---

## 版本历史

- **V0.1.0 DRAFT** (2026-07-20) — 初版决策模块设计稿,从 XHS 8 套模板 + 8 问流程抽离