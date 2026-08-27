# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BRAND_NAME = "李秉凌·用以致学"
BRAND_TAGLINE = "用比学更重要"

PLATFORM_SIZES = {
    "gongzhonghao": {"width": 1920, "height": 1080, "ratio": "16:9", "desc": "公众号头图"},
    "gongzhonghao-wide": {"width": 2100, "height": 900, "ratio": "21:9", "desc": "公众号封面"},
    "gongzhonghao-square": {"width": 1080, "height": 1080, "ratio": "1:1", "desc": "公众号分享卡"},
    "xiaohongshu": {"width": 1080, "height": 1440, "ratio": "3:4", "desc": "小红书图文"},
    "xiaohongshu-square": {"width": 1080, "height": 1080, "ratio": "1:1", "desc": "小红书卡片"},
    "pengyouquan": {"width": 1080, "height": 1080, "ratio": "1:1", "desc": "朋友圈分享"},
    "shipin": {"width": 1920, "height": 1080, "ratio": "16:9", "desc": "视频封面"},
}

JINGJIE_COLORS = {
    "lianqi": {"main": "#FF6B35", "accent": "#FFD700", "bg": "#1A1A1A", "cn": "炼气·提升认知"},
    "liandan": {"main": "#FF8C00", "accent": "#FF4500", "bg": "#1A1A1A", "cn": "炼丹·AI百宝箱"},
    "zhuji": {"main": "#2D5BFF", "accent": "#00C49A", "bg": "#1A1A1A", "cn": "筑基·副业创业"},
    "jiedan": {"main": "#C9A961", "accent": "#FFD700", "bg": "#1A1A1A", "cn": "结丹·财商情商"},
    "pojing": {"main": "#00C49A", "accent": "#FFD700", "bg": "#1A1A1A", "cn": "破境·养育儿女"},
    "wudao": {"main": "#6B46C1", "accent": "#FFD700", "bg": "#1A1A1A", "cn": "悟道·内圣外王"},
    "changsheng": {"main": "#E8E8E8", "accent": "#00C49A", "bg": "#1A1A1A", "cn": "长生·养生有道"},
}

SPECIAL_PALETTES = {
    "moyu": {"main": "#7CB342", "accent": "#AED581", "bg": "#1A1A1A", "cn": "摸鱼绿"},
    "lianpo": {"main": "#FFD700", "accent": "#FF6B35", "bg": "#1A1A1A", "cn": "廉颇金"},
    "shenye": {"main": "#0e0d0c", "accent": "#d4a04a", "bg": "#0e0d0c", "cn": "深夜墨"},
    "shangwu": {"main": "#002FA7", "accent": "#FFD500", "bg": "#1A1A2e", "cn": "商务蓝"},
    "jianyue": {"main": "#FFFFFF", "accent": "#2D5BFF", "bg": "#FFFFFF", "cn": "简约白"},
}

ALL_PALETTES = {**JINGJIE_COLORS, **SPECIAL_PALETTES}

