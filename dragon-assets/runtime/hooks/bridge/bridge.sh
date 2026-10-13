---
license: UNKNOWN
---

#!/bin/bash
# =============================================================
# Bridge.sh - 门卫
# 天龙引擎Bridge系统 V1.0
#
# 职责：
# 1. EXIT trap自动善后（三层保险第一层）
# 2. 参数验证（门卫检查）
# 3. 环境准备（工作空间）
# 4. 信号处理（SIGINT/SIGTERM/SIGHUP）
#
# 三层保险：
# - Layer 1 (Shell): EXIT trap - 无论脚本如何退出都会触发清理
# - Layer 2 (Python): BaseException - 捕获所有Python异常
# - Layer 3 (Watchdog): 超时检测 - 检测死锁/僵死状态
# =============================================================

set -o errexit
set -o nounset
set -o pipefail

# 配置
BRIDGE_STATE_PATH="${BRIDGE_STATE_PATH:-$HOME/.claude/state/bridge/state.json}"
BRIDGE_LOG_PATH="${BRIDGE_LOG_PATH:-$HOME/.claude/state/bridge/logs/bridge-$(date +%Y%m%d_%H%M%S).log}"
BRIDGE_TIMEOUT="${BRIDGE_TIMEOUT:-300}"  # 秒

# =============================================================
# 第一层保险：EXIT trap - 自动善后
# 无论脚本如何退出（正常、错误、信号中断），都会触发此函数
# =============================================================
cleanup() {
    local exit_code=$?
    local timestamp=$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')

    echo "[$timestamp] EXIT trap triggered, exit_code=$exit_code" >> "$BRIDGE_LOG_PATH" 2>/dev/null || true

    # 更新状态文件
    if [[ -f "$BRIDGE_STATE_PATH" ]]; then
        # 使用Python进行原子JSON更新（shell处理JSON不可靠）
        python3 -c "
import json
import os
import sys

state_path = '$BRIDGE_STATE_PATH'
log_path = '$BRIDGE_LOG_PATH'
exit_code = $exit_code
timestamp = '$timestamp'

try:
    # 读取当前状态
    with open(state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)

    # 更新状态
    if state.get('status') == 'running':
        if exit_code == 0:
            state['status'] = 'completed'
        else:
            state['status'] = 'failed'

    state['exit_code'] = exit_code
    state['completed_at'] = timestamp
    state['shell_cleanup'] = True

    # 原子写入
    temp_path = state_path + '.tmp.' + str(os.getpid())
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    # Windows兼容：先删除目标文件
    if sys.platform == 'win32':
        try:
            os.remove(state_path)
        except:
            pass

    os.replace(temp_path, state_path)

    # 写入日志
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] State updated via EXIT trap: status={state[\"status\"]}\\n')

except Exception as e:
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] EXIT trap error: {e}\\n')
" 2>/dev/null || echo "[$timestamp] Failed to update state via EXIT trap" >> "$BRIDGE_LOG_PATH" 2>/dev/null || true
    fi

    # 清理临时文件
    rm -f "$BRIDGE_STATE_PATH.tmp.$$" 2>/dev/null || true
    rm -f "$BRIDGE_STATE_PATH.lock" 2>/dev/null || true

    echo "[$timestamp] Cleanup completed" >> "$BRIDGE_LOG_PATH" 2>/dev/null || true
}

# 注册EXIT trap
trap cleanup EXIT

# =============================================================
# 第二层保险：信号处理
# 捕获外部中断信号，确保状态正确记录
# =============================================================
handle_signal() {
    local signal=$1
    local timestamp=$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')

    echo "[$timestamp] Received signal: $signal" >> "$BRIDGE_LOG_PATH" 2>/dev/null || true

    # 更新状态为中断
    python3 -c "
import json
import os
import sys

state_path = '$BRIDGE_STATE_PATH'
log_path = '$BRIDGE_LOG_PATH'
signal = '$signal'
timestamp = '$timestamp'

try:
    with open(state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)

    state['status'] = 'interrupted'
    state['interrupted_at'] = timestamp
    state['interrupt_signal'] = signal

    temp_path = state_path + '.tmp.' + str(os.getpid())
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    if sys.platform == 'win32':
        try:
            os.remove(state_path)
        except:
            pass

    os.replace(temp_path, state_path)

except Exception as e:
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] Signal handler error: {e}\\n')
" 2>/dev/null || true

    # 退出码：128 + 信号编号
    case $signal in
        SIGINT)  exit 130 ;;  # 128 + 2
        SIGTERM) exit 143 ;;  # 128 + 15
        SIGHUP)  exit 129 ;;  # 128 + 1
        *)       exit 1 ;;
    esac
}

# 注册信号处理
trap 'handle_signal SIGINT' INT
trap 'handle_signal SIGTERM' TERM
trap 'handle_signal SIGHUP' HUP

