# -*- coding: utf-8 -*-
"""
lib-bingling-v2 测试脚本
双击此文件生成多套测试封面图
依赖：pip install Pillow
"""
import os
import sys
from pathlib import Path

# 添加技能路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from generator_v2 import (
    generate_cover,
    generate_quote_card,
    generate_jingjie_card,
    JINGJIE_COLORS,
    SPECIAL_PALETTES,
    PLATFORM_SIZES,
    LAYOUTS,
    BRAND_NAME,
)

# 输出目录
OUTPUT_DIR = script_dir / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def main():
    print("=" * 50)
    print("lib-bingling-v2 测试脚本")
    print("=" * 50)
    print(f"\n输出目录: {OUTPUT_DIR}")
    print(f"品牌: {BRAND_NAME}")

    # 生成示例封面图
    samples = [
        {
            "title": "客户嫌贵又觉得不值？",
            "subtitle": "用价值方程把不敢开价变成客户抢着付",
            "jingjie": "zhuji",
            "platform": "gongzhonghao",
            "layout": "full-title",
            "filename": "01-筑基蓝-公众号封面.png"
        },
        {
            "title": "心不老，身不灭",
            "jingjie": "wudao",
            "platform": "pengyouquan",
            "filename": "02-悟道紫-朋友圈金句.png"
        },
        {
            "title": "副业从0到1",
            "subtitle": "7天落地完整指南",
            "jingjie": None,
            "palette": "moyu",
            "platform": "xiaohongshu",
            "layout": "center-float",
            "filename": "03-摸鱼绿-小红书.png"
        },
        {
            "title": "吾未老，尚能战！",
            "subtitle": "用以致学，让你知行合一",
            "jingjie": None,
            "palette": "lianpo",
            "platform": "gongzhonghao",
            "layout": "dual-title",
            "filename": "04-廉颇金-公众号.png"
        },
        {
            "title": "AI时代副业新机遇",
            "subtitle": "普通人如何抓住这波红利",
            "jingjie": None,
            "palette": "shangwu",
            "platform": "gongzhonghao",
            "layout": "full-title",
            "filename": "05-商务蓝-公众号.png"
        },
        {
            "title": "会做的不如会卖的",
            "jingjie": "jiedan",
            "platform": "pengyouquan",
            "filename": "06-结丹金-朋友圈.png"
        },
        {
            "title": "认知破局",
            "subtitle": "提升认知是副业第一步",
            "jingjie": "lianqi",
            "platform": "xiaohongshu",
            "layout": "full-title",
            "filename": "07-炼气橙-小红书.png"
        },
        {
            "title": "养生有道",
            "subtitle": "身体是革命的本钱",
            "jingjie": "changsheng",
            "platform": "pengyouquan",
            "filename": "08-长生银-朋友圈.png"
        },
    ]

    print(f"\n开始生成 {len(samples)} 张示例封面图...\n")

    for i, sample in enumerate(samples, 1):
        print(f"[{i}/{len(samples)}] 生成: {sample['filename']}")
        output = OUTPUT_DIR / sample["filename"]

        try:
            if sample.get("jingjie"):
                generate_cover(
                    title=sample["title"],
                    subtitle=sample.get("subtitle", ""),
                    jingjie=sample["jingjie"],
                    platform=sample["platform"],
                    layout=sample.get("layout", "full-title"),
                    output=str(output)
                )
            elif sample.get("palette"):
                generate_cover(
                    title=sample["title"],
                    subtitle=sample.get("subtitle", ""),
                    palette=sample["palette"],
                    platform=sample["platform"],
                    layout=sample.get("layout", "full-title"),
                    output=str(output)
                )
            print(f"    成功: {output}")
        except Exception as e:
            print(f"    失败: {e}")

    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)
    print(f"\n所有图片已保存到: {OUTPUT_DIR}")
    print("\n按回车键退出...")
    input()


if __name__ == "__main__":
    main()
