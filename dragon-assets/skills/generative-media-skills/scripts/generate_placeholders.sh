#!/usr/bin/env bash
# Generate placeholder SKILL.md files for generative-media-skills
# Based on tags.json inventory (73 skills total)

SKILL_ROOT="C:/Users/li/.claude/projects/dragon-engine/skills/generative-media-skills/library"

# Define skills per category
declare -A skills
skills[_core]="edit media platform"
skills[edit]="ai-clipping muapi-ai-clipping"
skills[motion]="3d-logo-animation ai-fight-scene animal-video-generator award-ceremony-video cartoon-dance-animation character-story-video cinema-director drone-style-video freeze-effect-video giant-product-showcase jewelry-product-video muapi-cinema-director muapi-product-video-ad-maker muapi-seedance-2 muapi-social-media-video muapi-ugc-video-factory muapi-youtube-shorts muapi-youtube-thumbnail music-video one-shot-video product-ad-cinematic product-showcase-video product-video-ad-maker seedance-2 storyboard-to-cooking-video talking-baby-video ugc-lifestyle-try-on ugc-video-factory"
skills[social]="instagram-post product-campaign rednote-cover social-media-video social-pack ugc-ads-workflow youtube-shorts"
skills[visual]="action-figure-generator ad-creative amazon-product-listing blog-header brand-kit brochures chibi-collage-effect color-analysis-board couple-grid-creator design-guide fashion-try-on floor-plan-rendering interior-design interior-design-visualizer keyboard-art-maker logo-branding logo-creator logo-generator muapi-ad-creative muapi-instagram-post muapi-logo-creator muapi-nano-banana muapi-ui-design multi-angle-reshoot multi-angle-shots nano-banana photo-pack-generator selfie-with-celebrities storyboard ui-design url-to-design youtube-thumbnail"
skills[workflow]="workflow"

generate_skill_md() {
    local category="$1"
    local skill="$2"
    local dir="${SKILL_ROOT}/${category}/${skill}"
    local is_muapi=$(echo "$skill" | grep -q "muapi-" && echo "true" || echo "false")
    local model_name=$(echo "$skill" | sed 's/muapi-//')

    mkdir -p "$dir"

    cat > "${dir}/SKILL.md" << EOF
---
name: $skill
description: >
  $(if [ "$is_muapi" = "true" ]; then echo "muapi.ai 路由适配器 · ${model_name}"; else echo "生成式媒体技能 · ${skill}"; fi)
  Use when user asks to generate $(echo "$skill" | tr '-' ' ') via muapi.ai
version: 1.0.0
author: SamurAIGPT (MIT)
source: https://github.com/SamurAIGPT/Generative-Media-Skills
license: MIT
last_updated: 2026-07-20
category: $category
muapi_model: $model_name
status: placeholder
---

# $skill

> **占位 SKILL.md** · 待从上游完整 mirror

## L0: 一句话描述 (≤15字)

$(if [ "$is_muapi" = "true" ]; then echo "muapi ${model_name} 适配器"; else echo "${skill} 生成"; fi)

## L1: 使用场景

当用户需要使用 $(echo "$skill" | tr '-' ' ') 功能时调用本 skill。

## L2: 调用方式

\`\`\`bash
bash async-task-pattern/adapters/muapi.sh submit \
  --action "${model_name}" --payload '{"..."}' --timeout 300
\`\`\`

## L3: 依赖

- `async-task-pattern/adapters/muapi.sh`
- `MUAPI_API_KEY` 环境变量

## 注意事项

1. **待 mirror**：本文件为占位版本，完整内容待从上游拉取
2. **需 MUAPI_API_KEY**：实际调用需要配置 muapi.ai API Key
EOF

    echo "✓ Created: ${category}/${skill}/SKILL.md"
}

# Generate all SKILL.md files
total=0
for category in _core edit motion social visual workflow; do
    for skill in ${skills[$category]}; do
        generate_skill_md "$category" "$skill"
        ((total++))
    done
done

echo ""
echo "========================================"
echo "生成完成: $total 个 SKILL.md 占位文件"
echo "========================================"
