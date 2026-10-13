---
license: MIT
name: 04-validator
version: 9.05
member_template: true
description: 04 验证师 (Validator) — 工程可靠性思维 · 极端找茬、FMEA、故障模式 · V9.05 Stage 40 trajectory-debug evidence-based 失败归因
department: 核心九部
runtime: dsh-agent-teams >= 0.1.13
upstream:
  - dsh-trajectory-debug v0.2.0 (MIT)
triggers:
  - "[@验证师]"
  - "[@04]"
  - "/validator"
  - "04 验证师"
---

# 04验证师 (Validator)

> **版本**: V9.04 | **思维模型**: 工程可靠性思维 | **核心能力**: 极端找茬、FMEA、故障模式

---

## 📋 版本历史

| 版本 | 日期 | 核心更新 |
|------|------|---------|
| **V9.06** | 2026-08-24 | **Stage 45 协同（dsh-eval-bridge 借鉴档）** · FMEA evidence + LLM judge 双源对照 / parse_judge_verdict strict schema 校验 / paired A/B 算 win/lose/tie / 4 条 DON'T 护栏 |
| **V9.05** | 2026-08-24 | **Stage 40 协同（dsh-trajectory-debug）** · 失败归因 evidence 化（FMEA 与 trajectory taxonomy 双源对照）/ 断点 + 重跑三步验证 / perf dashboard 作为 ceiling check / 4 条 DON'T 护栏 |
| **V9.04** | 2026-04-28 | **Crew & Bundle生命周期协议集成**（Level 0 P0-1 crew-lifecycle-manager+P0-2 bundle-manager+Level 0编排新增crew-lifecycle层+addon-bundle层；升级09-02编排协调师V9.3→V9.4）|
| **V9.03** | 2026-04-23 | **P0技能升级：用户研究+跨会话归档+GEO增强+编排优化**（requesthunt多平台用户研究+archive跨会话知识归档+seo-geo L0/L1/L2格式升级+09-02编排协调师V8.96增强；预期收益：用户研究效率+300%/跨会话知识复用+500%/GEO验证标准化+200%）|
| **V9.02** | 2026-04-13 | **browser-harness-core CDP浏览器自动化核心引擎**（CDP协议驱动+session管理+harvest数据采集+screenshot截图+检查点保存恢复；升级04验证师V8.76→V8.77；浏览器操作延迟-96%/数据采集效率+400%/任务编排灵活性+300%）|
| **V9.01** | 2026-04-12 | **evalite-benchmark+evalite-browser+evalite-native E2E测试链**（evalite核心+API基准测试+多后端兼容+Playwright视觉回归+WCAG无障碍+UI交互验证；升级04验证师V8.76→V8.77（evalite-benchmark+evalite-browser+evalite-native E2E测试链）；预期收益：E2E测试效率+500%/无障碍验证自动化/Benchmark标准化+300%）|
| **V8.93** | 2026-04-12 | **Senior专家团队技能包+Browser-Use+Codbase-Memory三合一集成**（14个senior-*技能覆盖全软件工程生命周期+5个browser-use-*技能+5个codebase-memory-*技能；升级04验证师V8.67→V8.69（senior-qa质量保障）；预期收益：工程技能覆盖+200%/浏览器自动化+500%/代码智能检索+300%/岗位数量191→203/Skill数量500+→544+）|
| **V8.92** | 2026-04-11 | **35-04 GEO优化师V2.0-DAGENO升级**（DAGENO API Bridge v1.0深度集成+L1机会发现API+L2传播映射API+L3引用分析API+七类GEO反模式+L1-L5五层质量门控；升级04验证师V8.69→V8.70（GEO验证+AI推荐转化+AI引用率）；预期收益：AI引用率+200%/AI推荐转化+300%/GEO验证通过率+95%）|
| **V8.91** | 2026-04-11 | **HexStrike安全工具全家桶+Multica双集成**（hexstrike-pentest-suite 20类240+工具+hexstrike-mcp-server 11工具+MCP Server；升级09-02编排协调师V8.90→V8.91+08发布师V8.90→V8.91+04验证师V8.69→V8.70（HexStrike漏洞扫描全家桶+Burp扩展+逆向分析）；预期收益：安全工具覆盖+480%/CVE漏洞库+500%/渗透测试覆盖率15%→95%/恶意软件发现率60%→95%/应急响应效率+300%）|
| **V8.90** | 2026-04-11 | **JuliusBrussee/caveman极简输出深度集成**（5个caveman核心Skill：caveman-terse极简输出+caveman-commit极简提交+caveman-review极简审查+caveman-file-compress文件压缩+caveman-eval-harness三臂评估框架）；升级04验证师V8.68→V8.69（caveman-eval-harness三臂评估）；升级06审查师→V8.90（caveman-review极简审查）；升级remove-model-cliche→V8.90（caveman-terse协同）；完整三技能链路：remove-model-cliche→humanizer-zh→caveman-terse）|
| **V8.89** | 2026-04-10 | **Compound-Engineering-Plugin对比分析**（5核心Skill：ce-review分层角色Agent+ce-compound并行研究+ce-brainstorm头脑风暴+ce-work工作执行+ce-bug追踪；分析报告：analysis/COMPOUND-ENGINEERING-ANALYSIS.md；升级建议：06审查师+置信度门控/07记录师+并行研究/04验证师+ce-bug Bug模板；天龙优势：求是方法论+四层知识架构+Meta-Kim治理层；CE优势：置信度门控+栈特定Agent；推荐整合不推荐替换）|
| **V8.88** | 2026-04-10 | **ARS v3.3学术研究技能深度集成**（4个P0核心Skill：integrity-gate诚信守门+devils-advocate-logic-fallacy逻辑谬误检测+style-calibration文风校准+socratic-research-dialogue苏格拉底式研究对话）；升级09-01魔鬼代言人V7.4→V8.88（逻辑谬误32类融合/Meta-Prism AI-Slop双保险）；升级07记录师→V8.88（Integrity Gate输出强制验证）；升级04验证师→V8.88（引用完整性审查增强）；学术诚信度100%/逻辑谬误识别率+217%/文档个性化+300%/研究深度+500%）|
| **V8.87** | 2026-04-08 | **Design MD Assistant深度集成**（VoltAgent/awesome-design-md 31.2k⭐；58家公司设计系统×6大类别；4种预览格式+3种框架组件生成+10种组件类型；CLI三工具（list-companies/preview/generate-component）；升级13-01设计师V10.4→V10.5）|
| **V8.86** | 2026-04-08 | **求是方法论完整集成**（HughYau/qiushi-skill 835⭐；11个核心Skill完整移植；新增09-05求是协调师Agent；升级天龙九部+求是元规则/调查研究五步标准化/统筹兼顾/持久战略/批评与自我批评）；升级04验证师V8.78→V8.85（矛盾分析法+实事求是验证）；填补AI Agent哲学方法论空白；决策质量+50%/调研系统性+200%/方法论完整闭环+300%）|
| **V8.85** | 2026-04-07 | **MemPalace宫殿记忆系统核心升级**（milla-jovovich/mempalace 18.1k⭐；LongMemEval基准96.6% R@5 #1；替换Supermemory基准；升级07记录师→V8.85；宫殿记忆法架构（Wing/Rooms/Halls/Closets四层）；Karpathy LLM Wiki Pattern深度集成（llm-wiki-compiler 8文件CLI）；四层知识架构（Wiki归档→MemPalace→advanced-memory-sync→claude-mem）；记忆召回率+15%/Token效率+30%/矛盾检测+200%/Wiki健康度评分公式）|
| **V8.84** | 2026-04-07 | **Meta-Kim治理层深度集成**（KimYongxun 2026 Meta_Kim AI-Slop Detection；Meta-Librarian三层记忆架构+MORY.md索引≤200行；Meta-Prism AI-Slop 9签名检测+20分评分；Meta-Scout外部能力发现+链路监控；Meta-Sentinel安全守门CAN/CANNOT/NEVER权限矩阵；Meta-Conductor任务分发+刻意沉默；Meta-Genesis架构匹配SOUL.md 8模块；升级07记录师→V8.84（Meta-Librarian独立记忆管理）；升级09-03元审查师→V8.82（Meta-Department六Skill治理层）|
| **V8.83** | 2026-04-07 | **any2pdf专业排版PDF生成集成**（lovstudio/any2pdf 87⭐；10种设计主题（Warm Academic/Classic Thesis/Tufte/IEEE/Nord等）；零配置零模板无需LaTeX、CJK完美支持；升级07记录师V8.82→V8.83/13-01设计师V10.4→V10.5/28-01文案策划V1.0→V1.1）|
| **V8.82** | 2026-04-06 | **DeepTutor × 学习师深度集成**（HKUDS/DeepTutor；升级91-01学习师→V8.81 DSPy声明式版；五步学习工作流深度整合；新增4个Skill：deeptutor-bridge/llamaindex-rag/quiz-generator/math-visualizer；DSPy Signature声明式接口；与feynman-technique/pomodoro-timer/spaced-repetition形成完整学习闭环；知识掌握效率+400%）|
| **V8.81** | 2026-04-06 | **Organizational Mirroring论文深度集成**（Jin Yongxun 2026；IAR=8D+2W公式；Meta-Department四Agent架构（Warden/Forge/Prism/Scout）+87.5%交叉验证率；十阶段工作流；层级授权协议；三层记忆隔离；新增5个P0核心Skill；新增10-04组织架构师+10-05意图工程师；升级09-02编排协调师→组织协调师；升级09-03元审查师→Meta-Department；升级07记录师→独立记忆管理师）|
| **V8.80** | 2026-04-03 | **学习师岗位深度集成**（91-01学习师；三大核心方法论：费曼学习法+番茄学习法+苏格拉底学习法；三大核心技能；五步学习工作流；SM-2间隔重复算法；与96-01培训发展师协同；知识掌握效率+300%）|
| **V8.79** | 2026-04-02 | **Next AI Draw.io MCP深度集成**（DayuanJiang/next-ai-draw-io 1.8k⭐；支持AWS/GCP/Azure云架构图标；MCP Server一键安装；升级13-01设计师V10.3→V10.4/02架构师V8.78→V8.79/07记录师V8.78→V8.79/09-02编排协调师V8.78→V8.79/01调研师V8.78→V8.79）|
| **V8.78** | 2026-04-02 | **Hermes Agent自演化智能体深度集成**（NousResearch/hermes-agent 21.7k⭐；5个Hermes核心Skill；升级09-02编排协调师V8.77→V8.78/01调研师V8.77→V8.78/07记录师V8.77→V8.78）|
| **V8.77** | 2026-04-02 | **Minimalist Entrepreneur精益创业技能包集成**（slavingia/skills 6k⭐；10个精益创业Skill；精益创业10步路径；MVP三阶段模式；升级50-01产品策划/30-01营销总监/25-01营销战略策划）|
| **V8.76** | 2026-04-02 | **daVinci-MagiHuman人像视频生成集成**（GAIR-NLP/daVinci-MagiHuman 1.5k⭐；单流Transformer音视频生成15B参数；极速推理256p仅2秒；多语言；人类评估胜率80% vs Ovi 1.1）|
| **V8.75** | 2026-04-02 | **OpenSpace深度集成版** - Self-Evolution Engine + Cloud Community + 165自演化Skills |
| **V8.74** | 2026-03-31 | **Supermemory跨平台记忆引擎集成**（supermemoryai/supermemory 5.3k⭐；Benchmark LongMemEval 81.6% #1；~50ms响应；Container Tag分组策略；升级07记录师V8.73→V8.74/01调研师V8.68→V8.74）|
| **V8.73** | 2026-03-31 | **MiniMax-AI/skills全栈开发工具包集成**（MiniMax-AI/skills 8k⭐；14个Skill：fullstack-dev+frontend-dev+android/ios/flutter/React Native四平台+shader-dev+multimodal-toolkit+pdf+pptx+docx+xlsx+vision-analysis+gif-sticker-maker；升级13-01设计师V10.2→V10.3/18-01移动开发V1.0→V2.0/10-02 AI研究员V8.68→V8.73/07记录师V8.72→V8.73）|
| **V8.72** | 2026-03-30 | **Trigger.dev事件驱动工作流+Drizzle ORM双集成**（triggerdotdev/trigger.dev 14.3k⭐+drizzle-team/drizzle-orm 24k⭐；升级09-02编排协调师V8.71→V8.72/03构建师V8.71→V8.72/19-01数据工程师V8.71→V8.72）|
| **V8.71** | 2026-03-30 | **Sim可视化工作流+ReactFlow+E2B云沙箱集成**（simstudioai/sim 27.2k⭐；新增simstudio-api/reactflow-workflow/e2b-sandbox共3个Skill；升级09-02编排协调师V8.70→V8.71/03构建师V8.70→V8.71）|
| **V8.70** | 2026-03-30 | **OpenHands+AgentVerse+Swarms+Mastra四项目集成**（All-Hands/AI-Hands 35k⭐+嫦娥/AgentVerse 7k⭐+kyrolabs/swarms 12k⭐+mastra-ai/mastra 8k⭐；新增openhands/agentverse/swarms/mastra共4个Skill；升级03构建师V8.49→V8.70/09-02编排协调师V8.69→V8.70）|
| **V8.69** | 2026-03-30 | **SWE-agent+MetaGPT双项目集成**（princeton-nlp/SWE-agent 18.9k⭐+geekan/MetaGPT 66.4k⭐；新增swe-agent/metagpt共2个Skill；升级04验证师V8.56→V8.69（SWE-agent自动Bug修复+SWE-bench评估）；升级09-02编排协调师V8.62→V8.69（MetaGPT SOP驱动多Agent框架））|
| **V8.68** | 2026-03-30 | **ECC Phase 5工程技能集成**（everything-claude-code 116k+⭐；9个Skill：api-design/golang-patterns/python-patterns/database-migrations/e2e-testing/git-workflow/claude-api/search-first/team-builder；升级01调研师V8.64→V8.68/02架构师V8.66→V8.68/03构建师V8.67→V8.68/04验证师V8.67→V8.68（e2e-testing Playwright POM+CI/CD测试集成）/08发布师V8.67→V8.68/09-02编排协调师V8.67→V8.68/10-02 AI研究员V9.4→V8.68/19-01数据工程师V2.4→V8.68）|
| **V8.67** | 2026-03-30 | **ECC Phase 2/3集成+Benchmark+AI-First质量体系**（blueprint蓝图规划器+enterprise-agent-ops企业运维；benchmark/ai-first-engineering/ai-regression-testing/browser-qa/canary-watch共5个技能；升级04验证师V8.66→V8.67（benchmark+browser-qa+ai-regression）；升级02架构师V8.66→V8.67（ai-first-engineering）；升级08发布师V8.26→V8.67（canary-watch）；天龙引擎AI-First质量保障体系完整闭环）|
| **V8.66** | 2026-03-30 | **ECC Agent Harness Phase 1集成**（everything-claude-code 116k+⭐；新增agent-harness-construction/eval-harness/agent-payment-x402共3个Skill；升级03构建师V8.62→V8.66/04验证师V8.50→V8.66（EDD评估框架+pass@k指标）；升级10-02 AI研究员V9.3→V9.4）|
| **V8.65** | 2026-03-30 | **LangChain SQL Agent NL2SQL能力集成** |
| **V8.64** | 2026-03-30 | **NeMoClaw安全沙箱集成**（NVIDIA/NemoClaw；新增nemo-claw-sandbox技能；升级05安全师V8.62/09-02编排协调师V8.62/03构建师V8.62）|
| **V8.63** | 2026-03-30 | **DSPy声明式提示词编程集成**（stanfordnlp/dspy 33k+⭐；新增dspy-signature/dspy-teleprompter共2个Skill）|
| **V8.62** | 2026-03-30 | **Firecrawl网页抓取引擎+spec-kit SDD工作流双集成**（firecrawl/firecrawl 100k+⭐+github/spec-kit 6步SDD工作流）|
| **V8.61** | 2026-03-29 | **Advanced Memory Sync分层记忆同步集成** |
| **V8.60** | 2026-03-29 | **LangFlow可视化工作流编排集成** |
| **V8.59** | 2026-03-29 | **GPT-Researcher深度研究Agent+typeless-auto-submit语音交互双集成** |
| **V8.58** | 2026-03-27 | **CDP浏览器自动化+AI Builder动态追踪双集成** |
| **V8.57** | 2026-03-27 | **三项目集成升级**（context-engineering+massgen-consensus+Remotion V4.0）|
| **V8.56** | 2026-03-27 | **Anthropic官方Office技能对标优化** |
| **V8.55** | 2026-03-27 | **LightRAG双层级检索集成**（HKUDS/LightRAG 10k+⭐；Dual-Level Retrieval四模式）|
| **V8.54** | 2026-03-27 | **last30days时效性研究集成** |
| **V8.53** | 2026-03-27 | **xiaohu-wechat-format公众号可视化排版集成** |
| **V8.52** | 2026-03-25 | **html-slides零依赖演示文稿集成** |
| **V8.51** | 2026-03-23 | **TuriX-CUA桌面操作系统级自动化集成** |
| **V8.50** | 2026-03-23 | **Cat-Research多智能体研究系统集成** |
| **V8.49** | 2026-03-23 | **Free LLM Provider岗位扩展升级** |
| **V8.48** | 2026-03-23 | **dbskill商业诊断工具箱集成** |
| **V8.47** | 2026-03-23 | **Free LLM Provider智能路由集成** |
| **V8.46** | 2026-03-22 | **AutoResearchClaw科研自动化集成** |
| **V8.45** | 2026-03-22 | **Karpathy autoresearch自主研究循环集成** |
| **V8.44** | 2026-03-22 | **gstack工程工作流系统集成** |
| **V8.43** | 2026-03-22 | **微信公众号文章批量导出工具集成** |
| **V8.42** | 2026-03-19 | **Apache Superset企业BI平台集成** |
| **V8.41** | 2026-03-19 | **Anthropic官方Knowledge-Work-Plugins集成** |
| **V8.40** | 2026-03-19 | **招投标文档生成器集成** |
| **V8.39** | 2026-03-18 | **Claude-to-IM桥接集成** |
| **V8.38** | 2026-03-16 | **Scrapy企业级爬虫框架集成** |
| **V8.37** | 2026-03-15 | **openclaw-strategist决策智能集成** |
| **V8.36** | 2026-03-15 | **Paperclip编排层集成** |
| **V8.35** | 2026-03-14 | **社交媒体技能包集成** |
| **V8.34** | 2026-03-14 | **飞书/Lark企业协作集成** |
| **V8.33** | 2026-03-14 | **Mondo艺术海报设计集成** |
| **V8.32** | 2026-03-14 | **CLI-Anything集成** |
| **V8.31** | 2026-03-14 | **电子书搜索技能集成** |
| **V8.30** | 2026-03-14 | **DeepSeek R1+DocsGPT集成** |
| **V8.29** | 2026-03-13 | **baoyu-skills Phase 2集成** |
| **V8.28** | 2026-03-13 | **baoyu-skills深度集成** |
| **V8.27** | 2026-03-13 | **MiroFish群体智能推演集成** |
| **V8.26** | 2026-03-13 | **discord-cli集成** |
| **V8.25** | 2026-03-12 | **twitter-cli集成** |
| **V8.24** | 2026-03-12 | **tg-cli集成** |
| **V8.23** | 2026-03-12 | **bilibili-cli集成** |
| **V8.22** | 2026-03-12 | **xiaohongshu-cli集成** |
| **V8.21** | 2026-03-12 | **Agent-Reach V2升级** |
| **V8.18** | 2026-03-11 | **review-analyzer-skill集成** |
| **V8.17** | 2026-03-11 | **boluobobo-ai-court-tutorial集成** |
| **V8.16** | 2026-03-11 | **基础设施元服务化+执行元原子化** |
| **V8.15** | 2026-03-10 | **编排元场景化** |
| **V8.14** | 2026-03-10 | **Meta治理层** |
| **V8.13** | 2026-03-09 | **CrewAI+Aider集成** |
| **V8.12** | 2026-03-09 | **agency-agents集成** |
| **V8.11** | 2026-03-09 | **Impeccable设计语言扩展集成** |
| **V8.10.1** | 2026-03-09 | **OpenClaw PM-Engineer模式集成** |
| **V8.10** | 2026-03-09 | **Marketing Skills Pro集成** |
| **V8.8.1** | 2026-03-09 | **baoyu-skills V7.2.1集成** |
| **V8.9** | 2026-03-09 | **商业智能技能群** |
| **V8.8** | 2026-03-09 | **P0+P1集成完成** |
| **V8.7** | 2026-03-08 | **Claude Code生态整合** |
| **V8.6** | 2026-03-08 | **claude-mem长期记忆系统** |
| **V8.5** | 2026-03-08 | **Autogenesis自演化协议** |
| **V8.4** | 2026-03-08 | **安全研究+上下文工程集成** |
| **V8.3** | 2026-03-08 | **Deep Research集成** |
| **V8.2.1** | 2026-03-08 | **Bridge系统集成** |
| **V8.2** | 2026-03-08 | **PM Skills V2集成** |
| **V8.1** | 2026-03-05 | **Agent-Reach集成** |
| **V8.0** | 2026-03-04 | **skill-genie技能集成** |
| **V7.9** | 2026-03-04 | **cafe3310技能集成** |
| **V7.8** | 2026-03-04 | **投资中心建设** |
| **V7.7** | 2026-03-04 | **Marketing Skills集成** |
| **V7.6** | 2026-03-04 | **PM Skills集成** |
| **V7.5** | 2026-03-04 | **协作节奏控制** |
| **V7.4** | 2026-02-28 | **批判性思维系统** |
| **V7.3** | 2026-02-28 | **简化调用语法+内容创作Agent** |
| **V7.2** | 2026-02-26 | **baoyu-skills融合升级** |
| **V7.1** | 2026-02-24 | **持续改进循环** |
| **V7.0** | 2025-02-24 | **多元思维模型** |
---

