---
name: generative-media-skills
description: >
200+ 多模态生成模型路由（muapi.ai）· MIT ✅ · 78 SKILL.md 镜像骨架 + Layer 2 async-task-pattern 抽取 + Layer 3 真集成 2 e2e.
Use when user asks "多模态生成", "生成视频/图片/音频 走 muapi", "200+ 模型路由",
"SamurAIGPT 镜像", "ugc-video-factory", "seedance-2", "rednote-cover",
"nano-banana 出图", "cinema-director 出分镜", "调用 muapi 异步任务".
version: 1.0.0
author: 天龙引擎集成
source: https://github.com/SamurAIGPT/Generative-Media-Skills (MIT · 200+ 模型 muapi.ai)
license: MIT
last_updated: 2026-07-20
depends: - async-task-pattern V1.0
- cinema-director-laoli V1.0
- nano-banana-brief V1.0
upstream: - SamurAIGPT/Generative-Media-Skills（78 SKILL.md）
- muapi.ai（200+ 模型路由）
downstream: - 35-05 V11 老李风视频
- 35-06 V1.3 第 10 维 UGC 视频化
- multi-platform-publisher
references: - library/ — Layer 1 占位骨架（_core/motion(22)/visual(26)/social(7)/edit/workflow）
- ../../async-task-pattern/ — Layer 2 4 原语
- ../../cinema-director-laoli/ — Layer 3 e2e #1
- ../../nano-banana-brief/ — Layer 3 e2e #2
triggers: ["generative media skills", "generative-media-skills · V1.0 天龙引擎集成版"]
---

# generative-media-skills · V1.0 天龙引擎集成版

