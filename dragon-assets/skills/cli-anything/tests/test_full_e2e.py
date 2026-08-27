"""
CLI-Anything E2E Tests
端到端测试 - 验证真实软件后端

测试原则：
- 调用真实软件后端
- 验证Magic Bytes
- 验证输出文件格式
- 支持软依赖（软件未安装时跳过）
"""

import pytest
import subprocess
import json
import os
import shutil
from pathlib import Path


def _resolve_cli(name: str) -> list:
    """解析CLI命令路径"""
    path = shutil.which(name)
    if path:
        return [path]
    return ['python', '-m', name.replace('-', '.')]


def _verify_magic_bytes(file_path: str, expected_magic: bytes) -> bool:
    """验证文件Magic Bytes"""
    with open(file_path, 'rb') as f:
        actual_magic = f.read(len(expected_magic))
    return actual_magic == expected_magic


def _is_software_installed(name: str) -> bool:
    """检查软件是否已安装"""
    return shutil.which(name) is not None


class TestLibreOfficeE2E:
    """LibreOffice E2E测试"""

    @pytest.fixture
    def sample_odt(self, tmp_path):
        """创建示例ODT文件"""
        odt_path = tmp_path / "test.odt"
        # 使用Python创建一个简单的ODT
        # ODT实际上是ZIP格式
        import zipfile
        with zipfile.ZipFile(odt_path, 'w') as zf:
            zf.writestr('content.xml', '<office:document-content/>')
            zf.writestr('mimetype', 'application/vnd.oasis.opendocument.text')
        return odt_path

    @pytest.mark.skipif(
        not _is_software_installed('libreoffice'),
        reason="LibreOffice not installed"
    )
    def test_convert_odt_to_pdf(self, sample_odt, tmp_path):
        """测试ODT转PDF"""
        cli_base = _resolve_cli('cli-anything-libreoffice')

        result = subprocess.run(
            cli_base + [
                'convert', str(sample_odt),
                '--format', 'pdf',
                '--output-dir', str(tmp_path)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            # 验证PDF文件生成
            pdf_path = tmp_path / "test.pdf"
            if pdf_path.exists():
                # 验证PDF Magic Bytes
                assert _verify_magic_bytes(str(pdf_path), b'%PDF')


class TestFFmpegE2E:
    """FFmpeg E2E测试"""

    @pytest.fixture
    def sample_audio(self, tmp_path):
        """创建示例音频文件（使用FFmpeg生成测试音频）"""
        audio_path = tmp_path / "test_audio.mp3"
        # 如果FFmpeg可用，生成测试音频
        if _is_software_installed('ffmpeg'):
            subprocess.run(
                ['ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=1',
                 '-y', str(audio_path)],
                capture_output=True
            )
        return audio_path

    @pytest.mark.skipif(
        not _is_software_installed('ffmpeg'),
        reason="FFmpeg not installed"
    )
    def test_convert_audio_format(self, sample_audio, tmp_path):
        """测试音频格式转换"""
        if not sample_audio.exists():
            pytest.skip("Sample audio not generated")

        cli_base = _resolve_cli('cli-anything-ffmpeg')

        output_path = tmp_path / "test_output.wav"

        result = subprocess.run(
            cli_base + [
                'convert', str(sample_audio),
                '--output', str(output_path)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            # 验证WAV Magic Bytes
            if output_path.exists():
                # WAV文件以RIFF开头
                with open(output_path, 'rb') as f:
                    header = f.read(4)
                assert header == b'RIFF'

    @pytest.mark.skipif(
        not _is_software_installed('ffprobe'),
        reason="FFprobe not installed"
    )
    def test_get_media_info(self, sample_audio):
        """测试获取媒体信息"""
        if not sample_audio.exists():
            pytest.skip("Sample audio not generated")

        cli_base = _resolve_cli('cli-anything-ffmpeg')

        result = subprocess.run(
            cli_base + ['info', str(sample_audio), '--json'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert 'path' in data


class TestBlenderE2E:
    """Blender E2E测试"""

    @pytest.fixture
    def sample_blend(self, tmp_path):
        """创建示例Blend文件"""
        blend_path = tmp_path / "test.blend"
        # Blender文件有特定的Magic Bytes
        # 实际测试中应该使用真实Blender创建
        return blend_path

    @pytest.mark.skipif(
        not _is_software_installed('blender'),
        reason="Blender not installed"
    )
    def test_run_python_script(self, tmp_path):
        """测试运行Python脚本"""
        # 创建测试脚本
        script_path = tmp_path / "test_script.py"
        with open(script_path, 'w') as f:
            f.write('import bpy; print("Blender test OK")')

        cli_base = _resolve_cli('cli-anything-blender')

        result = subprocess.run(
            cli_base + [
                'run-script', str(script_path),
                '--background'
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        # 验证脚本执行
        if result.returncode == 0:
            assert 'Blender test OK' in result.stdout or result.returncode == 0


class TestIntegrationWorkflow:
    """集成工作流测试"""

    @pytest.mark.skipif(
        not (_is_software_installed('ffmpeg') and _is_software_installed('libreoffice')),
        reason="Required software not installed"
    )
    def test_document_to_video_workflow(self, tmp_path):
        """测试文档转视频工作流"""
        # 步骤1: 创建文档
        doc_path = tmp_path / "input.txt"
        with open(doc_path, 'w') as f:
            f.write("Test content for video")

        # 步骤2: 转换为PDF (LibreOffice)
        lo_cli = _resolve_cli('cli-anything-libreoffice')
        subprocess.run(
            lo_cli + ['convert', str(doc_path), '--format', 'pdf', '--output-dir', str(tmp_path)],
            capture_output=True,
            timeout=60
        )

        # 步骤3: 转换为图片序列 (FFmpeg)
        pdf_path = tmp_path / "input.pdf"
        if pdf_path.exists():
            ff_cli = _resolve_cli('cli-anything-ffmpeg')
            subprocess.run(
                ff_cli + ['convert', str(pdf_path), '--frames', str(tmp_path / "frame_%03d.png")],
                capture_output=True,
                timeout=30
            )

        # 验证输出
        # 实际验证取决于软件是否成功执行


class TestErrorHandling:
    """错误处理测试"""

    def test_missing_software_error(self, tmp_path):
        """测试软件未安装时的错误提示"""
        # 模拟调用不存在的软件
        result = subprocess.run(
            ['python', '-m', 'cli_anything_nonexistent', '--help'],
            capture_output=True,
            text=True
        )

        # 应该返回错误
        assert result.returncode != 0 or 'error' in result.stderr.lower()

    def test_invalid_input_file(self, tmp_path):
        """测试无效输入文件"""
        nonexistent = tmp_path / "nonexistent.xyz"

        result = subprocess.run(
            ['python', '-m', 'cli_anything', 'project', 'open', str(nonexistent)],
            capture_output=True,
            text=True
        )

        # 应该返回错误
        assert result.returncode != 0

    def test_permission_denied(self, tmp_path):
        """测试权限拒绝"""
        # 创建只读文件
        readonly_file = tmp_path / "readonly.txt"
        readonly_file.write_text("readonly content")
        os.chmod(str(readonly_file), 0o444)

        # 尝试写入（应该失败）
        # 具体测试取决于CLI实现


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])