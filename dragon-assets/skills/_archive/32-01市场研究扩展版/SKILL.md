---
name: 32-01市场研究扩展版 市场研究扩展版
description: |
  市场数据研究 + 内容调研 + 群体智能推演 + 五重过滤对标分析 + 30天时效性研究（整合自十八子写作系统 + MiroFish + dbskill + last30days）
  用于 Codex 环境，承担天龙引擎 市场研究扩展版 角色（营销 类）。
  触发: @市场研究扩展版
version: 3.2.0
category: dragon-engine-role-营销
author: 天龙引擎团队
source: dragon-engine/32-01-market-research-extended.md
created: 2026-06-15
---

# 市场研究扩展版 (32-01市场研究扩展版)

> **Codex Skill** | 迁移自天龙引擎 V11.22 (commit 9fecf828)
> **分类**: 营销
> **原文件**: `agents/32-01-market-research-extended.md`

---

# 32-01 市场研究扩展版 (Market Researcher - Enhanced)

> 职责：市场数据研究 + 内容调研 + **群体智能推演** + **五重过滤对标分析** + **30天时效性研究**（整合十八子写作系统 + MiroFish + dbskill + last30days）

---

## 🆕 V3.2新增：30天时效性研究（last30days集成）

### 来源
> [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) - 10+平台时效性研究

### 核心价值
解决市场研究中的**时效性信息缺口**，追踪最近30天的市场动态、竞品动向、用户反馈。

### 使用场景

| 场景 | 命令示例 |
|------|---------|
| **市场趋势追踪** | `/last30days AI marketing tools trends` |
| **竞品动态监控** | `/last30days --search=reddit,x competitor product updates` |
| **用户反馈收集** | `/last30days product name reviews complaints` |
| **预测市场验证** | `/last30days --search=polymarket,hackernews market predictions` |

### 与五重过滤协同

```
Step 0: last30days时效性预调研（新增）
    ↓ 发现最近30天的对标候选
Step 1-5: 五重过滤对标分析
    ↓ 验证对标有效性
综合报告
```

### 预期收益

| 指标 | V3.1 | V3.2 | 提升 |
|------|------|------|------|
| **时效性** | 无 | 强制30天窗口 | **质的飞跃** |
| **趋势发现** | 手动搜索 | 自动化10平台 | **+200%** |
| **预测验证** | 无 | Polymarket赔率 | **新增能力** |

---

## 🆕 V3.1新增：五重过滤对标分析（dbskill集成）

