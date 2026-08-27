---
license: UNKNOWN
triggers: ["ai watermark skill", "AI Watermark SKILL"]
---
# AI Watermark SKILL

> AI水印去除与图像增强 —— 移除AI生成内容的水印、Logo、文字覆盖

## L0: 一句话描述 (≤15字)
AI水印文字覆盖自动去除

## L1: 使用场景 (50-100字)
当用户需要从图片/视频中去除AI水印、Logo、文字覆盖、文字遮挡，或需要对图像进行去噪、增强、修复时触发。适用于清理截图、文档处理、图像修复等场景。

## L2: 详细文档

### 核心技术

| 能力 | 模型/工具 | 说明 |
|------|-----------|------|
| 文本覆盖去除 | LaMa/GIMP Inpainting | 智能填充去除文字区域 |
| 水印去除 | U-2-Net/DeepWhitening | 专用水印检测与去除 |
| 图像修复 | GFPGAN/CodeFormer | 人脸与图像增强修复 |
| 背景移除 | RMBG-1.4/Remove.bg | 背景分离与替换 |
| 去模糊 | Real-ESRGAN/Defocus | 超分辨率与去模糊 |

### 方案一：Python + OpenCV + PIL 方案

**watermark_remover.py** - 本地处理:
```python
#!/usr/bin/env python3
"""AI水印去除工具 - OpenCV + PIL方案"""
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import sys
import os

def remove_text_overlay(image_path: str, output_path: str = None) -> str:
    """去除图片中的文字覆盖"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 边缘检测定位文字区域
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 过滤小区域(文字通常是小的连通区域)
    text_mask = np.zeros_like(gray)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 100 < area < 5000:  # 文字区域面积范围
            cv2.drawContours(text_mask, [cnt], -1, 255, -1)

    # 形态学处理平滑掩码
    kernel = np.ones((3, 3), np.uint8)
    text_mask = cv2.morphologyEx(text_mask, cv2.MORPH_CLOSE, kernel)
    text_mask = cv2.dilate(text_mask, kernel, iterations=1)

    # 修复(Inpaint)
    result = cv2.inpaint(img, text_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    if output_path is None:
        name, ext = os.path.splitext(image_path)
        output_path = f"{name}_cleaned{ext}"

    cv2.imwrite(output_path, result)
    return output_path

def remove_logo(image_path: str, output_path: str = None) -> str:
    """去除图片角落的Logo/水印"""
    img = cv2.imread(image_path)
    h, w = img.shape[:2]

    # 常见的Logo位置掩码(角落区域)
    margin = int(min(h, w) * 0.08)
    mask = np.ones((h, w), dtype=np.uint8) * 255

    # 四个角落
    corners = [
        (0, 0, margin, margin),           # 左上
        (w-margin, 0, w, margin),        # 右上
        (0, h-margin, margin, h),         # 左下
        (w-margin, h-margin, w, h),       # 右下
        (0, h-30, w, h),                 # 底部
    ]

    for x1, y1, x2, y2 in corners:
        mask[y1:y2, x1:x2] = 0

    result = cv2.inpaint(img, mask, inpaintRadius=7, flags=cv2.INPAINT_TELEA)

    if output_path is None:
        name, ext = os.path.splitext(image_path)
        output_path = f"{name}_delogo{ext}"

    cv2.imwrite(output_path, result)
    return output_path

def enhance_image(image_path: str, output_path: str = None,
                  sharpen: float = 1.5, contrast: float = 1.2,
                  brightness: float = 1.0) -> str:
    """图像增强处理"""
    img = Image.open(image_path)

    if sharpen > 1.0:
        img = img.filter(ImageFilter.SHARPEN)
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)

    if output_path is None:
        name, ext = os.path.splitext(image_path)
        output_path = f"{name}_enhanced.jpg"

    img.save(output_path, quality=95)
    return output_path

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "text"
    src = sys.argv[2] if len(sys.argv) > 2 else ""
    out = sys.argv[3] if len(sys.argv) > 3 else None

    if not src or not os.path.exists(src):
        print("用法: watermark_remover.py [text|logo|enhance] <源文件> [输出文件]")
        sys.exit(1)

    if cmd == "text":
        result = remove_text_overlay(src, out)
    elif cmd == "logo":
        result = remove_logo(src, out)
    elif cmd == "enhance":
        result = enhance_image(src, out)
    else:
        print("未知命令:", cmd)
        sys.exit(1)

    print(f"处理完成: {result}")
```

