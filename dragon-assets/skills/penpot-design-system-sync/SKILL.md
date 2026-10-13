---
license: UNKNOWN
triggers: ["penpot design system sync", "Penpot Design System Sync"]
---
# Penpot Design System Sync

## L0: 一句话描述 (≤15字)
Penpot设计系统双向同步工具

## L1: 使用场景 (50-100字)
将Penpot设计稿中的设计令牌(颜色/字体/间距/阴影)同步到Style Dictionary/Figma/Tailwind等格式，保持设计与代码的同步更新。适用于设计系统维护、设计-开发协作、多平台输出场景。

## L2: 详细文档

### 核心能力

| 能力 | 功能 | 输出格式 |
|------|------|---------|
| **令牌提取** | 从Penpot文件提取设计令牌 | JSON/YAML |
| **格式转换** | 转换为目标平台格式 | CSS/SCSS/iOS/Android/StyleDict |
| **双向同步** | 设计→代码单向同步 | 代码生成 |
| **版本控制** | 设计令牌版本管理 | Git diff |
| **变更检测** | 检测设计变更并通知 | Diff报告 |

### 架构

```
┌─────────────────────────────────────────────────────────────┐
│  Penpot Design System Sync Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Penpot API                                                │
│   ├── getDesignTokens()  → 提取设计令牌                   │
│   └── getShapeStyles()  →  提取形状样式                   │
│              ↓                                              │
│   ┌─────────────────────────────────────────┐              │
│   │         Token Normalizer                │              │
│   │  • 颜色格式标准化 (#hex/rgba/hsla)    │              │
│   │  • 字体族标准化 (Google Fonts)        │              │
│   │  • 间距值计算 (8px基准)                │              │
│   └─────────────────────────────────────────┘              │
│              ↓                                              │
│   ┌─────────────────────────────────────────┐              │
│   │        Platform Transformer             │              │
│   │  • Style Dictionary (iOS/Android/Web)  │              │
│   │  • Tailwind CSS Config                  │              │
│   │  • CSS Custom Properties                │              │
│   │  • Figma Tokens Plugin                  │              │
│   │  • Theo/Amazon Style Dict             │              │
│   └─────────────────────────────────────────┘              │
│              ↓                                              │
│   Output Formats: CSS/SCSS/JS/TS/iOS/Android/YAML        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 设计令牌结构

```typescript
interface DesignTokens {
  colors: ColorToken[];
  typography: TypographyToken[];
  spacing: SpacingToken[];
  shadows: ShadowToken[];
  borders: BorderToken[];
  radii: RadiusToken[];
  breakpoints: BreakpointToken[];
}

interface ColorToken {
  name: string;
  value: string;
  description?: string;
  category?: 'primary' | 'secondary' | 'neutral' | 'semantic' | 'functional';
  aliases?: string[];
}

interface TypographyToken {
  name: string;
  fontFamily: string;
  fontSize: string;
  fontWeight: string;
  lineHeight: string;
  letterSpacing?: string;
  textAlign?: string;
}
```

### 平台转换映射

| Penpot属性 | Style Dictionary | iOS | Android | Tailwind |
|------------|----------------|-----|----------|----------|
| `fillColor` | `color` | `UIColor` | `color.xml` | `colors` |
| `fontFamily` | `fontFamily` | `UIFont` | `fontFamily` | `fontFamily` |
| `fontSize` | `fontSize` | `CGFloat` | `dimen/sp` | `fontSize` |
| `fontWeight` | `fontWeight` | `UIFont.Weight` | `fontWeight` | `fontWeight` |
| `lineHeight` | `lineHeight` | `CGFloat` | `dimen/dp` | `leading` |
| `rect.width` | `spacing` | `CGFloat` | `dimen/dp` | `spacing` |
| `shadow` | `shadow` | `NSShadow` | `elevation` | `boxShadow` |

### 使用方法

#### 方式1: CLI命令

```bash
# 提取设计令牌
python scripts/sync.py extract --file-id <penpot-file-id> --output tokens.json

