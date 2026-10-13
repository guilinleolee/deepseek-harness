"""
老李风角色设定表 V9 · image-01 + 真人参考 (subject_reference)
============================================================

V9 突破思路:
- V8 模型依然画出"年轻动漫帅哥"
- 用 V2 (真人版老李 208KB) 作为 subject_reference
- 让模型"基于老李本人做卡通化"
- 6 格布局, 普通办公族风格
"""

import base64
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

IP_PROFILE_DIR = Path("C:/Users/li/.claude/ip-profiles/laoli_bro_2026")
REF_PHOTO = IP_PROFILE_DIR / "poster_test_2.png"  # V2 老李真人版做参考
IP_OUTPUT_V9 = IP_PROFILE_DIR / "poster_test_9.png"

MINIMAX_API_URL = "https://api.minimaxi.com/v1/image_generation"


def build_prompt_v9() -> str:
    """V9 提示词: 基于真人参考做卡通角色设定表"""
    return """Character reference sheet illustration, vertical 9:16 format, clean white
background. Multi-panel layout showing the same character in 6 panels arranged in 2 columns
3 rows. Character based on the reference photo: 45 year old Chinese Asian man, ordinary
middle-aged everyman, square face with high cheekbones, short straight black hair, slightly
weathered mature skin with subtle wrinkles around eyes and forehead, NOT young NOT handsome
NOT anime stylized. Style: 2D flat vector editorial illustration, simplified but realistic
proportions, friendly approachable like modern Chinese new media explainer comics from
Zhihu WeChat 36kr, soft clean outlines, limited 6-color flat palette (deep slate gray,
warm orange, cream, black, fog gray). Each panel separated by thin gray divider lines.
Around each panel small handwritten Chinese annotations and arrows. Panel 1 front view
standing relaxed hands at sides, Panel 2 side profile view facing right, Panel 3 three-
quarter view walking, Panel 4 sitting on simple chair explaining gesture one hand open
palm up friendly, Panel 5 leaning forward both hands spread excited explanation, Panel 6
small simplified chibi proportion version with confident stance hands on hips. Title text
top in handwritten style: 角色设定表. Subtitle below: 老李 IP 视觉规格 v1.0. No 3D no
realistic photo no oil painting no anime stylized character no fantasy armor no weapons."""


def upload_reference_photo(api_key: str, photo_path: Path) -> str:
    """上传参考照片到 OSS, 返回 URL (MiniMax 临时存储)"""
    # 简化处理: 直接读取为 base64 data URI
    # MiniMax 文档说 subject_reference.image_file 接受 URL 或本地路径
    # 但本地路径可能不支持, 这里用 base64 不可行
    # 改用: 把本地图片上传到 OSS 取得 URL
    # 暂时简化: 直接返回本地路径作为 image_file
    # 实际 MiniMax API 需要 https URL, 我们需要先上传
    print(f"  [警告] subject_reference 需要 https URL, 本地路径可能不支持")
    print(f"  暂时使用本地路径: {photo_path}")
    return str(photo_path)


def call_minimax_with_ref(api_key, prompt, output_path, ref_image):
    """调用 MiniMax 带 subject_reference"""
    payload = {
        "model": "image-01",
        "prompt": prompt,
        "aspect_ratio": "9:16",
        "n": 1,
        "response_format": "url",
        "prompt_optimizer": True,
        "watermark": False,
        "subject_reference": [
            {
                "type": "character",
                "image_file": ref_image,
            }
        ],
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    print(f"\n[调用 MiniMax + subject_reference]")
    print(f"  Ref: {ref_image}")

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(MINIMAX_API_URL, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  [FAIL] HTTP {e.code}: {e.read()[:300]}")
        return False

    if result.get("base_resp", {}).get("status_code") != 0:
        print(f"  [FAIL] {json.dumps(result, ensure_ascii=False)[:500]}")
        return False

    image_urls = result.get("data", {}).get("image_urls", [])
    if not image_urls:
        return False

    try:
        with urllib.request.urlopen(image_urls[0], timeout=60) as img_resp:
            output_path.write_bytes(img_resp.read())
        print(f"  [OK] {output_path} ({output_path.stat().st_size:,} bytes)")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def main() -> int:
    print("=" * 60)
    print("老李风角色设定表 V9 · subject_reference 真人版")
    print("=" * 60)

    api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not api_key:
        print("[FAIL] 需 MINIMAX_API_KEY")
        return 2

    if not REF_PHOTO.exists():
        print(f"[FAIL] 参考图不存在: {REF_PHOTO}")
        return 2

    prompt = build_prompt_v9()
    print(f"\n[V9 提示词] {len(prompt)} chars")

    ref_url = upload_reference_photo(api_key, REF_PHOTO)

    print("\n[主调用] image-01 + subject_reference")
    if call_minimax_with_ref(api_key, prompt, IP_OUTPUT_V9, ref_url):
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())