# RequestHunt - 多平台用户研究引擎

## 概述

RequestHunt 是 ReScienceLab 开发的多平台用户研究引擎，支持 Reddit、X/Twitter、GitHub、YouTube、LinkedIn、Amazon 六大平台的用户反馈采集、情感分析和竞品监控。

## 安装

### 前置依赖

```bash
# Reddit (内置，无需额外配置)
# X/Twitter
npm install -g xreach  # 可选

# GitHub
gh auth login  # 需要 GitHub CLI

# YouTube
pip install yt-dlp

# LinkedIn
mcporter setup  # 可选
```

### 安装 RequestHunt

```bash
# 直接使用 Python
D:/python/python.exe c:/Users/li/.claude/skills/requesthunt/scripts/requesthunt_client.py --help

# 或创建快捷命令
alias requesthunt='D:/python/python.exe c:/Users/li/.claude/skills/requesthunt/scripts/requesthunt_client.py'
```

## 使用方式

### 1. 用户研究

```bash
requesthunt research "Claude AI" --platforms reddit,twitter --limit 100
```

### 2. 情感分析

```bash
requesthunt sentiment "Tesla FSD" --platforms all --time-range 30d
```

### 3. 竞品监控

```bash
requesthunt monitor "Apple,Samsung" --platforms twitter,reddit --alert on
```

### 4. 评论采集

```bash
requesthunt reviews "MacBook Pro" --platform amazon --limit 200
```

## 与天龙引擎协同

RequestHunt 与天龙引擎现有技能形成完整用户研究链路：

| 技能 | 职责 | 层级 |
|------|------|------|
| agent-reach | 原始数据采集 | 数据层 |
| **requesthunt** | 洞察分析 | 洞察层 |
| deep-research | 深度研究报告 | 研究层 |
| MiroFish | 舆情预测推演 | 预测层 |

## 局限性

- 部分平台需要 API 认证
- 情感分析基于规则，准确率约 75-85%
- 建议结合 agent-reach 进行深度数据采集

## 文件结构

```
requesthunt/
├── SKILL.md              # 技能说明文档
├── README.md            # 本文件
└── scripts/
    └── requesthunt_client.py  # Python 客户端
```
