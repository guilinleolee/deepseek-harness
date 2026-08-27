"""
老李风 IP 卡通讲解图生成器 V4
==============================

V3 → V4 修正:
- V3 模型默认输出 3D 渲染图 (即使是 live 版)
- V4 强制使用 2D 矢量插画 / 编辑漫画风描述
- 明确关键词: 2D vector, editorial illustration, hand-drawn, line art
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

IP_PROFILE_DIR = Path("C:/Users/li/.claude/ip-profiles/laoli_bro_2026")
IP_OUTPUT_V4 = IP_PROFILE_DIR / "poster_test_4.png"

MINIMAX_API_URL = "https://api.minimaxi.com/v1/image_generation"
MINIMAX_MODEL = "image-01-live"
ASPECT_RATIO = "9:16"


def build_prompt_v4() -> str:
    """V4 提示词: 强制 2D 编辑插画风"""

    prompt = """2D editorial illustration, hand-drawn vector style, flat colors no shading,
no gradients, clean line art, contemporary Chinese new media explainer comic style.
Vertical 9:16 poster format. Scene: middle-aged Chinese man cartoon character with
slightly simplified cartoon proportions (slightly larger head), wearing plain black
polo shirt, sitting at a wooden desk with a laptop. Multiple speech bubbles and UI
cards floating around him representing different AI tools like ChatGPT Claude DeepSeek
icons in simple flat circle/rectangle icons. Simple round head, basic facial features
only, friendly smile. Color palette: deep slate gray background dominant, warm orange
highlights on tool icons, cream skin tone, pure black hair and polo, fog gray desk.
Composition: top 30 percent empty white space for text title overlay, character in
middle ground, desk surface at bottom third. Small price tag stickers 9.9 yuan 199
yuan 998 yuan scattered around the floating icons, plus a small calendar showing
14 days two weeks marker. Style references: New Yorker editorial cartoon, Vox explainer
illustration style, modern Chinese new media comics from Zhihu WeChat 36kr style.
No 3D render, no photographic style, no realistic rendering, no anime, no manga, no
oil painting, no complex textures, no detailed wrinkles, no glasses, no suit, no tie.
Flat 2D vector, simple geometric shapes, friendly approachable aesthetic, single weight
black outlines, limited 6-color flat palette only."""

    return prompt


def call_minimax(api_key, prompt, output_path, model):
    payload = {
        "model": model, "prompt": prompt, "aspect_ratio": ASPECT_RATIO,
        "n": 1, "response_format": "url", "prompt_optimizer": True, "watermark": False,
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(MINIMAX_API_URL, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"[FAIL] HTTP {e.code}: {e.read()[:300]}")
        return False

    if result.get("base_resp", {}).get("status_code") != 0:
        print(f"[FAIL] {json.dumps(result, ensure_ascii=False)[:300]}")
        return False

    image_urls = result.get("data", {}).get("image_urls", [])
    if not image_urls:
        return False

    try:
        with urllib.request.urlopen(image_urls[0], timeout=60) as img_resp:
            output_path.write_bytes(img_resp.read())
        print(f"[OK] {output_path} ({output_path.stat().st_size:,} bytes)")
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def main() -> int:
    print("=" * 60)
    print("老李风卡通讲解图 V4 · 2D 矢量插画")
    print("=" * 60)

    api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not api_key:
        print("[FAIL] 需 MINIMAX_API_KEY")
        return 2

    prompt = build_prompt_v4()
    print(f"\n[V4 提示词] {len(prompt)} chars")

    print("\n[主调用] image-01-live (2D 矢量)")
    if call_minimax(api_key, prompt, IP_OUTPUT_V4, "image-01-live"):
        return 0

    print("\n[退路] image-01")
    return 0 if call_minimax(api_key, prompt, IP_OUTPUT_V4, "image-01") else 1


if __name__ == "__main__":
    sys.exit(main())