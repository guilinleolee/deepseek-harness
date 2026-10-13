#!/usr/bin/env bash
# -*- coding: utf-8 -*-
"""
===============================================================================
free-llm-tier-router 安装脚本
Usage: bash scripts/setup.sh [--provider ollama|lmstudio|llamacpp|openrouter|deepseek|nvidia]
===============================================================================
"""

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIGS_DIR="$SKILL_DIR/configs"

echo "=================================================="
echo "  free-llm-tier-router 安装向导"
echo "=================================================="
echo ""

# 解析参数
PROVIDER="${1:-all}"

# 检查 Python 环境
check_python() {
    echo "[检查] Python 环境..."
    if command -v python3 &> /dev/null; then
        PYTHON="python3"
    elif command -v python &> /dev/null; then
        PYTHON="python"
    else
        echo "[错误] 未找到 Python，请先安装 Python 3.8+"
        exit 1
    fi
    echo "  → Python: $($PYTHON --version)"
}

# 安装依赖
install_dependencies() {
    echo ""
    echo "[安装] Python 依赖..."
    $PYTHON -m pip install httpx pydantic python-dotenv --quiet
    echo "  → httpx, pydantic, python-dotenv 已安装"
}

# 检查 Provider 服务
check_provider() {
    local name=$1
    local url=$2
    echo -n "  [$name] $url ... "
    if curl -s --max-time 3 "$url" > /dev/null 2>&1; then
        echo "✅ 在线"
        return 0
    else
        echo "⚠️ 离线"
        return 1
    fi
}

# 检查本地 Provider
check_local_providers() {
    echo ""
    echo "[检查] 本地 LLM Provider..."
    echo ""

    local providers=(
        "ollama:http://localhost:11434"
        "lmstudio:http://localhost:1234"
        "llamacpp:http://localhost:8080"
    )

    for entry in "${providers[@]}"; do
        local name="${entry%%:*}"
        local url="${entry##*:}"
        check_provider "$name" "$url" || true
    done
}

# 检查云端 Provider
check_cloud_providers() {
    echo ""
    echo "[检查] 云端 Provider 配置..."
    echo ""

    # 检查配置文件
    if [[ -f "$CONFIGS_DIR/.env" ]]; then
        source "$CONFIGS_DIR/.env"

        if [[ -n "$OPENROUTER_API_KEY" ]]; then
            echo "  [openrouter] API Key: ✅ 已配置"
        else
            echo "  [openrouter] API Key: ⚠️ 未配置"
        fi

        if [[ -n "$DEEPSEEK_API_KEY" ]]; then
            echo "  [deepseek] API Key: ✅ 已配置"
        else
            echo "  [deepseek] API Key: ⚠️ 未配置"
        fi

        if [[ -n "$NVIDIA_API_KEY" ]]; then
            echo "  [nvidia] API Key: ✅ 已配置"
        else
            echo "  [nvidia] API Key: ⚠️ 未配置"
        fi
    else
        echo "  ⚠️ 未找到 .env 配置文件"
        echo "  → 请复制 configs/.env.example 为 .env 并填写 API Key"
    fi
}

# 验证 Tier Router 引擎
verify_router() {
    echo ""
    echo "[验证] Tier Router 引擎..."
    if [[ -f "$SCRIPT_DIR/tier_router.py" ]]; then
        echo "  → tier_router.py: ✅"
        $PYTHON "$SCRIPT_DIR/tier_router.py" status 2>/dev/null && echo "  → 引擎验证: ✅" || echo "  → 引擎验证: ⚠️ 需要检查"
    else
        echo "  → tier_router.py: ⚠️ 未找到"
    fi
}

# 主流程
main() {
    check_python
    install_dependencies

    case "$PROVIDER" in
        ollama|lmstudio|llamacpp)
            check_local_providers
            ;;
        openrouter|deepseek|nvidia)
            check_cloud_providers
            ;;
        all)
            check_local_providers
            check_cloud_providers
            ;;
        *)
            echo "[错误] 未知 Provider: $PROVIDER"
            echo "支持的 Provider: ollama, lmstudio, llamacpp, openrouter, deepseek, nvidia, all"
            exit 1
            ;;
    esac

    verify_router

    echo ""
    echo "=================================================="
    echo "  安装完成!"
    echo "=================================================="
    echo ""
    echo "  后续步骤:"
    echo "  1. 复制配置文件: cp configs/.env.example configs/.env"
    echo "  2. 填写 API Key"
    echo "  3. 启动本地 Provider (Ollama/LM Studio/llama.cpp)"
    echo "  4. 测试路由: python scripts/tier_router.py route '写一段Python代码'"
    echo ""
}

main
