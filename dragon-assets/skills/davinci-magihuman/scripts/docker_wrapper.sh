#!/bin/bash
# daVinci-MagiHuman Docker封装脚本
# 天龙引擎集成脚本 V1.0

set -e

# 配置
IMAGE_NAME="sandai/magi-human:latest"
CONTAINER_NAME="magihuman-$(date +%s)"
OUTPUT_DIR="${OUTPUT_DIR:-./output}"
GPU_ARGS="${GPU_ARGS:---gpus all}"
MEMORY_ARGS="${MEMORY_ARGS:---shm-size=64g}"

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
    cat << EOF
daVinci-MagiHuman Docker封装脚本

用法: magihuman-docker.sh [命令] [选项]

命令:
    generate     生成视频
    batch        批量生成
    shell        进入容器shell
    logs         查看容器日志
    cleanup      清理容器
    status       查看状态

选项:
    --prompt, -p        视频描述
    --negative, -n      负向提示词 (默认: 低质量, 模糊, 变形)
    --frames, -f        帧数 (默认: 97)
    --fps               帧率 (默认: 24)
    --output, -o        输出路径 (默认: output.mp4)
    --portrait          人像模式
    --scene             场景模式

示例:
    # 生成视频
    ./magihuman-docker.sh generate -p "一个穿着汉服的女子在樱花树下"

    # 人像视频
    ./magihuman-docker.sh generate -p "年轻女性在海边奔跑" --portrait

    # 批量生成
    ./magihuman-docker.sh batch --config batch.json

    # 进入shell
    ./magihuman-docker.sh shell
EOF
}

# 检查Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker未运行，请启动Docker"
        exit 1
    fi

    log_info "Docker检查通过"
}

# 拉取镜像
pull_image() {
    if docker images | grep -q "$IMAGE_NAME"; then
        log_info "镜像已存在，跳过拉取"
    else
        log_info "拉取镜像: $IMAGE_NAME"
        docker pull "$IMAGE_NAME"
    fi
}

# 生成视频
cmd_generate() {
    local prompt=""
    local negative="低质量, 模糊, 变形"
    local frames=97
    local fps=24
    local output="output.mp4"
    local portrait=false
    local scene=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--prompt)
                prompt="$2"
                shift 2
                ;;
            -n|--negative)
                negative="$2"
                shift 2
                ;;
            -f|--frames)
                frames="$2"
                shift 2
                ;;
            --fps)
                fps="$2"
                shift 2
                ;;
            -o|--output)
                output="$2"
                shift 2
                ;;
            --portrait)
                portrait=true
                shift
                ;;
            --scene)
                scene=true
                shift
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done

    if [[ -z "$prompt" ]]; then
        log_error "缺少必要参数: --prompt"
        exit 1
    fi

    mkdir -p "$(dirname "$output")"

    log_info "生成视频..."
    log_info "  提示词: $prompt"
    log_info "  帧数: $frames"
    log_info "  输出: $output"

    docker run --rm \
        $GPU_ARGS \
        $MEMORY_ARGS \
        -v "$(pwd)/$OUTPUT_DIR:/app/output" \
        -w /app \
        "$IMAGE_NAME" \
        python -m magihuman.generate \
            --prompt "$prompt" \
            --negative "$negative" \
            --num_frames "$frames" \
            --fps "$fps" \
            --output "/app/output/$output"

    log_info "视频已保存: $output"
}

# 批量生成
cmd_batch() {
    local config_file=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--config)
                config_file="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$config_file" ]]; then
        log_error "缺少必要参数: --config"
        exit 1
    fi

    log_info "批量生成视频..."
    log_info "  配置文件: $config_file"

    docker run --rm \
        $GPU_ARGS \
        $MEMORY_ARGS \
        -v "$(pwd)/$config_file:/app/config.json" \
        -v "$(pwd)/$OUTPUT_DIR:/app/output" \
        -w /app \
        "$IMAGE_NAME" \
        python -m magihuman.batch --config /app/config.json

    log_info "批量生成完成"
}

# 进入Shell
cmd_shell() {
    docker run -it --rm \
        $GPU_ARGS \
        $MEMORY_ARGS \
        -v "$(pwd)/$OUTPUT_DIR:/app/output" \
        -w /app \
        "$IMAGE_NAME" \
        /bin/bash
}

# 查看日志
cmd_logs() {
    docker logs "${CONTAINER_NAME:-magihuman}" 2>&1 | tail -100
}

# 清理
cmd_cleanup() {
    log_info "清理容器..."
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
    docker image prune -f
    log_info "清理完成"
}

# 查看状态
cmd_status() {
    echo "=== daVinci-MagiHuman 状态 ==="
    echo ""
    echo "镜像:"
    docker images "$IMAGE_NAME" 2>/dev/null || echo "  未安装"
    echo ""
    echo "容器:"
    docker ps -a | grep -E "magihuman|$IMAGE_NAME" || echo "  无运行中容器"
    echo ""
    echo "输出目录: $OUTPUT_DIR"
    if [[ -d "$OUTPUT_DIR" ]]; then
        echo "生成文件数: $(find "$OUTPUT_DIR" -name "*.mp4" 2>/dev/null | wc -l)"
    fi
}

# 主入口
main() {
    check_docker

    local command="${1:-help}"
    shift || true

    case $command in
        generate)
            pull_image
            cmd_generate "$@"
            ;;
        batch)
            pull_image
            cmd_batch "$@"
            ;;
        shell)
            pull_image
            cmd_shell
            ;;
        logs)
            cmd_logs
            ;;
        cleanup)
            cmd_cleanup
            ;;
        status)
            cmd_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
