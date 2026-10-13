---
name: voxcpm-voice-distillery
description: VoxCPM2 博主声音指纹蒸馏（5-10 分钟音频 → LoRA 适配 + 6 维声音指纹 + 全息克隆）. Use when user asks "博主声音克隆", "声音蒸馏", "voice fingerprint", "博主声音复刻", "音频 LoRA 微调", "voxcpm LoRA", "博主全息克隆", "博主声音指纹", "Blogger voice clone".
version: 1.0.0
author: 天龙引擎集成
depends: - voxcpm-tts-integration V1.0
upstream: - 35-06 博主蒸馏分析师 V1.1
- OpenBMB/VoxCPM (31.7k ⭐)
license: Apache-2.0 + MIT
last_updated: 2026-06-26
triggers: ["voxcpm voice distillery", "voxcpm-voice-distillery · V1.0 天龙引擎集成版"]
---

# voxcpm-voice-distillery · V1.0 天龙引擎集成版

## L0: 一句话描述 (≤15字)

**博主声音指纹蒸馏 → VoxCPM LoRA 适配**

## L1: 使用场景 (50-100字)

当用户需要把某个博主/角色的声音反向工程，提取 6 维声音指纹（音色/语速/方言/情绪/韵律/用词），并产出 VoxCPM2 LoRA 微调包以实现工业化复制时，使用本 skill。配套 35-06 博主蒸馏分析师 V1.1 形成"全息克隆"链路（文+图+音）。

## L2: 详细文档

### V1.0 核心能力

| 维度 | 能力 |
|------|------|
| **6 维声音指纹** | 音色 timbre / 语速 speed / 方言 dialect / 情绪 emotion / 韵律 prosody / 用词 vocabulary |
| **指纹模板** | 10 套预置模板（治愈系 / 知识区 / 搞笑博主 / 带货主播 / 影视解说 / 美食博主 / 科技评测 / 二次元 / 母婴 / 古风）|
| **音频输入** | 5-10 分钟干净音频（自动 VAD 切句 / 降噪）|
| **指纹提取** | Whisper 转写 + 声学分析（基频 F0 / 共振峰 / 语速）→ 6 维指纹 |
| **LoRA 微调** | 生成 VoxCPM2 LoRA 训练包 + 配置文件 + WebUI 启动脚本 |
| **伦理护栏** | 强制 consent 文件 + 博主身份验证 + AI 标注 |
| **集成下游** | 35-06 博主蒸馏分析师 V1.1 / voxcpm-tts-integration V1.0 |

### 6 维声音指纹模型

| 维度 | 描述 | 提取方法 | 量化指标 |
|------|------|---------|---------|
| **音色 (Timbre)** | 声带特征/共振峰分布 | pyworld 频谱分析 | F1/F2/F3 频率（Hz）+ Spectral Centroid |
| **语速 (Speed)** | 字符/秒 | Whisper 时间戳 | 平均语速 + 标准差 |
| **方言 (Dialect)** | 地域口音 | 关键词识别 + ASR 置信度 | "普通话/粤语/川话/..." |
| **情绪 (Emotion)** | 主导情绪 | 音频能量 + 频谱特征 | "开心/平静/严肃/激动..." |
| **韵律 (Prosody)** | 音高变化/重音模式 | pyworld F0 提取 | F0 均值 + 变化范围 |
| **用词 (Vocabulary)** | 口头禅/高频词 | jieba + 词频统计 | Top-20 高频词 + 口头禅标记 |

### 10 套博主音色模板

| # | 模板名 | 6 维特征简述 |
|---|--------|------------|
| 1 | **治愈系** | 音色:温柔 / 语速:慢 / 方言:普通话 / 情绪:平静 / 韵律:平稳 / 用词:温暖 |
| 2 | **知识区** | 音色:清晰 / 语速:中 / 方言:普通话 / 情绪:理性 / 韵律:抑扬顿挫 / 用词:专业 |
| 3 | **搞笑博主** | 音色:夸张 / 语速:快 / 方言:东北话 / 情绪:亢奋 / 韵律:夸张起伏 / 用词:网络梗 |
| 4 | **带货主播** | 音色:高亢 / 语速:极快 / 方言:普通话 / 情绪:激动 / 韵律:重音突出 / 用词:促销词 |
| 5 | **影视解说** | 音色:磁性 / 语速:中 / 方言:普通话 / 情绪:中性 / 韵律:故事化 / 用词:专业 |
| 6 | **美食博主** | 音色:亲切 / 语速:中 / 方言:川话/粤/... / 情绪:愉悦 / 韵律:停顿多 / 用词:拟声词 |
| 7 | **科技评测** | 音色:冷静 / 语速:稍快 / 方言:普通话 / 情绪:理性 / 韵律:稳定 / 用词:参数 |
| 8 | **二次元** | 音色:清亮 / 语速:快 / 方言:日式/中文 / 情绪:活泼 / 韵律:夸张 / 用词:ACG 词 |
| 9 | **母婴** | 音色:温柔 / 语速:慢 / 方言:普通话 / 情绪:温暖 / 韵律:起伏温和 / 用词:叠词 |
| 10 | **古风** | 音色:古典 / 语速:慢 / 方言:古汉语 / 情绪:悠远 / 韵律:古典 / 用词:文言 |

