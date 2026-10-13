---
license: UNKNOWN
triggers: ["davinci magihuman", "daVinci-MagiHuman SKILL"]
---
# daVinci-MagiHuman SKILL

## 概述

| 属性 | 值 |
|------|-----|
| **技能名称** | davinci-magihuman |
| **来源项目** | GAIR-NLP/daVinci-MagiHuman |
| **Stars** | 1.5k ⭐ |
| **许可证** | Apache 2.0 |
| **版本** | V1.0 |

## 核心能力

基于15B参数的40层单流Transformer架构，通过自注意力机制联合处理文本、视频和音频，无需交叉注意力或多流复杂设计。

```
┌─────────────────────────────────────────────────────────────┐
│ daVinci-MagiHuman Architecture                              │
├─────────────────────────────────────────────────────────────┤
│  Text ──┐                                                  │
│         ├──► Single-Stream Transformer (15B, 40 layers)   │
│  Video ──┤         ↓                                      │
│         │    Self-Attention (Unified)                     │
│  Audio ──┘         ↓                                      │
│              ┌─────────────┐                               │
│              │  Generated  │                               │
│              │   Video     │                               │
│              └─────────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

## 主要特性

| 特性 | 说明 |
|------|------|
| 🧠 **单流架构** | 15B参数，40层Transformer |
| 🎭 **人像视频** | 高质量人像，面部表情丰富 |
| 🌍 **多语言** | 中、英、日、韩、德、法 |
| ⚡ **极速推理** | 256p仅2秒，1080p仅38秒 |
| 🏆 **SOTA性能** | 人类评估胜率80% vs Ovi 1.1 |

## 性能基准

| 分辨率 | 基础生成 | 超分 | 解码 | 总耗时 |
|--------|----------|------|------|--------|
| 256p   | 1.6s     | —    | 0.4s | **2.0s** |
| 540p   | 1.6s     | 5.1s | 1.3s | **8.0s** |
| 1080p  | 1.6s     | 31s  | 5.8s | **38.4s** |

## 安装方式

### 方式1: Docker (推荐)

```bash
# 拉取镜像
docker pull sandai/magi-human:latest

# 运行容器
docker run --gpus all --shm-size=64g \
  -v $(pwd)/output:/app/output \
  sandai/magi-human:latest \
  python -m magihuman.generate \
  --prompt "你的视频描述"
```

### 方式2: Conda环境

```bash
# 创建环境
conda create -n magihuman python=3.12
conda activate magihuman

# 安装PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 安装Flash Attention
pip install flash-attn --no-build-isolation

# 安装MagiHuman
pip install magi-human
```

### 方式3: HuggingFace模型

```python
from huggingface_hub import snapshot_download

# 下载模型
model_path = snapshot_download(repo_id="GAIR-NLP/MagiHuman")

# 或使用hf_transfer加速
HF_HUB_ENABLE_HF_TRANSFER=1 huggingface-cli download GAIR-NLP/MagiHuman
```

## 使用方法

### 基础视频生成

```python
import torch
from magihuman import MagiHumanPipeline

# 初始化
pipeline = MagiHumanPipeline(
    model_path="GAIR-NLP/MagiHuman",
    device="cuda" if torch.cuda.is_available() else "cpu"
)

# 生成视频
video = pipeline.generate(
    prompt="一个穿着汉服的女子在樱花树下翩翩起舞",
    negative_prompt="低质量, 模糊, 变形",
    num_frames=97,
    guidance_scale=7.5,
    num_inference_steps=50
)

# 保存
pipeline.save_video(video, "output.mp4")
```

### 批量处理

```python
from magihuman import BatchProcessor

# 初始化批处理器
batch = BatchProcessor(
    prompts_file="prompts.json",
    output_dir="./output",
    batch_size=4
)

# 执行
batch.run()
```

### CLI使用

```bash
# 单个视频
python -m magihuman.generate \
  --prompt "一个穿着汉服的女子在樱花树下" \
  --negative "低质量, 模糊" \
  --num_frames 97 \
  --fps 24 \
  --output output.mp4

# 批量生成
python -m magihuman.batch \
  --config batch_config.yaml
```

## 提示词技巧

### 人像视频

```markdown
# 优质人像提示词
[主体] + [动作] + [服装] + [场景] + [氛围] + [光照]

示例:
"一位年轻的东方女性，穿着淡蓝色汉服，
在古典园林中优雅地行走，长发随风飘动，
柔和的午后阳光，画面唯美，高清画质"
```

### 场景视频

```markdown
# 优质场景提示词
[场景类型] + [细节描述] + [动态元素] + [氛围] + [画质]

示例:
"一片广阔的薰衣草花海，远处有风车，
蜜蜂飞舞，光影变幻，夕阳余晖，
电影级画质，8K超清"
```

### 多语言支持

```python
# 中文提示词
prompt_cn = "一个穿着白色连衣裙的女孩在海边奔跑"

# 英文翻译（推荐用于更好效果）
prompt_en = "A young girl in a white dress running on the beach, sunny day, ocean waves"

# 日文
prompt_jp = "白いドレスを着た女の子が大海原を走っている"
```

## 天龙引擎集成

### 岗位升级

| 岗位 | 升级内容 |
|------|---------|
| **35-05 短视频编导** | 新增MagiHuman人像视频生成能力 |
| **13-01 设计师** | 新增动态海报+视频化设计 |
| **35-02 社媒运营** | 新增短视频自动化内容 |
| **07 记录师** | 新增视频化知识传播 |

### 与现有技能协同

| 现有技能 | MagiHuman协同 | 效果 |
|---------|--------------|------|
| **remotion-best-practices** | 代码驱动 → 人像增强 | 质的飞跃 |
| **seedance2-skill** | AI生成 → 人像视频 | 互补 |
| **ppt-generator** | 幻灯片 → 视频化 | +200% |
| **manga-style-video** | 静态风格 → 动态视频 | +300% |

### 工作流示例

```bash
# 短视频编导工作流
[@35-05] 使用MagiHuman生成产品展示人像视频
[@35-05] 结合Remotion添加动态数据可视化
[@35-05] 使用FFmpeg添加背景音乐

# 社媒运营工作流
[@35-02] 使用MagiHuman生成多语言社媒短视频
[@35-02] 结合剪映添加字幕和特效
[@35-02] 发布到抖音/快手/小红书
```

## 硬件要求

| 分辨率 | GPU显存 | 推荐配置 |
|--------|--------|---------|
| 256p   | 16GB   | RTX 3090 / A5000 |
| 540p   | 24GB   | RTX 4090 / A6000 |
| 1080p  | 40GB   | A100 40GB / H100 |

## 注意事项

1. **内存要求**: 推荐64GB系统内存
2. **CUDA版本**: 需要CUDA 12.1+
3. **Flash Attention**: 推荐安装以提升性能
4. **模型下载**: 首次运行需要下载~30GB模型

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| OOM错误 | 降低num_frames或使用较低分辨率 |
| 显存不足 | 使用 distillation 模型代替 base 模型 |
| 生成质量差 | 调整guidance_scale (5-10) 或增加steps |
| 面部变形 | 添加negative_prompt: "deformed face" |

## 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| V1.0 | 2026-04-02 | 初始版本，支持基础视频生成 |

---

**天龙引擎版本**: V8.75
**集成日期**: 2026-04-02
