---
license: UNKNOWN
triggers: ["minimax docx", "MiniMax DOCX Generation Skill"]
---
# MiniMax DOCX Generation Skill

## Overview

Professional Word document creation using OpenXML SDK, for documents that require precise formatting control.

## Invocation

```
/minimax-docx create "生成Word文档"
[@07记录师] 使用minimax-docx创建专业文档
```

## Workflow

### 1. Document Structure
Define sections, headings, content blocks.

### 2. Style Configuration
Set fonts, colors, spacing, numbering.

### 3. Content Generation
Create paragraphs, tables, lists, images.

### 4. Final Assembly
```bash
python scripts/create_docx.py --template template.json --content content.json --output document.docx
```

## Supported Elements

| Element | Example |
|---------|---------|
| Headings | H1, H2, H3 with styles |
| Paragraphs | Rich text with formatting |
| Tables | Complex layouts, merged cells |
| Lists | Numbered, bulleted, multi-level |
| Images | With captions, sizing |
| Page Breaks | Section breaks |
| Headers/Footers | Different per section |

## Style Configuration

```json
{
  "styles": {
    "heading1": {
      "font": "Arial",
      "size": 28,
      "bold": true,
      "color": "#1a365d",
      "spaceBefore": 24,
      "spaceAfter": 12
    },
    "heading2": {
      "font": "Arial",
      "size": 24,
      "bold": true,
      "color": "#2c5282"
    },
    "body": {
      "font": "Calibri",
      "size": 12,
      "color": "#2d3748",
      "lineSpacing": 1.5
    }
  }
}
```

## Dependencies

```bash
pip install python-docx openpyxl  # For table support
npm install -g docx  # Alternative Node.js library
```

## Integration with 天龙引擎

**Upgrades:**
- 07记录师 V8.72 → V8.73: Professional document generation

**Synergies:**
- docx: Base DOCX capabilities
- minimax-pdf: PDF export
- bidding-document-generator: Formal documents
