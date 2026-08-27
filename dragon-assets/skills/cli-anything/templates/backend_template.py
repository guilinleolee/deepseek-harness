"""
CLI-Anything Backend Template
后端封装模板 - 调用真实软件后端

关键原则：使用真实软件后端，而非重实现
"""

import subprocess
import shutil
import os
import sys
from typing import Optional, Dict, Any, List


class BackendNotFoundError(RuntimeError):
    """软件后端未找到错误"""

    def __init__(self, software_name: str, install_instructions: str):
        self.software_name = software_name
        self.install_instructions = install_instructions
        super().__init__(
            f"{software_name} not found in PATH.\n"
            f"Please install it:\n{install_instructions}"
        )


def find_executable(
    name: str,
    alternatives: Optional[List[str]] = None,
    install_instructions: str = "apt install <software>"
) -> str:
    """查找软件可执行文件

    Args:
        name: 主可执行文件名
        alternatives: 备选可执行文件名列表
        install_instructions: 安装指引

    Returns:
        可执行文件路径

    Raises:
        BackendNotFoundError: 软件未找到
    """
    # 检查主可执行文件
    path = shutil.which(name)
    if path:
        return path

    # 检查备选可执行文件
    if alternatives:
        for alt in alternatives:
            path = shutil.which(alt)
            if path:
                return path

    raise BackendNotFoundError(name, install_instructions)


def run_command(
    cmd: List[str],
    check: bool = True,
    capture_output: bool = True,
    timeout: int = 300,
    **kwargs
) -> subprocess.CompletedProcess:
    """运行命令并处理错误

    Args:
        cmd: 命令列表
        check: 是否检查返回码
        capture_output: 是否捕获输出
        timeout: 超时时间（秒）
        **kwargs: subprocess.run 额外参数

    Returns:
        CompletedProcess 对象
    """
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            **kwargs
        )
        return result
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Command timed out after {timeout}s: {' '.join(cmd)}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Command failed with code {e.returncode}:\n"
            f"Command: {' '.join(cmd)}\n"
            f"Stderr: {e.stderr}"
        )


# ============================================================
# 软件后端封装示例
# ============================================================

