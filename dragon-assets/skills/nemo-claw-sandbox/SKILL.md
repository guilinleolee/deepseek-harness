---
license: UNKNOWN
name: nemo-claw-sandbox
description: NeMoClaw安全沙箱管理，NVIDIA开源安全沙箱运行参考栈
github_repo: NVIDIA/NemoClaw
github_hash: 260b23739922e67798b3baeffbf2fe698b91747d
last_updated: 2026-04-25
source_type: marketplace
triggers: ["nemo claw sandbox", "NemoClaw 安全沙箱 Skill"]
---

# NemoClaw 安全沙箱 Skill

> 集成 NVIDIA NeMoClaw，为天龙引擎 Agent 提供安全沙箱隔离能力

## 功能概述

NemoClaw 是 NVIDIA 官方发布的 OpenClaw 安全沙箱运行参考栈，提供：
- **四层安全隔离**：Landlock + seccomp + netns + Filesystem
- **声明式网络策略**：YAML 配置的内核级网络控制
- **透明推理路由**：NVIDIA Nemotron / GPT / Claude / Gemini 一键切换
- **TUI 实时审批**：操作拦截时的图形化审批界面

## 安装

```bash
# 一键安装
curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash

# 验证安装
nemoclaw --version
```

## 核心命令

### 沙箱管理

| 命令 | 功能 |
|------|------|
| `nemoclaw onboard` | 交互式向导：创建沙箱、配置推理、设置策略 |
| `nemoclaw <name> connect` | 连接沙箱 shell |
| `nemoclaw start` / `stop` / `status` | 管理辅助服务 |
| `openshell term` | 打开 TUI 监控界面 |

### OpenClaw 命令（沙箱内）

| 命令 | 功能 |
|------|------|
| `openclaw tui` | 交互式聊天界面 |
| `openclaw agent --agent main -m "message"` | CLI 单次执行 |
| `openshell sandbox list` | 列出沙箱 |
| `openshell policy set <file>` | 设置网络策略 |

### 策略管理

| 命令 | 功能 |
|------|------|
| `openshell policy set openclaw-sandbox.yaml` | 应用网络策略 |
| `openshell policy list` | 列出可用策略预设 |

## 预设策略

NemoClaw 提供常用平台预设策略：

| 策略文件 | 适用场景 |
|----------|----------|
| `pypi.yaml` | Python 包安装 |
| `docker-hub.yaml` | Docker 镜像拉取 |
| `slack.yaml` | Slack 集成 |
| `jira.yaml` | Jira 集成 |

## 推理提供商

| 提供商 | 支持模型 |
|--------|----------|
| NVIDIA Endpoints | Nemotron-3 120B |
| OpenAI | GPT-4o, GPT-4o-mini |
| Anthropic | Claude 3.5, Claude 3 |
| Google Gemini | Gemini 2.0, Gemini 1.5 |
| OpenAI 兼容端点 | 自托管模型 |
| Ollama | 本地模型 |

## 安全层

```
┌─────────────────────────────────────────────────────────────┐
│ NeMoClaw 四层安全架构                                       │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Inference  ← 推理请求透明路由                     │
│  Layer 3: Network   ← Landlock + seccomp 策略控制          │
│  Layer 2: Filesystem ← 沙箱边界 /sandbox + /tmp           │
│  Layer 1: Process  ← syscall 过滤，阻止权限提升            │
└─────────────────────────────────────────────────────────────┘
```

## 天龙引擎集成

### 05安全师 集成

使用沙箱执行高风险操作：

```bash
# 在沙箱内执行敏感操作
nemoclaw secure-sandbox connect
openclaw agent -m "执行 git reset --hard，确认无风险"
```

### 09-02编排协调师 集成

沙箱级任务编排：

```yaml
# 任务配置
tasks:
  - name: 安全构建
    sandbox: secure-sandbox
    commands:
      - nemoclaw secure-sandbox connect
      - openclaw agent -m "构建项目"
```

### 03构建师 集成

容器化构建环境：

```bash
# 在沙箱内构建
nemoclaw build-sandbox connect
cd /sandbox/project
pip install -r requirements.txt
pytest
```

## 最佳实践

### 1. 创建专用沙箱

```bash
# 为不同任务创建独立沙箱
nemoclaw onboard  # 创建安全沙箱
nemoclaw build connect  # 构建环境
nemoclaw deploy connect  # 部署环境
```

### 2. 策略分层

```yaml
# openclaw-sandbox.yaml
network:
  allowed:
    - api.github.com
    - pypi.org
    - docker.io
  denied:
    - "*"
  on_blocked:
    action: prompt  # 拦截时提示审批
```

### 3. 推理源切换

```bash
# 切换推理源
nemoclaw inference set nvidia/nemotron-3-120b
nemoclaw inference set anthropic/claude-3-5-sonnet
```

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 安装失败 | 确保 Docker 运行时已启动 |
| 沙箱无法连接 | 检查 `nemoclaw <name> status` |
| 网络策略冲突 | 运行 `openshell policy set default.yaml` |
| 内存不足 | 分配至少 8GB RAM 或配置 swap |

## 参考资料

- [NeMoClaw 官方文档](https://docs.nvidia.com/nemoclaw/latest/)
- [OpenShell 策略配置](https://docs.nvidia.com/openshell/latest/reference/policy-schema.html)
- [NVIDIA Agent Toolkit](https://github.com/NVIDIA/NemoClaw)

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.62+ | **Alpha状态**: 2026-03-16
