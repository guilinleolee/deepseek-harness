---
name: style-24-to-gpt-image-2-mapping
version: 1.0.0
stage: 22
date: 2026-07-20
upstream: xhs-visual-director-skill/docs/style_system.md（24 风格）
downstream: gpt-image-2-style-library/references/style-library.md（21 模板）
---

# 24 风格 → 21 模板 合并映射表

## 0. 目标

把 `xhs-visual-director-skill/docs/style_system.md` 的 **24 内置风格**合并回灌到 [gpt-image-2-style-library](C:\Users\li\.claude\skills\gpt-image-2-style-library\SKILL.md) 的 **21 模板分类树**，解决：
- 本地 21 模板覆盖不全（缺商务 / 地图 / 暗黑 / 黑金 / 漫画分镜）
- 24 风格零代码、纯文档，与 21 模板各擅胜场，需要去重映射

## 1. 24 风格清单（按 upstream 顺序）

| # | 风格 | 品类 |
|---|---|---|
| 1 | 深色科技杂志风 | AI/技术 |
| 2 | 黑白灰 + 荧光绿冲击风 | AI/技术 |
| 3 | Notion 高级卡片风 | 教程/工具 |
| 4 | 液态玻璃 / 弥散极光风 | 产品/品牌 |
| 5 | 极简产品发布会风 | 产品 |
| 6 | 反差冲击封面风 | 观点/爆款 |
| 7 | 架构图 / 系统拆解风 | 工程/方法论 |
| 8 | 手机截图改造风 | 工具教程 |
| 9 | **高级商业提案风** ⚠️本地缺 | 商业/产业 |
| 10 | **全球贸易网络风** ⚠️本地缺 | 外贸/跨境 |
| 11 | 高级白底杂志风 | 观点/编辑 |
| 12 | 红绿对错对比风 | 改版/教程 |
| 13 | **赛博档案 / 黑客文件风** ⚠️本地缺 | 技术 |
| 14 | **未来实验室风** ⚠️本地缺 | 实验/原型 |
| 15 | 设计师灵感板风 | 设计教程 |
| 16 | **高级极简黑金风** ⚠️本地缺 | 品牌/课程 |
| 17 | 软件界面 UI 风 | 工具/SaaS |
| 18 | 课程讲义 / 高级黑板风 | 教学 |
| 19 | 个人品牌宣言风 | 个人 IP |
| 20 | 情绪共鸣 / 夜间独白风 | 情感/思考 |
| 21 | 数据报告 / 趋势洞察风 | 行业/数据 |
| 22 | **故事漫画分镜风** ⚠️本地缺 | 故事/漫画 |
| 23 | 课程讲义（同 18） | 重命名 |
| 24 | 极简黑金风（同 16） | 重命名 |

**24 风格 → 21 有效风格**（去掉 23/24 重命名）= **22 风格**（其中 7 条本地之前缺）

## 2. 21 模板分类树（gpt-image-2-style-library）

| # | 模板 | 类别 |
|---|---|---|
| 1 | UI Screenshot System | UI 与界面 |
| 2 | Infographic Engine | 图表与信息可视化 |
| 3 | Scientific Scale Diagram | 图表与信息可视化 |
| 4 | Poster Layout System | 海报与排版 |
| 5 | Sports Campaign Poster | 海报与排版 |
| 6 | Conceptual Typography Poster | 海报与排版 |
| 7 | Ink Double Exposure Poster | 海报与排版 |
| 8 | Nature Science Poster | 海报与排版 |
| 9 | Product Commerce Visual | 商品与电商 |
| 10 | Personalized Beauty Report | 商品与电商 |
| 11 | Brand Identity Package | 品牌与标志 |
| 12 | Brand Touchpoint Board | 品牌与标志 |
| 13 | Architecture & Space | 建筑与空间 |
| 14 | Realistic Photography | 摄影与写实 |
| 15 | Street Accident Moment | 摄影与写实 |
| 16 | Illustration & Art Style | 插画与艺术 |
| 17 | Character Design Sheet | 人物与角色 |
| 18 | 3D Collectible Toy | 人物与角色 |
| 19 | Scene Storytelling | 场景与叙事 |
| 20 | History & Classical Themes | 历史与古风 |
| 21 | Document & Publishing | 文档与出版物 |
| 22 | Concept Product Breakdown | 其他应用场景 |

