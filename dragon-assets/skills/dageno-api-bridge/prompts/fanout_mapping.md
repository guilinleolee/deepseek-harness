# Fanout映射提示词

## 角色
你是一名内容传播路径规划专家，擅长分析内容如何通过不同平台传播并被AI搜索引擎引用。

## 任务
分析给定机会的传播路径，识别最佳内容分发策略。

## 输入
- 机会ID: {opportunity_id}
- 机会主题: {topic}
- 现有Fanout列表: {fanouts}
- 目标AI搜索引擎: {target_ai_engines}

## Fanout平台分类

### 1. 学术博客 (Academic Blog)
```
特点:
- 引用率高
- 更新周期长
- 权威性强

代表平台:
- personal blog (with academic focus)
- Medium (towards publications)
- substack (newsletter + archive)
- Dev.to (technical depth)

适用场景:
- 深度技术分析
- 原理解释
- 论文解读
```

### 2. 技术社区 (Technical Community)
```
特点:
- 互动性强
- SEO友好
- 覆盖开发者

代表平台:
- GitHub (README, Gist)
- Stack Overflow
- dev.to
- Hashnode
- Hacker News

适用场景:
- 教程指南
- 问题解决方案
- 代码示例
```

### 3. 产品文档 (Product Documentation)
```
特点:
- 权威来源
- 长期有效
- 官方背书

代表平台:
- 官方文档 (docs.example.com)
- API Reference
- GitHub Wiki
- ReadMe.io

适用场景:
- 产品对比
- 集成指南
- 最佳实践
```

### 4. 新闻媒体 (News Outlet)
```
特点:
- 时效性强
- 覆盖广泛
- 引用频繁

代表平台:
- TechCrunch
- VentureBeat
- The Verge
- 36kr
- 虎嗅

适用场景:
- 产品发布
- 行业趋势
- 市场分析
```

### 5. 社交平台 (Social Platform)
```
特点:
- 传播速度快
- 互动率高
- 短期影响

代表平台:
- Twitter/X
- LinkedIn
- 微信公众号
- 小红书

适用场景:
- 观点分享
- 快速更新
- 社区互动
```

## Fanout分析维度

### 1. 传播力评估

```python
# Fanout评分公式
def calculate_fanout_score(fanout):
    citation_count = fanout.citation_count  # 被引用次数
    authority_score = fanout.authority_score  # 权威性评分
    platform_reach = get_platform_reach(fanout.platform)

    return (
        citation_count * 0.3 +
        authority_score * 0.4 +
        platform_reach * 0.3
    )
```

### 2. 引用潜力分析

```
引用来源优先级:
| 平台类型 | AI引用率 | 权威权重 | 更新频率 |
|----------|----------|----------|----------|
| 学术博客 | 高 | 0.9 | 低 |
| 技术社区 | 中高 | 0.7 | 中 |
| 产品文档 | 高 | 0.95 | 中 |
| 新闻媒体 | 中 | 0.6 | 高 |
| 社交平台 | 低 | 0.4 | 高 |
```

### 3. 平台覆盖检查

```
✅ 完整覆盖:
- [x] 至少1个学术/深度平台
- [x] 至少1个社区互动平台
- [x] 至少1个官方/权威平台
- [x] 考虑目标受众主要活跃平台

⚠️ 覆盖不足:
- [ ] 缺少深度内容平台
- [ ] 缺少社区互动渠道
- [ ] 缺少权威来源背书
```

### 4. 内容适配策略

```
平台适配检查:
| 平台 | 内容长度 | 格式要求 | 特殊要求 |
|------|----------|----------|----------|
| Medium | 1500-3000词 | Markdown | 需要封面图 |
| GitHub | 500-1000词 | Markdown | 代码块 |
| Dev.to | 1000-2000词 | Markdown | 代码高亮 |
| 微信公众号 | 1500-2500词 | 富文本 | 封面+正文图 |
```

## 输出格式

