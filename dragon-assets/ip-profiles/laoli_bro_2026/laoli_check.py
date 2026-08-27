"""
老李风 4 层自检 V1.0
====================
对 article_test_1.md 跑 L1~L4 自动校验

退出码:
- 0: 全部 PASS
- 1: 部分 FAIL
- 2: 文件不存在
"""

import re
import sys
from pathlib import Path

ARTICLE = Path("C:/Users/li/.claude/ip-profiles/laoli_bro_2026/article_test_1.md")

# ===== L1 硬性规则 =====
L1_FORBIDDEN_WORDS = ["说白了", "本质上", "意味着", "换句话说", "不可否认", "值得注意的是"]
L1_FORBIDDEN_PUNCT = ["：", "——", "—", "\u201c", "\u201d"]  # ：———""

# ===== L4 老李风专属 =====
L4_LAOLI_KEYWORDS = ["兄弟", "哥们", "我跟你说", "我寻思", "你想想看", "我当时就", "我跟你说",
                      "你看看", "懂你", "我也是", "就这么点事", "慢慢来", "愚钝如我",
                      "这尼玛", "真的就是一声叹息", "我当时就愣住了", "魔幻", "就挺突然的"]
L4_LAOLI_EMOTION = ["自嘲", "无奈", "兴奋", "吐槽", "温情", "较真"]


def check(name, ok, detail=""):
    status = "[OK]   PASS" if ok else "[FAIL] FAIL"
    line = f"  {status}  {name}"
    if detail and not ok:
        line += f" -- {detail}"
    print(line)
    return ok


def extract_body(text):
    """去掉 frontmatter 和元数据, 只校验正文"""
    lines = text.split("\n")
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "================================================================================" and i > 5:
            # 找到第一个分割线之后
            continue
        if "兄弟们" in line or "我今天" in line or "我花了" in line:
            body_start = i
            break
    body_end = len(lines)
    for i in range(body_start, len(lines)):
        if "【老李风格自检" in lines[i]:
            body_end = i
            break
    return "\n".join(lines[body_start:body_end])