### 工作流（5 阶段）

#### 阶段 1: 音频采集与预处理
```bash
# 输入：5-10 分钟原始音频（mp3/wav/m4a）
python scripts/distill.py \
  --audio /path/to/blogger_raw.mp3 \
  --output ./distill_output/ \
  --mode full
```

**自动处理**：
- VAD（语音活动检测）切句
- 降噪（noisereduce / DNN 降噪）
- 静音剔除
- 采样率归一化（16kHz）
- 输出：`clean_chunks/*.wav`

#### 阶段 2: 转写与时间对齐
```bash
# 自动调用 Whisper-large-v3
python scripts/distill.py --audio ... --stage transcribe
```

**输出**：
- `transcript.json`：每段音频的时间戳 + 文本
- `transcript.srt`：SRT 字幕
- `word_timeline.json`：词级时间戳（用于语速分析）

#### 阶段 3: 6 维指纹提取
```bash
python scripts/distill.py --audio ... --stage fingerprint
```

**输出**（`fingerprint.json`）：
```json
{
  "timbre": {
    "f1_mean": 580.2,
    "f2_mean": 1620.5,
    "spectral_centroid": 2105.3,
    "label": "温柔/磁性"
  },
  "speed": {
    "chars_per_second": 5.8,
    "std": 1.2,
    "label": "中等"
  },
  "dialect": {
    "detected": "普通话",
    "confidence": 0.92,
    "features": ["儿化音", "轻声"]
  },
  "emotion": {
    "dominant": "平静",
    "distribution": {"平静": 0.65, "开心": 0.25, "激动": 0.10}
  },
  "prosody": {
    "f0_mean": 165.3,
    "f0_range": [85.2, 285.7],
    "stress_pattern": "抑扬顿挫"
  },
  "vocabulary": {
    "top_words": ["然后", "就是说", "真的", "对吧", ...],
    "catchphrases": ["对吧？", "你说是不是"],
    "style": "口语化/网络化"
  },
  "matched_template": "治愈系",
  "template_score": 0.87
}
```

#### 阶段 4: LoRA 训练包生成
```bash
python scripts/distill.py --audio ... --stage lora
```

**输出**（`lora_training/`）：
```
lora_training/
├── data/
│   ├── train_chunks/        # 训练音频切片
│   ├── train.txt            # 训练文本
│   └── val_chunks/          # 验证集
├── conf/
│   └── voxcpm_v2/
│       └── voxcpm_finetune_lora.yaml  # LoRA 配置
├── scripts/
│   └── train.sh             # 训练启动脚本
├── webui/
│   └── lora_ft_webui.py     # WebUI 训练入口
├── consent.txt              # 强制同意书
├── README.md                # 训练说明
└── fingerprint.json         # 同步指纹
```

**训练命令**：
```bash
cd lora_training/
python scripts/train_voxcpm_finetune.py \
  --config_path conf/voxcpm_v2/voxcpm_finetune_lora.yaml

# 或 WebUI
python webui/lora_ft_webui.py
# 打开 http://localhost:7860
```

**训练时长**：5-10 分钟音频 → 1-2 小时单卡 RTX 4090

#### 阶段 5: 推理与评估
```bash
# 使用训练好的 LoRA 推理
python ~/.claude/skills/voxcpm-tts-integration/scripts/voxcpm.py \
  --text "今天我们来聊聊..." \
  --mode hifi_clone \
  --prompt-audio lora_training/data/train_chunks/sample_001.wav \
  --prompt-text "原文转写" \
  --reference-audio lora_training/data/train_chunks/sample_001.wav \
  --consent-file ./consent.txt
```

### 伦理护栏 ⚠️

强制要求（缺一不可）：
1. ✅ `consent.txt` 同意书（博主本人或代理人签字）
2. ✅ 博主身份验证（邮箱/手机号/链接）
3. ✅ AI 生成水印（自动注入到 wav 文件）
4. ✅ 用途限制（仅限个人学习/已获授权用途）
5. ✅ 输出标注（文件 metadata 标记 "ai_cloned_voice"）

