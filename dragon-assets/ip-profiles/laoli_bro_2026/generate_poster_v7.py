"""
老李风角色设定表 V7 · 日漫动画前期参考图
========================================

V6 → V7 修正:
- V6 模型输出的是动漫海报, 不是动画前期参考图
- V7 强调: 动画前期设定资料 / anime production key animation sheet
- 关键词: production reference, line art only, no shading
- 明确要求: 不要上色, 只要线稿 + 极淡色块
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

IP_PROFILE_DIR = Path("C:/Users/li/.claude/ip-profiles/laoli_bro_2026")
IP_OUTPUT_V7 = IP_PROFILE_DIR / "poster_test_7.png"

MINIMAX_API_URL = "https://api.minimaxi.com/v1/image_generation"
MINIMAX_MODEL = "image-01-live"
ASPECT_RATIO = "9:16"


def build_prompt_v7() -> str:
    """V7 提示词: 动画前期参考图 (production key animation reference sheet)"""

    prompt = """Anime production key animation reference sheet, vertical 9:16, clean white
background. Multi-panel layout showing same character from different angles in 6 panels
2 columns 3 rows. Character: ordinary 45 year old Chinese man, square face, short straight
black hair, plain black polo shirt dark trousers, realistic body proportions not chibi
exaggerated. Style: traditional 2D anime production line art thin black outlines, minimal
color mostly white space, simple flat cell shading 2-3 tones only, like Japanese animation
studio pre-production reference board. Each panel separated by thin gray divider lines.
Around each panel small handwritten Chinese annotations and arrows pointing to body parts
explaining posture clothing expression. Panel 1 front view standing relaxed, Panel 2 side
profile view facing right, Panel 3 three-quarter angle view, Panel 4 sitting on chair
explaining gesture one hand raised, Panel 5 leaning forward both hands spread excited
explanation pose, Panel 6 small simplified chibi version confident stance. Title text top
in clean printed Chinese: 角色设定表. Subtitle below: 老李 IP 视觉规格 v1.0. Bottom area
simple color palette spec notes. Pure reference sheet quality, technical document style,
not artistic illustration. No 3D no realistic photo no oil painting no watercolor no
polished anime poster. No watermarks no logos no decorative borders."""


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
    print("老李风角色设定表 V7 · 动画前期参考图")
    print("=" * 60)

    api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not api_key:
        print("[FAIL] 需 MINIMAX_API_KEY")
        return 2

    prompt = build_prompt_v7()
    print(f"\n[V7 提示词] {len(prompt)} chars")

    print("\n[主调用] image-01-live")
    if call_minimax(api_key, prompt, IP_OUTPUT_V7, "image-01-live"):
        return 0

    print("\n[退路] image-01")
    return 0 if call_minimax(api_key, prompt, IP_OUTPUT_V7, "image-01") else 1


if __name__ == "__main__":
    sys.exit(main())