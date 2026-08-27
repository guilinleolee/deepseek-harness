---
license: UNKNOWN
name: universal-converter
version: 1.0.0
description: |
  【万能格式转换助手 /uc】集成了 Pandoc, FFmpeg, ImageMagick, Stirling-PDF, Calibre 和 MeshLab 的全能转换引擎。支持 /convert (转换), /compress (压缩), /ocr (识字), /merge (合并), /3d (模型) 等指令。
author: 天龙引擎团队
created: 2026-02-26
category: automation

triggers:
  - "用户提到「universal-converter」时"
---

# Universal Converter 万能格式转换助手

## ⌨️ 快捷命令 (Quick Commands)

- `/uc`: (推荐) 启动“万能格式转换助手”主入口菜单。
- `/convert`: 快速启动格式转换流程 (DOCX, PDF, 音视频, 3D)。
- `/compress`: 优化文件体积，适用于视频、PDF 和图片。
- `/ocr`: 对 PDF 或图像执行文字识别，生成可搜索的 PDF。
- `/merge`: 合并多个 PDF 或图像文件。
- `/3d`: 执行 3D 模型格式转换、网格简化或降噪。

## 🛠 交互入口指引

当您输入 `/uc` 或输入 **万能格式转换助手** 时，Claude 将引导您通过 `AskUserQuestion` 选择以下功能：

1. **快速格式转换 (`/convert`)**: 处理文档、音视频及 3D 格式。
2. **文件体积压缩 (`/compress`)**: 针对大文件进行优化。
3. **文字识别 (`/ocr`)**: 扫描件转可搜索 PDF。
4. **合并多个文件 (`/merge`)**: PDF 合并或图片拼图。
5. **3D 模型处理 (`/3d`)**: 专项 3D 网格操作。

## Overview

本项目旨在通过整合六大顶级开源工具链，构建一个“一次性解决所有转换需求”的自动化引擎。

## 🛠 核心能力模块 (Core Capabilities)

### 1. 文档枢纽 (Pandoc)
- **触发场景**: MD/HTML/DOCX/PDF/LaTeX 互转。
- **最佳实践**: 始终指定 `--extract-media` 处理图片；使用 Lua 过滤器处理复杂格式转化。
- **优化建议**: 针对学术文档，配合 `citeproc` 处理参考文献。

### 2. 多媒体指挥官 (FFmpeg)
- **触发场景**: 视频转码、音频提取、动图制作、视频压缩。
- **最佳实践**: 优先使用 `-crf` (18-28) 控制质量而非固定比特率；使用 `drawtext` 过滤器添加动态水印。
- **优化建议**: 在支持的环境下开启 `h264_nvenc` 或 `h264_vaapi` 硬件加速。

### 3. 影像工厂 (ImageMagick)
- **触发场景**: 图像格式转换、批量缩放、色彩优化、PDF 转图。
- **最佳实践**: 使用 `magick` (v7+) 替代旧版 `convert`；处理大批量图片时使用 `mogrify`。
- **优化建议**: 针对 Web 场景，配合 `-quality` 和 `-strip` 移除元数据以减小体积。

### 4. PDF 手术刀 (Stirling-PDF)
- **触发场景**: PDF 合并、拆分、OCR、密文处理、压缩。
- **最佳实践**: 使用其 OCR 模块 (Tesseract) 时指定双语语言包（如 `chi_sim+eng`）。
- **优化建议**: 利用其“Sanitize”功能彻底清除文档中的敏感元数据。

### 5. 电纸书引擎 (Calibre)
- **触发场景**: EPUB/MOBI/AZW3 转换、元数据修复。
- **最佳实践**: 使用命令行工具 `ebook-convert` 进行 headless 自动化处理。
- **优化建议**: 在转换时启用 `--heuristic-analysis` 修复不规范的源文件排版。

### 6. 3D 模型顾问 (MeshLab)
- **触发场景**: STL/OBJ/PLY 转换、网格简化、降噪。
- **最佳实践**: 使用 `meshlabserver` 配合 MLX 脚本进行批处理。
- **优化建议**: 执行网格简化前，务必先进行 `Remove Duplicated Vertex` 操作。

## 🚀 任务执行流程 (Workflow)

1. **识别需求**: 确定源文件类型与目标需求。
2. **工具选择**: 根据 [toolchain_guide.md](references/toolchain_guide.md) 选择对应工具链。
3. **参数优化**: 应用上述“优化建议”构建防御性命令。
4. **验证交付**: 检查输出文件完整性及元数据合规性。

## 💡 进阶优化建议

- **原子化执行**: 复杂的跨类转换（如 3D 渲染转视频）应拆分为“3D -> Image Seq -> Video”步骤。
- **防御性处理**: 对所有外部工具调用强制设置 `timeout=30`，并捕获 `stderr` 进行重试。
- **并发控制**: 批量图片或视频处理建议使用任务队列或并发工具（如 `GNU Parallel`）以充分利用多核 CPU。

---
*更多详细命令参考：[toolchain_guide.md](references/toolchain_guide.md)*
