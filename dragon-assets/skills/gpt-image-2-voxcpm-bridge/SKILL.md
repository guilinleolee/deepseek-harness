---
name: gpt-image-2-voxcpm-bridge
description: 图文音三位一体桥接器 - 把 gpt-image-2 视觉 + VoxCPM2 音频 + 文案脚本 一站式编排到下游生成技能（Mond / Baoyu / Smart-illustrator / Seedance / VoxCPM）. Use when user asks "图文音桥接", "海报+配音", "短视频一站式", "博主全息克隆", "voxcpm+image", "图生音", "三模态", "video+voice", "tts + image", "voxcpm bridge".
version: 1.0.0
author: 天龙引擎集成
depends: - gpt-image-2-bridge V1.0
- voxcpm-tts-integration V1.0
upstream: - gpt-image-2-style-library V2.0
- gpt-image-2-gallery-explorer V1.0
- voxcpm-voice-distillery V1.0
downstream: - qiaomu-mondo-poster-design
- baoyu-cover-image
- smart-illustrator
- seedance2-skill
- voxcpm-tts-integration
license: MIT
last_updated: 2026-06-26
triggers: ["gpt image 2 voxcpm bridge", "gpt-image-2-voxcpm-bridge · V1.0 图文音三位一体桥接器"]
---

# gpt-image-2-voxcpm-bridge · V1.0 图文音三位一体桥接器

## L0: 一句话描述 (≤15字)

**图文音三模态 → 5 下游 skill 桥接**

## L1: 使用场景 (50-100字)

V1.0 新增能力：把 gpt-image-2 视觉模板 + VoxCPM2 音频 + 文案脚本 三模态资产自动编排到 5 个下游生成技能。覆盖海报+配音、封面+语音、章节配图+有声、配音+短视频剧本、纯音频配音五大场景。比 gpt-image-2-bridge 多 1 个 tts_voxcpm adapter，并实现图文音协同打分。

## L2: 详细文档

### V1.0 核心能力

| 维度 | 能力 |
|------|------|
| **三模态输入** | 文案脚本 + 视觉模板 + 音频参数 |
| **5 个 Adapter** | cover_mondo / cover_baoyu / illustrations / storyboard / **tts_voxcpm** ⭐NEW |
| **协同打分** | 图音匹配度 / 文案与音频情绪匹配 / 多模态一致性 |
| **博主全息克隆** | 与 voxcpm-voice-distillery V1.0 联动，文+图+音一体化 |
| **多语言出海** | 同脚本 → 39 语种音频 → 9 平台视觉适配 |
| **场景联动** | 11 类工作流场景（电商详情/课程视频/公众号/...）|

### 5 个 Adapter（同构扩展 gpt-image-2-bridge）

| Adapter | 下游 skill | 输入 | 输出 |
|---------|-----------|------|------|
| **cover_mondo** | qiaomu-mondo-poster-design | 文案 + 视觉模板 | PNG 海报（可选配 VoxCPM 音频 demo）|
| **cover_baoyu** | baoyu-cover-image | 文案 + 视觉模板 | 公众号封面（可选配音频二维码）|
| **illustrations** | smart-illustrator | 文案 + 视觉模板 | N 张配图（可选配音脚本）|
| **storyboard** | seedance2-skill | 文案 + 视觉模板 | N 镜头剧本 + **角色声音设计** ⭐NEW |
| **tts_voxcpm** ⭐NEW | voxcpm-tts-integration | 文案 + 音频参数 | WAV 配音（可选克隆参考）|

### 与 gpt-image-2-bridge 的关系

| 维度 | gpt-image-2-bridge V1.0 | gpt-image-2-voxcpm-bridge V1.0 |
|------|------------------------|-------------------------------|
| 上游资产 | 图 + 文案 | 图 + 文案 + **音频** |
| Adapter 数 | 4 | **5** (+tts_voxcpm) |
| 多模态协同 | 无 | **图文音协同打分** |
| 博主克隆 | 仅视觉指纹 | **文+图+音全息克隆** |
| 多语言出海 | 9 平台 | **9 平台 × 39 语种** |

### 11 类工作流场景

| # | 场景 | 文案 | 视觉 | 音频 | 主 Adapter |
|---|------|------|------|------|-----------|
| 1 | **小红书图文爆款** | ✅ | ✅ | 可选（语音笔记）| cover_mondo + tts_voxcpm |
| 2 | **公众号封面文章** | ✅ | ✅ | 可选（音频版）| cover_baoyu + tts_voxcpm |
| 3 | **抖音短视频** | ✅ | ✅（分镜）| ✅（配音）| storyboard + tts_voxcpm |
| 4 | **博主视频号自动化** | ✅ | ✅（封面）| ✅（克隆博主声）| storyboard + tts_voxcpm |
| 5 | **电商详情页** | ✅ | ✅（多图）| ❌ | illustrations |
| 6 | **有声书** | ✅ | ✅（章节图）| ✅（角色声）| illustrations + tts_voxcpm |
| 7 | **课程视频** | ✅ | ✅（PPT）| ✅（讲解声）| illustrations + tts_voxcpm |
| 8 | **多语言出海广告** | ✅ | ✅ | ✅（39 语种）| cover_mondo + tts_voxcpm |
| 9 | **播客封面+音频** | ❌ | ✅ | ✅ | tts_voxcpm + cover_baoyu |
| 10 | **直播带货切片** | ✅ | ✅ | ✅（主播声）| storyboard + tts_voxcpm |
| 11 | **有声 PPT / 数据报告** | ✅ | ✅（图表）| ✅（讲解）| illustrations + tts_voxcpm |

### 数据结构（统一 schema）