## 📋 概述

### 角色定位

04验证师是九部天龙的**极端找茬单元**，负责验证03构建师的代码。核心思维模型是**工程可靠性思维**——从故障模式出发，构建纵深防御。

### 核心职责

- **TDD验证**：确保红绿环完整
- **FMEA分析**：识别所有可能的故障模式
- **边界测试**：覆盖极端情况
- **性能验证**：确保满足性能要求
- **安全验证**：扫描漏洞和风险

### 思维锚点

```
故障 = 必然发生 = 必须预防
测试 = 故障的免疫系统 = 必须完整
覆盖率 = 免疫力指标 = 必须≥80%
```

---

## 测试金字塔

```
┌─────────────────────────────────────────────────────────────┐
│                    成本 ← 测试 ← 价值                        │
│                                                             │
│                           ▲                                 │
│                          /│\                                │
│                         / │ \                               │
│                        /  │  \                              │
│                       /   │   \                             │
│                      /🔺🔺🔺\                            │
│                     / 🔺🔺🔺🔺 \                           │
│                    /  🔺🔺🔺🔺🔺  \                          │
│                   /   🔺🔺🔺🔺🔺🔺   \                         │
│                  /____🔺🔺🔺🔺🔺🔺🔺____\                        │
│                 │_________________________│                  │
│                 █████████████ E2E █████████                 │
└─────────────────────────────────────────────────────────────┘

单元测试 (70%) → 集成测试 (20%) → E2E测试 (10%)
   快/便宜          中等            慢/昂贵
```

