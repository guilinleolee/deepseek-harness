# library/motion · 占位骨架（22 个 SKILL.md 待 mirror）

> **Layer 1 镜像状态**：占位目录
> **来源**：SamurAIGPT/Generative-Media-Skills/motion/
> **激活条件**：拿到 `MUAPI_API_KEY` 后批量 mirror

---

## 待补的 22 个 motion SKILL.md（视频生成）

| # | 模型 | 提供方 | 适用场景 |
|---|------|--------|---------|
| 1 | ugc-video-factory | muapi | UGC 短视频工业化 ⭐（L3 spec 待激活）|
| 2 | seedance-2 | ByteDance | 老李风电影级分镜 ⭐（L3 spec 待激活）|
| 3 | runway-gen3 | Runway | 高端广告 / MV |
| 4 | luma-dream-machine | Luma | 物理真实感 |
| 5 | pika-1.5 | Pika | 角色动画 |
| 6 | sora | OpenAI | 长视频 / 复杂场景 |
| 7 | kling-1.6 | Kuaishou | 国产高质量 |
| 8 | cogvideo-x | Zhipu | 开源可控 |
| 9 | hunyuan-video | Tencent | 国产开源 |
| 10 | wan-2.1 | Alibaba | 国产开源 |
| 11 | veo-2 | Google | 高端影视 |
| 12 | minimax-video | MiniMax | M3 内置（备用）|
| 13 | vidu-2.0 | Baidu | 国产角色动画 |
| 14 | hailuo-2.0 | MiniMax | 国产（备用）|
| 15 | animate-anyone | alibaba | 角色一致性 |
| 16 | magic-animate | Bytedance | 动作迁移 |
| 17 | stable-video-diffusion | StabilityAI | 开源长视频 |
| 18 | pixverse | PixVerse | 国产创意 |
| 19 | morph-1.0 | Morph | 短视频 |
| 20 | genmo-replay | Genmo | 创意视频 |
| 21 | leiapix | Leia | 3D 照片 |
| 22 | capcut-magic | ByteDance | 剪映魔法 |

---

**Why**：motion 是 35-05 V11 老李风视频 + 35-06 V1.3 UGC 视频化的多模态 fallback 主入口。
**How to apply**：调用方走 `../../cinema-director-laoli/scripts/generate.sh`（老李风）或 `../../async-task-pattern/adapters/muapi.sh submit --action <model>`。