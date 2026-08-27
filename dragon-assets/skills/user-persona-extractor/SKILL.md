---
name: user-persona-extractor
description: 当用户使用 `/画像`、`/persona` 命令，或需要提取关键词的用户画像数据、分析受众特征、获取地域/年龄/性别分布时使用此skill。从多个数据源（百度指数、抖音指数、微信指数、5118 API等）提取用户画像数据，包括地域分布、年龄分布、性别分布、内容偏好等维度，生成详细的用户画像报告和可视化图表。支持关键词查询、多数据源聚合、HTML 可视化输出。
github_url: https://github.com/anthropics/skills/tree/main/skills/user-persona-extractor
github_hash: 5128e1865d670f5d6c9cef000e6dfc4e951fb5b9
github_repo: anthropics/skills
license: MIT
metadata: 
version: 2.0.0
author: Claude
created: 2026-02-26
category: analytics
domain: user-research
updated: 2025-01-15
python-tools: persona_aggregator.py, report_generator.py
tech-stack: Python, MCP-Chrome-DevTools, data-visualization, web-scraping
triggers: ["user persona extractor", "用户画像提取器"]
---
# 用户画像提取器

## Overview

通过百度指数智能提取关键词的用户画像数据，包括地域分布、年龄分布、性别分布、兴趣偏好等维度，生成详细的分析报告和可视化图表。

**数据来源：百度指数（已配置登录状态）、抖音指数（头条指数已整合到抖音平台）**

## When to Use

### 触发条件

**使用 Slash Command（推荐）：**
```
/画像 企业培训
/persona SaaS软件
/画像 新能源汽车 --source=baidu,douyin
```

**自然语言触发：**
- "提取'企业培训'的用户画像"
- "分析'SaaS软件'的受众特征"
- "查看'新能源汽车'的用户年龄和地域分布"
- "生成'在线教育'的用户画像报告"
- "对比两个关键词的用户画像"

### 适用场景

- 内容创作前的受众分析
- 广告投放前的用户研究
- 产品定位和目标用户分析
- 竞品用户画像对比
- 市场调研和趋势分析

### 何时不使用

- 纯粹搜索内容信息（使用 WebSearch 即可）
- 分析国外平台数据（本技能专注中国平台）
- 不需要详细画像的简单统计

## Workflow

### 完整工作流程

```
1. 用户输入关键词
    ↓
2. 并行访问百度指数和抖音指数
    ↓
3. 从两个数据源提取人群画像数据
    ↓
4. 聚合多数据源（加权平均）
    ↓
5. 生成报告和可视化
    ↓
6. 保存结果文件并自动打开 HTML 报告
```

### 详细步骤

#### 步骤 1：输入关键词

**必需参数：**
- `keyword`（关键词）：要分析的关键词

**可选参数：**
- `--source`（数据源）：默认 `baidu,douyin`（百度+抖音双数据源聚合）
  - 支持值：`baidu`（百度指数）、`douyin`（抖音指数，包含头条指数数据）、`baidu,douyin`（双数据源聚合）
  - 可使用逗号分隔多个数据源
- `--output`（输出格式）：报告格式，默认 `both`
  - 可选值：`markdown`、`html`、`both`

#### 步骤 2：获取用户画像数据

**数据源：百度指数、抖音指数（包含头条指数）**

| 数据源 | 状态 | 数据维度 | 获取方式 | 预计耗时 | 稳定性 |
|--------|------|----------|----------|----------|--------|
| **百度指数** | ✅ 使用中 | 年龄、性别、地域、兴趣 | 网页爬取 | 20-30秒 | ⭐⭐⭐ |
| **抖音指数** | ✅ 可用 | 年龄、性别、地域、兴趣 | 网页爬取 | 20-30秒 | ⭐⭐⭐ |

**百度指数配置：**
- 已配置登录状态（cookies已保存）
- 数据时效性：近30天
- 数据维度：年龄、性别、地域、兴趣

**抖音指数配置：**
- 头条指数已整合到抖音创作者中心
- URL: https://creator.douyin.com/creator-micro/creator-count/arithmetic-index
- 数据时效性：近30天
- 数据维度：年龄、性别、地域、兴趣
- 登录要求：需要抖音账号登录

#### 步骤 3：数据提取和标准化

**标准化流程：**
```python
# 统一数据格式
standardized_data = {
    'keyword': keyword,
    'source': '百度指数',
    'demographics': {
        'age': {},      # 年龄分布（≤19岁, 20-29岁, 30-39岁, 40-49岁, ≥50岁）
        'gender': {},   # 性别分布（男性、女性）
        'region': {},   # 地域分布（TOP10省份/城市）
        'interest': {}, # 兴趣分布（TOP10兴趣类别）
    },
    'timestamp': datetime.now().isoformat()
}
```

#### 步骤 4：用户画像分析

参考 [references/persona_framework.md](references/persona_framework.md)

**分析维度：**
1. **地域分布分析**
   - TOP 省份/城市排行
   - 地域渗透率

2. **年龄分布分析**
   - 年龄段分布（≤19岁, 20-29岁, 30-39岁, 40-49岁, ≥50岁）
   - 核心年龄段识别
   - TGI指数分析

