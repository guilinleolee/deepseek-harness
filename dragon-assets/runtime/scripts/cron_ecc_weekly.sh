#!/usr/bin/env bash
# cron_ecc_weekly.sh - Stage 47.2 ECC 7 天观察期 Linux/macOS cron 脚本
#
# 用法:
#   ./cron_ecc_weekly.sh                 # 默认 register到用户 crontab
#   ./cron_ecc_weekly.sh --uninstall     # 从 crontab 删除

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ECC_7DAY_PY="${SCRIPT_DIR}/ecc_7day.py"
CRON_LINE="0 0 * * * cd '${SCRIPT_DIR}/..' && PYTHONIOENCODING=utf-8 python '${ECC_7DAY_PY}' single >> reports/stage-472-ecc/cron.log 2>&1"

if [[ "${1:-}" == "--uninstall" ]]; then
    crontab -l 2>/dev/null | grep -v "ecc_7day.py single" | crontab -
    echo "[OK] cron_ecc_weekly 已卸载"
    exit 0
fi

# install
( crontab -l 2>/dev/null || true; echo "$CRON_LINE" ) | grep -v "^$" | sort -u | crontab -
echo "[OK] 已注册 cron job (每日 00:00 UTC 跑):"
echo "    $CRON_LINE"
echo ""
echo "立即测试: cd '${SCRIPT_DIR}/..' && PYTHONIOENCODING=utf-8 python '${ECC_7DAY_PY}' single"
exit 0
