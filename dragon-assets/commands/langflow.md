---
name: langflow
description: LangFlow可视化工作流命令
invokable: true
---
# LangFlow可视化工作流命令

## 快速命令

```bash
# 方法1: 使用专用启动脚本（推荐）
python ~/.claude/skills/langflow-workflow-designer/scripts/start_langflow.py

# 方法2: 使用虚拟环境启动
%LOCALAPPDATA%\Temp\langflow-env\Scripts\python.exe -m langflow

# 方法3: 直接使用uvicorn（如果venv路径不同）
uvicorn langflow.main:setup_app --host 127.0.0.1 --port 7860

# 访问Web界面
open http://127.0.0.1:7860

# API文档
open http://127.0.0.1:7860/docs
```

## 天龙引擎SKILL命令

### 工作流设计器
```bash
# 查看服务状态
python3 ~/.claude/skills/langflow-workflow-designer/scripts/langflow_workflow.py status

# 启动服务
python3 ~/.claude/skills/langflow-workflow-designer/scripts/langflow_workflow.py start

# 列出所有工作流
python3 ~/.claude/skills/langflow-workflow-designer/scripts/langflow_workflow.py list

# 导出工作流
python3 ~/.claude/skills/langflow-workflow-designer/scripts/langflow_workflow.py export --flow-id <ID> --output flow.json

# 搜索组件
python3 ~/.claude/skills/langflow-workflow-designer/scripts/langflow_workflow.py search "LLM"
```

### MCP桥接器
```bash
# 查看MCP Server状态
python3 ~/.claude/skills/langflow-mcp-bridge/scripts/langflow_mcp_bridge.py status

# 启动MCP Server
python3 ~/.claude/skills/langflow-mcp-bridge/scripts/langflow_mcp_bridge.py serve

# 列出MCP工具
python3 ~/.claude/skills/langflow-mcp-bridge/scripts/langflow_mcp_bridge.py list

# 部署工作流为MCP工具
python3 ~/.claude/skills/langflow-mcp-bridge/scripts/langflow_mcp_bridge.py deploy --flow-id <ID>
```

### 组件构建器
```bash
# 生成LLM组件
python3 ~/.claude/skills/langflow-component-builder/templates/component_template.py generate \
  --type llm --name my_llm_component --display-name "我的LLM组件" \
  --description "调用Claude API"

# 生成数据处理组件
python3 ~/.claude/skills/langflow-component-builder/templates/component_template.py generate \
  --type processor --name data_processor --display-name "数据处理器"

# 生成API集成组件
python3 ~/.claude/skills/langflow-component-builder/templates/component_template.py generate \
  --type api --name api_caller --display-name "API调用器"

# 生成RAG组件
python3 ~/.claude/skills/langflow-component-builder/templates/component_template.py generate \
  --type rag --name rag_search --display-name "RAG检索"
```

## 版本说明

当前安装版本: **v1.0.9** (langflow-base v0.0.85)

```bash
# 检查版本
%LOCALAPPDATA%\Temp\langflow-env\Scripts\python.exe -c "import langflow; print(langflow.__version__)" 2>nul || echo "use uv pip list"

# 升级到最新版本（如需要）
uv pip install langflow --upgrade --python %LOCALAPPDATA%\Temp\langflow-env\Scripts\python.exe
```

## 工作流导出

LangFlow工作流可以导出为JSON格式，供其他系统集成：

```python
import requests

# 导出工作流
flow_id = "your-flow-id"
response = requests.get(f"http://127.0.0.1:7860/api/v1/flows/{flow_id}")
flow_data = response.json()

# 保存为JSON
import json
with open("flow.json", "w") as f:
    json.dump(flow_data, f, indent=2)
```
