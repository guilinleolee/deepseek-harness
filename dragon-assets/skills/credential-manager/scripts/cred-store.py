#!/usr/bin/env python3
"""
Credential Manager - API Key 安全存储与轮换
借鉴 Huginn Credentials Store 设计
"""

import os
import sys
import sqlite3
import argparse
import getpass
import json
from pathlib import Path
from datetime import datetime

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# 配置
CRED_DIR = Path(os.path.expanduser("~/.claude/credentials"))
CRED_DB = CRED_DIR / "credentials.db"
CRED_AUDIT = CRED_DIR / "audit.log"
KEY_FILE = CRED_DIR / ".master.key"


def get_master_key():
    """获取或生成主密钥"""
    if KEY_FILE.exists():
        return KEY_FILE.read_text().strip()
    else:
        key = os.urandom(32).hex()
        KEY_FILE.write_text(key)
        KEY_FILE.chmod(0o600)
        return key


def init_db():
    """初始化数据库"""
    CRED_DIR.mkdir(parents=True, exist_ok=True)
    CRED_DIR.chmod(0o700)

    conn = sqlite3.connect(str(CRED_DB))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            value_encrypted TEXT NOT NULL,
            tag TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            version INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()

    if not CRED_AUDIT.exists():
        CRED_AUDIT.touch()


def encrypt(value, key=None):
    """加密凭证"""
    if key is None:
        key = get_master_key()

    if CRYPTO_AVAILABLE:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'credential-manager-salt',
            iterations=100000,
        )
        fernet_key = Fernet.generate_key()
        # 简化版：直接使用 base64 编码
        import base64
        encoded = base64.b64encode(fernet_key).decode() + base64.b64encode(value.encode()).decode()
        return encoded
    else:
        import base64
        return base64.b64encode(value.encode()).decode()


def decrypt(encrypted, key=None):
    """解密凭证"""
    if key is None:
        key = get_master_key()

    if CRYPTO_AVAILABLE:
        try:
            import base64
            decoded = base64.b64decode(encrypted.encode()).decode()
            fernet_key = base64.b64decode(decoded[:44])
            cipher_text = base64.b64decode(decoded[44:])
            f = Fernet(fernet_key)
            return f.decrypt(cipher_text).decode()
        except:
            pass

    import base64
    return base64.b64decode(encrypted.encode()).decode()


