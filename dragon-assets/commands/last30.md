---
name: last30
description: last30 - 30天时效性研究快捷命令
invokable: true
---
# last30 - 30天时效性研究快捷命令

快速调用last30days技能的便捷命令。

## 用法

```bash
# 基础调用
/last30 AI视频工具

# 对比研究
/last30 cursor vs windsurf

# 快速模式（8-12条结果）
/last30 --quick AI编辑器

# 深度模式（50-70条结果）
/last30 --deep Claude Code新功能

# 指定平台
/last30 --search=reddit,x,youtube 最佳项目管理工具

# 输出JSON格式
/last30 --emit=json AI趋势

# 输出到文件
/last30 --emit=path 热门AI工具
```

## 平台选项

| 平台 | 权重 | 免费 | 说明 |
|------|------|------|------|
| reddit | 25% | 部分 | 海外社区讨论 |
| x | 25% | 部分 | X/Twitter |
| youtube | 15% | ✅ | 视频内容 |
| tiktok | 10% | 部分 | 短视频 |
| hackernews | 10% | ✅ | 技术社区 |
| polymarket | 5% | ✅ | 预测市场 |
| bluesky | 5% | ✅ | 新兴社媒 |
| web | 10% | ✅ | DuckDuckGo搜索 |

## 三维评分

```
score = relevance * 0.4 + recency * 0.3 + engagement * 0.3
```

## 与天龙岗位协同

| 岗位 | 使用场景 |
|------|---------|
| **01调研师** | 时效性信息收集 |
| **32-01市场研究** | 消费趋势追踪 |
| **35-02社媒运营** | 热点内容发现 |
| **00分析师** | 时效性证据验证 |
| **62-02行业研究员** | 行业动态追踪 |

## API密钥配置

必需：
```bash
export SCRAPECREATORS_API_KEY="your-key"  # Reddit搜索
```

可选（增强功能）：
```bash
export XAI_API_KEY="your-key"        # X搜索
export BRAVE_API_KEY="your-key"      # 网页搜索
export OPENAI_API_KEY="your-key"     # 回退搜索
```

## 输出目录

所有报告输出到：`~/Documents/Last30Days/`

---

**完整文档**: [skills/last30days/SKILL.md](skills/last30days/SKILL.md)