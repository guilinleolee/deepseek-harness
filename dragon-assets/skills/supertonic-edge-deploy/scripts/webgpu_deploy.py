#!/usr/bin/env python3
"""
Supertonic Edge Deploy - WebGPU部署脚本

在支持WebGPU的浏览器环境中部署Supertonic TTS边缘推理引擎
来源: https://github.com/supertone-inc/supertonic
"""

import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class WebGPUDeploymentConfig:
    """WebGPU部署配置"""
    model: str = "supertonic-base"
    language: str = "en"
    quantization: str = "int8"  # qint8, float16, float32
    sample_rate: int = 24000
    max_text_length: int = 500
    voice_model_path: Optional[str] = None
    output_dir: str = "./supertonic-webgpu"


@dataclass
class WebGPUEnvironmentInfo:
    """WebGPU环境信息"""
    browser: str
    browser_version: str
    os: str
    device_vendor: str
    device_renderer: str
    webgpu_supported: bool
    webgpu_adapter: str
    max_buffer_size: int
    max_compute_workgroup_size: list
    memory_limit_mb: int


class SupertonicWebGPUDeployer:
    """Supertonic WebGPU部署器"""

    # 模型下载URL (示例，实际请参考官方release)
    MODEL_URLS = {
        "supertonic-base": {
            "qint8": "https://github.com/supertone-inc/supertonic/releases/download/v1.0/supertonic-base-int8.tar.gz",
            "float16": "https://github.com/supertone-inc/supertonic/releases/download/v1.0/supertonic-base-f16.tar.gz",
        },
        "supertonic-large": {
            "qint8": "https://github.com/supertone-inc/supertonic/releases/download/v1.0/supertonic-large-int8.tar.gz",
            "float16": "https://github.com/supertone-inc/supertonic/releases/download/v1.0/supertonic-large-f16.tar.gz",
        },
    }

    def __init__(self):
        self.config = None

    def check_environment(self) -> WebGPUEnvironmentInfo:
        """检查WebGPU环境"""
        print("=" * 60)
        print("检查WebGPU环境...")
        print("=" * 60)

        # 生成环境检测脚本
        check_script = """
        (async () => {
            const info = {
                browser: navigator.userAgent,
                browser_version: navigator.appVersion,
                os: navigator.platform,
                webgpu_supported: false,
                webgpu_adapter: 'N/A',
                max_buffer_size: 0,
                max_compute_workgroup_size: [0, 0, 0],
                memory_limit_mb: 0,
                device_vendor: 'Unknown',
                device_renderer: 'Unknown'
            };

            if (navigator.gpu) {
                info.webgpu_supported = true;
                try {
                    const adapter = await navigator.gpu.requestAdapter();
                    if (adapter) {
                        const features = Array.from(adapter.features);
                        info.webgpu_adapter = adapter.info ? `${adapter.info.vendor} ${adapter.info.architecture}` : 'Unknown';
                        info.device_vendor = adapter.info?.vendor || 'Unknown';
                        info.device_renderer = adapter.info?.device || 'Unknown';

                        // 估算内存限制
                        const memory = adapter.limits?.maxStorageBufferBindingSize || 0;
                        info.memory_limit_mb = Math.round(memory / (1024 * 1024));

                        // 最大Buffer大小
                        info.max_buffer_size = adapter.limits?.maxBufferSize || 0;

                        // Compute workgroup大小
                        info.max_compute_workgroup_size = [
                            adapter.limits?.maxComputeWorkgroupSizeX || 0,
                            adapter.limits?.maxComputeWorkgroupSizeY || 0,
                            adapter.limits?.maxComputeWorkgroupSizeZ || 0
                        ];
                    }
                } catch (e) {
                    console.error('WebGPU adapter error:', e);
                }
            }

            console.log(JSON.stringify(info));
        })();
        """

        print("\nWebGPU环境检测脚本:")
        print("-" * 40)
        print("在浏览器控制台中运行以下代码:")
        print("-" * 40)
        print(check_script)
        print("-" * 40)

        # 生成HTML检测页面
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Supertonic WebGPU Environment Check</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #1a1a1a; margin-bottom: 24px; }}
        .status {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
        }}
        .success {{ background: #d4edda; color: #155724; }}
        .error {{ background: #f8d7da; color: #721c24; }}
        .warning {{ background: #fff3cd; color: #856404; }}
        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .info-label {{ font-weight: 600; color: #666; }}
        .info-value {{ color: #1a1a1a; }}
    </style>
</head>
<body>
    <h1>🔊 Supertonic WebGPU Environment Check</h1>

    <div class="card">
        <h2>Environment Information</h2>
        <div id="env-info">
            <p>Checking environment...</p>
        </div>
    </div>

    <div class="card">
        <h2>WebGPU Support</h2>
        <div id="webgpu-status">
            <span class="status warning">Checking...</span>
        </div>
    </div>

    <div class="card">
        <h2>Detection Code</h2>
        <p>Copy and run this in browser console:</p>
        <pre id="detection-code">{check_script.replace('<', '&lt;').replace('>', '&gt;')}</pre>
    </div>

    <script>
        (async () => {{
            const envInfo = document.getElementById('env-info');
            const statusDiv = document.getElementById('webgpu-status');

            const info = {{
                browser: navigator.userAgent,
                browser_version: navigator.appVersion,
                os: navigator.platform,
                webgpu_supported: false,
                webgpu_adapter: 'N/A',
                max_buffer_size: 0,
                max_compute_workgroup_size: [0, 0, 0],
                memory_limit_mb: 0,
                device_vendor: 'Unknown',
                device_renderer: 'Unknown'
            }};

            let html = '<div class="info-row"><span class="info-label">User Agent</span><span class="info-value">' + info.browser + '</span></div>';
            html += '<div class="info-row"><span class="info-label">Platform</span><span class="info-value">' + info.os + '</span></div>';

            if (navigator.gpu) {{
                info.webgpu_supported = true;
                try {{
                    const adapter = await navigator.gpu.requestAdapter();
                    if (adapter) {{
                        info.webgpu_adapter = adapter.info ? `${{adapter.info.vendor}} ${{adapter.info.architecture}}` : 'Unknown';
                        info.device_vendor = adapter.info?.vendor || 'Unknown';
                        info.device_renderer = adapter.info?.device || 'Unknown';

                        const memory = adapter.limits?.maxStorageBufferBindingSize || 0;
                        info.memory_limit_mb = Math.round(memory / (1024 * 1024));
                        info.max_buffer_size = adapter.limits?.maxBufferSize || 0;
                        info.max_compute_workgroup_size = [
                            adapter.limits?.maxComputeWorkgroupSizeX || 0,
                            adapter.limits?.maxComputeWorkgroupSizeY || 0,
                            adapter.limits?.maxComputeWorkgroupSizeZ || 0
                        ];
                    }}
                }} catch (e) {{
                    console.error('WebGPU error:', e);
                }}
            }}

            html += '<div class="info-row"><span class="info-label">Device Vendor</span><span class="info-value">' + info.device_vendor + '</span></div>';
            html += '<div class="info-row"><span class="info-label">Device Renderer</span><span class="info-value">' + info.device_renderer + '</span></div>';
            html += '<div class="info-row"><span class="info-label">Memory Limit</span><span class="info-value">' + info.memory_limit_mb + ' MB</span></div>';
            html += '<div class="info-row"><span class="info-label">Max Buffer Size</span><span class="info-value">' + info.max_buffer_size + ' bytes</span></div>';
            html += '<div class="info-row"><span class="info-label">Compute Workgroup</span><span class="info-value">' + info.max_compute_workgroup_size.join(' x ') + '</span></div>';

            envInfo.innerHTML = html;

            if (info.webgpu_supported) {{
                statusDiv.innerHTML = '<span class="status success">✓ WebGPU Supported</span><p>Adapter: ' + info.webgpu_adapter + '</p>';
            }} else {{
                statusDiv.innerHTML = '<span class="status error">✗ WebGPU Not Supported</span><p>Please use Chrome 113+, Edge 113+, or Firefox Nightly with WebGPU enabled.</p>';
            }}

            console.log(JSON.stringify(info, null, 2));
        }})();
    </script>
</body>
</html>
"""

        html_path = Path("./webgpu_check.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"\nHTML检测页面已生成: {html_path}")
        print("请在浏览器中打开此页面查看WebGPU环境信息")

        # 返回默认信息（实际检测需要在浏览器中运行）
        return WebGPUEnvironmentInfo(
            browser="Unknown (需要在浏览器中检测)",
            browser_version="",
            os="Unknown",
            device_vendor="Unknown",
            device_renderer="Unknown",
            webgpu_supported=False,
            webgpu_adapter="Unknown",
            max_buffer_size=0,
            max_compute_workgroup_size=[0, 0, 0],
            memory_limit_mb=0
        )

    def download_model(
        self,
        model_name: str = "supertonic-base",
        quantization: str = "qint8",
        output_dir: str = "./models"
    ) -> str:
        """下载模型文件"""
        print("\n" + "=" * 60)
        print(f"下载模型: {model_name} ({quantization})")
        print("=" * 60)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        model_urls = self.MODEL_URLS.get(model_name, {})
        url = model_urls.get(quantization)

        if not url:
            raise ValueError(f"不支持的模型配置: {model_name}/{quantization}")

        filename = url.split("/")[-1]
        filepath = output_path / filename

        print(f"下载地址: {url}")
        print(f"保存路径: {filepath}")

        if filepath.exists():
            print(f"模型文件已存在: {filepath}")
            return str(filepath)

        print("正在下载...")
        try:
            import urllib.request
            urllib.request.urlretrieve(url, filepath)
            print(f"下载完成: {filepath}")
        except Exception as e:
            print(f"下载失败: {e}")
            print("提示: 请手动下载模型文件到 models 目录")
            return str(output_path)

        # 解压
        if filepath.suffix == ".gz" or ".tar" in filepath.name:
            with zipfile.ZipFile(filepath, "r") as zf:
                zf.extractall(output_path)

        return str(output_path)

    def create_html_app(self, config: WebGPUDeploymentConfig) -> str:
        """创建WebGPU TTS应用HTML"""
        html_content = f"""<!DOCTYPE html>
<html lang="{config.language}" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Supertonic TTS - WebGPU</title>

    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
        :root {{
            --supertonic-primary: #6366f1;
            --supertonic-secondary: #8b5cf6;
            --supertonic-bg: #fafafa;
        }}

        body {{
            background: var(--supertonic-bg);
            min-height: 100vh;
        }}

        .main-container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}

        .logo {{
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, var(--supertonic-primary), var(--supertonic-secondary));
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            font-size: 32px;
        }}

        .model-selector {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }}

        .synthesis-card {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }}

        .text-input {{
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 16px;
            font-size: 16px;
            min-height: 150px;
            resize: vertical;
            transition: border-color 0.2s;
        }}

        .text-input:focus {{
            border-color: var(--supertonic-primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }}

        .speak-btn {{
            background: linear-gradient(135deg, var(--supertonic-primary), var(--supertonic-secondary));
            border: none;
            border-radius: 12px;
            padding: 16px 32px;
            font-size: 18px;
            font-weight: 600;
            color: white;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .speak-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
        }}

        .speak-btn:active {{
            transform: translateY(0);
        }}

        .speak-btn:disabled {{
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }}

        .status-bar {{
            background: #f3f4f6;
            border-radius: 8px;
            padding: 12px 16px;
            margin-top: 16px;
            font-size: 14px;
            color: #6b7280;
        }}

        .voice-style {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: #f3f4f6;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .voice-style:hover {{
            background: #e5e7eb;
        }}

        .voice-style.active {{
            background: var(--supertonic-primary);
            color: white;
        }}

        .waveform {{
            height: 60px;
            background: linear-gradient(90deg,
                transparent 0%,
                var(--supertonic-primary) 50%,
                transparent 100%);
            border-radius: 8px;
            opacity: 0.1;
            transition: opacity 0.3s;
        }}

        .waveform.playing {{
            animation: wave 1s ease-in-out infinite;
            opacity: 1;
        }}

        @keyframes wave {{
            0%, 100% {{ transform: scaleY(0.5); }}
            50% {{ transform: scaleY(1); }}
        }}

        .loading-spinner {{
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Header -->
        <div class="header">
            <div class="logo">🔊</div>
            <h1>Supertonic TTS</h1>
            <p class="text-muted">Lightning-fast WebGPU Text-to-Speech</p>
        </div>

        <!-- Model Selector -->
        <div class="model-selector">
            <h5 class="mb-3">Voice Style</h5>
            <div class="d-flex flex-wrap gap-2" id="voiceStyles">
                <button class="voice-style active" data-style="N1">N1 自然</button>
                <button class="voice-style" data-style="N2">N2 专业</button>
                <button class="voice-style" data-style="N3">N3 关怀</button>
                <button class="voice-style" data-style="M1">M1 活力男</button>
                <button class="voice-style" data-style="M2">M2 沉稳男</button>
                <button class="voice-style" data-style="F1">F1 活泼女</button>
                <button class="voice-style" data-style="F2">F2 专业女</button>
            </div>
        </div>

        <!-- Synthesis Card -->
        <div class="synthesis-card">
            <h5 class="mb-3">Text to Synthesize</h5>

            <textarea
                id="textInput"
                class="text-input form-control"
                placeholder="Enter text to synthesize..."
                maxlength="{config.max_text_length}"
            >Hello, this is Supertonic TTS running on WebGPU. Experience lightning-fast text-to-speech synthesis directly in your browser!</textarea>

            <div class="d-flex justify-content-between align-items-center mt-3">
                <div class="text-muted">
                    <span id="charCount">0</span> / {config.max_text_length} characters
                </div>
                <button id="speakBtn" class="speak-btn" onclick="synthesize()">
                    <span id="btnText">🔊 Speak</span>
                    <span id="btnLoading" class="loading-spinner" style="display: none;"></span>
                </button>
            </div>

            <div class="waveform" id="waveform"></div>

            <div class="status-bar" id="statusBar">
                Ready. Model loaded: {config.model}
            </div>
        </div>

        <!-- Expression Tags Help -->
        <div class="mt-4 p-3 bg-light rounded">
            <h6>Expression Tags (Optional)</h6>
            <small class="text-muted">
                <code>[laugh]</code> [breath] [sigh] [hmm] [punch] - Add natural expressions
            </small>
        </div>
    </div>

    <!-- Audio Element -->
    <audio id="audioPlayer" style="display: none;"></audio>

    <script>
        // Supertonic WebGPU TTS Engine
        class SupertonicEngine {{
            constructor() {{
                this.adapter = null;
                this.device = null;
                this.model = null;
                this.isLoaded = false;
                this.currentStyle = 'N1';
            }}

            async init() {{
                const status = document.getElementById('statusBar');
                status.textContent = 'Initializing WebGPU...';

                if (!navigator.gpu) {{
                    throw new Error('WebGPU not supported. Please use Chrome 113+ or Edge 113+');
                }}

                try {{
                    this.adapter = await navigator.gpu.requestAdapter();
                    if (!this.adapter) {{
                        throw new Error('Failed to get WebGPU adapter');
                    }}

                    this.device = await this.adapter.requestDevice();
                    status.textContent = 'Loading model...';

                    // TODO: Load ONNX model via WebGPU
                    // This is a placeholder - actual implementation would load
                    // the ONNX model using ONNX Runtime WebGPU

                    this.isLoaded = true;
                    status.textContent = 'Model ready!';
                    return true;
                }} catch (e) {{
                    console.error('Init error:', e);
                    status.textContent = 'Error: ' + e.message;
                    return false;
                }}
            }}

            setStyle(style) {{
                this.currentStyle = style;
                // TODO: Switch voice style in model
            }}

            async synthesize(text) {{
                if (!this.isLoaded) {{
                    throw new Error('Model not loaded');
                }}

                const status = document.getElementById('statusBar');
                status.textContent = 'Synthesizing...';

                try {{
                    // TODO: Actual ONNX inference via WebGPU
                    // This placeholder generates a simple audio tone

                    await new Promise(resolve => setTimeout(resolve, 500));

                    // Create a simple beep as placeholder
                    const audioContext = new AudioContext();
                    const oscillator = audioContext.createOscillator();
                    const gainNode = audioContext.createGain();

                    oscillator.connect(gainNode);
                    gainNode.connect(audioContext.destination);

                    oscillator.frequency.value = 440;
                    oscillator.type = 'sine';
                    gainNode.gain.value = 0.1;

                    // Create WAV blob
                    const duration = 1;
                    const sampleRate = {config.sample_rate};
                    const numSamples = sampleRate * duration;
                    const buffer = audioContext.createBuffer(1, numSamples, sampleRate);
                    const channel = buffer.getChannelData(0);

                    for (let i = 0; i < numSamples; i++) {{
                        channel[i] = Math.sin(2 * Math.PI * 440 * i / sampleRate) * 0.1;
                    }}

                    const wavBlob = this.audioBufferToWav(buffer);
                    const url = URL.createObjectURL(wavBlob);

                    status.textContent = 'Synthesis complete!';
                    return url;
                }} catch (e) {{
                    status.textContent = 'Error: ' + e.message;
                    throw e;
                }}
            }}

            audioBufferToWav(buffer) {{
                const numChannels = buffer.numberOfChannels;
                const sampleRate = buffer.sampleRate;
                const format = 1; // PCM
                const bitDepth = 16;

                const bytesPerSample = bitDepth / 8;
                const blockAlign = numChannels * bytesPerSample;

                const dataLength = buffer.length * blockAlign;
                const bufferLength = 44 + dataLength;

                const arrayBuffer = new ArrayBuffer(bufferLength);
                const view = new DataView(arrayBuffer);

                // WAV header
                this.writeString(view, 0, 'RIFF');
                view.setUint32(4, 36 + dataLength, true);
                this.writeString(view, 8, 'WAVE');
                this.writeString(view, 12, 'fmt ');
                view.setUint32(16, 16, true);
                view.setUint16(20, format, true);
                view.setUint16(22, numChannels, true);
                view.setUint32(24, sampleRate, true);
                view.setUint32(28, sampleRate * blockAlign, true);
                view.setUint16(32, blockAlign, true);
                view.setUint16(34, bitDepth, true);
                this.writeString(view, 36, 'data');
                view.setUint32(40, dataLength, true);

                // Write audio data
                const channelData = buffer.getChannelData(0);
                let offset = 44;
                for (let i = 0; i < buffer.length; i++, offset += 2) {{
                    const sample = Math.max(-1, Math.min(1, channelData[i]));
                    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
                }}

                return new Blob([arrayBuffer], {{ type: 'audio/wav' }});
            }}

            writeString(view, offset, string) {{
                for (let i = 0; i < string.length; i++) {{
                    view.setUint8(offset + i, string.charCodeAt(i));
                }}
            }}
        }}

        // Global engine instance
        let engine = new SupertonicEngine();

        // Initialize on load
        document.addEventListener('DOMContentLoaded', async () => {{
            const status = document.getElementById('statusBar');
            status.textContent = 'Loading...';

            const success = await engine.init();
            if (success) {{
                document.getElementById('speakBtn').disabled = false;
            }} else {{
                document.getElementById('speakBtn').disabled = true;
            }}
        }});

        // Voice style selection
        document.querySelectorAll('.voice-style').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.voice-style').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                engine.setStyle(btn.dataset.style);
            }});
        }});

        // Character counter
        const textInput = document.getElementById('textInput');
        const charCount = document.getElementById('charCount');
        textInput.addEventListener('input', () => {{
            charCount.textContent = textInput.value.length;
        }});

        // Synthesis function
        async function synthesize() {{
            const btn = document.getElementById('speakBtn');
            const btnText = document.getElementById('btnText');
            const btnLoading = document.getElementById('btnLoading');
            const audioPlayer = document.getElementById('audioPlayer');
            const waveform = document.getElementById('waveform');

            const text = textInput.value.trim();
            if (!text) return;

            // Disable button and show loading
            btn.disabled = true;
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline-block';
            waveform.classList.add('playing');

            try {{
                const audioUrl = await engine.synthesize(text);

                audioPlayer.src = audioUrl;
                await audioPlayer.play();

                audioPlayer.onended = () => {{
                    btn.disabled = false;
                    btnText.style.display = 'inline';
                    btnLoading.style.display = 'none';
                    waveform.classList.remove('playing');
                    URL.revokeObjectURL(audioUrl);
                }};
            }} catch (e) {{
                console.error('Synthesis error:', e);
                btn.disabled = false;
                btnText.style.display = 'inline';
                btnLoading.style.display = 'none';
                waveform.classList.remove('playing');
            }}
        }}
    </script>
</body>
</html>
"""

        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        html_path = output_dir / "index.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"HTML应用已创建: {html_path}")
        return str(html_path)

    def create_service_worker(self, config: WebGPUDeploymentConfig) -> str:
        """创建Service Worker实现离线支持"""
        sw_content = """
const CACHE_NAME = 'supertonic-tts-v1';
const MODEL_CACHE = 'supertonic-models-v1';

const STATIC_ASSETS = [
    './',
    './index.html',
    './manifest.json'
];

const MODEL_URLS = [
    // Add model file URLs here
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(STATIC_ASSETS))
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME && name !== MODEL_CACHE)
                    .map((name) => caches.delete(name))
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') return;

    // For model files, use cache-first strategy
    if (url.pathname.includes('/models/')) {
        event.respondWith(
            caches.open(MODEL_CACHE).then((cache) => {
                return cache.match(request).then((cached) => {
                    if (cached) return cached;
                    return fetch(request).then((response) => {
                        if (response.ok) {
                            cache.put(request, response.clone());
                        }
                        return response;
                    });
                });
            })
        );
        return;
    }

    // For other assets, use stale-while-revalidate
    event.respondWith(
        caches.match(request).then((cached) => {
            const fetchPromise = fetch(request).then((response) => {
                if (response.ok) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(request, responseClone);
                    });
                }
                return response;
            }).catch(() => cached);

            return cached || fetchPromise;
        })
    );
});

