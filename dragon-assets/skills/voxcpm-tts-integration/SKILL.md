---
name: voxcpm-tts-integration
description: VoxCPM2 多语种 TTS 集成封装（30 语言 + 9 中文方言 + 音色设计 + 可控克隆 + 6 部署栈）. Use when user asks "VoxCPM", "VoxCPM2", "TTS 集成", "文本转语音", "语音克隆", "音色设计", "多语言配音", "方言合成", "OpenBMB 语音", "nano-vllm-voxcpm", "vllm-omni", "voxcpm 微调".
version: 1.0.0
author: 天龙引擎集成
source: https://github.com/OpenBMB/VoxCPM (31.7k ⭐)
license: Apache-2.0 (VoxCPM) + MIT (skill wrapper)
last_updated: 2026-06-26
triggers: ["voxcpm tts integration", "voxcpm-tts-integration · V1.0 天龙引擎集成版"]
---

# voxcpm-tts-integration · V1.0 天龙引擎集成版

## L0: 一句话描述 (≤15字)

**VoxCPM2 多语种 TTS 集成封装**

## L1: 使用场景 (50-100字)

当用户需要把文本转为多语言/方言语音，或需要做音色设计、可控声音克隆、或需要生产级 TTS 部署时，使用本 skill。支持 6 种部署栈（PyTorch / Nano-vLLM / vLLM-Omni / ComfyUI / Web Demo / 微调 LoRA），含 30 种全球语言 + 9 种中文方言矩阵、5 维音色设计模板、克隆伦理护栏。

## L2: 详细文档

### V1.0 核心能力

| 维度 | 能力 |
|------|------|
| 语言覆盖 | 30 种全球语言 + 9 种中文方言（四川/粤语/吴/东北/河南/陕西/山东/天津/闽南）|
| 音色设计 | 5 维（性别/年龄/音色/情绪/语速）自然语言描述生成全新音色 |
| 可控克隆 | 参考音频 + 风格指令（情绪/语速/表现力），保留原始音色 |
| 极致克隆 | 音频续写 + prompt_text，高保真还原（与 VoxCPM1.5 一致）|
| 音频质量 | 48kHz 原生输出（16kHz 参考音频经 AudioVAE V2 超分）|
| 实时流式 | RTX 4090 RTF ~0.3 / Nano-vLLM 加速 ~0.13 |
| 微调能力 | SFT + LoRA，5-10 分钟音频即可适配 |
| 商用许可 | Apache-2.0，免费商用 |

### 6 种部署栈对比

| # | 部署栈 | 端点/调用 | 性能 | 适用场景 |
|---|--------|----------|------|---------|
| 1 | **PyTorch 原生** | `pip install voxcpm` + Python API | RTF ~0.3 | 本地开发/原型 |
| 2 | **Nano-vLLM** ⭐ | `pip install nano-vllm-voxcpm` | RTF ~0.13 | 高吞吐 GPU 服务 |
| 3 | **vLLM-Omni** ⭐ | `vllm serve openbmb/VoxCPM2 --omni` | OpenAI 兼容 API | 生产级多租户 |
| 4 | **ComfyUI 节点** | `ComfyUI-VoxCPM` / `ComfyUI_RH_VoxCPM` | 工作流集成 | 视觉创作联动 |
| 5 | **Web Demo** | `python app.py --port 8808` | 交互式 | 试听/手动调优 |
| 6 | **LoRA 微调** | `python lora_ft_webui.py` | 自定义音色 | 博主/角色定制 |

### 4 大调用模式

#### 1️⃣ 纯文本转语音（TTS）
```python
from voxcpm import VoxCPM
import soundfile as sf

model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
wav = model.generate(
    text="VoxCPM2 是目前推荐使用的多语言语音合成版本。",
    cfg_value=2.0,
    inference_timesteps=10,
)
sf.write("demo.wav", wav, model.tts_model.sample_rate)
```

#### 2️⃣ 音色设计（Voice Design）
无需参考音频，用自然语言凭空创建音色。格式：在 `text` 开头加 `(音色描述)`：

```python
wav = model.generate(
    text="(年轻女性,声音温柔甜美)你好,欢迎使用VoxCPM2!",
    cfg_value=2.0,
    inference_timesteps=10,
)
```

#### 3️⃣ 可控声音克隆（Controllable Clone）
上传参考音频，克隆音色 + 风格指令调节：

```python
wav = model.generate(
    text="(稍快一点,欢快的语气)这是带风格控制的克隆语音。",
    reference_wav_path="path/to/voice.wav",
    cfg_value=2.0,
    inference_timesteps=10,
)
```

