---
name: generative-media-skills-integration
description: SamurAIGPT/Generative-Media-Skills V1.0 阶段 21 集成 · 78 SKILL.md · MIT ✅ · 200+ 模型走 muapi.ai
metadata:
  node_type: memory
  type: project
  originSessionId: stage-21-generative-media-skills
  modified: 2026-07-20T02:08:43.314Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# generative-media-skills V1.0 · 阶段 21 集成

> **触发源**：[SamurAIGPT/Generative-Media-Skills](https://github.com/SamurAIGPT/Generative-Media-Skills)（200+ 多模态生成模型 · MIT ✅ · 走 [muapi.ai](https://muapi.ai)）
> **集成度**：阶段 21 ⭐NEW · Layer 1/2/3 三层架构 · 累计 **602 PASS**
> **战略定位**：天龙引擎「多模态生成路由」入口 · 补齐 guizang/baoyu/gpt-image-2 之外的 200+ 模型 fallback

---

## 一、为什么是这一步

| 维度 | 数据 | 评价 |
|------|------|------|
| 上游质量 | SamurAIGPT/Generative-Media-Skills · MIT ✅ · 200+ 模型 | ⭐⭐⭐⭐⭐ |
| 已知集成 | 阶段 3 gpt-image-2 (544 案例) + 阶段 4 VoxCPM2 + 阶段 18 guizang | 3 个视觉/音频专精 |
| **剩余缺口** | 中长尾多模态模型（视频/动效/工作流）走 muapi.ai 一键调用 | 唯一通用 fallback |
| AGPL 红线 | ✅ MIT → 无商业限制（对比 guizang AGPL-3.0） | 零红线 |
| **本次集成** | **Layer 1 镜像 + Layer 2 抽取 + Layer 3 真集成 2 e2e** | 三层渐进 |

---

## 二、集成度（Layer 1/2/3 现状）

### Layer 1 · 上游镜像（78 SKILL.md）
- **状态**：占位骨架 + 真 LICENSE
- **路径**：`dragon-engine/skills/generative-media-skills/library/{_core, motion(22), visual(26), social(7), edit, workflow}/`
- **待补**：78 个上游 SKILL.md（用户决策「占位骨架」优先）
- **激活条件**：拿到 `MUAPI_API_KEY` 后批量 mirror

### Layer 2 · async-task-pattern 反向抽取（19/19 PASS）
- **状态**：✅ 完成
- **路径**：`dragon-engine/skills/async-task-pattern/`
- **核心**：4 原语（submit/poll/upload/download）+ 5 adapter（minimax/voxcpm/gpt-image-2/baoyu/muapi）
- **JSON 契约**：5 必传字段（provider/action/payload/timeout/callback）
- **语义化退出码**：0=PASS / 1=FAIL / 2=配置错 / 3=系统错 / 4=未实现

### Layer 3 · 真集成 e2e（12/12 PASS）
- **状态**：✅ 完成
- **路径**：
  - `dragon-engine/skills/nano-banana-brief/` — GPT-Image2 reasoning brief（6/6 PASS minimax e2e）
  - `dragon-engine/skills/cinema-director-laoli/` — 老李风 cinema director（6/6 PASS minimax e2e）
- **待激活**：3 个 L3 spec（ugc-video-factory / seedance-2 / rednote-cover）需 MUAPI_API_KEY

---

## 三、入口文件

```
dragon-engine/skills/generative-media-skills/SKILL.md          ← Layer 1 入口（占位骨架）
dragon-engine/skills/async-task-pattern/SKILL.md               ← Layer 2 入口
dragon-engine/skills/nano-banana-brief/SKILL.md                ← Layer 3 真集成 #1
dragon-engine/skills/cinema-director-laoli/SKILL.md            ← Layer 3 真集成 #2
memory/mit-attribution-statements.md                            ← MIT 合规引用模板
memory/guizang-v2-pipeline.md                                  ← 阶段 19（参照模板）
```

---

## 四、借鉴清单

| 来源 | 借鉴物 | 天龙落地 |
|------|--------|---------|
| SamurAIGPT/Generative-Media-Skills | 78 SKILL.md 分类（motion/visual/social/edit/workflow/_core） | library/ 占位骨架 |
| SamurAIGPT/Generative-Media-Skills/core/ | 异步任务 8 项 agent-native 范式 | async-task-pattern 4 原语 |
| SamurAIGPT/Generative-Media-Skills | muapi.ai 200+ 模型路由 | adapters/muapi.sh（待 KEY） |
| muapi.ai async task pattern | submit/poll/upload/download 语义 | JSON 契约 5 必传 + 退出码 0/1/2/3/4 |

---

## 五、升级摘要

| 维度 | 阶段 21 之前 | **阶段 21 ⭐NEW** |
|------|-------------|------------------|
| 多模态模型路由 | guizang (28) + baoyu (21) + gpt-image-2 (1) ≈ 50 | **+200+ fallback** |
| 异步任务接口 | 每 skill 自己实现 polling | **4 原语统一抽象** |
| License 红线 | guizang AGPL ⚠️ → 仅 PNG 商单 | **MIT 零红线** |
| 视频专业摄影 | 无 | **cinema-director-laoli 老李风分镜** |
| UGC 视频化 | 无 | **35-06 V1.3 第 10 维**（待激活） |
| 横版小红书 | guizang 通用模板 | **rednote-cover**（待激活） |

---

## 六、累计验证 PASS（602 ⭐）

| 测试 | PASS | 来源 |
|------|------|------|
| async-task-pattern 19 用例 | 19/19 | layer 2 |
| Layer 3 e2e（nano-banana-brief + cinema-director-laoli）| 12/12 | layer 3 |
| 3 L3 spec（ugc-video-factory / seedance-2 / rednote-cover）| 已写，待 KEY | layer 3 待激活 |
| 阶段 1-20 累计 | 571/571 | 历史 |
| **合计** | **602 PASS** | 阶段 21 |

---

## 七、已知限制 / 待改进

| 局限 | 影响 | 激活条件 |
|------|------|---------|
| Layer 1 仅占位骨架 | 调用方不能直接用 library/* 下 78 个上游 SKILL.md | 拿到 MUAPI_API_KEY 后批量 mirror |
| 3 个 L3 spec 未激活 | ugc-video-factory / seedance-2 / rednote-cover 仍为空 spec | MUAPI_API_KEY |
| 35-05 V11 agent 文档 | cinema-director-laoli 已建，agent 升级待补 | 阶段 22 |
| 35-06 V1.3 第 10 维 | UGC 视频化 skill 待落地 | 阶段 23 |
| gpt-image-2-prompt-library 灌入 nano-banana reasoning brief | 两库融合 | 阶段 24 |

---

## 八、与天龙 X 阶段 skill 的协同点

| 天龙 skill | 协同点 | 收益 |
|-----------|--------|------|
| 阶段 18 guizang V1.0 ⚠️AGPL | guizang 出图 → guizang 用 guizang-AGPL 模板；其余多模态走 muapi | guizang 缩到 28 版式专精 |
| 阶段 16 huashu-design | 设计底座通用；cinema-director-laoli 走 muapi Seedance/Runway | 老李风电影级分镜 |
| 阶段 4 VoxCPM2 | 配音仍走 VoxCPM2（CPU 真推理）；muapi 仅做 fallback | 主路径不动 |
| 阶段 3 gpt-image-2 | gpt-image-2 主路径；nano-banana-brief 补推理 brief | reasoning + 视觉组合 |
| 阶段 15 baoyu-skills | baoyu 21 skill 仍走本地；新 baoyu-* skill 可选 muapi 后端 | 长尾多模态 fallback |
| 35-02 V13.3 老李风 | 老李风短文案 → cinema-director-laoli 老李风分镜 | 一致性贯通 |
| 35-05 V10.3 视频 | cinema-director-laoli 给 35-05 喂分镜；35-05 调 muapi Seedance | 老李风电影视频 |
| 35-06 V1.3 第 10 维（UGC 视频化）| 待 ugc-video-factory spec 激活 | UGC 短视频工业化 |
| multi-platform-publisher | publisher V2.0 接 muapi 生成物入 publisher.db | 一键多平台分发 |

---

## 九、资产清单

| 路径 | 大小 | 内容 |
|------|------|------|
| `skills/generative-media-skills/` | ~10 KB | SKILL.md + LICENSE + README + library/{_core, motion(22), visual(26), social(7), edit, workflow}/ 占位 README |
| `skills/async-task-pattern/` | ~25 KB | SKILL.md + 4 原语脚本 + 5 adapter + tests/ |
| `skills/nano-banana-brief/` | ~10 KB | SKILL.md + generate.sh + prompt-template.md |
| `skills/cinema-director-laoli/` | ~12 KB | SKILL.md + generate.sh + shot-list.md |
| `memory/mit-attribution-statements.md` | ~5 KB | MIT 合规引用模板 |
| **合计** | **~62 KB** | 7 个新文件 + 7 个占位 README |

---

## 十、关键使用模式

### 模式 1 · 调用多模态模型（最常见）
```bash
# 调用 muapi 上的 GPT-Image2（待 KEY）
bash dragon-engine/skills/async-task-pattern/adapters/muapi.sh \
  --model "gpt-image-2" --prompt "kraft-paper 牛皮纸 ..."

# 调本地 VoxCPM2（无需 KEY）
bash dragon-engine/skills/async-task-pattern/adapters/voxcpm.sh \
  --text "..." --out demo.wav

# 调 MiniMax-M3 via CC Switch
bash dragon-engine/skills/async-task-pattern/adapters/minimax.sh \
  --text "..." --model "claude-opus-4-8"
```

### 模式 2 · 推理 brief → GPT-Image2
```bash
bash dragon-engine/skills/nano-banana-brief/scripts/generate.sh \
  --subject "老李兄弟" --scene "咖啡馆" --style "kraft-paper" --light "暖棕"
# → JSON brief → gpt-image-2 → PNG (6/6 PASS minimax e2e)
```

### 模式 3 · 老李风电影分镜
```bash
bash dragon-engine/skills/cinema-director-laoli/scripts/generate.sh \
  --script "scripts/demo.md" --shots 8
# → shot-list.md → 35-05 V10.3 视频生成 (6/6 PASS minimax e2e)
```

### 模式 4 · 拿到 MUAPI_API_KEY 后激活 3 个 L3 spec
```bash
echo "$MUAPI_API_KEY" > ~/.muapi_key
bash dragon-engine/skills/async-task-pattern/adapters/muapi.sh --verify
# → 激活 ugc-video-factory / seedance-2 / rednote-cover 三 spec
```

---

**Why**：阶段 21 把天龙引擎从「专精工具栈」（guizang + baoyu + gpt-image-2 + VoxCPM2 ≈ 50 模型）升级到「通用 fallback + 专精并用」（+200+ muapi 模型）。Layer 1/2/3 三层架构 + MIT 零红线让商业部署不再受 AGPL 牵制。

**How to apply**：当用户需要「多模态生成但本地图栈没有」 → 直接走 `async-task-pattern/adapters/muapi.sh`；需要「推理 brief → 视觉」 → `nano-banana-brief`；需要「老李风电影分镜」 → `cinema-director-laoli`。

相关：[[guizang-v2-pipeline]] · [[blogger-hologram-to-poster-v2]] · [[laoli-collaboration-integration]] · [[agpl-attribution-statements]]