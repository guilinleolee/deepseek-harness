# Hyperframes 流水线执行指南

## 场景判断

在启动流水线前，首先判断是否适合 Hyperframes：

### ✅ 适合 Hyperframes 的场景
- 品牌视频、产品宣传、slogan 视频
- 数据可视化视频（KPI 大屏、趋势图表）
- 社交媒体开场钩子视频（TikTok/抖音/Reels）
- 需要批量生成的模板化视频（多版本 A/B test）
- 需要精确控制每一帧的品牌展示

### ❌ 不适合 Hyperframes 的场景
- 需要真实人像/面部表情的视频 → Seedance
- 需要复杂 3D 场景/动态图表的程序化渲染 → Remotion
- 纯 AI 生成艺术风格视频 → Seedance
- 视频需要复杂的物理仿真/粒子效果 → Remotion

## 流水线执行步骤

### Step 1: 内容分析

从用户请求中提取：

```
核心信息（HEADLINE）: __________
补充说明（SUBHEADLINE）: __________
行动号召（CTA_TEXT）: __________
品牌账号（BRAND_HANDLE）: __________
目标平台: __________
视频时长: __________
```

### Step 2: 模板选择

| 模板 | 尺寸 | 场景 |
|------|------|------|
| social-media | 1080x1920 | TikTok/抖音/Reels |
| data-viz | 1920x1080 | 数据报告、KPI 对比 |
| product-intro | 1920x1080 | 产品发布、功能介绍 |

### Step 3: 风格推荐

调用 style_selector.py：

```bash
python skills/hyperframes-core/scripts/style_selector.py recommend "内容描述" --industry 行业
```

获取 VisualStyle 推荐后，记录推荐理由。

### Step 4: Props 填充

根据模板类型填充 props：

**social-media:**
```json
{
  "HEADLINE_TEXT": "...",
  "SUBHEADLINE_TEXT": "...",
  "CTA_TEXT": "...",
  "BRAND_HANDLE": "...",
  "STYLE": "swiss-pulse"
}
```

**data-viz:**
```json
{
  "OVERVIEW_TITLE": "...",
  "METRIC_1_VALUE": "...",
  "METRIC_1_LABEL": "...",
  "METRIC_1_DELTA": "..."
}
```

**product-intro:**
```json
{
  "PRODUCT_NAME": "...",
  "TAGLINE": "...",
  "PAIN_TITLE": "...",
  "SOLUTION_TITLE": "..."
}
```

### Step 5: 渲染执行

```python
from hf_cli_wrapper import HyperframesCLI, CompositionProps, VisualStyle

cli = HyperframesCLI(verbose=True)

# 生成 props 文件
props = CompositionProps(
    headline="...",
    subheadline="...",
    cta_text="...",
    brand_handle="...",
    style=VisualStyle.SWISS_PULSE
)
cli.generate_props_file(Template.SOCIAL_MEDIA, props, "output/props.json")

# 执行渲染
result = cli.render(
    "compositions/social-media/index.html",
    "output/final.mp4",
    props=props.to_hyperframes_props(),
    format="mp4",
    quality="high",
    fps=30
)

if result.success:
    print(f"✅ 渲染成功: {result.output_path}")
else:
    print(f"❌ 渲染失败: {result.error}")
```

### Step 6: 输出验证

- 确认文件生成
- 确认尺寸正确（对比目标平台）
- 确认时长符合预期
- 如有问题，检查 props 变量映射

## 批量流水线

多场景视频使用 Pipeline Composer：

```python
from hf_cli_wrapper import PipelineComposer, CompositionProps

composer = PipelineComposer()

# Scene 1: 开场钩子
composer.add_scene(
    name="hook",
    template="social-media",
    props=CompositionProps(
        headline="开场金句",
        style=VisualStyle.SWISS_PULSE
    ),
    transition="fade"
)

# Scene 2: 核心卖点
composer.add_scene(
    name="feature",
    template="data-viz",
    props=CompositionProps(
        headline="数据支撑",
        style=VisualStyle.DATA_DRIFT
    ),
    transition="wipe"
)

# Scene 3: 行动号召
composer.add_scene(
    name="cta",
    template="product-intro",
    props=CompositionProps(
        headline="立即行动",
        style=VisualStyle.VELVET_STANDARD
    ),
    transition="fade"
)

# 批量渲染
results = composer.render_all("output/batch/")
```

## 平台适配检查清单

- [ ] TikTok/抖音: 1080x1920, MP4, high quality
- [ ] Instagram Reels: 1080x1920, MP4, high quality
- [ ] YouTube Shorts: 1080x1920, MP4, high quality
- [ ] 微博视频: 1080x1920, MP4, medium quality
- [ ] LinkedIn: 1920x1080, MP4, high quality
- [ ] 内部汇报: 1920x1080, MP4/WebM, medium quality