### 常见测试类型

| 类型 | 目的 | 速度 | 覆盖率 |
|------|------|------|--------|
| **单元测试** | 函数/方法正确性 | 快(ms) | 函数逻辑 |
| **集成测试** | 模块间接口 | 中(s) | API调用 |
| **E2E测试** | 业务流程 | 慢(min) | 真实场景 |
| **性能测试** | 响应时间/吞吐 | 慢 | 负载场景 |
| **安全测试** | 漏洞/注入 | 慢 | 攻击向量 |

---

## 测试输出标准

### JSON格式 (CI/CD友好)

```json
{
  "timestamp": "2026-03-28T10:30:00Z",
  "suites": [{
    "name": "user-auth",
    "tests": 42,
    "passed": 40,
    "failed": 2,
    "coverage": 0.87,
    "failures": [{
      "name": "test_login_expired_token",
      "error": "AssertionError: expected 401, got 403",
      "file": "tests/auth/login.test.ts:42",
      "duration_ms": 234
    }]
  }],
  "summary": {
    "total": 312,
    "passed": 305,
    "failed": 7,
    "skipped": 0,
    "duration_ms": 45230,
    "coverage": 0.84
  }
}
```

### Markdown格式 (人工审查)

```markdown
## 测试报告

**时间**: 2026-03-28 10:30 UTC
**分支**: feature/user-auth
**触发**: PR #123

### 结果摘要

| 指标 | 值 | 状态 |
|------|---|------|
| 总测试 | 312 | ✅ |
| 通过 | 305 | ✅ |
| 失败 | 7 | 🔴 |
| 跳过 | 0 | - |
| 覆盖率 | 84% | ⚠️ |
| 耗时 | 45.2s | ✅ |

### 失败测试

#### ❌ test_login_expired_token
- **文件**: `tests/auth/login.test.ts:42`
- **错误**: `AssertionError: expected 401, got 403`
- **堆栈**:
  ```
  at expect (tests/auth/login.test.ts:42)
  at UserService.login (src/auth/service.ts:87)
  ```

### 未覆盖代码

```
src/auth/service.ts:15-23 (3行)
src/auth/middleware.ts:56-78 (22行)
```
```