LAYOUTS = {
    "full-title": {"name": "全幅大字", "title_scale": 0.09, "subtitle_scale": 0.038},
    "center-float": {"name": "居中悬浮", "title_scale": 0.07, "subtitle_scale": 0.032},
    "dual-title": {"name": "双标题对比", "title_scale": 0.065, "subtitle_scale": 0.045},
    "kpi-card": {"name": "KPI数据卡片", "title_scale": 0.06, "subtitle_scale": 0.04},
}


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_font(size, bold=True):
    font_paths = [
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    if not bold:
        font_paths = ["C:/Windows/Fonts/msyh.ttc"] + font_paths
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    lines = []
    current = ""
    for char in text:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines


def generate_cover(title, subtitle="", jingjie="zhuji", palette=None, platform="gongzhonghao", layout="full-title", color_scheme="dark", brand_mark=True, output="./cover.png"):
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)

    if palette and palette in ALL_PALETTES:
        pal = ALL_PALETTES[palette]
    elif jingjie and jingjie in JINGJIE_COLORS:
        pal = JINGJIE_COLORS[jingjie]
    else:
        pal = {"main": "#2D5BFF", "accent": "#00C49A", "bg": "#1A1A1A"}

    size_info = PLATFORM_SIZES.get(platform, {"width": 1920, "height": 1080})
    width = size_info["width"]
    height = size_info["height"]

    if color_scheme == "light":
        bg_rgb = hex_to_rgb(pal.get("bg", "#FFFFFF"))
    else:
        bg_rgb = hex_to_rgb(pal.get("bg", "#1A1A1A"))

    main_rgb = hex_to_rgb(pal.get("main", "#2D5BFF"))
    accent_rgb = hex_to_rgb(pal.get("accent", "#00C49A"))

    img = Image.new("RGB", (width, height), bg_rgb)
    draw = ImageDraw.Draw(img)

    # 上下装饰条
    draw.rectangle([(0, 0), (width, 8)], fill=main_rgb)
    draw.rectangle([(0, height - 8), (width, height)], fill=main_rgb)

    # 七境徽章
    if pal.get("cn"):
        badge_text = pal["cn"]
        badge_font = get_font(int(width * 0.033))
        bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        bw = bbox[2] - bbox[0]
        bh = bbox[3] - bbox[1]
        bx = (width - bw) // 2
        by = int(height * 0.08)
        pad = 20
        text_color = hex_to_rgb("#1A1A1A") if color_scheme == "dark" else hex_to_rgb("#FFFFFF")
        draw.rectangle([(bx - pad, by - 10), (bx + bw + pad, by + bh + 10)], fill=accent_rgb)
        draw.text((bx, by), badge_text, font=badge_font, fill=text_color)

    # 主标题
    max_title_w = int(width * 0.85)
    layout_config = LAYOUTS.get(layout, LAYOUTS["full-title"])
    title_font = get_font(int(width * layout_config["title_scale"]), bold=True)
    title_lines = wrap_text(title, title_font, max_title_w, draw)

    # 副标题
    sub_font = get_font(int(width * layout_config["subtitle_scale"]))
    sub_lines = wrap_text(subtitle, sub_font, max_title_w, draw) if subtitle else []

    # 计算位置
    line_h = int(width * layout_config["title_scale"] * 1.2)
    sub_line_h = int(width * layout_config["subtitle_scale"] * 1.4)
    gap = int(height * 0.04)
    total_h = len(title_lines) * line_h + gap + len(sub_lines) * sub_line_h
    start_y = (height - total_h) // 2 - int(height * 0.02)

    text_color = hex_to_rgb("#FFFFFF") if color_scheme == "dark" else hex_to_rgb("#1A1A1A")
    sub_color = hex_to_rgb(pal.get("sub", "#94a3b8")) if color_scheme == "dark" else hex_to_rgb("#6b7280")

    # 绘制标题
    for i, line in enumerate(title_lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        tx = (width - tw) // 2
        ty = start_y + i * line_h
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            draw.text((tx + dx, ty + dy), line, font=title_font, fill=(0, 0, 0))
        draw.text((tx, ty), line, font=title_font, fill=text_color)

    # 绘制副标题
    if subtitle:
        sub_start_y = start_y + len(title_lines) * line_h + gap
        for i, line in enumerate(sub_lines):
            bbox = draw.textbbox((0, 0), line, font=sub_font)
            sw = bbox[2] - bbox[0]
            sx = (width - sw) // 2
            sy = sub_start_y + i * sub_line_h
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                draw.text((sx + dx, sy + dy), line, font=sub_font, fill=(0, 0, 0))
            draw.text((sx, sy), line, font=sub_font, fill=sub_color)

    # 品牌标识
    if brand_mark:
        mark_font = get_font(int(width * 0.015), bold=False)
        bbox = draw.textbbox((0, 0), BRAND_NAME, font=mark_font)
        mw = bbox[2] - bbox[0]
        mh = bbox[3] - bbox[1]
        mx = (width - mw) // 2
        my = height - mh - int(height * 0.03)
        draw.rectangle([(mx - 15, my - 6), (mx + mw + 15, my + mh + 6)], fill=(0, 0, 0, 60))
        draw.text((mx, my), BRAND_NAME, font=mark_font, fill=(140, 140, 140))

    img.save(output, quality=95)
    return str(out)


def generate_quote_card(quote, author="李秉凌", jingjie="wudao", palette=None, platform="gongzhonghao", brand_mark=True, output="./quote.png"):
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)

    if palette and palette in ALL_PALETTES:
        pal = ALL_PALETTES[palette]
    elif jingjie and jingjie in JINGJIE_COLORS:
        pal = JINGJIE_COLORS[jingjie]
    else:
        pal = {"main": "#6B46C1", "accent": "#FFD700", "bg": "#1A1A1A"}

    size_info = PLATFORM_SIZES.get(platform, {"width": 1920, "height": 1080})
    width = size_info["width"]
    height = size_info["height"]

    bg_rgb = hex_to_rgb(pal.get("bg", "#1A1A1A"))
    main_rgb = hex_to_rgb(pal.get("main", "#6B46C1"))
    accent_rgb = hex_to_rgb(pal.get("accent", "#FFD700"))

    img = Image.new("RGB", (width, height), bg_rgb)
    draw = ImageDraw.Draw(img)

    # 侧边装饰条
    bar_w = 6
    draw.rectangle([(bar_w, 0), (bar_w * 2, height)], fill=main_rgb)
    draw.rectangle([(width - bar_w * 2, 0), (width - bar_w, height)], fill=main_rgb)

    # 引号
    is_landscape = width / height > 1.5
    quote_font_size = int(width * (0.06 if is_landscape else 0.08))
    quote_font = get_font(quote_font_size, bold=True)
    lq_x = int(width * 0.1)
    lq_y = int(height * (0.08 if is_landscape else 0.12))
    draw.text((lq_x, lq_y), "「", font=quote_font, fill=main_rgb)

    # 金句正文
    body_font_size = int(width * (0.045 if is_landscape else 0.06))
    body_font = get_font(body_font_size, bold=True)
    quote_clean = quote.replace("「", "").replace("」", "")
    lines = wrap_text(quote_clean, body_font, width * 0.75, draw)

    n_lines = len(lines)
    if n_lines <= 1:
        line_height = int(body_font_size * 1.6)
    elif n_lines == 2:
        line_height = int(body_font_size * 1.4)
    else:
        line_height = int(body_font_size * 1.35)

    start_y = int(height * (0.20 if is_landscape else 0.28))
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=body_font)
        lw = bbox[2] - bbox[0]
        lx = (width - lw) // 2
        ly = start_y + i * line_height
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            draw.text((lx + dx, ly + dy), line, font=body_font, fill=(0, 0, 0))
        draw.text((lx, ly), line, font=body_font, fill=(255, 255, 255))

    # 结束引号
    quote_block_end = start_y + (n_lines - 1) * line_height + body_font_size
    rq_y = quote_block_end - quote_font_size
    draw.text((width - lq_x - int(width * 0.2), rq_y), "」", font=quote_font, fill=main_rgb)

    # 作者
    author_font_size = int(width * 0.035)
    author_font = get_font(author_font_size)
    author_text = "-- " + author
    bbox = draw.textbbox((0, 0), author_text, font=author_font)
    aw = bbox[2] - bbox[0]
    ax = (width - aw) // 2
    ay = quote_block_end + int(height * 0.07)
    draw.text((ax, ay), author_text, font=author_font, fill=accent_rgb)

    if brand_mark:
        mark_font = get_font(int(width * 0.015), bold=False)
        bbox = draw.textbbox((0, 0), BRAND_NAME, font=mark_font)
        mw = bbox[2] - bbox[0]
        mh = bbox[3] - bbox[1]
        mx = (width - mw) // 2
        my = height - mh - int(height * 0.03)
        draw.rectangle([(mx - 15, my - 6), (mx + mw + 15, my + mh + 6)], fill=(0, 0, 0, 60))
        draw.text((mx, my), BRAND_NAME, font=mark_font, fill=(140, 140, 140))

    img.save(output, quality=95)
    return str(out)


if __name__ == "__main__":
    print("BRAND_NAME:", BRAND_NAME)
    print("Platforms:", list(PLATFORM_SIZES.keys()))
    print("Jingjie colors:", list(JINGJIE_COLORS.keys()))
    print("Special palettes:", list(SPECIAL_PALETTES.keys()))
    print("Layouts:", list(LAYOUTS.keys()))
