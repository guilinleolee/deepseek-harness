# Vibma Design EXTEND.md

## 默认视觉品牌管理配置

---

## 自定义品牌资产

### logo-system
- formats: [svg, png, pdf]
- variants: [primary, icon, monochrome]
- sizes: [16, 32, 64, 128, 256, 512]
- spacing: clear_space_rules

### color-palette
- system: [primary, secondary, accent]
- shades: [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]
- accessibility: wcag_aa_compliant
- formats: hex_rgb_hsl

### typography
- fonts: [heading, body, mono]
- weights: [300, 400, 500, 600, 700]
- scales: [12, 14, 16, 18, 21, 24, 32, 48, 64]
- line_height: 1_5_1_75

---

## 自定义设计模板

### social-media
- platforms: [instagram, twitter, linkedin]
- formats: [story, post, cover]
- dimensions: [1080x1080, 1080x1920]
- templates: branded_templates

### presentation
- themes: [light, dark, brand_colors]
- layouts: [title, content, section, divider]
- masters: slide_masters
- exports: [pdf, pptx, images]

### marketing-assets
- types: [brochure, flyer, banner, poster]
- sizes: [a4, letter, custom]
- bleed: professional_print
- exports: [pdf, png, svg]

---

## 自定义设计工作流

### brand-new
- phase: research_define
- deliverables: [guidelines, assets]
- iterations: 3_rounds
- timeline: 2_3_weeks

### brand-refresh
- phase: audit_update
- deliverables: [updated_assets, migration_guide]
- iterations: 2_rounds
- timeline: 1_2_weeks

### campaign-creative
- phase: concept_production
- deliverables: [ad_creatives, variations]
- iterations: rapid_ab_test
- timeline: 1_week

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 完整品牌系统
- config: brand-new
- assets: [logo, colors, typography, guidelines]

### 社交媒体模板
- config: campaign-creative
- platforms: [instagram, linkedin]
- formats: [post, story]

### 营销物料设计
- config: brand-refresh
- assets: [brochure, flyer, banner]
- exports: print_ready