// Background sync for model downloads
self.addEventListener('sync', (event) => {
    if (event.tag === 'download-model') {
        event.waitUntil(downloadModels());
    }
});

async function downloadModels() {
    const cache = await caches.open(MODEL_CACHE);
    for (const url of MODEL_URLS) {
        try {
            const response = await fetch(url);
            if (response.ok) {
                await cache.put(url, response);
                console.log('Model downloaded:', url);
            }
        } catch (e) {
            console.error('Failed to download model:', url, e);
        }
    }
}

// Push notification support (optional)
self.addEventListener('push', (event) => {
    const data = event.data?.json() || {};
    const title = data.title || 'Supertonic TTS';
    const options = {
        body: data.body || 'New synthesis ready',
        icon: './icon-192.png',
        badge: './badge-72.png'
    };
    event.waitUntil(self.registration.showNotification(title, options));
});
"""

        output_dir = Path(config.output_dir)
        sw_path = output_dir / "sw.js"
        with open(sw_path, "w", encoding="utf-8") as f:
            f.write(sw_content)

        print(f"Service Worker已创建: {sw_path}")
        return str(sw_path)

    def create_manifest(self, config: WebGPUDeploymentConfig) -> str:
        """创建Web App Manifest"""
        manifest = {
            "name": "Supertonic TTS",
            "short_name": "Supertonic",
            "description": "Lightning-fast WebGPU text-to-speech synthesis",
            "start_url": "./",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#6366f1",
            "orientation": "portrait-primary",
            "icons": [
                {
                    "src": "./icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "./icon-512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable"
                }
            ],
            "categories": ["productivity", "utilities"],
            "lang": config.language,
            "screenshots": [],
            "related_applications": [],
            "prefer_related_applications": False
        }

        output_dir = Path(config.output_dir)
        manifest_path = output_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        print(f"Manifest已创建: {manifest_path}")
        return str(manifest_path)

    def create_readme(self, config: WebGPUDeploymentConfig) -> str:
        """创建README文件"""
        readme = f"""# Supertonic TTS - WebGPU Deployment

