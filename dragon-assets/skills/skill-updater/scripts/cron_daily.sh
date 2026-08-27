#!/usr/bin/env bash
# cron_daily.sh · skill-updater V1.1 增量 · 本地每日 09:00 apply
# 部署方式（任选其一）：
#   1. Linux/Mac: crontab -e → 加 `0 9 * * * /path/to/cron_daily.sh >> /var/log/skill-updater.log 2>&1`
#   2. Windows Git Bash: 用 deploy_daily.ps1（Task Scheduler 友好）
#   3. 手动跑：bash scripts/cron_daily.sh
#
# 行为：
#   1. 先跑 scan.sh 出最新 reports/scan-*.tsv
#   2. 跑 apply.py（默认 REAL-APPLY 模式）
#   3. 失败时调 notify_email.py
#   4. 全部结果写 logs/cron-daily-YYYYMMDD.log
#
# 退出码：0=全 PASS / 1=有 FAILED / 2=配置错

set -uo pipefail

# 路径常量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DRAGON_ROOT="${DRAGON_ROOT:-C:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine}"
DRAGON_ROOT_UNIX="$(cygpath -u "${DRAGON_ROOT}" 2>/dev/null || echo "${DRAGON_ROOT}")"
LOGS_DIR="${SKILL_DIR}/logs"
DATE_STAMP="$(date -u +%Y%m%d-%H%M%S)"
DATE_DAY="$(date -u +%Y%m%d)"
LOG_FILE="${LOGS_DIR}/cron-daily-${DATE_DAY}.log"
SCAN_LOG="${LOGS_DIR}/cron-scan-${DATE_DAY}.log"

# 全局 UTF-8
export PYTHONIOENCODING=utf-8
export LC_ALL=C.UTF-8

mkdir -p "${LOGS_DIR}"

log() {
    local ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "[${ts}] $*" | tee -a "${LOG_FILE}"
}

log "═══ skill-updater · cron_daily · ${DATE_STAMP} ═══"
log "天龙根: ${DRAGON_ROOT_UNIX}"
log "scan 日志: ${SCAN_LOG}"
log "apply 日志: ${LOG_FILE}"

# Python 探测
if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    log "❌ 未找到 python，退出"
    exit 3
fi
log "Python: $(${PYTHON_BIN} --version 2>&1)"

# ────────────────────────────────────────
# Step 1 · 跑 scan.sh 出最新报告
# ────────────────────────────────────────
log ""
log "── Step 1 · scan.sh 扫全盘 ──"
if ! bash "${SCRIPT_DIR}/scan.sh" \
        --root "${DRAGON_ROOT}" \
        --no-readme \
        --format tsv \
        >> "${SCAN_LOG}" 2>&1; then
    log "❌ scan.sh 失败，详情见 ${SCAN_LOG}"
    # 失败也继续（可能老报告可用）
fi

# ────────────────────────────────────────
# Step 2 · 跑 apply.py
# ────────────────────────────────────────
log ""
log "── Step 2 · apply.py REAL-APPLY 模式 ──"
APPLY_RC=0
if ! ${PYTHON_BIN} "${SCRIPT_DIR}/apply.py" \
        --root "${DRAGON_ROOT_UNIX}" \
        >> "${LOG_FILE}" 2>&1; then
    APPLY_RC=$?
    log "❌ apply.py exit=${APPLY_RC}"
fi

# ────────────────────────────────────────
# Step 3 · 失败时调 notify_email.py
# ────────────────────────────────────────
if [[ ${APPLY_RC} -ne 0 ]]; then
    log ""
    log "── Step 3 · 发邮件通知 ──"
    if [[ -n "${NOTIFY_TO:-}" ]]; then
        SUBJECT="⚠️ skill-updater apply 失败 [$(hostname)]"
        BODY="apply 模式失败，exit=${APPLY_RC}\n\n日志: ${LOG_FILE}\n扫描日志: ${SCAN_LOG}\n\n请登录后人工 review。"
        ${PYTHON_BIN} "${SCRIPT_DIR}/notify_email.py" \
            --subject "${SUBJECT}" \
            --body "${BODY}" \
            >> "${LOG_FILE}" 2>&1 || log "❌ 邮件通知也失败"
    else
        log "⚠️  NOTIFY_TO 未配置，跳过邮件通知"
    fi
    exit 1
fi

log ""
log "✅ cron_daily 完成，全部 PASS"
exit 0
