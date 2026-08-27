# -*- coding: utf-8 -*-
"""
lib-bingling-v2 测试脚本
双击此文件生成多套测试封面图
"""
import os
import sys
from pathlib import Path

# 添加技能路径
sys.path.insert(0, str(Path(__file__).parent))

from generator_v2 import (
    generate_cover,
    generate_quote_card,
    generate_jingjie_card,
    generate_lianpo_thumbnail,
    JINGJIE_COLORS,
    SPECIAL_PALETTES,
    PLATFORM_SIZES,
    LAYOUTS,
    BRAND_NAME,
)

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def test_all_platforms():
    """测试所有平台"""
    print("\n" + "="*50)
    print("🧪 测试所有平台尺寸")
    print("="*50)

    title = "客户嫌贵又觉得不值？"
    subtitle = "用价值方程让客户抢着付"

    for platform, info in PLATFORM_SIZES.items():
        print(f"\n📐 测试 {platform} ({info['ratio']})...")
        output = OUTPUT_DIR / f"test-{platform}.png"
        try:
            generate_cover(
                title=title,
                subtitle=subtitle,
                jingjie="zhuji",
                platform=platform,
                layout="full-title",
                output=str(output)
            )
            print(f"   ✅ 已生成: {output}")
        except Exception as e:
            print(f"   ❌ 失败: {e}")

def test_all_palettes():
    """测试所有配色"""
    print("\n" + "="*50)
    print("🎨 测试所有配色方案")
    print("="*50)

    title = "副业从0到1"
    subtitle = "7天落地指南"

    # 七境配色
    print("\n【七境配色】")
    for jingjie, info in JINGJIE_COLORS.items():
        print(f"\n🌟 测试 {info['cn']}...")
        output = OUTPUT_DIR / f"test-{jingjie}.png"
        try:
            generate_cover(
                title=title,
                subtitle=subtitle,
                jingjie=jingjie,
                platform="gongzhonghao",
                layout="full-title",
                output=str(output)
            )
            print(f"   ✅ {info['main']}")
        except Exception as e:
            print(f"   ❌ 失败: {e}")

    # 特殊配色
    print("\n【特殊配色】")
    for palette, info in SPECIAL_PALETTES.items():
        print(f"\n⭐ 测试 {info['cn']}...")
        output = OUTPUT_DIR / f"test-{palette}.png"
        try:
            generate_cover(
                title=title,
                subtitle=subtitle,
                jingjie=None,
                palette=palette,
                platform="gongzhonghao",
                layout="full-title",
                output=str(output)
            )
            print(f"   ✅ {info['main']}")
        except Exception as e:
            print(f"   ❌ 失败: {e}")

def test_all_layouts():
    """测试所有版式"""
    print("\n" + "="*50)
    print("📐 测试所有版式骨架")
    print("="*50)

    title = "副业从0到1的7个步骤"
    subtitle = "老李亲测有效"

    for layout, info in LAYOUTS.items():
        print(f"\n📐 测试 {info['name']}...")
        output = OUTPUT_DIR / f"test-layout-{layout}.png"
        try:
            generate_cover(
                title=title,
                subtitle=subtitle,
                jingjie="zhuji",
                platform="gongzhonghao",
                layout=layout,
                output=str(output)
            )
            print(f"   ✅ {info['desc']}")
        except Exception as e:
            print(f"   ❌ 失败: {e}")

def generate_samples():
    """生成示例封面图"""
    print("\n" + "="*50)
    print("📸 生成示例封面图")
    print("="*50)

    samples = [
        # 筑基蓝 - 公众号封面
        {
            "title": "客户嫌贵又觉得不值？",
            "subtitle": "用价值方程把不敢开价变成客户抢着付",
            "jingjie": "zhuji",
            "platform": "gongzhonghao",
            "layout": "full-title",
            "filename": "01-筑基蓝-公众号封面.png"
        },
        # 悟道紫 - 朋友圈金句
        {
            "title": "心不老，身不灭",
            "jingjie": "wudao",
            "platform": "pengyouquan",
            "filename": "02-悟道紫-朋友圈金句.png"
        },
        # 摸鱼绿 - 小红书
        {
            "title": "副业从0到1",
            "subtitle": "7天落地完整指南",
            "jingjie": None,
            "palette": "moyu",
            "platform": "xiaohongshu",
            "layout": "center-float",
            "filename": "03-摸鱼绿-小红书.png"
        },
        # 廉颇金 - 公众号
        {
            "title": "吾未老，尚能战！",
            "subtitle": "用以致学，让你知行合一",
            "jingjie": None,
            "palette": "lianpo",
            "platform": "gongzhonghao",
            "layout": "dual-title",
            "filename": "04-廉颇金-公众号.png"
        },
        # 商务蓝 - 公众号
        {
            "title": "AI时代副业新机遇",
            "subtitle": "普通人如何抓住这波红利",
            "jingjie": None,
            "palette": "shangwu",
            "platform": "gongzhonghao",
            "layout": "full-title",
            "filename": "05-商务蓝-公众号.png"
        },
        # 结丹金 - 朋友圈
        {
            "title": "会做的不如会卖的",
            "jingjie": "jiedan",
            "platform": "pengyouquan",
            "filename": "06-结丹金-朋友圈.png"
        },
    ]

    for i, sample in enumerate(samples, 1):
        print(f"\n📸 生成示例 {i}: {sample['filename']}")
        output = OUTPUT_DIR / sample["filename"]

        try:
            if "jingjie" in sample and sample["jingjie"]:
                generate_cover(
                    title=sample["title"],
                    subtitle=sample.get("subtitle", ""),
                    jingjie=sample["jingjie"],
                    platform=sample["platform"],
                    layout=sample.get("layout", "full-title"),
                    output=str(output)
                )
            elif "palette" in sample and sample["palette"]:
                generate_cover(
                    title=sample["title"],
                    subtitle=sample.get("subtitle", ""),
                    palette=sample["palette"],
                    platform=sample["platform"],
                    layout=sample.get("layout", "full-title"),
                    output=str(output)
                )
            print(f"   ✅ 已生成: {output}")
        except Exception as e:
            print(f"   ❌ 失败: {e}")

def main():
    print("="*50)
    print("🚀 lib-bingling-v2 测试脚本")
    print("="*50)
    print(f"\n📁 输出目录: {OUTPUT_DIR}")
    print(f"👤 品牌: {BRAND_NAME}")

    # 列出支持的配置
    print("\n" + "-"*50)
    print("📐 支持的平台:", len(PLATFORM_SIZES))
    for k in PLATFORM_SIZES:
        print(f"   - {k}")

    print("\n🎨 支持的配色:", len(JINGJIE_COLORS) + len(SPECIAL_PALETTES))
    print("   七境:", list(JINGJIE_COLORS.keys()))
    print("   特殊:", list(SPECIAL_PALETTES.keys()))

    print("\n📐 支持的版式:", len(LAYOUTS))
    for k in LAYOUTS:
        print(f"   - {k}")

    # 生成示例
    print("\n" + "="*50)
    print("🚀 开始生成示例封面图...")
    print("="*50)

    generate_samples()

    print("\n" + "="*50)
    print("✅ 测试完成！")
    print("="*50)
    print(f"\n📁 所有图片已保存到: {OUTPUT_DIR}")
    print("\n按回车键退出...")
    input()

if __name__ == "__main__":
    main()