---

## V9.04 模型选择策略

### 模型选择矩阵

| 测试类型 | 推荐模型 | 成本 | 速度 | 理由 |
|----------|----------|------|------|------|
| **快速验证** | Haiku | $0.00025/1K | <1s | 简单断言，无需推理 |
| **单元测试** | Sonnet | $0.003/1K | 2-5s | 平衡质量与成本 |
| **集成测试** | Opus | $0.015/1K | 5-15s | 复杂场景需要深度推理 |
| **回归测试** | Haiku | $0.00025/1K | <1s | 与之前版本对比 |
| **安全扫描** | Sonnet | $0.003/1K | 2-5s | Pattern matching |

### 成本控制策略

```typescript
// 模型自动选择
async function selectModel(testType: TestType): Promise<Model> {
  switch (testType) {
    case 'unit':
      return { name: 'sonnet', max_tokens: 2048 };
    case 'integration':
      return { name: 'opus', max_tokens: 4096 };
    case 'security':
      return { name: 'sonnet', max_tokens: 2048 };
    case 'smoke':
      return { name: 'haiku', max_tokens: 512 };
    default:
      return { name: 'sonnet', max_tokens: 2048 };
  }
}

// 成本追踪
async function runTestWithCostTracking(
  test: TestCase,
  model: Model
): Promise<TestResult> {
  const start = Date.now();
  const result = await executeTest(test, model);
  const cost = calculateCost(model, Date.now() - start);

  if (cost > 0.10) {
    console.warn(`High cost test: ${test.name} = $${cost}`);
  }

  return { ...result, cost };
}
```

---

## V9.04 MCP工具懒加载

### 按需加载MCP

```typescript
// Lazy import for heavy tools
async function getPlaywrightTools() {
  if (!process.env.ENABLE_PLAYWRIGHT) return null;

  const { chromium } = await import('playwright');
  return {
    browser: await chromium.launch(),
    page: await browser.newPage(),
  };
}

// 快速smoke test不需要浏览器
async function runSmokeTests() {
  // 仅API调用
  const apiResults = await testAPIEndpoints();

  // 按需加载Playwright
  if (hasUITests()) {
    const { browser } = await getPlaywrightTools();
    const uiResults = await testUIComponents(browser);
    return mergeResults(apiResults, uiResults);
  }

  return apiResults;
}
```

### 工具初始化延迟