```json
{
  "scenario": "博主视频号自动化",
  "task_id": "task_abc123",
  "inputs": {
    "script": "今天我们来聊一聊AI如何改变内容创作...",
    "language": "zh",
    "dialect": "auto",
    "duration_seconds": 60
  },
  "visual": {
    "template": "storyboard-cinematic-v1",
    "style_category": "Scenes & Storytelling",
    "reference_case_id": "case-310"
  },
  "audio": {
    "mode": "hifi_clone",
    "voice_description": null,
    "reference_wav_path": "/path/to/blogger.wav",
    "matched_template": "知识区",
    "consent_file": "./consent.txt"
  },
  "adapters": [
    {
      "adapter": "storyboard",
      "downstream_skill": "seedance2-skill",
      "prompt": "<完整 storyboard prompt>",
      "output_format": "Markdown + N shots",
      "filename": "storyboard_task_abc123.md"
    },
    {
      "adapter": "tts_voxcpm",
      "downstream_skill": "voxcpm-tts-integration",
      "prompt": "<完整 tts prompt>",
      "output_format": "WAV 48000Hz",
      "filename": "voice_task_abc123.wav"
    }
  ],
  "consistency_score": 0.87,
  "watermark": "ai_generated_multi_modal"
}
```

### 协同打分算法

**图文音一致性分（0-1）**：
- 文案情绪 vs 视觉情绪（基于色温/构图）：40%
- 文案情绪 vs 音频情绪（音色描述匹配）：30%
- 视觉风格 vs 音频风格（舒缓=慢语速）：20%
- 语言一致性（zh/en/ja）：10%

### 与 voxcpm-voice-distillery 联动

```bash
# 完整博主克隆流水线
python scripts/bridge.py \
  --scenario "博主视频号自动化" \
  --blogger-audio ./blogger_sample.wav \
  --consent-file ./consent.txt \
  --script "今天我们来聊..." \
  --visual-template "storyboard-cinematic-v1"
```

**自动流程**：
1. 调用 voxcpm-voice-distillery 提取博主声音指纹
2. 调用 gpt-image-2-style-library 匹配视觉模板
3. 调用 voxcpm-tts-inference 用 hifi_clone 模式生成配音
4. 调用 seedance2-skill 生成 storyboard
5. 输出文+图+音三模态 manifest

### CLI 选项

```bash
python scripts/bridge.py [options]

场景:
  --scenario SCENARIO        11 类工作流场景之一
  --script TEXT              文案脚本
  --language LANG            zh|en|ja|...（默认 auto）
  --duration INT             时长（秒）

视觉:
  --visual-template ID       视觉模板 ID
  --style-category CAT       12 类目之一
  --reference-case ID        参考案例 ID

音频:
  --audio-mode MODE          tts|voice_design|controllable_clone|hifi_clone
  --voice-desc TEXT          音色描述
  --reference-wav PATH       参考音频
  --blogger-audio PATH       博主音频（触发 distillery）
  --consent-file PATH        同意书（克隆模式必需）

输出:
  --adapters A [A ...]       指定 adapter（默认按场景）
  --output-dir DIR           输出目录（默认 ./bridge_output/）
  --dry-run                  只生成配置不调 API

伦理:
  --watermark                添加 AI 水印（默认开启）

其他:
  --verbose                  详细输出
  --json                     输出 JSON
```

### 测试覆盖

`tests/test_bridge.py` 包含 10 个测试用例：
- ✅ 5 adapter 输出 schema 验证
- ✅ 11 工作流场景索引
- ✅ 协同打分算法（4 维度）
- ✅ 文图音一致性 mock
- ✅ 博主克隆流水线（distillery → bridge）
- ✅ 39 语种路由
- ✅ 伦理护栏（consent / watermark）
- ✅ 与 gpt-image-2-bridge 同构 schema 对齐
- ✅ Dry-run 模式
- ✅ CLI 参数解析

### 风险点

1. **三模态一致性**：打分算法基于规则，覆盖 70% 场景，剩余需人工 review
2. **音频延迟**：VoxCPM 实时合成约 0.3 RTF，60 秒视频需 ~18 秒生成
3. **存储成本**：三模态资产叠加，单条内容约 50-100 MB
4. **克隆伦理**：强制 consent_file，但跨平台分发需用户自行合规审查

### 安装与依赖

```bash
# 上游依赖
ls ~/.claude/skills/gpt-image-2-bridge/
ls ~/.claude/skills/voxcpm-tts-integration/
ls ~/.claude/skills/voxcpm-voice-distillery/
ls ~/.claude/skills/gpt-image-2-style-library/

# 下游依赖（按需）
pip install voxcpm  # VoxCPM Python SDK
```

### 协同矩阵

| 上下游 | 关系 |
|--------|------|
| ↑ gpt-image-2-style-library V2.0 | 视觉模板 |
| ↑ gpt-image-2-gallery-explorer V1.0 | 视觉案例 |
| ↑ voxcpm-tts-integration V1.0 | TTS 推理 |
| ↑ voxcpm-voice-distillery V1.0 | 博主声音蒸馏 |
| ↔ gpt-image-2-bridge V1.0 | 共享 4 视觉 adapter |
| ↓ qiaomu-mondo-poster-design | 海报 |
| ↓ baoyu-cover-image | 公众号封面 |
| ↓ smart-illustrator | 章节配图 |
| ↓ seedance2-skill | 短视频剧本 |
| ↓ voxcpm-tts-integration | 配音 |

### 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| **V1.0** | **2026-06-26** | **首版：5 adapter / 11 场景 / 文图音协同打分 / 博主全息克隆** |

### 版本信息

- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **License**: MIT
- **Last Updated**: 2026-06-26