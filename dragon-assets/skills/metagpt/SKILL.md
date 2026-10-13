---
license: UNKNOWN
github_repo: geekan/MetaGPT
github_hash: 11cdf466d042aece04fc6cfd13b28e1a70341b1f
last_updated: 2026-04-25
source_type: derived
triggers: ["metagpt", "MetaGPT Skill"]
---
# MetaGPT Skill

> 多Agent元编程框架 | 66,400+ Stars | MIT License

## Overview

MetaGPT 是多Agent元编程框架的核心项目，只需输入一行需求，即可输出完整的软件产品：用户故事、需求文档、数据结构、API文档和代码实现。

## 核心能力

```
自然语言需求 → 完整软件产品
┌─────────────────────────────────────────────────────────────┐
│ One-line input → 输出全套产出:                              │
│ • 用户故事 (User Stories)                                  │
│ • 需求文档 (Requirements)                                   │
│ • 数据结构 (Data Structures)                                │
│ • API文档                                                  │
│ • 代码实现                                                  │
└─────────────────────────────────────────────────────────────┘
```

## 技术架构

### Multi-Agent Role System

```
MetaGPT Multi-Agent                    天龙引擎对标
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Product Manager (PM)         ←         00分析师
  └─ 需求解析、用户故事                      (问题分析)

Architect                        ←         02架构师
  └─ 系统设计、架构决策                      (架构设计)

Project Manager                  ←         09-02编排协调师
  └─ 任务分解、进度管理                      (编排调度)

Engineer                        ←         03构建师
  └─ 代码实现、模块开发                      (编码施工)

QA Engineer                     ←         04验证师
  └─ 测试设计、缺陷验证                      (测试验证)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOP-Driven Workflow ("Code = SOP(Team)")
```

### SOP标准操作流程

MetaGPT 核心理念：**Code = SOP(Team)**

```
需求输入 → SOP解析 → 角色分配 → 协作执行 → 产物生成
    ↓
每个Agent遵循标准操作流程，确保输出一致性
```

## 安装

```bash
# 方式1: pip安装
pip install meta-gpt

# 方式2: 从源码安装
git clone https://github.com/geekan/MetaGPT.git
cd MetaGPT
pip install -e .

# 方式3: Docker (推荐)
docker pull metagpt/metagpt:latest
docker run --rm -it metagpt/metagpt:latest

# 配置API Key
export OPENAI_API_KEY="sk-..."     # OpenAI
export OPENAI_API_BASE="..."        # 可选: API代理
export ANTHROPIC_API_KEY="..."     # 可选: Claude
```

## 核心命令

### 1. 基础使用

```bash
# 一句话需求开发
metagpt "开发一个简单的TODO应用，包含添加、删除、完成功能"

# 指定项目目录
metagpt "开发一个博客系统" --directory ./my_blog

# 指定模型
metagpt "开发电商系统" --model claude-3-5-sonnet-20240620
```

### 2. 配置文件

```yaml
# config.yaml
model:
  provider: anthropic
  name: claude-3-5-sonnet-20240620
  api_key: ${ANTHROPIC_API_KEY}

sop:
  enabled: true
  strict: true

roles:
  product_manager:
    enabled: true
  architect:
    enabled: true
  project_manager:
    enabled: true
  engineer:
    enabled: true
  qa_engineer:
    enabled: true

output:
  directory: ./workspace
  save_actions: true
```

### 3. 自定义SOP

```python
# custom_sop.py
from metagpt.sop import SOPTemplate

class CustomSOP(SOPTemplate):
    name = "Custom Development SOP"

    def define_roles(self):
        return [
            Role(name="需求分析师", profile="需求解析"),
            Role(name="架构师", profile="系统设计"),
            Role(name="开发者", profile="代码实现"),
            Role(name="测试工程师", profile="测试验证"),
        ]

    def define_workflow(self):
        return [
            Step(role="需求分析师", action="解析需求", output="需求文档"),
            Step(role="架构师", action="设计架构", output="架构文档"),
            Step(role="开发者", action="实现代码", output="代码"),
            Step(role="测试工程师", action="编写测试", output="测试报告"),
        ]
```

## 天龙引擎集成

### 与天龙九部完美对标

```yaml
天龙九部                          MetaGPT角色
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
00分析师 ←──────→ Product Manager
  问题分析 ──需求解析 ───────────┘

01调研师 ←──────→ (协同支持)
  调研支持 ──技术调研 ──────────┘

02架构师 ←──────→ Architect
  架构设计 ──系统设计 ──────────┘

03构建师 ←──────→ Engineer
  代码施工 ──代码实现 ──────────┘

04验证师 ←──────→ QA Engineer
  测试验证 ──测试设计 ──────────┘

06审查师 ←──────→ (协同审查)
  终极审计 ──代码审查 ──────────┘

09-02编排 ←────→ Project Manager
  编排调度 ──任务分解 ──────────┘
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 天龙引擎调用示例

```bash
# 基础调用
[@09-02编排] 使用MetaGPT开发一个用户认证系统
[@编排协调师] 启动MetaGPT多Agent协作流程

# 高级调用
[@09-02] 使用MetaGPT SOP流程开发电商后端
[@编排] 配置MetaGPT使用Claude模型