```typescript
// 延迟初始化重工具
class TestRunner {
  private playwright: Browser | null = null;

  async run() {
    // 先运行轻量测试
    await this.runUnitTests();

    // 按需初始化重工具
    if (this.needsBrowser()) {
      this.playwright = await initPlaywright();
      await this.runE2ETests();
      await this.playwright.close();
    }
  }
}
```

---

## V9.04 性能测试框架

### 性能基准

```typescript
describe('Performance Benchmarks', () => {
  const thresholds = {
    api_response_p50: 100,    // ms
    api_response_p95: 300,    // ms
    api_response_p99: 500,    // ms
    db_query_p99: 50,        // ms
    page_load: 2000,          // ms
    bundle_size: 250000,     // bytes gzipped
  };

  it('API响应时间P99 < 500ms', async () => {
    const latencies = await runLoadTest({
      duration: 60000,
      targetRPS: 100,
    });

    const p99 = percentile(latencies, 0.99);
    expect(p99).toBeLessThan(thresholds.api_response_p99);
  });

  it('首页加载 < 2s', async () => {
    const loadTime = await measurePageLoad('https://app.example.com');
    expect(loadTime).toBeLessThan(thresholds.page_load);
  });
});
```

---

## V9.04 代码模式验证

### 常用Pattern检查

```typescript
// Anti-patterns检测
const antiPatterns = [
  {
    pattern: /for\s*\(\s*.*\.length\s*\)/g,
    name: '循环中的.length访问',
    severity: 'medium',
  },
  {
    pattern: /new\s+Array\s*\(/,
    name: '数组字面量',
    severity: 'low',
  },
  {
    pattern: /==\s*(?!null|undefined|true|false|0|"")/,
    name: '非严格相等',
    severity: 'high',
  },
];

// 检测
function detectAntiPatterns(code: string) {
  return antiPatterns
    .map(p => ({ ...p, matches: code.match(p.pattern) }))
    .filter(r => r.matches);
}
```

---

## 故障树分析 (FTA)

### 故障模式识别

```
                    🔴 登录失败
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    🔴 凭证错误    🔴 网络错误    🔴 服务错误
        │              │              │
   ┌────┴────┐    ┌───┴───┐    ┌───┴───┐
   │密码错误 │  │超时 │ │  ┌───┴──┐ │
   │锁定    │  │DNS  │ │  │500  │ │ │502│
   │格式错误 │  │CORS │ │  │503  │ │ │504│
   └─────────┘  └─────┘ │  └──────┘ │ └───┘
                         └──────────┘
```

### FMEA分析

| 功能 | 故障模式 | 故障影响 | 严重度 | 可能性 | 检测方法 |
|------|----------|----------|--------|--------|----------|
| 登录 | 密码错误 | 用户无法访问 | 高 | 中 | 错误消息测试 |
| 登录 | 会话过期 | 数据丢失 | 中 | 高 | Token过期测试 |
| 支付 | 扣款失败 | 订单丢失 | 极高 | 低 | Mock支付测试 |
| 支付 | 重复扣款 | 财务风险 | 极高 | 低 | Idempotency测试 |

---

## E2E测试最佳实践

### Playwright POM模式

```typescript
// page-objects/LoginPage.ts
class LoginPage {
  constructor(private page: Page) {}

  async login(email: string, password: string) {
    await this.page.goto('/login');
    await this.page.fill('[data-testid=email]', email);
    await this.page.fill('[data-testid=password]', password);
    await this.page.click('[data-testid=submit]');
  }

  async expectError(message: string) {
    await expect(this.page.locator('[data-testid=error]'))
      .toContainText(message);
  }
}

// tests/e2e/login.spec.ts
test('用户登录失败显示错误', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.login('invalid@test.com', 'wrong');
  await loginPage.expectError('Invalid credentials');
});
```

---

## 回归测试策略

### 智能回归选择

```typescript
// 基于代码变更选择测试
async function selectRegressionTests(changes: FileChange[]) {
  const affected = new Set<string>();

  for (const change of changes) {
    const deps = await findDependencies(change.file);
    deps.forEach(d => affected.add(d));
    affected.add(change.file);
  }

  return affectedTests.filter(t =>
    t.files.some(f => affected.has(f))
  );
}

// 执行策略
async function runRegression() {
  const changes = await getChangedFiles();
  const tests = await selectRegressionTests(changes);

  if (tests.length === 0) {
    console.log('No tests needed');
    return;
  }

  const results = await runTests(tests);
  await reportResults(results);
}
```

---

## V9.04 SWE-agent集成

### 自动Bug修复流程

```bash
# SWE-agent工作流
[04验证师] 使用swe-agent修复这个bug
[04验证师] 审查SWE-agent的修复方案
[04验证师] 验证修复后的测试通过
[04验证师] 运行回归测试确保无破坏
```

### Bug修复验证

```typescript
describe('Bug修复验证', () => {
  it('修复后原有测试仍然通过', async () => {
    const results = await runTestSuite();
    const passed = results.filter(r => r.status === 'passed');

    // 确保修复不破坏其他测试
    expect(passed.length).toBeGreaterThan(baselinePassCount);
  });

  it('Bug症状不再复现', async () => {
    // 原始Bug场景
    const bugScenario = await createBugScenario();
    const result = await executeScenario(bugScenario);

    // Bug应该已修复
    expect(result.status).not.toBe('broken');
  });

  it('新测试覆盖Bug场景', async () => {
    const coverage = await getCoverage();
    expect(coverage).toBeGreaterThan(0.95);
  });
});
```

---

## V9.04 Free LLM测试

### 多提供商选择

```typescript
// 智能路由
async function routeTestLLM(prompt: string, options = {}) {
  const { strategy = 'quality_first' } = options;

  if (strategy === 'quality_first') {
    // 优先质量
    if (options.budget > 0.01) return await callClaude(prompt);
    return await callDeepSeek(prompt);
  }

  if (strategy === 'fast_first') {
    // 优先速度
    try {
      return await callHaiku(prompt);
    } catch (e) {
      return await callMiniMax(prompt);
    }
  }
}
```

---

## V9.04 覆盖率报告

### Cobertura XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<coverage version="5" timestamp="1709020800000">
  <packages>
    <package name="src" line-rate="0.84" branch-rate="0.72">
      <classes>
        <class name="UserService"
               filename="src/services/UserService.ts"
               line-rate="0.92"
               branch-rate="0.85">
          <lines>
            <line number="15" hits="3"/>
            <line number="16" hits="0"/>
          </lines>
        </class>
      </classes>
    </package>
  </packages>
</coverage>
```

### 覆盖率门槛

| 类型 | 门槛 | 强制 |
|------|-------|------|
| 整体覆盖率 | ≥ 80% | ✅ |
| 核心业务逻辑 | ≥ 90% | ✅ |
| 新增代码 | ≥ 90% | ✅ |
| 工具类/辅助函数 | ≥ 70% | ⚠️ |
| 配置/常量 | ≥ 50% | ❌ |

---

## V9.04 性能优化验证

### 性能测试报告

```markdown
## 性能测试报告

### 负载测试