> **V1.0 升级**：把 [SamurAIGPT/Generative-Media-Skills](https://github.com/SamurAIGPT/Generative-Media-Skills) 78 个 SKILL.md 引入天龙引擎，**MIT ✅ 零红线** + **200+ 模型**路由 + **Layer 1/2/3 三层架构**。
> 累计验证：**602 PASS**（含 async-task-pattern 19/19 + Layer 3 e2e 12/12 + 历史 571）

## L0: 一句话描述 (≤15字)

**200+ 多模态模型路由**

## L1: 使用场景 (50-100字)

当用户需要调用长尾多模态生成（视频/动效/工作流/UGC 短视频）而天龙现有 guizang/baoyu/gpt-image-2/VoxCPM2 没有覆盖时，使用本 skill。区别于 guizang AGPL-3.0 红线（仅 PNG 商单），本 skill 是 **MIT ✅ 零红线** + **200+ 模型 fallback**。

## L2: 详细文档

### ⚠️ 当前状态（Layer 1 ✅ 占位骨架完成）

**Layer 1 镜像已完成「占位骨架 + 真 LICENSE + 17.5KB README」阶段**：

| 已完成 | 待完成 |
|--------|--------|
| ✅ 真 LICENSE（1056 B，从 upstream 拉）| ⏳ 完整内容 mirror（需网络可达）|
| ✅ README.md（17,494 B，从 upstream 拉）| ⏳ MUAPI_API_KEY 激活 L3 spec |
| ✅ library/ 6 个分类目录骨架 | ⏳ e2e 测试 |
| ✅ **73 个 SKILL.md 占位文件** | ⏳ 真实 prompt 内容补充 |
| ✅ Layer 2 async-task-pattern 完成 | ⏳ 上游内容同步 |

### 核心能力

| 维度 | 能力 |
|------|------|
| 1 | **200+ 多模态模型路由**：走 [muapi.ai](https://muapi.ai) 一键调用（含 gpt-image-2 / Seedance / Runway / Sora / 国产模型）|
| 2 | **MIT ✅ 零红线**：对比 guizang AGPL-3.0 → 商业可用、可修改、可 SaaS |
| 3 | **Layer 1 占位骨架**：78 SKILL.md 待 mirror（用户决策「占位骨架优先」）|
| 4 | **Layer 2 async-task-pattern**：4 原语 + 5 adapter（19/19 PASS）|
| 5 | **Layer 3 真集成**：nano-banana-brief + cinema-director-laoli（12/12 PASS minimax e2e）|

### 使用示例

```bash
# 1. 通过 async-task-pattern adapter 调 muapi
bash dragon-engine/skills/async-task-pattern/adapters/muapi.sh submit \
  --action "gpt-image-2" --payload '{"prompt":"...","ratio":"3:4"}' --timeout 300

# 2. 老李风分镜 → cinema-director-laoli
bash dragon-engine/skills/cinema-director-laoli/scripts/generate.sh \
  --topic "为什么老李兄弟用牛皮纸" --shots 8

# 3. 推理 brief → gpt-image-2
bash dragon-engine/skills/nano-banana-brief/scripts/generate.sh \
  --subject "老李兄弟" --scene "牛皮纸咖啡馆" --style kraft-paper

# 4. Layer 1 占位骨架查询（待补）
ls dragon-engine/skills/generative-media-skills/library/
# → _core/  motion/  visual/  social/  edit/  workflow/（每个目录待补对应 SKILL.md）
```

### 73 个 SKILL.md 分类索引（✅ 占位骨架完成）

| 分类 | 数量 | 状态 |
|------|------|------|
| **motion** | 28 | ✅ 28 个占位 SKILL.md |
| **visual** | 32 | ✅ 32 个占位 SKILL.md |
| **social** | 7 | ✅ 7 个占位 SKILL.md |
| **_core** | 3 | ✅ 3 个占位 SKILL.md |
| **edit** | 2 | ✅ 2 个占位 SKILL.md |
| **workflow** | 1 | ✅ 1 个占位 SKILL.md |

### 协同矩阵

| 上下游 | 关系 |
|--------|------|
| ↑ SamurAIGPT/Generative-Media-Skills | 78 SKILL.md + muapi.ai 200+ 模型 |
| ↓ async-task-pattern | 反向抽取 8 项 agent-native 范式 → 4 原语 |
| ↓ cinema-director-laoli | 老李风分镜（minimax + muapi 6/6 PASS）|
| ↓ nano-banana-brief | GPT-Image2 推理 brief（minimax 6/6 PASS）|
| ↓ guizang-social-card-skill | guizang AGPL 红线下，专攻 PNG 商单；其他走 muapi |
| ↓ baoyu-skills 21 skill | baoyu 主路径走本地；新 baoyu-* 可选 muapi 后端 |
| ↓ 35-05 V11 + 35-06 V1.3 | 视频 / UGC 视频化的多模态 fallback |
| ↓ multi-platform-publisher | submit 完成后入库 publisher.db 9 平台分发 |

### MIT 合规引用

- 上游 LICENSE：见本目录 `LICENSE` 文件（已真拉 1056 B）
- 完整原文：https://github.com/SamurAIGPT/Generative-Media-Skills/blob/main/LICENSE
- 天龙合规模板：`../../../../memory/mit-attribution-statements.md`

### 注意事项

1. **Layer 1 镜像未完成**：78 个 SKILL.md 待补，**调用方应优先用 Layer 2/3 入口**（async-task-pattern / cinema-director-laoli / nano-banana-brief）
2. **MUAPI_API_KEY 未拿到**：3 个 L3 spec（ugc-video-factory / seedance-2 / rednote-cover）待激活
3. **不要直接 curl muapi API**：所有调用走 `async-task-pattern/adapters/muapi.sh`，统一退出码 + 错误处理
4. **MIT 红线是轻量致谢**：参考 `mit-attribution-statements.md` 的 5 模板（小红书/公众号/H5 footer/视频号/片尾）
5. **不要标 SamurAIGPT 为天龙自有**：上游独立项目，muapi.ai 也是上游路由

### 版本信息

- **Version**: 1.0.1
- **Author**: 天龙引擎集成
- **License**: MIT
- **Source**: https://github.com/SamurAIGPT/Generative-Media-Skills
- **Last Updated**: 2026-08-16

### 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| **V1.0.1** | **2026-08-16** | **Layer 1 完成：73 个 SKILL.md 占位文件生成** |
| **V1.0** | **2026-07-20** | 首版：占位骨架 + 真 LICENSE + README + Layer 2/3 完整 |