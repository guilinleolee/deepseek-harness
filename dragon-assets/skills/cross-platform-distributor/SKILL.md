---
license: UNKNOWN
triggers: ["cross platform distributor", "cross-platform-distributor"]
---
# cross-platform-distributor

## L0: 一句话描述 (≤15字)

**跨平台分发：一键分发AI变现内容到全球平台**

---

## L1: 使用场景 (50-100字)

**适用场景**：AI变现内容多平台分发、社媒内容一键发布、全球平台覆盖、跨境内容矩阵运营、内容自动化同步分发。**触发关键词**：`cross-platform`、`分发`、`多平台`、`全球发布`、`平台矩阵`、`一键分发`

---

## L2: 详细文档

### 核心能力矩阵

| 能力 | 版本 | 说明 |
|------|------|------|
| 跨平台分发引擎 | V1.0 | 一键分发到20+全球平台 |
| 平台适配转换 | V1.0 | 内容自动适配各平台格式 |
| 发布排程管理 | V1.0 | 最优发布时间自动推荐 |
| 全球化合规 | V1.0 | 各平台内容合规检查 |
| 效果追踪分析 | V1.0 | 多平台数据统一回收 |

---

### 全球平台覆盖矩阵

```
┌─────────────────────────────────────────────────────────────┐
│                    全球内容分发平台矩阵                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  中国平台                                                    │
│  ├── 小红书(RED) - 种草/带货/品牌                        │
│  ├── 微信公众号 - 深度内容/订阅                           │
│  ├── 抖音 - 短视频/直播/带货                             │
│  ├── 微博 - 热点/话题/品牌曝光                           │
│  └── 知乎 - 知识付费/专业背书                            │
│                                                             │
│  海外英文平台                                               │
│  ├── Twitter/X - 短内容/热点/增长                         │
│  ├── LinkedIn - B2B/专业人设/职场                       │
│  ├── YouTube - 长视频/教程/品牌                           │
│  ├── Instagram - 视觉内容/生活方式                        │
│  ├── TikTok - 短视频/全球增长                            │
│  └── Medium - 博客/深度内容                              │
│                                                             │
│  海外本地化平台                                            │
│  ├── LINE (日本/台湾) - 私域/社群                        │
│  ├── Kakao (韩国) - 私域/社群                           │
│  ├── WhatsApp (东南亚/中东) - 私域                       │
│  └── Telegram (俄语区/全球) - 私域/社群                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 平台发布规格矩阵

```yaml
平台发布规格:
  小红书(RED):
    内容类型: 图文/视频/纯文字
    图片规格: 1:1(方图) 或 3:4(竖图)
    视频规格: mp4, 720p+, 15s-15min
    标签: #话题1 #话题2
    最佳发布时间: 07:00-09:00, 12:00-13:00, 18:00-20:00
    特殊限制: 不允许外部链接(需小红书号@)

  抖音:
    内容类型: 短视频/直播/图文
    视频规格: mp4, 1080p, 9:16, 15s-10min
    封面: 关键帧自动截取 或 手动上传
    最佳发布时间: 12:00-14:00, 18:00-22:00
    特殊限制: 敏感词过滤

  微信公众号:
    内容类型: 图文/音频/视频/链接
    封面图: 900x383px
    摘要: 最多120字
    最佳发布时间: 20:00-22:00
    特殊限制: 外部链接需微信认证

  Twitter/X:
    内容类型: 推文/图片/视频/线程
    文字限制: 280字符(付费380字符)
    图片: 最多4张
    视频: mp4, 140s(免费), 10min(付费)
    最佳发布时间: 09:00-11:00, 15:00-17:00
    特殊限制: 线程需用推文串格式

  LinkedIn:
    内容类型: 文章/图片/视频/文档
    文字限制: 3000字符(文章无限)
    图片: 最多9张
    视频: mp4, 10min
    最佳发布时间: 08:00-10:00(工作日)
    特殊限制: B2B语气, 禁止硬广

  YouTube:
    内容类型: 视频/Shorts/直播
    视频规格: mp4, 1080p+, 16:9
    Shorts规格: 9:16, 60s以内
    最佳发布时间: 14:00-16:00, 18:00-20:00
    特殊限制: 版权音乐, 缩略图

  Instagram:
    内容类型: 图片/Reels/Stories/IGTV
    图片规格: 1:1(方图) 或 4:5(竖图), 1080px+
    Reels规格: 9:16, 90s以内
    Stories规格: 1080x1920, 15s/帧
    最佳发布时间: 11:00-13:00, 19:00-21:00
    特殊限制: 不支持外部链接(Stories除外)

  TikTok:
    内容类型: 短视频/Reels/直播
    视频规格: mp4, 1080p, 9:16, 15s-10min
    最佳发布时间: 18:00-22:00
    特殊限制: AI生成内容标注

  Medium:
    内容类型: 文章
    文字限制: 无限制
    标签: 最多5个
    最佳发布时间: 周二-周四, 06:00-09:00
    特殊限制: 付费墙支持, 联盟链接
