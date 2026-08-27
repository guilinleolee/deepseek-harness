#!/bin/bash
# =============================================================================
# Dragon Brain 列表脚本
# 用法: ./list-projects.sh [--short] [--details]
# =============================================================================

BRAIN_DIR="${HOME}/.dragon-engine/projects"

# 颜色
GREEN='\033[0;32m'
NC='\033[0m'

FORMAT="normal"

# 解析参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        --short)
            FORMAT="short"
            shift
            ;;
        --details)
            FORMAT="details"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# 检查目录
if [ ! -d "$BRAIN_DIR" ]; then
    echo "📂 暂无项目 (目录不存在)"
    exit 0
fi

# 读取当前项目
CURRENT_PROJECT=""
if [ -f "${HOME}/.dragon-engine/current_project" ]; then
    CURRENT_PROJECT=$(cat "${HOME}/.dragon-engine/current_project")
fi

# 获取项目列表
PROJECTS=$(ls -1d "$BRAIN_DIR"/*/ 2>/dev/null | xargs -I {} basename {} | sort)

if [ -z "$PROJECTS" ]; then
    echo "📂 暂无项目"
    exit 0
fi

case "$FORMAT" in
    short)
        echo "项目列表:"
        for dir in $PROJECTS; do
            CURRENT_MARK=""
            if [ "$dir" = "$CURRENT_PROJECT" ]; then
                CURRENT_MARK=" ← 当前"
            fi
            echo "  • $dir$CURRENT_MARK"
        done
        ;;

    details)
        echo "═══════════════════════════════════════════════════════"
        echo "                    Dragon Brain 项目列表              "
        echo "═══════════════════════════════════════════════════════"
        for dir in $PROJECTS; do
            BRAIN_FILE="$BRAIN_DIR/$dir/brain.json"
            CURRENT_MARK=""

            if [ "$dir" = "$CURRENT_PROJECT" ]; then
                CURRENT_MARK=" ✅ (当前)"
            fi

            echo ""
            echo -e "${GREEN}📁 $dir$CURRENT_MARK${NC}"

            if [ -f "$BRAIN_FILE" ]; then
                # 使用 Node.js 读取 JSON（避免 jq 依赖问题）
                INFO=$(node -e "
                    const fs = require('fs');
                    const brain = JSON.parse(fs.readFileSync('$BRAIN_FILE', 'utf8'));
                    console.log(JSON.stringify({
                        name: brain.project_name || brain.project_id || '$dir',
                        niche: (brain.brand && brain.brand.niche) || '未设置',
                        updated: (brain.updated_at || brain.created_at || '').split('T')[0],
                        platforms: Object.entries(brain.platforms || {})
                            .filter(([k, v]) => v && v.enabled)
                            .map(([k]) => k)
                            .join(', ')
                    }));
                " 2>/dev/null)

                if [ -n "$INFO" ]; then
                    NAME=$(echo "$INFO" | node -e "console.log(JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')).name)")
                    NICHE=$(echo "$INFO" | node -e "console.log(JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')).niche)")
                    PLATFORMS=$(echo "$INFO" | node -e "console.log(JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')).platforms)")
                    UPDATED=$(echo "$INFO" | node -e "console.log(JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')).updated)")

                    echo "   名称: $NAME"
                    echo "   定位: $NICHE"
                    echo "   平台: ${PLATFORMS:-无}"
                    echo "   更新: $UPDATED"
                fi
            fi
        done
        echo ""
        echo "═══════════════════════════════════════════════════════"
        ;;

    *)
        echo "📂 Dragon Brain 项目列表"
        echo "========================"
        for dir in $PROJECTS; do
            BRAIN_FILE="$BRAIN_DIR/$dir/brain.json"
            CURRENT_MARK=""

            if [ "$dir" = "$CURRENT_PROJECT" ]; then
                CURRENT_MARK=" ← 当前项目"
            fi

            if [ -f "$BRAIN_FILE" ]; then
                NAME=$(node -e "
                    const fs = require('fs');
                    const brain = JSON.parse(fs.readFileSync('$BRAIN_FILE', 'utf8'));
                    console.log(brain.project_name || brain.project_id || '$dir');
                " 2>/dev/null)
                echo "• $dir: $NAME$CURRENT_MARK"
            else
                echo "• $dir$CURRENT_MARK"
            fi
        done
        ;;
esac

echo ""
echo "使用 --details 查看详细信息"
