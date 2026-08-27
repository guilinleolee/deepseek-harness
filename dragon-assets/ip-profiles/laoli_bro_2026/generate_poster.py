"""
老李风 IP 海报生成器 V1.0
==========================

融合 3 个资产:
1. qiaomu-mondo V1.1 (Mondo screen-print 美学)
2. IP profile (laoli_bro_2026 的 8 维指纹)
3. 老李风 (laoli-writer V1.0 标点禁令 + 6 维参数化)

输出:
- 老李风对齐的英文 Mondo 提示词
- 老李风对齐的中文版排版指令
- 调用 AI Gateway 实际生成 PNG

使用前需设置环境变量:
  export AI_GATEWAY_API_KEY=sk-xxxxx

依赖:
- qiaomu-mondo 技能 (路径见 MONDO_SKILL_PATH)
- 标准库: json, os, sys, subprocess
"""

import json
import os
import sys
import subprocess
from pathlib import Path

# ===== 路径常量 =====
IP_PROFILE_DIR = Path("C:/Users/li/.claude/ip-profiles/laoli_bro_2026")
IP_PROFILE_JSON = IP_PROFILE_DIR / "ip_profile_8dim.json"
IP_PROMPT_EN = IP_PROFILE_DIR / "prompt_en.txt"
IP_PROMPT_ZH = IP_PROFILE_DIR / "poster_prompt_zh.md"
IP_OUTPUT = IP_PROFILE_DIR / "poster_test_1.png"

MONDO_SKILL = Path("C:/Users/li/.claude/projects/dragon-engine/.claude/skills/qiaomu-mondo-poster-design")


# ===== 老李风标点禁令（自动注入提示词）=====
LAOLI_FORBIDDEN_PUNCTUATION = ["：", "—", "——", "\"", "\""]
LAOLI_FORBIDDEN_WORDS = [
    "说白了", "本质上", "意味着", "换句话说", "不可否认", "值得注意的是",
    "智能", "未来已来", "颠覆", "革命性", "划时代",
]


def load_ip_profile() -> dict:
    """加载 IP profile"""
    with open(IP_PROFILE_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def build_mondo_prompt(ip: dict, article_title: str, article_subtitle: str) -> str:
    """基于 IP profile 动态构建 Mondo 提示词"""

    anchor = ip["dim_8_ip_visual"]["anchor"]
    spec = ip["dim_8_ip_visual"]["spec"]
    ext = ip["dim_8_ip_visual"]["extensions"]

    # 主标题必须通过老李风标点校验
    for pun in LAOLI_FORBIDDEN_PUNCTUATION:
        if pun in article_title:
            raise ValueError(f"标题含老李风禁用标点: {pun}")
    for word in LAOLI_FORBIDDEN_WORDS:
        if word in article_title:
            raise ValueError(f"标题含老李风禁用词: {word}")

    palette = spec["color_palette"]
    palette_str = ", ".join(palette)

    prompt = f"""Mondo screen-print book cover, 9:16 vertical, {anchor['description']},
late afternoon natural outdoor light, warm side-back rim light, three-quarter view 15 degrees,
hands relaxed at sides, thoughtful expression with slight furrow and focused eyes,
subtle closed-mouth smile, medium shot from waist up, head in upper third with 30 percent negative space above for title.

Screen print aesthetic, 3-4 flat color blocks, risograph halftone dots, paper grain,
1-2 pixel misregistration, low saturation, slightly aged paper feel, avoid over-sharpening.

Limited palette: {palette_str}, dominant deep slate, warm orange accent maximum 5 percent.

Composition: single subject, simple layered atmospheric, no clutter, no props, no logos,
no watermarks, no PPT screens, no ties, no blue suits, no stiff corporate portraits,
no on-screen text mockups. Title rendered in clean bold Heiti Chinese sans-serif
in upper 30 percent negative space, no curving, high contrast, no colons no dashes no quotation marks.

Style keywords: {', '.join(spec['style_keywords'])}.
Action: {ext['actions'][0]}.
Expression: {ext['expressions'][0]}.

Mood: experienced ordinary person carefully explaining something they care about,
not celebrity, not film star, not tech keynote, just a real person who has thought this through.

Article title: {article_title}
Article subtitle: {article_subtitle}

Vintage 1970s alternative book cover, Martin Ansin minimalist, Olly Moss clarity,
authentic handmade screen print, ground-level composition, viewer eye level at subject chest."""

    return prompt


def run_mondo_generator(prompt_extra: str, output_path: Path):
    """调用 qiaomu-mondo 脚本生成图片"""
    cmd = [
        "python",
        str(MONDO_SKILL / "scripts" / "generate_mondo_enhanced.py"),
        prompt_extra,
        "book",
        "--style", "martin-ansin",
        "--ai-enhance",
        "--colors", "deep slate, warm orange, cream, black",
        "--aspect-ratio", "9:16",
        "--output", str(output_path),
    ]
    print(f"[执行] {' '.join(cmd)}")
    env = os.environ.copy()
    if "AI_GATEWAY_API_KEY" not in env:
        print("[警告] AI_GATEWAY_API_KEY 未设置, 可能生成失败")
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    print(result.stdout[-2000:] if result.stdout else "")
    if result.stderr:
        print(f"[stderr] {result.stderr[-1000:]}")
    return result.returncode == 0


def main() -> int:
    print("=" * 60)
    print("老李风 IP 海报生成器 V1.0")
    print("=" * 60)

    # 加载 IP profile
    print("\n[1/4] 加载 IP profile...")
    ip = load_ip_profile()
    print(f"  博主: {ip['blogger_name']} ({ip['blogger_id']})")
    print(f"  风格: {ip['dim_7_writing_style']['style_name']}")
    print(f"  色板: {', '.join(ip['dim_8_ip_visual']['spec']['color_palette'])}")

    # 老李风标点校验
    print("\n[2/4] 老李风标点校验...")
    title = "我花了 2 周 把 AI 写作这件事彻底想明白了"
    subtitle = "一个有阅历的普通人的真实感受"
    print(f"  标题: {title}")
    print(f"  副标: {subtitle}")
    for pun in LAOLI_FORBIDDEN_PUNCTUATION:
        if pun in title or pun in subtitle:
            print(f"  [FAIL] 禁用标点: {pun}")
            return 1
    print("  [OK] 标点校验通过")

    # 构建 Mondo 提示词
    print("\n[3/4] 构建 Mondo 提示词...")
    prompt = build_mondo_prompt(ip, title, subtitle)
    print(f"  提示词长度: {len(prompt)} chars")
    print(f"  预览: {prompt[:200]}...")

    # 调用生成器
    print("\n[4/4] 调用 qiaomu-mondo 生成...")
    if not IP_OUTPUT.exists():
        success = run_mondo_generator(prompt, IP_OUTPUT)
        if success:
            print(f"  [OK] 海报已生成: {IP_OUTPUT}")
        else:
            print("  [FAIL] 生成失败, 但提示词已保存到 prompt_en.txt")
    else:
        print(f"  [SKIP] 已存在: {IP_OUTPUT}")

    print("\n" + "=" * 60)
    print("老李风 IP 海报生成完毕")
    print("=" * 60)
    print(f"\n产物清单:")
    print(f"  - {IP_PROMPT_ZH} (中文版排版指令)")
    print(f"  - {IP_PROMPT_EN} (Mondo 英文提示词)")
    print(f"  - {IP_OUTPUT} (最终海报 PNG, 需 AI_GATEWAY_API_KEY)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