### 方案二：API方案（第三方服务）

**api_watermark.py** - 云端API调用:
```python
#!/usr/bin/env python3
"""AI水印去除工具 - API方案"""
import requests
import base64
import json
import sys
import os

def call_lama_api(image_path: str, mask_path: str = None) -> bytes:
    """调用LaMa Inpainting API"""
    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()

    payload = {"image": img_data, "mask": None}
    # 实际使用时替换为真实API端点
    resp = requests.post("https://api.example.com/inpaint", json=payload, timeout=60)
    return resp.content

def call_rmbg_api(image_path: str) -> bytes:
    """调用Remove.bg API去除背景/水印"""
    with open(image_path, "rb") as f:
        files = {"image_file": f}
        # 实际使用时替换为真实API Key
        resp = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files=files,
            headers={"X-Api-Key": os.getenv("RM_BG_API_KEY", "")},
            timeout=30
        )
    return resp.content

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "lama"
    src = sys.argv[2] if len(sys.argv) > 2 else ""

    if not src or not os.path.exists(src):
        print("用法: api_watermark.py [lama|rmbg] <源文件>")
        sys.exit(1)

    if cmd == "lama":
        result = call_lama_api(src)
    elif cmd == "rmbg":
        result = call_rmbg_api(src)
    else:
        print("未知命令:", cmd)
        sys.exit(1)

    name, ext = os.path.splitext(src)
    out_path = f"{name}_api_result.png"
    with open(out_path, "wb") as f:
        f.write(result)
    print(f"API处理完成: {out_path}")
```

### 方案三：GIMP脚本（无命令行基础）

**gimp_watermark.scm** - GIMP批处理脚本:
```scheme
(define (remove-watermark filename outname)
  (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE filename filename)))
         (drawable (car (gfile-get-active-drawable image)))
         (selection (car (gimp-image-get-selection image))))
    ; 选择文字区域(需手动标记)
    (plug-in-inpaint RUN-NONINTERACTIVE image drawable selection 5)
    (gimp-file-save RUN-NONINTERACTIVE image drawable outname outname)
    (gimp-image-delete image)))

; 批量处理
(define (batch-remove directory)
  (let* ((filelist (cadr (file-glob (string-append directory "/*.png") 100))))
    (while (not (null? filelist))
      (let ((filename (car filelist)))
        (remove-watermark filename (string-append filename "_clean.png"))
        (set! filelist (cdr filelist))))))
```

### 天龙引擎集成

| 天龙岗位 | 集成方式 |
|----------|-----------|
| 07记录师 | 清理截图水印，归档纯净图像 |
| 01调研师 | 去除研究素材的水印保护 |
| 03构建师 | 自动化测试图像处理流程 |
| 35-02社媒运营 | 社媒图片去水印处理 |
| 28-01文案策划 | 配图净化处理 |

### 使用命令

```bash
# 文字覆盖去除
python3 ~/.claude/skills/ai-watermark-skill/scripts/watermark_remover.py text input.png output.png

# Logo/水印去除
python3 ~/.claude/skills/ai-watermark-skill/scripts/watermark_remover.py logo input.png output.png

# 图像增强
python3 ~/.claude/skills/ai-watermark-skill/scripts/watermark_remover.py enhance input.png output.png

# API方案(需配置API Key)
export RM_BG_API_KEY="your-api-key"
python3 ~/.claude/skills/ai-watermark-skill/scripts/api_watermark.py rmbg input.png
```

### 适用场景

| 场景 | 推荐方案 | 效果 |
|------|---------|------|
| 简单文字去除 | OpenCV | 快速、本地、免费 |
| 复杂水印 | LaMa API | 高质量、需API |
| 背景去除 | Remove.bg | 专用、需API |
| 批量处理 | GIMP脚本 | 批量、自动化 |

### 限制与注意事项

1. **版权合规**: 去除水印仅用于个人学习研究，尊重版权
2. **效果限制**: 复杂背景的水印去除效果有限，可能需要人工修图
3. **API费用**: 第三方API可能产生费用
4. **图像损伤**: 修复过程可能造成图像质量损失

## 文件结构

```
ai-watermark-skill/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── watermark_remover.py    # OpenCV本地处理
│   └── api_watermark.py       # API调用方案
└── README.md                   # 使用说明
```

## 版本信息

- **版本**: 1.0.0
- **更新日期**: 2026-05-07
- **来源**: ChromeAppHeroes #132 NanoBanana Watermark Remover + 独立开发
- **_stars**: N/A