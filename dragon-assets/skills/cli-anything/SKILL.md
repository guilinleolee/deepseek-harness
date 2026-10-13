---
license: UNKNOWN
github_repo: HKUDS/CLI-Anything
github_hash: 47540664f834027f336ebe0d56b28d3ca1c6711b
last_updated: 2026-04-25
source_type: derived
triggers: ["cli anything", "CLI-Anything: Making ALL Software Agent-Native"]
---
# CLI-Anything: Making ALL Software Agent-Native

> 来源: [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) - 11,801 ⭐
> 一键将任意软件转为Agent可控CLI

## 核心价值

| 维度 | 说明 |
|------|------|
| **Universal Access** | 每个软件瞬间变为Agent可控 |
| **Seamless Integration** | 无需API、GUI、重构或复杂封装 |
| **Future-Ready** | 人类设计的软件一键转为Agent-Native工具 |

## 7阶段流水线

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: 🔍 代码分析     - 识别后端引擎，映射GUI→API        │
│ Phase 2: 📐 架构设计     - 命令分组，状态模型，输出格式      │
│ Phase 3: 🔨 实现构建     - Click CLI + REPL + JSON输出     │
│ Phase 4: 📋 测试规划     - TEST.md测试计划文档              │
│ Phase 5: 🧪 测试实现     - 单元测试 + E2E测试 + 真实软件    │
│ Phase 6: 📝 文档记录     - 测试结果 + 覆盖率                │
│ Phase 7: 📦 发布部署     - setup.py + PATH安装             │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 安装

```bash
# 添加CLI-Anything插件市场
/plugin marketplace add HKUDS/CLI-Anything

# 安装插件
/plugin install cli-anything
```

### 使用

```bash
# 生成任意软件的CLI（完整7阶段）
/cli-anything:cli-anything ./your-software

# 从GitHub仓库生成
/cli-anything:cli-anything https://github.com/user/repo

# 增量优化 - 全面分析
/cli-anything:refine ./software

# 增量优化 - 定向优化
/cli-anything:refine ./software "批量处理和过滤器"

# 验证CLI质量
/cli-anything:validate ./software

# 列出已生成的CLI
/cli-anything:list
```

## 生成的CLI使用

```bash
# 安装到PATH
cd software/agent-harness && pip install -e .

# 使用命令
cli-anything-software --help
cli-anything-software --json project new --width 1920 --height 1080

# 进入交互REPL
cli-anything-software
```

## 核心组件

### 1. HARNESS.md - 7阶段方法论

完整方法论文档，指导Agent如何系统化地将GUI软件转为CLI。

**关键原则**:
- 使用真实软件后端，而非重实现
- JSON + Human 双模式输出
- 状态持久化 + Undo/Redo
- 生产级测试（单元+E2E+真实软件）

### 2. ReplSkin - 统一REPL接口

提供一致的交互式REPL体验：

```python
from cli_anything.software.utils.repl_skin import ReplSkin

skin = ReplSkin("software", version="1.0.0")
skin.print_banner()          # 品牌启动框
skin.success("Saved")        # ✓ 绿色消息
skin.error("Not found")      # ✗ 红色消息
skin.warning("Unsaved")      # ⚠ 黄色消息
skin.table(headers, rows)    # 格式化表格
skin.progress(3, 10, "...")  # 进度条
```

### 3. 后端封装模式

```python
# utils/software_backend.py
def find_software():
    """查找软件可执行文件，提供安装指引"""
    import shutil
    path = shutil.which("software")
    if not path:
        raise RuntimeError("请安装software: apt install software")
    return path

def export_to_format(input_path, output_format, output_path):
    """调用真实软件后端"""
    exe = find_software()
    subprocess.run([exe, "--headless", "--convert-to", output_format, input_path])
    return {"output": output_path, "method": "real-software"}
```

### 4. 测试模式

```python
# 测试必须使用真实软件后端
def test_export_pdf():
    """E2E测试 - 调用真实LibreOffice"""
    cli = _resolve_cli("cli-anything-libreoffice")
    result = subprocess.run(cli + ["export", "doc.odt", "--format", "pdf"])
    assert result.returncode == 0
    assert os.path.exists("doc.pdf")
    # 验证Magic Bytes
    with open("doc.pdf", "rb") as f:
        assert f.read(4) == b"%PDF"
```

## 适用场景

| 类别 | 示例软件 |
|------|---------|
| **GitHub仓库** | VSCodium, WordPress, Calibre, Zotero |
| **AI/ML平台** | Stable Diffusion WebUI, ComfyUI, Open WebUI |
| **数据分析** | JupyterLab, Superset, Metabase, DBeaver |
| **开发工具** | Jenkins, Gitea, Portainer, SonarQube |
| **创意媒体** | Blender, GIMP, OBS Studio, Kdenlive, Shotcut |
| **科学计算** | FreeCAD, QGIS, ParaView, KiCad |
| **企业办公** | LibreOffice, NextCloud, GitLab, Grafana |
| **沟通协作** | Zoom, Jitsi Meet, Mattermost |
| **图表绘制** | Draw.io, Mermaid, PlantUML, Excalidraw |

## 与天龙引擎协同

| 天龙岗位 | 协同方式 |
|----------|---------|
| **02架构师** | 使用7阶段方法论设计CLI架构 |
| **03构建师** | 使用ReplSkin和后端封装模式实现CLI |
| **04验证师** | 使用TEST.md模式和真实软件测试 |
| **07记录师** | 自动生成测试文档 |
| **09-02编排协调师** | 编排Agent-Native软件工作流 |

## 文件结构

```
skills/cli-anything/
├── SKILL.md              # 本文档
├── HARNESS.md            # 7阶段方法论详细文档
├── repl_skin.py          # REPL统一接口组件
├── templates/
│   ├── test_template.py      # 测试模板
│   ├── backend_template.py   # 后端封装模板
│   └── cli_template.py       # CLI结构模板
└── scripts/
    └── cli-anything.sh       # 一键生成脚本
```

## 预期收益

| 指标 | 提升 |
|------|------|
| **CLI开发效率** | **质的飞跃**（自动化生成） |
| **Agent软件控制** | **任意软件可Agent化** |
| **测试覆盖率** | **+200%**（TDD + E2E + 真实软件） |
| **文档自动化** | **+150%**（TEST.md自动生成） |
| **输出标准化** | **统一JSON+Human双模式** |

## 参考资源

- [CLI-Anything GitHub](https://github.com/HKUDS/CLI-Anything)
- [HARNESS.md](./HARNESS.md) - 完整方法论
- [repl_skin.py](./repl_skin.py) - REPL组件源码