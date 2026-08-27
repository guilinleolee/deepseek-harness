# library/_core · 占位骨架（9 个 SKILL.md 待 mirror）

> **Layer 1 镜像状态**：占位目录
> **来源**：SamurAIGPT/Generative-Media-Skills/core/
> **激活条件**：拿到 `MUAPI_API_KEY` 后批量 mirror

---

## 待补的 9 个 _core SKILL.md

| # | 文件名 | 用途 | 优先级 |
|---|--------|------|--------|
| 1 | `async-task.md` | 异步任务原语（已抽取到 `../../async-task-pattern/`）| ✅ 已覆盖 |
| 2 | `muapi-client.md` | muapi.ai API client | ⏳ 待补 |
| 3 | `rate-limit.md` | 速率限制（429 / 5xx 重试）| ⏳ 待补 |
| 4 | `retry-strategy.md` | 指数退避 + 抖动 | ⏳ 待补 |
| 5 | `cache-strategy.md` | 任务结果本地缓存 | ⏳ 待补 |
| 6 | `prompt-builder.md` | prompt 模板构建器 | ⏳ 待补 |
| 7 | `file-handler.md` | 上传/下载文件统一处理 | ⏳ 待补 |
| 8 | `auth-handler.md` | 多 provider 认证统一管理 | ⏳ 待补 |
| 9 | `error-mapper.md` | provider 错误码 → async-task-pattern 退出码 | ⏳ 待补 |

---

**Why**：_core 9 个 SKILL.md 是其他库的底层支撑。async-task 已抽取到独立 skill，剩余 8 个待 mirror。
**How to apply**：调用方不应直接依赖本目录，应走 `../../async-task-pattern/` + `../../async-task-pattern/adapters/muapi.sh`。