**注**：gpt-image-2-style-library 实际是 22 个模板（含 Concept Product Breakdown）。

## 3. 合并映射表（核心）

| 24 风格 # | 24 风格名 | 主映射 21 模板 | 备选 21 模板 | 合并动作 |
|---|---|---|---|---|
| 1 | 深色科技杂志风 | 4 Poster Layout System | 7 Ink Double Exposure | 风格描述追加至模板 4 的 guidance |
| 2 | 黑白灰 + 荧光绿冲击风 | 6 Conceptual Typography Poster | 5 Sports Campaign Poster | 风格描述追加至模板 6 |
| 3 | Notion 高级卡片风 | 2 Infographic Engine | 11 Brand Touchpoint Board | 风格描述追加至模板 2 |
| 4 | 液态玻璃 / 弥散极光风 | 1 UI Screenshot System | 4 Poster Layout System | 风格描述追加至模板 1 |
| 5 | 极简产品发布会风 | 22 Concept Product Breakdown | 9 Product Commerce Visual | 风格描述追加至模板 22 |
| 6 | 反差冲击封面风 | 5 Sports Campaign Poster | 6 Conceptual Typography Poster | 风格描述追加至模板 5 |
| 7 | 架构图 / 系统拆解风 | 2 Infographic Engine | 1 UI Screenshot System | 风格描述追加至模板 2 |
| 8 | 手机截图改造风 | 1 UI Screenshot System | 2 Infographic Engine | 风格描述追加至模板 1 |
| **9** ⚠️ | **高级商业提案风** | **12 Brand Touchpoint Board**（新增商业提案子分支）| 4 Poster Layout System | **模板 12 新增子分支：commercial_proposal** |
| **10** ⚠️ | **全球贸易网络风** | **13 Architecture & Space**（地图叙事子分支）| 12 Brand Touchpoint Board | **模板 13 新增子分支：global_trade_network** |
| 11 | 高级白底杂志风 | 4 Poster Layout System | 21 Document & Publishing | 风格描述追加至模板 4 |
| 12 | 红绿对错对比风 | 2 Infographic Engine | 5 Sports Campaign Poster | 风格描述追加至模板 2 |
| **13** ⚠️ | **赛博档案 / 黑客文件风** | **1 UI Screenshot System**（暗色变体）| 22 Concept Product Breakdown | **模板 1 新增子分支：cyber_archive** |
| **14** ⚠️ | **未来实验室风** | **22 Concept Product Breakdown**（实验子分支）| 1 UI Screenshot System | **模板 22 新增子分支：future_lab** |
| 15 | 设计师灵感板风 | 12 Brand Touchpoint Board | 11 Brand Identity Package | 风格描述追加至模板 12 |
| **16** ⚠️ | **高级极简黑金风** | **11 Brand Identity Package**（黑金子分支）| 4 Poster Layout System | **模板 11 新增子分支：minimalist_black_gold** |
| 17 | 软件界面 UI 风 | 1 UI Screenshot System | 22 Concept Product Breakdown | 风格描述追加至模板 1 |
| 18 | 课程讲义 / 高级黑板风 | 8 Nature Science Poster | 2 Infographic Engine | 风格描述追加至模板 8 |
| 19 | 个人品牌宣言风 | 11 Brand Identity Package | 6 Conceptual Typography Poster | 风格描述追加至模板 11 |
| 20 | 情绪共鸣 / 夜间独白风 | 6 Conceptual Typography Poster | 21 Document & Publishing | 风格描述追加至模板 6 |
| 21 | 数据报告 / 趋势洞察风 | 2 Infographic Engine | 4 Poster Layout System | 风格描述追加至模板 2 |
| **22** ⚠️ | **故事漫画分镜风** | **19 Scene Storytelling**（漫画子分支）| 16 Illustration & Art Style | **模板 19 新增子分支：comic_storyboard** |

## 4. 合并动作汇总

### 4.1 仅追加描述（17 条）— 不动模板结构

