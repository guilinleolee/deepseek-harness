---
name: dragon-brain
description: >
  天龙引擎项目上下文记忆系统 · 存储品牌定位、目标受众、风格偏好等业务上下文
  类似于 SlideSmith 的 Brain 系统，为每个项目维护独立的记忆上下文
version: 1.0.0
status: production
license: MIT
author: dragon-engine
created: 2026-08-17
triggers:
  - "项目上下文"
  - "Brain"
  - "品牌记忆"
  - "项目设置"
  - "context"
  - "brand"
  - "dragon brain"
phrases:
  - "初始化项目Brain"
  - "查询项目上下文"
  - "更新品牌信息"
  - "切换项目"
  - "项目记忆"
tags:
  - memory
  - context
  - project
  - brand
  - identity
upstream: []
---

# 🧠 Dragon Brain · 天龙引擎项目上下文记忆系统 V1.0

> **一句话**：为每个项目维护独立的品牌记忆、风格偏好、业务上下文，让 AI 生成内容始终保持一致性。

---

## 1. 系统概述

### 1.1 什么是 Brain？

Brain 是项目的「记忆中枢」，存储：
- **品牌信息**：名称、定位、受众、人格
- **风格偏好**：配色、字体、模板、图片风格
- **业务上下文**：近期任务、偏好设置、约束条件
- **历史资产**：成功的 prompt、模板、素材引用

### 1.2 与 SlideSmith Brain 的区别

| 维度 | SlideSmith Brain | Dragon Brain |
|------|------------------|--------------|
| 用途 | 轮播图生成 | 全品类内容生产 |
| 规模 | 单项目 | 多项目并行 |
| 平台 | TikTok/IG | 9 平台分发 |
| 记忆深度 | 内容风格 | 品牌+业务+合规 |

---

## 2. 数据结构

