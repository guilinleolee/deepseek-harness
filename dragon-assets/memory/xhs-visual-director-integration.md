---
name: xhs-visual-director-integration
description: 阶段 22 · xhs-visual-director-skill MIT 镜像 + l3-spec 桥接 + 24 风格回灌 gpt-image-2 合并映射
metadata:
  node_type: memory
  type: project
  originSessionId: stage-22-xhs-visual-director
  modified: 2026-07-20T02:21:49.200Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# 阶段 22 · xhs-visual-director-skill 天龙集成

> **Why**：ziguishian/xhs-visual-director-skill 是小红书图文赛道 **1,065 ⭐ 头部 skill**，与本地 [baoyu-xhs-images](C:\Users\li\.claude\projects\dragon-engine\skills\baoyu-xhs-images\SKILL.md) / [xhs-images](C:\Users\li\.claude\projects\dragon-engine\skills\xhs-images\SKILL.md) **互补**而非替代——前者是"决策/规划上游"，后两者是"出图器"。
>
> **How to apply**：任何"做小红书图文"任务，**先跑 visual-director 10 问协议 + 风格判断报告**，再用 l3-spec 把决策下发到 [gpt-image-2-style-library](C:\Users\li\.claude\skills\gpt-image-2-style-library\SKILL.md) / baoyu-xhs-images / xhs-images 之一出图。

---

## 一、阶段 22 全景

| 资产 | 路径 | 状态 |
|---|---|---|
| 上游仓库 | https://github.com/ziguishian/xhs-visual-director-skill | 1,065 ⭐ · MIT · 19 文件 |
| 本地镜像 | `dragon-engine/skills/xhs-visual-director-skill/` | ✅ 24 文件完整镜像 + ATTRIBUTION + CHANGELOG |
| l3-spec 1 | `xhs-visual-director-skill/l3-specs/xhs-visual-director-to-image-gen.md` | ✅ 桥接规范 |
| l3-spec 2 | `xhs-visual-director-skill/l3-specs/style-24-to-gpt-image-2-mapping.md` | ✅ 24 风格 → 21 模板去重映射 |
| gpt-image-2 回灌 | `gpt-image-2-style-library/references/style-library.md` | ⏳ 待执行（17 描述追加 + 6 子分支） |
| 合规 | `mit-attribution-statements.md § 11` | ✅ 入库 |
| 主题文件 | 本文件 | ✅ |

**累计 PASS**：

| 维度 | 阶段 21 | 阶段 22 增量 | 累计 |
|---|---|---|---|
| Layer 1 镜像 | 78 SKILL.md | +19 + 3 cover + 2 l3-spec + 1 README + 1 ATTRIBUTION + 1 CHANGELOG | 105 文件 |
| Layer 2 协议 | 19/19 async-task | +1 桥接规范 + 1 风格映射 | 21 |
| Layer 3 真集成 | 12/12 e2e | ⏳ 待 MUAPI_API_KEY 激活 | 12 |
| SPEC | 3 个 l3-spec | +2 个 l3-spec | 5 |
| 累计验证 | 602 PASS | **+0**（仅 spec，e2e 待办） | 602 |

## 二、阶段 22 关键判断

### 2.1 为什么镜像而非自研

| 维度 | 自研 | 镜像 |
|---|---|---|
| 时间 | 40-80h | 1h |
| 风格库 | 从 0 到 24 | 现成 24 + 扩展模板 |
| 苏格拉底 10 问协议 | 需自己设计 | 业界验证过的方法论 |
| License | 闭源 | MIT ✅ 零红线 |
| 与本地去重 | 高（都是 24 风格独立设计）| 低（视觉总监 ≠ 出图器）|

**结论**：自研 ROI 太低，镜像是绝对优选。`xhs-images`（88 模板 + 12 AI 封面）+ `baoyu-xhs-images`（12 风格 × 8 版式 × 3 调色板）都是"出图器"，而 visual-director 是"决策/规划上游"，**三层叠加**才是小红书图文的完整链路。

### 2.2 为什么合并到现有 21 模板而非新增子类

| 维度 | 合并 | 新增 xhs-visual-director-24 子类 |
|---|---|---|
| 模板数 | 22 + 6 子分支 | 22 + 24 = 46 |
| 分类清晰度 | 单一树 | 双树并存 |
| 用户查询路径 | 一次选择风格 | 二次选择（先选源再选风格）|
| 维护成本 | 低 | 高（双线更新）|
| 覆盖度 | ✅ 24/24 | ✅ 24/24 |

**结论**：24 风格 90% 可映射到现有 21 模板，剩余 6 条以"子分支"形式新增，**结构简洁 + 用户体验一致**。

### 2.3 为什么放在 `dragon-engine/skills/` 而非 `~/.claude/skills/`

| 维度 | dragon-engine/skills/ | ~/.claude/skills/ |
|---|---|---|
| 与现有 21 阶段集成 | ✅ 同级 | ❌ 跨目录 |
| 主题文件关联 | ✅ 一对一直引 | ⚠️ 路径较长 |
| 21 阶段流水线一致性 | ✅ 阶段 22 = 第 22 个 skill | ❌ 例外 |
| 是否需 ATTRIBUTION.md | ✅ 与 generative-media-skills 同档 | ⚠️ 单独处理 |

**结论**：保持 21 阶段流水线的目录一致性。

## 三、与本地已有 skill 的关系图