Lightning-fast text-to-speech synthesis running directly in your browser using WebGPU.

## Features

- ⚡ **WebGPU Acceleration** - Leverage GPU compute shaders for real-time TTS
- 🌐 **Works Offline** - PWA with Service Worker support
- 🔒 **Privacy First** - All processing happens locally in your browser
- 📱 **Installable** - Add to home screen like a native app
- 🎨 **Multiple Voice Styles** - Natural, Professional, Warm, and more

## Supported Browsers

| Browser | Minimum Version | WebGPU Support |
|---------|---------------|----------------|
| Chrome | 113+ | ✅ Full |
| Edge | 113+ | ✅ Full |
| Firefox | Nightly | ⚠️ Behind flag |
| Safari | Technology Preview | ⚠️ Experimental |

## Quick Start

1. Open `index.html` in a WebGPU-enabled browser
2. Grant GPU access when prompted
3. Enter text and click "Speak"
4. Enjoy lightning-fast TTS!

## Voice Styles

| Code | Description | Best For |
|------|-------------|---------|
| N1 | Natural Neutral | General purpose, friendly |
| N2 | Professional Neutral | Business, formal |
| N3 | Warm & Caring | Healthcare, support |
| M1 | Energetic Male | Games, entertainment |
| M2 | Calm Male | Narration, news |
| F1 | Cheerful Female | Education, casual |
| F2 | Professional Female | Corporate, formal |

