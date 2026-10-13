---
license: UNKNOWN
name: indie-launch-channels
description: 独立开发者推广渠道数据库 - 结构化搜索367个渠道，支持平台分类、关键词查询、场景推荐
version: "1.0.0"
created: "2026-05-05"
tags: ["推广渠道", "独立开发者", "渠道数据库", "367渠道", "平台分类"]
platforms: ["claude", "cursor", "codex", "gemini", "trae", "windsurf"]
source: "naxiaoduo/1000UserGuide"
天龙岗位: ["30-01-营销总监", "35-02-社媒运营", "25-02-精益创业导师", "32-01-市场研究"]
triggers: ["indie launch channels", "indie-launch-channels"]
---

# indie-launch-channels

独立开发者推广渠道数据库 — 来自 [naxiaoduo/1000UserGuide](https://github.com/naxiaoduo/1000UserGuide) (3.8k Stars)

## L0: 一句话
结构化搜索 367 个独立开发者推广渠道，支持平台分类、关键词查询、场景推荐。

## L1: 使用场景

- 推广新产品时寻找合适渠道
- 按平台（国内/海外/AI）筛选渠道
- 关键词搜索渠道名称/描述
- 查看各渠道的分类和使用说明

## L2: 详细文档

### 数据来源

- **原始数据**: GitHub README.md（自动同步）
- **更新频率**: 手动运行解析脚本
- **渠道总数**: 367 个
- **分类数**: 8 大类

### 分类体系

| category | category_cn | 说明 |
|----------|-------------|------|
| `cn_website` | 国内网站渠道 | 阮一峰周刊、少数派等 |
| `cn_directory` | 国内网址导航站 | 酷壳、奇客资讯等 |
| `cn_community` | 国内社区论坛 | 掘金、思否、V2EX等 |
| `overseas_website` | 海外网站渠道 | Product Hunt、Hacker News等 |
| `ai_directory` | 海外AI导航网站 | AI导航、AI工具集等 |
| `overseas_directory` | 海外目录站点 | 目录站、导航站 |
| `overseas_community` | 海外社区 | Reddit子版块等 |
| `reddit` | Reddit子版块 | r/Startups、r/SideProject等 |

### 数据结构

```json
{
  "source": "1000UserGuide",
  "total_count": 367,
  "categories": ["cn_website", "cn_directory", ...],
  "channels": [
    {
      "name": "科技爱好者周刊",
      "url": "https://www.ruanyifeng.com/blog/weekly/",
      "category": "cn_website",
      "category_cn": "国内网站渠道",
      "description": "阮一峰分享的科技内容，记录每周值得分享的科技内容，周五发布",
      "source": "1000UserGuide"
    }
  ]
}
```

### 查询示例

> **Windows Git Bash 用户注意**: 请使用 `PYTHONIOENCODING=utf-8 python`（不要用 `python3`，Windows 下 `python3` 可能不可用）。设置 `PYTHONIOENCODING=utf-8` 是为了让 emoji 字符（📊🔍📋）在 Windows GBK 控制台正常显示。

#### 按分类搜索

```bash
PYTHONIOENCODING=utf-8 python ~/.claude/skills/indie-launch-channels/scripts/query_channels.py --category cn_community
```

#### 关键词搜索

```bash
PYTHONIOENCODING=utf-8 python ~/.claude/skills/indie-launch-channels/scripts/query_channels.py --keyword "独立开发"
```

#### 按平台筛选

```bash
# 海外渠道
PYTHONIOENCODING=utf-8 python ~/.claude/skills/indie-launch-channels/scripts/query_channels.py --platform overseas

# 国内渠道
PYTHONIOENCODING=utf-8 python ~/.claude/skills/indie-launch-channels/scripts/query_channels.py --platform cn
```

#### 场景推荐

```bash
PYTHONIOENCODING=utf-8 python ~/.claude/skills/indie-launch-channels/scripts/query_channels.py --scene "独立开发者首发"
```

### 更新数据

```bash
# 重新从 GitHub 抓取并解析
PYTHONIOENCODING=utf-8 python ~/.claude/skills/indie-launch-channels/scripts/parse_channels.py
```

### 文件结构

```
indie-launch-channels/
├── SKILL.md                    # 本文件
├── data/
│   └── channels.json          # 367 渠道数据库
└── scripts/
    ├── parse_channels.py      # 从 GitHub 解析渠道数据
    └── query_channels.py      # 查询接口
```

### 使用场景矩阵

| 场景 | 推荐分类 | 关键词 |
|------|---------|--------|
| 独立开发者首发 | cn_community, overseas_community | "独立开发", "Product Hunt" |
| AI 产品推广 | ai_directory, overseas_website | "AI", "工具" |
| 程序员社区 | cn_community | "掘金", "思否", "V2EX" |
| 出海推广 | overseas_directory, reddit | "Product Hunt", "r/Startups" |
| 资源导航收录 | cn_directory, overseas_directory | "导航", "目录" |

### 与天龙九部协同

| 天龙岗位 | 协同方式 |
|---------|---------|
| **30-01 营销总监** | 渠道策略规划 |
| **35-02 社媒运营** | 渠道发布执行 |
| **25-02 精益创业导师** | 首 100 用户获取 |
| **32-01 市场研究** | 渠道调研 |

## 来源

- **项目**: [naxiaoduo/1000UserGuide](https://github.com/naxiaoduo/1000UserGuide)
- **Stars**: 3,811
- **用途**: 独立开发者推广渠道大全
- **更新**: 2026-05-05