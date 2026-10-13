
import sqlite3
conn = sqlite3.connect(r"C:\Users\li\.claude\skills\blogger-fingerprint-registry\registry.db")
cur = conn.cursor()

# 加 fingerprints 设计列
try:
    cur.execute("ALTER TABLE fingerprints ADD COLUMN design_style TEXT")
    print("[+] fingerprints: design_style OK")
except sqlite3.OperationalError as e:
    print(f"[!] fingerprints.design_style: {e}")

try:
    cur.execute("ALTER TABLE fingerprints ADD COLUMN design_consent_file TEXT")
    print("[+] fingerprints: design_consent_file OK")
except sqlite3.OperationalError as e:
    print(f"[!] fingerprints.design_consent_file: {e}")

# ip_profiles（如存在）
cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='ip_profiles'")
if cur.fetchone()[0]:
    for col in ["design_style", "design_assets_dir", "design_consent_file"]:
        try:
            cur.execute(f"ALTER TABLE ip_profiles ADD COLUMN {col} TEXT")
            print(f"[+] ip_profiles: {col} OK")
        except sqlite3.OperationalError as e:
            print(f"[!] ip_profiles.{col}: {e}")
else:
    print("[i] ip_profiles 不存在，跳过")

# 索引
cur.execute("CREATE INDEX IF NOT EXISTS idx_design_style ON fingerprints(design_style)")
print("[+] idx_design_style OK")

conn.commit()
conn.close()
print("V3 升级完成")
