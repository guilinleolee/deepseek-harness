#!/bin/bash
#===============================================================================
# free-claude-code 健康检查脚本
# Usage: bash health-check.sh [--verbose]
#===============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

VERBOSE=false
if [[ "$1" == "--verbose" || "$1" == "-v" ]]; then
    VERBOSE=true
fi

echo "=============================================="
echo "  free-claude-code 健康检查"
echo "=============================================="

FAILED=0
PASSED=0

check() {
    local name="$1"
    local cmd="$2"

    if eval "$cmd" > /dev/null 2>&1; then
        log_success "$name"
        ((PASSED++))
        return 0
    else
        log_error "$name"
        ((FAILED++))
        return 1
    fi
}

check_json() {
    local name="$1"
    local cmd="$2"

    if RESULT=$(eval "$cmd" 2>/dev/null); then
        if echo "$RESULT" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
            log_success "$name"
            ((PASSED++))
            if [ "$VERBOSE" = true ]; then
                echo "    $RESULT" | python3 -m json.tool 2>/dev/null | head -20
            fi
            return 0
        fi
    fi
    log_error "$name"
    ((FAILED++))
    return 1
}

echo ""
echo "--- 代理服务检查 ---"
check "代理服务 (localhost:8082)" "curl -sf http://localhost:8082/health"
check_json "代理健康端点" "curl -s http://localhost:8082/health"

echo ""
echo "--- 本地 Provider 检查 ---"

# Ollama
if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
    log_success "Ollama 服务运行中"
    ((PASSED++))
    if [ "$VERBOSE" = true ]; then
        OLLAMA_MODELS=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; data=json.load(sys.stdin); print('\n'.join([m['name'] for m in data.get('models',[])]))" 2>/dev/null || echo "无法获取模型列表")
        echo "    已安装模型:"
        echo "$OLLAMA_MODELS" | while read -r model; do echo "      - $model"; done
    fi
else
    log_warn "Ollama 服务未运行 (跳过)"
fi

# LM Studio
if curl -sf http://localhost:1234/v1/models > /dev/null 2>&1; then
    log_success "LM Studio 服务运行中"
    ((PASSED++))
    if [ "$VERBOSE" = true ]; then
        LM_MODELS=$(curl -s http://localhost:1234/v1/models | python3 -c "import sys,json; data=json.load(sys.stdin); print('\n'.join([m['id'] for m in data.get('data',[])]))" 2>/dev/null || echo "无法获取模型列表")
        echo "    已加载模型:"
        echo "$LM_MODELS" | while read -r model; do echo "      - $model"; done
    fi
else
    log_warn "LM Studio 服务未运行 (跳过)"
fi

# llama.cpp
if curl -sf http://localhost:8080/v1/models > /dev/null 2>&1; then
    log_success "llama.cpp 服务器运行中"
    ((PASSED++))
else
    log_warn "llama.cpp 服务器未运行 (跳过)"
fi

echo ""
echo "--- 环境变量检查 ---"
if [ -n "$ANTHROPIC_AUTH_TOKEN" ]; then
    log_success "ANTHROPIC_AUTH_TOKEN 已设置"
    ((PASSED++))
else
    log_warn "ANTHROPIC_AUTH_TOKEN 未设置 (使用默认值 'freecc')"
fi

if [ -n "$ANTHROPIC_BASE_URL" ]; then
    log_success "ANTHROPIC_BASE_URL: $ANTHROPIC_BASE_URL"
    ((PASSED++))
else
    log_warn "ANTHROPIC_BASE_URL 未设置 (使用默认值)"
fi

if [ -f "$(dirname "$(dirname "${BASH_SOURCE[0]}")")/free-claude-code/.env" ]; then
    log_success ".env 配置文件存在"
    ((PASSED++))
else
    log_error ".env 配置文件不存在"
    ((FAILED++))
fi

echo ""
echo "=============================================="
echo "  健康检查汇总"
echo "  通过: $PASSED"
echo "  失败: $FAILED"
echo "=============================================="

if [ $FAILED -gt 0 ]; then
    echo ""
    log_error "部分检查失败，请查看上述警告"
    exit 1
else
    echo ""
    log_success "全部检查通过!"
    exit 0
fi
