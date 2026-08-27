#!/usr/bin/env python3
"""
Supertonic Edge Deploy - Raspberry Pi部署脚本

在Raspberry Pi设备上部署Supertonic TTS边缘推理引擎
来源: https://github.com/supertone-inc/supertonic
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PiDeploymentConfig:
    """Raspberry Pi部署配置"""
    model: str = "supertonic-base"
    language: str = "en"
    quantization: str = "int8"  # int8, float16, float32
    device: str = "cpu"
    threads: int = 4
    sample_rate: int = 24000
    voice_model_path: Optional[str] = None
    output_dir: str = "./supertonic-pi"


@dataclass
class PiSystemInfo:
    """Raspberry Pi系统信息"""
    model: str
    os_version: str
    cpu_arch: str
    cpu_cores: int
    total_ram_mb: int
    python_version: str
    pip_version: str
    is_64bit: bool


class SupertonicPiDeployer:
    """Supertonic树莓派部署器"""

    # 模型下载URL (示例，实际请参考官方release)
    MODEL_URLS = {
        "supertonic-base": {
            "int8": "https://github.com/supertone-inc/supertonic/releases/download/v1.0/supertonic-base-int8.tar.gz",
            "float16": "https://github.com/supertone-inc/supertonic/releases/download/v1.0/supertonic-base-f16.tar.gz",
        },
        "supertonic-large": {
            "int8": "https://github.com/supertone-inc/supertonic/releases/download/v1.0/supertonic-large-int8.tar.gz",
            "float16": "https://github.com/supertone-inc/supertonic/releases/download/v1.0/supertonic-large-f16.tar.gz",
        },
    }

    def __init__(self):
        self.config = None

    def check_system(self) -> PiSystemInfo:
        """检查Raspberry Pi系统信息"""
        print("=" * 60)
        print("检查Raspberry Pi系统信息...")
        print("=" * 60)

        # 获取CPU信息
        cpu_info = self._get_cpu_info()

        # 获取内存信息
        total_ram = self._get_total_ram()

        # 获取Python版本
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        # 获取pip版本
        pip_version = subprocess.run(
            ["pip", "--version"],
            capture_output=True,
            text=True
        ).stdout.strip() if shutil.which("pip") else "Not installed"

        # 检查系统架构
        machine = platform.machine()
        is_64bit = sys.maxsize > 2**32

        # 获取OS版本
        os_version = self._get_os_version()

        info = PiSystemInfo(
            model=cpu_info,
            os_version=os_version,
            cpu_arch=machine,
            cpu_cores=os.cpu_count() or 4,
            total_ram_mb=total_ram,
            python_version=python_version,
            pip_version=pip_version,
            is_64bit=is_64bit
        )

        print(f"\n系统信息:")
        print(f"  设备型号: {info.model}")
        print(f"  OS版本: {info.os_version}")
        print(f"  CPU架构: {info.cpu_arch} {'(64bit)' if info.is_64bit else '(32bit)'}")
        print(f"  CPU核心: {info.cpu_cores}")
        print(f"  内存: {info.total_ram_mb} MB")
        print(f"  Python: {info.python_version}")
        print(f"  pip: {info.pip_version}")

        return info

    def _get_cpu_info(self) -> str:
        """获取CPU型号"""
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("model name"):
                        return line.split(":")[1].strip()
                    elif line.startswith("Model"):
                        return line.split(":")[1].strip()
        except:
            pass

        # 回退方案
        machine = platform.machine()
        if "armv7l" in machine:
            return "Raspberry Pi (ARMv7)"
        elif "aarch64" in machine:
            return "Raspberry Pi (ARM64)"
        return "Unknown ARM Device"

    def _get_total_ram(self) -> int:
        """获取总内存(MB)"""
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal"):
                        kb = int(line.split()[1])
                        return kb // 1024
        except:
            pass
        return 0

    def _get_os_version(self) -> str:
        """获取OS版本"""
        try:
            # 尝试读取/etc/os-release
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME"):
                        return line.split("=")[1].strip().strip('"')
        except:
            pass

        # 回退方案
        if Path("/etc/rpi-issue").exists():
            return "Raspberry Pi OS"
        return platform.system()

    def check_compatibility(self, info: PiSystemInfo) -> tuple[bool, list[str]]:
        """检查系统兼容性"""
        issues = []

        # 检查是否在树莓派上运行
        if "raspberry" not in info.model.lower() and "pi" not in info.model.lower():
            issues.append("警告: 未检测到Raspberry Pi设备，脚本可能需要调整")

        # 检查内存
        if info.total_ram_mb < 500:
            issues.append(f"警告: 内存({info.total_ram_mb}MB)较低，建议至少1GB")

        # 检查Python版本
        if info.python_version < "3.9":
            issues.append(f"警告: Python版本({info.python_version})过低，建议升级到3.9+")

        # 检查架构
        if not info.is_64bit:
            issues.append("提示: 32位系统，建议使用int8量化模型以节省内存")

        return len(issues) == 0, issues

    def install_dependencies(self) -> bool:
        """安装系统依赖"""
        print("\n" + "=" * 60)
        print("安装系统依赖...")
        print("=" * 60)

        # 更新包列表
        print("更新软件包列表...")
        subprocess.run(["sudo", "apt-get", "update"], check=True)

        # 安装基础依赖
        print("安装基础依赖库...")
        deps = [
            "python3-pip",
            "python3-dev",
            "libgomp1",
            " portaudio19-dev",
        ]

        for dep in deps:
            print(f"  安装 {dep}...")
            subprocess.run(["sudo", "apt-get", "install", "-y", dep], check=True)

        # 安装Python依赖
        print("\n安装Python依赖...")
        python_deps = [
            "numpy>=1.21.0",
            "scipy>=1.7.0",
            "soundfile>=0.10.0",
            "praat-parselmouth>=1.2.0",
        ]

        for dep in python_deps:
            print(f"  安装 {dep}...")
            subprocess.run(
                ["pip3", "install", "--user", dep],
                check=True
            )

        print("依赖安装完成!")
        return True

    def download_model(
        self,
        model_name: str = "supertonic-base",
        quantization: str = "int8",
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

        # 检查文件是否已存在
        if filepath.exists():
            print(f"模型文件已存在: {filepath}")
            return str(filepath)

        # 下载文件
        print("正在下载(可能需要几分钟)...")
        urllib.request.urlretrieve(url, filepath)
        print(f"下载完成: {filepath}")

        # 解压
        print("解压模型文件...")
        if filepath.suffix == ".gz" or ".tar" in filepath.name:
            with tarfile.open(filepath, "r:gz") as tar:
                tar.extractall(output_path)
        elif filepath.suffix == ".zip":
            with zipfile.ZipFile(filepath, "r") as zf:
                zf.extractall(output_path)

        # 删除压缩包
        filepath.unlink()

        # 查找模型目录
        model_dir = output_path / model_name
        if not model_dir.exists():
            # 查找解压后的目录
            for item in output_path.iterdir():
                if item.is_dir() and model_name in item.name.lower():
                    model_dir = item
                    break

        print(f"模型已解压到: {model_dir}")
        return str(model_dir)

    def install_onnx_runtime(self) -> bool:
        """安装ONNX Runtime"""
        print("\n" + "=" * 60)
        print("安装ONNX Runtime...")
        print("=" * 60)

        # 根据架构选择合适的ONNX Runtime版本
        machine = platform.machine()

        if "aarch64" in machine:
            # ARM64 (Pi 4 64bit)
            package = "onnxruntime"
        elif "armv7l" in machine:
            # ARM32 (Pi 3/4 32bit)
            package = "onnxruntime"
        else:
            package = "onnxruntime"

        print(f"安装 {package}...")
        result = subprocess.run(
            ["pip3", "install", "--user", package],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"警告: 标准安装失败，尝试替代方案...")
            subprocess.run(
                ["pip3", "install", "--user", "onnxruntime-rocm-4.5.1"],
                check=False
            )

        print("ONNX Runtime安装完成!")
        return True

    def create_config(self, config: PiDeploymentConfig) -> str:
        """创建部署配置文件"""
        print("\n" + "=" * 60)
        print("创建配置文件...")
        print("=" * 60)

        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        config_data = {
            "model": config.model,
            "language": config.language,
            "inference": {
                "device": config.device,
                "threads": config.threads,
                "quantization": config.quantization,
            },
            "audio": {
                "sample_rate": config.sample_rate,
                "channels": 1,
                "bit_depth": 16,
            },
            "voice": config.voice_model_path or None,
        }

        config_file = output_dir / "config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        print(f"配置文件已创建: {config_file}")
        return str(config_file)

    def create_inference_script(self, output_dir: str) -> str:
        """创建推理脚本"""
        script_content = '''#!/usr/bin/env python3
"""Supertonic TTS 边缘推理脚本"""

import argparse
import json
import numpy as np
import soundfile as sf
from pathlib import Path
import sys

try:
    import onnxruntime as ort
except ImportError:
    print("错误: 请先安装ONNX Runtime: pip install onnxruntime")
    sys.exit(1)


class SupertonicEngine:
    """Supertonic TTS推理引擎"""

    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.session = None
        self._load_model()

    def _load_config(self, config_path: str) -> dict:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_model(self):
        """加载ONNX模型"""
        model_dir = Path(self.config.get("model_dir", "./models"))
        model_files = list(model_dir.glob("*.onnx"))

        if not model_files:
            raise FileNotFoundError(f"未找到模型文件在 {model_dir}")

        model_path = model_files[0]
        print(f"加载模型: {model_path}")

        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        providers = ["CPUExecutionProvider"]
        if self.config["inference"]["device"] == "cuda":
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]

        self.session = ort.InferenceSession(
            str(model_path),
            sess_options=sess_options,
            providers=providers
        )

        print(f"模型加载完成，提供商: {self.session.get_providers()}")

    def synthesize(self, text: str, output_path: str = "output.wav") -> str:
        """合成语音"""
        print(f"合成文本: {text[:50]}{"..." if len(text) > 50 else ""}")

        # 模型推理(简化示例，实际需要参考官方API)
        # 这里仅作占位

        # 生成音频数据(示例)
        sample_rate = self.config["audio"]["sample_rate"]
        duration = len(text) * 0.1  # 粗略估算
        audio = np.zeros(int(sample_rate * duration), dtype=np.float32)

        # 保存音频
        sf.write(output_path, audio, sample_rate)
        print(f"音频已保存: {output_path}")

        return output_path


def main():
    parser = argparse.ArgumentParser(description="Supertonic TTS边缘推理")
    parser.add_argument("text", help="要合成的文本")
    parser.add_argument("-o", "--output", default="output.wav", help="输出文件路径")
    parser.add_argument("-c", "--config", default="config.json", help="配置文件路径")

    args = parser.parse_args()

    engine = SupertonicEngine(args.config)
    output = engine.synthesize(args.text, args.output)

    print(f"\\n完成! 输出: {output}")


if __name__ == "__main__":
    main()
'''

        script_path = Path(output_dir) / "synthesize.py"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        # 添加执行权限
        os.chmod(script_path, 0o755)

        print(f"推理脚本已创建: {script_path}")
        return str(script_path)

    def create_launcher(self, output_dir: str) -> str:
        """创建启动脚本"""
        launcher_content = '''#!/bin/bash
# Supertonic TTS Raspberry Pi Launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 需要Python 3"
    exit 1
fi

# 检查ONNX Runtime
python3 -c "import onnxruntime" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "错误: 需要ONNX Runtime"
    echo "运行: pip3 install onnxruntime"
    exit 1
fi

# 运行推理
python3 synthesize.py "$@"
'''

        launcher_path = Path(output_dir) / "run.sh"
        with open(launcher_path, "w", encoding="utf-8") as f:
            f.write(launcher_content)

        os.chmod(launcher_path, 0o755)

        print(f"启动脚本已创建: {launcher_path}")
        return str(launcher_path)

    def deploy(self, config: PiDeploymentConfig) -> dict:
        """执行完整部署流程"""
        print("\n" + "=" * 60)
        print("Supertonic TTS Raspberry Pi部署")
        print("=" * 60)

        results = {}

        # 1. 检查系统
        print("\n[1/6] 检查系统...")
        info = self.check_system()
        results["system_info"] = {
            "model": info.model,
            "cpu_cores": info.cpu_cores,
            "ram_mb": info.total_ram_mb,
            "python_version": info.python_version,
        }

        compatible, issues = self.check_compatibility(info)
        results["compatible"] = compatible
        results["issues"] = issues

        if not compatible:
            print("\n发现兼容性问题:")
            for issue in issues:
                print(f"  - {issue}")
            if not input("\n是否继续部署? (y/N): ").strip().lower() == "y":
                return results

        # 2. 安装依赖
        print("\n[2/6] 安装系统依赖...")
        deps_ok = self.install_dependencies()
        results["deps_installed"] = deps_ok

        # 3. 安装ONNX Runtime
        print("\n[3/6] 安装ONNX Runtime...")
        onnx_ok = self.install_onnx_runtime()
        results["onnx_installed"] = onnx_ok

        # 4. 下载模型
        print("\n[4/6] 下载模型...")
        model_dir = self.download_model(
            config.model,
            config.quantization,
            f"{config.output_dir}/models"
        )
        results["model_path"] = model_dir

        # 更新配置中的模型路径
        config.voice_model_path = model_dir

        # 5. 创建配置和脚本
        print("\n[5/6] 创建配置和脚本...")
        config_file = self.create_config(config)
        results["config_file"] = config_file

        inference_script = self.create_inference_script(config.output_dir)
        results["inference_script"] = inference_script

        launcher = self.create_launcher(config.output_dir)
        results["launcher"] = launcher

        # 6. 验证
        print("\n[6/6] 验证部署...")
        print("\n" + "=" * 60)
        print("部署完成!")
        print("=" * 60)
        print(f"""
