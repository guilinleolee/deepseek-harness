---
name: huashu-vs-guizang-course-redirect
description: 知识付费 / 模板方法论课程视觉底座：改用 huashu-design V1.0（自有协议）替代 guizang（AGPL-3.0）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1b69faff-55b8-4ac4-982e-93b0e3e2aafb
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# C4 知识付费课程视觉底座迁移：huashu-design 替代 guizang

> **Why**：guizang-social-card-skill 是 **AGPL-3.0**（R1 评估 2026-07-17）。COMMERCIAL_LICENSING.md L107 + L171 明确禁止"将 guizang 能力包装后再出售给第三方平台"。把 28 版式 / 10 主题作为方法论课程售卖 = 🔴 禁止。
>
> **How to apply**：任何"教别人怎么做出小红书图文 / 公众号封面"的课程（含博主全息课、IP 训练营、社群分享、模板方法论），视觉底座改用天龙阶段 15 已集成的 `huashu-design V1.0`（自有协议 · 21.5k ⭐ · 42 文件）。

---

## 为什么是 huashu-design

| 维度 | guizang-social-card-skill | huashu-design V1.0 |
|------|--------------------------|-------------------|
| 许可证 | 🔴 **AGPL-3.0**（禁止商业再分发）| ✅ **自有协议**（允许自由使用与教学）|
| 视觉系统 | Editorial × Swiss 双套 + 28 版式 | 6 大能力（Fallback 顾问 / App 原型 / PPT / 动画 / 信息图 / 评审）|
| 主题预设 | 10 套（墨水/靛蓝/IKB/柠檬/...）| 21 套工业模板 + Launch Film Director Notes 14KB 万字方法论 |
| 模板方法论 | COMMERCIAL_LICENSING.md L107 禁止封装售卖 | 可作为自有课程内容 |
| 博客封面 / 信息图 / 演示 deck | ⚠️ 涉及 AGPL § 13 网络分发 | ✅ 完整覆盖 + render-video.js 动画→MP4 |
| 与博主全息协同 | ⚠️ 需附 AGPL footer + Source 链接 | ✅ 完全自有 |

## 课程内容映射（28 版式 → huashu 能力）

| 原 guizang 课程章节 | 改用 huashu 对应能力 |
|-------------------|---------------------|
| Editorial 杂志风 16 版式（M01-M16）| huashu **App/iOS 高保真原型** + **演示 deck** + **信息图** |
| Swiss 网格 12 版式（S01-S12）| huashu **品牌资产协议**（双重护栏） + **5 维专家评审** |
| 10 套主题预设 | huashu **21 套工业模板** + **html2pptx.js**（PPT 工具栈）|
| 28 版式骨架方法论 | huashu **Fallback 顾问**（需求模糊时给 3 方向）+ **render-video.js**（动画 → MP4）|

## 课程交付建议

- **课件**：huashu-design 21 套工业模板做视觉底座
- **演示**：huashu render-video.js 做动画演示（替代 guizang WebGL 墨流）
- **作业模板**：基于 huashu html2pptx.js 输出（不依赖 guizang）
- **课程声明**：「本课程基于开源项目 alchaincyf/huashu-design 的视觉方法论，遵循其协议」

## 不变（仍可用 guizang）

| 场景 | 判断 |
|------|------|
| 个人小红书图文（自营）| ✅ 继续用 guizang（仅 PNG 输出）+ 挂版权声明 |
| 公众号封面（自营）| ✅ 继续用 guizang（仅 PNG）|
| 甲方商单交付（仅交付 PNG）| ✅ 继续用 guizang（LICENSE § 4 允许收费）|
| 朋友圈 / 视频号封面（自营）| ✅ 继续用 guizang |
| **知识付费课程** | 🔴 **改用 huashu-design** |
| **模板方法论付费教程** | 🔴 **改用 huashu-design** |
| **模板作为商品售卖** | 🔴 **改用 huashu-design** |

## 红线

- 🔴 **不要在课程里截图 guizang 28 版式具体实现**作为"我的课程内容"
- 🔴 **不要把 guizang SKILL.md / templates / layout-recipes.md** 作为课程资料分发
- ✅ 可以**引用 guizang 的设计哲学**（"Swiss 网格美学"），但**不复用具体实现**

---

## 相关链接

- [[guizang-social-card-integration]] — guizang 集成主题文件（AGPL 边界完整版）
- [[huashu-design-integration]] — huashu-design V1.0 完整版（阶段 15）
- [[agpl-attribution-statements]] — guizang 商用版权声明模板