---
license: UNKNOWN
triggers: ["ecommerce image generator", "ecommerce-image-generator"]
---
# ecommerce-image-generator

## L0: 一句话描述 (≤15字)
电商场景GPT-Image-2提示词库

## L1: 使用场景 (50-100字)
当用户需要为电商场景（商品主图/广告Banner/详情页/小红书种草）生成专业图像时使用此技能。包含100+社区验证的电商专用提示词，适用于商品展示、价格标签、场景图、种草图文等场景。

## L2: 详细文档

### 核心能力

**数据来源**：[EvoLinkAI/awesome-gpt-image-2-API-and-Prompts](https://github.com/EvoLinkAI/awesome-gpt-image-2-API-and-Prompts) - E-commerce分类

**电商专用提示词结构**：
```
产品主体 + 背景场景 + 光效风格 + 视角角度 + 规格标注
```

### 电商场景分类

| 分类 | 用途 | 提示词特征 |
|------|------|-----------|
| **商品主图** | 淘宝/京东/亚马逊 | 白底/透明背景，高清细节 |
| **广告Banner** | 直通车/首页 | 大面积文字区，冲击配色 |
| **详情页** | 详情描述 | 场景代入，情感共鸣 |
| **种草图文** | 小红书/抖音 | 生活场景，真实感 |
| **对比图** | 竞品分析 | 左右分栏，同一场景 |
| **价格标签** | 促销/秒杀 | 醒目价格，促销元素 |

### 核心命令

```bash
# 搜索电商提示词
python3 ~/.claude/skills/ecommerce-image-generator/scripts/query.py \
  --category product_main --limit 10

# 按场景搜索
python3 ~/.claude/skills/ecommerce-image-generator/scripts/query.py \
  --scene lifestyle --limit 5

# 批量导出
python3 ~/.claude/skills/ecommerce-image-generator/scripts/query.py \
  --category ad_banner --export json --output ecommerce_prompts.json
```

### 高转化提示词模板

```python
# 商品主图模板
PRODUCT_MAIN = """{product_name} on clean white background,
studio lighting, high resolution product photography,
detailed texture, {angle} view,
minimalist composition, 4K, white seamless backdrop"""

# 场景图模板
LIFESTYLE = """{product} in {scene} setting,
warm natural lighting, {mood} atmosphere,
{brand} aesthetic, lifestyle photography,
cinematic composition, soft focus background"""

# 种草图文模板
SEEDING = """aesthetic flat lay of {products},
{style} photography, styled with {props},
natural daylight, {color_palette} palette,
minimalist composition, instagram-worthy,
{props_context}"""
```

### 与现有技能协同

| 现有技能 | 协同方式 |
|---------|---------|
| **gpt-image-2-prompt-library** | 获取通用肖像/海报提示词 |
| **gpt-image-2-api-integration** | API调用生成图像 |
| **xiaohu-wechat-format** | 种草图文→公众号排版 |
| **xhs-images** | 小红书图片生成 |

### 天龙岗位升级

| 岗位 | 版本升级 | 新增能力 |
|------|---------|---------|
| **45-01 电商运营** | V2.0→V2.1 | 电商专用提示词+转化率优化 |
| **35-02 社媒运营** | V12.6→V12.7 | 种草图文生成+小红书配图 |
| **28-01 文案策划** | V1.2→V1.3 | 配图+文案一体化 |

### 提示词优化技巧

| 技巧 | 示例 | 效果 |
|------|------|------|
| 加"官方设计风格" | "...official design style" | 避免AI味 |
| 加"手机拍摄" | "...shot with iPhone 15 Pro" | 更真实 |
| 加"无版权背景" | "...unsplash background" | 可商用 |
| 加具体尺寸 | "...square 1:1 ratio" | 适配平台 |

### 注意事项

1. **版权合规**：避免使用品牌Logo，保护知识产权
2. **平台规范**：不同平台有不同尺寸要求
3. **A/B测试**：建议生成3-5个变体测试效果

### 版本信息
- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **Source**: EvoLinkAI/awesome-gpt-image-2-API-and-Prompts
- **Last Updated**: 2026-05-08