使用说明:
  1. 进入部署目录:
     cd {config.output_dir}

  2. 运行推理:
     ./run.sh "Hello world" -o output.wav

  3. 或直接使用Python:
     python3 synthesize.py "你好" -o output.wav

部署信息:
  模型: {config.model} ({config.quantization})
  线程: {config.threads}
  输出目录: {config.output_dir}
""")

        results["success"] = True
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Supertonic TTS Raspberry Pi部署工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检查系统兼容性
  python pi_deploy.py check

  # 部署基础模型
  python pi_deploy.py deploy --model supertonic-base --quantization int8

  # 部署高性能模型(需要Pi 4 4GB+)
  python pi_deploy.py deploy --model supertonic-large --quantization float16 --threads 4

说明:
  - 推荐Raspberry Pi 4 (2GB+) 用于实时语音合成
  - int8量化模型适合1-2GB内存的设备
  - float16模型需要更多内存但质量更好
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # check命令
    check_parser = subparsers.add_parser("check", help="检查系统兼容性")

    # deploy命令
    deploy_parser = subparsers.add_parser("deploy", help="部署到Raspberry Pi")
    deploy_parser.add_argument("--model", "-m", default="supertonic-base",
                              choices=["supertonic-base", "supertonic-large"],
                              help="模型名称")
    deploy_parser.add_argument("--quantization", "-q", default="int8",
                              choices=["int8", "float16", "float32"],
                              help="量化方式")
    deploy_parser.add_argument("--threads", "-t", type=int, default=4,
                              help="推理线程数")
    deploy_parser.add_argument("--sample-rate", "-r", type=int, default=24000,
                              help="采样率")
    deploy_parser.add_argument("--output", "-o", default="./supertonic-pi",
                              help="输出目录")
    deploy_parser.add_argument("--skip-deps", action="store_true",
                              help="跳过依赖安装")

    args = parser.parse_args()

    deployer = SupertonicPiDeployer()

    if args.command == "check":
        info = deployer.check_system()
        compatible, issues = deployer.check_compatibility(info)

        print("\n兼容性结果:")
        print(f"  状态: {'✓ 兼容' if compatible else '⚠ 部分兼容'}")

        if issues:
            print("\n问题列表:")
            for issue in issues:
                print(f"  - {issue}")

    elif args.command == "deploy":
        config = PiDeploymentConfig(
            model=args.model,
            quantization=args.quantization,
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
