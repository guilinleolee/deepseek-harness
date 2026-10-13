# library/edit · 占位骨架（N 个 SKILL.md 待 mirror）

> **Layer 1 镜像状态**：占位目录
> **来源**：SamurAIGPT/Generative-Media-Skills/edit/
> **激活条件**：拿到 `MUAPI_API_KEY` 后批量 mirror

---

## 待补的典型 edit SKILL.md

| # | 类别 | 文件 | 说明 |
|---|------|------|------|
| 1 | 图像编辑 | `outpaint.md` | 扩图（左侧/右侧/四周）|
| 2 | 图像编辑 | `inpaint.md` | 局部重绘 |
| 3 | 图像编辑 | `upscale-4x.md` | 4 倍超分 |
| 4 | 图像编辑 | `upscale-8x.md` | 8 倍超分 |
| 5 | 图像编辑 | `background-removal.md` | 抠图 |
| 6 | 图像编辑 | `colorize.md` | 上色 |
| 7 | 视频编辑 | `video-cut.md` | 智能剪辑 |
| 8 | 视频编辑 | `video-subtitle.md` | 字幕生成 |
| 9 | 视频编辑 | `video-translate.md` | 视频翻译配音 |

---

**Why**：edit 是后期处理（小红书封面裁切、视频粗剪、超分）的多模态 fallback。
**How to apply**：调用方走 `../../async-task-pattern/adapters/muapi.sh submit --action <edit>`。