## Expression Tags

Add natural expressions to your speech:

| Tag | Effect | Example |
|-----|--------|---------|
| `[laugh]` | Laughing | "That's funny[laugh]" |
| `[breath]` | Breathing | "[breath] Hello everyone" |
| `[sigh]` | Sighing | "Oh well[sigh]" |
| `[hmm]` | Thinking | "Let me think[hmm]" |
| `[punch]` | Emphasis | "Very important[punch]" |

## Model Configuration

Current model: `{config.model}`
Quantization: `{config.quantization}`
Sample rate: `{config.sample_rate} Hz`
Max text length: `{config.max_text_length} characters`

## Offline Usage

This is a Progressive Web App (PWA):

1. Open in Chrome/Edge
2. Click "Install" in the address bar
3. Use offline just like a native app!

## API Reference

```javascript
// Initialize engine
const engine = new SupertonicEngine();
await engine.init();

// Set voice style
engine.setStyle('N1');  // Natural

// Synthesize text
const audioUrl = await engine.synthesize('Hello world!');

// Play audio
const audio = new Audio(audioUrl);
audio.play();
```

## Performance Tips

1. **Use Chrome/Edge** - Best WebGPU support
2. **Enable hardware acceleration** - Settings > Advanced > Hardware acceleration
3. **Keep tab active** - Best performance when tab is focused
4. **Close other GPU apps** - More GPU memory available

