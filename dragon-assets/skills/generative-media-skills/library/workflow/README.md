# library/workflow · 占位骨架（N 个 SKILL.md 待 mirror）

> **Layer 1 镜像状态**：占位目录
> **来源**：SamurAIGPT/Generative-Media-Skills/workflow/
> **激活条件**：拿到 `MUAPI_API_KEY` 后批量 mirror

---

## 待补的典型 workflow SKILL.md

| # | 类别 | 文件 | 说明 |
|---|------|------|------|
| 1 | 批量生成 | `batch-image.md` | 1 prompt → N 张图 |
| 2 | 批量生成 | `batch-video.md` | 1 脚本 → N 段视频 |
| 3 | 风格迁移 | `style-transfer-image.md` | A 风格 → B 风格 |
| 4 | 风格迁移 | `style-transfer-video.md` | A 风格 → B 风格 |
| 5 | 角色一致性 | `character-consistency.md` | 多镜头同角色 |
| 6 | 多镜头叙事 | `multi-shot-story.md` | 1 脚本 → 8 镜头连贯视频 |
| 7 | 工作流编排 | `dag-workflow.md` | DAG 编排（image → video → audio）|
| 8 | 工作流编排 | `pipeline-as-skill.md` | skill 链式调用 |

---

**Why**：workflow 是「UGC 视频化 + 老李风分镜工业化」的 orchestration 入口。
**How to apply**：调用方走 `../../async-task-pattern/` 链式调用，或自定义编排脚本。