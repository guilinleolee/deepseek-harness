---
license: UNKNOWN
name: x-publisher-v2
version: 1.0.0
description: |
  X/Twitter发布双路线保障系统。Chrome CDP路线 + twitter-cli路线互为备份，确保发布可靠性。支持普通帖子、视频、引用推文、长文文章。
author: 天龙引擎团队 (基于 baoyu-post-to-x + twitter-cli)
created: 2026-03-13
category: social-media

triggers:
  - "post to X"
  - "post to Twitter"
  - "tweet"
  - "发推"
  - "发布到X"
  - "x-publisher"
---

# X Publisher V2 - 双路线发布保障系统

X/Twitter发布系统，双路线互为备份，确保发布成功率。

## 触发词
- post to X
- post to Twitter
- tweet
- 发推
- 发布到X
- x-publisher

## 核心价值

**双路线保障机制**：

```
┌─────────────────────────────────────────────────────────────┐
│ Route 1: twitter-cli (API路线)                              │
│   ✓ TLS指纹 + 请求延迟                                      │
│   ✓ 原生API调用                                             │
│   ✓ 速度快、稳定性高                                        │
│   ⚠️ 需要认证配置                                           │
├─────────────────────────────────────────────────────────────┤
│ Route 2: Chrome CDP (浏览器路线)                            │
│   ✓ 真实浏览器模拟                                          │
│   ✓ 反爬虫突破                                              │
│   ✓ 支持复杂交互                                            │
│   ⚠️ 首次需要登录                                           │
└─────────────────────────────────────────────────────────────┘

策略：优先 Route 1，失败时自动切换 Route 2
```

## 支持的发布类型

| 类型 | Route 1 (twitter-cli) | Route 2 (Chrome CDP) |
|------|----------------------|---------------------|
| 普通文本 | ✅ `twitter post` | ✅ x-browser.ts |
| 图片帖子 | ✅ `twitter post --media` | ✅ x-browser.ts |
| 视频帖子 | ✅ `twitter post --video` | ✅ x-video.ts |
| 引用推文 | ✅ `twitter quote` | ✅ x-quote.ts |
| 回复 | ✅ `twitter reply` | ✅ x-browser.ts |
| 长文文章 | ❌ | ✅ x-article.ts |
| 删除推文 | ✅ `twitter delete` | ❌ |

## 使用方式

### 普通发布（自动选择路线）

```bash
# 发布文本
/x-publisher-v2 "Hello World!"

# 发布带图片
/x-publisher-v2 "Check this out!" --images img1.png,img2.png

# 发布带视频
/x-publisher-v2 "New video!" --video demo.mp4

# 引用推文
/x-publisher-v2 "Great point!" --quote-tweet 1234567890
```

### 指定路线

```bash
# 强制使用 Route 1 (twitter-cli)
/x-publisher-v2 "Hello!" --route api

# 强制使用 Route 2 (Chrome CDP)
/x-publisher-v2 "Hello!" --route browser
```

### 长文文章（仅 Chrome CDP）

```bash
# 发布长文文章
/x-publisher-v2 article.md --type article

# 支持Markdown格式
/x-publisher-v2 my-thoughts.md --type article
```

## Route 1: twitter-cli 命令

```bash
# 认证检查
twitter status --yaml

# 发布
twitter post "内容"
twitter post "内容" --media image.png
twitter post "内容" --video video.mp4

# 互动
twitter reply 12345 "回复内容"
twitter quote 12345 "评论"
twitter like 12345
twitter retweet 12345
```

## Route 2: Chrome CDP 脚本

| 脚本 | 功能 |
|------|------|
| `x-browser.ts` | 普通帖子（文本+图片） |
| `x-video.ts` | 视频帖子 |
| `x-quote.ts` | 引用推文 |
| `x-article.ts` | 长文文章 |
| `md-to-html.ts` | Markdown转HTML |

## 自动故障切换

```
尝试 Route 1 (twitter-cli)
    │
    ├── 成功 ✓ → 完成
    │
    └── 失败 ✗
          │
          ├── 错误类型判断
          │     ├── 认证过期 → 提示重新认证
          │     ├── 速率限制 → 等待后重试
          │     ├── API错误 → 切换 Route 2
          │     └── 网络错误 → 切换 Route 2
          │
          └── 切换 Route 2 (Chrome CDP)
                │
                ├── 成功 ✓ → 完成
                └── 失败 ✗ → 报告错误
```

## 前置条件

### Route 1 (twitter-cli)
```bash
# 安装
pip install twitter-cli

# 认证
twitter auth --save
```

### Route 2 (Chrome CDP)
- Google Chrome 或 Chromium
- bun 运行时
- 首次运行需手动登录X（session会被保存）

## 天龙岗位映射

| 岗位 | 使用场景 |
|------|---------|
| **35-02 社媒运营** | X/Twitter内容发布 |
| **32-01 市场研究** | 研究成果分享 |
| **28-01 文案策划** | 文案发布测试 |

## 与现有能力协同

| 天龙技能 | 协同方式 |
|---------|---------|
| **twitter-cli** | Route 1 核心 |
| **x-reader** | 发布前内容分析 |
| **humanizer-zh** | 文案去AI味后发布 |

## 预期收益

| 指标 | 单路线 | 双路线 | 提升 |
|------|-------|--------|------|
| 发布成功率 | 95% | **99%** | +4% |
| 故障恢复时间 | 手动 | **自动** | 质的飞跃 |
| 发布延迟 | 基准 | **<5s** | 保持 |

## 版本历史

- **v1.0.0** (2026-03-13) - 双路线发布保障系统集成