```

---

### AI内容适配转换规则

```yaml
内容自动适配:
  标题适配:
    小红书: 吸引眼球型, "这个AI工具让我月入X万"
    公众号: 专业深度型, "[深度]AI变现完全指南"
    Twitter: 简洁钩子型, "I made $X with AI in 30 days"
    LinkedIn: 专业背书型, "How we scaled AI revenue to $X"

  正文适配:
    小红书: 种草+痛点+解决方案+行动
    公众号: 深度分析+案例+方法论+资源
    Twitter: 线程格式, 每条独立信息点
    LinkedIn: 洞察+数据+职业视角+CTA

  标签适配:
    小红书: #[话题] #[品牌] #[AI工具]
    抖音: #AI #变现 #教程 #涨粉
    Twitter: #AI #SideProject #BuildInPublic
    LinkedIn: #AI #Innovation #[行业]

  图片适配:
    小红书: 高清产品图+数据截图+对比图
    公众号: 封面图+文中配图
    Instagram: 视觉冲击+品牌感
    LinkedIn: 专业场景+数据图表

  CTA适配:
    小红书: 点击主页链接 | 评论区见
    公众号: 扫码关注 | 原文链接
    Twitter: 关注+引用转发
    LinkedIn: 评论区讨论 | 关注获取更多
```

---

### 发布排程优化

```yaml
最佳发布时间推荐算法:
  因素权重:
    平台活跃高峰: 40%
    目标受众时区: 30%
    内容类型: 20%
    历史数据表现: 10%

  各平台黄金时段:
    中国(UTC+8):
      小红书: 07:00-09:00, 12:00-13:00, 18:00-20:00
      抖音: 12:00-14:00, 18:00-22:00
      公众号: 20:00-22:00

    美国东部(UTC-5):
      LinkedIn: 08:00-10:00(周二-周四)
      Twitter: 09:00-11:00, 15:00-17:00
      Instagram: 11:00-13:00, 19:00-21:00

    欧洲(UTC+1):
      LinkedIn: 08:00-10:00(工作日)
      Twitter: 09:00-11:00
      Medium: 06:00-09:00(周二-周四)

  排程策略:
    首发平台: 抖音/小红书(中国) 或 Twitter/LinkedIn(海外)
    二次分发: 首发后2-4小时分发到其他平台
    线程发布: Twitter线程每条间隔30分钟
```

---

### AI提示词模板

#### 多平台内容生成提示词

```markdown
# Role: 跨平台内容分发专家

# 核心产品
- 产品名称: {product_name}
- 产品价值: {core_value}
- 目标受众: {target_audience}

# 变现信息
- 价格: {price}
- 促销信息: {promotion}
- 转化链接: {conversion_link}

# 发布平台
- 中国平台: {cn_platforms} (小红书/抖音/公众号/微博/知乎)
- 海外英文: {en_platforms} (Twitter/LinkedIn/YouTube/Instagram/TikTok)
- 本地化平台: {local_platforms} (LINE/Kakao/Telegram)

