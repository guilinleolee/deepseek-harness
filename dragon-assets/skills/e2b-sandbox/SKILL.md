---
license: UNKNOWN
github_repo: simstudioai/sim
github_hash: 3422f64c5f6e1a1c4c008fac1ac1709e9c97035a
last_updated: 2026-04-25
source_type: derived
triggers: ["e2b sandbox", "e2b-sandbox"]
---
# e2b-sandbox

> E2B云沙箱集成 - 安全隔离的远程代码执行环境

## 来源项目

| 项目 | Stars | 核心能力 |
|------|-------|---------|
| [simstudioai/sim](https://github.com/simstudioai/sim) | 27.2k | 远程代码执行（集成E2B） |
| [e2b-dev/e2b](https://github.com/e2b-dev/e2b) | 12k+ | 云沙箱安全执行环境 |

## 核心价值

填补天龙引擎在**云沙箱远程执行**的关键空白，实现：
- 安全隔离的代码执行环境
- 云端动态代码运行
- 多语言支持（Python, Node.js, Bash等）
- 沙箱内工具调用和文件系统访问

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│ E2B Cloud Sandbox Architecture                               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐ │
│  │  Client SDK │ ──▶ │  Sandbox    │ ──▶ │  Results    │ │
│  │  (Python/JS)│     │  (Isolated) │     │  (Output)   │ │
│  └─────────────┘     └─────────────┘     └─────────────┘ │
│                             │                                │
│         ┌──────────────────┼──────────────────┐             │
│         ↓                  ↓                  ↓             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │
│  │  Filesystem │   │   Network   │   │   Tools     │      │
│  │  (Read/    │   │  (Allowed)  │   │  (Python/   │      │
│  │   Write)    │   │             │   │   Node)     │      │
│  └─────────────┘   └─────────────┘   └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 与NeMoClaw对比

| 维度 | NeMoClaw | E2B | 选择建议 |
|------|----------|-----|---------|
| **部署模式** | 本地部署 | 云端托管 | 快速验证→E2B |
| **安全隔离** | Landlock+seccomp | 虚拟机级隔离 | 高安全→NeMoClaw |
| **成本** | 无（自托管） | 按使用计费 | 成本控制→NeMoClaw |
| **启动速度** | 即时 | ~500ms | 实时场景→NeMoClaw |
| **生态集成** | 手动配置 | 1,000+工具 | 快速集成→E2B |

## 天龙岗位升级

| 岗位 | 版本 | 新增能力 | 提升 |
|------|------|---------|------|
| **03 构建师** | V8.68 → V8.69 | 云沙箱执行 + 远程验证 | ⭐⭐⭐⭐ |
| **04 验证师** | V8.68 → V8.69 | 隔离测试执行 + 安全验证 | ⭐⭐⭐⭐ |
| **05 安全师** | V8.68 → V8.69 | 沙箱安全审计 + 隔离验证 | ⭐⭐⭐⭐ |

## 核心命令速查

```bash
# 安装SDK
pip install e2b-sdk
# 或
npm install e2b

# 环境变量
export E2B_API_KEY="your-api-key"

# 运行沙箱
e2b run --lang python "print('Hello')"
e2b run --lang node "console.log('Hello')"
```

## SDK使用示例

### Python SDK

```python
from e2b import Sandbox

# 创建沙箱
sandbox = Sandbox()

# 执行代码
result = sandbox.run_code(
    '''
import json
data = {"hello": "world"}
print(json.dumps(data))
''',
    language="python"
)
print(result.stdout)

# 执行命令
result = sandbox.run_command("ls -la")

# 文件操作
sandbox.filesystem.write("/tmp/test.txt", "Hello World")
content = sandbox.filesystem.read("/tmp/test.txt")

# 工具调用
result = sandbox.tools.run("web-search", {"query": "AI agents"})

# 清理
sandbox.close()
```

### JavaScript SDK

```javascript
import { Sandbox } from 'e2b';

const sandbox = await Sandbox.create();

// 执行代码
const result = await sandbox.runCode(`
  const data = { hello: 'world' };
  console.log(JSON.stringify(data));
`, { language: 'nodejs' });
console.log(result.stdout);

// 执行命令
const cmdResult = await sandbox.runCommand('ls -la');

// 文件操作
await sandbox.filesystem.write('/tmp/test.txt', 'Hello World');
const content = await sandbox.filesystem.read('/tmp/test.txt');

await sandbox.close();
```

## 天龙集成模式

### 模式1：开发验证（推荐日常使用）

```python
from e2b import Sandbox

def validate_with_sandbox(code: str, language: str = "python"):
    """在沙箱中验证代码"""
    sandbox = Sandbox()

    try:
        result = sandbox.run_code(code, language=language)

        if result.error:
            return {
                "status": "failed",
                "error": result.error,
                "stdout": result.stdout
            }

        return {
            "status": "success",
            "output": result.stdout,
            "execution_time": result.elapsed_time
        }
    finally:
        sandbox.close()
```

### 模式2：安全测试隔离

```python
def safe_test(code: str, dangerous_patterns: list):
    """安全测试 - 检测危险代码"""
    sandbox = Sandbox(timeout=5)  # 5秒超时

    # 检查危险模式
    for pattern in dangerous_patterns:
        if pattern in code:
            return {
                "status": "blocked",
                "reason": f"Dangerous pattern detected: {pattern}"
            }

    try:
        result = sandbox.run_code(code, language="python")
        return {"status": "executed", "output": result.stdout}
    finally:
        sandbox.close()
```

### 模式3：工具调用编排

```python
def workflow_with_tools():
    """带工具调用的工作流"""
    sandbox = Sandbox(
        tools=["web-search", "filesystem", "browser"]
    )

    try:
        # 搜索
        search_result = sandbox.tools.run("web-search", {
            "query": "latest AI news"
        })

        # 分析
        analysis = sandbox.run_code(f'''
import json
results = {search_result}

# 分析逻辑
analysis = [item for item in results if item["source"] == "tech"]
print(json.dumps(analysis))
        ''', language="python")

        return {"analysis": analysis.stdout}
    finally:
        sandbox.close()
```

## 预配置沙箱模板

```python
# Python数据科学
ds_sandbox = Sandbox(template="data-science")

# Web开发
web_sandbox = Sandbox(template="web-dev")

# 通用
base_sandbox = Sandbox(template="base")

# 自定义
custom_sandbox = Sandbox(
    cpu=2,
    memory=2048,
    timeout=60,
    tools=["filesystem", "network"]
)
```

## 与Sim工作流集成

```yaml
# Sim工作流中调用E2B
nodes:
  - id: code_executor
    type: tool
    config:
      tool: e2b-sandbox
      params:
        template: python-data-science
        timeout: 60
        code: |
          import pandas as pd
          import numpy as np

          # 数据处理逻辑
          df = pd.read_csv("data.csv")
          result = df.describe()
          print(result)
```

## 安装与配置

```bash
# 安装SDK
pip install e2b-sdk
# 或
npm install e2b

# 获取API Key
# 访问 https://e2b.dev/docs/getting-started/api-key

# 环境变量
export E2B_API_KEY="your-api-key"

# Docker本地开发（可选）
docker pull e2b/base
```

## 安全最佳实践

1. **超时设置**：始终设置合理的超时时间
2. **资源限制**：沙箱有CPU/内存限制
3. **网络控制**：根据需要启用/禁用网络
4. **文件清理**：执行后清理临时文件
5. **敏感信息**：不要在沙箱中存储敏感信息

## 预期收益

| 指标 | V8.68 | V8.69 | 提升 |
|------|-------|-------|------|
| **代码执行安全** | NeMoClaw本地 | E2B云+本地双模式 | ⭐⭐⭐⭐⭐ |
| **开发验证速度** | 本地构建 | 即时沙箱 | ⭐⭐⭐⭐ |
| **测试隔离性** | 手动隔离 | 自动隔离 | ⭐⭐⭐⭐ |
| **危险代码检测** | 规则检查 | 沙箱执行 | ⭐⭐⭐⭐⭐ |

## 技能文件

- [skills/e2b-sandbox/SKILL.md](skills/e2b-sandbox/SKILL.md)
- [skills/e2b-sandbox/scripts/e2b_client.py](skills/e2b-sandbox/scripts/e2b_client.py)
- [skills/e2b-sandbox/templates/sandboxes.py](skills/e2b-sandbox/templates/sandboxes.py)
