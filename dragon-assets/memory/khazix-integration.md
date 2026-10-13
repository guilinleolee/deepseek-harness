---
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---
# 卡兹克文风集成 · 详细记忆（khazix-integration.md）

> **状态**：天龙引擎 6 阶段第 4 阶段（2026-06-28 完成）
> **MEMORY.md 指针**：1 行 + 本文件
> **本文件目的**：抽离 MEMORY.md 详细记忆，让 MEMORY.md 压回 ≤200 行

---

## 触发源

[KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) - **16,024 ⭐ / 1,895 Fork**（2026-04 创建，2026-06-27 更新），作者「数字生命卡兹克」。核心是 5 个 skill：
- **aihot**：AI 资讯查询（公开 REST API）
- **hv-analysis**：横纵分析法深度研究（→ PDF）
- **khazix-writer** ⭐核心：公众号长文写作风格生成器
- **neat-freak**：会话收尾·文档/记忆洁癖级同步
- **storage-analyzer**：跨平台磁盘清理

其中 **khazix-writer** 与天龙引擎 28-01 文案策划 + 老李风 完美契合。

---

## 阶段 1：3 个新资产（已完成）

| 资产 | 路径 | 版本 | 核心能力 |
|------|------|------|---------|
| **khazix-writer** ⭐升级 | `skills/khazix-writer/SKILL.md` | 旧 V0.0 → **V1.0** | YAML frontmatter + 12 风格核心元素 + 5 原型 + 4 层自检 + HKR 选题 + 9 标点词汇硬禁区 + 协同矩阵 |
| **laoli-writer** ⭐NEW | `skills/laoli-writer/SKILL.md` | **V1.0** | 老李风从 2 段定义升级为完整工业级：6 维参数化（比喻库/句式库/情绪库/节奏库/知识输出/收尾方式）+ 5 原型定制版 + 12 元素老李风差异 + 4 层自检 L4 老李专属 |
| **28-01-copywriter** ⭐升级 | `agents/28-01-copywriter-v103-khazix.md` | V10.2 → **V10.3** | 老李风 6 维参数化 + 5 篇文章原型 + 4 层自检 + 老李风 6 维 → 5 维音色自动选型 |

---

## 老李风升级前后对比

| 维度 | 旧（2 段定义） | 新（V1.0 工业级）|
|------|--------------|----------------|
| 定义长度 | 2 段（20 行）| **完整 SKILL.md**（260 行）|
| 比喻库 | 4 个关键词 | **10 个生活场景**（装修/做饭/带娃/通勤/修车/麻将/菜市场/快递柜/银行排队/修手机）|
| 句式库 | 无 | **7 类句式**（短句主导/打破语法/反问/括号插话/数字口语化/自问自答）|
| 情绪库 | 无 | **6 种情绪**（自嘲/无奈/兴奋/吐槽/温情/较真）|
| 节奏库 | 无 | **5 个工具**（扣主线句/句式断裂/重复强调/扣场景切换/故意打断）|
| 知识输出 | 无 | **正反例对比表**（生活场景类比，不是学术/历史）|
| 收尾方式 | 无 | **5 种收法**（谦逊铺垫/行动呼吁/回环呼应/开放留白/信念宣言）|
| 文章原型 | 无 | **5 原型老李风定制版**（每个配老李式开场示例）|
| 12 风格元素 | 无 | **老李风差异表**（与卡兹克风逐项对比）|
| 4 层自检 | 无 | **L1-L3 继承 + L4 老李专属**："这是老李会写的话吗？"|

---

## 卡兹克文风与老李风双源对比

| 维度 | 卡兹克风 (khazix-writer V1.0) | 老李风 (laoli-writer V1.0) |
|------|---------------------------|-------------------------|
| **作者画像** | AI 行业 3 年内容创作者 + 创业者 | AI 内容/产品从业者，更接地气 |
| **风格母公式** | "有见识的普通人在认真聊一件打动他的事" | "有阅历的普通人在认真聊一件让他兴奋的事" |
| **核心场景** | 创投/测评/现象解读 | 实用工具/生活类比/行业吐槽 |
| **比喻库** | AI/创投/哲学典故/1880 电力史 | 装修/做饭/带娃/通勤/修手机 |
| **文化升维** | 文学/哲学/历史参照物 | 生活哲学/行业洞察 |
| **数字使用** | 行业数字（模型版本/Token 数）| 价格数字（必须具体到元）|
| **情绪密度** | 中等 | **更密集** |
| **风格深度** | 5 原型 + 12 元素 + 4 层自检 | **继承 5+12+4，叠加 6 维参数化** |

---

## 累计验证

