#!/usr/bin/env bash
# cron_weekly.sh · skill-updater 周度自动扫描
# 阶段 34 · Windows Git Bash cron-equivalent 部署
#
# 用法：
#   bash scripts/cron_weekly.sh              # 默认每周日 03:00 报告
#   bash scripts/cron_weekly.sh --force     # 立即跑(测试用)
#
# Windows Task Scheduler 配置：
#   1. 打开"任务计划程序" → "创建任务"
#   2. 常规 → 名称 "skill-updater weekly scan"
#   3. 触发器 → 新建 → 每周 → 星期日 → 03:00:00
#   4. 操作 → 新建 → 启动程序
#      - 程序: bash
#      - 参数: C:\Users\li\.claude\projects\c--Users-li--claude\dragon-engine\skills\skill-updater\scripts\cron_weekly.sh
#      - 起始于: C:\Users\li\.claude\projects\c--Users-li--claude\dragon-engine\skills\skill-updater
#   5. 条件 → 取消勾选"只有在使用交流电源时才启动"
#   6. 设置 → 允许按需运行任务 + 如果任务失败则每隔 1 分钟重启
#
# Git Bash cron（Linux/Mac）配置：
#   0 3 * * 0 cd /path/to/skill-updater && bash scripts/cron_weekly.sh >> logs/cron.log 2>&1

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPORTS_DIR="${SKILL_DIR}/reports"
LOGS_DIR="${SKILL_DIR}/logs"

mkdir -p "${REPORTS_DIR}" "${LOGS_DIR}"

# Python 探测
if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    echo "[$(date +%Y-%m-%dT%H:%M:%S)] ERROR: 无 python" >> "${LOGS_DIR}/cron_weekly.log"
    exit 3
fi

# UTF-8 防乱码
export PYTHONIOENCODING=utf-8
export LC_ALL=C.UTF-8

# 是否强制跑(测试用)
FORCE=0
if [ "${1:-}" = "--force" ]; then
    FORCE=1
fi

# 周日才跑(非强制模式)
if [ $FORCE -eq 0 ]; then
    DOW=$(date +%u)  # 1=Mon ... 7=Sun
    if [ "$DOW" != "7" ]; then
        echo "[$(date +%Y-%m-%dT%H:%M:%S)] skip (今天 DOW=$DOW, 非周日)" >> "${LOGS_DIR}/cron_weekly.log"
        exit 0
    fi
fi

# 触发扫描
LOG_FILE="${LOGS_DIR}/cron_weekly_$(date +%Y%m%d_%H%M%S).log"
echo "[$(date +%Y-%m-%dT%H:%M:%S)] scan started" >> "${LOG_FILE}"
bash "${SCRIPT_DIR}/scan.sh" --no-network >> "${LOG_FILE}" 2>&1
EXIT_CODE=$?

echo "[$(date +%Y-%m-%dT%H:%M:%S)] scan done, exit=${EXIT_CODE}" >> "${LOG_FILE}"

# 退出码契约
if [ $EXIT_CODE -ne 0 ]; then
    echo "[$(date +%Y-%m-%dT%H:%M:%S)] scan FAILED, exit=${EXIT_CODE}" >> "${LOGS_DIR}/cron_weekly.log"
    exit $EXIT_CODE
fi

# 列出本次新报告
NEW_REPORTS=$(ls -t "${REPORTS_DIR}"/report-*.{tsv,json} 2>/dev/null | head -2 | tr '\n' ' ')
echo "[$(date +%Y-%m-%dT%H:%M:%S)] scan OK, new reports: ${NEW_REPORTS}" >> "${LOGS_DIR}/cron_weekly.log"

exit 0