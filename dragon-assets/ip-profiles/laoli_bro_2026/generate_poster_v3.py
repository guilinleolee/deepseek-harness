"""
老李风 IP 卡通讲解图生成器 V3
==============================

V3 思路转变:
- V1/V2: 人物肖像 (失败: 偏老外/像农民)
- V3: 卡通讲解图 (illustrated explanation scene)
  - 主体: 一张书桌, 桌上有笔记本电脑/手机/纸张
  - 角色: 中年大叔卡通形象 (大头, 简化线条)
  - 元素: 多个 AI 工具图标气泡 (悬浮的对话框)
  - 装饰: 价格标签 (9.9 / 199 / 998), 装订效果, 周历标签
  - 顶部留 30% 放标题

风格:
- 现代扁平卡通 (modern flat cartoon illustration)
- 中国当代都市风 (不是古代, 不是国外)
- 颜色饱和度中等, 老李风 6 色板
- 干净线条, 留白充足
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

IP_PROFILE_DIR = Path("C:/Users/li/.claude/ip-profiles/laoli_bro_2026")
IP_PROFILE_JSON = IP_PROFILE_DIR / "ip_profile_8dim.json"
IP_OUTPUT_V3 = IP_PROFILE_DIR / "poster_test_3.png"

MINIMAX_API_URL = "https://api.minimaxi.com/v1/image_generation"
MINIMAX_MODEL = "image-01-live"  # 卡通用 live 更艺术化
ASPECT_RATIO = "9:16"


def build_prompt_v3() -> str:
    """V3 卡通讲解图提示词"""

    # 关键约束: 现代扁平卡通 + AI 写作测试 2 周场景
    prompt = """Modern flat cartoon illustration, vertical 9:16 poster. Scene: middle-aged
Chinese cartoon man sitting at simple desk with laptop showing multiple AI chat windows.
Above laptop floating cartoon speech bubbles with simplified AI tool icons (chatbot
avatars). Man wearing plain black polo shirt, simple round head friendly expression.
Color palette: deep slate gray background, warm orange highlights on bubbles, cream
skin, pure black hair shirt, fog gray desk, 6 flat colors no gradients. Top 30 percent
empty for text overlay, character middle, desk lower. Scene includes small price tags
9.9 yuan 199 yuan 998 yuan near tools, small calendar icon showing 14 days for 2 weeks.
Style: clean flat modern cartoon similar to Chinese new media explainer comics, simplified
geometric shapes, friendly approachable, no realistic rendering no oil painting no 3D no
anime. Subtle warm side glow lighting. Avoid photorealistic style, portrait photo, oil
painting, 3D render, anime manga, complex facial features wrinkles realistic skin, mockup
text in image."""

    return prompt


def call_minimax(api_key: str, prompt: str, output_path: Path, model: str = "image-01-live") -> bool:
    payload = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": ASPECT_RATIO,
        "n": 1,
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

    status_code = result.get("base_resp", {}).get("status_code", -1)
    if status_code != 0:
        print(f"  [FAIL] status_code={status_code}")
        print(f"  Body: {json.dumps(result, ensure_ascii=False)[:500]}")
        return False

    image_urls = result.get("data", {}).get("image_urls", [])
    if not image_urls:
        return False

    try:
        with urllib.request.urlopen(image_urls[0], timeout=60) as img_resp:
            output_path.write_bytes(img_resp.read())
        print(f"  [OK] 已保存: {output_path} ({output_path.stat().st_size:,} bytes)")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def main() -> int:
    print("=" * 60)
    print("老李风卡通讲解图生成器 V3")
    print("=" * 60)

    api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not api_key:
        print("[FAIL] 需 MINIMAX_API_KEY")
        return 2

    prompt = build_prompt_v3()
    print(f"\n[V3 提示词] {len(prompt)} chars")

    # 卡通用 image-01-live 增强版
    print("\n[主调用] image-01-live")
    if call_minimax(api_key, prompt, IP_OUTPUT_V3, model="image-01-live"):
        return 0

    # 退路
    print("\n[退路] image-01")
    return 0 if call_minimax(api_key, prompt, IP_OUTPUT_V3, model="image-01") else 1


if __name__ == "__main__":
    sys.exit(main())