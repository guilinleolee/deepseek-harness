# Brand Guidelines EXTEND.md

## 默认品牌指南配置

---

## 自定义色彩模式 (Custom Color Mode)

### strict-palette
- enforcement: exact_colors_only
- variations: none
- custom_colors: forbidden
- accessibility: wcag_aa

### flexible-palette
- enforcement: primary_strict_secondary_flexible
- variations: allowed_ranges
- custom_colors: with_approval
- accessibility: wcag_aa_strict

### creative-palette
- enforcement: thematic_alignment
- variations: extensive_library
- custom_colors: encouraged
- accessibility: best_effort

---

## 自定义排版规则 (Custom Typography Rules)

### brand-fonts-only
- fonts: brand_typeface_only
- weights: predefined_set
- sizes: scale_based
- pairing: locked_combinations

### extended-allowed
- fonts: brand_with_fallbacks
- weights: extended_range
- sizes: flexible_scale
- pairing: guidelines_based

### open-typography
- fonts: aesthetic_matching
- weights: full_spectrum
- sizes: free_selection
- pairing: design_judgment

---

## 自定义Logo使用 (Custom Logo Usage)

### strict-logo
- placement: designated_zones_only
- sizing: exact_specifications
- variations: none
- clearspace: mandatory

### flexible-logo
- placement: context_appropriate
- sizing: proportional_ranges
- variations: approved_alternates
- clearspace: recommended

### creative-logo
- placement: aesthetic_integration
- sizing: balanced
- variations: extensive_library
- clearspace: minimal_guidance

---

## 自定义语音语调 (Custom Voice Tone)

### corporate-voice
- tone: formal_professional
- pronouns: first_person_plural
- contractions: avoided
- humor: minimal

### friendly-voice
- tone: approachable_warm
- pronouns: first_person_singular
- contractions: natural
- humor: light_occasional

### casual-voice
- tone: conversational
- pronouns: first_second_person
- contractions: frequent
- humor: encouraged

---

## 自定义布局约束 (Custom Layout Constraints)

### grid-strict
- alignment: exact_grid_positions
- spacing: fixed_increment
- responsive: breakpoint_based
- white_space: controlled

### grid-guided
- alignment: grid_with_flexibility
- spacing: modular_scale
- responsive: fluid_ranges
- white_space: generous

### layout-free
- alignment: visual_balance
- spacing: aesthetic
- responsive: organic
- white_space: dramatic

---

## 自定义图像风格 (Custom Image Style)

### brand-imagery
- photography: strict_style_guide
- illustrations: brand_artists_only
- graphics: templated_elements
- treatments: consistent_filters

### mixed-imagery
- photography: style_aligned
- illustrations: compatible_styles
- graphics: thematic_consistency
- treatments: light_cohesion

### open-imagery
- photography: context_appropriate
- illustrations: creative_freedom
- graphics: case_by_case
- treatments: minimal_constraints

---

## 自定义内容规范 (Custom Content Standards)

### minimal-standards
- requirements: basic_quality
- review: informal
- brand_check: visual_only
- approval: creator_discretion

### standard-standards
- requirements: quality_benchmarks
- review: peer_review
- brand_check: content_alignment
- approval: team_lead

### strict-standards
- requirements: comprehensive_criteria
- review: multi_stage
- brand_check: full_audit
- approval: brand_governance

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/brand-guidelines/EXTEND.md`
- **用户级**: `~/.claude/skills/brand-guidelines/EXTEND.md`
- **默认级**: `skills/brand-guidelines/EXTEND.md`

---

## 使用示例

### 企业品牌
```markdown
## Corporate Brand

### corporate-brand
- colors: strict-palette
- typography: brand-fonts-only
- logo: strict-logo
- voice: corporate-voice
- layout: grid-strict
- imagery: brand-imagery
- standards: strict-standards
```

### 现代品牌
```markdown
## Modern Brand

### modern-brand
- colors: flexible-palette
- typography: extended-allowed
- logo: flexible-logo
- voice: friendly-voice
- layout: grid-guided
- imagery: mixed-imagery
- standards: standard-standards
```

### 创意品牌
```markdown
## Creative Brand

### creative-brand
- colors: creative-palette
- typography: open-typography
- logo: creative-logo
- voice: casual-voice
- layout: layout-free
- imagery: open-imagery
- standards: minimal-standards
```
