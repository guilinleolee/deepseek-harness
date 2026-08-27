#!/usr/bin/env bash
#==============================================================================
# Credential Manager - API Key 安全存储与轮换
# 借鉴 Huginn Credentials Store 设计
#==============================================================================

set -euo pipefail

# 配置
CRED_DIR="${CRED_DIR:-$HOME/.claude/credentials}"
CRED_DB="$CRED_DIR/credentials.db"
CRED_AUDIT="$CRED_DIR/audit.log"
VAULT_FILE="$CRED_DIR/vault.enc"
MASTER_KEY_FILE="$CRED_DIR/.master.key"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 初始化
init() {
    mkdir -p "$CRED_DIR"
    chmod 700 "$CRED_DIR"

    if [[ ! -f "$CRED_DB" ]]; then
        sqlite3 "$CRED_DB" "CREATE TABLE credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            value_encrypted TEXT NOT NULL,
            iv TEXT NOT NULL,
            tag TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            version INTEGER DEFAULT 1
        );"
        log_success "数据库初始化完成: $CRED_DB"
    fi

    # 审计日志
    touch "$CRED_AUDIT"
}

# 获取主密钥
get_master_key() {
    if [[ -f "$MASTER_KEY_FILE" ]]; then
        openssl rand -hex 32 > "$MASTER_KEY_FILE" 2>/dev/null || \
            python3 -c "import secrets; print(secrets.token_hex(32))" > "$MASTER_KEY_FILE"
        chmod 600 "$MASTER_KEY_FILE"
    fi
    cat "$MASTER_KEY_FILE"
}

# 加密凭证
encrypt_credential() {
    local value="$1"
    local master_key
    master_key=$(get_master_key)

    openssl enc -aes-256-gcm -K "$master_key" -iv "$(openssl rand -hex 16)" -S "$(openssl rand -hex 16)" -A <<< "$value" 2>/dev/null || \
    python3 << EOF
import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = bytes.fromhex("$master_key")
iv = os.urandom(12)
aesgcm = AESGCM(key)
ct = aesgcm.encrypt(iv, b"$value", None)
print(base64.b64encode(iv + ct).decode())
EOF
}

# 解密凭证
decrypt_credential() {
    local encrypted="$1"
    local master_key
    master_key=$(get_master_key)

    openssl enc -aes-256-gcm -d -K "$master_key" -A <<< "$encrypted" 2>/dev/null || \
    python3 << EOF
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = bytes.fromhex("$master_key")
data = base64.b64decode("$encrypted")
iv, ct = data[:12], data[12:]
aesgcm = AESGCM(key)
print(aesgcm.decrypt(iv, ct, None).decode())
EOF
}

# 添加凭证
add_credential() {
    local name="$1"
    local value="$2"
    local tag="${3:-}"

    init

    local encrypted iv
    encrypted=$(encrypt_credential "$value")
    iv=$(openssl rand -hex 16)

    if sqlite3 "$CRED_DB" "SELECT 1 FROM credentials WHERE name='$name'" 2>/dev/null | grep -q 1; then
        log_warn "凭证 '$name' 已存在，使用 update 命令更新"
        return 1
    fi

    sqlite3 "$CRED_DB" "INSERT INTO credentials (name, value_encrypted, iv, tag) VALUES ('$name', '$encrypted', '$iv', '$tag')"
    audit_log "ADD" "$name"
    log_success "凭证 '$name' 已存储"
}

# 获取凭证
get_credential() {
    local name="$1"
    local export="${2:-false}"

    init

    local encrypted
    encrypted=$(sqlite3 "$CRED_DB" "SELECT value_encrypted FROM credentials WHERE name='$name'" 2>/dev/null)

    if [[ -z "$encrypted" ]]; then
        log_error "凭证 '$name' 不存在"
        return 1
    fi

    local value
    value=$(decrypt_credential "$encrypted")
    audit_log "GET" "$name"

    if [[ "$export" == "true" ]]; then
        echo "export ${name}=${value}"
    else
        echo "$value"
    fi
}

# 列出凭证
list_credentials() {
    local tag="${1:-}"
    init

    if [[ -n "$tag" ]]; then
        sqlite3 -header -column "$CRED_DB" \
            "SELECT name, tag, created_at, expires_at FROM credentials WHERE tag='$tag'" 2>/dev/null
    else
        sqlite3 -header -column "$CRED_DB" \
            "SELECT name, tag, created_at, expires_at FROM credentials" 2>/dev/null
    fi
}

# 删除凭证
delete_credential() {
    local name="$1"
    local force="${2:-false}"

    init

    if [[ "$force" != "true" ]]; then
        read -p "确认删除凭证 '$name'? (y/N): " confirm
        [[ "$confirm" != "y" && "$confirm" != "Y" ]] && return 0
    fi

    sqlite3 "$CRED_DB" "DELETE FROM credentials WHERE name='$name'" 2>/dev/null
    audit_log "DELETE" "$name"
    log_success "凭证 '$name' 已删除"
}

