---
name: reference-creation-column-benchmark-repos
description: content-studio【创作】栏目对标调研核实的 GitHub 仓库事实（4个引用项目2个不存在），star 截至 2026-09-25
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_subagent_agent_c658ef03-823b-4729-942d-98e1dd7f8bf0
---

2026-09-25 经 GitHub API 核实的【创作】栏目提示词方案对标事实（star 截至 2026-09-25）：

**方案引用项目核验**：
- nhaouari/obsidian-textgenerator-plugin — 1987 星，MIT，2026-08 有推送，低频维护中。引用真实，保留
- 「BMO AI Content Studio」**不存在**；真实项目是 longy2k/obsidian-bmo-chatbot（531 星，MIT，2024-09 起停更一年+）
- Typefully — 闭源 SaaS 确认（GitHub org 仅 minimal-twitter 999 星、agent-skills 59 星等周边）；开源替代 coollabsio/shoutrrr（379 星，Apache-2.0，2026-06 创建，活跃）
- 「Markdown Editor Enhanced」**不存在有规模的同名项目**（同名最高 25 星）；疑似想引 Tencent/cherry-markdown（4880 星，active，license NOASSERTION）或 Vanessa219/vditor（11350 星，MIT，活跃，已从 b3log 迁移）

**8 功能域新核实仓库**：
- blader/humanizer — 51.8k 星，MIT，活跃。去 AI 味 prompt 方法论（正当改写，非 detector bypass），域 c 头部
- epoko77-ai/im-not-ai — 5.7k 星，MIT，活跃。韩语版 humanizer，证明方法论可本地化
- promptfoo/promptfoo — 25.4k 星，MIT；confident-ai/deepeval — 18.4k 星，Apache-2.0。均活跃；G-Eval rubric 打分参照
- konsheng/Sensitive-lexicon — 4159 星，MIT，2026-08 活跃。纯中文敏感词库可直接打包
- houbb/sensitive-word — 6063 星，Apache-2.0（Java DFA 框架，借设计不引代码）；广告法极限词无成熟独立词库（仅 0 星 skill dx2020z/ad-redline-guardian 可作规则清单参考）
- Ryze-AI-Adgent/open-seo-mcp-skills — 1488 星，MIT，极活跃。SEO+GEO 技能方法论文本
- hashtag 生成无头部项目（最高 <50 星），需自建 prompt
- Vinzent03/obsidian-git — 12k 星 MIT；saga-soft/novelWriter — 3136 星 GPL-3.0（原 vkbo），快照元数据设计参照
- iniwap/AIWriteX — 2022 星，Apache-2.0，极活跃，中文多平台 AI 写作头部对标
- ziguishian/xhs-visual-director-skill — 1366 星，MIT。小红书图文「视觉导演」skill
- harry0703/MoneyPrinterTurbo — 125.5k 星，MIT，活跃（短视频脚本结构参照）
- steven-tey/novel — 16.4k 星但 2025-01 起停更；GeekyWizKid/writing-helper — 645 星 MIT；theJayTea/WritingTools — 2458 星 GPL-3.0（改写菜单交互参照）
- 排除项：rudra496/StealthHumanizer（自称 bypass GPTZero/Turnitin，属 detector bypass 攻击工具，禁用）

**How to apply:** 评审/实现【创作】栏目时直接引用本结论；选题库侧事实见 [[reference-topic-library-benchmark-repos]]，项目背景见 [[project-content-studio-topic-library]]。