class LibreOfficeBackend:
    """LibreOffice 后端封装"""

    EXECUTABLE = "libreoffice"
    ALTERNATIVES = ["soffice", "libreoffice7.x"]
    INSTALL_INSTRUCTIONS = """
# Ubuntu/Debian
sudo apt install libreoffice

# macOS
brew install --cask libreoffice

# Windows
winget install TheDocumentFoundation.LibreOffice
"""

    @classmethod
    def find(cls) -> str:
        """查找LibreOffice可执行文件"""
        return find_executable(
            cls.EXECUTABLE,
            cls.ALTERNATIVES,
            cls.INSTALL_INSTRUCTIONS
        )

    @classmethod
    def convert(
        cls,
        input_path: str,
        output_format: str,
        output_path: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """转换文档格式

        Args:
            input_path: 输入文件路径
            output_format: 输出格式 (pdf, docx, xlsx, pptx等)
            output_path: 输出文件路径（可选）
            output_dir: 输出目录（可选）

        Returns:
            转换结果字典
        """
        exe = cls.find()
        cmd = [exe, "--headless", "--convert-to", output_format, input_path]

        if output_dir:
            cmd.extend(["--outdir", output_dir])

        run_command(cmd)

        # 确定输出路径
        if not output_path:
            base = os.path.splitext(input_path)[0]
            output_path = f"{base}.{output_format}"

        return {
            "output": output_path,
            "format": output_format,
            "method": "libreoffice-headless"
        }


class BlenderBackend:
    """Blender 后端封装"""

    EXECUTABLE = "blender"
    INSTALL_INSTRUCTIONS = """
# Ubuntu/Debian
sudo snap install blender --classic

# macOS
brew install --cask blender

# Windows
winget install BlenderFoundation.Blender
"""

    @classmethod
    def find(cls) -> str:
        return find_executable(cls.EXECUTABLE, None, cls.INSTALL_INSTRUCTIONS)

    @classmethod
    def run_script(
        cls,
        script_path: str,
        blend_path: Optional[str] = None,
        background: bool = True
    ) -> Dict[str, Any]:
        """运行Blender Python脚本

        Args:
            script_path: Python脚本路径
            blend_path: .blend文件路径（可选）
            background: 是否后台运行

        Returns:
            执行结果字典
        """
        exe = cls.find()
        cmd = [exe]

        if background:
            cmd.append("--background")

        if blend_path:
            cmd.append(blend_path)

        cmd.extend(["--python", script_path])

        result = run_command(cmd)

        return {
            "success": True,
            "output": result.stdout,
            "method": "blender-python"
        }

    @classmethod
    def render(
        cls,
        blend_path: str,
        output_path: str,
        frame: Optional[int] = None,
        animation: bool = False
    ) -> Dict[str, Any]:
        """渲染场景

        Args:
            blend_path: .blend文件路径
            output_path: 输出路径
            frame: 渲染帧号（可选）
            animation: 是否渲染动画

        Returns:
            渲染结果字典
        """
        exe = cls.find()
        cmd = [exe, "--background", blend_path, "--render-output", output_path]

        if frame is not None:
            cmd.extend(["--render-frame", str(frame)])
        elif animation:
            cmd.append("--render-anim")

        run_command(cmd, timeout=600)  # 渲染可能耗时较长

        return {
            "output": output_path,
            "method": "blender-render"
        }


class FFmpegBackend:
    """FFmpeg 后端封装（用于视频/音频处理）"""

    EXECUTABLE = "ffmpeg"
    INSTALL_INSTRUCTIONS = """
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
winget install Gyan.FFmpeg
"""

    @classmethod
    def find(cls) -> str:
        return find_executable(cls.EXECUTABLE, None, cls.INSTALL_INSTRUCTIONS)

    @classmethod
    def convert(
        cls,
        input_path: str,
        output_path: str,
        codec: Optional[str] = None,
        crf: int = 23,
        **options
    ) -> Dict[str, Any]:
        """转换媒体格式

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            codec: 视频编解码器（可选）
            crf: 恒定质量因子（0-51，越小质量越高）
            **options: 额外FFmpeg选项

        Returns:
            转换结果字典
        """
        exe = cls.find()
        cmd = [exe, "-i", input_path]

        if codec:
            cmd.extend(["-c:v", codec])

        cmd.extend(["-crf", str(crf)])
        cmd.append(output_path)

        run_command(cmd, timeout=600)

        return {
            "output": output_path,
            "method": "ffmpeg"
        }

    @classmethod
    def get_info(cls, path: str) -> Dict[str, Any]:
        """获取媒体信息

        Args:
            path: 媒体文件路径

        Returns:
            媒体信息字典
        """
        exe = cls.find()
        cmd = [exe, "-i", path, "-hide_banner"]

        # ffprobe 需要单独处理
        probe = shutil.which("ffprobe")
        if probe:
            cmd = [probe, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path]
            result = run_command(cmd)
            import json
            return json.loads(result.stdout)

        return {"path": path, "method": "ffmpeg-info"}


# ============================================================
# 后端工厂
# ============================================================

BACKENDS = {
    "libreoffice": LibreOfficeBackend,
    "blender": BlenderBackend,
    "ffmpeg": FFmpegBackend,
    # 添加更多后端...
}


def get_backend(name: str):
    """获取后端类

    Args:
        name: 后端名称

    Returns:
        后端类

    Raises:
        ValueError: 后端不存在
    """
    if name not in BACKENDS:
        raise ValueError(
            f"Unknown backend: {name}. "
            f"Available: {list(BACKENDS.keys())}"
        )
    return BACKENDS[name]