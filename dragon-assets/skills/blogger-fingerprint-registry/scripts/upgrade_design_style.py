"""
upgrade_design_style.py · V1.0
补全 laoli_bro_2026 的第 9 维 design_style(huashu-design 40 风格库 → guizang 主题映射)
"""
import sqlite3
import datetime as dt
import sys

DB_PATH = r"C:\Users\li\.claude\skills\blogger-fingerprint-registry\registry.db"

def main(blogger_id: str = "laoli_bro_2026", design_style: str = "kraft-paper"):
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()

    cur.execute(
        "SELECT blogger_id, design_style, design_consent_file, writing_style FROM fingerprints WHERE blogger_id=?",
        (blogger_id,),
    )
    before = cur.fetchone()
    print(f"BEFORE: {before}")

    cur.execute(
        """
        UPDATE fingerprints
        SET design_style = ?,
            design_consent_file = COALESCE(design_consent_file, 'ip_consent.txt'),
            updated_at = ?
        WHERE blogger_id = ?
        """,
        (design_style, dt.datetime.now().isoformat(timespec="seconds"), blogger_id),
    )
    db.commit()

    cur.execute(
        "SELECT blogger_id, design_style, design_consent_file, writing_style FROM fingerprints WHERE blogger_id=?",
        (blogger_id,),
    )
    after = cur.fetchone()
    print(f"AFTER:  {after}")
    print(f"delta:  design_style '{before[1]}' → '{after[1]}'")
    return after

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "laoli_bro_2026",
         sys.argv[2] if len(sys.argv) > 2 else "kraft-paper")