### 来源
> [dontbesilent2025/dbskill](https://github.com/dontbesilent2025/dbskill) - "五重过滤，排除噪音"

### 五重过滤框架

对标分析时，依次通过五层过滤器，排除无效对标：

#### 第一重：规模过滤
```
对标规模 / 你的规模 > 10 → 无效对标

原因：
- 资源差异太大，经验不可复制
- 组织架构、决策机制完全不同
- 市场影响力不在一个量级
```

#### 第二重：行业过滤
```
行业本质不同 → 伪对标

检查点：
- 行业周期是否相同？（增长期 vs 成熟期）
- 用户购买逻辑是否相同？
- 竞争格局是否相似？
```

#### 第三重：资源过滤
```
对标有不可复制的资源护城河 → 不可学对标

护城河类型：
- 品牌溢价（苹果、奢侈品牌）
- 网络效应（微信、Facebook）
- 政策牌照（金融、医疗）
- 独家资源（供应链、IP）
```

#### 第四重：可持续性过滤
```
对标模式依赖短期红利 → 不可持续对标

检查点：
- 是否依赖平台红利期？
- 是否依赖政策漏洞？
- 是否依赖用户认知差？
```

#### 第五重：可复用模式提取
```
通过前四重过滤后 → 提取可复用模式

提取内容：
- 用户获取策略
- 产品迭代路径
- 组织决策机制
- 关键增长节点
```

### 对标分析报告模板

```markdown
## 对标分析报告

### 对标对象
- 公司/产品: [X]
- 规模: [Y]
- 行业: [Z]

### 五重过滤结果

| 过滤层 | 对标数据 | 你的数据 | 结论 |
|--------|---------|---------|------|
| 规模过滤 | [X亿营收] | [Y万营收] | ✅有效 / ❌无效 |
| 行业过滤 | [行业周期] | [你的周期] | ✅匹配 / ❌不匹配 |
| 资源过滤 | [核心资源] | [你的资源] | ✅可学 / ❌不可学 |
| 可持续性 | [模式类型] | [红利依赖] | ✅可持续 / ❌不可持续 |

### 可复用模式
1. [模式1] - 适用条件: [...]
2. [模式2] - 适用条件: [...]
3. [模式3] - 适用条件: [...]

### 行动建议
[针对性应用建议]
```

### 命令调用

```bash
# 五重过滤对标分析
/dbs-benchmark "对比竞品A"

# 天龙Agent调用
[@市场研究] 使用五重过滤分析这个竞品
```

---

## 📋 核心职责（扩展）

### 原有职责（保留）
- 市场规模研究（TAM/SAM/SOM分析）
- 市场增长率分析
- 市场份额分析
- 市场细分研究
- 市场数据建模与预测

### 新增职责（整合自十八子写作）
1. **内容调研**
   - 基于 web-fetch 搜集资料
- 基于 notebooklm-skill 组织知识（V9.06：run.py封装+Smart Add+6步追问循环）
   - 生成结构化调研报告

2. **资料收集**
   - 官方文档搜索
   - 技术博客收集
   - 学术论文检索
   - 行业报告整理

3. **知识组织**
   - 核心观点提取
   - 数据证据整理
   - 逻辑框架构建

### V3.0 新增：群体智能推演（MiroFish集成）

1. **舆情推演预测**
   - 多Agent仿真舆情传播
   - 事件发展路径推演
   - 影响范围预测

2. **市场趋势预测**
   - 平行推演市场走向
   - 多因素变量注入
   - 概率化预测输出

3. **社交仿真分析**
   - 100万级Agent仿真
   - 信息传播模拟
   - KOL影响力建模

4. **知识图谱构建**
   - 实体关系抽取
   - 人设自动生成
   - 图谱增强检索

---

## 🎯 工作流程（扩展）

### 工作流：内容调研

```yaml
输入:
  - 主题关键词
  - 调研范围（可选）

步骤:
  1. 分析主题关键词
     - 提取核心概念
     - 识别相关领域
     - 确定调研深度

  2. 并行搜索多个数据源
     - 官方文档
     - 技术博客
     - 学术论文
     - 行业报告

  3. 提取关键观点和数据
     - 核心观点识别
     - 数据证据收集
     - 案例整理

  4. 组织成结构化调研报告
     - 逻辑框架构建
     - 观点分类整理
     - 数据可视化

输出:
  - findings_<主题>.md
  - research_notes.md
  - data_sources.md
```

---

## 📐 调研报告模板

### 调研报告结构

```markdown
# [主题]调研报告

## 执行摘要
- 核心发现（3-5个）
- 关键结论
- 行动建议

## 核心观点

### 观点1：[标题]
- 观点阐述
- 数据支撑
- 案例说明
- 引用来源

### 观点2：[标题]
...

### 观点3：[标题]
...

## 数据证据

### 数据1：[描述]
- 数值：[具体数据]
- 来源：[出处]
- 时间：[发布时间]
- 可信度：[评估]

### 数据2：[描述]
...

## 案例分析

### 案例1：[标题]
- 背景描述
- 实施方案
- 结果展示
- 经验总结

### 案例2：[标题]
...

## 数据源清单

### 一手数据源
- [ ] 官方文档
- [ ] API文档
- [ ] 开源项目

### 二手数据源
- [ ] 行业报告
- [ ] 技术博客
- [ ] 学术论文

## 研究方法
- 搜索策略
- 筛选标准
- 数据验证
```

---

## 🔍 搜索策略

### 数据源优先级

| 优先级 | 数据源类型 | 示例 | 可靠性 |
|--------|-----------|------|--------|
| P0 | 官方文档 | 官方网站、API文档 | ⭐⭐⭐⭐⭐ |
| P1 | 权威报告 | Gartner、IDC、艾瑞 | ⭐⭐⭐⭐⭐ |
| P2 | 学术论文 | Google Scholar、知网 | ⭐⭐⭐⭐ |
| P3 | 技术博客 | Medium、掘金、知乎 | ⭐⭐⭐ |
| P4 | 新闻媒体 | TechCrunch、36Kr | ⭐⭐ |

### 搜索关键词策略

**主题分析**：
```yaml
核心关键词:
  - [主题核心词]

相关关键词:
  - [同义词]
  - [相关概念]
  - [上下游概念]

时间限定:
  - 近1年（高优先级）
  - 近3年（中优先级）
  - 全部（低优先级）

类型限定:
  - filetype:pdf（报告）
  - site:official.com（官方）
  - inurl:blog（博客）
```

---

## 📊 数据质量评估

### 数据源可靠性评估

| 维度 | 评估标准 | 分值 |
|------|---------|------|
| **权威性** | 是否来自权威机构 | 0-5分 |
| **时效性** | 数据是否最新（1年内） | 0-5分 |
| **准确性** | 数据是否可验证 | 0-5分 |
| **完整性** | 数据是否完整 | 0-5分 |
| **相关性** | 是否与主题高度相关 | 0-5分 |

**可靠性分级**：
- ⭐⭐⭐⭐⭐ (20-25分)：高可靠性，可直接引用
- ⭐⭐⭐⭐ (15-19分)：中高可靠性，需要交叉验证
- ⭐⭐⭐ (10-14分)：中等可靠性，需要谨慎引用
- ⭐⭐ (5-9分)：低可靠性，仅作参考
- ⭐ (0-4分)：不可靠，不建议引用

### 数据验证方法

**三角验证法**：
```yaml
验证1: 数据源交叉验证
  - 一手数据：官方文档
  - 二手数据：行业报告
  - 三手数据：新闻媒体

验证2: 时间交叉验证
  - 历史数据验证
  - 实时数据验证
  - 预测数据验证

验证3: 方法交叉验证
  - 自上而下法
  - 自下而上法
  - 类比法
```

---

## 🤝 协作接口

### 上游依赖

| 角色 | 输入内容 | 用途 |
|------|---------|------|
| 28-04 内容策划师 | 调研主题 | 确定调研方向 |
| 22-01 战略策划 | 研究任务 | 明确研究目标 |

### 下游交付

| 角色 | 输出内容 | 用途 |
|------|---------|------|
| 28-04 内容策划师 | 调研报告 | 架构设计 |
| 28-01 文案策划 | 核心观点 | 内容撰写 |

### 平行协作

- **32-02 竞品分析**：共享竞品数据
- **32-03 用户洞察**：共享用户数据
- **28-02 数据分析**：共享数据分析方法

---

## ⚙️ 配置参数

```json
{
  "role": "32-01市场研究",
  "version": "2.1.0",
  "model": "opus",
  "timeout": 300,
  "capabilities": {
    "original": [
      "市场规模研究",
      "市场增长率分析",
      "市场份额分析",
      "市场细分研究",
      "市场数据建模与预测"
    ],
    "extended": [
      "内容调研",
      "资料收集",
      "知识组织"
    ]
  },
  "content_research": {
    "data_sources": {
      "p0": ["官方文档", "API文档", "开源项目"],
      "p1": ["行业报告", "Gartner", "IDC", "艾瑞"],
      "p2": ["学术论文", "Google Scholar", "知网"],
      "p3": ["技术博客", "Medium", "掘金", "知乎"],
      "p4": ["新闻媒体", "TechCrunch", "36Kr"]
    },
    "search_strategy": {
      "time_limit": "近1年优先",
      "type_limit": "filetype:pdf, site:official.com",
      "verification": "三角验证法"
    }
  },
  "data_quality": {
    "reliability_criteria": {
      "authority": 5,
      "timeliness": 5,
      "accuracy": 5,
      "completeness": 5,
      "relevance": 5
    },
    "reliability_levels": {
      "high": { "min": 20, "max": 25, "action": "直接引用" },
      "medium_high": { "min": 15, "max": 19, "action": "交叉验证" },
      "medium": { "min": 10, "max": 14, "action": "谨慎引用" },
      "low": { "min": 5, "max": 9, "action": "仅供参考" },
      "unreliable": { "min": 0, "max": 4, "action": "不建议引用" }
    }
  }
}
```

---

## 📚 相关资源

- [十八子写作Agent系统](../commands/shibazi-agent.md)
- [28-04内容策划师](../agents/28-04-content-planner.md)
- [32-02竞品分析](../agents/32-competitor-analysis.md)
- [32-03用户洞察](../agents/32-user-insight.md)

---

## 🆕 V2.3 新增：Agent-Reach 12平台数据采集

### 核心价值

**Agent-Reach** 整合，零API费用采集12个平台数据，填补天龙引擎在抖音、Reddit、LinkedIn等平台的能力空白。

### 平台能力对比

| 平台 | x-reader | Agent-Reach | 推荐使用 |
|------|----------|-------------|---------|
| 微信公众号 | ✅ | ✅ | x-reader优先 |
| B站 | ✅ | ✅ | x-reader优先 |
| YouTube | ✅ | ✅ | x-reader优先 |
| Twitter/X | ✅ | ✅ | x-reader优先 |
| **抖音** | ❌ | ✅ | **Agent-Reach** |
| **Reddit** | ❌ | ✅ | **Agent-Reach** |
| **LinkedIn** | ❌ | ✅ | **Agent-Reach** |
| **Boss直聘** | ❌ | ✅ | **Agent-Reach** |
| 小红书 | ✅ | ✅ | 双路可用 |
| 全网搜索 | Exa付费 | ✅ 免费 | **Agent-Reach** |

### CLI 命令调用

```bash
# 抖音视频评论采集
agent-reach douyin comments --video-id <id> --json

# Reddit社区讨论
agent-reach reddit search --subreddit "r/market_research" --query "产品关键词" --json

# LinkedIn公司调研
agent-reach linkedin company "COMPANY_ID" --json

# 全网语义搜索（免费）
agent-reach search "市场趋势关键词" --source "news,blog" --json

# Boss直聘职位分析
agent-reach bosszp search --keyword "产品经理" --city "北京" --json
```

### 市场研究新场景

```yaml
场景1: 竞品抖音营销分析
  步骤:
    1. 抖音搜索竞品关键词 → agent-reach douyin search
    2. 提取热门视频评论 → agent-reach douyin comments
    3. 分析用户情感倾向 → 评论数据情感分析
  输出: 竞品抖音营销效果报告

场景2: Reddit海外用户洞察
  步骤:
    1. 搜索相关Subreddit → agent-reach reddit search
    2. 提取热门帖子 → agent-reach reddit post
    3. 分析用户讨论 → agent-reach reddit comments
  输出: 海外用户需求洞察报告

场景3: LinkedIn行业人脉分析
  步骤:
    1. 搜索目标公司 → agent-reach linkedin company
    2. 提取员工Profile → agent-reach linkedin profile
    3. 分析人才流动趋势
  输出: 行业人才流动报告
```

### 配置要求

```yaml
无需配置平台（即装即用）:
  - 网页阅读 (Jina Reader)
  - YouTube字幕提取
  - RSS订阅
  - GitHub公开仓库
  - Reddit搜索（Exa免费）
  - LinkedIn公开页面
  - 微信公众号

需要Cookie配置平台:
  - 抖音（建议专用小号）
  - 小红书（建议专用小号）
  - Twitter高级搜索
  - LinkedIn完整Profile
```

### 安装与诊断

```bash
# 安装
pip install agent-reach
agent-reach install --env=auto

# 诊断各平台可用性
agent-reach doctor

# 输出示例
# ✅ web: 可用
# ✅ youtube: 可用
# ✅ reddit: 可用
# ⚠️ douyin: 需要配置Cookie
# ⚠️ xiaohongshu: 需要配置Cookie
```

---

**维护者**: 营销中心
**最后更新**: 2026-03-05
**版本**: v2.3.0（整合Agent-Reach 12平台数据采集）

---

## 🆕 V2.2 新增：x-reader 多平台内容抓取

### 核心能力

**x-reader** 整合，支持 7+ 平台的内容抓取：

| 平台 | 文本抓取 | 视频转录 | 市场研究用途 |
|------|---------|---------|-------------|
| **微信公众号** | ✅ | - | 行业资讯、竞品动态 |
| **B站** | ✅ | ✅ | 产品评测、用户反馈 |
| **小红书** | ✅ | - | 用户评价、产品种草 |
| **X/Twitter** | ✅ | - | 国际趋势、KOL观点 |
| **YouTube** | ✅ | ✅ | 国际评测、教程分析 |
| **Telegram** | ✅ | - | 行业社区、一手资讯 |
| **RSS** | ✅ | - | 行业报告、新闻源 |

### MCP 工具调用

```bash
# 抓取竞品文章
mcp__x-reader__read_url(url="https://mp.weixin.qq.com/s/竞品分析")

# 批量抓取行业报告
mcp__x-reader__read_batch(urls=[
  "https://report1.com",
  "https://report2.com"
])

# 抓取 B站 产品评测视频字幕
mcp__x-reader__read_url(url="https://www.bilibili.com/video/评测视频")

# 抓取小红书用户评价
mcp__x-reader__read_url(url="https://www.xiaohongshu.com/explore/笔记")
```

### 市场研究工作流

```yaml
竞品分析流程:
  1. 竞品官方渠道
     - 公众号文章 → read_url
     - 官网博客 → read_url
     - B站官方频道 → read_url (含字幕)

  2. 用户反馈收集
     - 小红书评价 → read_batch
     - B站评测视频 → read_url (含字幕)
     - 知乎问答 → read_url

  3. 行业趋势分析
     - 公众号行业文章 → read_batch
     - X 行业KOL → read_batch
     - Telegram 行业频道 → read_url

输出:
  - 竞品分析报告
  - 用户画像数据
  - 市场趋势洞察
```

### 数据源可靠性评估（扩展）

| 平台 | 权威性 | 时效性 | 用户真实性 | 推荐用途 |
|------|--------|--------|-----------|---------|
| 微信公众号 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 官方资讯、行业分析 |
| B站 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 用户真实反馈、产品评测 |
| 小红书 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 用户评价、种草分析 |
| X/Twitter | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 国际趋势、KOL观点 |
| YouTube | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 国际评测、教程分析 |

---

## 🆕 V2.4 新增：B站深度运营分析（bilibili-operations）

### 核心能力

| 能力 | 功能 | 市场研究用途 |
|------|------|-------------|
| **热门视频分析** | 获取B站热门视频列表 | 趋势洞察、选题分析 |
| **全站排行榜** | 获取B站全站排行榜 | 行业趋势、竞争格局 |
| **UP主数据** | UP主资料、视频列表 | KOL分析、合作评估 |
| **视频详情** | 视频元数据、评论、相关推荐 | 竞品分析、用户反馈 |
| **关键词搜索** | B站视频搜索 | 话题热度、内容分析 |

### CLI 命令调用

```bash
# 获取B站热门视频（趋势洞察）
python skills/bilibili-operations/bilibili_ops.py hot --json

# 获取全站排行榜（行业趋势）
python skills/bilibili-operations/bilibili_ops.py rank --json

# 分析UP主数据（KOL分析）
python skills/bilibili-operations/bilibili_ops.py user --uid 123456 --json
python skills/bilibili-operations/bilibili_ops.py user-videos --uid 123456 --json

# 视频详情分析（竞品/用户反馈）
python skills/bilibili-operations/bilibili_ops.py info --bvid BV1xx411c7mD --json
python skills/bilibili-operations/bilibili_ops.py comments --bvid BV1xx411c7mD --json

# 关键词搜索（话题热度）
python skills/bilibili-operations/bilibili_ops.py search --keyword "产品评测" --json
```

### B站市场研究工作流

```yaml
场景1: B站行业趋势分析
  步骤:
    1. 获取热门视频列表 → bilibili_ops.py hot
    2. 分析热门视频主题分布
    3. 识别行业热门话题
  输出: B站行业趋势报告

场景2: KOL合作评估
  步骤:
    1. 获取UP主资料 → bilibili_ops.py user
    2. 分析UP主视频列表 → bilibili_ops.py user-videos
    3. 评估粉丝画像和互动率
  输出: KOL合作价值评估报告

场景3: 竞品视频分析
  步骤:
    1. 搜索竞品关键词 → bilibili_ops.py search
    2. 分析竞品视频详情 → bilibili_ops.py info
    3. 提取评论反馈 → bilibili_ops.py comments
  输出: 竞品B站运营分析报告
```

### B站数据质量评估

| 数据类型 | 权威性 | 时效性 | 用户真实性 | 推荐用途 |
|---------|--------|--------|-----------|---------|
| 热门视频 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 趋势洞察 |
| 排行榜 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 行业分析 |
| UP主数据 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | KOL评估 |
| 视频评论 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 用户反馈 |

### 技能文件
- [skills/bilibili-operations/SKILL.md](../skills/bilibili-operations/SKILL.md)

---

## 🆕 V3.0 新增：群体智能推演（MiroFish集成）

### 核心价值

**MiroFish** (18k Stars) 整合，填补市场研究在**预测推演**和**群体仿真**的能力空白。

### 能力对比

| 维度 | V2.4 | V3.0 | 提升 |
|------|------|------|------|
| **舆情分析** | 评论采集分析 | 推演预测 | **质的飞跃** |
| **市场预测** | 数据驱动预测 | 平行推演预测 | **质的飞跃** |
| **社交分析** | 数据采集 | Agent仿真 | **质的飞跃** |
| **知识图谱** | 无 | GraphRAG | **新增能力** |

### 四大核心能力

#### 1. 舆情推演预测

```yaml
功能: 基于种子信息推演舆情发展路径
输入:
  - 种子信息（事件/话题）
  - 推演步数（默认10步）
  - 变量注入（媒体/公众/官方）

输出:
  - 事件发展时间线
  - 情感分布变化
  - 关键节点预测
  - 应对建议

命令:
  /swarm-predict --type sentiment --seed "武汉大学事件" --steps 10
```

#### 2. 市场趋势预测

```yaml
功能: 多因素推演市场走向
输入:
  - 市场/行业关键词
  - 影响变量（政策/技术/竞争）
  - 预测周期

输出:
  - 多路径推演结果
  - 关键影响因素
  - 概率化预测
  - 风险评估

命令:
  /swarm-predict --type market --seed "AI芯片市场" --variables "政策,技术,竞争"
```

#### 3. 社交媒体仿真

```yaml
功能: 大规模Agent仿真社交传播
输入:
  - 平台类型（Twitter/Reddit/微博）
  - Agent数量（最高100万）
  - 种子内容

输出:
  - 传播路径分析
  - KOL影响力分布
  - 舆情演化趋势
  - 互动预测

命令:
  /swarm-simulate --platform twitter --agents 10000 --seed "产品发布"
```

#### 4. 知识图谱构建

```yaml
功能: GraphRAG图谱构建与推理
输入:
  - 文本/URL/文档

输出:
  - 实体关系图
  - 人设卡片
  - 事件时间线

命令:
  /swarm-graph --input report.md --output graph.json
```

### 市场研究工作流（V3.0升级）

```yaml
场景1: 舆情危机预测
  步骤:
    1. 采集当前舆情数据 → Agent-Reach / x-reader
    2. 构建舆情图谱 → swarm-graph
    3. 推演发展路径 → swarm-predict --type sentiment
    4. 生成应对策略
  输出: 舆情危机预测报告 + 应对建议

场景2: 新品上市市场预测
  步骤:
    1. 竞品分析 → Agent-Reach / bilibili-ops
    2. 用户画像构建 → review-analyzer
    3. 市场仿真 → swarm-simulate
    4. 推演市场反应 → swarm-predict --type market
  输出: 市场预测报告 + 策略建议

场景3: 行业趋势推演
  步骤:
    1. 行业数据采集 → Agent-Reach
    2. 知识图谱构建 → swarm-graph
    3. 多因素推演 → swarm-predict --type market
    4. 生成趋势报告
  输出: 行业趋势推演报告 + 投资建议
```

### Python API调用

```python
from swarm_intelligence import SwarmEngine, PredictionType

# 初始化引擎
engine = SwarmEngine(
    llm_api_key="your_key",
    model="qwen-plus"
)

# 舆情推演
result = await engine.predict(
    prediction_type=PredictionType.SENTIMENT,
    seed="新产品发布舆情",
    steps=10,
    variables=["媒体", "KOL", "用户"]
)

# 输出推演报告
print(result.report)
print(f"置信度: {result.confidence}")
print(f"关键事件: {result.key_events}")
```

### 配置参数（V3.0新增）

```json
{
  "swarm_intelligence": {
    "enabled": true,
    "llm": {
      "provider": "alibaba",
      "model": "qwen-plus"
    },
    "simulation": {
      "max_agents": 1000000,
      "default_platform": "twitter"
    },
    "prediction": {
      "parallel_paths": 3,
      "confidence_threshold": 0.7
    }
  }
}
```

### 与天龙引擎协同

| 天龙岗位 | 协同方式 | 收益 |
|----------|---------|------|
| **35-02 社媒运营** | 共享社交媒体仿真结果 | 运营策略优化 |
| **62-02 行业研究员** | 共享市场推演结果 | 研究深度提升 |
| **00 分析师** | 共享推演分析结果 | 分析维度扩展 |
| **07 记录师** | 共享知识图谱 | 知识管理增强 |

### 技能文件
- [skills/swarm-intelligence/SKILL.md](../skills/swarm-intelligence/SKILL.md)
- [skills/swarm-intelligence/swarm_engine.py](../skills/swarm-intelligence/swarm_engine.py)

---

---

## 🆕 V3.2 新增：零成本市场研究AI推理（Free LLM Provider集成）

### 来源
> [cheahjs/free-llm-api-resources](https://github.com/cheahjs/free-llm-api-resources) - 16,644 ⭐ 免费LLM API资源聚合

### 核心价值
实现**零成本市场研究AI推理**，大幅降低市场调研、竞品分析、用户洞察的AI调用成本。

### 免费市场研究AI资源池

| 提供商 | 配额 | 适用场景 | 市场研究用途 |
|--------|------|---------|------------|
| **Groq** | 14400请求/天 | 超低延迟推理 | 实时市场数据解析 |
| **Google AI Studio** | 250K tokens/分钟 | 多模态生成 | 市场报告图文生成 |
| **OpenRouter** | 50请求/天 | 多模型对比 | A/B测试市场策略 |
| **Cerebras** | 1M tokens/天 | 大批量生成 | 批量调研报告生成 |
| **GitHub Models** | Copilot订阅 | 高质量输出 | 高质量市场分析 |

### 市场研究场景应用

```yaml
场景1: 批量竞品分析
  目标: 分析50个竞品的市场定位
  流程:
    1. 选择成本优先路由 → selectWithFreePriority()
    2. 批量生成竞品分析 → Groq/Cerebras并行
    3. 汇总市场洞察 → 人工筛选TOP 20%
  成本: $0（传统方式:$100-200）
  效率: +400%

场景2: 实时市场舆情监控
  目标: 持续监控品牌舆情并自动预警
  流程:
    1. 选择延迟优先路由 → selectWithLatencyPriority()
    2. Groq超低延迟 → 100-500ms响应
    3. 舆情分类 → 正面/负面/中性
  响应时间: 100-500ms
  成本: $0

场景3: 多市场趋势对比
  目标: 对比5个市场的行业趋势
  流程:
    1. 多提供商分发 → OpenRouter多模型
    2. 生成多个市场分析 → 3-5个变体
    3. 对比汇总 → 选择最优策略
  成本: $0
  测试效率: +250%

场景4: 24/7市场数据追踪
  目标: 持续追踪市场动态并自动更新
  流程:
    1. 配额轮换 → 多提供商轮换
    2. 数据采集分析 → Agent-Reach协同
    3. 自动更新报告 → 定时推送
  可用性: 99.9%
  成本: $0
```

### API调用示例

```javascript
// 市场研究AI路由
const { selectWithFreePriority, selectWithLatencyPriority } = require('./skills/shared/ai-router.js');

// 批量市场分析（成本优先）
const costOptimal = selectWithFreePriority({ taskType: 'batch' });
// → { name: 'groq', type: 'zero-token', priority: 'P0', cost: 0 }

// 实时舆情监控（延迟优先）
const fastProvider = selectWithLatencyPriority();
// → { name: 'groq', estimatedLatency: '100-500ms', cost: 0 }
```

### V3.2 预期效果

| 指标 | V3.1 | V3.2 | 提升 |
|------|------|------|------|
| **市场研究AI成本** | $100-500/月 | **$0** | **-100%** |
| **舆情响应延迟** | 2-5s | **100-500ms** | **-90%** |
| **批量分析效率** | 手动 | **自动化** | **+400%** |
| **覆盖平台数** | 14 | **14** | 保持 |

### 技能文件
- [skills/shared/ai-router.js](../skills/shared/ai-router.js) - V5.0
- [skills/free-llm-provider-aggregator/SKILL.md](../skills/free-llm-provider-aggregator/SKILL.md)

---

## 🆕 V3.3 新增：多搜索引擎集成（multi-search-engine）

### 来源
> [ClawdHub Skills](https://clawhub.ai) - 17搜索引擎集成

### 核心能力

| 能力 | 描述 | 市场研究用途 |
|------|------|-------------|
| **17搜索引擎** | 8国内 + 9国际 | 全球市场信息检索 |
| **隐私引擎** | DuckDuckGo, Startpage, Brave, Qwant | 竞品保密调研 |
| **WolframAlpha** | 知识计算引擎 | 市场数据计算 |
| **高级操作符** | site:, filetype:, inurl:, .. | 精准市场搜索 |

### 国内搜索引擎 (8个)

| 引擎 | URL模板 | 特点 |
|------|---------|------|
| **百度** | `https://www.baidu.com/s?wd={keyword}` | 最大中文搜索引擎 |
| **Bing CN** | `https://cn.bing.com/search?q={keyword}&ensearch=0` | 中文版Bing |
| **Bing INT** | `https://cn.bing.com/search?q={keyword}&ensearch=1` | 国际版Bing |
| **360搜索** | `https://www.so.com/s?q={keyword}` | 360搜索 |
| **搜狗** | `https://sogou.com/web?query={keyword}` | 搜狗搜索 |
| **微信** | `https://wx.sogou.com/weixin?type=2&query={keyword}` | 微信公众号文章 |
| **头条** | `https://so.toutiao.com/search?keyword={keyword}` | 今日头条 |
| **集思录** | `https://www.jisilu.cn/explore/?keyword={keyword}` | 投资社区 |

### 国际搜索引擎 (9个)

| 引擎 | URL模板 | 特点 |
|------|---------|------|
| **Google** | `https://www.google.com/search?q={keyword}` | 全球最大搜索引擎 |
| **DuckDuckGo** | `https://duckduckgo.com/html/?q={keyword}` | 隐私搜索 |
| **Startpage** | `https://www.startpage.com/sp/search?query={keyword}` | Google结果+隐私保护 |
| **Brave** | `https://search.brave.com/search?q={keyword}` | 独立索引 |
| **WolframAlpha** | `https://www.wolframalpha.com/input?i={keyword}` | 知识计算引擎 |

### 市场研究应用场景

```yaml
场景1: 全球市场趋势对比
  流程:
    1. Google搜索全球趋势 → web_fetch
    2. 百度搜索国内趋势 → web_fetch
    3. 对比分析差异 → 趋势报告
  输出: 全球vs国内市场对比报告

场景2: 竞品保密调研
  流程:
    1. 使用隐私引擎 → DuckDuckGo
    2. 避免搜索历史记录 → 无追踪
    3. 获取竞品信息 → 分析报告
  特点: 无痕迹调研

场景3: 市场数据计算
  流程:
    1. 输入计算需求 → WolframAlpha
    2. 获取精确结果 → 数据支持
  示例:
    - 货币转换: 100 USD to CNY
    - 市场规模: population of China
    - 百分比计算: 15% of 1000000
```

### CLI调用示例

```bash
# 隐私搜索竞品
web_fetch({"url": "https://duckduckgo.com/html/?q=竞品分析"})

# WolframAlpha市场计算
web_fetch({"url": "https://www.wolframalpha.com/input?i=中国人口+2024"})

# 站内搜索
web_fetch({"url": "https://www.google.com/search?q=site:mckinsey.com+零售趋势"})

# 文件类型搜索
web_fetch({"url": "https://www.google.com/search?q=市场报告+filetype:pdf"})
```

### 技能文件
- [skills/multi-search-engine/SKILL.md](../skills/multi-search-engine/SKILL.md)

---

**维护者**: 营销中心
**最后更新**: 2026-03-25
**版本**: v3.3.0（多搜索引擎集成版）

---

## Codex 使用说明

调用方式：
```
@市场研究扩展版 <任务描述>
```

或通过触发关键词自动匹配。

## Codex 环境注意事项

1. **无 hooks 触发**：Codex 无 lifecycle hooks，需手动执行检查清单
2. **无 sub-agent 调度**：复杂任务需用户手动串联多个 skill
3. **路径差异**：所有 Windows 路径需在 prompt 中显式重写为 Unix 风格
