"""
老李风 IP 海报生成器 · MiniMax image-01 V2.0
=============================================

V2 修正要点 (V1 → V2):
1. ✅ 黄种人脸型 (V1 偏白人/欧洲脸)
2. ✅ 短直黑发 (V1 卷发)
3. ✅ 黑色 Polo 衫主体 (V1 偏蓝色衬衫)
4. ✅ 留 30% 头部空间 (V1 没留白)
5. ✅ 45 岁真实感 (V1 像 30 多岁)
6. ✅ 纪实摄影感 (V1 太"漂亮")

新参数:
- model: image-01 (基础版, 更写实, 不像 image-01-live 偏艺术化)
- prompt_optimizer: True
- 增加 "Asian Chinese middle-aged man, realistic documentary photo, not stylized"
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

IP_PROFILE_DIR = Path("C:/Users/li/.claude/ip-profiles/laoli_bro_2026")
IP_PROFILE_JSON = IP_PROFILE_DIR / "ip_profile_8dim.json"
IP_OUTPUT_V2 = IP_PROFILE_DIR / "poster_test_2.png"  # V2 版本

MINIMAX_API_URL = "https://api.minimaxi.com/v1/image_generation"
MINIMAX_MODEL = "image-01"  # V2 改用基础版, 比 live 更写实
ASPECT_RATIO = "9:16"
N_IMAGES = 1


def load_ip_profile() -> dict:
    with open(IP_PROFILE_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt_v2(ip: dict) -> str:
    """V2 提示词 - 黄种人真实感"""

    palette = ip["dim_8_ip_visual"]["spec"]["color_palette"]

    # V2 提示词 (压缩到 ≤1400 chars)
    prompt = """Documentary portrait of 45 year old Chinese Asian man, straight short black
hair, square face, weathered skin with wrinkles, ordinary everyman not model. Wearing plain
basic black polo shirt, collar open, no tie. Medium shot waist up, three-quarter view,
head in upper third with 30 percent empty negative space above for text overlay.
Expression: thoughtful furrowed brow, eyes focused, subtle closed-mouth smile, real person
sharing honest opinion after thinking 2 weeks. Late afternoon outdoor natural light,
warm rim light on hair edges, soft natural shadows. Blurred outdoor park trees background,
muted greenish grayish tones, depth of field bokeh. Color palette: deep slate gray dominant,
warm orange 5 percent accent, cream face highlights, pure black hair and polo, fog gray
shadows, low saturation documentary feel. Realistic documentary photography not digital art
not illustration, authentic phone-camera photojournalism. Avoid: white European face, curly
wavy hair, blue green eyes, beard glasses, suit tie, blue white shirt, stiff pose, smiling
teeth, young attractive model, Hollywood lighting, fantasy illustration, oil painting, anime
cartoon, mockup text watermarks logos. 50mm prime lens, natural skin texture, film grain,
ISO 400, f/2.8, available light only."""

    return prompt


def call_minimax(api_key: str, prompt: str, output_path: Path, model: str = "image-01") -> bool:
    """调用 MiniMax image_generation API"""
    payload = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": ASPECT_RATIO,
        "n": N_IMAGES,
        "response_format": "url",
        "prompt_optimizer": True,
        "watermark": False,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    print(f"\n[调用 MiniMax]")
    print(f"  Model    : {model}")
    print(f"  Prompt   : {len(prompt)} chars")
    print(f"  Aspect   : {ASPECT_RATIO}")

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

    status_code = result.get("base_resp", {}).get("status_code", -1)
    if status_code != 0:
        print(f"  [FAIL] status_code={status_code}")
        print(f"  Body: {json.dumps(result, ensure_ascii=False)[:500]}")
        return False

    image_urls = result.get("data", {}).get("image_urls", [])
    if not image_urls:
        print(f"  [FAIL] 无 image_urls")
        return False

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
    print("老李风 IP 海报生成器 V2 · MiniMax image-01")
    print("=" * 60)

    api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not api_key:
        print("\n[FAIL] 需设置 MINIMAX_API_KEY")
        return 2
    print(f"\n[API Key] {api_key[:8]}...{api_key[-4:]}")

    ip = load_ip_profile()

    # V2 提示词
    prompt = build_prompt_v2(ip)
    print(f"\n[V2 提示词]")
    print(f"  长度: {len(prompt)} chars")
    print(f"  预览: {prompt[:300]}...")

    # 主调用 (image-01 基础版, 写实)
    print("\n[主调用] image-01 (基础写实版)")
    if call_minimax(api_key, prompt, IP_OUTPUT_V2, model="image-01"):
        print(f"\n[OK] V2 海报生成成功: {IP_OUTPUT_V2}")
        return 0

    # 退路 (image-01-live 增强版)
    print("\n[退路] image-01-live (增强版, 可能更艺术化)")
    return 0 if call_minimax(api_key, prompt, IP_OUTPUT_V2, model="image-01-live") else 1


if __name__ == "__main__":
    sys.exit(main())