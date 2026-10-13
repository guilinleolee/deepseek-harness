# Penpot Design System Sync

Bidirectional sync between Penpot design files and code-based design systems.

## Quick Start

### CLI

```bash
# Extract tokens from Penpot
python scripts/sync.py extract --file-id <uuid> --output tokens.json

# Transform to CSS
python scripts/sync.py transform --input tokens.json --format css --output tokens.css

# Transform to iOS Swift
python scripts/sync.py transform --input tokens.json --format ios --prefix DS --output DesignTokens.swift

# Sync to multiple platforms
python scripts/sync.py sync --input tokens.json --platforms ios,android,web --output-dir ./design-system

# Watch for changes
python scripts/sync.py watch --file-id <uuid> --on-change "echo 'Design updated!'"

# Compare versions
python scripts/sync.py diff --before tokens-v1.json --after tokens-v2.json
```

### Python API

```python
from penpot_sync import PenpotSync

sync = PenpotSync(api_key="your-api-key")

# Extract tokens
tokens = sync.extract_tokens(file_id="uuid")

# Transform to CSS
css = sync.transform(tokens, format="css", options={"prefix": "ds"})

# Export to multiple platforms
sync.export(tokens, formats=["ios", "android", "web"], output_dir="./design-system")
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Penpot API                                                 │
│   ↓ (extract)                                              │
│ TokenExtractor                                             │
│   ↓ (normalize)                                           │
│ TokenNormalizer                                            │
│   ↓ (transform)                                            │
│ TokenTransformer                                          │
│   ↓                                                       │
│ Output Formats: CSS, SCSS, iOS, Android, Tailwind, Figma │
└─────────────────────────────────────────────────────────────┘
```

## Token Types

- **Colors**: Primary, secondary, neutral, semantic, functional
- **Typography**: Font family, size, weight, line height, letter spacing
- **Spacing**: 8px grid-based values
- **Shadows**: Box shadow definitions
- **Borders**: Border width, color, style
- **Radii**: Border radius values
- **Breakpoints**: Responsive breakpoints

## Platform Support

| Platform | Format | Output |
|----------|--------|--------|
| Web | CSS | `tokens.css` |
| Web | SCSS | `_tokens.scss` |
| iOS | Swift | `DesignTokens.swift` |
| Android | XML | `colors.xml`, `dimens.xml` |
| Tailwind | Config | `tailwind.config.js` |
| Figma | JSON | `tokens.json` |

## MCP Server

```bash
# Start MCP server
python scripts/mcp_server.py

# Or use MCP tools
# extract_tokens, transform_tokens, sync_tokens, diff_tokens
```

## File Structure

```
penpot-design-system-sync/
├── SKILL.md
├── README.md
├── scripts/
│   ├── sync.py           # Main CLI
│   ├── mcp_server.py    # MCP server
│   ├── extract.py        # Token extraction
│   ├── transform.py      # Format transformation
│   ├── diff.py           # Change detection
│   └── __init__.py      # Core module
├── templates/
│   ├── style-dictionary.config.js
│   ├── tailwind.config.js
│   └── figma-tokens.json
├── token-templates/
│   ├── base-colors.json
│   ├── semantic-colors.json
│   ├── typography.json
│   └── spacing.json
└── examples/
    ├── basic-usage.py
    ├── multi-platform.js
    └── sync-workflow.sh
```