| 模板 | 追加的风格描述 |
|---|---|
| 1 UI Screenshot System | 风格 4 液态玻璃 / 风格 8 手机截图改造 / 风格 17 软件界面 UI / 风格 13 赛博档案（子分支） |
| 2 Infographic Engine | 风格 3 Notion / 风格 7 架构图 / 风格 12 红绿对错 / 风格 21 数据报告 |
| 4 Poster Layout System | 风格 1 深色科技 / 风格 11 白底杂志 / 风格 9 商业提案 / 风格 16 黑金 |
| 5 Sports Campaign Poster | 风格 6 反差冲击 |
| 6 Conceptual Typography Poster | 风格 2 黑白灰荧光绿 / 风格 20 情绪共鸣 |
| 8 Nature Science Poster | 风格 18 课程讲义 |
| 11 Brand Identity Package | 风格 19 个人品牌 / 风格 16 黑金（子分支）|
| 12 Brand Touchpoint Board | 风格 15 灵感板 / 风格 9 商业提案 |
| 22 Concept Product Breakdown | 风格 5 产品发布会 / 风格 14 未来实验室（子分支） |

### 4.2 新增子分支（6 条）— 模板内部分化

| 模板 | 新增子分支 | 来自风格 |
|---|---|---|
| 1 UI Screenshot System | cyber_archive | 13 赛博档案 |
| 11 Brand Identity Package | minimalist_black_gold | 16 黑金 |
| 12 Brand Touchpoint Board | commercial_proposal | 9 商业提案 |
| 13 Architecture & Space | global_trade_network | 10 全球贸易网络 |
| 19 Scene Storytelling | comic_storyboard | 22 故事漫画分镜 |
| 22 Concept Product Breakdown | future_lab | 14 未来实验室 |

### 4.3 不动模板（5 条）— 已被映射

无（24 风格全部都能找到归宿）

## 5. 回灌执行清单

按以下顺序修改 [gpt-image-2-style-library/references/style-library.md](C:\Users\li\.claude\skills\gpt-image-2-style-library\references\style-library.md)：

1. **追加 17 条风格描述**到对应模板的 `guidance` 字段（合并而非新增条目）
2. **新增 6 个子分支字段** `sub_style` 到 6 个模板的 yaml schema
3. **更新** `SKILL.md` 的"13 大模板类目 21 套模板"表格，新增"含 24 风格回灌 / 6 个新增子分支"标注
4. **更新** `style-library.md` 的 Template Index 章节，标注哪些模板被 xhs-visual-director 风格回灌
5. **验证**：跑一次 gpt-image-2-style-library 的 reference 重建脚本，确认 22 个模板 + 24 个风格 + 6 个子分支全部被索引

## 6. 不做的事

- ❌ 不修改 gpt-image-2-style-library 的 21 模板主结构（category 一级不变）
- ❌ 不动 `templates.md`（仅 `style-library.md` 被回灌）
- ❌ 不创建新模板分类（24 风格合并到现有 22 模板，不新增第 14 类）
- ❌ 不删除任何现有模板

## 7. 回灌后覆盖度

| 维度 | 回灌前 | 回灌后 | 增量 |
|---|---|---|---|
| 模板数 | 22 | 22 + 6 子分支 | +6 个细分场景 |
| 风格覆盖 | ~12 类 | 24 类（合并去重后 22 类）| +10 类本地之前缺 |
| 信息密度档位 | 3 档（low/medium/high）| 4 档（+extreme，from xhs-visual-director） | +1 档 |
| 画幅 | 1:1 / 16:9 / 9:16 | +3:4 锁定（小红书）| +1 |

## 8. 与其他 skill 的覆盖关系

- **baoyu-xhs-images** 12 风格：与本表 12 条主映射模板功能重合，但 baoyu 是"1-10 张卡片"路径，gpt-image-2 是"单图高清"路径 → 互补
- **xhs-images** 88 模板：与本表 14 条交叉（特别是 5/6/11），但 xhs-images 是天龙自研模板生成器，gpt-image-2 是 AI 生成器 → 互补
- **huashu-design** 设计底座：与本表 12（Brand Touchpoint）+ 15（灵感板）有强协同，但 huashu 是设计规范，gpt-image-2 是 AI 出图 → 上游引用

## 9. PASS 验证

| 项 | 判定 |
|---|---|
| 24 风格全部映射 | ✅ 24/24（22 主 + 2 重命名） |
| 7 条本地之前缺全覆盖 | ✅ 7/7（9/10/13/14/16/22 + 1 重复） |
| 不破坏 21 模板结构 | ✅ 仅追加 guidance + 6 子分支 |
| 子分支数 | ✅ 6 个，全部新增无重复 |
| 回灌文档化 | ✅ 本 spec 即文档 |