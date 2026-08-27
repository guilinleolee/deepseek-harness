#!/bin/bash
#===============================================================================
# free-llm-local-bridge 一键安装脚本
# Usage: bash setup.sh [--provider ollama|lmstudio|llamacpp]
#===============================================================================

set -e

PROVIDER="${1:-ollama}"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "=============================================="
echo "  free-llm-local-bridge 一键安装"
echo "  Provider: $PROVIDER"
echo "=============================================="

# Step 1: 检查 uv
log_info "检查 uv 包管理器..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    log_success "uv 已安装: $UV_VERSION"
else
    log_info "安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source "$HOME/.cargo/env" 2>/dev/null || true
    log_success "uv 安装完成"
fi

# Step 2: 检查 Python 3.14
log_info "检查 Python 3.14..."
if uv python list | grep -q "3.14"; then
    log_success "Python 3.14 已安装"
else
    log_info "安装 Python 3.14..."
    uv python install 3.14
    log_success "Python 3.14 安装完成"
fi

# Step 3: 克隆仓库
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -d "$PARENT_DIR/free-claude-code" ]; then
    log_warn "free-claude-code 已存在，跳过克隆"
else
    log_info "克隆 free-claude-code..."
    git clone https://github.com/Alishahryar1/free-claude-code.git "$PARENT_DIR/free-claude-code"
    log_success "克隆完成"
fi

# Step 4: 安装依赖
log_info "安装 Python 依赖..."
cd "$PARENT_DIR/free-claude-code"
uv sync
log_success "依赖安装完成"

# Step 5: 配置环境变量
log_info "配置环境变量..."
if [ -f "$PARENT_DIR/free-claude-code/.env" ]; then
    log_warn ".env 已存在，跳过创建"
else
    cp "$PARENT_DIR/free-claude-code/.env.example" "$PARENT_DIR/free-claude-code/.env"
    log_success "创建 .env 文件，请编辑配置 Provider"
fi

# Step 6: 检查本地 Provider
log_info "检查本地 Provider ($PROVIDER)..."

case "$PROVIDER" in
    ollama)
        if command -v ollama &> /dev/null; then
            OLLAMA_VERSION=$(ollama --version)
            log_success "Ollama 已安装: $OLLAMA_VERSION"
            log_info "下载推荐模型..."
            ollama pull llama3.1:8b 2>/dev/null || log_warn "模型下载失败，请手动运行: ollama pull llama3.1:8b"
        else
            log_error "Ollama 未安装，请运行以下命令安装:"
            echo "  Linux: curl -fsSL https://ollama.com/install.sh | sh"
            echo "  macOS: brew install ollama"
            echo "  Windows: 下载 https://ollama.com/download"
        fi
        ;;
    lmstudio)
        log_info "LM Studio 需要手动安装: https://lmstudio.ai/"
        log_info "启动后点击 Server -> Enable Server 启用 API"
        ;;
    llamacpp)
        log_info "llama.cpp 需要从源码编译: https://github.com/ggerganov/llama.cpp"
        log_info "编译后运行: ./server -m models/xxx.gguf --port 8080"
        ;;
esac

echo ""
echo "=============================================="
echo "  安装完成!"
echo "=============================================="
echo ""
echo "下一步:"
echo "  1. 启动本地 Provider"
echo "     $PROVIDER serve"
echo ""
echo "  2. 启动代理服务"
echo "     cd $PARENT_DIR/free-claude-code"
echo "     uv run uvicorn server:app --host 0.0.0.0 --port 8082"
echo ""
echo "  3. 启动 Claude Code"
echo "     export ANTHROPIC_AUTH_TOKEN='freecc'"
echo "     export ANTHROPIC_BASE_URL='http://localhost:8082'"
echo "     claude"
echo ""