**默认黑名单**（自动拦截）：
- 政治人物
- 知名公众人物（未授权）
- 医疗/法律咨询（误导风险）

**审核流程**（建议）：
- 微调前 → 自动检查黑名单
- 推理时 → 强制 consent_file
- 部署时 → 在 README 标注伦理边界

### 与 35-06 博主蒸馏分析师 V1.1 联动

```
35-06 博主蒸馏分析师 V1.1（风格/选题/封面/声音 7 维蒸馏）
        ↓ 声音指纹调用
voxcpm-voice-distillery V1.0（6 维声音指纹 → LoRA 训练包）
        ↓ LoRA 模型
voxcpm-tts-integration V1.0（VoxCPM2 推理）
        ↓ 音频输出
gpt-image-2-voxcpm-bridge V1.0（图+音桥接到 4 下游）
```

**输出 7 维蒸馏报告**（35-06 V1.1）：
```json
{
  "fingerprint_v7": {
    "writing_style": "...",      // 文风
    "topic_preference": "...",   // 选题偏好
    "visual_style": "...",       // 视觉风格（封面/分镜）
    "cover_pattern": "...",      // 封面模式
    "posting_rhythm": "...",     // 发布节奏
    "engagement_tactic": "...",  // 互动策略
    "voice_fingerprint": {       // ⭐NEW V1.1
      "timbre": "...",
      "speed": "...",
      "dialect": "...",
      "emotion": "...",
      "prosody": "...",
      "vocabulary": "..."
    }
  }
}
```

### 数据结构

```python
# 输入
{
    "audio_path": "/path/to/blogger_raw.mp3",
    "blogger_id": "blogger_xxx",  # 内部 ID
    "blogger_name": "昵称",
    "consent_file": "./consent.txt",
    "mode": "full" | "fingerprint_only" | "lora_only",
    "output_dir": "./distill_output/",
}

# 输出
{
    "clean_chunks_dir": "./distill_output/clean_chunks/",
    "transcript_path": "./distill_output/transcript.json",
    "fingerprint": {...},  # 6 维指纹
    "lora_training_dir": "./distill_output/lora_training/",
    "matched_template": "治愈系",
    "template_score": 0.87,
    "training_estimate_hours": 1.5,
    "watermark": "ai_cloned_voice",
}
```

### CLI 选项

```bash
python scripts/distill.py [options]

输入:
  --audio PATH             原始音频路径（必需）
  --blogger-id ID          博主内部 ID
  --blogger-name NAME      博主昵称
  --consent-file PATH      同意书文件（必需）

输出:
  --output-dir DIR         输出目录（默认 ./distill_output/）

阶段:
  --stage STAGE            preprocess | transcribe | fingerprint | lora | all（默认 all）
  --mode MODE              full | fingerprint_only | lora_only（默认 full）

模板:
  --template NAME          强制指定模板（跳过自动匹配）
  --list-templates         列出 10 套博主模板

模型:
  --whisper-model NAME     Whisper 模型（默认 large-v3）
  --device DEVICE          auto|cpu|cuda（默认 auto）

伦理:
  --skip-watermark         跳过水印（不推荐）
  --dry-run                只分析不生成训练包

其他:
  --verbose                详细输出
  --json                   输出 JSON 格式
```

### 测试覆盖

`tests/test_distill.py` 包含 8 个测试用例：
- ✅ 6 维指纹 schema 验证
- ✅ 10 套博主模板索引
- ✅ 音频格式校验（wav/mp3/m4a）
- ✅ 同意书强制检查
- ✅ 模板匹配算法（余弦相似度）
- ✅ LoRA 训练包结构
- ✅ Whisper 转写 mock
- ✅ 黑名单拦截（敏感人物）

### 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| **V1.0** | **2026-06-26** | **首版：6 维指纹 + 10 模板 + LoRA 训练包** |

### 协同矩阵

| 上下游 | 关系 |
|--------|------|
| ↑ OpenBMB/VoxCPM | LoRA 训练基础模型 |
| ↑ 35-06 博主蒸馏分析师 V1.1 | 7 维指纹蒸馏（+声音）|
| ↔ voxcpm-tts-integration V1.0 | 推理层依赖 |
| ↓ gpt-image-2-voxcpm-bridge | 图音桥接 |
| ↓ 35-05 短视频编导 V10.2 | 博主配音工业化 |

### 版本信息

- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **License**: Apache-2.0 + MIT
- **Last Updated**: 2026-06-26