---
license: UNKNOWN
---

# MiniMax Vision Analysis Skill

## Overview

Image analysis with OCR, chart extraction, UI mockup review, and visual content understanding.

## Invocation

```
/minimax-vision analyze "分析图片"
/minimax-vision ocr "提取文字"
/minimax-vision chart "提取图表数据"
[@01调研师] 使用minimax-vision分析设计稿
[@04验证师] 使用minimax-vision验证UI
```

## Core Capabilities

### OCR (Optical Character Recognition)

```bash
# Basic OCR
python scripts/ocr.py --image screenshot.png --output text.txt

# With layout preservation
python scripts/ocr.py --image screenshot.png --layout --output text.txt

# Multi-language
python scripts/ocr.py --image doc.png --langs eng+chi+jpn --output text.txt
```

### Chart Data Extraction

```bash
# Extract chart data from images
python scripts/chart_extract.py --image chart.png --output data.json

# Output format
{
  "type": "bar_chart",
  "title": "Sales by Quarter",
  "data": [
    {"label": "Q1", "value": 100},
    {"label": "Q2", "value": 150},
    {"label": "Q3", "value": 120},
    {"label": "Q4", "value": 200}
  ],
  "labels": ["Region A", "Region B", "Region C"]
}
```

### UI Mockup Review

```bash
# Analyze UI design
python scripts/ui_review.py --mockup design.png --output analysis.json

# Analysis includes:
# - Component identification
# - Spacing analysis
# - Typography check
# - Color palette extraction
# - Accessibility hints
```

### Visual Content Analysis

```bash
# Describe image content
python scripts/analyze.py --image photo.jpg --prompt "Describe the main elements"

# Extract structured information
python scripts/analyze.py --image form.png --schema schema.json --output data.json
```

## Integration with 天龙引擎

**Upgrades:**
- 01调研师 V8.68 → V8.73: Visual analysis capabilities
- 04验证师 V8.68 → V8.73: UI verification

**Synergies:**
- follow-builders: Design screenshot analysis
- impeccable: Design audit
- browser-qa: Visual testing
