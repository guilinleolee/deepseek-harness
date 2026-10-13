# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

# Setup path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import generator
from generator_v2 import generate_cover, JINGJIE_COLORS, BRAND_NAME

# Output directory
OUTPUT_DIR = script_dir / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def main():
    print("=" * 50)
    print("lib-bingling-v2 Test")
    print("=" * 50)
    print("\nOutput:", OUTPUT_DIR)
    print("Brand:", BRAND_NAME)

    samples = [
        {"title": "客户嫌贵又觉得不值？", "subtitle": "用价值方程把不敢开价变成客户抢着付", "jingjie": "zhuji", "platform": "gongzhonghao", "filename": "01-公众号-筑基蓝.png"},
        {"title": "心不老，身不灭", "jingjie": "wudao", "platform": "pengyouquan", "filename": "02-朋友圈-悟道紫.png"},
        {"title": "副业从0到1", "subtitle": "7天落地完整指南", "jingjie": None, "palette": "moyu", "platform": "xiaohongshu", "layout": "center-float", "filename": "03-小红书-摸鱼绿.png"},
        {"title": "吾未老，尚能战！", "subtitle": "用以致学，让你知行合一", "jingjie": None, "palette": "lianpo", "platform": "gongzhonghao", "layout": "dual-title", "filename": "04-公众号-廉颇金.png"},
        {"title": "AI时代副业新机遇", "subtitle": "普通人如何抓住这波红利", "jingjie": None, "palette": "shangwu", "platform": "gongzhonghao", "filename": "05-公众号-商务蓝.png"},
        {"title": "会做的不如会卖的", "jingjie": "jiedan", "platform": "pengyouquan", "filename": "06-朋友圈-结丹金.png"},
        {"title": "认知破局", "subtitle": "提升认知是副业第一步", "jingjie": "lianqi", "platform": "xiaohongshu", "filename": "07-小红书-炼气橙.png"},
        {"title": "养生有道", "subtitle": "身体是革命的本钱", "jingjie": "changsheng", "platform": "pengyouquan", "filename": "08-朋友圈-长生银.png"},
    ]

    print("\nGenerating", len(samples), "images...\n")

    for i, sample in enumerate(samples, 1):
        print("[{}/{}] {}".format(i, len(samples), sample["filename"]))
        output = OUTPUT_DIR / sample["filename"]

        try:
            kwargs = {"output": str(output)}
            if sample.get("jingjie"):
                kwargs["jingjie"] = sample["jingjie"]
            else:
                kwargs["palette"] = sample.get("palette", "zhuji")
            kwargs["title"] = sample["title"]
            kwargs["subtitle"] = sample.get("subtitle", "")
            kwargs["platform"] = sample["platform"]
            kwargs["layout"] = sample.get("layout", "full-title")

            generate_cover(**kwargs)
            print("    [OK]", output)
        except Exception as e:
            print("    [FAIL]", str(e))

    print("\n" + "=" * 50)
    print("Test Complete!")
    print("=" * 50)
    print("\nAll images saved to:", OUTPUT_DIR)
    print("\nPress Enter to exit...")
    input()


if __name__ == "__main__":
    main()
