---
name: voxcpm-multi-speaker
description: VoxCPM2 多说话人对话生成（多人配音 + 对话脚本编排 + 角色一致性 + 跨说话人切换）. Use when user asks "多说话人", "multi-speaker", "多人配音", "对话生成", "有声书多角色", "广播剧", "访谈节目", "播客多嘉宾", "voxcpm 多声", "角色对话", "speech dialogue".
version: 1.0.0
author: 天龙引擎集成
depends: - voxcpm-tts-integration V1.0
- voxcpm-voice-distillery V1.0
upstream: - OpenBMB/VoxCPM (31.7k ⭐)
license: Apache-2.0 + MIT
last_updated: 2026-06-27
triggers: ["voxcpm multi speaker", "voxcpm-multi-speaker · V1.0 多说话人对话生成"]
---

# voxcpm-multi-speaker · V1.0 多说话人对话生成

## L0: 一句话描述 (≤15字)

**多说话人对话 + 跨角色一致性**

## L1: 使用场景 (50-100字)

当用户需要生成包含多个角色的对话音频（如有声书、广播剧、访谈节目、播客多嘉宾），或需要确保多个角色间的声音一致性和自然切换时，使用本 skill。支持 4 种角色定义方式（音色设计/参考音频/声音指纹/预设模板）、对话脚本 DSL、自动停顿与语气切换。

## L2: 详细文档

### V1.0 核心能力

| 维度 | 能力 |
|------|------|
| **4 种角色定义** | voice_design / reference_audio / fingerprint / preset_template |
| **角色数量** | 支持 2-10 个角色同场景 |
| **对话脚本 DSL** | JSON/YAML 格式，含角色标签 + 文本 + 情绪 + 停顿 |
| **跨角色一致性** | 角色音色锁定，不漂移 |
| **自动停顿** | 标点驱动 + 说话人间 200ms 静音 |
| **拼接输出** | 单 WAV 文件，含时间戳 manifest |

### 4 种角色定义方式

| 方式 | 适用 | 示例 |
|------|------|------|
| **voice_design** | 无参考音频，凭空设计 | `(年轻女性,温柔甜美)` |
| **reference_audio** | 有清晰音频样本 | `reference.wav` + prompt_text |
| **fingerprint** | 已蒸馏过的博主指纹 | `fingerprint_id: tech_blogger_01` |
| **preset_template** | 用 10 套博主模板 | `preset: 治愈系` |

### 对话脚本 DSL (JSON Schema)

```json
{
  "title": "深夜电台访谈",
  "language": "zh",
  "speakers": {
    "host": {
      "definition": "preset_template",
      "preset": "治愈系",
      "voice_description": "(中年女性,声音温柔,语速慢)"
    },
    "guest": {
      "definition": "fingerprint",
      "fingerprint_id": "tech_blogger_01",
      "consent_file": "./consent.txt"
    }
  },
  "dialogue": [
    {"speaker": "host", "text": "欢迎来到深夜电台...", "emotion": "温柔", "pause_ms": 500},
    {"speaker": "guest", "text": "大家好,我是...", "emotion": "理性", "pause_ms": 300},
    {"speaker": "host", "text": "今天我们来聊...", "emotion": "平静", "pause_ms": 200},
    ...
  ],
  "output": {
    "format": "wav",
    "sample_rate": 48000,
    "merge_strategy": "sequential",  // sequential / parallel
    "silence_between_speakers_ms": 200
  }
}
```

### 6 类预设场景

| 场景 | 角色数 | 典型应用 |
|------|-------|---------|
| **访谈节目** | 2 | 1 主持 + 1 嘉宾 |
| **播客多嘉宾** | 3-5 | 1 主持 + 2-4 嘉宾 |
| **有声书** | 2-10 | 旁白 + 多角色 |
| **广播剧** | 3-8 | 多角色对戏 |
| **辩论节目** | 2-4 | 正反方 + 主持 |
| **教学对话** | 2 | 老师 + 学生 |

### 工作流（5 阶段）

```
输入: 对话脚本（JSON/YAML）
   │
   ▼
Step 1: 解析对话脚本
   → 校验 speakers + dialogue schema
   → 提取每个说话人的 definition 类型
   │
   ▼
Step 2: 加载角色定义
   - voice_design → 用 voxcpm-tts-integration 5 维描述
   - reference_audio → 用 voxcpm hifi_clone 模式
   - fingerprint → 调用 voxcpm-voice-distillery 加载 LoRA
   - preset_template → 套用 10 套博主模板
   │
   ▼
Step 3: 顺序合成（per utterance）
   $ python ~/.claude/skills/voxcpm-tts-integration/scripts/voxcpm.py \
     --text "..." \
     --mode <voice_design|hifi_clone> \
     --voice-desc "..." \
     --reference-wav "..." \
     --consent-file "..." \
     --output utt_001.wav
   │
   ▼
Step 4: 拼接 + 停顿插入
   - sequential：按 dialogue 顺序拼接
   - 说话人间插入 200ms 静音（可配置）
   - 标点驱动自然停顿（句号 500ms / 逗号 200ms）
   │
   ▼
Step 5: 输出 manifest
   - 单 WAV 文件
   - JSON manifest（含时间戳、角色、文本）
```