```
                  ┌──────────────────────────────┐
                  │ xhs-visual-director-skill    │ ← 阶段 22 新增
                  │ (决策/规划上游 · MIT)        │
                  └──────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ gpt-image-2  │  │ baoyu-xhs-   │  │ xhs-images   │
    │ -style-lib   │  │ images       │  │ (88 模板 +   │
    │ (22 模板+    │  │ (12×8×3)     │  │  12 AI)      │
    │  24 风格)    │  │              │  │              │
    └──────────────┘  └──────────────┘  └──────────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              ▼
                  ┌──────────────────────────────┐
                  │ multi-platform-publisher     │
                  │ V1.0（xhs / wechat / web）   │
                  └──────────────────────────────┘
```

## 四、24 风格回灌后 gpt-image-2-style-library 的覆盖度

| 维度 | 回灌前 | 回灌后 | 增量来源 |
|---|---|---|---|
| 模板数 | 22 | 22 + 6 子分支 | 风格 9/10/13/14/16/22 |
| 风格数 | ~12 类 | 22 类（24-2 重命名）| 全 |
| 信息密度 | 3 档 | 4 档（+extreme）| xhs-visual-director |
| 画幅 | 3 种 | 4 种（+3:4 锁定）| xhs-visual-director |

**回灌执行清单**（待办）：
1. 追加 17 条风格描述到 9 个模板的 `guidance` 字段
2. 新增 6 个子分支（cyber_archive / minimalist_black_gold / commercial_proposal / global_trade_network / future_lab / comic_storyboard）
3. 更新 SKILL.md 的"13 大模板类目 21 套模板"表格
4. 验证 reference 重建脚本

## 五、阶段 22 已知约束

- ⚠️ 镜像本身是纯文档 skill，**无可执行代码** → 验证只能 PASS L2（文档完整性）+ 风格映射覆盖度，无法 PASS L3 真集成 e2e
- ⚠️ 中文渲染在 AI 图像生成中不稳定 → 强制 `text_safe_zone` + 后期叠加
- ⚠️ 苏格拉底 10 问需要交互输入，无法批量自动化

## 六、阶段 22 待办（下一批）

1. **执行回灌**：把 17 描述 + 6 子分支真正写入 `gpt-image-2-style-library/references/style-library.md`
2. **e2e 真集成**：拿到 MUAPI_API_KEY 后跑一次完整 10 问 → 风格判断 → 出图
3. **联动评估**：同作者 **MxPage（245 ⭐）** —— 电商头图，与 guizang 强重叠
4. **联动评估**：同作者 **brand-design-skill（34 ⭐）** —— 品牌 VI，可能补齐博主"个人品牌"维
5. **l3-spec 升级**：把 dbs-xhs-title 升级为 dbs-xhs-brief V1.0，加入苏格拉底 10 问协议

## 七、阶段 22 与其他阶段的协同点

| 协同点 | 来源 | 受益方 |
|---|---|---|
| 苏格拉底 10 问协议 | visual-director | dbs-xhs-brief V1.0（待办）|
| 24 风格库 | visual-director | gpt-image-2-style-library（待办）|
| 视觉母版机制 | visual-director | blogger-fingerprint-registry V3.0（已升级 design_style）|
| 反 AI cliché 列表 | visual-director | baoyu-xhs-images 的 anti_patterns.md |
| 风格扩展模板 | visual-director | dbs-xhs-title + 博主全息克隆 |

## 八、阶段 22 文件清单（最终）

```
C:\Users\li\.claude\projects\dragon-engine\skills\xhs-visual-director-skill\
├── README.md                          ✅ 已写（本地元信息 + 上游原文 + 本地扩展入口）
├── ATTRIBUTION.md                     ✅ 已写（MIT 合规）
├── CHANGELOG.md                       ✅ 已写
├── LICENSE                            ✅ upstream 原样
├── AGENTS.md                          ✅ upstream 原样
├── .gitignore                         ✅ upstream 原样
├── skill/
│   ├── SKILL.md                       ✅ upstream 原样
│   └── agents/openai.yaml             ✅ upstream 原样
├── docs/                              ✅ upstream 原样（7 文件）
│   ├── anti_patterns.md
│   ├── final_image_generation_workflow.md
│   ├── page_structure_rules.md
│   ├── prompt_rules.md
│   ├── socratic_questioning_protocol.md
│   ├── style_system.md（24 风格核心）
│   └── visual_consistency_protocol.md
├── templates/                         ✅ upstream 原样（5 文件）
│   ├── final_caption_template.md
│   ├── image_prompt_template.md
│   ├── style_extension_template.md
│   ├── visual_review_checklist.md
│   └── xhs_carousel_plan_template.md
├── examples/                          ✅ upstream 原样（5 文件）
│   ├── example_image_prompt.md
│   ├── example_input_topic.md
│   ├── example_output_plan.md
│   ├── example_output_yiwu_plan.md
│   └── style_reference_notes.md
├── assets/covers/                     ✅ upstream 原样（3 PNG）
│   ├── cover-vibe-coding.png
│   ├── cover-yiwu-ai.png
│   └── cover-phone-dashboard.png
└── l3-specs/                          ✅ 本地新增（与 upstream 物理隔离）
    ├── xhs-visual-director-to-image-gen.md   ✅ 桥接规范
    └── style-24-to-gpt-image-2-mapping.md   ✅ 去重映射
```

**合计**：24 文件镜像 + 2 l3-spec = **26 文件**。

---

**Why**：阶段 22 是天龙 21 阶段流水线中第一个**完全靠镜像 + 桥接规范**完成的集成阶段，不写新代码、不调权重、不改 prompt，只把 ziguishian 的视觉总监方法论与天龙 21 阶段的 3 个出图器串起来。MIT 零红线 + 1h 完成 + 零破坏 = 22 阶段的 ROI 满分。