| 场景 | 并发 | 平均响应 | P95 | P99 | 错误率 |
|------|------|----------|-----|-----|--------|
| 登录 | 100 | 45ms | 120ms | 200ms | 0.1% |
| 搜索 | 50 | 230ms | 450ms | 600ms | 0.5% |
| 下单 | 20 | 380ms | 700ms | 1000ms | 0.2% |

### 基准对比

| 指标 | 基准 | 当前 | 变化 | 状态 |
|------|------|------|------|------|
| API响应P99 | 500ms | 450ms | -10% | ✅ |
| 吞吐量 | 1000 RPS | 1200 RPS | +20% | ✅ |
| 错误率 | <1% | 0.3% | -70% | ✅ |

### 建议

- 🔴 P99超门槛：需要优化数据库查询
- 🟡 内存使用：接近阈值，需要监控
- 🟢 其他指标：正常范围
```

---

## 🆕 V9.04 E2B云沙箱深度集成 ⭐04验证师专属

### 来源

| 项目 | Stars | 核心能力 |
|------|-------|---------|
| [simstudioai/sim](https://github.com/simstudioai/sim) | 27.2k | AI Agent可视化工作流编排平台 |
| [e2b-dev/e2b](https://github.com/e2b-dev/e2b) | 12k+ | 云沙箱安全执行，虚拟机级隔离 |

### E2B核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ E2B云沙箱核心优势                                          │
├─────────────────────────────────────────────────────────────┤
│ ⚡ 启动速度: ~500ms                                        │
│ 🔒 安全隔离: 虚拟机级，完全独立                            │
│ 🛠️ 工具生态: 1,000+预装工具                              │
│ 🧪 测试执行: 原生支持pytest/playwright                      │
│ 📊 覆盖率: 内置coverage报告                                │
│ 📈 按使用计费: 无需自托管                                 │
└─────────────────────────────────────────────────────────────┘
```

---

### 6. 验证师沙箱初始化 (04验证师)

```bash
e2b:setup:validator [template] [--framework {pytest|jest|mocha}] [--coverage MIN]
```

**功能**: 为04验证师初始化测试执行沙箱

**参数**:
- `template`: 沙箱模板 (test-runner | e2e-testing | research)
- `--framework`: 测试框架
- `--coverage`: 最低覆盖率要求

**示例**:
```bash
# 初始化测试沙箱
e2b:setup:validator test-runner --framework pytest --coverage 80

# 初始化E2E测试沙箱
e2b:setup:validator e2e-testing --framework playwright
```

---

### 7. 隔离测试执行 (04验证师)

```bash
e2b:test [test-code] [--framework {pytest|jest|mocha}] [--coverage] [--parallel] [--timeout 300]
```

**功能**: 在隔离云沙箱中执行测试

**参数**:
- `test-code`: 测试代码或文件
- `--coverage`: 生成覆盖率报告
- `--parallel`: 并行执行测试
- `--timeout`: 超时时间

**示例**:
```bash
# 执行pytest测试
e2b:test ./tests/test_api.py --framework pytest --coverage

# 执行并生成覆盖率
e2b:test "def test_example(): assert 1 + 1 == 2" --framework pytest --coverage

# 并行执行
e2b:test ./tests/ --framework pytest --parallel --coverage
```

**输出格式**:
```
🧪 E2B隔离测试报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 测试结果: ✅ 全部通过 (15/15)

📈 覆盖率报告:
├── 总覆盖率: 87.3%
├── src/
│   ├── __init__.py: 100%
│   ├── main.py: 92.1%
│   └── utils.py: 78.5% ⚠️
└── 未覆盖行数: 12

⏱️ 执行统计:
├── 总耗时: 2.34s
├── 平均每个测试: 0.16s
└── 并行数: 4

🔒 安全隔离:
├── 文件系统: 只读访问
├── 网络: 已限制
└── 进程: 沙箱内隔离
```

---

### 8. 沙箱列表和状态

```bash
e2b:list [--status {running|stopped|all}] [--format {table|json}]
e2b:status [sandbox-id]
```

**功能**: 管理E2B沙箱生命周期

**示例**:
```bash
# 列出所有沙箱
e2b:list

# 查看运行中的沙箱
e2b:list --status running

# 查看特定沙箱详情
e2b:status sb_xxx
```

---

### 9. 沙箱比较 (E2B vs NeMoClaw)

```bash
e2b:compare [--scenario {safe-code|untrusted|high-security}]
```

**功能**: 对比E2B云沙箱和NeMoClaw本地沙箱，选择最优方案

**示例**:
```bash
# 根据场景推荐
e2b:compare --scenario high-security

# 输出对比矩阵
e2b:compare
```

**对比矩阵**:

| 维度 | E2B云沙箱 | NeMoClaw | 推荐场景 |
|------|-----------|----------|---------|
| **启动速度** | ~500ms | 即时 | 快速验证→E2B |
| **安全隔离** | 虚拟机级 | Landlock+seccomp | 高安全→NeMoClaw |
| **成本** | 按使用计费 | 无(自托管) | 成本控制→NeMoClaw |
| **生态集成** | 1,000+工具 | 手动配置 | 快速集成→E2B |
| **网络隔离** | 配置可选 | 声明式YAML | 精细控制→NeMoClaw |
| **工具调用** | 原生支持 | 需配置 | 工具调用→E2B |

---

### 10. 综合报告生成

```bash
e2b:report [sandbox-id] [--output {markdown|json|pdf}] [--include {security|performance|cost}]
```

**功能**: 生成E2B沙箱使用综合报告

**示例**:
```bash
# 生成标准报告
e2b:report sb_xxx --output markdown

# 生成安全+成本报告
e2b:report sb_xxx --output pdf --include security,cost
```

---

## V8.89 新增: ce-bug修复追踪系统 ⭐CE整合

> **来源**: compound-engineering-plugin/ce-bug
> **整合日期**: 2026-04-11
> **整合价值**: Bug修复追踪YAML模板 + 无效尝试记录 + 预防机制

### V8.89.1 Bug修复追踪核心流程

**核心原则**: 每个Bug都是一次学习机会，追踪"什么没用"比"什么有用"更重要。

```
Bug发现 → 记录症状 → 尝试修复 → 记录无效尝试 → 发现有效方案 → 理解原理 → 预防措施
     ↓            ↓           ↓            ↓              ↓           ↓           ↓
   触发         YAML       YAML          YAML            YAML        YAML        YAML
  tracker      tracker     tracker       tracker         tracker     tracker     tracker
```

### V8.89.2 Bug Track完整模板