# 转换为CSS
python scripts/sync.py transform --input tokens.json --format css --output tokens.css

# 转换为iOS
python scripts/sync.py transform --input tokens.json --format ios --output DesignTokens.swift

# 同步到Style Dictionary
python scripts/sync.py sync --input tokens.json --platforms ios,android,web

# 监听变更
python scripts/sync.py watch --file-id <penpot-file-id> --on-change "echo 'Design updated!'"
```

#### 方式2: Python API

```python
from penpot_sync import PenpotSync

sync = PenpotSync(
    api_key="your-penpot-api-key",
    api_endpoint="https://api.penpot.app/v1"
)

# 提取令牌
tokens = sync.extract_tokens(file_id="uuid")

# 转换格式
css = sync.transform(tokens, format="css", options={
    "prefix": "ds",
    "cssVariables": True
})

# 导出到文件
sync.export(tokens, formats=["ios", "android", "web"], output_dir="./design-system")
```

#### 方式3: MCP工具

```bash
# 使用MCP服务
python scripts/mcp_server.py start --port 5005
```

### 配置示例

#### style-dictionary.config.js

```javascript
module.exports = {
  source: ['tokens/**/*.json'],
  platforms: {
    ios: {
      transforms: ['attribute/cti', 'name/cti/camel', 'color/css'],
      buildPath: 'ios/',
      files: [{
        destination: 'DesignTokens.swift',
        format: 'ios/swiftClass',
        className: 'DesignTokens',
      }]
    },
    android: {
      transforms: ['attribute/cti', 'name/cti/snake', 'color/android'],
      buildPath: 'android/',
      files: [{
        destination: 'tokens.xml',
        format: 'xml/resources',
      }]
    },
    web: {
      transforms: ['attribute/cti', 'name/cti/kebab', 'color/css'],
      buildPath: 'web/',
      files: [{
        destination: 'tokens.css',
        format: 'css/variables',
        options: { outputReferences: true }
      }]
    }
  }
};
```

#### tailwind.config.js

```javascript
module.exports = {
  theme: {
    extend: {
      colors: 'tokens/colors.json',
      fontFamily: 'tokens/typography.json',
      spacing: 'tokens/spacing.json',
    }
  }
}
```

### 变更检测

```bash
# 生成Diff报告
python scripts/sync.py diff --before tokens-v1.json --after tokens-v2.json

# 输出示例
# {
#   "added": ["color-success-light", "spacing-px-1"],
#   "removed": ["color-warning-dim"],
#   "modified": [
#     {"name": "color-primary", "before": "#0055FF", "after": "#0066FF"}
#   ],
#   "breaking": ["color-danger"]  # 删除的语义色=Breaking
# }
```

### 最佳实践

1. **令牌命名**: 使用语义化命名 `color-primary` 而非 `blue-500`
2. **别名系统**: `color-brand` 别名到 `color-primary-500`
3. **版本标签**: 每个设计令牌带版本号便于回溯
4. **变更审查**: Breaking Change需人工确认

### 依赖

```json
{
  "dependencies": {
    "style-dictionary": "^3.1.2",
    "tinycolor2": "^1.6.0",
    "webcolors": "^1.8.1"
  }
}
```

### 目录结构

```
penpot-design-system-sync/
├── SKILL.md                    # 本文件
├── README.md                    # 详细使用文档
├── scripts/
│   ├── sync.py                # 主同步脚本
│   ├── mcp_server.py           # MCP服务器
│   ├── extract.py              # 令牌提取
│   ├── transform.py            # 格式转换
│   └── diff.py                 # 变更对比
├── templates/
│   ├── style-dictionary.config.js    # Style Dictionary配置
│   ├── tailwind.config.js          # Tailwind配置
│   └── figma-tokens.json           # Figma Tokens格式
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

## 关联技能

- `penpot-plugin-development` - 插件开发基础
- `penpot-mcp-integration` - MCP集成
- `style-dictionary` - 设计令牌标准格式
