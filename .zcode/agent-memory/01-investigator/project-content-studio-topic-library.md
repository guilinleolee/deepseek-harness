---
name: project-content-studio-topic-library
description: DSH content-studio 正在新增【选题库】二级栏目，本地优先无后端；2026-09-25 完成 GitHub
  对标调研，4 个引用项目中 2 个存在误引
metadata:
  node_type: memory
  type: project
  originSessionId: sess_subagent_agent_3e2f2839-9083-4395-9c98-ec6d11d52f9e
---

DSH content-studio（本地优先 AI 内容创作插件，浏览器端 UI）新增【选题库】二级栏目。数据存本地 JSON（~/.dsh/outputs/<主题>/），无数据库无后端；视图/筛选配置存 localStorage 不落盘；排期写全局 _schedule.json。

核心能力：表格+看板双视图（五状态栏：灵感待评估/待创作/创作中/已完成/暂存搁置）、AI 选题评分 0-10（受众需求/差异化/竞争度/创作成本）、AI 生成 3 备选标题、来源溯源（来源类型+溯源 ID 跳回素材/对标拆解）、标签筛选批量导出 Markdown。

**Why:** 2026-09-25 应需求方要求做 GitHub 开源对标调研。发现需求文档 4 个引用项目中 2 个有误引：YAML Databases 实际无看板视图且 2022 年已停更；TNT AI Writer 是 WordPress 插件而非 GitHub 开源项目。MediaCrawler 是非商业学习许可（禁商用）。

**How to apply:** 后续做选题库方案评审、实现或二次调研时直接引用本次结论，勿再把这 4 个引用当作准确前提。已核实仓库清单见 [[reference-topic-library-benchmark-repos]]。