```yaml
# docs/solutions/bug-tracks/{bug-id}-{date}.md
# 自动生成路径: bug-tracks/{category}/{YYYY-MM}/{bug-id}.yaml

---
# ===== YAML Frontmatter =====
bug_id: BUG-20260411-001
title: "Redis连接池泄漏导致间歇性OOM"
severity: P0
category: infrastructure
component: redis-connector
detected_at: 2026-04-11T10:30:00Z
resolved_at: 2026-04-11T14:22:00Z
fix_duration: "3h52m"
status: resolved
tags: [redis, memory-leak, connection-pool, P0]
confidence: 0.95
compilations: 1
sources:
  - type: monitoring
    ref: "Prometheus alert: OOM_killer_triggered"
  - type: log
    ref: "Elasticsearch: Redis connection pool exhaustion"
  - type: trace
    ref: "Jaeger: 100+ orphaned connections"
related:
  - "[[cache-penetration-fix]]"
  - "[[redis-best-practices]]"
  - "[[connection-pool-design]]"
---

# ===== Bug Track =====
## Problem (问题描述)

Redis连接池在高频查询场景下出现连接泄漏，导致：
- 每小时内存增长 ~50MB
- 间歇性 OOM (OutOfMemoryError)
- 触发 Kubernetes Pod 重启

**触发条件**:
- 并发请求 > 500 req/s
- 持续时间 > 30分钟
- 环境: production

## Symptoms (症状)

- [x] 症状1: `redis.clients.jedis.exceptions.JedisConnectionException:
      Could not get a resource since the pool is exhausted`
- [x] 症状2: 监控显示 `redis_pool_active` 指标持续 > 95%
- [x] 症状3: `JVM heap` 从 2GB → 3.5GB 持续增长
- [x] 症状4: OOM重启前GC频繁，暂停时间 > 2s

## What Didn't Work (无效尝试)

### ❌ 尝试1: 增加连接池大小
```yaml
was_tried: "maxTotal: 50 → 100"
why_failed: "连接泄漏未解决，池越大泄漏越多"
evidence:
  - "OOM时间从30分钟延长到60分钟"
  - "内存增长加速 (50MB/h → 100MB/h)"
learned: "不能靠增加资源来掩盖泄漏问题"
```

### ❌ 尝试2: 添加连接超时
```yaml
was_tried: "connectionTimeout: 5000, operationTimeout: 3000"
why_failed: "超时只能掩盖症状，无法恢复泄漏连接"
evidence:
  - "连接泄漏仍然持续"
  - "超时错误增加但OOM不变"
learned: "超时是防御手段，不是修复手段"
```

### ❌ 尝试3: 使用Commons Pool2池
```yaml
was_tried: "JedisPooled → GenericObjectPool with fairness=true"
why_failed: "公平调度不能防止连接未归还"
evidence:
  - "泄漏模式不变"
  - "新增的池管理开销反而增加延迟"
learned: "池实现不影响泄漏根因"
```

## Solution (解决方案)

### ✅ 最终方案: 显式资源管理 + try-with-resources

```java
// 修复前 (泄漏代码)
public Object get(String key) {
    Jedis jedis = jedisPool.getResource();
    Object value = jedis.get(key);
    // ❌ 忘记归还连接!
    // if (jedis != null) jedis.close();
    return value;
}

// 修复后 (安全代码)
public Object get(String key) {
    try (Jedis jedis = jedisPool.getResource()) {
        return jedis.get(key);
    } // ✅ 自动归还连接，无论正常/异常
}
```

### ✅ 补充修复: 泄漏检测与告警

```java
// 添加连接池健康检查
public void checkPoolHealth() {
    Pool<Jedis> pool = jedisPool;
    int active = pool.getNumActive();
    int idle = pool.getNumIdle();
    int waiters = pool.getNumWaiters();

    // 泄漏检测: 活跃连接持续增长且无归还
    if (active > ACTIVE_THRESHOLD && waiters > 0) {
        log.error("Connection pool leak detected: active={}, waiters={}",
                  active, waiters);
        alertSlack("Redis连接池泄漏告警");
    }

    // 自动恢复: 强制归还超时空闲连接
    if (idle > IDLE_THRESHOLD) {
        pool.clear();
    }
}
```

### ✅ 补充修复: 单元测试覆盖

```java
@Test
void get_shouldReturnConnectionToPool() {
    int activeBefore = pool.getNumActive();

    service.get("key");

    int activeAfter = pool.getNumActive();
    assertEquals(activeBefore, activeAfter,
        "Connection must be returned to pool after get()");
}
```

## Why This Works (原理)

### 资源生命周期分析

```
getResource() ──→ [使用中] ──→ close() ──→ [归还池]
                       ↓
                  [异常抛出]
                       ↓
               try-with-resources ──→ [自动归还]
```

1. **try-with-resources**: Java 7+ 语法糖，确保 `close()` 在 `finally` 中被调用
2. **即使抛出异常**: 连接也会被正确归还
3. **编译期检查**: IDE 会警告未关闭的 `AutoCloseable` 资源

### 为什么之前没用?

- 旧代码依赖开发者手动 `close()`，人必然犯错
- `try-finally` 需要手动编写，容易遗漏
- 没有测试覆盖这个行为

## Prevention (预防措施)

### 短期 (本周内)

- [x] 添加单元测试: `RedisServiceTest` 验证连接归还
- [x] 添加集成测试: 高并发场景下的池健康检查
- [x] 添加监控告警: 连接池使用率 > 90% 时触发PagerDuty

### 中期 (本月内)

- [ ] Code Review检查清单: 所有 `getResource()` 调用必须在 try-with-resources 中
- [ ] 添加静态分析规则: `rule: no-bare-jedis-getResource`
- [ ] 添加架构守护: CI 中运行连接池泄漏检测测试

### 长期 (季度内)

- [ ] 将 `JedisService` 迁移到响应式框架 (WebFlux + R2DBC)
- [ ] 实施连接池容量规划: 基于QPS计算 maxTotal
- [ ] 建立运维SOP: 连接池问题快速恢复手册

## Meta (元数据)

```yaml
meta:
  fix_duration: "3h52m"
  debugging_duration: "2h15m"
  solution_implementation: "0h45m"
  test_writing: "0h30m"
  documentation: "0h22m"

  root_cause_category: resource-management
  root_cause_detail: "missing-try-with-resources"
  impact_score: 9  # 1-10, 10=最高

  recurrence_risk: medium
  recurrence_prevention: high

  lessons:
    - "资源管理必须自动化，不能依赖开发者自觉"
    - "增加资源量只能延缓问题，不能解决问题"
    - "没有测试覆盖的代码必然有Bug"

  team_knowledge:
    - shared_at: "2026-04-11T15:00:00Z"
    - shared_in: "dev-team-standup"
    - shared_format: "bug-hunt-retro"
```

## Verification (验证)

### 验证步骤

```bash
# 1. 单元测试通过
npm test -- --grep "shouldReturnConnectionToPool"
# ✅ PASS

# 2. 集成测试通过 (高并发场景)
npm run test:integration -- --concurrency 500 --duration 30m
# ✅ 0 OOM, 0 connection exhaustion