### 数据结构（输出）

```json
{
  "output_wav": "dialogue_final.wav",
  "duration_seconds": 312.5,
  "sample_rate": 48000,
  "speakers_used": ["host", "guest"],
  "utterances": [
    {
      "index": 1,
      "speaker": "host",
      "text": "欢迎来到深夜电台",
      "start_seconds": 0.0,
      "end_seconds": 3.5,
      "wav_path": "utt_001.wav",
      "mode": "voice_design"
    },
    ...
  ],
  "manifest_path": "dialogue_manifest.json"
}
```

### CLI 选项

```bash
python scripts/multi_speaker.py [options]

输入:
  --script PATH              对话脚本路径（JSON/YAML，必需）
  --speakers ID [ID ...]     指定只生成部分说话人（默认全部）

输出:
  --output PATH              输出 wav 路径（默认 ./dialogue_final.wav）
  --manifest PATH            manifest JSON 路径
  --sample-rate INT          采样率（默认 48000）
  --silence-ms INT           说话人间静音（默认 200）
  --merge-strategy STR       sequential|parallel（默认 sequential）

模型:
  --device DEVICE            auto|cpu|cuda
  --backend BACKEND          pytorch|nano_vllm|vllm_omni

伦理:
  --consent-file PATH        同意书（fingerprint/reference_audio 必需）

其他:
  --dry-run                  只解析不合成
  --verbose                  详细输出
  --json                     输出 JSON
```

### 6 套预设对话模板

| # | 模板 | 角色 | 应用 |
|---|------|------|------|
| 1 | **访谈节目** | 1 主持 + 1 嘉宾 | 知识访谈/娱乐访谈 |
| 2 | **播客 3 人** | 1 主持 + 2 嘉宾 | 圆桌讨论 |
| 3 | **有声书·旁白+主角** | 旁白 + 主角 | 小说/传记 |
| 4 | **有声书·多人** | 旁白 + 主角 + 配角 + 反派 | 长篇小说 |
| 5 | **广播剧** | 3-5 角色 | 剧本/段子 |
| 6 | **辩论节目** | 主持 + 正方 + 反方 | 辩论赛 |

### 与 voxcpm-voice-distillery 联动

**博主对谈**：2 个博主声克隆 + 1 个旁白

```bash
python ~/.claude/skills/voxcpm-multi-speaker/scripts/multi_speaker.py \
  --script dialogue_bloggers.yaml \
  --consent-file blogger_A_consent.txt \
  --consent-file blogger_B_consent.txt \
  --output dialogue_bloggers.wav
```

**YAML 示例**：
```yaml
title: 科技博主圆桌
language: zh
speakers:
  host:
    preset: 治愈系
    voice_desc: (中年男性,声音磁性专业)
  blogger_A:
    fingerprint_id: tech_blogger_01
    consent_file: ./A_consent.txt
  blogger_B:
    fingerprint_id: tech_blogger_02
    consent_file: ./B_consent.txt
dialogue:
  - speaker: host
    text: 大家好，欢迎来到科技圆桌
    emotion: 平静
    pause_ms: 500
  - speaker: blogger_A
    text: 我觉得AI的未来在于开源
    emotion: 理性
    pause_ms: 300
  - speaker: blogger_B
    text: 商业化才是关键
    emotion: 激动
    pause_ms: 200
  ...
```

### 测试覆盖

`tests/test_multi_speaker.py` 包含 10 个测试用例：
- ✅ 4 种角色定义方式
- ✅ 对话脚本 DSL 解析（JSON/YAML）
- ✅ 6 套预设场景模板
- ✅ 跨角色一致性验证
- ✅ 拼接与停顿算法
- ✅ 时间戳 manifest
- ✅ 伦理护栏（fingerprint 必需 consent）
- ✅ Dry-run 模式
- ✅ CLI 参数解析
- ✅ 与 voxcpm-tts-integration schema 对齐

### 风险与限制

1. **跨角色音色漂移**：每个 utterance 独立合成，长对话可能音色漂移 → 用 reference_audio + hifi_clone 模式缓解
2. **拼接不自然**：标点停顿 + 说话人间静音可缓解，但仍有"拼接感"
3. **角色数限制**：建议 ≤ 5 角色，超过可能音色管理困难
4. **硬件门槛**：长对话（>5 分钟）需较高显存

### 后续规划

- [ ] V1.1: 跨 utterance 音色缓存（一致性优化）
- [ ] V1.2: 实时多人对话流式输出
- [ ] V1.3: 情感联动（一方情绪影响另一方）

### 协同矩阵

| 上下游 | 关系 |
|--------|------|
| ↑ voxcpm-tts-integration V1.0 | 单 utterance 合成 |
| ↑ voxcpm-voice-distillery V1.0 | 角色指纹加载 |
| ↓ 有声书生成器 | 长篇有声书 |
| ↓ 播客剪辑工具 | 播客后期 |
| ↓ 35-05 短视频编导 V10.2 | 多角色短视频 |

### 版本信息

- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **License**: Apache-2.0 + MIT
- **Last Updated**: 2026-06-27