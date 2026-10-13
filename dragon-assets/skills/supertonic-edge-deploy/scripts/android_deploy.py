#!/usr/bin/env python3
"""
Supertonic Edge Deploy - Android部署脚本

在Android设备上部署Supertonic TTS边缘推理引擎
来源: https://github.com/supertone-inc/supertonic
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AndroidDeploymentConfig:
    """Android部署配置"""
    model: str = "supertonic-base"
    language: str = "en"
    quantization: str = "int8"  # int8, float16, float32
    device_type: str = "phone"  # phone, tablet, automotive
    min_sdk: int = 24  # Android 7.0
    target_sdk: int = 34  # Android 14
    abi_filters: list = field(default_factory=lambda: ["arm64-v8a", "armeabi-v7a"])
    threads: int = 4
    sample_rate: int = 24000
    output_dir: str = "./supertonic-android"


@dataclass
class AndroidDeviceInfo:
    """Android设备信息"""
    brand: str
    model: str
    android_version: str
    sdk_version: int
    cpu_arch: str
    cpu_cores: int
    total_ram_mb: int
    gpu_renderer: str
    is_64bit: bool


class SupertonicAndroidDeployer:
    """Supertonic Android部署器"""

    # 模型下载URL (示例)
    MODEL_URLS = {
        "supertonic-base": {
            "int8": "https://github.com/supertone-inc/supertonic/releases/download/v1.0/supertonic-base-int8-android.tar.gz",
            "float16": "https://github.com/supertone-inc/supertonic/releases/download/v1.0/supertonic-base-f16-android.tar.gz",
        },
        "supertonic-large": {
            "int8": "https://github.com/supertone-inc/supertonic/releases/download/v1.0/supertonic-large-int8-android.tar.gz",
            "float16": "https://github.com/supertone-inc/supertonic/releases/download/v1.0/supertonic-large-f16-android.tar.gz",
        },
    }

    def __init__(self):
        self.config = None
        self.adb_path = self._find_adb()
        self.aapt_path = self._find_aapt()

    def _find_adb(self) -> Optional[str]:
        """查找adb路径"""
        # 检查环境变量
        if os.getenv("ANDROID_HOME"):
            adb = Path(os.getenv("ANDROID_HOME")) / "platform-tools" / ("adb.exe" if sys.platform == "win32" else "adb")
            if adb.exists():
                return str(adb)

        # 常见路径
        common_paths = [
            "C:/Users/{}/AppData/Local/Android/Sdk/platform-tools/adb.exe".format(os.getenv("USERNAME", "")),
            "/usr/local/bin/adb",
            "/opt/android-sdk/platform-tools/adb",
        ]
        for path in common_paths:
            if Path(path).exists():
                return path

        # PATH中查找
        for path in os.environ.get("PATH", "").split(os.pathsep):
            adb = Path(path) / ("adb.exe" if sys.platform == "win32" else "adb")
            if adb.exists():
                return str(adb)

        return None

    def _find_aapt(self) -> Optional[str]:
        """查找aapt路径"""
        if os.getenv("ANDROID_HOME"):
            aapt = Path(os.getenv("ANDROID_HOME")) / "build-tools" / "latest" / ("aapt.exe" if sys.platform == "win32" else "aapt")
            if aapt.exists():
                return str(aapt)
        return None

    def check_device(self) -> Optional[AndroidDeviceInfo]:
        """检查连接的Android设备"""
        if not self.adb_path:
            print("警告: 未找到adb，请安装Android SDK Platform Tools")
            return None

        # 获取设备列表
        result = subprocess.run(
            [self.adb_path, "devices", "-l"],
            capture_output=True,
            text=True
        )

        devices_output = result.stdout.strip()
        if "device:" not in devices_output:
            print("未检测到Android设备，请确保设备已连接并启用USB调试")
            return None

        # 获取设备型号
        device_id = devices_output.split("device:")[1].split()[0] if "device:" in devices_output else None
        if not device_id:
            return None

        # 获取设备信息
        info = {}

        # 品牌和型号
        result = subprocess.run(
            [self.adb_path, "-s", device_id, "shell", "getprop", "ro.product.brand"],
            capture_output=True, text=True
        )
        info["brand"] = result.stdout.strip()

        result = subprocess.run(
            [self.adb_path, "-s", device_id, "shell", "getprop", "ro.product.model"],
            capture_output=True, text=True
        )
        info["model"] = result.stdout.strip()

        # Android版本
        result = subprocess.run(
            [self.adb_path, "-s", device_id, "shell", "getprop", "ro.build.version.release"],
            capture_output=True, text=True
        )
        info["android_version"] = result.stdout.strip()

        result = subprocess.run(
            [self.adb_path, "-s", device_id, "shell", "getprop", "ro.build.version.sdk"],
            capture_output=True, text=True
        )
        info["sdk_version"] = int(result.stdout.strip() or "24")

        # CPU信息
        result = subprocess.run(
            [self.adb_path, "-s", device_id, "shell", "getprop", "ro.product.cpu.abi"],
            capture_output=True, text=True
        )
        info["cpu_arch"] = result.stdout.strip()

        # 核心数
        result = subprocess.run(
            [self.adb_path, "-s", device_id, "shell", "cat", "/proc/cpuinfo"],
            capture_output=True, text=True
        )
        cpu_cores = result.stdout.count("processor")
        info["cpu_cores"] = cpu_cores if cpu_cores > 0 else 4

        # 内存信息
        result = subprocess.run(
            [self.adb_path, "-s", device_id, "shell", "cat", "/proc/meminfo"],
            capture_output=True, text=True
        )
        for line in result.stdout.split("\n"):
            if line.startswith("MemTotal"):
                kb = int(line.split()[1])
                info["total_ram_mb"] = kb // 1024
                break
        else:
            info["total_ram_mb"] = 0

        # GPU信息
        result = subprocess.run(
            [self.adb_path, "-s", device_id, "shell", "dumpsys", "SurfaceFlinger", "|", "grep", "GLES"],
            capture_output=True, text=True
        )
        info["gpu_renderer"] = result.stdout.strip().split("\n")[0] if result.stdout else "Unknown"

        # 64位检查
        is_64bit = "arm64" in info.get("cpu_arch", "") or "x86_64" in info.get("cpu_arch", "")
        info["is_64bit"] = is_64bit

        device_info = AndroidDeviceInfo(
            brand=info.get("brand", "Unknown"),
            model=info.get("model", "Unknown"),
            android_version=info.get("android_version", "Unknown"),
            sdk_version=info.get("sdk_version", 24),
            cpu_arch=info.get("cpu_arch", "Unknown"),
            cpu_cores=info.get("cpu_cores", 4),
            total_ram_mb=info.get("total_ram_mb", 0),
            gpu_renderer=info.get("gpu_renderer", "Unknown"),
            is_64bit=info.get("is_64bit", False)
        )

        print("=" * 60)
        print("Android设备信息")
        print("=" * 60)
        print(f"  品牌: {device_info.brand}")
        print(f"  型号: {device_info.model}")
        print(f"  Android版本: {device_info.android_version} (API {device_info.sdk_version})")
        print(f"  CPU架构: {device_info.cpu_arch} {'(64bit)' if device_info.is_64bit else '(32bit)'}")
        print(f"  CPU核心: {device_info.cpu_cores}")
        print(f"  内存: {device_info.total_ram_mb} MB")
        print(f"  GPU: {device_info.gpu_renderer[:50] if device_info.gpu_renderer else 'Unknown'}...")

        return device_info

    def check_compatibility(self, info: AndroidDeviceInfo, config: AndroidDeploymentConfig) -> tuple[bool, list[str]]:
        """检查设备兼容性"""
        issues = []

        # SDK版本检查
        if info.sdk_version < config.min_sdk:
            issues.append(f"错误: Android版本过低，需要API {config.min_sdk}+，当前 {info.sdk_version}")

        # 内存检查
        if info.total_ram_mb < 1000:
            issues.append(f"警告: 内存({info.total_ram_mb}MB)较低，建议至少2GB")
        elif info.total_ram_mb < 2000:
            issues.append(f"提示: 内存({info.total_ram_mb}MB)一般，建议使用int8量化")

        # 架构检查
        if config.quantization == "float16" and not info.is_64bit:
            issues.append("警告: float16需要64位设备，32位设备建议使用int8")

        # 设备类型建议
        if config.device_type == "automotive" and info.sdk_version < 29:
            issues.append("警告: Automotive建议使用Android 10+ (API 29)")

        return len([i for i in issues if i.startswith("错误")]) == 0, issues

    def install_dependencies(self) -> bool:
        """安装Python依赖(通过adb)"""
        if not self.adb_path:
            print("错误: 需要Android SDK Platform Tools")
            return False

        print("\n" + "=" * 60)
        print("安装依赖...")
        print("=" * 60)

        # 检查Termux或Python环境
        print("\n在Android设备上安装Python环境:")
        print("1. 安装Termux应用")
        print("2. 运行: pkg update && pkg install python")
        print("3. 运行: pip install numpy soundfile onnxruntime")
        print("\n或者使用Pydroid 3应用")

        return True

    def create_gradle_project(self, config: AndroidDeploymentConfig) -> str:
        """创建Android Gradle项目"""
        print("\n" + "=" * 60)
        print("创建Android项目...")
        print("=" * 60)

        project_dir = Path(config.output_dir)
        project_dir.mkdir(parents=True, exist_ok=True)

        # 项目结构
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "app" / "src" / "main" / "java" / "com" / "supertonic" / "tts").mkdir(parents=True, exist_ok=True)
        (project_dir / "app" / "src" / "main" / "jniLibs" / "arm64-v8a").mkdir(parents=True, exist_ok=True)
        (project_dir / "app" / "src" / "main" / "jniLibs" / "armeabi-v7a").mkdir(parents=True, exist_ok=True)
        (project_dir / "app" / "src" / "main" / "assets").mkdir(parents=True, exist_ok=True)
        (project_dir / "app" / "src" / "main" / "res" / "layout").mkdir(parents=True, exist_ok=True)

        # settings.gradle.kts
        settings_content = '''pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "SupertonicTTS"
include(":app")
'''

        (project_dir / "settings.gradle.kts").write_text(settings_content, encoding="utf-8")

        # build.gradle.kts (root)
        root_build_content = '''// Top-level build file
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.20" apply false
}
'''

        (project_dir / "build.gradle.kts").write_text(root_build_content, encoding="utf-8")

        # gradle.properties
        gradle_props = '''android.useAndroidX=true
android.enableJetifier=true
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
'''
        (project_dir / "gradle.properties").write_text(gradle_props, encoding="utf-8")

        # app/build.gradle.kts
        app_build = f'''plugins {{
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}}

android {{
    namespace = "com.supertonic.tts"
    compileSdk = {config.target_sdk}

    defaultConfig {{
        applicationId = "com.supertonic.tts"
        minSdk = {config.min_sdk}
        targetSdk = {config.target_sdk}
        versionCode = 1
        versionName = "1.0"

        ndk {{
            abiFilters += listOf({", ".join(f'"{abi}"' for abi in config.abi_filters)})
        }}
    }}

    buildTypes {{
        release {{
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }}
    }}

    compileOptions {{
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }}

    kotlinOptions {{
        jvmTarget = "17"
    }}
}}

dependencies {{
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")

    // ONNX Runtime
    val onnxVersion = "1.16.3"
    implementation("com.microsoft.onnxruntime:onnxruntime-android:$onnxVersion")

    // 音频处理
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}}
'''

        (project_dir / "app" / "build.gradle.kts").write_text(app_build, encoding="utf-8")

        # proguard-rules.pro
        proguard_rules = '''# ONNX Runtime
-keep class ai.onnxruntime.** { *; }

# Supertonic模型
-keep class com.supertonic.tts.model.** { *; }
'''
        (project_dir / "app" / "proguard-rules.pro").write_text(proguard_rules, encoding="utf-8")

        # AndroidManifest.xml
        manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"
        android:maxSdkVersion="28" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="Supertonic TTS"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.SupertonicTTS">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.SupertonicTTS">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- TTS服务 -->
        <service
            android:name=".SupertonicTTSService"
            android:exported="false">
            <intent-filter>
                <action android:name="android.intent.action.TTS_SERVICE" />
                <category android:name="android.intent.category.DEFAULT" />
            </intent-filter>
        </service>

    </application>

</manifest>
'''
        (project_dir / "app" / "src" / "main" / "AndroidManifest.xml").write_text(manifest, encoding="utf-8")

        print(f"Android项目已创建: {project_dir}")
        return str(project_dir)

    def create_inference_engine(self, output_dir: str) -> str:
        """创建推理引擎"""
        engine_content = '''package com.supertonic.tts

import ai.onnxruntime.OnnxRuntime
import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.nio.FloatBuffer

/**
 * Supertonic TTS推理引擎
 */
class SupertonicEngine(
    private val modelPath: String,
    private val config: TTSConfig
) {
    private val environment: OrtEnvironment = OnnxRuntime.getEnv()
    private val session: OrtSession = environment.createSession(modelPath)

    data class TTSConfig(
        val sampleRate: Int = 24000,
        val threads: Int = 4,
        val quantization: String = "int8"
    )

    /**
     * 合成语音
     */
    suspend fun synthesize(text: String): ByteArray = withContext(Dispatchers.Default) {
        // 文本预处理
        val inputIds = preprocessText(text)

        // 创建输入张量
        val inputTensor = OnnxTensor.createTensor(
            environment,
            LongArray(inputIds.size) { inputIds[it].toLong() },
            longArrayOf(1L, inputIds.size.toLong())
        )

        // 运行推理
        val outputs = session.run(mapOf("input_ids" to inputTensor))

        // 后处理音频
        val audioData = postprocessAudio(outputs[0].value as FloatArray)

        inputTensor.close()
        audioData
    }

    private fun preprocessText(text: String): List<Int> {
        // 简化的文本转ID (实际需要Tokenizer)
        return text.map { it.code }.take(512)
    }

    private fun postprocessAudio(floatArray: FloatArray): ByteArray {
        // Float32 PCM转Int16 PCM
        val pcm16 = ShortArray(floatArray.size)
        for (i in floatArray.indices) {
            val sample = (floatArray[i] * 32767).toInt().coerceIn(-32768, 32767)
            pcm16[i] = sample.toShort()
        }

        // 转字节数组
        val bytes = ByteArray(pcm16.size * 2)
        for (i in pcm16.indices) {
            bytes[i * 2] = (pcm16[i].toInt() and 0xFF).toByte()
            bytes[i * 2 + 1] = ((pcm16[i].toInt() shr 8) and 0xFF).toByte()
        }
        return bytes
    }
}
'''

        java_dir = Path(output_dir) / "app" / "src" / "main" / "java" / "com" / "supertonic" / "tts"
        (java_dir / "SupertonicEngine.kt").write_text(engine_content, encoding="utf-8")
        return str(java_dir / "SupertonicEngine.kt")

    def create_tts_service(self, output_dir: str) -> str:
        """创建Android TTS服务"""
        service_content = '''package com.supertonic.tts

import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.os.Build
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.io.File
import java.util.Locale

/**
 * Supertonic TTS Android服务
 */
class SupertonicTTSService : TextToSpeech.OnInitListener {
    private var tts: TextToSpeech? = null
    private var engine: SupertonicEngine? = null
    private val scope = CoroutineScope(Dispatchers.Main)

    private val sampleRate = 24000
    private val channelConfig = AudioFormat.CHANNEL_OUT_MONO
    private val audioFormat = AudioFormat.ENCODING_PCM_16BIT

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            tts?.language = Locale.US
        }
    }

    /**
     * 初始化推理引擎
     */
    fun initialize(modelDir: File) {
        scope.launch {
            val modelFile = File(modelDir, "model.onnx")
            if (modelFile.exists()) {
                engine = SupertonicEngine(
                    modelPath = modelFile.absolutePath,
                    config = SupertonicEngine.TTSConfig(
                        sampleRate = sampleRate,
                        threads = Runtime.getRuntime().availableProcessors()
                    )
                )
            }
        }
    }

    /**
     * 合成并播放
     */
    fun speak(text: String) {
        scope.launch {
            engine?.synthesize(text)?.let { audioData ->
                playAudio(audioData)
            } ?: run {
                // 回退到系统TTS
                tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, text.hashCode().toString())
            }
        }
    }

    private fun playAudio(audioData: ByteArray) {
        val bufferSize = AudioTrack.getMinBufferSize(sampleRate, channelConfig, audioFormat)

        val audioTrack = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            AudioTrack.Builder()
                .setAudioAttributes(
                    AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                        .build()
                )
                .setAudioFormat(
                    AudioFormat.Builder()
                        .setEncoding(audioFormat)
                        .setSampleRate(sampleRate)
                        .setChannelMask(channelConfig)
                        .build()
                )
                .setBufferSizeInBytes(bufferSize)
                .setTransferMode(AudioTrack.MODE_STREAM)
                .build()
        } else {
            @Suppress("DEPRECATION")
            AudioTrack(
                AudioManager.STREAM_MUSIC,
                sampleRate,
                channelConfig,
                audioFormat,
                bufferSize,
                AudioTrack.MODE_STREAM
            )
        }

        audioTrack.play()
        audioTrack.write(audioData, 0, audioData.size)
        audioTrack.stop()
        audioTrack.release()
    }

    fun shutdown() {
        tts?.stop()
        tts?.shutdown()
    }
}
'''

        java_dir = Path(output_dir) / "app" / "src" / "main" / "java" / "com" / "supertonic" / "tts"
        (java_dir / "SupertonicTTSService.kt").write_text(service_content, encoding="utf-8")
        return str(java_dir / "SupertonicTTSService.kt")

    def create_main_activity(self, output_dir: str) -> str:
        """创建MainActivity"""
        activity_content = '''package com.supertonic.tts

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

/**
 * Supertonic TTS演示应用
 */
class MainActivity : AppCompatActivity() {
    private lateinit var ttsService: SupertonicTTSService
    private lateinit var textInput: EditText
    private lateinit var speakButton: Button
    private lateinit var statusText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        textInput = findViewById(R.id.text_input)
        speakButton = findViewById(R.id.speak_button)
        statusText = findViewById(R.id.status_text)

        ttsService = SupertonicTTSService { status ->
            runOnUiThread {
                statusText.text = when (status) {
                    TextToSpeech.SUCCESS -> "TTS引擎就绪"
                    else -> "TTS引擎初始化失败"
                }
            }
        }

        speakButton.setOnClickListener {
            val text = textInput.text.toString()
            if (text.isNotBlank()) {
                ttsService.speak(text)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        ttsService.shutdown()
    }
}
'''

        java_dir = Path(output_dir) / "app" / "src" / "main" / "java" / "com" / "supertonic" / "tts"
        (java_dir / "MainActivity.kt").write_text(activity_content, encoding="utf-8")
        return str(java_dir / "MainActivity.kt")

    def create_layout(self, output_dir: str) -> str:
        """创建布局文件"""
        layout_content = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Supertonic TTS"
        android:textSize="24sp"
        android:textStyle="bold"
        android:layout_gravity="center_horizontal"
        android:layout_marginBottom="16dp" />

    <EditText
        android:id="@+id/text_input"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:hint="输入要合成的文本..."
        android:inputType="textMultiLine"
        android:gravity="top"
        android:padding="8dp" />

    <Button
        android:id="@+id/speak_button"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="合成语音"
        android:layout_marginTop="8dp" />

    <TextView
        android:id="@+id/status_text"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="正在初始化..."
        android:layout_gravity="center_horizontal"
        android:layout_marginTop="8dp" />

</LinearLayout>
'''

        layout_dir = Path(output_dir) / "app" / "src" / "main" / "res" / "layout"
        (layout_dir / "activity_main.xml").write_text(layout_content, encoding="utf-8")
        return str(layout_dir / "activity_main.xml")

    def deploy(self, config: AndroidDeploymentConfig) -> dict:
        """执行完整部署流程"""
        print("\n" + "=" * 60)
        print("Supertonic TTS Android部署")
        print("=" * 60)

        results = {}

        # 1. 检查设备
        print("\n[1/5] 检查Android设备...")
        device_info = self.check_device()
        if device_info:
            results["device_info"] = {
                "brand": device_info.brand,
                "model": device_info.model,
                "sdk_version": device_info.sdk_version,
                "cpu_arch": device_info.cpu_arch,
                "ram_mb": device_info.total_ram_mb,
            }

            # 检查兼容性
            compatible, issues = self.check_compatibility(device_info, config)
            results["compatible"] = compatible
            results["issues"] = issues

            if not compatible:
                print("\n兼容性检查失败:")
                for issue in issues:
                    print(f"  - {issue}")
                return results
        else:
            # 无设备时仍创建项目
            print("未检测到设备，将创建可导入Android Studio的项目")

        # 2. 创建项目结构
        print("\n[2/5] 创建Android项目...")
        project_dir = self.create_gradle_project(config)
        results["project_dir"] = project_dir

        # 3. 创建推理引擎
        print("\n[3/5] 创建推理引擎...")
        self.create_inference_engine(project_dir)

        # 4. 创建TTS服务
        print("\n[4/5] 创建TTS服务...")
        self.create_tts_service(project_dir)

        # 5. 创建MainActivity
        print("\n[5/5] 创建UI...")
        self.create_main_activity(project_dir)
        self.create_layout(project_dir)

        # 创建配置文件
        config_data = {
            "model": config.model,
            "language": config.language,
            "quantization": config.quantization,
            "device_type": config.device_type,
            "min_sdk": config.min_sdk,
            "target_sdk": config.target_sdk,
            "abi_filters": config.abi_filters,
            "inference": {
                "sample_rate": config.sample_rate,
                "threads": config.threads,
            },
        }
        config_file = Path(project_dir) / "app" / "src" / "main" / "assets" / "config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(json.dumps(config_data, indent=2), encoding="utf-8")
        results["config_file"] = str(config_file)

        print("\n" + "=" * 60)
        print("部署完成!")
        print("=" * 60)
        print(f"""
