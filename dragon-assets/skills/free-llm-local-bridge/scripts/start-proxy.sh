#!/bin/bash
#===============================================================================
# free-claude-code 代理服务启动脚本
# Usage: bash start-proxy.sh [--port PORT] [--host HOST] [--provider PROVIDER]
#===============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 默认配置
PORT="${PORT:-8082}"
HOST="${HOST:-0.0.0.0}"
PROVIDER="${PROVIDER:-ollama}"

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --provider)
            PROVIDER="$2"
            shift 2
            ;;
        --background|-b)
            BACKGROUND=true
            shift
            ;;
        --log)
            LOG_FILE="$2"
            shift 2
            ;;
        *)
            log_error "未知参数: $1"
            exit 1
            ;;
    esac
done

# 确定脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$PARENT_DIR/free-claude-code"

echo "=============================================="
echo "  free-claude-code 代理服务启动"
echo "  Provider: $PROVIDER"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "=============================================="

# 检查 .env 文件
if [ ! -f "$PROJECT_DIR/.env" ]; then
    log_warn ".env 文件不存在，创建默认配置..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    log_warn "请编辑 $PROJECT_DIR/.env 配置 Provider"
fi

# 检查 Provider 是否运行
case "$PROVIDER" in
    ollama)
        if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            log_error "Ollama 未运行，请先启动: ollama serve"
            exit 1
        fi
        OLLAMA_MODELS=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | head -5 || echo "无法获取模型列表")
        log_success "Ollama 已运行"
        log_info "已安装模型: $OLLAMA_MODELS"
        ;;
    lmstudio)
        if ! curl -s http://localhost:1234/v1/models > /dev/null 2>&1; then
            log_error "LM Studio 未运行，请启动并启用 Server 模式"
            exit 1
        fi
        log_success "LM Studio 已运行"
        ;;
    llamacpp)
        if ! curl -s http://localhost:8080/v1/models > /dev/null 2>&1; then
            log_error "llama.cpp 服务器未运行，请启动: ./server -m models/xxx.gguf --port 8080"
            exit 1
        fi
        log_success "llama.cpp 服务器已运行"
        ;;
esac

# 启动代理服务
cd "$PROJECT_DIR"

if [ "$BACKGROUND" = true ]; then
    LOG_FILE="${LOG_FILE:-proxy.log}"
    log_info "后台启动代理服务..."
    nohup uv run uvicorn server:app --host "$HOST" --port "$PORT" > "$LOG_FILE" 2>&1 &
    PROXY_PID=$!
    echo "$PROXY_PID" > /tmp/free-claude-code.pid
    sleep 3

    if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
        log_success "代理服务启动成功! PID: $PROXY_PID"
        log_info "日志文件: $LOG_FILE"
        log_info "健康检查: http://localhost:$PORT/health"
    else
        log_error "代理服务启动失败，查看日志: tail -f $LOG_FILE"
        exit 1
    fi
else
    log_info "前台启动代理服务 (Ctrl+C 停止)..."
    log_info ""
    log_info "启动命令:"
    echo "    cd $PROJECT_DIR"
    echo "    uv run uvicorn server:app --host $HOST --port $PORT"
    echo ""
    log_info "Claude Code 连接配置:"
    echo "    export ANTHROPIC_AUTH_TOKEN='freecc'"
    echo "    export ANTHROPIC_BASE_URL='http://localhost:$PORT'"
    echo ""

    uv run uvicorn server:app --host "$HOST" --port "$PORT"
fi
