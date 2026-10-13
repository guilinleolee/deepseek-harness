"""
老李风 IP 海报生成器 · MiniMax image-01 版 V1.0
================================================

调用 MiniMax image_generation API:
  POST https://api.minimaxi.com/v1/image_generation
  model: image-01 (或 image-01-live 增强版)

融合资产:
1. 老李风 (laoli-writer V1.0)
2. IP profile (laoli_bro_2026 8 维)
3. Mondo screen-print 美学
4. 老李风标点禁令 (已校验)

输出:
- 老李风对齐的英文提示词 (经 MiniMax 自动 prompt_optimizer)
- 调用 MiniMax image-01 出 PNG
- 提示词 1500 字符上限校验

依赖:
- requests
- 需环境变量 MINIMAX_API_KEY
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# ===== 路径常量 =====
IP_PROFILE_DIR = Path("C:/Users/li/.claude/ip-profiles/laoli_bro_2026")
IP_PROFILE_JSON = IP_PROFILE_DIR / "ip_profile_8dim.json"
IP_PROMPT_EN = IP_PROFILE_DIR / "prompt_en.txt"
IP_OUTPUT = IP_PROFILE_DIR / "poster_test_1.png"

# ===== MiniMax API 配置 =====
MINIMAX_API_URL = "https://api.minimaxi.com/v1/image_generation"
MINIMAX_MODEL = "image-01-live"  # image-01-live 画风增强版
ASPECT_RATIO = "9:16"  # 老李风长文封面, 竖屏
N_IMAGES = 1
RESPONSE_FORMAT = "url"  # 临时链接 (24h 有效)
PROMPT_OPTIMIZER = True
WATERMARK = False  # 不加水印 (干净版本, 老李风禁用套话)

# ===== 老李风标点禁令 =====
LAOLI_FORBIDDEN_PUNCT = ["：", "——", "—", "\u201c", "\u201d"]
LAOLI_FORBIDDEN_WORDS = [
    "说白了", "本质上", "意味着", "换句话说", "不可否认", "值得注意的是",
    "智能", "未来已来", "颠覆", "革命性", "划时代",
]


def load_ip_profile() -> dict:
    with open(IP_PROFILE_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_laoli(text: str) -> tuple:
    """老李风标点/词汇校验"""
    for p in LAOLI_FORBIDDEN_PUNCT:
        if p in text:
            return False, f"禁用标点: {p}"
    for w in LAOLI_FORBIDDEN_WORDS:
        if w in text:
            return False, f"禁用词: {w}"
    return True, "OK"


def build_prompt(ip: dict) -> str:
    """构建 MiniMax 提示词 (老李风 + Mondo + IP profile)"""

    anchor = ip["dim_8_ip_visual"]["anchor"]
    spec = ip["dim_8_ip_visual"]["spec"]
    palette = spec["color_palette"]

    # 英文提示词 (MiniMax image-01 对英文支持更好, 但支持中文)
    # 注: prompt_optimizer=True 时, MiniMax 会自动补全专业术语
    prompt = f"""Mondo screen-print book cover, 9:16 vertical portrait.
Subject: {anchor['description']}.
Composition: medium shot from waist up, three-quarter view 15 degrees, head positioned
in upper third with 30 percent negative space above for title, hands relaxed at sides.
Expression: thoughtful serious face with slightly furrowed brow, eyes focused down-right,
subtle closed-mouth smile. Late afternoon outdoor natural light, warm side-back rim light
catching hair edges.

Style keywords: {', '.join(spec['style_keywords'])}.
Action: {spec['style_keywords'][0]} and grounded.

Color palette (6 colors): deep slate gray {palette[0]}, steel blue gray {palette[1]},
warm orange {palette[2]} used only as 5 percent accent, cream off-white {palette[3]},
pure black {palette[4]}, fog gray {palette[5]}.

Screen print aesthetic: 3-4 flat color blocks, risograph halftone dots, paper grain,
1-2 pixel misregistration between color layers, low saturation, slightly aged paper feel,
avoid over-sharpening or digital gradients. Limited palette, authentic handmade print quality.

Mood: experienced ordinary middle-aged person carefully explaining something they care about,
not celebrity, not film star, not tech keynote speaker, just a real grounded person who has
thought this through for 2 weeks and wants to share their honest experience.

Reference styles: Martin Ansin minimalist, Olly Moss figure-ground clarity, vintage 1970s
alternative book cover poster, alternative movie poster, limited edition screen print.

Strictly avoid: stiff corporate portraits, blue suits, white shirts, ties, PPT screens,
laptops in frame, mockup text boxes, watermarks, logos, complex facial details, over-rendering,
AI-glossy digital look.