# 轮换凭证
rotate_credential() {
    local name="$1"
    local new_value="$2"

    init

    # 备份旧版本
    sqlite3 "$CRED_DB" "UPDATE credentials SET version=version+1 WHERE name='$name'" 2>/dev/null

    # 加密新值
    local encrypted
    encrypted=$(encrypt_credential "$new_value")

    sqlite3 "$CRED_DB" "UPDATE credentials SET value_encrypted='$encrypted', updated_at=CURRENT_TIMESTAMP WHERE name='$name'" 2>/dev/null
    audit_log "ROTATE" "$name"
    log_success "凭证 '$name' 已轮换"
}

# 审计日志
audit_log() {
    local action="$1"
    local name="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$action] $name" >> "$CRED_AUDIT"
}

# 审计查询
audit_query() {
    local days="${1:-7}"
    init

    tail -n 100 "$CRED_AUDIT" 2>/dev/null | \
        awk -v days="$days" -v now="$(date +%s)" '
        BEGIN { cutoff = now - days * 86400 }
        /^\[/ {
            gsub(/[\[\]]/, "", $0)
            split($0, t, " ")
            gsub(/-/, " ", t[1])
            gsub(/:/, " ", t[2])
            cmd = "date -d \"" t[1] " " t[2] "\" +%s"
            cmd | getline ts
            if (ts >= cutoff) print $0
        }' || tail -n 100 "$CRED_AUDIT"
}

# 生成 ENV 注入脚本
gen_env_inject() {
    local names=("$@")
    init

    echo "#!/usr/bin/env bash"
    echo "# Auto-generated by credential-manager"
    echo

    for name in "${names[@]}"; do
        local value
        value=$(get_credential "$name" 2>/dev/null) || continue
        echo "export ${name}=${value}"
    done
}

# 诊断
doctor() {
    echo "=== Credential Manager 诊断 ==="
    echo

    echo "[1] 目录检查"
    if [[ -d "$CRED_DIR" ]]; then
        perms=$(stat -c "%a" "$CRED_DIR" 2>/dev/null || stat -f "%OLp" "$CRED_DIR" 2>/dev/null)
        echo "  目录: $CRED_DIR (权限: $perms)"
        [[ "$perms" == "700" ]] && echo "  ✓ 权限正确" || echo "  ⚠ 权限应设为 700"
    else
        echo "  ✗ 目录不存在"
    fi

    echo
    echo "[2] 数据库检查"
    if [[ -f "$CRED_DB" ]]; then
        count=$(sqlite3 "$CRED_DB" "SELECT COUNT(*) FROM credentials" 2>/dev/null)
        echo "  数据库: $CRED_DB"
        echo "  凭证数量: $count"
        echo "  ✓ 数据库正常"
    else
        echo "  ✗ 数据库不存在"
    fi

    echo
    echo "[3] 审计日志"
    if [[ -f "$CRED_AUDIT" ]]; then
        lines=$(wc -l < "$CRED_AUDIT")
        echo "  审计日志: $CRED_AUDIT"
        echo "  记录数: $lines"
        echo "  ✓ 审计日志正常"
    else
        echo "  ⚠ 审计日志不存在"
    fi

    echo
    echo "[4] OpenSSL 检查"
    if command -v openssl &>/dev/null; then
        version=$(openssl version)
        echo "  ✓ OpenSSL: $version"
    else
        echo "  ✗ OpenSSL 未安装"
    fi

    echo
    echo "[5] Python3 检查"
    if command -v python3 &>/dev/null; then
        version=$(python3 --version)
        echo "  ✓ Python3: $version"
        python3 -c "from cryptography.hazmat.primitives.ciphers.aead import AESGCM" 2>/dev/null && \
            echo "  ✓ cryptography 库已安装" || \
            echo "  ⚠ 请安装: pip install cryptography"
    else
        echo "  ✗ Python3 未安装"
    fi
}

# 帮助
usage() {
    cat << EOF
Credential Manager - API Key 安全存储与轮换

用法: cred-store <命令> [参数]

命令:
  add <name> <value> [--tag]      添加凭证
  get <name> [--export]           获取凭证
  list [--tag]                    列出凭证
  delete <name> [--force]         删除凭证
  rotate <name> <new_value>       轮换凭证
  audit [--days N]                查询审计日志
  inject <name>...                生成 ENV 注入脚本
  doctor                           诊断检查
  init                            初始化

示例:
  cred-store add openai "sk-xxx" --tag production
  cred-store get openai
  cred-store list --tag production
  cred-store rotate openai "sk-yyy"
  source <(cred-store inject openai github)
  cred-store audit --days 30

EOF
}

# 主入口
main() {
    local cmd="${1:-}"
    shift || true

    case "$cmd" in
        add)
            add_credential "$@"
            ;;
        get)
            get_credential "$@"
            ;;
        list)
            list_credentials "$@"
            ;;
        delete)
            delete_credential "$@"
            ;;
        rotate)
            rotate_credential "$@"
            ;;
        audit)
            audit_query "$@"
            ;;
        inject)
            gen_env_inject "$@"
            ;;
        doctor)
            doctor
            ;;
        init)
            init
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            usage
            ;;
    esac
}

main "$@"
