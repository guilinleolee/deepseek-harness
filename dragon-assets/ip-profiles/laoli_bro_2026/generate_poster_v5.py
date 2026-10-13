"""
老李风讲解图 V5 · 无人物纯场景科普图
====================================

V4 修正思路转变:
- V1/V2/V3/V4 都在画人物 → 模型容易画成"帅哥/外国人"
- V5 改为不画人脸, 只画桌面+AI工具+价格标签+日历的科普插图
- 风格: 极简 2D 矢量信息图 (infographic)
- 类似 36氪 / 知乎专栏 / 得到 讲解图
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

IP_PROFILE_DIR = Path("C:/Users/li/.claude/ip-profiles/laoli_bro_2026")
IP_OUTPUT_V5 = IP_PROFILE_DIR / "poster_test_5.png"

MINIMAX_API_URL = "https://api.minimaxi.com/v1/image_generation"
MINIMAX_MODEL = "image-01-live"
ASPECT_RATIO = "9:16"


def build_prompt_v5() -> str:
    """V5 提示词: 无人物科普图, 2D 矢量信息图风格"""

    prompt = """Modern Chinese new media infographic, 2D flat vector style, editorial explainer
graphic, vertical 9:16 poster. No human face, just objects scene. Top 30 percent empty
clean white background for text title overlay. Middle: wooden desk from above slightly
angled, on desk - laptop with chat bubble icons, stack of paper with notes, coffee mug,
smartphone showing chat, reading glasses, pen. Around desk: floating cartoon speech bubble
icons in flat circular design representing AI tools, each with tiny face icon. Small
price tags 9.9 yuan 199 yuan 998 yuan near tool bubbles. Calendar showing 14 days two
weeks marker. Below desk: simple flat icons row - human hand icon versus robot AI hand
icon, side by side comparison. Color palette strictly: deep slate gray background, warm
orange only on highlights, cream off-white space, pure black outlines, fog gray desk
surface. Style: clean flat 2D vector, single weight black line outlines, no gradients no
shadows no 3D no realistic rendering no anime no manga no portrait. Modern Chinese new
media comic style from Zhihu WeChat 36kr Caixin. Friendly approachable minimal aesthetic,
like Vox explainer. Top space clearly empty for text overlay, no embedded text."""


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
    print("老李风讲解图 V5 · 无人物科普图")
    print("=" * 60)

    api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not api_key:
        print("[FAIL] 需 MINIMAX_API_KEY")
        return 2

    prompt = build_prompt_v5()
    print(f"\n[V5 提示词] {len(prompt)} chars")

    print("\n[主调用] image-01-live")
    if call_minimax(api_key, prompt, IP_OUTPUT_V5, "image-01-live"):
        return 0

    print("\n[退路] image-01")
    return 0 if call_minimax(api_key, prompt, IP_OUTPUT_V5, "image-01") else 1


if __name__ == "__main__":
    sys.exit(main())