# 内容适配要求
## 小红书适配
- 风格: 种草/测评/干货
- 结构: 痛点→体验→效果→行动
- 视觉: 高清图+数据截图

## Twitter/X适配
- 风格: 短平快+钩子
- 结构: 线程格式(每条独立信息点)
- 字数: 每条≤280字符

## LinkedIn适配
- 风格: 专业洞察+数据背书
- 结构: 观点→数据→洞察→讨论
- 语气: B2B专业, 禁止硬广

## YouTube适配
- 风格: 教程/测评/案例
- 结构: Hook(3秒)→价值承诺→内容→CTA
- 时长: 8-15分钟最佳

# 输出要求
## 分平台内容包
| 平台 | 标题 | 正文 | 标签 | 最佳发布时间 |
|------|------|------|------|-------------|
| 小红书 | ... | ... | ... | ... |
| 抖音 | ... | ... | ... | ... |
| 公众号 | ... | ... | ... | ... |
| Twitter | ... | ... | ... | ... |
| LinkedIn | ... | ... | ... | ... |

## 发布排程
- 首发平台: {first_platform}
- 分发顺序: {distribution_order}
- 间隔时间: {interval}
```

#### 本地化适配提示词

```markdown
# Role: 内容本地化专家

# 原始内容
- 原文: {original_content}
- 原文语言: {source_lang}
- 目标语言: {target_lang}

# 目标市场
- 地区: {region}
- 文化特点: {cultural_notes}
- 本地化程度: {localization_level} (完全本地化/轻度适配/仅翻译)

# 本地化要点
- 表达习惯: {expression_habits}
- 禁忌内容: {taboos}
- 货币格式: {currency_format}
- 联系方式: {contact_format}

# 输出要求
## 本地化版本
- 标题: {localized_title}
- 正文: {localized_body}
- 标签/hashtags: {localized_tags}

## 文化适配说明
- 保留元素: {preserve}
- 调整元素: {adapt}
- 替换元素: {replace}
```

---

### 命令调用

```bash
# 跨平台内容分发
cross-platform publish --content "内容文件.md" --platforms "小红书,抖音,Twitter,LinkedIn"

# 多平台排程发布
cross-platform schedule --content "campaign.md" --timezone "Asia/Shanghai"

# 本地化内容生成
cross-platform localize --content "source.md" --target-lang "ja,ko,th"

# 平台数据分析
cross-platform analytics --platforms "all" --period "7d"

# 竞品内容监控
cross-platform monitor --competitors "竞品账号" --platforms "小红书,抖音"

# 一键素材适配
cross-platform adapt --original "素材.jpg" --platforms "all"
```

---

### MCP工具调用

```bash
# 内容生成+分发
mcp__distributor__generate_and_publish "AI变现教程" --platforms "小红书,抖音,Twitter,LinkedIn,Medium"

# 平台适配转换
mcp__distributor__adapt_content --source "公众号文章.md" --targets "小红书,抖音,Twitter"

# 发布排程优化
mcp__distributor__optimize_schedule --content-type "种草" --target-audience "25-35岁职场人"

# 多平台数据汇总
mcp__distributor__analytics_aggregate --platforms "all" --metrics "阅读,互动,转化"

# 竞品内容抓取
mcp__distributor__competitor_scrape --accounts "竞品1,竞品2" --platform "小红书"
```

---

### 与其他技能协同

| 技能 | 协同方式 | 效果 |
|------|---------|------|
| `monetization-seven-swords` | 七剑文案→跨平台分发 | 一键分发高转化文案 |
| `ai-card-system` | AI卡牌→多平台发布 | 卡牌内容矩阵分发 |
| `shell-site-generator` | 站点→链接嵌入分发 | 落地页+分发闭环 |
| `overseas-pricing-strategy` | 定价→全球分发 | 定价策略全球发布 |

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-05 | 初始版本，跨平台分发完整系统 |

---

**版本**: v1.0
**最后更新**: 2026-05-05
**技能类型**: 跨平台内容分发