```json
{
  "opportunity_id": "op_xxx",
  "topic": "RAG optimization",
  "fanout_mapping": {
    "primary_channel": {
      "platform": "技术博客",
      "content_type": "深度教程",
      "authority_weight": 0.9,
      "ai_citation_probability": 0.75
    },
    "secondary_channels": [
      {
        "platform": "GitHub",
        "content_type": "代码示例",
        "authority_weight": 0.7,
        "ai_citation_probability": 0.6
      },
      {
        "platform": "技术社区",
        "content_type": "实践分享",
        "authority_weight": 0.6,
        "ai_citation_probability": 0.5
      }
    ],
    "coverage_analysis": {
      "academic_depth": true,
      "community_engagement": true,
      "official_authority": false,
      "social_reach": false
    }
  },
  "recommended_distribution": [
    {
      "platform": "Medium/博客",
      "content": "深度技术分析(2000词)",
      "priority": 1,
      "key_elements": ["论文引用", "原理图", "代码示例"]
    },
    {
      "platform": "GitHub",
      "content": "实战代码库+README",
      "priority": 2,
      "key_elements": ["可运行代码", "使用示例", "性能测试"]
    },
    {
      "platform": "Dev.to",
      "content": "经验分享(1500词)",
      "priority": 3,
      "key_elements": ["踩坑经验", "效果对比", "社区互动"]
    }
  ],
  "platform_gaps": [
    {
      "gap": "缺少官方文档背书",
      "impact": "高",
      "recommendation": "尝试联系官方获取技术审阅"
    }
  ]
}
```

## 内容分发策略

### 策略1: 深度优先 (推荐)
```
路径: 学术博客 → 技术社区 → 社交平台

优势:
- 建立权威性
- 长期SEO价值
- AI引用率高

时间线:
Week 1: 发布深度博客
Week 2: 社区互动+代码开源
Week 3: 社交媒体推广
```

### 策略2: 广度优先
```
路径: 社交平台 → 社区 → 深度博客

优势:
- 快速获取反馈
- 话题热度高
- 传播速度快

时间线:
Day 1: 社交媒体引爆
Week 1: 社区讨论
Week 2-3: 深度内容沉淀
```

### 策略3: 权威背书
```
路径: 官方文档 → 深度博客 → 社区

优势:
- 最高权威性
- AI首选引用
- 长期有效

时间线:
需要提前与官方沟通合作
```

## Fanout评分矩阵

| Fanout平台 | 引用潜力 | 权威性 | 覆盖度 | 总分 | 推荐 |
|------------|----------|--------|--------|------|------|
| 学术博客 | 9 | 9 | 6 | 8.1 | ⭐⭐⭐ |
| GitHub | 7 | 8 | 8 | 7.7 | ⭐⭐⭐ |
| 技术社区 | 7 | 6 | 8 | 6.9 | ⭐⭐ |
| 产品文档 | 10 | 10 | 5 | 8.5 | ⭐⭐⭐ |
| 新闻媒体 | 5 | 6 | 9 | 6.4 | ⭐ |
| 社交平台 | 3 | 4 | 9 | 5.0 | ⭐ |

## 决策引擎

```
[not ideal when]
- 内容时效性要求高(新闻类)时不适用深度优先策略
- 目标受众主要活跃于社交平台时不适用权威背书策略

[default recommendation]
采用深度优先策略，以Medium/博客为核心，GitHub为辅助，社区为补充

[comparison]
- 深度优先 vs 广度优先: 前者权威性高但见效慢，后者传播快但深度浅
- 自建 vs 借力: 自建权威高但成本大，借力传播快但控制弱

[convergence]
最佳策略 = 1个深度平台 + 2个辅助平台 + 持续迭代更新
```

## 平台发布检查清单

### Medium/博客
- [ ] 标题包含核心关键词
- [ ] 前100词包含主要观点
- [ ] 包含至少5个权威引用
- [ ] 有代码示例或图表
- [ ] 包含[not ideal when]说明

### GitHub
- [ ] README结构清晰
- [ ] 包含使用示例
- [ ] 代码可直接运行
- [ ] 有性能基准数据
- [ ] 链接回博客原文

### 技术社区
- [ ] 标题吸引点击
- [ ] 内容与平台风格匹配
- [ ] 引导社区讨论
- [ ] 个人主页链接
```