3. **性别分布分析**
   - 性别比例
   - TGI指数分析

4. **兴趣偏好分析**
   - TOP 10 兴趣类别
   - TGI指数分析

#### 步骤 5：生成报告和可视化（HTML 自动打开）

**报告格式：**
- Markdown 报告：`~/persona-reports/[关键词]_[时间戳].md`
- HTML 可视化：`~/persona-reports/[关键词]_[时间戳].html` ← 自动在浏览器中打开
- CSV 数据：`~/persona-reports/[关键词]_[时间戳].csv`

## Quick Reference

### 数据源说明

| 数据源 | 状态 | 数据维度 | 获取方式 | 预计耗时 | 稳定性 |
|--------|------|----------|----------|----------|--------|
| **百度指数** | ✅ 使用中 | 年龄、性别、地域、兴趣 | 网页爬取 | 20-30秒 | ⭐⭐⭐ |
| **抖音指数** | ✅ 可用 | 年龄、性别、地域、兴趣 | 网页爬取 | 20-30秒 | ⭐⭐⭐ |
| **双源聚合** | ✅ 默认 | 全部维度（加权平均） | 并行爬取+聚合 | 30-50秒 | ⭐⭐⭐⭐ |

### 数据维度说明

| 维度 | 说明 |
|------|------|
| **地域分布** | TOP 10 省份/城市分布及占比 |
| **年龄分布** | 5个年龄段占比及 TGI 指数 |
| **性别分布** | 男性、女性占比及 TGI 指数 |
| **兴趣分布** | TOP 10 兴趣类别及 TGI 指数 |

### 画像分析框架

**核心用户群识别：**
```python
核心用户群 = {
    'primary_age': 占比最高的年龄段,
    'primary_gender': 占比最高的性别,
    'primary_regions': TOP3 地域,
    'primary_interests': TOP3 兴趣类别
}
```

## Output Format

### Markdown 报告结构

```markdown
# 用户画像分析报告 - {关键词}

## 📊 执行摘要
- 关键词：{keyword}
- 数据源：百度指数
- 分析时间：{timestamp}
- 核心发现：{key_findings}

## 👥 核心用户画像
- 主要年龄段：{primary_age}
- 性别比例：{gender_ratio}
- 核心地域：{top_regions}
- 主要兴趣：{top_interests}

## 🌍 地域分布分析
### TOP 10 省份

## 👶 年龄分布分析
### 年龄段分布图
### TGI 指数分析

## ⚧ 性别分布分析
### 性别比例
### TGI 指数分析

## 🎯 兴趣分布分析
### TOP 10 兴趣类别
### TGI 指数分析

## 💡 洞察与建议
### 用户特征洞察
### 内容策略建议
```

### HTML 可视化特性

- 使用 Chart.js 绘制交互式图表
- **生成后自动在浏览器中打开**
- 响应式设计，支持移动端查看
- 图表类型：
  - 柱状图+折线图：年龄分布（占比 + TGI指数）
  - 条形图：性别分布（占比 + TGI指数）
  - 柱状图：地域 TOP 10
  - 极坐标图：兴趣 TOP 10

## Common Mistakes

### 错误 1：忽略数据时效性
❌ 错误做法：使用过时的数据
✅ 正确做法：优先使用近 30 天数据，标注数据时间范围

### 错误 2：过度解读数据
❌ 错误做法：对小样本数据做绝对性结论
✅ 正确做法：标注数据量和置信度，给出参考性结论

## Tips

### 使用技巧

1. **关键词选择**：
   - 使用具体行业词（如"SaaS软件"而非"软件"）
   - 避免过于宽泛的词（如"生活"、"美食"）
   - 优先选择有搜索量的词

2. **报告解读**：
   - 关注核心用户群（占比 >30%）
   - 注意数据异常值（可能是数据质量问题）
   - 结合业务场景解读数据
   - TGI指数 >100 表示高于平均水平

### 常见问题

**Q: 为什么默认使用百度+抖音双数据源？**
A: 双数据源聚合可以提供更全面的用户画像。百度代表搜索引擎用户，抖音代表短视频用户，两者结合覆盖更广泛的人群。聚合算法使用加权平均（百度权重1.0，抖音权重0.9）来平衡数据质量。

**Q: 如何只使用单一数据源？**
A: 使用 `--source` 参数指定，如 `/画像 关键词 --source=baidu` 或 `/画像 关键词 --source=douyin`。

**Q: 头条指数去哪了？**
A: 头条指数已整合到抖音创作者中心，使用抖音指数数据源即可获取头条相关数据。

**Q: 分析需要多长时间？**
A: 单个数据源约 20-30 秒，多数据源会相应增加时间。

**Q: 数据准确性如何？**
A: 数据来源于各平台官方，反映真实搜索和用户行为，数据时效性为近 30 天。

**Q: 如何提高爬取成功率？**
A:
1. 控制爬取频率，避免批量请求
2. 保存登录状态，复用 cookies
3. 遇到验证码时手动处理