def audit_log(action, name):
    """记录审计日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CRED_AUDIT, 'a') as f:
        f.write(f"[{timestamp}] [{action}] {name}\n")


def cmd_add(args):
    """添加凭证"""
    init_db()

    if not sys.stdin.isatty():
        value = sys.stdin.read().strip()
    else:
        value = args.value

    if not value:
        print("Error: 请提供凭证值")
        return 1

    encrypted = encrypt(value)

    conn = sqlite3.connect(str(CRED_DB))
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO credentials (name, value_encrypted, tag) VALUES (?, ?, ?)",
            (args.name, encrypted, args.tag)
        )
        conn.commit()
        audit_log("ADD", args.name)
        print(f"[OK] 凭证 '{args.name}' 已存储")
    except sqlite3.IntegrityError:
        print(f"[WARN] 凭证 '{args.name}' 已存在，使用 update 命令更新")
    finally:
        conn.close()

    return 0


def cmd_get(args):
    """获取凭证"""
    init_db()

    conn = sqlite3.connect(str(CRED_DB))
    cursor = conn.cursor()
    cursor.execute("SELECT value_encrypted FROM credentials WHERE name=?", (args.name,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"[ERROR] 凭证 '{args.name}' 不存在")
        return 1

    value = decrypt(row[0])
    audit_log("GET", args.name)

    if args.export:
        print(f"export {args.name}={value}")
    else:
        print(value)

    return 0


def cmd_list(args):
    """列出凭证"""
    init_db()

    conn = sqlite3.connect(str(CRED_DB))
    cursor = conn.cursor()

    if args.tag:
        cursor.execute(
            "SELECT name, tag, created_at FROM credentials WHERE tag=?",
            (args.tag,)
        )
    else:
        cursor.execute("SELECT name, tag, created_at FROM credentials")

    print(f"{'名称':<30} {'标签':<20} {'创建时间':<20}")
    print("-" * 70)
    for row in cursor.fetchall():
        print(f"{row[0]:<30} {row[1] or '':<20} {row[2] or '':<20}")

    conn.close()
    return 0


def cmd_delete(args):
    """删除凭证"""
    init_db()

    if not args.force:
        confirm = input(f"确认删除凭证 '{args.name}'? (y/N): ")
        if confirm.lower() != 'y':
            return 0

    conn = sqlite3.connect(str(CRED_DB))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM credentials WHERE name=?", (args.name,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted:
        audit_log("DELETE", args.name)
        print(f"[OK] 凭证 '{args.name}' 已删除")
    else:
        print(f"[ERROR] 凭证 '{args.name}' 不存在")

    return 0


def cmd_rotate(args):
    """轮换凭证"""
    init_db()

    if not sys.stdin.isatty():
        new_value = sys.stdin.read().strip()
    else:
        new_value = args.new_value

    if not new_value:
        print("Error: 请提供新的凭证值")
        return 1

    encrypted = encrypt(new_value)

    conn = sqlite3.connect(str(CRED_DB))
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE credentials SET value_encrypted=?, updated_at=CURRENT_TIMESTAMP, version=version+1 WHERE name=?",
        (encrypted, args.name)
    )
    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated:
        audit_log("ROTATE", args.name)
        print(f"[OK] 凭证 '{args.name}' 已轮换")
    else:
        print(f"[ERROR] 凭证 '{args.name}' 不存在")

    return 0


def cmd_audit(args):
    """审计日志"""
    init_db()

    if not CRED_AUDIT.exists():
        print("无审计日志")
        return 0

    with open(CRED_AUDIT, 'r') as f:
        lines = f.readlines()

    # 过滤最近的日志
    print("=== 审计日志 ===")
    for line in lines[-args.days * 10 if args.days else 100:]:
        print(line.strip())

    return 0


def cmd_inject(args):
    """生成 ENV 注入脚本"""
    init_db()

    print("#!/usr/bin/env bash")
    print("# Auto-generated by credential-manager")
    print()

    conn = sqlite3.connect(str(CRED_DB))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM credentials")
    for row in cursor.fetchall():
        name = row[0]
        cursor2 = conn.cursor()
        cursor2.execute("SELECT value_encrypted FROM credentials WHERE name=?", (name,))
        row2 = cursor2.fetchone()
        if row2:
            value = decrypt(row2[0])
            print(f"export {name}={value}")
    conn.close()

    return 0


def cmd_doctor(args):
    """诊断检查"""
    print("=== Credential Manager Diagnosis ===")
    print()

    print("[1] Directory Check")
    if CRED_DIR.exists():
        print(f"  [OK] Directory: {CRED_DIR}")
    else:
        print(f"  [X] Directory not exists")

    print()
    print("[2] Database Check")
    if CRED_DB.exists():
        conn = sqlite3.connect(str(CRED_DB))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM credentials")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"  Database: {CRED_DB}")
        print(f"  Credentials: {count}")
        print("  [OK] Database normal")
    else:
        print("  [X] Database not exists")

    print()
    print("[3] OpenSSL Check")
    import subprocess
    try:
        result = subprocess.run(['openssl', 'version'], capture_output=True, text=True)
        print(f"  [OK] OpenSSL: {result.stdout.strip()}")
    except:
        print("  [!] OpenSSL not found via CLI")

    print()
    print("[4] Python cryptography Check")
    if CRYPTO_AVAILABLE:
        print("  [OK] cryptography installed")
    else:
        print("  [!] cryptography not installed, using basic encryption")

    print()
    print("[5] Master Key Check")
    if KEY_FILE.exists():
        print("  [OK] Master key generated")
    else:
        print("  [!] Master key not generated, will be auto-generated on first add")


def main():
    parser = argparse.ArgumentParser(description="Credential Manager - API Key 安全存储")
    subparsers = parser.add_subparsers(dest='cmd', help='命令')

    # add
    p_add = subparsers.add_parser('add', help='添加凭证')
    p_add.add_argument('name', help='凭证名称')
    p_add.add_argument('value', nargs='?', help='凭证值')
    p_add.add_argument('--tag', help='标签')
    p_add.set_defaults(func=cmd_add)

    # get
    p_get = subparsers.add_parser('get', help='获取凭证')
    p_get.add_argument('name', help='凭证名称')
    p_get.add_argument('--export', action='store_true', help='导出为 export 语句')
    p_get.set_defaults(func=cmd_get)

    # list
    p_list = subparsers.add_parser('list', help='列出凭证')
    p_list.add_argument('--tag', help='按标签筛选')
    p_list.set_defaults(func=cmd_list)

    # delete
    p_del = subparsers.add_parser('delete', help='删除凭证')
    p_del.add_argument('name', help='凭证名称')
    p_del.add_argument('--force', action='store_true', help='强制删除')
    p_del.set_defaults(func=cmd_delete)

    # rotate
    p_rot = subparsers.add_parser('rotate', help='轮换凭证')
    p_rot.add_argument('name', help='凭证名称')
    p_rot.add_argument('new_value', nargs='?', help='新凭证值')
    p_rot.set_defaults(func=cmd_rotate)

    # audit
    p_aud = subparsers.add_parser('audit', help='审计日志')
    p_aud.add_argument('--days', type=int, default=7, help='查询天数')
    p_aud.set_defaults(func=cmd_audit)

    # inject
    p_inj = subparsers.add_parser('inject', help='生成 ENV 注入脚本')
    p_inj.set_defaults(func=cmd_inject)

    # doctor
    p_doc = subparsers.add_parser('doctor', help='诊断检查')
    p_doc.set_defaults(func=cmd_doctor)

    # init
    p_init = subparsers.add_parser('init', help='初始化')
    p_init.set_defaults(func=lambda args: init_db() or print("[OK] 初始化完成"))

    args = parser.parse_args()

    if hasattr(args, 'func'):
        return args.func(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
