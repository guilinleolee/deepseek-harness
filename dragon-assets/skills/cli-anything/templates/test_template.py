"""
CLI-Anything Test Template
测试模板 - 单元测试 + E2E测试 + CLI subprocess测试
"""

import pytest
import subprocess
import os
import json
import shutil

# ============================================================
# Helper Functions
# ============================================================

def _resolve_cli(name):
    """解析已安装的CLI命令；开发环境回退到python -m

    设置环境变量 CLI_ANYTHING_FORCE_INSTALLED=1 强制使用已安装命令
    """
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = name.replace("cli-anything-", "cli_anything.") + "." + name.split("-")[-1] + "_cli"
    print(f"[_resolve_cli] Falling back to: python -m {module}")
    return ["python", "-m", module]


def _verify_magic_bytes(path, expected):
    """验证文件Magic Bytes"""
    with open(path, "rb") as f:
        magic = f.read(len(expected))
    return magic == expected


def _verify_zip_structure(path):
    """验证ZIP/OOXML结构（DOCX, XLSX, PPTX等）"""
    import zipfile
    if not zipfile.is_zipfile(path):
        return False
    with zipfile.ZipFile(path, 'r') as z:
        return '[Content_Types].xml' in z.namelist()


# ============================================================
# Unit Tests (test_core.py)
# ============================================================

class TestProjectOperations:
    """项目操作单元测试"""

    def test_project_new_default(self, tmp_path):
        """测试创建默认项目"""
        # TODO: 实现测试
        pass

    def test_project_new_with_params(self, tmp_path):
        """测试带参数创建项目"""
        # TODO: 实现测试
        pass

    def test_project_open(self, tmp_path):
        """测试打开项目"""
        # TODO: 实现测试
        pass

    def test_project_save(self, tmp_path):
        """测试保存项目"""
        # TODO: 实现测试
        pass


class TestCoreOperations:
    """核心操作单元测试"""

    def test_add_operation(self):
        """测试添加操作"""
        # TODO: 实现测试
        pass

    def test_remove_operation(self):
        """测试删除操作"""
        # TODO: 实现测试
        pass

    def test_modify_operation(self):
        """测试修改操作"""
        # TODO: 实现测试
        pass


class TestSessionManagement:
    """会话管理单元测试"""

    def test_undo(self):
        """测试撤销"""
        # TODO: 实现测试
        pass

    def test_redo(self):
        """测试重做"""
        # TODO: 实现测试
        pass

    def test_history(self):
        """测试历史记录"""
        # TODO: 实现测试
        pass


# ============================================================
# E2E Tests (test_full_e2e.py)
# ============================================================

class TestE2EIntermediateFiles:
    """E2E测试 - 中间文件验证"""

    def test_project_file_structure(self, tmp_path):
        """测试项目文件结构正确性"""
        # TODO: 验证生成的项目文件结构
        pass

    def test_xml_validity(self, tmp_path):
        """测试XML有效性"""
        # TODO: 验证生成的XML文件
        pass


class TestE2ERealBackend:
    """E2E测试 - 真实软件后端"""

    def test_export_pdf(self, tmp_path):
        """测试导出PDF - 调用真实软件"""
        # 1. 创建项目
        # 2. 调用真实软件后端导出
        # 3. 验证输出文件存在且格式正确
        output_path = os.path.join(tmp_path, "output.pdf")
        # TODO: 实现导出

        # 验证输出
        assert os.path.exists(output_path), "输出文件不存在"
        assert os.path.getsize(output_path) > 0, "输出文件为空"
        assert _verify_magic_bytes(output_path, b"%PDF"), "不是有效的PDF文件"

        print(f"\n  PDF: {output_path} ({os.path.getsize(output_path):,} bytes)")

    def test_export_docx(self, tmp_path):
        """测试导出DOCX - 调用真实软件"""
        output_path = os.path.join(tmp_path, "output.docx")
        # TODO: 实现导出

        # 验证输出
        assert os.path.exists(output_path), "输出文件不存在"
        assert _verify_zip_structure(output_path), "不是有效的DOCX文件"

        print(f"\n  DOCX: {output_path} ({os.path.getsize(output_path):,} bytes)")


class TestE2EWorkflows:
    """E2E测试 - 真实工作流场景"""

    def test_complete_workflow(self, tmp_path):
        """测试完整工作流：创建→编辑→导出"""
        # 工作流步骤：
        # 1. 创建新项目
        # 2. 添加内容
        # 3. 导出为最终格式
        # 4. 验证输出

        # TODO: 实现工作流
        pass


# ============================================================
# CLI Subprocess Tests
# ============================================================

class TestCLISubprocess:
    """CLI subprocess测试 - 作为真实用户/Agent使用"""

    CLI_BASE = _resolve_cli("cli-anything-<SOFTWARE>")

    def _run(self, args, check=True):
        """运行CLI命令"""
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
        )

    def test_help(self):
        """测试--help命令"""
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "Usage:" in result.stdout or "usage:" in result.stdout

    def test_version(self):
        """测试--version命令"""
        result = self._run(["--version"])
        assert result.returncode == 0

    def test_json_output(self, tmp_path):
        """测试JSON输出"""
        output_file = os.path.join(tmp_path, "test.json")
        result = self._run(["--json", "project", "new", "-o", output_file])
        assert result.returncode == 0

        # 验证JSON有效性
        data = json.loads(result.stdout)
        assert "project" in data or "status" in data

    def test_project_new(self, tmp_path):
        """测试创建项目"""
        output_file = os.path.join(tmp_path, "project.ext")
        result = self._run(["project", "new", "-o", output_file])
        assert result.returncode == 0
        assert os.path.exists(output_file)


# ============================================================
# Run Tests
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])