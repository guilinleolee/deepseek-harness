---
license: UNKNOWN
triggers: ["hyperframes pipeline", "Hyperframes Pipeline Skill"]
---
# Hyperframes Pipeline Skill

## L0: 一句话描述 (≤15字)
将 Hyperframes 视频生成融入天龙引擎流水线。

## L1: 使用场景 (50-100字)
当用户请求生成短视频、社交媒体内容、数据可视化视频、产品介绍视频时，由 35-05 短视频编导 Agent 触发。Hyperframes 提供 HTML+GSAP 程序化视频生成能力，与 Remotion/Seedance 形成三引擎互补。

## L2: 详细文档

### 核心职责

本技能作为 Hyperframes 与天龙引擎的管道适配层，负责：
1. 判断是否适合使用 Hyperframes（而非 Remotion/Seedance）
2. 从业务目标提取视频需求（模板/风格/时长/平台）
3. 驱动 `hf_cli_wrapper.py` 完成渲染
4. 触发 style_selector.py 进行风格推荐
5. 管理输出路径和格式适配

### Hyperframes vs Remotion vs Seedance 选型矩阵

| 维度 | Hyperframes | Remotion | Seedance |
|------|------------|-----------|----------|
| **核心范式** | HTML模板 + GSAP动画 | React组件 + 函数式 | 自然语言描述 → AI生成 |
| **适用内容** | 品牌视频/数据可视化/产品介绍 | 程序化数据/动态图表/3D内容 | 人像视频/复杂运镜/艺术风格 |
| **输出质量** | 高（像素级控制） | 高（React渲染） | 高（AI推理） |
| **渲染速度** | 快（CLI本地） | 中（需Lambda加速） | 慢（云端推理） |
| **定制粒度** | 模板变量替换 | 代码级控制 | Prompt控制 |
| **批量生产** | ✅ 极佳（Pipeline Composer） | ✅ 好（参数化） | ❌ 差（每次生成） |
| **触发词** | "品牌视频"、"数据大屏"、"产品宣传" | "动态图表"、"3D场景"、"代码驱动" | "生成视频"、"AI制作" |

### 流水线流程

```
用户请求（"生成一条产品宣传视频"）
    ↓
1. 内容分析 → 判断是否 Hyperframes 适用
    ↓
2. 模板选择 → social-media / data-viz / product-intro
    ↓
3. 风格推荐 → style_selector.py recommend
    ↓
4. 属性提取 → 从业务目标提取 props
    ↓
5. CLI 调用 → hf_cli_wrapper.py PipelineComposer
    ↓
6. 输出适配 → 平台格式转换（MP4/WebM/GIF）
```

### 流水线调用链

**完整流水线调用示例：**

```python
from hf_cli_wrapper import HyperframesCLI, PipelineComposer, CompositionProps, VisualStyle

# 初始化
cli = HyperframesCLI(verbose=True)

# 单视频渲染
props = CompositionProps(
    headline="新品发布预告",
    subheadline="突破性技术创新，引领行业未来",
    cta_text="立即预约",
    brand_handle="mybrand",
    style=VisualStyle.SWISS_PULSE
)
props_file = cli.generate_props_file(Template.PRODUCT_INTRO, props)
result = cli.render(
    "compositions/product-intro.html",
    "output/product-launch.mp4",
    props={"HEADLINE": "新品发布预告", ...},
    format="mp4",
    quality="high",
    fps=30
)
```

**Pipeline Composer 批量场景：**

```python
composer = PipelineComposer()
composer.add_scene("intro", "product-intro", intro_props, transition="fade")
composer.add_scene("feature", "product-intro", feature_props, transition="wipe")
composer.add_scene("cta", "product-intro", cta_props, transition="fade")
results = composer.render_all("output/product-video/")
```

### Props 属性提取指南

| Prop | 来源 | 说明 |
|------|------|------|
| `HEADLINE` | 用户请求第一句核心信息 | 9字以内最佳 |
| `SUBHEADLINE` | 补充说明或价值主张 | 20字以内 |
| `CTA_TEXT` | 行动号召 | 4-6字 |
| `BRAND_HANDLE` | 社交媒体账号 | 带@ |
| `STYLE` | style_selector.py 推荐 | 8种之一 |
| 模板特有 | 参见各模板 SKILL.md | - |

### 输出格式适配

| 平台 | 尺寸 | 格式 | 质量 |
|------|------|------|------|
| TikTok/抖音 | 1080x1920 | MP4 | high |
| Instagram Reels | 1080x1920 | MP4 | high |
| YouTube Shorts | 1080x1920 | MP4 | high |
| 微博视频 | 1080x1920 | MP4 | medium |
| LinkedIn | 1920x1080 | MP4 | high |
| 内部汇报 | 1920x1080 | MP4/WebM | medium |
| 动态演示 | 自适应 | GIF | low |

### 模板场景映射

**social-media (1080x1920, 9:16)**
- 适用：TikTok/抖音/Reels 开场钩子视频
- 典型内容：品牌宣言、产品卖点、活动预告
- 最佳风格：Swiss Pulse、Soft Signal、Folk Frequency

**data-viz (1920x1080, 16:9)**
- 适用：数据报告、产品数据对比、年度总结
- 典型内容：KPI大屏、趋势图表、对比分析
- 最佳风格：Data Drift、Maximalist Type

**product-intro (1920x1080, 16:9)**
- 适用：产品发布、功能介绍、品牌故事
- 典型内容：Logo+名称开场、痛点→解决方案→CTA
- 最佳风格：Velvet Standard、Shadow Cut

### 流水线 Agent 协同

| Agent | 角色 | 输入 | 输出 |
|-------|------|------|------|
| 35-05 短视频编导 | 流水线总控 | 业务目标 | 视频文件 |
| 28-01 文案策划 | 脚本撰写 | 视频主题 | 脚本文本 |
| 13-01 设计师 | 视觉把控 | StyleRecommendation | 风格批准 |
| 03 构建师 | 模板开发 | 特殊需求 | 自定义模板 |

### 常见错误处理

| 错误 | 原因 | 解决 |
|------|------|------|
| "Hyperframes CLI not found" | npx 未安装 | `npm install -g @hyperframes/cli` |
| 渲染超时 | 复杂动画 | 降低 fps 或 quality |
| Props 缺失 | 模板变量未替换 | 检查所有 {VARIABLE} 是否有对应 prop |
| 尺寸不匹配 | 模板选错 | social-media=9:16, data-viz=16:9 |

### 与 Remotion 的协同边界

```python
# 决策伪代码
if 需要程序化数据驱动动画:
    → Remotion  # 数据驱动的动态图表
elif 需要人像/复杂运镜:
    → Seedance  # AI 生成人像视频
elif 需要品牌模板/批量生产/数据可视化:
    → Hyperframes  # HTML 模板 + Pipeline Composer
```

### CLI 快速命令

```bash
# CLI 模式
python scripts/hf_cli_wrapper.py init my-project --template social-media
python scripts/hf_cli_wrapper.py render input.html output.mp4 --props props.json
python scripts/hf_cli_wrapper.py list

# 风格推荐
python scripts/style_selector.py recommend "品牌发布 数据驱动" --industry tech

# Python API 模式
from hf_cli_wrapper import quick_render
result = quick_render("social-media", "out.mp4",
    HEADLINE="Hello", SUBHEADLINE="Welcome",
    CTA_TEXT="Click", BRAND_HANDLE="@brand")
```
