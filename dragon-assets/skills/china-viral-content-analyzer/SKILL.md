---
license: UNKNOWN
name: china-viral-content-analyzer
version: 1.0.0
description: |
  Use when the user uses /viral or /爆款分析 command, or needs to analyze viral content from Chinese platforms, research content trends, or find creative inspiration. Analyze historical viral content from platforms like Xiaohongshu, Douyin, Bilibili, Zhihu, WeChat Video, and WeChat Official Accounts to extract viral elements and generate detailed analysis reports.
author: 天龙引擎团队
created: 2026-02-26
category: workflow

triggers:
  - "用户提到「china-viral-content-analyzer 中国爆款内容分析」时"
---

# 国内平台爆款内容分析

## Overview

通过系统化分析国内各大内容平台的历史爆款内容，提取爆款要素（标题、封面、内容结构、话题标签、情绪价值等），生成可复用的爆款公式和创作建议。

## When to Use

### 触发条件

**使用Slash Command（推荐）：**
```
/viral 企业培训
/viral 职场成长
/爆款分析 个人提升
```

**自然语言触发：**
- "分析一下XX关键词的爆款内容"
- "帮我研究小红书/抖音上的爆款"
- "找一些关于XX的热门内容分析"
- "我想了解XX领域的爆款趋势"

### 适用场景

- 内容创作前的竞品分析
- 爆款内容要素研究
- 平台内容趋势调研
- 用户痛点挖掘
- 情绪价值分析

### 何时不使用

- 纯粹搜索技术问题（使用WebSearch即可）
- 分析国外平台内容
- 不需要详细分析的简单搜索

## Workflow

### 完整工作流程

```
1. 输入关键词
   ↓
2. 检查去重
   ↓
3. 搜索各平台（WebSearch）
   ↓
4. 浏览器提取内容（Playwright headless）
   ↓
5. 六维度分析
   ↓
6. 生成报告
   ↓
7. 保存文件
```

### 详细步骤

#### 步骤1：输入关键词
- 从slash命令或自然语言中提取关键词
- 示例：`/viral 企业培训` → 关键词 = "企业培训"

#### 步骤2：检查去重
```bash
# 检查 ~/viral-content-reports/ 目录
# 查找是否存在 [关键词].md 文件
# 如果存在，询问用户：覆盖 / 追加 / 取消
```

#### 步骤3：搜索各平台
```javascript
// 使用WebSearch搜索各平台
const platforms = [
  { name: '小红书', query: 'site:xiaohongshu.com "{keyword}" 爆款' },
  { name: '抖音', query: 'site:douyin.com "{keyword}" 热门' },
  { name: 'B站', query: 'site:bilibili.com "{keyword}" 播放量高' },
  { name: '知乎', query: 'site:zhihu.com "{keyword}" 高赞' },
  { name: '视频号', query: '"{keyword}" 视频号 爆款' },
  { name: '公众号', query: 'site:mp.weixin.qq.com "{keyword}"' }
];
```

#### 步骤4：浏览器提取内容
```javascript
// 使用Playwright（headless模式）访问链接
const { chromium } = require('playwright');
const browser = await chromium.launch({ headless: true });

// 提取：标题、封面图URL、点赞数、评论数、收藏数
// 截图保存封面图
```

#### 步骤5：六维度分析
参考 [references/analysis_framework.md](references/analysis_framework.md)

1. 标题分析：字数、关键词、情绪词、结构模式
2. 封面/视觉分析：视觉风格、文字信息量、色彩情绪
3. 内容结构分析：开头钩子、段落结构、结尾引导
4. 话题标签分析：标签数量、层级搭配、热门标签
5. 用户痛点/情绪价值分析：痛点类型、情绪价值层次
6. 数据表现分析：互动数据、传播深度

#### 步骤6：生成报告
使用 [assets/report_templates/viral_analysis_report.md](assets/report_templates/viral_analysis_report.md) 模板

#### 步骤7：保存文件
- 文件：`~/viral-content-reports/[关键词].md`
- 图片：`~/viral-content-reports/images/[关键词]/`

## Quick Reference

### 平台搜索策略速查

| 平台 | 搜索模式 | 用户特征 | 内容偏好 |
|------|---------|---------|---------|
| 小红书 | `site:xiaohongshu.com "{keyword}" 爆款` | 18-35岁女性为主 | 种草、教程、生活方式 |
| 抖音 | `site:douyin.com "{keyword}" 热门` | 全年龄段 | 娱乐、情感、实用技巧 |
| B站 | `site:bilibili.com "{keyword}" 播放量高` | Z世代 | 知识、娱乐、二次元 |
| 知乎 | `site:zhihu.com "{keyword}" 高赞` | 高学历群体 | 专业观点、深度分析 |
| 视频号 | `"{keyword}" 视频号 爆款` | 30+岁，微信生态 | 情感、职场、健康 |
| 公众号 | `site:mp.weixin.qq.com "{keyword}"` | 微信用户 | 深度文章、观点 |

