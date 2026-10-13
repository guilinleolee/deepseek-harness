#!/usr/bin/env bash
#
# penpot-design-system-sync - Sync Workflow Script
#
# This script demonstrates a complete workflow for syncing design tokens
# from Penpot to multiple platforms.
#
# Usage:
#   ./sync-workflow.sh [command] [options]
#
# Commands:
#   extract     - Extract tokens from Penpot
#   transform   - Transform tokens to various formats
#   sync        - Run full sync pipeline
#   watch       - Watch for Penpot file changes
#   diff        - Compare token versions
#   clean       - Clean generated files
#

set -e

# Configuration
PENPOT_API_KEY="${PENPOT_API_KEY:-}"
PENPOT_URL="${PENPOT_URL:-https://penpot.app}"
TOKEN_FILE="${TOKEN_FILE:-./tokens.json}"
OUTPUT_DIR="${OUTPUT_DIR:-./dist}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

header() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════"
}

# Check dependencies
check_dependencies() {
    header "Checking Dependencies"

    local missing=()

    # Check Python
    if command -v python3 &> /dev/null; then
        success "Python3: $(python3 --version)"
    elif command -v python &> /dev/null; then
        success "Python: $(python --version)"
    else
        missing+=("python3")
    fi

    # Check Node.js (optional)
    if command -v node &> /dev/null; then
        success "Node.js: $(node --version)"
    else
        warn "Node.js not found (optional for advanced transforms)"
    fi

    # Check jq (optional)
    if command -v jq &> /dev/null; then
        success "jq: $(jq --version)"
    else
        warn "jq not found (optional for JSON processing)"
    fi

    if [ ${#missing[@]} -gt 0 ]; then
        error "Missing required dependencies: ${missing[*]}"
        exit 1
    fi

    success "All required dependencies installed"
}

# Extract tokens from Penpot
cmd_extract() {
    header "Extracting Tokens from Penpot"

    local file_id="${1:-}"
    local output_file="${2:-$TOKEN_FILE}"

    if [ -z "$PENPOT_API_KEY" ]; then
        warn "PENPOT_API_KEY not set"
        warn "Generating sample tokens for demonstration..."

        # Generate sample tokens
        mkdir -p "$(dirname "$output_file")"
        cat > "$output_file" << 'EOF'
{
  "$metadata": {
    "tokenSetOrder": ["base/colors", "base/typography", "base/spacing"],
    "version": "1.0.0"
  },
  "base": {
    "colors": {
      "primitive": {
        "white": { "value": "#ffffff", "type": "color" },
        "black": { "value": "#000000", "type": "color" }
      },
      "gray": {
        "50": { "value": "#f9fafb", "type": "color" },
        "100": { "value": "#f3f4f6", "type": "color" },
        "200": { "value": "#e5e7eb", "type": "color" },
        "300": { "value": "#d1d5db", "type": "color" },
        "400": { "value": "#9ca3af", "type": "color" },
        "500": { "value": "#6b7280", "type": "color" },
        "600": { "value": "#4b5563", "type": "color" },
        "700": { "value": "#374151", "type": "color" },
        "800": { "value": "#1f2937", "type": "color" },
        "900": { "value": "#111827", "type": "color" }
      },
      "blue": {
        "50": { "value": "#eff6ff", "type": "color" },
        "100": { "value": "#dbeafe", "type": "color" },
        "500": { "value": "#3b82f6", "type": "color" },
        "600": { "value": "#2563eb", "type": "color" },
        "700": { "value": "#1d4ed8", "type": "color" }
      }
    },
    "typography": {
      "fontFamily": {
        "sans": { "value": "Inter, -apple-system, sans-serif", "type": "fontFamily" },
        "mono": { "value": "JetBrains Mono, monospace", "type": "fontFamily" }
      },
      "fontSize": {
        "xs": { "value": "0.75rem", "type": "fontSize" },
        "sm": { "value": "0.875rem", "type": "fontSize" },
        "base": { "value": "1rem", "type": "fontSize" },
        "lg": { "value": "1.125rem", "type": "fontSize" },
        "xl": { "value": "1.25rem", "type": "fontSize" },
        "2xl": { "value": "1.5rem", "type": "fontSize" }
      },
      "fontWeight": {
        "normal": { "value": "400", "type": "fontWeight" },
        "medium": { "value": "500", "type": "fontWeight" },
        "semibold": { "value": "600", "type": "fontWeight" },
        "bold": { "value": "700", "type": "fontWeight" }
      }
    },
    "spacing": {
      "0": { "value": "0px", "type": "dimension" },
      "1": { "value": "4px", "type": "dimension" },
      "2": { "value": "8px", "type": "dimension" },
      "3": { "value": "12px", "type": "dimension" },
      "4": { "value": "16px", "type": "dimension" },
      "5": { "value": "20px", "type": "dimension" },
      "6": { "value": "24px", "type": "dimension" },
      "8": { "value": "32px", "type": "dimension" },
      "10": { "value": "40px", "type": "dimension" }
    }
  }
}
EOF
        success "Sample tokens generated: $output_file"
        return 0
    fi

    if [ -z "$file_id" ]; then
        read -p "Enter Penpot File ID: " file_id
    fi

    if [ -z "$file_id" ]; then
        error "File ID is required"
        return 1
    fi

    info "Extracting from: $PENPOT_URL"
    info "File ID: $file_id"

    # Call Penpot API
    local response
    response=$(curl -s -X GET \
        -H "Authorization: Bearer $PENPOT_API_KEY" \
        "$PENPOT_URL/api/v1/files/$file_id")

    if echo "$response" | jq -e '.errors' &> /dev/null; then
        error "API Error: $(echo "$response" | jq -r '.errors[0].message')"
        return 1
    fi

    mkdir -p "$(dirname "$output_file")"
    echo "$response" > "$output_file"
    success "Tokens extracted: $output_file"
}

# Transform tokens to various formats
cmd_transform() {
    header "Transforming Tokens"

    local input_file="${1:-$TOKEN_FILE}"
    local format="${2:-all}"

    if [ ! -f "$input_file" ]; then
        error "Token file not found: $input_file"
        return 1
    fi

    mkdir -p "$OUTPUT_DIR/web" "$OUTPUT_DIR/ios" "$OUTPUT_DIR/android/res/values" "$OUTPUT_DIR/tailwind"

    # CSS
    if [ "$format" = "all" ] || [ "$format" = "css" ]; then
        info "Transforming to CSS..."
        python3 -c "
import json
import sys

with open('$input_file') as f:
    tokens = json.load(f)

css = ':root {\\n'

# Colors
if 'base' in tokens and 'colors' in tokens['base']:
    for cat, scales in tokens['base']['colors'].items():
        if cat == 'primitive': continue
        if isinstance(scales, dict):
            for shade, tok in scales.items():
                if isinstance(tok, dict) and 'value' in tok:
                    css += f'  --color-{cat}-{shade}: {tok[\"value\"]};\\n'

# Spacing
if 'base' in tokens and 'spacing' in tokens['base']:
    for name, tok in tokens['base']['spacing'].items():
        if isinstance(tok, dict) and 'value' in tok:
            css += f'  --space-{name}: {tok[\"value\"]};\\n'

css += '}\\n'

with open('$OUTPUT_DIR/web/tokens.css', 'w') as f:
    f.write(css)
"
        success "CSS: $OUTPUT_DIR/web/tokens.css"
    fi

    # SCSS
    if [ "$format" = "all" ] || [ "$format" = "scss" ]; then
        info "Transforming to SCSS..."
        python3 -c "
import json

with open('$input_file') as f:
    tokens = json.load(f)

scss = ''

if 'base' in tokens and 'colors' in tokens['base']:
    for cat, scales in tokens['base']['colors'].items():
        if cat == 'primitive': continue
        if isinstance(scales, dict):
            for shade, tok in scales.items():
                if isinstance(tok, dict) and 'value' in tok:
                    scss += f'\${cat}-{shade}: {tok[\"value\"]};\\n'

if 'base' in tokens and 'spacing' in tokens['base']:
    for name, tok in tokens['base']['spacing'].items():
        if isinstance(tok, dict) and 'value' in tok:
            scss += f'\$space-{name}: {tok[\"value\"]};\\n'

with open('$OUTPUT_DIR/web/tokens.scss', 'w') as f:
    f.write(scss)
"
        success "SCSS: $OUTPUT_DIR/web/tokens.scss"
    fi

    # iOS Swift
    if [ "$format" = "all" ] || [ "$format" = "ios" ]; then
        info "Transforming to iOS Swift..."
        python3 -c "
import json

with open('$input_file') as f:
    tokens = json.load(f)

swift = 'import UIKit\\n\\nenum DesignTokens {\\n\\n'

# Colors
if 'base' in tokens and 'colors' in tokens['base']:
    swift += '  enum Colors {\\n'
    for cat, scales in tokens['base']['colors'].items():
        if cat == 'primitive': continue
        if isinstance(scales, dict):
            swift += f'    enum {cat.capitalize()} {{ \\n'
            for shade, tok in scales.items():
                if isinstance(tok, dict) and 'value' in tok:
                    swift += f'      static let {shade} = UIColor(hex: \"{tok[\"value\"]}\")\\n'
            swift += '    }\\n'
    swift += '  }\\n\\n'

# Spacing
if 'base' in tokens and 'spacing' in tokens['base']:
    swift += '  enum Spacing {\\n'
    for name, tok in tokens['base']['spacing'].items():
        if isinstance(tok, dict) and 'value' in tok:
            val = tok['value'].replace('px', '')
            swift += f'    static let {name} = CGFloat({val})\\n'
    swift += '  }\\n\\n'

swift += '}\\n'

with open('$OUTPUT_DIR/ios/Tokens.swift', 'w') as f:
    f.write(swift)
"
        success "iOS Swift: $OUTPUT_DIR/ios/Tokens.swift"
    fi

    # Android XML
    if [ "$format" = "all" ] || [ "$format" = "android" ]; then
        info "Transforming to Android XML..."
        python3 -c "
import json

with open('$input_file') as f:
    tokens = json.load(f)

colors = '<?xml version=\"1.0\" encoding=\"utf-8\"?>\\n<resources>\\n'
dimens = '<?xml version=\"1.0\" encoding=\"utf-8\"?>\\n<resources>\\n'

if 'base' in tokens and 'colors' in tokens['base']:
    for cat, scales in tokens['base']['colors'].items():
        if cat == 'primitive': continue
        if isinstance(scales, dict):
            for shade, tok in scales.items():
                if isinstance(tok, dict) and 'value' in tok:
                    colors += f'  <color name=\"{cat}_{shade}\">{tok[\"value\"]}</color>\\n'

if 'base' in tokens and 'spacing' in tokens['base']:
    for name, tok in tokens['base']['spacing'].items():
        if isinstance(tok, dict) and 'value' in tok:
            dimens += f'  <dimen name=\"space_{name}\">{tok[\"value\"]}</dimen>\\n'

colors += '</resources>\\n'
dimens += '</resources>\\n'

with open('$OUTPUT_DIR/android/res/values/colors.xml', 'w') as f:
    f.write(colors)
with open('$OUTPUT_DIR/android/res/values/dimens.xml', 'w') as f:
    f.write(dimens)
"
        success "Android: $OUTPUT_DIR/android/res/values/colors.xml"
        success "Android: $OUTPUT_DIR/android/res/values/dimens.xml"
    fi

    # Tailwind Config
    if [ "$format" = "all" ] || [ "$format" = "tailwind" ]; then
        info "Transforming to Tailwind config..."
        python3 -c "
import json

with open('$input_file') as f:
    tokens = json.load(f)

theme = { 'colors': {}, 'spacing': {}, 'fontFamily': {}, 'fontSize': {} }

if 'base' in tokens and 'colors' in tokens['base']:
    for cat, scales in tokens['base']['colors'].items():
        if cat == 'primitive': continue
        if isinstance(scales, dict):
            theme['colors'][cat] = {}
            for shade, tok in scales.items():
                if isinstance(tok, dict) and 'value' in tok:
                    theme['colors'][cat][shade] = tok['value']

if 'base' in tokens and 'spacing' in tokens['base']:
    for name, tok in tokens['base']['spacing'].items():
        if isinstance(tok, dict) and 'value' in tok:
            theme['spacing'][name] = tok['value']

config = f'''/** @type {{import('tailwindcss').Config}} */
module.exports = {{
  content: ['./src/**/*.{{html,js}}'],
  theme: {{
    extend: {json.dumps(theme, indent=2)}
  }},
  plugins: []
}};'''

with open('$OUTPUT_DIR/tailwind/tailwind.config.js', 'w') as f:
    f.write(config)
"
        success "Tailwind: $OUTPUT_DIR/tailwind/tailwind.config.js"
    fi

    success "Transform complete!"
}

# Full sync pipeline
cmd_sync() {
    header "Running Full Sync Pipeline"

    cmd_extract "$@"
    cmd_transform
}

# Watch for changes (requires fswatch or similar)
cmd_watch() {
    header "Watching for Changes"

    if command -v fswatch &> /dev/null; then
        info "Watching for file changes..."

        if [ ! -f "$TOKEN_FILE" ]; then
            error "Token file not found. Run 'extract' first."
            return 1
        fi

        fswatch -r "$(dirname "$TOKEN_FILE")" --event=Modified | while read -r event; do
            info "Change detected: $event"
            cmd_transform
        done
    else
        warn "fswatch not installed"
        info "Install with: brew install fswatch (macOS) or apt install inotify-tools (Linux)"
        info "Alternatively, use the Python watch mode:"
        info "  python scripts/sync.py watch --file-id <uuid>"
    fi
}

# Compare token versions
cmd_diff() {
    header "Comparing Token Versions"

    local before="${1:-$TOKEN_FILE}"
    local after="${2:-$TOKEN_FILE.old}"

    if [ ! -f "$before" ]; then
        error "Before file not found: $before"
        return 1
    fi

    if [ ! -f "$after" ]; then
        warn "After file not found: $after"
        warn "Comparing before with current..."
        after="$before"
    fi

    info "Before: $before"
    info "After: $after"

    python3 -c "
import json

with open('$before') as f:
    before = json.load(f)
with open('$after') as f:
    after = json.load(f)

def flatten(obj, prefix=''):
    result = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict) and 'value' in v and 'type' in v:
                result[f'{prefix}{k}' if prefix else k] = v['value']
            else:
                result.update(flatten(v, f'{prefix}{k}_' if prefix else f'{k}_'))
    return result

before_flat = flatten(before)
after_flat = flatten(after)

added = set(after_flat.keys()) - set(before_flat.keys())
removed = set(before_flat.keys()) - set(after_flat.keys())
common = set(before_flat.keys()) & set(after_flat.keys())

changed = [(k, before_flat[k], after_flat[k]) for k in common if before_flat[k] != after_flat[k]]

print()
print(f'  Added: {len(added)} tokens')
print(f'  Removed: {len(removed)} tokens')
print(f'  Changed: {len(changed)} tokens')
print()

if changed:
    print('Changed tokens:')
    for k, b, a in changed[:10]:
        print(f'  {k}: {b} -> {a}')
    if len(changed) > 10:
        print(f'  ... and {len(changed) - 10} more')
"

    success "Diff complete!"
}

# Clean generated files
cmd_clean() {
    header "Cleaning Generated Files"

    if [ -d "$OUTPUT_DIR" ]; then
        rm -rf "$OUTPUT_DIR"
        success "Cleaned: $OUTPUT_DIR"
    fi

    if [ -f "$TOKEN_FILE" ]; then
        rm -f "$TOKEN_FILE"
        success "Cleaned: $TOKEN_FILE"
    fi

    success "Clean complete!"
}

# Show help
show_help() {
    cat << 'EOF'
penpot-design-system-sync - Design Token Sync Workflow

Usage:
    ./sync-workflow.sh <command> [options]

Commands:
    extract    Extract tokens from Penpot to JSON
    transform  Transform tokens to CSS/SCSS/iOS/Android/Tailwind
    sync       Run full sync pipeline (extract + transform)
    watch      Watch for file changes and auto-transform
    diff       Compare token versions
    clean      Clean generated files
    help       Show this help message

Environment Variables:
    PENPOT_API_KEY    Your Penpot API key
    PENPOT_URL        Penpot instance URL (default: https://penpot.app)
    TOKEN_FILE        Token JSON file path (default: ./tokens.json)
    OUTPUT_DIR        Output directory (default: ./dist)

Examples:
    # Extract tokens (requires PENPOT_API_KEY)
    PENPOT_API_KEY=xxx ./sync-workflow.sh extract

    # Generate sample tokens
    ./sync-workflow.sh extract

    # Transform to all formats
    ./sync-workflow.sh transform

    # Transform to specific format
    ./sync-workflow.sh transform --format css

    # Full pipeline
    ./sync-workflow.sh sync

    # Compare versions
    ./sync-workflow.sh diff tokens-v1.json tokens-v2.json

    # Clean all generated files
    ./sync-workflow.sh clean
EOF
}

# Main entry point
main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        extract)
            cmd_extract "$@"
            ;;
        transform)
            cmd_transform "$@"
            ;;
        sync)
            cmd_sync "$@"
            ;;
        watch)
            cmd_watch "$@"
            ;;
        diff)
            cmd_diff "$@"
            ;;
        clean)
            cmd_clean "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main with all arguments
main "$@"