使用说明:
  1. 在Android Studio中打开项目:
     cd {project_dir}
     open .

  2. 复制ONNX模型到 assets 目录:
     cp /path/to/model.onnx app/src/main/assets/

  3. 连接Android设备并构建运行:
     ./gradlew installDebug

  4. 或通过ADB安装APK:
     adb install app/build/outputs/apk/debug/app-debug.apk

部署配置:
  模型: {config.model} ({config.quantization})
  目标SDK: {config.target_sdk}
  ABI过滤: {", ".join(config.abi_filters)}
  输出目录: {project_dir}
""")

        results["success"] = True
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Supertonic TTS Android部署工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检查连接设备
  python android_deploy.py check

  # 创建项目
  python android_deploy.py deploy --model supertonic-base --quantization int8

  # Automotive专用配置
  python android_deploy.py deploy --device-type automotive --min-sdk 29

说明:
  - 需要Android SDK Platform Tools (adb)
  - 支持Android 7.0 (API 24)及以上
  - 推荐设备: 2GB+ RAM, ARM64架构
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # check命令
    check_parser = subparsers.add_parser("check", help="检查Android设备")

    # deploy命令
    deploy_parser = subparsers.add_parser("deploy", help="部署到Android设备")
    deploy_parser.add_argument("--model", "-m", default="supertonic-base",
                              choices=["supertonic-base", "supertonic-large"],
                              help="模型名称")
    deploy_parser.add_argument("--quantization", "-q", default="int8",
                              choices=["int8", "float16", "float32"],
                              help="量化方式")
    deploy_parser.add_argument("--device-type", "-d", default="phone",
                              choices=["phone", "tablet", "automotive"],
                              help="设备类型")
    deploy_parser.add_argument("--min-sdk", type=int, default=24,
                              help="最低Android版本 (API)")
    deploy_parser.add_argument("--target-sdk", type=int, default=34,
                              help="目标Android版本 (API)")
    deploy_parser.add_argument("--threads", "-t", type=int, default=4,
                              help="推理线程数")
    deploy_parser.add_argument("--sample-rate", "-r", type=int, default=24000,
                              help="采样率")
    deploy_parser.add_argument("--output", "-o", default="./supertonic-android",
                              help="输出目录")

    args = parser.parse_args()

    deployer = SupertonicAndroidDeployer()

    if args.command == "check":
        deployer.check_device()

    elif args.command == "deploy":
        config = AndroidDeploymentConfig(
            model=args.model,
            quantization=args.quantization,
            device_type=args.device_type,
            min_sdk=args.min_sdk,
            target_sdk=args.target_sdk,
            threads=args.threads,
            sample_rate=args.sample_rate,
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
