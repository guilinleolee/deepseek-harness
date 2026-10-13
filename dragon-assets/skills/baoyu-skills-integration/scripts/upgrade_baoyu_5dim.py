#!/usr/bin/env python3
"""
upgrade_baoyu_5dim.py · V1.0
自动给 baoyu 8 个设计类 SKILL.md 灌入 huashu-design 5(+1) 维反 AI slop 自检
退出码:0=PASS / 1=FAIL / 2=NOTHING TO DO
"""
import argparse
import datetime as _dt
import json
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path("C:/Users/li/.claude/projects/dragon-engine/skills")

# 8 个有设计产出的 baoyu skill(其余 13 个是纯文本/发布类,不需要 5 维自检)
DESIGN_SKILLS = [
    "baoyu-cover-image",
    "baoyu-image-gen",
    "baoyu-xhs-images",
    "baoyu-comic",
    "baoyu-infographic",
    "baoyu-article-illustrator",
    "baoyu-diagram",
    "baoyu-slide-deck",
]

CHECK_BLOCK_HEADER = "\n\n## 🚨 反 AI slop 5(+1) 维自检(huashu-design 引入 · 阶段 15)\n"

def check_block() -> str:
    return CHECK_BLOCK_HEADER + """
每次产出前**必须先自评**这 6 个维度,任意维度 ≤5 分则**回炉重做**:

### 0. 概念/立意
- [ ] 这个设计的独有 idea 是什么?(能一句话讲出吗)
- [ ] 盖住 logo/文字还认得出主题吗?
- [ ] 换主题是否还成立?(成立 = 模板套皮,直接 ≤5)

### 1. 哲学一致性
- [ ] 是否选了 1 个明确的设计哲学?(editorial / swiss / brutalist / pentagram / takram ...)
- [ ] 颜色/字体/布局是否与哲学对齐?
- [ ] 有没有自相矛盾的元素?

### 2. 视觉层级
- [ ] 视线是否沿主→次→辅助 自然流动?
- [ ] 中间层级是否清晰?(至少 5 级可区分)

### 3. 细节执行
- [ ] typography 精确(字号都是 8px 倍数)?
- [ ] spacing 一致(8px baseline grid)?
- [ ] 是否避免渐变/shadow 滥用?

### 4. 功能性
- [ ] 主信息 5 秒可读?
- [ ] contrast ≥4.5?(WCAG AA)
- [ ] 响应式考虑(移动端读者 ≥50%)?

### 5. 创新性(反 AI cliché)
- [ ] 是否避免 6 个 AI 视觉套路:渐变/glassmorphism/neon/字号混乱/颜色过多/字体过多?
- [ ] 是否用真实数据?(无 lorem ipsum / 占位 URL)
- [ ] CJK 字体栈优先级?(Noto Sans/Serif SC > Inter)

**一票否决**:概念 ≤5 → 总评封顶 6.0,直接回炉。
"""

def has_check_block(text: str) -> bool:
    return "反 AI slop 5(+1) 维自检" in text

def backup(skill_md: Path) -> Path:
    ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = skill_md.parent / f".{skill_md.name}.5dim.{ts}.bak"
    shutil.copy2(skill_md, backup_path)
    return backup_path

def upgrade_skill(skill_name: str, dry_run: bool = False, rollback: bool = False) -> dict:
    skill_md = SKILL_ROOT / skill_name / "SKILL.md"
    if not skill_md.exists():
        return {"skill": skill_name, "ok": False, "reason": "missing"}
    text = skill_md.read_text(encoding="utf-8")
    if rollback:
        backups = sorted((skill_md.parent).glob(f".{skill_md.name}.5dim.*.bak"))
        if not backups:
            return {"skill": skill_name, "ok": False, "reason": "no backup"}
        latest = backups[-1]
        if dry_run:
            return {"skill": skill_name, "ok": True, "action": "would-rollback", "backup": str(latest)}
        shutil.copy2(latest, skill_md)
        return {"skill": skill_name, "ok": True, "action": "rolled-back", "backup": str(latest)}
    if has_check_block(text):
        return {"skill": skill_name, "ok": True, "action": "skipped", "reason": "already has check block"}
    new_text = text + check_block()
    if dry_run:
        return {"skill": skill_name, "ok": True, "action": "would-apply", "added_chars": len(check_block())}
    bk = backup(skill_md)
    skill_md.write_text(new_text, encoding="utf-8")
    return {"skill": skill_name, "ok": True, "action": "applied", "backup": str(bk)}

def main():
    p = argparse.ArgumentParser(description="给 baoyu 8 个设计类 skill 灌入 5 维自检")
    p.add_argument("--skill", help="单 skill 名")
    p.add_argument("--all", action="store_true", help="升级全部 8 个")
    p.add_argument("--dry-run", action="store_true", help="仅预览,不写文件")
    p.add_argument("--rollback", action="store_true", help="回滚到最近一次备份")
    p.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = p.parse_args()
    targets = [args.skill] if args.skill else DESIGN_SKILLS
    if args.all:
        targets = DESIGN_SKILLS
    if not (args.skill or args.all):
        p.print_help()
        sys.exit(2)
    results = [upgrade_skill(t, dry_run=args.dry_run, rollback=args.rollback) for t in targets]
    applied = sum(1 for r in results if r["ok"] and r.get("action") == "applied")
    skipped = sum(1 for r in results if r["ok"] and r.get("action") == "skipped")
    failed = sum(1 for r in results if not r["ok"])
    summary = {"targets": targets, "applied": applied, "skipped": skipped, "failed": failed, "results": results}
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"{r['skill']}: {r.get('action', r.get('reason'))}")
        print(f"\n总计:applied={applied} skipped={skipped} failed={failed}")
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()