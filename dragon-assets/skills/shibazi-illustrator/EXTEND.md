# Shibazi Illustrator EXTEND.md

## 默认十八子配图配置

---

## 自定义图片尺寸

### wechat-size
- dimensions: 900x500
- aspect_ratio: 16_9
- dpi: 72
- format: jpg_png

### juejin-size
- dimensions: 800x450
- aspect_ratio: 16_9
- dpi: 72
- format: jpg

### zhihu-size
- dimensions: 1200x675
- aspect_ratio: 16_9
- dpi: 72
- format: jpg_webp

### xiaohongshu-size
- dimensions: 1080x1080
- aspect_ratio: 1_1
- dpi: 72
- format: jpg

---

## 自定义视觉风格

### minimal-tech
- style: clean_geometric
- colors: monochrome_accent
- typography: sans_serif
- layout: grid_based

### vibrant-modern
- style: colorful_gradients
- colors: bold_palettes
- typography: display_fonts
- layout: dynamic

### hand-drawn
- style: sketch_illustration
- colors: watercolor_pastel
- typography: handwritten
- layout: organic

### corporate-professional
- style: business_infographic
- colors: brand_compliant
- typography: professional
- layout: structured

---

## 自定义内容提取

### title-extraction
- method: headline_analysis
- keywords: top_3
- emphasis: visual_hierarchy
- placement: prominent

### summary-extraction
- method: key_sentences
- keywords: topic_modeling
- emphasis: core_message
- placement: supporting

### quote-extraction
- method: notable_phrases
- keywords: impact_words
- emphasis: callout_boxes
- placement: accent

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 公众号配图
- size: wechat-size
- style: minimal-tech
- content: title-extraction

### 掘金封面
- size: juejin-size
- style: vibrant-modern
- content: summary-extraction

### 小红书卡片
- size: xiaohongshu-size
- style: hand-drawn
- content: quote-extraction
