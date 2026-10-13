# library/social · 占位骨架（7 个 SKILL.md 待 mirror）

> **Layer 1 镜像状态**：占位目录
> **来源**：SamurAIGPT/Generative-Media-Skills/social/
> **激活条件**：拿到 `MUAPI_API_KEY` 后批量 mirror

---

## 待补的 7 个 social SKILL.md（平台特定封面）

| # | 平台 | 文件 | 比例 |
|---|------|------|------|
| 1 | 小红书 | `rednote-cover` ⭐（L3 spec 待激活）| 3:4 + 1:1 |
| 2 | TikTok | `tiktok-cover` | 9:16 |
| 3 | 微博 | `weibo-cover` | 16:9 |
| 4 | YouTube | `youtube-thumbnail` | 16:9 |
| 5 | LinkedIn | `linkedin-banner` | 4:1 |
| 6 | 公众号 | `wechat-cover` | 21:9 + 1:1 |
| 7 | Instagram | `instagram-cover` | 1:1 + 9:16 |

---

**Why**：social 是「直接出 9 平台封面」专用，避免调用方手动调 prompt 选比例。
**How to apply**：调用方走 `../../async-task-pattern/adapters/muapi.sh submit --action rednote-cover`（待激活）。