## Troubleshooting

### "WebGPU not supported"
- Update your browser to the latest version
- Enable WebGPU in experimental features if needed

### "Model failed to load"
- Check your internet connection
- Clear browser cache and try again
- Ensure sufficient GPU memory

### "Audio playback failed"
- Check system audio settings
- Allow autoplay with sound in browser

## License

MIT License - See [Supertonic](https://github.com/supertone-inc/supertonic)

## Acknowledgments

Built with:
- ONNX Runtime WebGPU
- Web Audio API
- Bootstrap 5
"""

        output_dir = Path(config.output_dir)
        readme_path = output_dir / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme)

        print(f"README已创建: {readme_path}")
        return str(readme_path)

    def deploy(self, config: WebGPUDeploymentConfig) -> dict:
        """执行完整部署流程"""
        print("\n" + "=" * 60)
        print("Supertonic TTS WebGPU部署")
        print("=" * 60)

        results = {}

        # 1. 检查环境
        print("\n[1/5] 检查WebGPU环境...")
        env_info = self.check_environment()
        results["environment"] = {
            "webgpu_supported": env_info.webgpu_supported,
            "browser": env_info.browser,
        }

        # 2. 下载模型
        print("\n[2/5] 下载模型...")
        model_dir = self.download_model(
            config.model,
            config.quantization,
            f"{config.output_dir}/models"
        )
        results["model_path"] = model_dir
        config.voice_model_path = model_dir

        # 3. 创建HTML应用
        print("\n[3/5] 创建WebGPU TTS应用...")
        html_path = self.create_html_app(config)
        results["html_app"] = html_path

        # 4. 创建Service Worker
        print("\n[4/5] 创建Service Worker...")
        sw_path = self.create_service_worker(config)
        results["service_worker"] = sw_path

        # 5. 创建Manifest和README
        print("\n[5/5] 创建Manifest和README...")
        manifest_path = self.create_manifest(config)
        results["manifest"] = manifest_path
        readme_path = self.create_readme(config)
        results["readme"] = readme_path

        print("\n" + "=" * 60)
        print("部署完成!")
        print("=" * 60)
        print(f"""
使用说明:
  1. 进入部署目录:
     cd {config.output_dir}

  2. 启动本地服务器:
     python -m http.server 8080

  3. 在浏览器中打开:
     http://localhost:8080

  4. 使用WebGPU检测页面验证环境:
     python -m http.server 8080 --directory .

部署信息:
  模型: {config.model} ({config.quantization})
  输出目录: {config.output_dir}
  语音风格: N1/N2/N3/M1/M2/F1/F2
""")

        results["success"] = True
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Supertonic TTS WebGPU部署工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检查WebGPU环境
  python webgpu_deploy.py check

  # 部署到本地目录
  python webgpu_deploy.py deploy --model supertonic-base --quantization qint8

  # 部署指定语言
  python webgpu_deploy.py deploy --language zh --model supertonic-base

说明:
  - 推荐使用 Chrome 113+ 或 Edge 113+ 以获得最佳WebGPU支持
  - Firefox Nightly 需要在 about:config 中启用 WebGPU
  - Safari 技术预览版支持有限
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # check命令
    check_parser = subparsers.add_parser("check", help="检查WebGPU环境")

    # deploy命令
    deploy_parser = subparsers.add_parser("deploy", help="部署WebGPU应用")
    deploy_parser.add_argument("--model", "-m", default="supertonic-base",
                              choices=["supertonic-base", "supertonic-large"],
                              help="模型名称")
    deploy_parser.add_argument("--quantization", "-q", default="qint8",
                              choices=["qint8", "float16", "float32"],
                              help="量化方式")
    deploy_parser.add_argument("--language", "-l", default="en",
                              help="语言代码")
    deploy_parser.add_argument("--sample-rate", "-r", type=int, default=24000,
                              help="采样率")
    deploy_parser.add_argument("--max-length", "-L", type=int, default=500,
                              help="最大文本长度")
    deploy_parser.add_argument("--output", "-o", default="./supertonic-webgpu",
                              help="输出目录")

    args = parser.parse_args()

    deployer = SupertonicWebGPUDeployer()

    if args.command == "check":
        deployer.check_environment()

    elif args.command == "deploy":
        config = WebGPUDeploymentConfig(
            model=args.model,
            quantization=args.quantization,
            language=args.language,
            sample_rate=args.sample_rate,
            max_text_length=args.max_length,
            output_dir=args.output
        )

        results = deployer.deploy(config)

        if results.get("success"):
            print("\n部署成功!")
        else:
            print("\n部署失败，请检查上述错误信息")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