#### 4️⃣ 极致克隆（Hifi Clone）
音频续写模式，提供参考音频 + 精确转写：

```python
wav = model.generate(
    text="这是使用VoxCPM2的极致克隆演示。",
    prompt_wav_path="path/to/voice.wav",
    prompt_text="参考音频的文本转录。",
    reference_wav_path="path/to/voice.wav",  # 可选，提升相似度
)
```

### CLI 模式

```bash
# 音色设计（无需参考音频）
voxcpm design --text "VoxCPM2带来全新语音合成体验。" --output out.wav

# 可控声音克隆（带风格控制）
voxcpm design \
  --text "VoxCPM2带来全新语音合成体验。" \
  --control "年轻女声,温暖温柔,略带微笑" \
  --output out.wav

# 声音克隆（参考音频）
voxcpm clone \
  --text "这是一个声音克隆的演示。" \
  --reference-audio path/to/voice.wav \
  --output out.wav

# 极致克隆（提示音频 + 转录文本）
voxcpm clone \
  --text "这是一个声音克隆的演示。" \
  --prompt-audio path/to/voice.wav \
  --prompt-text "参考音频转录文本" \
  --reference-audio path/to/voice.wav \
  --output out.wav

# 批量处理
voxcpm batch --input examples/input.txt --output-dir outs

# 帮助
voxcpm --help
```

### 生产部署（vLLM-Omni · OpenAI 兼容 API）

```bash
# 启动 OpenAI 兼容的 TTS 服务
vllm serve openbmb/VoxCPM2 --omni --port 8000

# 任意 OpenAI 客户端均可调用
curl http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"openbmb/VoxCPM2","input":"你好,欢迎使用 VoxCPM2 on vLLM-Omni!","voice":"default"}' \
  --output out.wav
```

**优势**：PagedAttention KV 缓存 + 连续批处理 + OpenAI 完全兼容 `/v1/audio/speech` 接口

### 30 语种 × 9 方言矩阵

#### 全球 30 语言
阿拉伯语、缅甸语、中文、丹麦语、荷兰语、英语、芬兰语、法语、德语、希腊语、希伯来语、印地语、印尼语、意大利语、日语、高棉语、韩语、老老挝语、马来语、挪威语、波兰语、葡萄牙语、俄语、西班牙语、斯瓦希里语、瑞典语、菲律宾语、泰语、土耳其语、越南语

#### 9 种中文方言
四川话、粤语、吴语、东北话、河南话、陕西话、山东话、天津话、闽南话

**总覆盖**：39 语种/方言，可直接输入文本，无需语言标签

### 微调工作流

```bash
# LoRA 微调（参数高效，推荐）
python scripts/train_voxcpm_finetune.py \
  --config_path conf/voxcpm_v2/voxcpm_finetune_lora.yaml

# 全参数微调
python scripts/train_voxcpm_finetune.py \
  --config_path conf/voxcpm_v2/voxcpm_finetune_all.yaml

# WebUI 训练与推理
python lora_ft_webui.py
# 然后打开 http://localhost:7860
```

**最低数据要求**：5-10 分钟干净音频

### 伦理护栏 ⚠️

VoxCPM 官方明确警告：
- 🚫 **严禁冒充他人**：声音克隆能力可生成高度逼真合成语音
- 🚫 **严禁欺诈/虚假信息传播**
- ✅ **必须标注**：所有 AI 生成内容需明确标注
- ⚠️ **可控生成不稳定**：建议生成 1-3 次取最优

集成层已添加 `voice-clone-ethics` 检查（见 `scripts/voxcpm.py`），自动拦截：
- 无 `consent.txt` 文件的克隆请求
- 未标注 AI 生成标识的输出
- 已知敏感人物名单（默认空，需用户配置）

### 数据结构

```python
# 输入（统一 schema）
{
    "text": "要合成的文本",
    "mode": "tts" | "voice_design" | "controllable_clone" | "hifi_clone",
    "language": "auto" | "zh" | "en" | "ja" | ...,  # auto=自动检测
    "dialect": "auto" | "sichuan" | "yue" | ...,  # 中文方言
    "voice_description": "(年轻女性,温柔甜美)",  # voice_design 模式
    "reference_wav_path": "path/to/voice.wav",  # clone 模式
    "prompt_wav_path": "path/to/prompt.wav",  # hifi_clone 模式
    "prompt_text": "参考音频转写",  # hifi_clone 模式
    "cfg_value": 2.0,
    "inference_timesteps": 10,
    "output_path": "out.wav",
}

# 输出
{
    "wav_path": "out.wav",
    "sample_rate": 48000,
    "duration_seconds": 5.2,
    "language_detected": "zh",
    "dialect_detected": None,
    "mode": "tts",
    "watermark": "ai_generated_voxcpm2",  # 自动水印
}
```