**Q: 抖音指数需要登录吗？**
A: 是的，需要抖音账号登录。首次使用需要在浏览器中扫码登录，之后可以保存 cookies 复用。

## Example Usage

### 示例 1：基础画像分析（默认双数据源）

```bash
用户：/画像 企业培训

Claude：
✅ 开始提取"企业培训"的用户画像（百度指数 + 抖音指数）...
[1/7] 打开百度指数页面...
[2/7] 从百度指数提取数据...
[3/7] 打开抖音指数页面...
[4/7] 从抖音指数提取数据...
[5/7] 聚合多数据源...
[6/7] 生成分析报告...
[7/7] 完成！

✅ 分析完成！

📊 数据源：百度指数、抖音指数（2个数据源聚合）

👥 核心用户画像：
• 主要年龄段：30-39岁（占 32%，聚合结果）
• 性别比例：女性 58%，男性 42%
• 核心地域：广东（16%）、江苏（11%）、山东（10%）
• 主要兴趣：影视娱乐（78%）、医疗健康（72%）、教育培训（68%）

📁 报告已保存到：
• Markdown: ~/persona-reports/企业培训_20250116_143025.md
• HTML: ~/persona-reports/企业培训_20250116_143025.html ← 自动在浏览器中打开
• CSV: ~/persona-reports/企业培训_20250116_143025.csv
```

### 示例 2：指定输出格式

```bash
用户：/persona SaaS软件 --output=html

Claude：
✅ 输出格式：HTML 可视化报告
...
```

### 示例 3：仅使用百度指数

```bash
用户：/画像 在线教育 --source=baidu

Claude：
✅ 数据源：仅百度指数
[1/6] 打开百度指数页面...
...
```

### 示例 4：仅使用抖音指数

```bash
用户：/persona 短视频 --source=douyin

Claude：
✅ 数据源：仅抖音指数
[1/6] 打开抖音指数页面...
...
```

### 示例 5：自定义双数据源

```bash
用户：/画像 新能源汽车 --source=baidu,douyin --output=html

Claude：
✅ 数据源：百度指数 + 抖音指数
✅ 输出格式：HTML 可视化报告
...
```

## Technical Details

### 技术栈

- **数据获取**：
  - MCP Chrome DevTools（网页自动化）

- **数据处理**：
  - 数据标准化和聚合

- **报告生成**：
  - Chart.js（HTML 可视化）
  - Tailwind CSS（样式）

- **HTML 自动打开**：
  - webbrowser 模块（Python 标准库）

### 依赖工具

- **MCP 工具**：
  - `mcp__chrome-devtools__*`（百度指数网页爬取）

## References

- [references/data_sources_guide.md](references/data_sources_guide.md) - 数据源详细使用指南
- [references/persona_framework.md](references/persona_framework.md) - 用户画像分析框架

## Configuration

### 基础配置

创建 `~/.persona-extractor/config.json`：

```json
{
  "data_source": {
    "name": "baidu,douyin",
    "enabled": true,
    "method": "scrape"
  },
  "scraper": {
    "timeout": 30000,
    "delay_min": 2000,
    "delay_max": 5000,
    "max_retries": 3
  },
  "output": {
    "directory": "~/persona-reports",
    "format": "both",
    "auto_open_html": true
  }
}
```

### Cookies 存储

创建 `~/.persona-extractor/cookies.json`：

```json
{
  "baidu": {
    "url": "https://index.baidu.com",
    "logged_in": true,
    "user_info": "创鑫电商学院",
    "cookies": [
      {"name": "XFI", "value": "...", "domain": ".baidu.com"},
      {"name": "BAIDUID", "value": "...", "domain": ".baidu.com"}
      // ... 14 cookies total
    ],
    "saved_at": "2025-01-16T16:37:06Z"
  },
  "douyin": {
    "url": "https://creator.douyin.com",
    "logged_in": false,
    "user_info": "",
    "cookies": [],
    "saved_at": null,
    "note": "头条指数已整合到抖音创作者中心，需要抖音账号登录"
  }
}
```

**当前状态**：
- 百度指数：Cookies 已配置，可直接使用
- 抖音指数：需要配置 cookies（使用时需要抖音账号登录）

**默认使用双数据源的原因**：
- **数据互补**：百度搜索用户 vs 抖音短视频用户，覆盖不同人群
- **提高准确性**：多源聚合降低单一平台偏差
- **更全面洞察**：结合搜索引擎和社交媒体数据
- **加权算法**：百度权重1.0，抖音权重0.9，自动平衡数据质量

## Related Skills

- **china-viral-content-analyzer** - 爆款内容分析，可结合用户画像
- **comment-analyzer** - 评论分析，可验证用户画像准确性
- **content-creator** - 基于用户画像生成内容策略

#### Evolution Pattern (Maintenance)

To preserve custom improvements when a core skill is upgraded, avoid editing `SKILL.md` directly for individual modifications. Instead:

1. Create or update an `evolution.json` file in the skill's root directory.
2. Store modification suggestions, custom rules, or evolved logic there.
3. This ensures that your custom "evolutions" are preserved even if the base `SKILL.md` is replaced during an upgrade.