def main():
    if not ARTICLE.exists():
        print(f"[FAIL] 文章不存在: {ARTICLE}")
        return 2

    text = ARTICLE.read_text(encoding="utf-8")
    body = extract_body(text)

    print("=" * 60)
    print("老李风 4 层自检 · article_test_1.md")
    print("=" * 60)
    results = []

    # ===== L1 硬性规则 =====
    print("\n[L1 硬性规则]")
    for w in L1_FORBIDDEN_WORDS:
        cnt = body.count(w)
        results.append(check(f"禁用词「{w}」零命中", cnt == 0, f"出现 {cnt} 次"))
    for p in L1_FORBIDDEN_PUNCT:
        cnt = body.count(p)
        results.append(check(f"禁用标点「{p}」零命中", cnt == 0, f"出现 {cnt} 次"))

    # 工具名具体性
    tools = ["9.9", "199", "ChatGPT", "Claude", "DeepSeek", "豆包"]
    tools_found = [t for t in tools if t in body]
    results.append(check("工具名/价格具体", len(tools_found) >= 4,
                         f"找到 {len(tools_found)}/{len(tools)}: {tools_found}"))

    # 套话开场检查
    cliche_openings = ["近年来", "随着", "在当今", "在当前", "在数字化", "在信息化", "在 AI 时代",
                        "随着人工智能", "随着科技", "随着互联网", "随着大数据"]
    has_cliche = any(body[:500].count(o) > 0 for o in cliche_openings)
    results.append(check("套话开场零命中", not has_cliche))

    # ===== L2 风格一致性 =====
    print("\n[L2 风格一致性]")
    # 句式断裂 (单独成行的"。" "魔幻。" "就挺突然的。"等)
    sentence_breaks = re.findall(r"^[^\n]*[。！] ?$", body, re.MULTILINE)
    results.append(check(f"句式断裂 ≥ 3 处", len(sentence_breaks) >= 3, f"共 {len(sentence_breaks)} 处"))

    # 老李式表达数量
    laoli_phrases = sum(1 for kw in L4_LAOLI_KEYWORDS if kw in body)
    results.append(check(f"老李式表达 ≥ 8", laoli_phrases >= 8, f"共 {laoli_phrases} 个"))

    # 标点禁令二次确认
    punct_again = sum(body.count(p) for p in L1_FORBIDDEN_PUNCT)
    results.append(check("标点禁令二次确认", punct_again == 0, f"累计 {punct_again}"))

    # ===== L3 内容质量 =====
    print("\n[L3 内容质量]")
    # 数字具体到元（接受 "X 元" 或 "X 包月/包年/一个月" 或裸金额 9.9/199/998）
    yuan_explicit = len(re.findall(r"\d+(?:\.\d+)? ?元", body))
    yuan_implicit = len(re.findall(r"\d+(?:\.\d+)? ?(?:包月|包年|一个月|一年)", body))
    yuan_bare = sum(1 for amt in ["9.9", "199", "998", "49", "99", "1999"] if amt in body)
    total_yuan = yuan_explicit + yuan_implicit + yuan_bare
    results.append(check(
        f"价格/数字具体（元/包月/裸金额）≥ 3",
        total_yuan >= 3,
        f"显式元 {yuan_explicit} 处 + 隐式包月 {yuan_implicit} 处 + 裸金额 {yuan_bare} 处 = {total_yuan}"
    ))

    # 年龄数字
    age_count = len(re.findall(r"\d+ ?岁", body))
    results.append(check(f"具体年龄/数量", age_count >= 2, f"共 {age_count} 处"))

    # 生活场景类比 (至少 2 个)
    life_scenes = ["装修", "带娃", "做饭", "买菜", "通勤", "打车", "修车", "4S", "麻将", "砍价",
                   "快递", "外卖", "银行", "排队", "修手机", "修电脑", "买房", "开发商", "淘宝",
                   "计算器", "Word", "相机", "抱娃", "奶粉", "哈佛"]
    scenes_found = [s for s in life_scenes if s in body]
    results.append(check(f"生活场景类比 ≥ 3", len(scenes_found) >= 3, f"共 {len(scenes_found)}: {scenes_found}"))

    # ===== L4 老李风专属活人感 =====
    print("\n[L4 老李风专属 · 活人感终审]")
    # 称呼集体化（"兄弟们"）
    brothers = body.count("兄弟")
    results.append(check(f"「兄弟」称呼 ≥ 3", brothers >= 3, f"共 {brothers} 次"))

    # 情绪具象化
    emotions_found = [e for e in L4_LAOLI_EMOTION if e in body]
    # 这些是隐式情绪, 用关键词代替
    implicit_emotions = ["我当时就愣住了", "就挺突然的", "真的就是一声叹息", "这一下给我干懵了", "我寻思"]
    implicit_found = [e for e in implicit_emotions if e in body]
    results.append(check(f"情绪具象化 ≥ 3", len(implicit_found) >= 3, f"共 {len(implicit_found)}"))

    # 谦逊铺垫
    modest = ["我也不是", "愚钝", "我自己也不是", "慢慢来", "就这么点事"]
    modest_found = [m for m in modest if m in body]
    results.append(check(f"谦逊铺垫", len(modest_found) >= 1, f"共 {len(modest_found)}: {modest_found}"))

    # ===== 总结 =====
    passed = sum(results)
    total = len(results)
    print("\n" + "=" * 60)
    print(f"老李风 4 层自检: {passed}/{total} PASS")
    print("=" * 60)
    if passed == total:
        print("[OK] 全部通过！文章符合老李风 v1.0 标准")
        return 0
    else:
        print(f"[WARN] {total - passed} 项未通过, 需要修改")
        return 1


if __name__ == "__main__":
    sys.exit(main())