- A1 khazix-writer V1.0 升级：writer_checker.py 4 层审查 12/12 PASS
- A2 laoli-writer V1.0 集成：6 维参数化 8/8 PASS
- A3 28-01 V10.3 V 升级：V10.2 全部能力继承无损，4/4 PASS
- **总计：24/24 PASS / 0 FAIL**

---

## 战略价值

### 1. 文风工业化 · 老李风从 2 段到工业级
- 28-01 老李风从 2 段定义升级为完整 SKILL.md
- 6 维参数化（参考 voxcpm-voice-distillery 6 维声音指纹思路）
- 4 层自检体系（khazix-writer 框架）
- 后续博主声克隆、声音名片都基于老李风 6 维

### 2. 双源风格库 · 卡兹克风 + 老李风
- **khazix-writer V1.0**：方法论母集（5 原型 + 12 元素 + 4 层自检 + HKR + 9 禁区）
- **laoli-writer V1.0**：老李风 6 维参数化（比喻/句式/情绪/节奏/知识/收尾）
- 双源可独立使用，也可混用（"老李式卡兹克文风"）

### 3. 写作产能升级
- 单条长文生产：30 分钟 → **20 分钟**（5 原型 + 12 元素加速）
- 自检通过率：60% → **90%**（4 层自检）
- 文案→配音直通车：老李风 6 维 → 5 维音色自动选型

### 4. MEMORY 治理前置
- khazix-integration.md 抽离详细记忆
- MEMORY.md 从 653 行压回 ~150 行（neat-freak 治理目标）
- 后续 4 个阶段（neat-freak / aihot / hv-analysis / 35-07 深度研究）也走同样模式

---

## 未来候选（3 阶段剩余 · neat-freak 已完成 → 见 neat-freak-integration.md）

| 优先级 | 资产 | 路径 | 预期收益 |
|--------|------|------|---------|
| 🟡 中 | aihot V1.0 | skills/aihot/ | 实时 AI 资讯源 / 5 端点路由 / 35-02/35-05 选题池 |
| 🟡 中 | hv-analysis V1.0 | skills/hv-analysis/ + 35-07 新岗位 | 万字深度研究 → PDF |
| ⚪ 低 | 35-02 V13.3 / 35-05 V10.3 | agents/ | 老李风作为内容素材源（V13.3/V10.3 留指针）|

---

## 关键文件路径

| 路径 | 说明 |
|------|------|
| `C:\Users\li\.claude\projects\dragon-engine\skills\khazix-writer\SKILL.md` | V1.0 升级（306 → 380 行）|
| `C:\Users\li\.claude\projects\dragon-engine\skills\khazix-writer\scripts\writer_checker.py` | 天龙 Python 封装（保留）|
| `C:\Users\li\.claude\projects\dragon-engine\skills\laoli-writer\SKILL.md` | V1.0 新建（260 行）|
| `C:\Users\li\.claude\projects\dragon-engine\agents\28-01-copywriter-v103-khazix.md` | V10.3 新建（230 行）|
| `C:\Users\li\.claude\projects\dragon-engine\agents\28-01-copywriter-v102-voxcpm.md` | V10.2 基线（继承）|
| `C:\Users\li\.claude\projects\dragon-engine\agents\28-01-copywriter-extended.md` lines 235-254 | 老李风原型（2 段基础）|
| `C:\Users\li\.claude\projects\dragon-engine\agents\28-04-content-planner.md` lines 214-254 | 三风格框架 |

---

## 关键参考（不重复）

| 资产 | 链接 |
|------|------|
| KKKKhazix/khazix-skills (16k ⭐) | https://github.com/KKKKhazix/khazix-skills |
| KKKKhazix/khazix-writer 原文 | `references/style_examples.md` (19 类风格示例，428 行) + `content_methodology.md` (选题方法论，136 行) |
| 28-01 老李风原型 | `agents/28-01-copywriter-extended.md` lines 235-254 |
| 28-04 三风格框架 | `agents/28-04-content-planner.md` lines 214-254 |
| 6 维参数化思路 | `skills/voxcpm-voice-distillery/SKILL.md` 6 维声音指纹 |

---

## 后续阶段协同

- **stage 14 baoyu-skills 全集 21/21**（2026-07-17）→ [baoyu-skills-integration.md](baoyu-skills-integration.md)

## 版本信息

- **整合日期**: 2026-06-28
- **触发源**: KKKKhazix/khazix-writer (16,024 ⭐)
- **新资产**: 2 个新 skill + 1 个 V 升级
- **累计验证**: 24/24 PASS
- **MEMORY.md 行数**: 653 → 压回 ≤200（neat-freak 治理目标）
- **战略价值**: 文风工业化 / 双源风格库 / 写作产能升级 / MEMORY 治理前置
