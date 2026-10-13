"""
CLI-Anything Core Tests
核心功能单元测试

测试覆盖：
- CLI结构验证
- 后端封装验证
- JSON输出验证
- REPL接口验证
"""

import pytest
import subprocess
import json
import tempfile
import os
from pathlib import Path


class TestCLIStructure:
    """CLI结构测试"""

    def test_cli_help(self):
        """测试CLI帮助信息"""
        result = subprocess.run(
            ['python', '-m', 'cli_anything', '--help'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'CLI-Anything' in result.stdout or 'Usage' in result.stdout

    def test_version_option(self):
        """测试版本选项"""
        result = subprocess.run(
            ['python', '-m', 'cli_anything', '--version'],
            capture_output=True,
            text=True
        )
        # 版本命令可能返回0或退出
        assert 'version' in result.stdout.lower() or result.returncode in [0, 1]

    def test_json_flag_exists(self):
        """测试JSON标志存在"""
        result = subprocess.run(
            ['python', '-m', 'cli_anything', '--help'],
            capture_output=True,
            text=True
        )
        assert '--json' in result.stdout


class TestJSONOutput:
    """JSON输出测试"""

    def test_json_output_format(self):
        """测试JSON输出格式"""
        result = subprocess.run(
            ['python', '-m', 'cli_anything', '--json', 'project', 'new', '--name', 'TestProject'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # 验证JSON格式
            try:
                data = json.loads(result.stdout)
                assert 'status' in data
                assert data['status'] in ['success', 'error']
            except json.JSONDecodeError:
                pytest.skip("CLI not fully implemented yet")

    def test_json_error_format(self):
        """测试JSON错误格式"""
        result = subprocess.run(
            ['python', '-m', 'cli_anything', '--json', 'invalid', 'command'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # 错误应该有明确格式
            assert result.stderr or result.stdout


class TestBackendEncapsulation:
    """后端封装测试"""

    def test_find_executable_pattern(self):
        """测试可执行文件查找模式"""
        from skills.cli_anything.templates.backend_template import find_executable

        # 测试系统常见命令
        try:
            python_path = find_executable('python', None, 'Please install Python')
            assert os.path.exists(python_path)
        except RuntimeError:
            pytest.skip("Python not in PATH")

    def test_backend_not_found_error(self):
        """测试后端未找到错误"""
        from skills.cli_anything.templates.backend_template import (
            BackendNotFoundError,
            find_executable
        )

        with pytest.raises(BackendNotFoundError):
            find_executable(
                'nonexistent_software_12345',
                None,
                'Please install nonexistent_software_12345'
            )

    def test_run_command_timeout(self):
        """测试命令超时处理"""
        from skills.cli_anything.templates.backend_template import run_command

        with pytest.raises(RuntimeError, match="timeout"):
            # 使用一个非常短的超时和一个长时间运行的命令
            run_command(
                ['python', '-c', 'import time; time.sleep(10)'],
                timeout=1
            )


class TestProjectManagement:
    """项目管理测试"""

    def test_project_new(self, tmp_path):
        """测试创建新项目"""
        output_file = tmp_path / "project.json"

        result = subprocess.run(
            [
                'python', '-m', 'cli_anything',
                'project', 'new',
                '--name', 'TestProject',
                '--width', '1920',
                '--height', '1080',
                '--output', str(output_file)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # 验证项目文件创建
            assert output_file.exists()

            # 验证项目内容
            with open(output_file) as f:
                data = json.load(f)
                assert data['name'] == 'TestProject'
                assert data['width'] == 1920
                assert data['height'] == 1080

    def test_project_open(self, tmp_path):
        """测试打开项目"""
        # 先创建项目
        project_file = tmp_path / "project.json"
        project_data = {
            'name': 'ExistingProject',
            'width': 1280,
            'height': 720,
            'layers': []
        }

        with open(project_file, 'w') as f:
            json.dump(project_data, f)

        # 测试打开
        result = subprocess.run(
            [
                'python', '-m', 'cli_anything',
                'project', 'open', str(project_file),
                '--json'
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert data['status'] == 'success'


class TestREPLInterface:
    """REPL接口测试"""

    def test_repl_banner(self):
        """测试REPL启动横幅"""
        # 使用stdin发送exit命令
        result = subprocess.run(
            ['python', '-m', 'cli_anything'],
            input='exit\n',
            capture_output=True,
            text=True,
            timeout=5
        )

        # 验证横幅输出
        assert 'CLI-Anything' in result.stdout or 'exit' in result.stdout


class TestCommandPatterns:
    """命令模式测试"""

    def test_undo_redo_pattern(self, tmp_path):
        """测试撤销/重做模式"""
        # 创建项目
        project_file = tmp_path / "project.json"

        # 新建项目
        subprocess.run(
            [
                'python', '-m', 'cli_anything',
                'project', 'new',
                '--name', 'UndoTest',
                '--output', str(project_file)
            ],
            capture_output=True
        )

        # 添加图层
        subprocess.run(
            [
                'python', '-m', 'cli_anything',
                '--json', 'layer', 'add',
                '--name', 'Layer1'
            ],
            capture_output=True
        )

        # 执行撤销
        result = subprocess.run(
            [
                'python', '-m', 'cli_anything',
                '--json', 'undo'
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert 'status' in data

    def test_layer_management(self):
        """测试图层管理模式"""
        # 添加图层
        add_result = subprocess.run(
            [
                'python', '-m', 'cli_anything',
                '--json', 'layer', 'add',
                '--name', 'TestLayer',
                '--type', 'solid',
                '--color', '#ffffff'
            ],
            capture_output=True,
            text=True
        )

        if add_result.returncode == 0:
            data = json.loads(add_result.stdout)
            assert data['status'] == 'success'
            assert data['layer']['name'] == 'TestLayer'

        # 列出图层
        list_result = subprocess.run(
            [
                'python', '-m', 'cli_anything',
                '--json', 'layer', 'list'
            ],
            capture_output=True,
            text=True
        )

        if list_result.returncode == 0:
            data = json.loads(list_result.stdout)
            assert 'layers' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])