# CLI-Anything 测试计划

## 测试策略

### 1. 测试金字塔

```
        /\
       /  \        E2E测试 (10%)
      /    \       - 真实软件后端验证
     /------\      - Magic Bytes验证
    /        \
   /  集成测试 \    (30%)
  /            \   - CLI命令组合
 /              \  - 工作流测试
/----------------\
   单元测试 (60%)
- CLI结构验证
- JSON输出验证
- 后端封装验证
- REPL接口验证
```

### 2. 测试覆盖目标

| 测试类型 | 覆盖率目标 | 当前状态 |
|---------|-----------|---------|
| 单元测试 | > 80% | 待验证 |
| 集成测试 | > 60% | 待验证 |
| E2E测试 | 关键路径100% | 待验证 |

## 测试分类

### Phase 1: 单元测试 (test_core.py)

#### CLI结构测试
- [ ] `test_cli_help` - 验证帮助信息
- [ ] `test_version_option` - 验证版本选项
- [ ] `test_json_flag_exists` - 验证JSON标志

#### JSON输出测试
- [ ] `test_json_output_format` - 验证JSON格式
- [ ] `test_json_error_format` - 验证错误格式

#### 后端封装测试
- [ ] `test_find_executable_pattern` - 验证可执行文件查找
- [ ] `test_backend_not_found_error` - 验证未找到错误
- [ ] `test_run_command_timeout` - 验证超时处理

#### 项目管理测试
- [ ] `test_project_new` - 验证项目创建
- [ ] `test_project_open` - 验证项目打开

#### REPL接口测试
- [ ] `test_repl_banner` - 验证REPL横幅

#### 命令模式测试
- [ ] `test_undo_redo_pattern` - 验证撤销/重做
- [ ] `test_layer_management` - 验证图层管理

### Phase 2: E2E测试 (test_full_e2e.py)

#### LibreOffice测试
- [ ] `test_convert_odt_to_pdf` - ODT转PDF + PDF Magic验证

#### FFmpeg测试
- [ ] `test_convert_audio_format` - 音频格式转换 + WAV Magic验证
- [ ] `test_get_media_info` - 媒体信息获取

#### Blender测试
- [ ] `test_run_python_script` - Python脚本执行

#### 集成工作流测试
- [ ] `test_document_to_video_workflow` - 文档转视频工作流

#### 错误处理测试
- [ ] `test_missing_software_error` - 软件未安装错误
- [ ] `test_invalid_input_file` - 无效输入文件
- [ ] `test_permission_denied` - 权限拒绝

### Phase 3: CLI Subprocess测试

```python
# test_cli_subprocess.py
import subprocess
import shutil

def _resolve_cli(name: str) -> list:
    """解析CLI命令"""
    path = shutil.which(name)
    if path:
        return [path]
    return ['python', '-m', name.replace('-', '.')]

class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything")

    def test_help(self):
        result = subprocess.run(
            self.CLI_BASE + ['--help'],
            capture_output=True
        )
        assert result.returncode == 0

    def test_json_output(self):
        result = subprocess.run(
            self.CLI_BASE + ['--json', 'project', 'new'],
            capture_output=True, text=True
        )
        import json
        data = json.loads(result.stdout)
        assert 'status' in data
```

## 运行测试

### 运行所有测试
```bash
pytest skills/cli-anything/tests/ -v
```

### 运行单元测试
```bash
pytest skills/cli-anything/tests/test_core.py -v
```

### 运行E2E测试（需要软件已安装）
```bash
pytest skills/cli-anything/tests/test_full_e2e.py -v
```

### 跳过需要真实软件的测试
```bash
pytest skills/cli-anything/tests/ -v -m "not skipif"
```

### 生成覆盖率报告
```bash
pytest skills/cli-anything/tests/ --cov=skills.cli_anything --cov-report=html
```

## Magic Bytes验证

### 常见文件格式Magic Bytes

| 格式 | Magic Bytes | 验证方法 |
|------|------------|---------|
| PDF | `%PDF` | `f.read(4) == b'%PDF'` |
| PNG | `\x89PNG` | `f.read(4) == b'\x89PNG'` |
| JPEG | `\xFF\xD8\xFF` | `f.read(3) == b'\xFF\xD8\xFF'` |
| ZIP | `PK\x03\x04` | `f.read(4) == b'PK\x03\x04'` |
| WAV | `RIFF` | `f.read(4) == b'RIFF'` |
| MP4 | `ftyp` (offset 4) | `f.read(8)[4:8] == b'ftyp'` |

## 测试环境配置

### 必需软件
- Python 3.8+
- pytest
- pytest-cov (可选)

### 可选软件（E2E测试）
- LibreOffice
- FFmpeg
- Blender

### 安装测试依赖
```bash
pip install pytest pytest-cov
```

## 持续集成

### GitHub Actions配置示例
```yaml
name: CLI-Anything Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov
          pip install -e .
      - name: Run unit tests
        run: pytest skills/cli-anything/tests/test_core.py -v
      - name: Install LibreOffice
        run: sudo apt-get install -y libreoffice
      - name: Run E2E tests
        run: pytest skills/cli-anything/tests/test_full_e2e.py -v
```

## 测试最佳实践

1. **隔离测试**：每个测试独立运行，不依赖其他测试的状态
2. **Mock外部依赖**：对未安装的软件使用skipif跳过
3. **清理资源**：使用tmp_path fixture自动清理临时文件
4. **验证输出**：不仅验证返回码，还验证输出格式和内容
5. **Magic Bytes验证**：对生成的文件验证二进制头部

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| V1.0 | 2026-03-14 | 初始测试计划 |