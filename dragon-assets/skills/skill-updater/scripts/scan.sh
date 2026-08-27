#!/usr/bin/env bash
# scan.sh — skill-updater V1.0 主入口
# 报告模式（默认）：扫 → 解析 → GitHub 上游比对 → 渲染报告 + 写 TSV/JSON 到 reports/
# 强约束：除 reports/ 子目录外，绝不动任何文件
#
# Usage:
#   bash scripts/scan.sh
#   bash scripts/scan.sh --root "c:/Users/li/.claude"
#   bash scripts/scan.sh --root X --only nano-banana --no-readme
#   bash scripts/scan.sh --no-network

set -uo pipefail

# 严格模式下的 trap：捕到 ERR 时打印，**不退出**（只有无法恢复的错才退）
trap 'echo "[scan.sh] line $LINENO 非致命错误（exit=$?），继续..." >&2' ERR

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPORTS_DIR="${SKILL_DIR}/reports"

# Python 探测：Windows Git Bash 上 ${PYTHON_BIN} 可能指向 Microsoft Store stub，
# 优先用 "python"（通常在 Python311/ 下），其次 ${PYTHON_BIN}
if command -v python >/dev/null 2>&1 && python --version >/dev/null 2>&1; then
    PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1 && python3 --version >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    echo "ERROR: 未找到可用的 python 解释器" >&2
    exit 3
fi
echo "[scan.sh] Python: $($PYTHON_BIN --version 2>&1)" >&2
# Windows Git Bash 子进程默认 GBK，全局设 UTF-8（防 ⭐ / 中文字符爆掉）
export PYTHONIOENCODING=utf-8
export LC_ALL=C.UTF-8
echo "[scan.sh] PYTHONIOENCODING=${PYTHONIOENCODING}" >&2

# 默认参数
ROOTS=()
ONLY_PATTERN=""
NO_NETWORK=0
# 默认跳过 README 抓取:GitHub API 上 README 是 base64 解码,跨 ~150 skill 时易超时
# 如需 README 内容(人读提示词/风格选型),显式加 --with-readme
NO_README=1
NO_AGENTS=0
NO_MARKETPLACES=0
AUTOFILL_SOURCE=0
APPLY=0
FORMAT="all"
MAX_AGE=180

# 帮助
usage() {
    cat <<EOF
skill-updater · V1.0 · 全天龙引擎 skill 上游检查器（report-only）

Usage:
    bash scripts/scan.sh [OPTIONS]

Options:
    -r, --root PATH      扫描根目录（可多次指定，默认 \${SKILL_UPDATER_ROOT:-\$HOME/.claude}）
    --only PATTERN       只扫描名字包含 PATTERN 的 skill（可多次）
    --no-network         跳过所有网络请求（只看本地 frontmatter）
    --no-readme          （默认）跳过 README 抓取,最稳,适合 cron/全量扫
    --with-readme        抓 README 摘要（每个 skill 多 1 次 GitHub API,易超时）
    --format FMT         输出格式：table | tsv | json | all（默认 all）
    --max-age DAYS       本地 last_updated 超过 N 天标红（默认 180）
    -v, --verbose        详细日志
    -h, --help           显示本帮助

Environment:
    GITHUB_TOKEN         提高 GitHub API rate limit（5000/h vs 60/h）
    SKILL_UPDATER_ROOT   默认 --root

Examples:
    # 默认扫描全 ~/.claude
    bash scripts/scan.sh

    # 限制到天龙活跃路径
    bash scripts/scan.sh --root "c:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine"

    # 多根
    bash scripts/scan.sh \\
        --root "c:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine" \\
        --root "c:/Users/li/.claude/projects/dragon-engine"

    # 仅检查某个 skill
    bash scripts/scan.sh --only guizang

    # 不联网
    bash scripts/scan.sh --no-network
EOF
}

# 参数解析
while [[ $# -gt 0 ]]; do
    case "$1" in
        -r|--root) ROOTS+=("$2"); shift 2 ;;
        --only) ONLY_PATTERN="$2"; shift 2 ;;
        --no-network) NO_NETWORK=1; shift ;;
        --no-readme) NO_README=1; shift ;;
        --with-readme) NO_README=0; shift ;;
        --no-agents) NO_AGENTS=1; shift ;;
        --no-marketplaces) NO_MARKETPLACES=1; shift ;;
        --autofill-source) AUTOFILL_SOURCE=1; shift ;;
        --apply) APPLY=1; shift ;;
        --format) FORMAT="$2"; shift 2 ;;
        --max-age) MAX_AGE="$2"; shift 2 ;;
        -v|--verbose) VERBOSE=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "ERROR: 未知参数 $1" >&2; usage; exit 2 ;;
    esac
done

