"""
老李风 IP 角色设定图 V6 · Character Sheet 风格
==============================================

参考截图风格:
- 01 角色主播图: 角色正面/侧面/背面/3-4 视图, 配姿势+服饰+表情标注
- 03 动作/表情/小比例细节草图: 6 个不同姿态+小比例表情包
- 风格: 黑白线稿 + 局部淡彩 + 大量手写注释
- 用途: 老李 IP 形象设定表 (供后续所有图生成保持一致性)

V6 提示词:
- 多个分格 (multi-panel grid)
- 同一个老李角色 (45 岁/黑 polo/短直发/普通中年)
- 不同角度和姿态
- 手写风格注释 (中文风格)
- 9:16 竖屏排列 6 个分格
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

IP_PROFILE_DIR = Path("C:/Users/li/.claude/ip-profiles/laoli_bro_2026")
IP_OUTPUT_V6 = IP_PROFILE_DIR / "poster_test_6.png"

MINIMAX_API_URL = "https://api.minimaxi.com/v1/image_generation"
MINIMAX_MODEL = "image-01-live"
ASPECT_RATIO = "9:16"


def build_prompt_v6() -> str:
    """V6 提示词: 老李角色设定表 (character sheet)"""

    prompt = """Character design sheet reference illustration, vertical 9:16 poster, white clean
background with light gray grid lines. Multi-panel layout showing same character in different
poses. Character: 45 year old Chinese Asian man, ordinary everyman not handsome, square face
high cheekbones, short straight black hair neatly trimmed, weathered mature skin, wearing
plain basic black polo shirt collar open and dark casual trousers no tie. Body proportions
realistic not anime not chibi exaggerated. Layout: 6 panels in 2 columns 3 rows. Panel 1
front view standing relaxed, Panel 2 side profile facing right, Panel 3 three-quarter view
walking, Panel 4 sitting at desk with laptop explaining gesture, Panel 5 leaning forward
hands spread excited explaining, Panel 6 small chibi simplified version with hands on hips.
Style: clean line art with thin black outlines, minimal flat color fills (deep slate gray
warm orange cream black fog gray only), hand-drawn sketchy quality like animation pre-
production character sheet. Around each panel small handwritten style annotations and
arrows pointing to body parts explaining posture clothing facial expression. Title text
at top in handwritten style: 角色设定表. Empty white spaces between panels. No 3D no
realistic photo no oil painting, sketchy reference quality. No watermarks no logos."""


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
    print("老李风角色设定表 V6 · Character Sheet")
    print("=" * 60)

    api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not api_key:
        print("[FAIL] 需 MINIMAX_API_KEY")
        return 2

    prompt = build_prompt_v6()
    print(f"\n[V6 提示词] {len(prompt)} chars")

    print("\n[主调用] image-01-live")
    if call_minimax(api_key, prompt, IP_OUTPUT_V6, "image-01-live"):
        return 0

    print("\n[退路] image-01")
    return 0 if call_minimax(api_key, prompt, IP_OUTPUT_V6, "image-01") else 1


if __name__ == "__main__":
    sys.exit(main())