### 2.1 Brain JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["project_id", "brand", "created_at"],
  "properties": {
    "project_id": {
      "type": "string",
      "description": "项目唯一标识符"
    },
    "project_name": {
      "type": "string",
      "description": "项目显示名称"
    },
    "brand": {
      "type": "object",
      "required": ["name", "niche"],
      "properties": {
        "name": {
          "type": "string",
          "description": "品牌名称"
        },
        "niche": {
          "type": "string",
          "description": "品牌定位/细分领域"
        },
        "audience": {
          "type": "string",
          "description": "目标受众描述"
        },
        "personality": {
          "type": "string",
          "description": "品牌人格（专业/亲切/幽默等）"
        },
        "tone": {
          "type": "string",
          "description": "内容语气（正式/口语/学术等）"
        },
        "values": {
          "type": "array",
          "items": { "type": "string" },
          "description": "品牌核心价值观"
        }
      }
    },
    "style": {
      "type": "object",
      "properties": {
        "colors": {
          "type": "object",
          "properties": {
            "primary": { "type": "string" },
            "secondary": { "type": "string" },
            "accent": { "type": "string" },
            "background": { "type": "string" },
            "text": { "type": "string" }
          }
        },
        "fonts": {
          "type": "object",
          "properties": {
            "heading": { "type": "string" },
            "body": { "type": "string" },
            "accent": { "type": "string" }
          }
        },
        "templates": {
          "type": "array",
          "items": { "type": "string" },
          "description": "常用模板 ID 列表"
        },
        "image_style": {
          "type": "string",
          "description": "图片风格偏好"
        },
        "layout_preference": {
          "type": "string",
          "description": "布局偏好"
        }
      }
    },
    "platforms": {
      "type": "object",
      "description": "各平台配置",
      "properties": {
        "xiaohongshu": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean" },
            "aspect_ratio": { "type": "string" },
            "hashtags": { "type": "array", "items": { "type": "string" } }
          }
        },
        "douyin": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean" },
            "aspect_ratio": { "type": "string" },
            "hashtags": { "type": "array", "items": { "type": "string" } }
          }
        },
        "wechat": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean" },
            "account_type": { "type": "string" }
          }
        },
        "youtube": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean" },
            "thumbnail_style": { "type": "string" }
          }
        }
      }
    },
    "context": {
      "type": "object",
      "properties": {
        "recent_tasks": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "task_id": { "type": "string" },
              "type": { "type": "string" },
              "prompt": { "type": "string" },
              "success": { "type": "boolean" },
              "created_at": { "type": "string" }
            }
          }
        },
        "successful_prompts": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "type": { "type": "string" },
              "prompt": { "type": "string" },
              "success_rate": { "type": "number" },
              "last_used": { "type": "string" }
            }
          }
        },
        "preferences": {
          "type": "object",
          "description": "用户偏好设置"
        },
        "constraints": {
          "type": "array",
          "items": { "type": "string" },
          "description": "业务约束条件"
        }
      }
    },
    "compliance": {
      "type": "object",
      "properties": {
        "license": {
          "type": "string",
          "description": "内容 License 要求"
        },
        "attribution_required": {
          "type": "boolean"
        },
        "custom_rules": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

### 2.2 存储位置

```
~/.dragon-engine/
└── projects/
    └── {project_id}/
        ├── brain.json           # 项目 Brain 数据
        ├── memory/              # 项目记忆文件
        │   └── {date}.md       # 按日期归档
        ├── assets/              # 项目资产
        └── state.json           # 任务状态
```

---

## 3. 核心脚本

### 3.1 init-brain.sh - 初始化项目

```bash
#!/bin/bash
# Dragon Brain 初始化脚本
# 用法: ./init-brain.sh <project_name> [--template <template_id>]

set -e

PROJECT_NAME="${1:-}"
TEMPLATE="${2:-}"

if [ -z "$PROJECT_NAME" ]; then
    echo "❌ 请提供项目名称"
    echo "用法: ./init-brain.sh <project_name> [--template <template_id>]"
    exit 1
fi

# 生成项目 ID
PROJECT_ID=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')

# 创建项目目录
BRAIN_DIR="$HOME/.dragon-engine/projects/$PROJECT_ID"
mkdir -p "$BRAIN_DIR/memory" "$BRAIN_DIR/assets"

# 根据模板生成 brain.json
if [ "$TEMPLATE" == "--template" ] && [ -n "$3" ]; then
    # 使用模板
    cp "$DRAGON_ENGINE_ROOT/skills/dragon-brain/memory/template-$3.json" "$BRAIN_DIR/brain.json"
    # 替换占位符
    sed -i "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" "$BRAIN_DIR/brain.json"
    sed -i "s/{{PROJECT_ID}}/$PROJECT_ID/g" "$BRAIN_DIR/brain.json"
else
    # 生成空白 Brain
    cat > "$BRAIN_DIR/brain.json" << EOF
{
  "project_id": "$PROJECT_ID",
  "project_name": "$PROJECT_NAME",
  "brand": {
    "name": "$PROJECT_NAME",
    "niche": "",
    "audience": "",
    "personality": "",
    "tone": "",
    "values": []
  },
  "style": {
    "colors": {
      "primary": "#333333",
      "secondary": "#666666",
      "accent": "#E74C3C",
      "background": "#FFFFFF",
      "text": "#1A1A1A"
    },
    "fonts": {
      "heading": "Arial",
      "body": "Arial",
      "accent": "Georgia"
    },
    "templates": [],
    "image_style": "",
    "layout_preference": ""
  },
  "platforms": {
    "xiaohongshu": { "enabled": true, "aspect_ratio": "3:4", "hashtags": [] },
    "douyin": { "enabled": true, "aspect_ratio": "9:16", "hashtags": [] },
    "wechat": { "enabled": false, "account_type": "subscription" },
    "youtube": { "enabled": false, "thumbnail_style": "16:9" }
  },
  "context": {
    "recent_tasks": [],
    "successful_prompts": [],
    "preferences": {},
    "constraints": []
  },
  "compliance": {
    "license": "MIT",
    "attribution_required": false,
    "custom_rules": []
  },
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
fi

echo "✅ Brain 已创建: $BRAIN_DIR/brain.json"
echo "📝 请编辑 Brain 数据以完善项目信息"
```

### 3.2 query-brain.sh - 查询上下文

```bash
#!/bin/bash
# Dragon Brain 查询脚本
# 用法: ./query-brain.sh <project_id> [--field <field_path>]

PROJECT_ID="${1:-current}"
FIELD="${2:-}"

if [ "$PROJECT_ID" == "current" ]; then
    PROJECT_ID=$(cat "$HOME/.dragon-engine/current_project" 2>/dev/null || echo "")
fi

if [ -z "$PROJECT_ID" ]; then
    echo "❌ 未指定项目且无当前项目"
    echo "用法: ./query-brain.sh <project_id> [--field <field_path>]"
    exit 1
fi

BRAIN_FILE="$HOME/.dragon-engine/projects/$PROJECT_ID/brain.json"

if [ ! -f "$BRAIN_FILE" ]; then
    echo "❌ 项目 Brain 不存在: $PROJECT_ID"
    exit 1
fi

if [ -n "$FIELD" ]; then
    # jq 格式化输出指定字段
    cat "$BRAIN_FILE" | jq -r "$FIELD"
else
    # 输出完整 Brain
    cat "$BRAIN_FILE" | jq .
fi
```

### 3.3 update-brain.sh - 更新 Brain

```bash
#!/bin/bash
# Dragon Brain 更新脚本
# 用法: ./update-brain.sh <project_id> --field <path> --value <json_value>

PROJECT_ID="${1:-}"
FIELD=""
VALUE=""

while [ $# -gt 0 ]; do
    case "$1" in
        --field)
            FIELD="$2"
            shift 2
            ;;
        --value)
            VALUE="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$PROJECT_ID" ] || [ -z "$FIELD" ]; then
    echo "❌ 缺少必需参数"
    echo "用法: ./update-brain.sh <project_id> --field <path> --value <json_value>"
    exit 1
fi

BRAIN_FILE="$HOME/.dragon-engine/projects/$PROJECT_ID/brain.json"

if [ ! -f "$BRAIN_FILE" ]; then
    echo "❌ 项目 Brain 不存在: $PROJECT_ID"
    exit 1
fi

# 使用 jq 更新字段
TEMP_FILE=$(mktemp)
jq --argjson value "$VALUE" ".$FIELD = \$value | .updated_at = \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"" \
    "$BRAIN_FILE" > "$TEMP_FILE" && mv "$TEMP_FILE" "$BRAIN_FILE"

echo "✅ Brain 已更新: $FIELD"
```

### 3.4 list-projects.sh - 列出项目

```bash
#!/bin/bash
# 列出所有项目
# 用法: ./list-projects.sh [--short]

PROJECTS_DIR="$HOME/.dragon-engine/projects"

if [ ! -d "$PROJECTS_DIR" ]; then
    echo "📂 暂无项目"
    exit 0
fi

if [ "$1" == "--short" ]; then
    # 简洁输出
    for dir in "$PROJECTS_DIR"/*/; do
        PROJECT_ID=$(basename "$dir")
        BRAIN_FILE="$dir/brain.json"
        if [ -f "$BRAIN_FILE" ]; then
            NAME=$(jq -r '.project_name // .project_id' "$BRAIN_FILE")
            echo "$PROJECT_ID: $NAME"
        else
            echo "$PROJECT_ID"
        fi
    done
else
    # 详细输出
    echo "📂 项目列表"
    echo "================"
    for dir in "$PROJECTS_DIR"/*/; do
        PROJECT_ID=$(basename "$dir")
        BRAIN_FILE="$dir/brain.json"
        if [ -f "$BRAIN_FILE" ]; then
            NAME=$(jq -r '.project_name // .project_id' "$BRAIN_FILE")
            UPDATED=$(jq -r '.updated_at // .created_at' "$BRAIN_FILE" | cut -d'T' -f1)
            echo "• $PROJECT_ID"
            echo "  名称: $NAME"
            echo "  更新: $UPDATED"
            echo ""
        fi
    done
fi
```

### 3.5 switch-project.sh - 切换项目

```bash
#!/bin/bash
# 切换当前项目
# 用法: ./switch-project.sh <project_id>

PROJECT_ID="$1"

if [ -z "$PROJECT_ID" ]; then
    echo "❌ 请提供项目 ID"
    echo "用法: ./switch-project.sh <project_id>"
    exit 1
fi

BRAIN_FILE="$HOME/.dragon-engine/projects/$PROJECT_ID/brain.json"

if [ ! -f "$BRAIN_FILE" ]; then
    echo "❌ 项目不存在: $PROJECT_ID"
    exit 1
fi

echo "$PROJECT_ID" > "$HOME/.dragon-engine/current_project"
echo "✅ 已切换到项目: $PROJECT_ID"
```

---

## 4. 调用协议

### 4.1 Agent 调用方式

```
当用户创建新项目时：
1. 调用 dragon-brain/init-brain.sh 初始化项目
2. 引导用户填写 Brain 基本信息
3. 将项目 ID 写入 ~/.dragon-engine/current_project

当用户请求生成内容时：
1. 读取当前项目的 brain.json
2. 将 Brain 上下文注入到 prompt 中
3. 根据 platforms 配置选择目标平台
4. 生成后自动更新 recent_tasks
```

### 4.2 上下文注入示例

```markdown
## 当前项目 Brain 上下文

**项目**: {{project_name}}
**品牌定位**: {{brand.niche}}
**目标受众**: {{brand.audience}}
**品牌人格**: {{brand.personality}}
**内容语气**: {{brand.tone}}

**配色方案**:
- 主色: {{style.colors.primary}}
- 辅色: {{style.colors.secondary}}
- 强调色: {{style.colors.accent}}

**启用平台**: {{#each platforms}}{{#if this.enabled}}{{@key}}, {{/if}}{{/each}}
```

### 4.3 成功 Prompt 自动记录

生成成功的内容，其 prompt 自动存入 `brain.context.successful_prompts`：

```json
{
  "type": "xiaohongshu_cover",
  "prompt": "...",
  "success_rate": 0.85,
  "last_used": "2026-08-17T10:30:00Z"
}
```

---

## 5. 模板系统

### 5.1 内置模板

| 模板 ID | 适用场景 | 特点 |
|---------|---------|------|
| `tech-startup` | 科技创业 | 现代简约、科技蓝 |
| `lifestyle` | 生活时尚 | 温暖色调、人文气息 |
| `finance` | 财经分析 | 专业稳重、数据可视化 |
| `education` | 教育培训 | 清晰条理、亲和力 |
| `ecommerce` | 电商带货 | 高对比、行动号召 |

### 5.2 模板示例 (tech-startup.json)

```json
{
  "template_id": "tech-startup",
  "name": "科技创业",
  "description": "适合科技创业公司/产品的内容风格",
  "brand": {
    "niche": "科技创新",
    "personality": "前沿、专业、活力",
    "tone": "科技感、专业但亲切",
    "values": ["创新", "效率", "未来"]
  },
  "style": {
    "colors": {
      "primary": "#0066FF",
      "secondary": "#00D4AA",
      "accent": "#FF6B35",
      "background": "#F8FAFC",
      "text": "#1E293B"
    },
    "fonts": {
      "heading": "Inter",
      "body": "Noto Sans SC",
      "accent": "JetBrains Mono"
    },
    "image_style": "modern-tech, gradient-blur, glassmorphism",
    "layout_preference": "clean-minimal, generous-whitespace"
  },
  "platforms": {
    "xiaohongshu": {
      "enabled": true,
      "aspect_ratio": "3:4",
      "hashtags": ["#科技创新", "#创业干货", "#科技生活"]
    },
    "douyin": {
      "enabled": true,
      "aspect_ratio": "9:16",
      "hashtags": ["#科技", "#创业", "#干货"]
    }
  }
}
```

---

## 6. 与其他 Skills 的集成

### 6.1 与 ppt-master 集成

```javascript
// ppt-master 生成时自动注入 Brain 上下文
const brain = require('./dragon-brain/query-brain.js');
const context = brain.getContext(projectId);

// 生成 PPT 时使用 Brain 中的配色和字体
const pptx = generatePPTX({
  theme: {
    colors: context.style.colors,
    fonts: context.style.fonts
  },
  template: context.style.templates[0]
});
```

### 6.2 与 baoyu-slide-deck 集成

```javascript
// 社交媒体内容生成时引用 Brain
const brain = require('./dragon-brain/query-brain.js');
const context = brain.getContext(projectId);

// 根据平台选择风格
const style = brain.selectPlatformStyle(context, 'xiaohongshu');
```

### 6.3 与 multi-platform-publisher 集成

```javascript
// 发布时验证合规性
const compliance = brain.getCompliance(projectId);
publisher.validateCompliance({
  license: compliance.license,
  attribution: compliance.attribution_required
});
```

---

## 7. 故障排除

| 问题 | 解决方案 |
|------|---------|
| 项目 Brain 不存在 | 运行 `./init-brain.sh <name>` 创建 |
| 查询失败 | 检查 `~/.dragon-engine/` 目录是否存在 |
| 更新失败 | 确认 brain.json 格式正确，运行 `jq . brain.json` 验证 |
| 忘记当前项目 | `cat ~/.dragon-engine/current_project` |

---

## 8. 测试

```bash
# 测试 Brain 初始化
$ cd skills/dragon-brain/scripts
$ ./init-brain.sh "测试项目"
✅ Brain 已创建: ~/.dragon-engine/projects/ce-shi-xiang-mu/brain.json

# 测试查询
$ ./query-brain.sh ce-shi-xiang-mu
{
  "project_id": "ce-shi-xiang-mu",
  ...
}

# 测试更新
$ ./update-brain.sh ce-shi-xiang-mu --field "brand.niche" --value "\"人工智能\""
✅ Brain 已更新: brand.niche

# 测试切换
$ ./switch-project.sh ce-shi-xiang-mu
✅ 已切换到项目: ce-shi-xiang-mu
```

---

## 9. 许可与归属

**License**: MIT ✅

**参考项目**:
- [SlideSmith Brain System](https://github.com/athcagithub/SlideSmith) - 灵感来源

---

*最后更新: 2026-08-17 · v1.0.0*