# 特定角色调用
[@02架构师] 使用MetaGPT架构设计模块设计微服务
[@03构建师] 使用MetaGPT工程师角色实现API接口
[@04验证师] 使用MetaGPT QA角色设计测试用例
```

## 工作流程详解

```
┌─────────────────────────────────────────────────────────────────┐
│                    MetaGPT × 天龙引擎 SOP协作                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 1: 需求解析 (00分析师 + MetaGPT PM)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 用户输入: "开发一个在线商城系统"                           │  │
│  │                                                            │  │
│  │ MetaGPT PM:                                               │  │
│  │   → 需求澄清问题                                          │  │
│  │   → 生成用户故事 (User Stories)                           │  │
│  │   → 输出: 需求文档 (REQUIREMENTS.md)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│  Phase 2: 架构设计 (02架构师 + MetaGPT Architect)               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ MetaGPT Architect:                                         │  │
│  │   → 技术选型决策                                          │  │
│  │   → 系统架构设计 (MVC/Microservices)                      │  │
│  │   → 数据模型设计                                          │  │
│  │   → 输出: 架构文档 + 数据字典                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│  Phase 3: 任务分解 (09-02编排 + MetaGPT PM)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ MetaGPT PM:                                                 │  │
│  │   → 任务拆分 (Task Decomposition)                         │  │
│  │   → 依赖关系梳理                                          │  │
│  │   → 优先级排序                                            │  │
│  │   → 输出: 任务列表 (TASKS.md)                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│  Phase 4: 代码实现 (03构建师 + MetaGPT Engineer)                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ MetaGPT Engineer (并行):                                  │  │
│  │   → 用户模块开发                                          │  │
│  │   → 商品模块开发                                          │  │
│  │   → 订单模块开发                                          │  │
│  │   → 支付模块开发                                          │  │
│  │   → 输出: 完整代码库                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│  Phase 5: 测试验证 (04验证师 + MetaGPT QA)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ MetaGPT QA:                                                │  │
│  │   → 单元测试生成                                          │  │
│  │   → 集成测试设计                                          │  │
│  │   → 测试执行与报告                                        │  │
│  │   → 输出: 测试报告 (TEST_REPORT.md)                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│  Phase 6: 代码审查 (06审查师)                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 天龙06审查师:                                              │  │
│  │   → 架构合理性审查                                        │  │
│  │   → 代码质量审查                                          │  │
│  │   → 安全漏洞扫描                                          │  │
│  │   → 输出: 审查报告 (REVIEW.md)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 高级用法

### 1. 多模型协作

```yaml
# 多模型配置
models:
  claude:
    provider: anthropic
    name: claude-3-5-sonnet-20240620
    roles:
      - architect
      - engineer

  gpt4:
    provider: openai
    name: gpt-4-turbo
    roles:
      - pm
      - qa

  deepseek:
    provider: deepseek
    name: deepseek-coder
    roles:
      - engineer
```

### 2. 自定义角色

```python
from metagpt import Role
from metagpt.schema import Message

class CustomRole(Role):
    name: str = "CustomRole"
    profile: str = "Custom Profile"
    desc: str = "Custom role description"

    async def _act(self) -> Message:
        # 自定义行为
        todo = self.get_todo()
        result = await self.do(todo)
        return Message(content=result)
```

### 3. 与LangChain集成

```python
from metagpt import MetaGPT
from langchain.llms import ChatAnthropic

# 使用LangChain LLM
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

metagpt = MetaGPT(
    llm=llm,
    project="Custom Project",
    sdk="langchain"
)

await metagpt.run("开发一个数据可视化仪表板")
```

## 输出产物

```
workspace/
├── docs/
│   ├── 需求文档.md          # REQUIREMENTS.md
│   ├── 架构设计.md          # ARCHITECTURE.md
│   ├── 接口设计.md          # API.md
│   └── 数据字典.md          # DATA_DICT.md
├── tasks/
│   └── 任务列表.md          # TASKS.md
├── src/
│   ├── 模块1/
│   │   ├── __init__.py
│   │   ├── module.py
│   │   └── test_module.py
│   └── 模块2/
├── tests/
│   ├── test_integration.py
│   └── test_e2e.py
└── reports/
    ├── 测试报告.md          # TEST_REPORT.md
    └── 审查报告.md          # REVIEW.md
```

## 评估与基准

| 指标 | 数值 | 说明 |
|------|------|------|
| **SWE-bench** | Top-5 | 软件工程基准测试 |
| **MBPP** | >80% | Python代码生成 |
| **HumanEval** | >70% | 代码补全测试 |
| **Multi-turn** | 最高 | 多轮对话协作 |

## 参考资源

- **仓库**: https://github.com/geekan/MetaGPT
- **文档**: https://docs.deepwisdom.ai/
- **论文**: MetaGPT: Multi-Agent Framework via SOP
- **Discord**: https://discord.gg/METAGPT

## 相关天龙Skill

| 天龙Skill | 协同方式 |
|-----------|---------|
| crewai-orchestration (V8.13) | 多Agent协作编排 |
| autogenesis (V8.5) | 自演化协议 |
| langflow-workflow-designer (V8.60) | 可视化工作流设计 |
| blueprint (V8.67) | 蓝图规划器 |
| blueprint (V8.67) | 蓝图规划器 |
| eval-harness (V8.66) | 评估驱动开发 |
| context-budget (V8.66) | 上下文预算分析 |

## 与CrewAI协同

| 维度 | MetaGPT | CrewAI |
|------|---------|--------|
| **理念** | SOP驱动 | Role驱动 |
| **输出** | 完整软件产品 | Agent任务执行 |
| **适用** | 复杂软件开发 | 多角色协作 |
| **天龙定位** | 深度开发 (V8.69) | 日常协作 (V8.13) |

---

*Version: 1.0.0 | Updated: 2026-03-30*
