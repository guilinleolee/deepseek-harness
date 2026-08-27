#!/bin/bash
# =============================================================================
# Dragon Brain 初始化脚本 V4 (简化版)
# 用法: ./init-brain.sh <project_name> [--template <template_id>]
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/../memory"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 帮助信息
show_help() {
    cat << 'EOF'
Dragon Brain 初始化脚本

用法: $0 <project_name> [选项]

选项:
  --template <id>  使用模板 (tech-startup | lifestyle | finance)
  -h, --help       显示帮助

示例:
  $0 "我的科技博客" --template tech-startup
EOF
}

# 解析参数
PROJECT_NAME=""
TEMPLATE_ID=""
PROJECT_DIR="$HOME/.dragon-engine/projects"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) show_help; exit 0 ;;
        --template) TEMPLATE_ID="$2"; shift 2 ;;
        --dir) PROJECT_DIR="$2"; shift 2 ;;
        *) [ -z "$PROJECT_NAME" ] && PROJECT_NAME="$1"; shift ;;
    esac
done

# 验证参数
if [ -z "$PROJECT_NAME" ]; then
    log_error "请提供项目名称"
    exit 1
fi

# 生成项目 ID
PROJECT_ID=$(echo "$PROJECT_NAME" | \
    tr '[:upper:]' '[:lower:]' | \
    tr -cs 'a-z0-9' '-' | \
    tr -s '-' | \
    sed 's/^-//;s/-$//')

[ -z "$PROJECT_ID" ] && PROJECT_ID="project-$(date +%s)"

# 创建项目目录
BRAIN_DIR="$PROJECT_DIR/$PROJECT_ID"
mkdir -p "$BRAIN_DIR/memory" "$BRAIN_DIR/assets" "$BRAIN_DIR/exports"

log_info "创建项目目录: $BRAIN_DIR"

# 检查是否已存在
if [ -f "$BRAIN_DIR/brain.json" ]; then
    log_warn "项目已存在: $PROJECT_ID"
    read -p "是否覆盖? (y/N): " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
fi

CREATED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# 创建 Node.js 临时脚本
NODE_TEMP=$(mktemp --suffix=.js)

cat > "$NODE_TEMP" << 'NODEEOF'
const fs = require('fs');
const path = require('path');

// 从命令行参数获取
const args = process.argv.slice(2);
const projectName = args[0];
const projectId = args[1];
const templateId = args[2];
const templatesDir = args[3];
const outputDir = args[4];
const createdAt = new Date().toISOString();

const brainDir = path.join(outputDir, projectId);
const brainFile = path.join(brainDir, 'brain.json');

// 空白 Brain
const blankBrain = {
    project_id: projectId,
    project_name: projectName,
    brand: { name: projectName, niche: '', audience: '', personality: '', tone: '', values: [] },
    style: {
        colors: { primary: '#333333', secondary: '#666666', accent: '#E74C3C', background: '#FFFFFF', text: '#1A1A1A' },
        fonts: { heading: 'Arial', body: 'Arial', accent: 'Georgia' },
        templates: [], image_style: '', layout_preference: ''
    },
    platforms: {
        xiaohongshu: { enabled: true, aspect_ratio: '3:4', hashtags: [] },
        douyin: { enabled: true, aspect_ratio: '9:16', hashtags: [] },
        wechat: { enabled: false, account_type: 'subscription' },
        youtube: { enabled: false, thumbnail_style: '16:9' },
        instagram: { enabled: false, aspect_ratio: '1:1' },
        twitter: { enabled: false, aspect_ratio: '16:9' }
    },
    context: { recent_tasks: [], successful_prompts: [], preferences: {}, constraints: [] },
    compliance: { license: 'MIT', attribution_required: false, custom_rules: [] },
    created_at: createdAt,
    updated_at: createdAt
};

let brain = blankBrain;

// 模板合并
if (templateId) {
    const templateFile = path.join(templatesDir, 'template-' + templateId + '.json');
    if (fs.existsSync(templateFile)) {
        try {
            const t = JSON.parse(fs.readFileSync(templateFile, 'utf8'));
            brain = {
                project_id: projectId,
                project_name: projectName,
                template_id: t.template_id || templateId,
                description: t.description || '',
                brand: {
                    name: projectName,
                    niche: t.brand?.niche || '',
                    audience: t.brand?.audience || '',
                    personality: t.brand?.personality || '',
                    tone: t.brand?.tone || '',
                    values: t.brand?.values || []
                },
                style: t.style || blankBrain.style,
                platforms: t.platforms || blankBrain.platforms,
                compliance: t.compliance || blankBrain.compliance,
                context: blankBrain.context,
                created_at: createdAt,
                updated_at: createdAt
            };
            console.log('Using template: ' + templateId);
        } catch (e) {
            console.error('Template error: ' + e.message);
        }
    } else {
        console.error('Template not found: ' + templateId);
    }
}

// 写入文件
fs.writeFileSync(brainFile, JSON.stringify(brain, null, 2));
console.log('SUCCESS');
NODEEOF

# 执行 Node.js 脚本
node "$NODE_TEMP" "$PROJECT_NAME" "$PROJECT_ID" "$TEMPLATE_ID" "$TEMPLATES_DIR" "$PROJECT_DIR"
RESULT=$?
rm -f "$NODE_TEMP"

# 检查结果
if [ $RESULT -eq 0 ]; then
    mkdir -p "$HOME/.dragon-engine"
    echo "$PROJECT_ID" > "$HOME/.dragon-engine/current_project"

    echo ""
    log_info "✅ Dragon Brain 已创建"
    echo ""
    echo "  项目 ID:    $PROJECT_ID"
    echo "  项目名称:    $PROJECT_NAME"
    echo "  存储路径:    $BRAIN_DIR/brain.json"
    echo "  当前项目:    $PROJECT_ID"
    echo ""
    echo "📋 下一步:"
    echo "   1. 查看: node -e \"console.log(JSON.parse(require('fs').readFileSync('$HOME/.dragon-engine/projects/$PROJECT_ID/brain.json','utf8'))\""
    echo "   2. 列表: ./list-projects.sh --details"
    echo "   3. 查询: ./query-brain.sh --project $PROJECT_ID"
    echo ""
else
    log_error "创建失败"
    exit 1
fi
