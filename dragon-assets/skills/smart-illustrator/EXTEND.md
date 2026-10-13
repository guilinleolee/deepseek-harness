# Smart Illustrator 自定义配置

> Smart Illustrator 风格配置扩展文件
> 修改此文件以添加自定义风格，或在项目级/用户级创建覆盖配置

---

## Custom Styles

### tech-blueprint
- description: 技术蓝图风格，适合架构图和系统设计
- colors: #1a73e8, #4285f4, #34a853, #fbbc04
- background: #f8f9fa
- best-for: 架构图、系统设计、技术文档

### warm-handwritten
- description: 温暖手绘风格，适合生活方式类内容
- colors: #ff6b6b, #feca57, #48dbfb, #ff9ff3
- background: #fff5e6
- best-for: 生活方式、旅行、美食、个人成长

### minimal-japanese
- description: 日式极简风格，清爽克制
- colors: #2c3e50, #ecf0f1, #e74c3c
- background: #ffffff
- best-for: 哲学、极简主义、禅修内容

### cyberpunk-neon
- description: 赛博朋克霓虹风格，未来感强烈
- colors: #ff006e, #8338ec, #3a86ff, #06ffa5
- background: #0a0e27
- best-for: 科技、游戏、未来主题

### nature-organic
- description: 自然有机风格，大地色系
- colors: #2d6a4f, #40916c, #52b788, #d8f3dc
- background: #f7f9f7
- best-for: 环保、自然、健康、可持续发展

### corporate-memphis
- description: 企业孟菲斯风格，扁平化矢量
- colors: #0066cc, #00cc66, #ffcc00, #ff6600
- background: #ffffff
- best-for: 企业、SaaS、商务演示

### vintage-paper
- description: 复古纸张风格，怀旧质感
- colors: #5c4033, #8b7355, #d4c4b0, #f5e6d3
- background: #f9f1e1
- best-for: 历史、怀旧、传统文化

---

## Custom Cover Styles

### youtube-hero
- dimensions: 16:9
- text-style: bold-title
- mood: vibrant
- best-for: YouTube视频封面

### xiaohongshu-portrait
- dimensions: 3:4
- text-style: title-only
- mood: balanced
- best-for: 小红书笔记封面

### wechat-banner
- dimensions: 2.35:1
- text-style: title-subtitle
- mood: subtle
- best-for: 微信公众号头图

---

## Options

# 默认风格 (文章配图)
default_style = tech-blueprint

# 默认封面风格
default_cover_style = youtube-hero

# 输出质量 (normal, high, 2k)
output_quality = high

# 默认宽高比
default_aspect_ratio = 16:9

# 是否自动检测最佳风格
auto_detect_style = true
