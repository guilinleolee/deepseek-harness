---
license: UNKNOWN
triggers: ["minimax pdf", "MiniMax PDF Generation Skill"]
---
# MiniMax PDF Generation Skill

## Overview

PDF document generation with three workflows: CREATE (new PDFs), FILL (form fields), and REFORMAT (restyle existing docs).

## Invocation

```
/minimax-pdf create "生成报告PDF"
/minimax-pdf fill "填充表单"
/minimax-pdf reformat "重新排版"
[@07记录师] 使用minimax-pdf生成报告
```

## Three Workflows

### 1. CREATE - New PDF Generation

```bash
# Pipeline: palette.py → cover → body → merge
python scripts/palette.py --type report --output palette.json
python scripts/generate_cover.py --palette palette.json --output cover.pdf
python scripts/generate_body.py --content content.md --output body.pdf
python scripts/merge.py --inputs cover.pdf body.pdf --output final.pdf
```

**Document Types:**
| Type | Palette | Cover Pattern |
|------|---------|--------------|
| report | Professional blues/grays | Title block + gradient |
| proposal | Bold colors | High contrast hero |
| resume | Clean minimal | Single column |
| academic | Classic serif | Formal header |
| poster | Vibrant | Large typography |
| custom | User-defined | Custom template |

**Cover Styles (15 patterns):**
- Minimal clean, Bold geometric, Gradient fade
- Image background, Split layout, Centered typography
- Magazine style, Book style, Dashboard style
- Newsletter, Photography, Typography poster
- Product showcase, Event poster, Annual report

### 2. FILL - Form Field Population

```bash
# Inspect PDF form fields
python scripts/fill_inspect.py input.pdf --output fields.json

# Populate fields
python scripts/fill_write.py input.pdf --fields fields.json --data data.json --output filled.pdf
```

**Data format:**
```json
{
  "field_name_1": "John Doe",
  "field_name_2": "john@example.com",
  "check_box": true,
  "date_field": "2026-03-30"
}
```

### 3. REFORMAT - Restyle Existing Docs

```bash
# Parse source document
python scripts/reformat_parse.py --source document.md --output content.json

# Or from PDF
python scripts/reformat_parse.py --source document.pdf --output content.json

# Apply new style
python scripts/reformat_create.py --input content.json --style modern --output reformatted.pdf
```

## Dependencies

```bash
# Python 3.9+
pip install reportlab pypdf python-docx openpyxl

# Node.js 18+
npm install -g puppeteer  # For complex layouts

# Playwright (optional, for web-to-PDF)
npx playwright install chromium
```

## Theme Contract

```python
palette = {
    "primary": "#1a365d",      # Dark blue - titles
    "secondary": "#2c5282",     # Medium blue - subtitles
    "accent": "#3182ce",        # Light blue - highlights
    "background": "#ffffff",    # White
    "text": "#2d3748",          # Dark gray - body text
    "light": "#edf2f7",        # Light gray - backgrounds
}
```

## Integration with 天龙引擎

**Upgrades:**
- 07记录师 V8.72 → V8.73: Professional PDF generation

**Synergies:**
- ppt-generator: Presentation export
- docx: Word document generation
- pdf: Basic PDF capabilities