# =============================================================
# 参数验证 - 门卫检查
# 确保所有必要参数都已提供
# =============================================================
validate_params() {
    local errors=0

    if [[ -z "${BRIDGE_TASK_ID:-}" ]]; then
        echo "ERROR: BRIDGE_TASK_ID not set" >&2
        errors=$((errors + 1))
    fi

    if [[ -z "${BRIDGE_TASK_JSON:-}" ]]; then
        echo "ERROR: BRIDGE_TASK_JSON not set" >&2
        errors=$((errors + 1))
    fi

    # 验证JSON格式
    if ! echo "$BRIDGE_TASK_JSON" | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
        echo "ERROR: BRIDGE_TASK_JSON is not valid JSON" >&2
        errors=$((errors + 1))
    fi

    if [[ $errors -gt 0 ]]; then
        echo "[$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')] Parameter validation failed with $errors errors" >> "$BRIDGE_LOG_PATH" 2>/dev/null || true
        exit 1
    fi

    echo "[$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')] Parameters validated" >> "$BRIDGE_LOG_PATH" 2>/dev/null || true
}

# =============================================================
# 环境准备 - 工作空间
# 创建必要的目录和文件
# =============================================================
prepare_environment() {
    # 创建必要目录
    mkdir -p "$(dirname "$BRIDGE_STATE_PATH")" 2>/dev/null || true
    mkdir -p "$(dirname "$BRIDGE_LOG_PATH")" 2>/dev/null || true

    # 检查Python可用性
    if ! command -v python3 &>/dev/null; then
        echo "ERROR: python3 not found" >&2
        exit 1
    fi

    echo "[$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')] Environment prepared" >> "$BRIDGE_LOG_PATH" 2>/dev/null || true
}

# =============================================================
# 主执行逻辑
# =============================================================
main() {
    echo "[$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')] Bridge.sh started" >> "$BRIDGE_LOG_PATH" 2>/dev/null || true
    echo "  TASK_ID: ${BRIDGE_TASK_ID:-unknown}" >> "$BRIDGE_LOG_PATH" 2>/dev/null || true
    echo "  TIMEOUT: ${BRIDGE_TIMEOUT}s" >> "$BRIDGE_LOG_PATH" 2>/dev/null || true

    validate_params
    prepare_environment

    # 更新状态为运行中
    python3 -c "
import json
import os
import sys

state_path = '$BRIDGE_STATE_PATH'
task_json = '''$BRIDGE_TASK_JSON'''
log_path = '$BRIDGE_LOG_PATH'

try:
    task = json.loads(task_json)
except:
    task = {'raw': task_json}

state = {
    'task_id': '$BRIDGE_TASK_ID',
    'status': 'running',
    'started_at': '$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')',
    'pid': $$,
    'ppid': $PPID,
    'task': task,
    'heartbeat': $(date +%s),
    'shell_pid': $$
}

temp_path = state_path + '.tmp.' + str(os.getpid())
with open(temp_path, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

if sys.platform == 'win32':
    try:
        os.remove(state_path)
    except:
        pass

os.replace(temp_path, state_path)
" 2>/dev/null || true

    # 获取脚本所在目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # 执行Python脚本（带超时）
    if command -v timeout &>/dev/null; then
        # Linux/macOS有timeout命令
        timeout "$BRIDGE_TIMEOUT" python3 "$SCRIPT_DIR/bridge.py" \
            --task-id "$BRIDGE_TASK_ID" \
            --task-json "$BRIDGE_TASK_JSON" \
            --state-path "$BRIDGE_STATE_PATH" \
            --log-path "$BRIDGE_LOG_PATH"

        local py_exit_code=$?

        if [[ $py_exit_code -eq 124 ]]; then
            echo "[$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')] Python execution timed out after ${BRIDGE_TIMEOUT}s" >> "$BRIDGE_LOG_PATH" 2>/dev/null || true

            # 更新状态为超时
            python3 -c "
import json
import os
import sys

state_path = '$BRIDGE_STATE_PATH'
try:
    with open(state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)
    state['status'] = 'timeout'
    state['timeout_at'] = '$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')'
    state['timeout_seconds'] = $BRIDGE_TIMEOUT

    temp_path = state_path + '.tmp.' + str(os.getpid())
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    if sys.platform == 'win32':
        try:
            os.remove(state_path)
        except:
            pass
    os.replace(temp_path, state_path)
except: pass
" 2>/dev/null || true

            exit 124
        fi

        echo "[$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')] Python execution completed with code $py_exit_code" >> "$BRIDGE_LOG_PATH" 2>/dev/null || true
        exit $py_exit_code
    else
        # Windows没有timeout命令，直接执行
        python3 "$SCRIPT_DIR/bridge.py" \
            --task-id "$BRIDGE_TASK_ID" \
            --task-json "$BRIDGE_TASK_JSON" \
            --state-path "$BRIDGE_STATE_PATH" \
            --log-path "$BRIDGE_LOG_PATH"

        local py_exit_code=$?
        echo "[$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')] Python execution completed with code $py_exit_code" >> "$BRIDGE_LOG_PATH" 2>/dev/null || true
        exit $py_exit_code
    fi
}

main "$@"