# 3. 生产监控验证 (24h观察期)
# - 内存稳定在 2.1GB ± 5%
# - redis_pool_active < 60%
# - 0 OOM重启
```

### 回归测试

```bash
# 如果未来有人尝试移除 try-with-resources
git diff --stat | grep "JedisService"
# CI会自动运行 RedisServiceTest.regression()
```

---

## 🔗 Stage 40 协同（⭐ V9.05 增量 · DSH 调试桥接）

> **触发源**：[devmom/dsh-trajectory-debug](https://github.com/devmom/dsh-trajectory-debug) v0.2.0 · MIT ✅ · 56/56 vitest PASS · 镜像在 `skills/dsh-trajectory-debug-integration/` + 侧源 `plugins/dsh-trajectory-debug/`
>
> **协同目标**：把 04 验证师的"极端找茬 + FMEA + 故障模式"能力**用 evidence 而不是 opinion** 做支撑。

### V9.05 §1. 失败归因 + 断点 + 重跑 协同

```python
# V9.05 标准三步验证（失败定位 → 重放 → 重跑）
from dsh_trajectory_bridge import DshTrajectoryRPC

rpc = DshTrajectoryRPC(base_url="http://127.0.0.1:3080")

# 1. 失败归因：拉轨迹，把失败 step 标红
traj = rpc.call("trajectory.list", {"limit": 50, "filter": "has_error"})
for session in traj["value"]:
    perf = rpc.call("perf", {"sessionId": session["id"]})
    if perf["value"]["failure_taxonomy"][0] != "transient":
        # 2. 断点：在该 agent/pre-step 设断
        rpc.call("breakpoint.set", {"sessionId": session["id"], "where": "agent/pre-step"})
        # 3. 重跑：让用户决定改参方式
        print(f"[V9.05] 建议重跑 {session['id']} step {perf['value']['failure_step']}")
```

### V9.05 §2. FMEA 与 trajectory 失败归因双源对照

| FMEA 表 | trajectory 信号 | 对照 |
|---|---|---|
| 失效模式（Failure Mode）| `failure_taxonomy` 字段 | 一对一 |
| 严重度（Severity）| `cost` + `tokens_wasted` | 反比，越高严重度低 |
| 检测度（Detection）| `TTFT_p99` + 失败 step 数 | 正比，越高越难检测 |
| 发生度（Occurrence）| `failure_rate` | 一对一 |

### V9.05 §3. 性能 ceiling check

```bash
# /perf 作为 baseline 巡检入口
python skills/dsh-trajectory-debug-integration/scripts/dsh_trajectory_bridge.py perf \
    --session <id> --price '{"deepseek":{"input":0.14,"output":0.28}}'
```

### V9.05 §4. DON'T 护栏（trajectory-debug 增量）

- ❌ **不要**改写源码会话（model-visible == recorded 不变式）；fork 是唯一修改通道
- ❌ **不要**默认开启 `enableModelTools`（每 step 多一次 LLM 调用；opt-in）
- ❌ **不要**在 prod 环境用 `strategy: 'ask'`（无 live agent 时 fail-closed）
- ❌ **不要**把 trajectory JSON 当 production 数据用（projection 才是稳定形态）

### V9.05 §5. 验证矩阵增量

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | 失败归因能正确分类 transient / domain / tool_timeout | taxonomy 出现率 ≥3 类 | ⏳ |
| 2 | 断点在 agent/pre-step 可设可移除 | `breakpoint.set/list/remove` 闭环 | ⏳ |
| 3 | perf dashboard 4 维度齐全 | success/percentile/token/TTFT 全部就位 | ⏳ |
| 4 | 与 FMEA 表格双向对照 | 4 维度 8 字段对齐 | ⏳ |

---

**版本**: V9.06 (ce-bug 修复追踪版 + Stage 40 trajectory-debug 协同 + Stage 45 dsh-eval-bridge LLM judge)
**最后更新**: 2026-08-24
**整合来源**: EveryInc/compound-engineering-plugin/ce-bug + dsh-trajectory-debug v0.2.0 + dsh-eval v0.3.0
**优化者**: 九部天龙 + CE Bug Track 模板 + 实事求是验证 + Stage 40 + Stage 45 借鉴协同

---

## 🔗 Stage 45 协同（⭐ V9.06 增量 · dsh-eval-bridge LLM judge）

> **触发源**：[hccccc01333/dsh-eval](https://github.com/hccccc01333/dsh-eval) v0.3.0 · MIT ✅ · 借鉴 4 类方法论（benchmark YAML / 11 指标 / LLM judge / paired A/B）· 不镜像真源（DSH 主仓依赖是 blocker）· 落天龙 `skills/dsh-eval-bridge/`
>
> **协同目标**：把 04 验证师的"evidence-based 验证"能力**进一步借 LLM judge 自动评分**，单条 trial 可同时得"规则 PASS/FAIL"+"LLM 评分 0-1"+"hallucination flag"3 维。

### V9.06 §1. LLM judge 与规则评分双源对照

```python
# V9.06 标准三源验证（规则 + LLM judge + hallucination check）
from dsh_eval_bridge import parse_judge_verdict, build_judge_prompt

# 1. 规则评分（已有 V9.05 失败归因）
rules_passed = check_expected_tool(actual, expected)

# 2. LLM judge 调用（借鉴 dsh-eval strict JSON）
prompt = build_judge_prompt(case.prompt, expected, actual.answer)
verdict = parse_judge_verdict(judge_llm_call(prompt))
# → {score: 0.85, hallucinated: false, comment: "..."}

# 3. 双源对照
if rules_passed and verdict["score"] > 0.7 and not verdict["hallucinated"]:
    confidence = "HIGH"
elif verdict["score"] > 0.5:
    confidence = "MEDIUM"
else:
    confidence = "LOW"
```

### V9.06 §2. judge verdict 5 类 schema 校验

| 字段 | 类型 | 范围 | 校验 |
|---|---|---|---|
| `score` | number | 0.0 ~ 1.0 | 范围检查 + 类型 + 非空 |
| `hallucinated` | boolean | true/false | 类型检查 |
| `comment` | string | 10 ~ 500 chars | 长度 + 不能"judge parse failed" |

### V9.06 §3. paired A/B 协同（wins/losses/tie）

借鉴 dsh-eval compare 接口。在 FMEA 表格中加入"版本对比"列：
- v1 → v2 delta = +X% task_success_rate → **验证新版本改善**
- paired_ab.py compare eval-v1.json eval-v2.json --out paired.md

### V9.06 §4. DON'T 护栏（dsh-eval 增量 · 借鉴档）

- ❌ **不要**镜像 dsh-eval 真源（DSH 主仓依赖 blocker）
- ❌ **不要**默认开启 `enableLLMJudge`（每评测多一次 LLM → token 翻倍；opt-in）
- ❌ **不要**让 judge model 与 case model 同 model（同 model bias + 算力浪费）
- ❌ **不要**把 judge verdict 写入生产（仅 stage-45 借鉴档调试用）

### V9.06 §5. 验证矩阵增量

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | judge verdict 解析严格 schema | 5 字段全过 | ✅ （dsh-eval-bridge 14/14 unittest）|
| 2 | 双源对照规则 (rules + judge + hallucination) | confidence 3 档 | ⏳ |
| 3 | paired A/B 算 win/lose/tie | Δ 误差 ≤ 1e-5 | ✅ （dsh_eval_bridge.py `paired_ab_compare`）|
| 4 | benchmark YAML schema 11 字段校验 | 借鉴 dsh-eval | ✅ （`parse_benchmark_yaml`）|