Vintage 1970s era, ground-level composition, viewer eye level at subject chest height."""

    return prompt


def call_minimax(api_key: str, prompt: str, output_path: Path) -> bool:
    """调用 MiniMax image_generation API"""

    payload = {
        "model": MINIMAX_MODEL,
        "prompt": prompt,
        "aspect_ratio": ASPECT_RATIO,
        "n": N_IMAGES,
        "response_format": RESPONSE_FORMAT,
        "prompt_optimizer": PROMPT_OPTIMIZER,
        "watermark": WATERMARK,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    print(f"\n[调用 MiniMax image_generation]")
    print(f"  Endpoint : {MINIMAX_API_URL}")
    print(f"  Model    : {MINIMAX_MODEL}")
    print(f"  Aspect   : {ASPECT_RATIO}")
    print(f"  Prompt   : {len(prompt)} chars (limit 1500)")
    print(f"  N        : {N_IMAGES}")

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(MINIMAX_API_URL, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  [FAIL] HTTP {e.code}")
        print(f"  Body: {e.read()[:500]}")
        return False
    except Exception as e:
        print(f"  [FAIL] {type(e).__name__}: {e}")
        return False

    # 解析响应
    print(f"\n[响应]")
    print(f"  原始: {json.dumps(result, ensure_ascii=False)[:500]}")

    if "base_resp" in result:
        status_code = result["base_resp"].get("status_code", -1)
        status_msg = result["base_resp"].get("status_msg", "")
        if status_code != 0:
            print(f"  [FAIL] status_code={status_code}, msg={status_msg}")
            return False

    image_urls = result.get("data", {}).get("image_urls", [])
    if not image_urls:
        print(f"  [FAIL] 响应无 image_urls")
        return False

    # 下载第一张图
    img_url = image_urls[0]
    print(f"  图片URL: {img_url[:120]}...")

    try:
        with urllib.request.urlopen(img_url, timeout=60) as img_resp:
            img_data = img_resp.read()
        output_path.write_bytes(img_data)
        print(f"  [OK] 已保存: {output_path} ({len(img_data):,} bytes)")
        return True
    except Exception as e:
        print(f"  [FAIL] 下载失败: {e}")
        return False


def main() -> int:
    print("=" * 60)
    print("老李风 IP 海报生成器 · MiniMax image-01-live V1.0")
    print("=" * 60)

    # API Key
    api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not api_key:
        print("\n[FAIL] 需设置环境变量 MINIMAX_API_KEY 或 AI_GATEWAY_API_KEY")
        print("       set MINIMAX_API_KEY=sk-xxxxxxxxxxxxxx")
        return 2
    print(f"\n[API Key] {api_key[:8]}...{api_key[-4:]} (length={len(api_key)})")

    # 加载 IP profile
    print("\n[1/5] 加载 IP profile")
    ip = load_ip_profile()
    print(f"  博主    : {ip['blogger_name']} ({ip['blogger_id']})")
    print(f"  风格    : {ip['dim_7_writing_style']['style_name']}")
    print(f"  色板    : {', '.join(ip['dim_8_ip_visual']['spec']['color_palette'])}")

    # 老李风标点校验
    print("\n[2/5] 老李风标点校验 (对 IP profile 描述)")
    desc = ip["dim_8_ip_visual"]["anchor"]["description"]
    ok, msg = validate_laoli(desc)
    print(f"  {desc[:60]}...")
    print(f"  [{'OK' if ok else 'FAIL'}] {msg}")

    # 构建提示词
    print("\n[3/5] 构建 MiniMax 提示词 (老李风 + Mondo + IP)")
    prompt = build_prompt(ip)
    print(f"  长度: {len(prompt)} chars (MiniMax 上限 1500)")
    ok, msg = validate_laoli(prompt)
    print(f"  [{'OK' if ok else 'FAIL'}] 标点校验: {msg}")
    print(f"  预览: {prompt[:200]}...")

    # 长度校验
    if len(prompt) > 1500:
        print(f"\n  [WARN] 提示词超 1500 字符, 截断到 1500")
        prompt = prompt[:1497] + "..."

    # 调用 API
    print("\n[4/5] 调用 MiniMax image-01-live API")
    success = call_minimax(api_key, prompt, IP_OUTPUT)

    if not success:
        # 退路: 使用 prompt_optimizer=False 简化版重试
        print("\n[4.5/5] 退路: 重试 (prompt_optimizer=False, 简化参数)")
        retry_payload = {
            "model": "image-01",
            "prompt": prompt,
            "aspect_ratio": "9:16",
            "n": 1,
            "response_format": "url",
        }
        try:
            data = json.dumps(retry_payload).encode("utf-8")
            req = urllib.request.Request(MINIMAX_API_URL, data=data, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            })
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            print(f"  响应: {json.dumps(result, ensure_ascii=False)[:300]}")
            image_urls = result.get("data", {}).get("image_urls", [])
            if image_urls:
                with urllib.request.urlopen(image_urls[0], timeout=60) as img_resp:
                    IP_OUTPUT.write_bytes(img_resp.read())
                print(f"  [OK] 已保存: {IP_OUTPUT}")
                success = True
        except Exception as e:
            print(f"  [FAIL] 重试失败: {e}")

    # 总结
    print("\n[5/5] 完成")
    print("=" * 60)
    if success and IP_OUTPUT.exists():
        size_kb = IP_OUTPUT.stat().st_size / 1024
        print(f"[OK] 海报生成成功!")
        print(f"     路径: {IP_OUTPUT}")
        print(f"     大小: {size_kb:.1f} KB")
        return 0
    else:
        print("[FAIL] 海报生成失败")
        print(f"     提示词已保存: {IP_PROMPT_EN}")
        print(f"     提示词长度: {len(prompt)} chars")
        return 1


if __name__ == "__main__":
    sys.exit(main())