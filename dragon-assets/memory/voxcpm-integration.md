---
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---
# VoxCPM2 完整集成 · 详细记忆（voxcpm-integration.md）

> **状态**：天龙引擎 6 阶段第 2 阶段（2026-06-26 完成）
> **MEMORY.md 指针**：1 行 + 本文件
> **本文件目的**：抽离 MEMORY.md 详细记忆，让 MEMORY.md 压回 ≤200 行

---

## 触发源

[OpenBMB/VoxCPM](https://github.com/OpenBMB/VoxCPM) - **31.7k ⭐ / 3.6k Fork**（⭐ GitHub Trending #1），基于 MiniCPM-4 的 TTS 系统：**2B 参数 / 30 语言 + 9 中文方言 / 48kHz 高保真 / 6 部署栈**。

---

## 阶段 1：3 个新 Skill（已完成）

| skill | 路径 | 核心能力 |
|-------|------|---------|
| **voxcpm-tts-integration** ⭐NEW | `~/.claude/skills/voxcpm-tts-integration/` | 6 部署栈 / 4 调用模式 / 30 语言 + 9 方言 / 5 维音色设计 / 伦理护栏 |
| **voxcpm-voice-distillery** ⭐NEW | `~/.claude/skills/voxcpm-voice-distillery/` | 6 维声音指纹 / 10 套博主模板 / LoRA 训练包 / 强制 consent |
| **gpt-image-2-voxcpm-bridge** ⭐NEW | `~/.claude/skills/gpt-image-2-voxcpm-bridge/` | 5 adapter（+tts_voxcpm）/ 11 工作流场景 / 文图音协同打分（≥0.85 自动通过）|

---

## 阶段 2：4 个岗位 V 升级（已完成）

| 岗位 | 文件 | 版本 | 核心升级 |
|------|------|------|----------|
| **35-05 短视频编导** | `agents/35-05-video-director-v102-voxcpm.md` | V10.1 → **V10.2** | VoxCPM 配音工业化 / 博主声克隆视频 / Storyboard+TTS 联动 / 多语言出海 |
| **35-06 博主蒸馏分析师** | `agents/35-06-blogger-distiller-v11-voxcpm.md` | V1.0 → **V1.1** | 6 维视觉 → **7 维全息（+声音）**/ 博主全息克隆 / 跨模态打分 |
| **35-02 社媒运营** | `agents/35-02-social-media-v132-voxcpm.md` | V13.1 → **V13.2** | 9 平台 × 39 语种方言矩阵 / 方言爆款 / 博主视频号自动化 |
| **28-01 文案策划** | `agents/28-01-copywriter-v102-voxcpm.md` | V10.1 → **V10.2** | 文本→配音直通车 / 声音名片模板 / 39 语种文案矩阵 |

---

## 阶段 3：1 bridge 扩展（已完成）

- **gpt-image-2-bridge V1.0 → V1.1** — 引用 gpt-image-2-voxcpm-bridge V1.0（5 adapter），4 视觉 adapter 100% 同名同结构，新增 `tts_voxcpm` 第 5 adapter。

---

## 累计验证

- A1 voxcpm-tts-integration: **15/15 PASS**
- A2 voxcpm-voice-distillery: **10/10 PASS**
- A3 gpt-image-2-voxcpm-bridge: **12/12 PASS**
- 原 gpt-image-2-bridge: **8/8 PASS**（升级未破坏兼容）
- **总计：45/45 PASS / 0 FAIL**

---

## 核心数字

- **39 语种方言**（30 全球语言 + 9 中文方言）
- **6 部署栈**（PyTorch / Nano-VLLM / vLLM-Omni / ComfyUI / Web Demo / LoRA）
- **10 套博主音色模板**（治愈系/知识区/搞笑博主/带货主播/影视解说/美食博主/科技评测/二次元/母婴/古风）
- **5 adapter**（cover_mondo / cover_baoyu / illustrations / storyboard / **tts_voxcpm**）
- **11 工作流场景**（小红书/公众号/抖音/博主视频号/电商/有声书/课程/出海广告/播客/直播带货/有声PPT）
- **7 维全息指纹**（构图/色彩/字体/材质/光线/隐喻/声音）
- **351 条爆款内容/脚本**（9 平台 × 39 语种）

---

## 战略价值

- **图文音三模态闭环**：从图文双模态 → 文图音三模态，与 GPT-Image-2 形成对称升级
- **博主全息克隆**：35-06 V1.1 的 7 维指纹（文+图+音）让博主克隆从风格层升级到本人层
- **39 语种出海**：单脚本 → 351 条爆款矩阵，比肩头部 MCN 工业化产能
- **博主克隆成本**：~$0.19/条（比真人拍摄低 99%）

---

## 关键文件路径

| 路径 | 说明 |
|------|------|
| `C:\Users\li\.claude\skills\voxcpm-tts-integration\SKILL.md` | 6 部署栈 / 30 语种 + 9 方言 |
| `C:\Users\li\.claude\skills\voxcpm-voice-distillery\SKILL.md` | 6 维声音指纹 / 10 套博主模板 |
| `C:\Users\li\.claude\skills\gpt-image-2-voxcpm-bridge\SKILL.md` | 5 adapter（含 tts_voxcpm 第 5 个）|
| `C:\Users\li\.claude\projects\dragon-engine\agents\35-05-video-director-v102-voxcpm.md` | V10.2 短视频编导 |
| `C:\Users\li\.claude\projects\dragon-engine\agents\35-06-blogger-distiller-v11-voxcpm.md` | V1.1 博主蒸馏 |
| `C:\Users\li\.claude\projects\dragon-engine\agents\35-02-social-media-v132-voxcpm.md` | V13.2 社媒运营 |
| `C:\Users\li\.claude\projects\dragon-engine\agents\28-01-copywriter-v102-voxcpm.md` | V10.2 文案策划（基线，被 V10.3 继承）|

---

## 关键参考（不重复）

| 资产 | 链接 |
|------|------|
| OpenBMB/VoxCPM (31.7k ⭐) | https://github.com/OpenBMB/VoxCPM |
| MiniCPM-4 基座 | https://github.com/OpenBMB/MiniCPM |
| 上游阶段 gpt-image-2 集成 | `gpt-image-2-integration.md` |
| 下游阶段 khazix 集成 | `khazix-integration.md` |

---

## 后续阶段协同

- **stage 14 baoyu-skills 全集 21/21**（2026-07-17）→ [baoyu-skills-integration.md](baoyu-skills-integration.md)

## 版本信息

- **整合日期**: 2026-06-26
- **触发源**: OpenBMB/VoxCPM (31.7k ⭐)
- **新资产**: 3 个新 skill + 4 个 V 升级 + 1 个 bridge 扩展
- **累计验证**: 45/45 PASS
- **MEMORY.md 行数**: 治理前置阶段
- **战略价值**: 图文音三模态闭环 / 博主全息克隆 / 39 语种出海
