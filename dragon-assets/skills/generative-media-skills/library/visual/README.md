# library/visual · 占位骨架（26 个 SKILL.md 待 mirror）

> **Layer 1 镜像状态**：占位目录
> **来源**：SamurAIGPT/Generative-Media-Skills/visual/
> **激活条件**：拿到 `MUAPI_API_KEY` 后批量 mirror

---

## 待补的 26 个 visual SKILL.md（图像生成）

| # | 模型 | 提供方 | 适用场景 |
|---|------|--------|---------|
| 1 | nano-banana | Google | ⭐ 推理 brief（已抽到 `../../nano-banana-brief/`）|
| 2 | gpt-image-2 | OpenAI | ⭐ 主力（已抽到 `../../async-task-pattern/adapters/gpt-image-2.sh`）|
| 3 | midjourney-v7 | Midjourney | 高端艺术 |
| 4 | flux-1.1-pro | Black Forest Labs | 写实人像 |
| 5 | stable-diffusion-3.5 | StabilityAI | 开源可控 |
| 6 | recraft-v3 | Recraft | 矢量图 / 设计 |
| 7 | ideogram-2.0 | Ideogram | 文字渲染 |
| 8 | leonardo-phoenix | Leonardo | 创意游戏 |
| 9 | dall-e-3 | OpenAI | 通用 |
| 10 | imagen-3 | Google | 写实 |
| 11 | kling-image | Kuaishou | 国产高质量 |
| 12 | minimax-image | MiniMax | M3 内置 |
| 13 | qwen-vl-image | Alibaba | 国产多模态 |
| 14 | cogview-3 | Zhipu | 国产开源 |
| 15 | hunyuan-image | Tencent | 国产 |
| 16 | seedream-2.0 | ByteDance | 国产（备用）|
| 17 | doubao-image | ByteDance | 国产 |
| 18 | playground-v3 | Playground | 创意 |
| 19 | artbreeder | Artbreeder | 风格融合 |
| 20 | lexica | Lexica | 开源搜索 |
| 21 | civitai | Civitai | 社区 |
| 22 | bria | Bria | 商业安全 |
| 23 | adobe-firefly | Adobe | 商业集成 |
| 24 | canva-magic | Canva | 设计自动化 |
| 25 | getimg | GetIMG | 通用 |
| 26 | vector-ai | VectorAI | 矢量专用 |

---

**Why**：visual 是小红书图文 + 公众号封面 + 海报视觉的多模态 fallback 主入口。
**How to apply**：调用方走 `../../nano-banana-brief/scripts/generate.sh`（4 维推理 brief）或 `../../async-task-pattern/adapters/muapi.sh submit --action <model>`。