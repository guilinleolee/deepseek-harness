---
license: UNKNOWN
triggers: ["pixelle video", "Pixelle-Video集成技能"]
---
# Pixelle-Video集成技能

## L0: 一句话描述
Pixelle-Video是AI全自动短视频引擎，输入主题自动生成完整视频（文案+配图+配音+BGM+数字人口播）

## L1: 核心能力
- 全自动文案生成 → 配图 → 视频 → 配音 → BGM一键合成
- 数字人口播：上传图片+语音自动生成口播视频
- 动作迁移：参考视频动作驱动目标图片
- 多模型支持：GPT/Qwen/DeepSeek/Ollama + WAN 2.1/FLUX + ChatTTS

## L2: 详细文档

### 技术架构
- 核心：ComfyUI可视化工作流
- Pipeline: 文案生成 → 配图规划 → 逐帧处理 → 视频合成
- 输出格式：MP4 (H.264/H.265/AV1)

### 天龙引擎定位
35-05短视频编导V6.0五引擎之一，用于全自动短视频生成场景。

### 引擎选择决策
| 场景 | 推荐引擎 | 原因 |
|------|---------|------|
| 快速自动化 | Pixelle-Video | 端到端一键 |
| 数字人口播 | Pixelle-Video | 唯一支持 |
| 动作迁移 | Pixelle-Video | 唯一支持 |
| 精确控制教程 | Remotion | 代码级控制 |
| 数据可视化 | Remotion | React+图表 |
| 人像极速生成 | MagiHuman | 2秒256p |
| 品牌模板批量 | Hyperframes | HTML+GSAP |
| AI创意短片 | Seedance 2.0 | 风格化 |

### 核心命令
```bash
# 端到端视频生成
[@35-05] 使用Pixelle生成"AI Agent发展趋势"主题视频

# 数字人口播
[@35-05] 使用Pixelle数字人口播上传产品图片+ChatTTS配音

# 动作迁移
[@35-05] 使用Pixelle动作迁移：参考视频+产品图片

# TTS配音
[@35-05] 使用Pixelle-TTS为视频配音（ChatTTS中文音色）
```

### 部署方式
```bash
# Docker部署（推荐）
docker run -d --gpus all -p 8188:8188 \
  -v ./models:/app/models \
  pixelle-video:latest

# ComfyUI API调用
curl -X POST http://localhost:8188/prompt \
  -d '{"prompt": {"nodes": [...], "workflow": "digital-human"}}'
```

### 与其他引擎协同
- Pixelle生成素材 → Remotion添加数据可视化
- Pixelle数字人口播 → Hyperframes添加品牌模板
- Seedance生成背景 → Pixelle添加配音

## 技术约束
- 需要GPU（视频/图像生成必需）
- ComfyUI版本锁定（推荐v1.2.x）
- FFmpeg用于视频后处理