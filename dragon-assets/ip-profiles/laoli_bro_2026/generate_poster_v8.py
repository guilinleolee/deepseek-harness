"""
老李风角色设定表 V8 · 普通办公族多格参考图
============================================

V7 模型跑到武士风 (过度解读"角色参考图")
V8 强调: 普通中国办公族中年大叔 (反面关键词: 武士/战士/动漫/古装/西幻)

保留 V7 的多格布局 (这是对的)
换掉 V7 的"anime production key animation" 描述
改用"Chinese new media editorial character reference"
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

IP_PROFILE_DIR = Path("C:/Users/li/.claude/ip-profiles/laoli_bro_2026")
IP_OUTPUT_V8 = IP_PROFILE_DIR / "poster_test_8.png"

MINIMAX_API_URL = "https://api.minimaxi.com/v1/image_generation"
MINIMAX_MODEL = "image-01-live"
ASPECT_RATIO = "9:16"


def build_prompt_v8() -> str:
    """V8 提示词: 普通中年办公族参考图 (避免武士/动漫)"""

    prompt = """Character reference sheet illustration for Chinese new media content creator,
vertical 9:16 format, clean white background. Multi-panel layout showing one character in
5 panels arranged in 2 columns. Character: ordinary middle-aged Chinese man, age 45,
ordinary-looking everyday person you see in any office building, square face, short straight
black hair parted on side, slightly weathered skin with subtle wrinkles, NOT handsome NOT
young NOT anime NOT warrior NOT fantasy NOT samurai NOT historical NOT fantasy costume.
Wearing modern plain black polo shirt collar and dark casual trousers and simple sneakers,
holding nothing, no weapons no props no armor. Body proportions realistic adult human.
Style: clean 2D vector flat illustration, simplified but not chibi exaggerated, friendly
approachable like Zhihu WeChat 36kr editorial comics character, soft outlines, limited
flat color fills using only deep slate gray warm orange cream black fog gray palette.
Each panel separated by thin gray lines. Panel 1 front view standing relaxed hands at
sides, Panel 2 side profile view, Panel 3 three-quarter view with friendly smile, Panel 4
sitting on simple chair explaining gesture one hand open palm up, Panel 5 walking pose
with one hand in pocket casual. Around panels small handwritten Chinese notes about pose
and expression. No fantasy armor no weapons no samurai no ancient costume no anime magic
no magical effects. Pure modern ordinary office worker aesthetic."""


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
    print("老李风角色设定表 V8 · 普通办公族多格")
    print("=" * 60)

    api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not api_key:
        print("[FAIL] 需 MINIMAX_API_KEY")
        return 2

    prompt = build_prompt_v8()
    print(f"\n[V8 提示词] {len(prompt)} chars")

    print("\n[主调用] image-01-live")
    if call_minimax(api_key, prompt, IP_OUTPUT_V8, "image-01-live"):
        return 0

    print("\n[退路] image-01")
    return 0 if call_minimax(api_key, prompt, IP_OUTPUT_V8, "image-01") else 1


if __name__ == "__main__":
    sys.exit(main())