#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""batch-mirror.py · 批量下载剩余 SKILL.md（绕过 curl timeout）"""
import json, sys, os, io
# 强制 stdout UTF-8（避开 Windows GBK 编码错误）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import urllib.request, urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
CACHE = SCRIPT_DIR / ".cache"
LIBRARY = SKILL_DIR / "library"
RAW_BASE = "https://raw.githubusercontent.com/SamurAIGPT/Generative-Media-Skills/main"

tree = json.load((CACHE / "tree.json").open(encoding="utf-8"))
all_paths = [x["path"] for x in tree["tree"]
             if x["type"] == "blob" and x["path"].endswith("SKILL.md")]

# 路径映射
def map_local(p):
    if p.startswith("library/"):
        return LIBRARY / p[len("library/"):]
    if p.startswith("core/"):
        return LIBRARY / "_core" / p[len("core/"):]
    if p.startswith(".opencode/skills/muapi-"):
        rest = p[len(".opencode/skills/"):]  # muapi-foo/SKILL.md
        name = rest[:-len("/SKILL.md")]
        if any(k in name for k in ("cinema-director","video","ugc","seedance","shorts","thumbnail","social-media-video","product-video","ad-maker")):
            cat = "motion"
        elif any(k in name for k in ("logo","brand","design","ad-creative","ui","color","insta")):
            cat = "visual"
        elif any(k in name for k in ("post","ad","social","campaign")):
            cat = "social"
        elif "clipping" in name:
            cat = "edit"
        else:
            cat = "visual"
        return LIBRARY / cat / name / "SKILL.md"
    if p == "SKILL.md":
        return LIBRARY / "_core" / "ROOT" / "SKILL.md"
    return None

# 列出待下载
todo = []
for up in all_paths:
    local = map_local(up)
    if local is None:
        continue
    if local.exists() and local.stat().st_size > 100:
        continue
    todo.append((up, local))

print(f"待下载: {len(todo)}")
if not todo:
    print("✅ 全部已下载")
    sys.exit(0)

done = 0
fail = 0
def fetch(item):
    up, local = item
    local.parent.mkdir(parents=True, exist_ok=True)
    url = f"{RAW_BASE}/{up}"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "dragon-engine-mirror"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = r.read()
            if b"<html" in data[:200]:
                return ("404", up)
            # Windows 偶尔并发 PermissionError，retry 写文件
            for w in range(3):
                try:
                    local.write_bytes(data)
                    return ("OK", up, len(data))
                except PermissionError:
                    import time; time.sleep(0.5)
            return ("FAIL", up, "permission-denied")
        except (urllib.error.URLError, TimeoutError, ConnectionResetError) as e:
            if attempt < 3:
                import time; time.sleep(1)
                continue
            return ("FAIL", up, str(e)[:50])
    return ("FAIL", up, "unknown")

with ThreadPoolExecutor(max_workers=1) as ex:
    futs = {ex.submit(fetch, it): it for it in todo}
    for f in as_completed(futs):
        result = f.result()
        if result[0] == "OK":
            done += 1
            print(f"✅ {result[1]} ({result[2]} bytes)")
        elif result[0] == "404":
            fail += 1
            print(f"❌ 404 {result[1]}")
        else:
            fail += 1
            print(f"❌ {result[1]}: {result[2]}")

print(f"\nDONE: {done} / FAIL: {fail}")
sys.exit(0 if fail == 0 else 1)