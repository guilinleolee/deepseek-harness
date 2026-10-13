---
license: UNKNOWN
triggers: ["supertonic tts", "Supertonic TTS - 多语言语音合成"]
---
# Supertonic TTS - 多语言语音合成

## L0: 一句话描述 (≤15字)
边缘级多语言TTS语音合成

## L1: 使用场景 (50-100字)
适用场景：短视频配音、文档语音播报、语音交互、语音克隆、工作流自动化。支持31种语言、10种情感表达式标签、44.1kHz高保真输出，可在Raspberry Pi等边缘设备运行。

## L2: 详细文档

### 来源项目
> [supertone-inc/supertonic](https://github.com/supertone-inc/supertonic) - Lightning-fast on-device multilingual TTS

### 核心能力矩阵

| 维度 | 数据 |
|------|------|
| **参数量** | ~99M（比0.7B-2B竞品小10-20倍） |
| **语言支持** | 31种语言 |
| **输出采样率** | 44.1kHz |
| **情感标签** | 10种（laugh/breath/sigh/gasp/yawn/cough/sniff/hmm/punch/throat） |
| **边缘设备** | Raspberry Pi、e-readers、WebGPU浏览器 |
| **推理引擎** | ONNX Runtime |
| **License** | MIT（代码）+ OpenRAIL-M（模型） |

### 支持的语言

```
英语(en) | 中文(zh) | 日语(ja) | 韩语(ko) | 法语(fr) | 德语(de) | 西班牙语(es)
意大利语(it) | 葡萄牙语(pt) | 俄语(ru) | 阿拉伯语(ar) | 印地语(hi) | 印尼语(id)
泰语(th) | 越南语(vi) | 马来语(ms) | 土耳其语(tr) | 波兰语(pl) | 荷兰语(nl)
瑞典语(sv) | 挪威语(no) | 丹麦语(da) | 芬兰语(fi) | 捷克语(cs) | 匈牙利语(hu)
罗马尼亚语(ro) | 保加利亚语(bg) | 希腊语(el) | 克罗地亚语(hr) | 斯洛伐克语(sk) | 乌克兰语(uk)
```

### 表达式标签

| 标签 | 效果 |
|------|------|
| `<laugh>` | 笑声 |
| `<breath>` | 呼吸声 |
| `<sigh>` | 叹息 |
| `<gasp>` | 喘息 |
| `<yawn>` | 打哈欠 |
| `<cough>` | 咳嗽 |
| `<sniff>` | 吸鼻子 |
| `<hmm>` | 嗯哼 |
| `<punch>` | 捶打节奏 |
| `<throat>` | 清嗓子 |

### 安装

```bash
pip install supertonic

# 或从源码安装
git clone https://github.com/supertone-inc/supertonic.git
cd supertonic
pip install -e .
```

### Python SDK调用

```python
from supertonic import TTS

# 初始化（自动下载模型）
tts = TTS(auto_download=True)

# 获取语音风格
style = tts.get_voice_style(voice_name="M1")

# 基础合成
wav, duration = tts.synthesize(
    text="欢迎使用天龙引擎语音合成功能",
    lang="zh",
    voice_style=style,
    total_steps=8,
    speed=1.05
)

# 带情感标签
wav, duration = tts.synthesize(
    text="你好<laugh>欢迎使用我们的系统<sigh>",
    lang="zh",
    voice_style=style
)

# 保存音频
tts.save_audio(wav, "output.wav")

# 批量合成
texts = ["第一段文本", "第二段文本", "第三段文本"]
for i, text in enumerate(texts):
    wav, duration = tts.synthesize(text=text, lang="zh", voice_style=style)
    tts.save_audio(wav, f"output_{i}.wav")
```

### 命令行使用

```bash
# 合成语音
supertonic synthesize --text "Hello world" --lang en --output hello.wav

# 启动HTTP服务
supertonic serve --host 127.0.0.1 --port 7788

# 查看可用语音
supertonic list-voices

# 指定语音
supertonic synthesize --text "Hello" --voice M2 --output hello.wav
```

### 天龙引擎协同岗位

| 岗位 | 协同方式 |
|------|---------|
| **35-05 短视频编导** | 文案→TTS配音→多语言翻译→视频合成 |
| **07 记录师** | 文档生成→TTS语音播报→无障碍访问 |
| **47-03 IM运营师** | 消息接收→语音读出→移动端播放 |
| **17-04 桌面自动化** | 语音命令→自然语言解析→操作执行 |

### 天龙命令速查

```bash
# 文档语音化
[@07] 将这份报告转换为语音播报

# 短视频配音
[@35-05] 为这段文案生成TTS配音，使用欢快风格

# 语音命令
[@17-04] 监听语音命令，执行截图操作

# 多语言播报
[@07] 将这段中文内容翻译为英文并生成TTS
```

### 与现有技能协同

| 现有技能 | 协同方式 |
|---------|---------|
| **pixelle-video** | 视频生成→TTS配音→BGM合成 |
| **xiaohu-wechat-format** | 文章排版→TTS语音版 |
| **ppt-generator** | PPT生成→语音讲解 |
| **remotion-best-practices** | 视频生成→TTS配音 |

### 预期收益

| 指标 | 数值 |
|------|------|
| **配音效率** | +500% |
| **多语言支持** | 31种语言 |
| **边缘部署** | Raspberry Pi可用 |
| **情感表达** | 10种标签 |

### 文件结构

```
supertonic-tts/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── tts_client.py         # Python SDK封装
│   ├── batch_synthesize.py    # 批量合成脚本
│   └── voice_styles.json      # 语音风格配置
└── prompts/
    ├── tts-prompt.md         # TTS提示词模板
    └── multilingual-tts.md    # 多语言TTS指南
```

### 技术约束

- 需要ONNX Runtime支持
- 模型下载需要网络连接（或预下载）
- 边缘设备性能影响合成速度

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-19 | 初始集成，基于Supertonic TTS |