详细策略见 [references/platform_strategies.md](references/platform_strategies.md)

### 标题模式速查

| 模式 | 示例 | 适用场景 |
|------|------|---------|
| 数字对比式 | 3个月减20斤，我只做对了这1件事 | 成果展示 |
| 痛点提问式 | 为什么你总是存不下钱？ | 痛点共鸣 |
| 利益承诺式 | 学会这3招，同事都羡慕你 | 干货分享 |
| 反常识式 | 我劝你千万不要...除非... | 好奇驱动 |
| 故事悬念式 | 那个月薪3万的95后，后来怎么样了？ | 故事讲述 |

更多模式见 [references/title_patterns.md](references/title_patterns.md)

### 分析框架速查

```
爆款度 = (痛点精准度 × 3) + (情绪强度 × 2) + (信息密度 × 1.5) + (视觉吸引力 × 1)

各平台公式：
- 小红书：视觉冲击(40%) + 实用价值(35%) + 情绪共鸣(25%)
- 抖音：前3秒钩子(50%) + 情绪张力(30%) + 节奏感(20%)
- B站：内容深度(40%) + 趣味性(30%) + 实用性(30%)
- 知乎：观点独特性(40%) + 逻辑严密性(35%) + 信息增量(25%)
```

详细框架见 [references/analysis_framework.md](references/analysis_framework.md)

## Output Format

### 报告文件

**位置：** `~/viral-content-reports/[关键词].md`

**内容结构：**
1. 执行摘要
2. 平台爆款概览
3. 爆款标题深度分析
4. 封面/视觉分析
5. 内容结构分析
6. 话题标签策略
7. 用户痛点与情绪价值
8. 平台差异化分析
9. 爆款公式总结
10. 创作建议清单

完整模板见 [assets/report_templates/viral_analysis_report.md](assets/report_templates/viral_analysis_report.md)

### 图片文件

**位置：** `~/viral-content-reports/images/[关键词]/`

**命名规则：**
- `[平台]-序号-封面.png`
- 示例：`小红书-01-封面.png`

## Common Mistakes

### 错误1：只搜索不提取
❌ 错误做法：仅依赖WebSearch的搜索结果摘要
✅ 正确做法：使用Playwright访问链接，提取完整内容

### 错误2：忽略去重检查
❌ 错误做法：直接覆盖已有报告
✅ 正确做法：先检查文件是否存在，询问用户处理方式

### 错误3：单一平台分析
❌ 错误做法：只分析一个平台
✅ 正确做法：分析6个平台，进行跨平台对比

### 错误4：只罗列不分析
❌ 错误做法：只列出爆款内容，不提取规律
✅ 正确做法：分析爆款要素，总结可复用公式

### 错误5：忽视视觉分析
❌ 错误做法：只分析文字内容
✅ 正确做法：截图封面图，进行视觉分析

## Tips

### 搜索效率
- 一次执行多个WebSearch，并行获取各平台结果
- 每个平台获取5-10个样本即可
- 优先选择点赞/收藏高的内容

### 分析质量
- 优先分析近1年的爆款（时效性）
- 关注数据异常值（特别高或特别低的）
- 提取具体话术和案例

### 报告实用性
- 提供"拿来即用"的标题公式
- 给出具体的创作清单
- 包含真实的案例截图

## Example Usage

```
用户：/viral 企业培训

Claude：
1. 检查到 ~/viral-content-reports/ 企业培训.md 不存在
2. 开始搜索各平台...
   - 小红书：找到8篇爆款
   - 抖音：找到6篇爆款
   - B站：找到5篇爆款
   - 知乎：找到4篇爆款
3. 使用Playwright提取内容...
4. 进行六维度分析...
5. 生成报告...
6. 报告已保存到 ~/viral-content-reports/企业培训.md
   封面图已保存到 ~/viral-content-reports/images/企业培训/

✅ 分析完成！发现3个核心洞察：
1. 企业培训爆款最关注"数字化转型"话题
2. 标题平均18字，数字词出现率高达60%
3. 情绪价值以"焦虑缓解"为主（占45%）
```

## References

- [平台搜索策略](references/platform_strategies.md) - 各平台详细搜索策略
- [分析框架](references/analysis_framework.md) - 六维度分析框架详解
- [标题模式库](references/title_patterns.md) - 爆款标题模式库
- [报告模板](assets/report_templates/viral_analysis_report.md) - 标准报告模板

## Dependencies

- **WebSearch** - 搜索各平台内容
- **Playwright** - 浏览器自动化提取内容
- **playwright-skill** - 使用现有skill的Playwright功能

#### Evolution Pattern (Maintenance)

To preserve custom improvements when a core skill is upgraded, avoid editing `SKILL.md` directly for individual modifications. Instead:

1. Create or update an `evolution.json` file in the skill's root directory.
2. Store modification suggestions, custom rules, or evolved logic there.
3. This ensures that your custom "evolutions" are preserved even if the base `SKILL.md` is replaced during an upgrade.
