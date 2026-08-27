---
license: UNKNOWN
triggers: ["supertonic edge deploy", "Supertonic Edge Deploy - 边缘设备部署指南"]
---
# Supertonic Edge Deploy - 边缘设备部署指南

## L0: 一句话描述 (≤15字)
边缘设备TTS部署方案

## L1: 使用场景 (50-100字)
适用场景：离线语音助手、嵌入式设备、物联网语音交互、无网络环境。通过ONNX Runtime实现跨平台部署，支持Raspberry Pi等边缘设备，无需网络连接即可完成语音合成。

## L2: 详细文档

### 来源项目
> [supertone-inc/supertonic](https://github.com/supertone-inc/supertonic) - Lightning-fast on-device multilingual TTS

### 支持的边缘设备

| 设备 | CPU | 内存 | 性能 |
|------|-----|------|------|
| **Raspberry Pi 4/5** | ARM64 | 4-8GB | 实时合成 |
| **Raspberry Pi Zero 2** | ARM64 | 512MB | 低延迟 |
| **Android设备** | ARM64/ARMv7 | 2GB+ | 依赖硬件 |
| **iOS设备** | ARM64 | 2GB+ | 原生SDK |
| **Web浏览器** | - | - | WebGPU |
| **e-Readers** | ARM | 512MB | 受限运行 |

### ONNX Runtime部署

```python
# 边缘设备Python部署
from supertonic import TTS

# 初始化（本地模型）
tts = TTS(
    auto_download=True,
    model_path="./models/supertonic.onnx",
    runtime="onnx"
)

# 合成语音
style = tts.get_voice_style(voice_name="M1")
wav, duration = tts.synthesize(
    text="边缘设备语音合成",
    lang="zh",
    voice_style=style,
    total_steps=4  # 边缘设备减少步数
)

tts.save_audio(wav, "edge_output.wav")
```

### Raspberry Pi部署步骤

```bash
# 1. 安装ONNX Runtime
pip install onnxruntime==1.18.0

# 2. 下载模型
wget https://github.com/supertone-inc/supertonic/releases/download/v1.0/supertonic-onnx.tar.gz
tar -xzf supertonic-onnx.tar.gz

# 3. 测试合成
python3 test_tts.py

# 4. 后台服务
nohup python3 tts_server.py &
```

### WebGPU浏览器部署

```javascript
// Web端集成
import { createTTSEngine } from '@supertonic/webgpu';

const engine = await createTTSEngine({
    runtime: 'webgpu',
    modelUrl: './models/supertonic.wasm'
});

// 合成
const audio = await engine.synthesize({
    text: "浏览器语音合成",
    lang: "zh",
    voice: "M1"
});

// 播放
const context = new AudioContext();
const source = context.createBufferSource();
source.buffer = audio;
source.connect(context.destination);
source.start();
```

### iOS Swift SDK

```swift
import Supertonic

// 初始化
let config = TTSConfig(
    modelPath: "bundled_model.onnx",
    runtime: .coreML  // 或 .onnxruntime
)
let tts = Supertonic(config: config)

// 合成
tts.synthesize(
    text: "iOS原生语音合成",
    lang: "zh",
    voice: "M1"
) { result in
    switch result {
    case .success(let audioData):
        playAudio(audioData)
    case .failure(let error):
        print("Error: \(error)")
    }
}
```

### 性能优化配置

| 设备类型 | total_steps | 量化 | 内存优化 |
|---------|--------------|------|---------|
| 高端设备 | 8 | FP16 | 无 |
| 中端设备 | 6 | INT8 | 部分 |
| 低端设备 | 4 | INT8 | 完整 |

### 天龙引擎协同岗位

| 岗位 | 协同方式 |
|------|---------|
| **17-04 桌面自动化** | 离线语音命令 |
| **18-01 移动开发** | iOS/Android应用 |
| **16-01 DevOps** | 边缘设备CI/CD |
| **09-02 编排协调师** | 分布式TTS编排 |

### 天龙命令速查

```bash
# 边缘部署
[@16-01] 在Raspberry Pi部署Supertonic TTS

# 移动开发
[@18-01] 集成iOS Supertonic SDK

# 离线语音
[@17-04] 配置离线语音命令系统
```

### 与现有技能协同

| 现有技能 | 协同方式 |
|---------|---------|
| **turix-desktop-agent** | 离线语音命令 |
| **turi-x-cua** | 边缘GUI操作 |
| **nemo-claw-sandbox** | 安全隔离部署 |

### 预期收益

| 指标 | 数值 |
|------|------|
| **离线可用性** | 100% |
| **延迟** | <500ms |
| **功耗** | <2W |
| **内存占用** | <200MB |

### 文件结构

```
supertonic-edge-deploy/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── pi_deploy.py           # Raspberry Pi部署脚本
│   ├── android_deploy.py      # Android部署
│   └── webgpu_deploy.py       # Web端部署
├── configs/
│   ├── pi4_config.json        # Pi 4配置
│   └── mobile_config.json     # 移动设备配置
└── prompts/
    └── edge-optimization.md   # 边缘优化提示词
```

### 技术约束

- 边缘设备性能差异大
- 模型量化影响质量
- 存储空间有限

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-19 | 初始集成，基于Supertonic边缘部署 |