### 安装与依赖

```bash
# Python 包
pip install voxcpm

# 模型权重（HF）
pip install huggingface_hub
huggingface-cli download openbmb/VoxCPM2

# 模型权重（ModelScope · 国内）
pip install modelscope
python -c "from modelscope import snapshot_download; snapshot_download('OpenBMB/VoxCPM2', local_dir='./pretrained_models/VoxCPM2')"

# Nano-vLLM（高吞吐）
pip install nano-vllm-voxcpm

# vLLM-Omni（生产级）
uv pip install vllm==0.19.0 --torch-backend=auto
git clone https://github.com/vllm-project/vllm-omni.git
cd vllm-omni && uv pip install -e .
```

**环境要求**：Python ≥ 3.10 (<3.13), PyTorch ≥ 2.5.0, CUDA ≥ 12.0

### 性能基准（RTX 4090）

| 部署栈 | RTF | 显存 | 并发 |
|--------|-----|------|------|
| PyTorch 原生 | ~0.30 | ~8 GB | 1 |
| Nano-vLLM | ~0.13 | ~10 GB | 高 |
| vLLM-Omni | ~0.15 | ~12 GB | 极高 |

### CLI 选项（`scripts/voxcpm.py`）

```bash
python scripts/voxcpm.py [options]

输入:
  --text TEXT              要合成的文本（必需）
  --mode MODE              tts|voice_design|controllable_clone|hifi_clone
  --voice-desc TEXT        音色描述（voice_design 模式）
  --reference-audio PATH   参考音频（clone 模式）
  --prompt-audio PATH      提示音频（hifi_clone 模式）
  --prompt-text TEXT       提示音频转写（hifi_clone 模式）
  --language LANG          auto|zh|en|ja|...（默认 auto）
  --dialect DIALECT        auto|sichuan|yue|wu|...

输出:
  --output PATH            输出 wav 路径（默认 ./output.wav）
  --sample-rate INT        采样率（默认 48000）
  --watermark              添加 AI 生成水印（默认开启）

模型:
  --model MODEL            模型名称/路径（默认 openbmb/VoxCPM2）
  --device DEVICE          auto|cpu|mps|cuda|cuda:N（默认 auto）
  --cfg-value FLOAT        CFG 值（默认 2.0）
  --inference-steps INT    推理步数（默认 10）

部署:
  --backend BACKEND        pytorch|nano_vllm|vllm_omni（默认 pytorch）
  --server-url URL         vLLM-Omni 服务地址

伦理:
  --consent-file PATH      同意书文件（clone 模式必需）
  --skip-watermark         跳过水印（不推荐）

其他:
  --dry-run                只生成配置不实际推理
  --verbose                详细输出
```

### 测试覆盖

`tests/test_voxcpm.py` 包含 12 个测试用例：
- ✅ 模式路由（tts / voice_design / controllable_clone / hifi_clone）
- ✅ 30 语种 × 9 方言矩阵索引
- ✅ 6 部署栈端点配置
- ✅ 伦理护栏（consent / watermark / 敏感词拦截）
- ✅ 输入/输出 schema 验证
- ✅ 错误处理（缺音频/缺文本/不支持模式）
- ✅ CLI 参数解析
- ✅ Dry-run 模式
- ✅ 跨语言 prompt (zh/en)
- ✅ 集成示例（与 GPT-Image-2 / Seedance 联动）
- ✅ Watermark 自动注入
- ✅ 性能 benchmark（mock）

### 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| **V1.0** | **2026-06-26** | **首版：6 部署栈 / 4 调用模式 / 39 语种方言 / 伦理护栏** |

### 协同矩阵

| 上下游 | 关系 |
|--------|------|
| ↑ OpenBMB/VoxCPM | 源仓库（31.7k ⭐）|
| ↔ gpt-image-2-api-integration | 图文音三位一体（图+音+文案）|
| ↔ voxcpm-voice-distillery | 博主声音指纹提取 |
| ↔ gpt-image-2-voxcpm-bridge | 桥接下游 skill |
| ↓ qiaomu-mondo-poster-design | 海报 + 音频 demo |
| ↓ baoyu-cover-image | 公众号封面 + 音频 |
| ↓ seedance2-skill | 短视频剧本 + 配音 |

### 版本信息

- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **License**: Apache-2.0 (VoxCPM) + MIT (skill wrapper)
- **Last Updated**: 2026-06-26