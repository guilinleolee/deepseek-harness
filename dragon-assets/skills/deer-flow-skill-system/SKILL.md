---
license: UNKNOWN
github_repo: bytedance/deer-flow.git
github_hash: b9709934255b2f7f951fd4b2300543ef764e1473
last_updated: 2026-04-25
source_type: derived
triggers: ["deer flow skill system", "deer-flow-skill-system"]
---
# deer-flow-skill-system

## Overview

DeerFlow Skill System - ByteDance开源的Super Agent Harness技能系统。完整集成17个高质量Skills到天龙引擎。

**来源**: [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | **Stars**: 14k+ | **MIT License**

## When to Use

- 用户请求深度研究任务
- 需要咨询级分析报告
- 需要数据分析+图表可视化
- 需要演示文稿/PPT生成
- 需要AI图片/视频/播客生成
- 需要GitHub深度研究
- 需要创建新技能

## Core Skills (17个内置技能)

### 研究与分析
| 技能 | 功能 | 核心能力 |
|------|------|---------|
| **deep-research** | 深度研究方法论 | 三阶段研究流程、多角度探索、信息验证 |
| **consulting-analysis** | 咨询级分析报告 | McKinsey/BCG咨询风格、框架设计、数据可视化 |
| **github-deep-research** | GitHub深度研究 | 仓库分析、代码研究、开发者洞察 |
| **find-skills** | 技能发现 | 自动发现可用技能、推荐最合适技能 |

### 数据与可视化
| 技能 | 功能 | 核心能力 |
|------|------|---------|
| **data-analysis** | DuckDB数据分析 | SQL查询、统计分析、多文件关联、缓存机制 |
| **chart-visualization** | 26种图表生成 | 智能图表选择、参数化生成、主题定制 |

### 内容创作
| 技能 | 功能 | 核心能力 |
|------|------|---------|
| **ppt-generation** | 演示文稿生成 | 8种风格、顺序生成、图片参考链、一致性保持 |
| **image-generation** | AI图片生成 | 多风格支持、参考图片、主题定制 |
| **video-generation** | 视频生成 | 脚本生成、画面生成、配音合成 |
| **podcast-generation** | 播客生成 | 文本转语音、多角色配音、背景音乐 |

### 设计
| 技能 | 功能 | 核心能力 |
|------|------|---------|
| **frontend-design** | 前端界面设计 | 组件设计、交互设计、设计系统 |
| **web-design-guidelines** | Web设计指南 | 设计原则、最佳实践、响应式设计 |

### 工具与系统
| 技能 | 功能 | 核心能力 |
|------|------|---------|
| **skill-creator** | 技能创建工具 | 迭代开发、测试评估、盲测比较 |
| **bootstrap** | 引导启动 | 项目初始化、环境配置、快速开始 |
| **surprise-me** | 惊喜模式 | 智能推荐、随机创意、意外发现 |
| **claude-to-deerflow** | Claude-DeerFlow桥接 | API调用、消息发送、状态管理 |

## Quick Start

```bash
# 深度研究
[@调研师] 使用deer-flow-skills进行深度研究
"研究AI Agent发展趋势"

# 咨询级分析报告
[@记录师] 使用consulting-analysis生成报告
"分析中国新能源汽车市场竞争格局"

# 数据分析
[@数据分析师] 使用data-analysis分析数据
"分析销售数据.xlsx，找出top10产品"

# 演示文稿
[@记录师] 使用ppt-generation生成PPT
"为AI产品发布创建演示文稿"
```

## Architecture

```
DeerFlow Skill System
├── 研究层 (Research Layer)
│   ├── deep-research
│   ├── github-deep-research
│   └── find-skills
│
├── 分析层 (Analysis Layer)
│   ├── consulting-analysis
│   ├── data-analysis
│   └── chart-visualization
│
├── 创作层 (Creation Layer)
│   ├── ppt-generation
│   ├── image-generation
│   ├── video-generation
│   └── podcast-generation
│
├── 设计层 (Design Layer)
│   ├── frontend-design
│   └── web-design-guidelines
│
└── 系统层 (System Layer)
    ├── skill-creator
    ├── bootstrap
    ├── surprise-me
    └── claude-to-deerflow
```

## 与天龙引擎现有技能协同

| DeerFlow技能 | 天龙现有技能 | 协同效果 |
|------------|-------------|---------|
| deep-research | deep-research V3.2 | DeerFlow更系统化，互补 |
| consulting-analysis | consulting-analysis | 基本对标，增强 |
| data-analysis | superset-data-connector | DeerFlow更轻量 |
| chart-visualization | info-graphic-pro | 图表库扩展 |
| ppt-generation | ppt-generator | DeerFlow更多风格(8种) |
| image-generation | smart-illustrator | 基本对标 |
| video-generation | remotion-best-practices | 基本对标 |
| skill-creator | skills-cli | DeerFlow更完整 |
| claude-to-deerflow | claude-to-im | 跨平台协同 |

## 核心工作流

### 研究-报告工作流
```
deep-research → consulting-analysis → chart-visualization → ppt-generation
     ↓              ↓                  ↓                 ↓
  信息收集        框架设计           数据可视化         演示文稿
```

### 数据分析工作流
```
data-analysis → chart-visualization → consulting-analysis → report
     ↓              ↓                   ↓               ↓
  SQL查询      图表生成          分析洞察          最终报告
```

## Skills索引

- [deep-research](references/deep-research.md) - 深度研究方法论
- [consulting-analysis](references/consulting-analysis.md) - 咨询级分析报告
- [data-analysis](references/data-analysis.md) - DuckDB数据分析
- [chart-visualization](references/chart-visualization.md) - 26种图表
- [ppt-generation](references/ppt-generation.md) - 演示文稿生成
- [skill-creator](references/skill-creator.md) - 技能创建工具
- [claude-to-deerflow](references/claude-to-deerflow.md) - API桥接

## 安装

```bash
# 克隆DeerFlow技能库
git clone https://github.com/bytedance/deer-flow.git /tmp/deer-flow

# 复制技能到天龙引擎
cp -r /tmp/deer-flow/skills/* skills/deer-flow-skill-system/

# 安装依赖
cd skills/deer-flow-skill-system
pip install duckdb pandas matplotlib
npm install
```

## 配置

环境变量配置（可选）:
```bash
export DEERFLOW_URL=http://localhost:2026
export DEERFLOW_GATEWAY_URL=http://localhost:8001
export DEERFLOW_LANGGRAPH_URL=http://localhost:2024/api/langgraph
```

## 天龙岗位调用

```bash
# 01调研师 - 深度研究
[@调研师] 使用deer-flow-skills的deep-research研究这个技术趋势

# 07记录师 - 咨询级报告
[@记录师] 使用consulting-analysis生成市场分析报告

# 17-01数据分析师 - 数据分析
[@数据分析师] 使用data-analysis分析这份Excel数据

# 35-05短视频编导 - 演示文稿
[@短视频编导] 使用ppt-generation生成产品演示
```

## 预期收益

| 指标 | 当前 | 集成后 | 提升 |
|------|------|--------|------|
| 技能数量 | 440+ | 457+ | +17个 |
| 研究深度 | 8步法 | 17 Skills增强 | +100% |
| 报告质量 | 专业 | 咨询级 | +200% |
| 图表类型 | 20+ | 46+ | +130% |

## 版本

- **V1.0** (2026-04-02): 初始集成DeerFlow 17 Skills
