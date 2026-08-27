# DeerFlow PPT Generation Skill

## Overview

演示文稿生成技能 - 8种风格、顺序生成保证一致性。

## Presentation Styles

| 风格 | 描述 | 适用场景 |
|------|------|---------|
| **glassmorphism** | 毛玻璃效果、渐变背景、浮动卡片 | 科技产品、AI/SaaS演示 |
| **dark-premium** | 深黑背景、发光强调色、奢华质感 | 高端产品、高管演示 |
| **gradient-modern** | 粗粒渐变、现代排版、活力感 | 初创公司、创意机构 |
| **neo-brutalist** | 原始粗犷、高对比、反设计 | 前卫品牌、Gen-Z |
| **3d-isometric** | 等距3D插画、悬浮元素、柔和阴影 | 技术解释、产品功能 |
| **editorial** | 杂志级排版、高端摄影 | 年报、品牌 |
| **minimal-swiss** | 网格精准、Helvetica字体、大量留白 | 建筑、设计、咨询 |
| **keynote** | Apple风格、电影感、大胆排版 | 主题演讲、产品发布 |

## Workflow

### Step 1: 理解需求
- 主题/内容
- 幻灯片数量（默认5-10）
- 风格选择
- 纵横比（16:9或4:3）
- 每页要点

### Step 2: 创建演示计划

创建JSON文件：
```json
{
  "title": "演示标题",
  "style": "keynote",
  "aspect_ratio": "16:9",
  "slides": [
    {
      "slide_number": 1,
      "type": "title",
      "title": "主标题",
      "subtitle": "副标题",
      "visual_description": "图片生成描述"
    }
  ]
}
```

### Step 3: 顺序生成幻灯片

**关键规则**：必须按顺序一张一张生成！

```bash
# 第一张 - 建立视觉语言
python scripts/generate.py \
  --prompt-file slide-01.json \
  --output-file slide-01.jpg \
  --aspect-ratio 16:9

# 第二张 - 必须参考第一张
python scripts/generate.py \
  --prompt-file slide-02.json \
  --reference-images slide-01.jpg \
  --output-file slide-02.jpg \
  --aspect-ratio 16:9
```

### Step 4: 组合PPT

```bash
python scripts/generate.py \
  --plan-file presentation-plan.json \
  --slide-images slide-01.jpg slide-02.jpg slide-03.jpg \
  --output-file presentation.pptx
```

## Style Guidelines

### Glassmorphism
```json
{
  "color_palette": "渐变背景 (紫色#667eea到粉色#f093fb)",
  "typography": "SF Pro Display, 粗体标题600-700",
  "imagery": "浮动3D形状、柔和模糊光球",
  "layout": "毛玻璃卡片、圆角24-32px"
}
```

### Dark Premium
```json
{
  "color_palette": "深黑底(#0a0a0a)、发光强调色(#00d4ff)",
  "typography": "优雅无衬线、戏剧性大小对比(72pt+)",
  "imagery": "戏剧性灯光、边缘发光、电影感",
  "layout": "大量留白(60%+)、非对称平衡"
}
```

### Keynote
```json
{
  "color_palette": "深黑背景、纯白文字、蓝色强调(#0071e3)",
  "typography": "San Francisco Pro Display、极端粗细对比",
  "imagery": "电影感摄影、浅景深、戏剧性灯光",
  "layout": "最大留白、每页一个焦点"
}
```

## Quality Guidelines

### 必须做
- ✅ 使用英文生成图片提示词
- ✅ 极度具体化视觉细节
- ✅ 使用精确的十六进制颜色代码
- ✅ 每张幻灯片必须参考前一张
- ✅ 第一张建立整体视觉语言

### 禁止做
- ❌ 模糊提示如"专业幻灯片"
- ❌ 每页太多元素/文字
- ❌ 幻灯片之间风格不一致
- ❌ 并行生成幻灯片
- ❌ 使用不同设计风格

## Complete Example

```bash
# 1. 创建计划
cat > ai-product-plan.json << 'EOF'
{
  "title": "AI Product Launch",
  "style": "glassmorphism",
  "slides": [...]
}
EOF

# 2. 生成第一张
python scripts/generate.py --prompt-file slide-01.json \
  --output-file slide-01.jpg --aspect-ratio 16:9

# 3. 生成第二张（参考第一张）
python scripts/generate.py --prompt-file slide-02.json \
  --reference-images slide-01.jpg \
  --output-file slide-02.jpg --aspect-ratio 16:9

# 4. 组合
python scripts/generate.py --plan-file ai-product-plan.json \
  --slide-images slide-01.jpg slide-02.jpg slide-03.jpg \
  --output-file ai-product-launch.pptx
```
