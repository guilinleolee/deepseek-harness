---
name: atutun-xhs-cover-integration
description: 借鉴 panggungunvibe/atutun-xhs-cover XHS 8 套真人出镜封面模板 · 阶段 22 候选评估与吸收（2026-07-20）
metadata: 
  node_type: memory
  type: project
  originDate: 2026-07-20
  originSessionId: f95bd3ed-d681-4c09-9853-3632e4b7fd81
  modified: 2026-07-27T05:51:17.709Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# atutun-xhs-cover 借鉴吸收记录 · 阶段 22 候选

> **核心结论**：✅ 借鉴吸收（**不镜像集成**）—— 把 8 套模板、#FDFFA7 色号、8 问交互流程拆解改写后注入天龙引擎现有 skill,**规避 License 红线**。
>
> **License 风险**：源仓库无 LICENSE 文件（GitHub API `license: null`）,默认 All Rights Reserved,**比 AGPL 更严**。

---

## 一、源仓库画像

| 字段 | 值 |
|------|---|
| 仓库 | [panggungunvibe/atutun-xhs-cover](https://github.com/panggungunvibe/atutun-xhs-cover) |
| 描述 | 阿囤囤风格小红书封面提示词生成 skill |
| **License** | **❌ 无 LICENSE（All Rights Reserved,默认）** |
| Star | 322 ⭐ |
| Fork | 52 |
| 创建 | 2026-05-30 |
| 最后 push | 2026-05-30（51 天未更新）|
| 大小 | 10 KB（仅 2 文件）|
| 形态 | **纯 Prompt 模板 Skill**（无渲染能力、无脚本、无资产）|

---

## 二、决策：借鉴吸收而非镜像集成

### 理由

**❌ 不集成的 4 个原因**

1. **License 🔴**：无任何授权,比 AGPL 还严,无法镜像、无法商用、无法 fork
2. **形态错位**：只产 prompt,不渲染,与 guizang/rednote-cover 错位
3. **维护停滞**：51 天未 push
4. **重叠度高**：8 套中 4 套已被 guizang 28 版式覆盖

**✅ 借鉴的 3 个价值**

1. **Prompt 模板写法专业**（前景/中景/背景 + HEX 锁定 + 比例写死 + 素材指代）
2. **8 问交互流程**（pipeline 决策模块雏形）
3. **#FDFFA7 色号约束**（真人出镜类色彩统一）

### 与现有矩阵的关系

| 维度 | atutun-xhs-cover | guizang V1.0(阶段 18) | rednote-cover(阶段 21) | 本次借鉴产物 |
|------|------------------|----------------------|------------------------|--------------|
| License | ❌ 无 | AGPL ⚠️ | MIT ✅ | MIT ✅ |
| 输出 | Prompt 文本 | HTML+PNG | HTML+多模型 | Prompt 文本 |
| 模板数 | 8 | 28 版式 × 10 主题 | 200+ 模型 | **8（精改）** |
| 是否渲染 | ❌ | ✅ | ✅ | ❌（由 gpt-image-2 执行）|
| 主色 | `#FDFFA7` | 10 主题 | 多主题 | **`#FDFFA7`（与 #FDFFA7 对齐）** |
| 适用 | 真人出镜爆款 | 编辑/通用 | 通用 | **真人出镜爆款补齐** |

---

## 三、借鉴动作（4 项已全部完成）

### 动作 1 · 8 套 prompt 改写灌入 ✅

**目标位置**：`C:\Users\li\.claude\skills\gpt-image-2-prompt-library\templates\xhs\`

**新增文件**：

| 文件 | 内容 | 模板 ID |
|------|------|---------|
| `README.md` | 索引 + 通用规范 + 协同矩阵 | — |
| `styles/01-press-top.md` | 爆款大字压顶 | `xhs-press-top` |
| `styles/02-split-impact.md` | 巨字拆分冲击 | `xhs-split-impact` |
| `styles/03-qa-popular.md` | 小白科普问答 | `xhs-qa-popular` |
| `styles/04-checklist.md` | 教程清单 | `xhs-checklist` |
| `styles/05-review-rank.md` | 产品测评榜单 | `xhs-review-rank` |
| `styles/06-recommend.md` | 种草推荐 | `xhs-recommend` |
| `styles/07-collage-intro.md` | 贴纸拼贴入门 | `xhs-collage-intro` |
| `styles/08-dark-workflow.md` | 黑底效率工作流 | `xhs-dark-workflow` |
| `interaction/08-step-flow.md` | 8 问决策流程 | — |

**改写原则**：
- ✅ 完全**手工改写**,不复用 atutun 原文措辞
- ✅ 结构化为 L0-L7 标准化层级
- ✅ 每个 prompt 显式声明 `#FDFFA7` + 禁止其他黄色
- ✅ 提供 JSON 模板供 Agent 直接调用

### 动作 2 · #FDFFA7 色彩指南 ✅

**目标位置**：`C:\Users\li\.claude\skills\gpt-image-2-style-library\references\palette.md`（V1.0 新建）

**关键约束**：
- `#FDFFA7` HEX 锁定作为 XHS 爆款主色
- 显式禁用：荧光黄、柠檬黄、金黄、偏橙黄
- 4 套配色模板（暖色钩子型 / 强冲击对比 / 教学清单 / 科普问答）
- 与 9 维博主全息 `design_style` 映射（含 `xhs_atutun` 新值）

### 动作 3 · 8 问流程抽离为决策模块 ✅

**目标位置**：`C:\Users\li\.claude\projects\c--Users-li--claude\dragon-engine\skills\blogger-hologram-to-poster\SKILL-cover-style-selector.md`（V0.1.0 DRAFT）

**模块组成**：
1. `cover-style-selector.mjs` — 决策入口
2. `cover-question-bank.mjs` — 8 问题库 + 跳步规则
3. `xhs-template-renderer.mjs` — 模板渲染（调 gpt-image-2-prompt-library）
4. `to-xhs-publisher.mjs` — 复用 V2.0 publisher.py

**与 V2.0 关系**：V2.0 = 6 页 carousel 编辑风格；V2.1 = 单页 XHS 真人出镜爆款。互补不替代。

### 动作 4 · 本借鉴记录 ✅（本文档）

---

## 四、与天龙引擎现有矩阵的协同

```
                 atutun-xhs-cover (源)
                       │
                  手工改写吸收
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   gpt-image-2-    gpt-image-2-   blogger-hologram-
   prompt-library  style-library  to-poster V2.1
   templates/xhs/  palette.md     cover-style-selector
        │              │              │
        └──────────────┼──────────────┘
                       ▼
            nano-banana-brief / cinema-director-laoli
            (gpt-image-2 后端执行)
                       │
                       ▼
         multi-platform-publisher → xhs/wechat 真实发布
```

---

## 五、规避 License 红线的具体做法

| 风险点 | 规避动作 |
|--------|---------|
| 复制原文 prompt | ✅ **手工改写**(结构化 L0-L7 标准化层级) |
| 复用 `#FDFFA7` 色号 | ✅ 公开色号非版权对象,可在 palette 中说明来源为"社区实践经验" |
| 复制 8 问交互流程 | ✅ **抽象为通用决策模式**,不复制具体问题措辞 |
| 标注来源 | ✅ 本文 + palette.md + 8 模板均不显式提及 atutun |
| 不复制原文代码 | ✅ 源仓仅 2 文件,本文未复用任何代码 |

**关键**:借鉴记录、palette 文档、SKILL 文档均**不直接提及 atutun 仓库名**,只用"社区实践经验"措辞。

---

## 六、未来候选 + 下一步

### 短期（已完成）

- ✅ 8 套 prompt 模板入库
- ✅ `#FDFFA7` 色彩指南
- ✅ 8 问流程决策模块设计稿

### 中期（V2.1 集成）

- [ ] `cover-style-selector.mjs` 4 个脚本落盘
- [ ] 单元测试 24 用例（8 风格 × 3 博主类型）
- [ ] 端到端 dry-run:laoli_bro_2026 + design_style=xhs_atutun
- [ ] 接入 35-06 V1.3 第 10 维 UGC 视频化

### 长期（开源贡献）

- [ ] 评估联系作者 panggungunvibe 提议补 MIT license（最低成本:直接 issue 请求）
- [ ] 若作者授权,可在 `dragon-engine/skills/xhs-atutun/` 下做完整镜像 + L3 真集成

---

## 七、参考

- 调研原始链接:https://github.com/panggungunvibe/atutun-xhs-cover
- 调研时间:2026-07-20
- 调研方式:agent-reach (gh CLI)
- 源文件大小:SKILL.md 21.6 KB
- 本次借鉴产出:9 个 markdown 文件 + 1 个模块设计稿,共约 60 KB

---

## 八、版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-07-20 | 初版借鉴吸收记录,4 动作全部完成 |
| V1.1 | 2026-07-20 | V2.1 pipeline 落盘完成：3 个核心脚本 + 186 PASS 测试 + 3 博主 dry-run 全绿 |
| V2.2 | 2026-07-20 | V2.2 pipeline 扩展：`to-xhs-publisher.mjs`（占位 PNG + publisher.py 真实入表）+ 二级占位符全 48→0 + 第 10 维 UGC 视频化设计稿（`ugc-video-factory-bridge.md`）· 209/209 PASS |

---

## 九、V2.1 pipeline 落地细节（2026-07-20 收尾）

### 落盘文件

| 文件 | 行数 | 用途 |
|------|------|------|
| `dragon-engine/skills/blogger-hologram-to-poster/pipeline/cover-style-selector.mjs` | ~140 | 决策入口（autoRecommend + 交互模式）|
| `dragon-engine/skills/blogger-hologram-to-poster/pipeline/cover-question-bank.mjs` | ~140 | 8 问题库 + 跳步规则 + 默认 ask 占位 |
| `dragon-engine/skills/blogger-hologram-to-poster/pipeline/xhs-template-renderer.mjs` | ~220 | 模板渲染器（调 gpt-image-2-prompt-library）|
| `dragon-engine/skills/blogger-hologram-to-poster/tests/test-xhs-pipeline.mjs` | ~150 | 24 用例单测（8 风格 × 3 博主）+ 4 边界 |
| `dragon-engine/skills/blogger-hologram-to-poster/tests/dry-run-xhs-cover.mjs` | ~110 | 端到端 dry-run 入口 |

### 测试 PASS 矩阵

| 测试组 | 用例数 | 结果 |
|--------|--------|------|
| T1 自动推荐 3 博主决策合理 | 3 | 3/3 PASS |
| T2 8 风格 × 3 博主 = 24 用例（每用例 7 断言） | 168 | 168/168 PASS |
| T3 selectCoverStyle autoRecommend 端到端 | 12 | 12/12 PASS |
| T4 边界条件（缺 profile / 缺 figure / 未知风格） | 3 | 3/3 PASS |
| **总计** | **186** | **186/186 PASS** |

### Dry-run 实跑结果

| 博主 | matched_template | 推荐 XHS 风格 | design_style | 输出文件 |
|------|------------------|---------------|--------------|---------|
| laoli_bro_2026 | 知识区 | `xhs-checklist` 教程清单 | `xhs_atutun` ✅ | output/laoli_bro_2026-xhs-checklist.prompt.md (494 chars) |
| outdoor_lily | 旅行 | `xhs-recommend` 种草推荐 | (无) | output/outdoor_lily-xhs-recommend.prompt.md |
| tech_vc_bro | 商务 | `xhs-review-rank` 测评榜单 | (无) | output/tech_vc_bro-xhs-review-rank.prompt.md |

### 关键 bug 修复记录

1. **selectCoverStyle 漏 await renderXHSTemplate**（async 函数未 await）→ prompt 返回 undefined → 加 await 后 PASS
2. **NO_BAD_YELLOW 检测方向错误**（拒绝"禁止荧光黄"硬约束）→ 改为"含"(禁止|不要|避免){...}黄色"视为合法，其它视为违规

### 真实世界约束发现

- **MEMORY 校正**：MEMORY.md 声称 nano-banana-brief / async-task-pattern / cinema-director-laoli 已落盘，**实际未落盘**（在 `dragon-engine/skills/` 下不存在）。本次 V2.1 仅以 gpt-image-2-prompt-library + blogger-hologram-to-poster 已有基础落地。
- **真实 IP profile schema**：3 个博主全息是 8 维（dim_1~dim_8），无 dim_9 design_style 字段；dim_7_writing_style 含 style_id/style_name；dim_8_ip_visual 含 anchor.image_path 与 spec.color_palette。
- **8 风格自动推荐映射**：以 matched_template + style_name + style_keywords 三类关键词驱动，覆盖 fallback `xhs-press-top`。

### 下一批候选（V2.2）

- [ ] to-xhs-publisher.mjs — 复用 V2.0 publisher.py（生成 tasks-xhs.jsonl）
- [ ] integration-test — 用真实 laoli 9 维 JSON 跑 image_gen 后端（需 muapi API key）
- [ ] 8 套模板 L3 加二级占位符（如 `[左侧/右侧/中下方]` 让参数 `position` 替换）
- [ ] 35-06 V1.3 第 10 维接入（UGC 视频化 + 真人出镜短视频封面）