# 默认根目录
if [[ ${#ROOTS[@]} -eq 0 ]]; then
    if [[ -n "${SKILL_UPDATER_ROOT:-}" ]]; then
        ROOTS=("${SKILL_UPDATER_ROOT}")
    else
        # Git Bash on Windows: $HOME 通常是 c:/Users/li
        ROOTS=("${HOME:-.}/.claude")
    fi
fi

# 准备临时目录
TMP_DIR="$(mktemp -d -t skill-updater-XXXXXX)"
trap 'rm -rf "${TMP_DIR}"' EXIT

log() {
    if [[ "${VERBOSE:-0}" == "1" ]]; then
        echo "[scan.sh] $*" >&2
    fi
}

echo "=== skill-updater · V1.0 ===" >&2
echo "扫描根: ${ROOTS[*]}" >&2
echo "格式: ${FORMAT}" >&2
echo "网络: $([ "${NO_NETWORK}" == "1" ] && echo "关闭" || echo "开启")" >&2
echo "README: $([ "${NO_README}" == "1" ] && echo "跳过" || echo "抓取")" >&2

# 准备 reports 目录
mkdir -p "${REPORTS_DIR}"

# 合并多根的扫描结果
MERGED_PARSE="${TMP_DIR}/parse_merged.json"
echo "{" > "${MERGED_PARSE}"
echo "  \"scan_roots\": [" >> "${MERGED_PARSE}"
FIRST=1
for root in "${ROOTS[@]}"; do
    # 路径标准化（Windows → Git Bash 路径）
    root_norm="$(cygpath -u "${root}" 2>/dev/null || echo "${root}")"
    if [[ ! -d "${root_norm}" ]]; then
        echo "WARN: root 不存在，跳过: ${root_norm}" >&2
        continue
    fi
    log "扫描 ${root_norm}"
    ONLY_ARG=""
    [[ -n "${ONLY_PATTERN}" ]] && ONLY_ARG="--only ${ONLY_PATTERN}"

    PARSE_OUT="${TMP_DIR}/parse_$(echo "${root_norm}" | tr '/ ' '__').json"
    # Git Bash /tmp/... 是 MSYS 虚拟路径,Python 看不到,转 Windows 路径
    PARSE_OUT_WIN="$(cygpath -w "${PARSE_OUT}" 2>/dev/null || echo "${PARSE_OUT}")"
    log "parse_skill.py 输出到 ${PARSE_OUT} (Win: ${PARSE_OUT_WIN})"
    if ! ${PYTHON_BIN} "${SCRIPT_DIR}/parse_skill.py" "${root_norm}" ${ONLY_ARG} > "${PARSE_OUT}" 2>"${PARSE_OUT}.err"; then
        echo "ERROR: parse_skill.py 失败 (exit=$?)，错误信息:" >&2
        [[ -f "${PARSE_OUT}.err" ]] && cat "${PARSE_OUT}.err" >&2
        continue
    fi
    if [[ ! -s "${PARSE_OUT}" ]]; then
        echo "ERROR: parse_skill.py 输出为空: ${PARSE_OUT}" >&2
        [[ -f "${PARSE_OUT}.err" ]] && cat "${PARSE_OUT}.err" >&2
        continue
    fi
    COUNT=$(${PYTHON_BIN} -c "import json; print(json.load(open(r'${PARSE_OUT_WIN}', encoding='utf-8'))['total_skill_md_found'])")
    log "根 ${root_norm} 发现 ${COUNT} 个 skill"

    if [[ ${FIRST} == 0 ]]; then
        echo "," >> "${MERGED_PARSE}"
    fi
    FIRST=0
    echo -n "    {\"root\": \"${root_norm}\", \"count\": ${COUNT}}" >> "${MERGED_PARSE}"
    log "根 ${root_norm} 发现 ${COUNT} 个 skill"

    if [[ ${FIRST} == 0 ]]; then
        echo "," >> "${MERGED_PARSE}"
    fi
    FIRST=0
    echo -n "    {\"root\": \"${root_norm}\", \"count\": ${COUNT}}" >> "${MERGED_PARSE}"
done
echo "" >> "${MERGED_PARSE}"
echo "  ]," >> "${MERGED_PARSE}"

# 合并所有 skill 到一个数组
SKILLS_FILE="${TMP_DIR}/all_skills.jsonl"
SKILLS_FILE_WIN="$(cygpath -w "${SKILLS_FILE}" 2>/dev/null || echo "${SKILLS_FILE}")"
ALL_JSON="${TMP_DIR}/all_skills.json"
ALL_JSON_WIN="$(cygpath -w "${ALL_JSON}" 2>/dev/null || echo "${ALL_JSON}")"
MERGED_PARSE_WIN="$(cygpath -w "${MERGED_PARSE}" 2>/dev/null || echo "${MERGED_PARSE}")"
FETCH_OUT="${TMP_DIR}/fetch.json"
FETCH_OUT_WIN="$(cygpath -w "${FETCH_OUT}" 2>/dev/null || echo "${FETCH_OUT}")"

> "${SKILLS_FILE}"
for root in "${ROOTS[@]}"; do
    root_norm="$(cygpath -u "${root}" 2>/dev/null || echo "${root}")"
    PARSE_OUT="${TMP_DIR}/parse_$(echo "${root_norm}" | tr '/ ' '__').json"
    PARSE_OUT_WIN="$(cygpath -w "${PARSE_OUT}" 2>/dev/null || echo "${PARSE_OUT}")"
    [[ -f "${PARSE_OUT}" ]] || continue

    ${PYTHON_BIN} -c "
import json
with open(r'${PARSE_OUT_WIN}', encoding='utf-8') as f:
    d = json.load(f)
for s in d['skills']:
    print(json.dumps(s, ensure_ascii=False))
" >> "${SKILLS_FILE}"
done

# 把 jsonl 转成 JSON 数组
${PYTHON_BIN} -c "
import json
with open(r'${SKILLS_FILE_WIN}', encoding='utf-8') as f:
    items = [json.loads(line) for line in f if line.strip()]
with open(r'${ALL_JSON_WIN}', 'w', encoding='utf-8') as f:
    json.dump({'scanned_at': 'merged', 'skills': items}, f, ensure_ascii=False, indent=2)
"

# 把合并结果写回 MERGED_PARSE
${PYTHON_BIN} -c "
import json
with open(r'${ALL_JSON_WIN}', encoding='utf-8') as f:
    d = json.load(f)
print(json.dumps(d, ensure_ascii=False, indent=2))
" > "${MERGED_PARSE}"

FETCH_ARGS=("--input" "${MERGED_PARSE_WIN}")
[[ "${NO_NETWORK}" == "1" ]] && FETCH_ARGS+=("--no-network")
[[ "${NO_README}" == "1" ]] && FETCH_ARGS+=("--no-readme")

log "gh_fetch.py 跑..."
${PYTHON_BIN} "${SCRIPT_DIR}/gh_fetch.py" "${FETCH_ARGS[@]}" > "${FETCH_OUT}" 2>"${FETCH_OUT}.err" || {
    echo "ERROR: gh_fetch.py 失败,错误信息:" >&2
    cat "${FETCH_OUT}.err" >&2
}

# V1.1: 扫 agents + marketplaces (可选,用 --no-agents / --no-marketplaces 跳过)
AGENTS_OUT="${TMP_DIR}/agents.json"
AGENTS_OUT_WIN="$(cygpath -w "${AGENTS_OUT}" 2>/dev/null || echo "${AGENTS_OUT}")"
MARKETPLACES_OUT="${TMP_DIR}/marketplaces.json"
MARKETPLACES_OUT_WIN="$(cygpath -w "${MARKETPLACES_OUT}" 2>/dev/null || echo "${MARKETPLACES_OUT}")"

if [[ "${NO_AGENTS:-0}" != "1" ]]; then
    log "agents_scan.py 跑..."
    ${PYTHON_BIN} "${SCRIPT_DIR}/agents_scan.py" "${HOME:-.}/.claude" > "${AGENTS_OUT}" 2>"${AGENTS_OUT}.err" || {
        echo "WARN: agents_scan.py 失败,跳过 agents 段" >&2
    }
fi
if [[ "${NO_MARKETPLACES:-0}" != "1" ]]; then
    log "plugins_scan.py 跑..."
    ${PYTHON_BIN} "${SCRIPT_DIR}/plugins_scan.py" "${HOME:-.}/.claude" > "${MARKETPLACES_OUT}" 2>"${MARKETPLACES_OUT}.err" || {
        echo "WARN: plugins_scan.py 失败,跳过 marketplaces 段" >&2
    }
fi

# V1.1.2: autofill-source (git remote + AUTO_HINTS 混合模式,默认 dry-run)
if [[ "${AUTOFILL_SOURCE:-0}" == "1" ]]; then
    log "autofill_source.py 跑..."
    if [[ "${APPLY:-0}" == "1" ]]; then
        ${PYTHON_BIN} "${SCRIPT_DIR}/autofill_source.py" --root "${HOME:-.}/.claude" --apply
    else
        ${PYTHON_BIN} "${SCRIPT_DIR}/autofill_source.py" --root "${HOME:-.}/.claude"
    fi
fi

# 渲染报告
REPORT_ARGS=("--parse" "${MERGED_PARSE_WIN}" "--fetch" "${FETCH_OUT_WIN}" "--out-dir" "${REPORTS_DIR}" "--format" "${FORMAT}" "--max-age" "${MAX_AGE}")
[[ "${NO_AGENTS:-0}" != "1" && -s "${AGENTS_OUT}" ]] && REPORT_ARGS+=("--agents" "${AGENTS_OUT_WIN}")
[[ "${NO_MARKETPLACES:-0}" != "1" && -s "${MARKETPLACES_OUT}" ]] && REPORT_ARGS+=("--marketplaces" "${MARKETPLACES_OUT_WIN}")
${PYTHON_BIN} "${SCRIPT_DIR}/report.py" "${REPORT_ARGS[@]}" 2>&1 | tee "${TMP_DIR}/report_stdout.txt" || true

echo "" >&2
echo "[scan.sh] 完成。报告目录: ${REPORTS_DIR}" >&2