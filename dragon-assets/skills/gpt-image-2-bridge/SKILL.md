---
name: gpt-image-2-bridge
description: 把 gpt-image-2 工业模板库 + 案例库桥接到下游 4 个生成技能（Mond poster / Baoyu 公众号封面 / smart-illustrator 章节配图 / Seedance 短视频剧本）. Use when user asks "用 GPT-Image2 案例做海报", "案例 → 公众号封面", "gpt-image-2 → Mondo", "gpt-image-2 → Seedance", "GPT-Image2 案例配图".
version: 1.1.0
author: 天龙引擎集成
license: MIT
downstream: - qiaomu-mondo-poster-design
- baoyu-cover-image
- smart-illustrator
- seedance2-skill
- gpt-image-2-voxcpm-bridge  # V1.1: 图音一体扩展
upstream: - gpt-image-2-style-library V2.0
- gpt-image-2-gallery-explorer V1.0
- voxcpm-tts-integration V1.0  # V1.1: 音频上游
last_updated: 2026-06-26
triggers: ["gpt image 2 bridge", "gpt-image-2-bridge · 工业模板 × 案例库 → 下游 4 技能"]
---

# gpt-image-2-bridge · 工业模板 × 案例库 → 下游 4 技能

## L0: 一句话描述 (≤15字)

**gpt-image-2 案例 → Mondo/Baoyu/Smart/Seedance 桥接**

## L1: 使用场景 (50-100字)

**V1.0 新增能力**：把 gpt-image-2 工业模板 + 544 真实案例自动编排到 4 个下游生成技能：

1. **cover_mondo** — 选 Posters 类目案例 → Mondo 海报
2. **cover_baoyu** — 选 UI/Posters 案例 → Baoyu 公众号封面
3. **illustrations** — 按类目选 N 案例 → smart-illustrator 配图
4. **storyboard** — 选 Scenes 案例 → Seedance 短视频剧本

与 `book-distiller-bridge` 同构（共享 4 个下游），但输入是**结构化工业模板 + 真实案例**而非蒸馏产物。

## L2: 详细文档

### 核心定位

| 维度 | book-distiller-bridge | **gpt-image-2-bridge** |
|------|----------------------|------------------------|
| 上游 | github-to-skills 蒸馏产物 (SKILL.md + chapters) | gpt-image-2-style-library + gallery-explorer |
| 输入类型 | 书籍/教程文本 | 工业模板 JSON + 真实案例 |
| 视觉基准 | 蒸馏章节关键词 | 21 套工业模板 + 544 案例 |
| 类目路由 | 章节顺序 | 类目分类 (12 类目) |
| 输出 | 4 adapter | 4 adapter（**同名同构**）|

### 4 个 Adapter（与 book-distiller-bridge 同名同结构）

| Adapter | 下游 skill | 类目路由 | 输出格式 |
|---------|-----------|----------|----------|
| **cover_mondo** | qiaomu-mondo-poster-design | Posters & Typography / Brand & Logos | PNG 1:1 |
| **cover_baoyu** | baoyu-cover-image | UI / Posters (高对比中文友好) | PNG 900×383 (16:9) |
| **illustrations** | smart-illustrator | 全部 12 类目 (按需选 N) | PNG 16:9 (1920×1080) |
| **storyboard** | seedance2-skill | Scenes & Storytelling / Characters | Markdown + N 镜头 prompt |

### 与上游 2 个 skill 协同

```
gpt-image-2-style-library V2.0 (21 工业模板 JSON)
        ↓
        bridge.py 读取 templates.md → 提取 21 套模板定义
        ↓
gpt-image-2-gallery-explorer V1.0 (544 案例)
        ↓
        bridge.py 调 query.py → 按类目/关键词筛选案例
        ↓
        4 个 adapter → Mondo / Baoyu / Smart-illustrator / Seedance
```

### 快速使用

```bash
# 1. 按类目自动编排（推荐）
python ~/.claude/skills/gpt-image-2-bridge/scripts/bridge.py \
  --category "Posters & Typography" \
  --count 5 --dry-run

# 2. 按关键词 + 类目
python ~/.claude/skills/gpt-image-2-bridge/scripts/bridge.py \
  --keyword "futuristic dashboard" --category "UI & Interfaces" \
  --only cover_baoyu

# 3. 按案例 ID 单点编排
python ~/.claude/skills/gpt-image-2-bridge/scripts/bridge.py \
  --case 17 --case 45

# 4. 全自动（按类目统计 + 抽样）
python ~/.claude/skills/gpt-image-2-bridge/scripts/bridge.py \
  --auto-sample --per-category 2
```

### 类目 → Adapter 路由矩阵

| gpt-image-2 类目 | cover_mondo | cover_baoyu | illustrations | storyboard |
|------------------|-------------|-------------|---------------|------------|
| UI & Interfaces | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| Charts & Infographics | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| **Posters & Typography** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Products & E-commerce | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| Brand & Logos | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| Architecture & Spaces | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐ |
| Photography & Realism | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Illustration & Art | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Characters & People | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Scenes & Storytelling** | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| History & Classical | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐ |
| Document & Publication | ⭐ | ⭐ | ⭐⭐ | ⭐ |

### CLI 选项

```bash
python bridge.py [options]

输入:
  --category TEXT          按类目筛选 (12 类目之一)
  --keyword TEXT           按关键词搜索 (prompt/title 包含)
  --case ID [ID ...]       按案例 ID 列表指定
  --auto-sample            自动按类目统计 + 抽样
  --per-category N         --auto-sample 时每类目抽 N 个

输出:
  --only [adapter]         只跑某 adapter (cover_mondo/cover_baoyu/illustrations/storyboard)
  --count N                illustrations 数量上限 (默认 6)
  --mondo-style STYLE      vintage/modern/minimal (默认 vintage)
  --seedance-duration SEC  短视频时长 15/30/60 (默认 30)
  --lang {auto,zh,en}      prompt 语言 (默认 auto)
  --dry-run                只生成 prompt 不调 API
  --output-dir DIR         输出目录 (默认 ./bridge_output/)
```

### 与 book-distiller-bridge 共享的 prompt 结构

为保证两个 bridge 可互换使用，4 个 adapter 输出的 prompt schema 与 book-distiller-bridge 完全一致：

```json
{
  "adapter": "cover_mondo",
  "downstream_skill": "qiaomu-mondo-poster-design",
  "prompt": "<完整 gpt-image-2 prompt>",
  "output_format": "PNG 1024x1024",
  "filename": "cover_mondo_case17.png",
  "source_case_id": "case-17",
  "source_category": "UI & Interfaces"
}
```

### 测试覆盖

`tests/test_bridge.py` 包含 8 个测试用例：
- 类目筛选（Posters / UI / Scenes）
- 关键词搜索
- 案例 ID 直接指定
- 4 个 adapter 输出 schema 验证
- 跨语言 prompt (zh/en)
- dry-run 模式
- 与 book-distiller-bridge 的 schema 对齐

### 风险点

1. **prompt 长度差异**：gpt-image-2 案例的 prompt 通常 200-500 字（比 book chapters 短），需调整 truncate 阈值
2. **图像直引**：gallery 案例含真实图片 URL，可直接附在 manifest 中供下游参考
3. **类目覆盖不全**：gallery V1.0 有 61 个 Unknown 案例，需用 title 兜底（已 V1.1 优化到 11.2%）

### 安装与依赖

```bash
# 依赖
pip install python-docx beautifulsoup4  # query.py 已自带
ls ~/.claude/skills/gpt-image-2-{style-library,gallery-explorer}

# 验证
python ~/.claude/skills/gpt-image-2-bridge/scripts/bridge.py \
  --category "Posters & Typography" --count 3 --dry-run
```

### 协同矩阵

| 上下游 | 关系 |
|--------|------|
| ↑ gpt-image-2-style-library V2.0 | 读取 21 套工业模板定义 |
| ↑ gpt-image-2-gallery-explorer V1.0 | 读取 544 真实案例 |
| ↔ book-distiller-bridge | 共享 4 个下游 skill（同名 adapter） |
| ↔ **gpt-image-2-voxcpm-bridge V1.0** ⭐NEW | **共享 4 视觉 adapter + +1 tts_voxcpm（5 adapter）** |
| ↓ qiaomu-mondo-poster-design | 海报生成 |
| ↓ baoyu-cover-image | 公众号封面 |
| ↓ smart-illustrator | 章节/案例配图 |
| ↓ seedance2-skill | 短视频剧本 |

### V1.1 扩展：5th Adapter 引用（2026-06-26）

V1.0 的 4 adapter（cover_mondo / cover_baoyu / illustrations / storyboard）已被新 skill **gpt-image-2-voxcpm-bridge V1.0** 扩展为 **5 adapter**，新增 `tts_voxcpm` 维度（VoxCPM2 配音）。

**分工矩阵**：

| 需求 | 推荐 skill |
|------|-----------|
| 仅视觉（海报/封面/配图/分镜）| **本 skill（gpt-image-2-bridge）** |
| 视觉 + 音频（图音一体）| **gpt-image-2-voxcpm-bridge V1.0** |
| 博主声克隆 + 视觉 | **gpt-image-2-voxcpm-bridge V1.0** + voxcpm-voice-distillery V1.0 |
| 多语种出海（39 语种）| **gpt-image-2-voxcpm-bridge V1.0** |
| 图音协同打分 ≥ 0.85 自动质检 | **gpt-image-2-voxcpm-bridge V1.0** |

**Adapter 同构性保证**：
- 4 视觉 adapter（cover_mondo / cover_baoyu / illustrations / storyboard）与新 bridge 100% 同名同结构
- 可与本 skill 无缝切换，prompt 格式不需修改
- 唯一新增的是 `tts_voxcpm` 第 5 个 adapter

**升级路径**：
```
# V1.0 调用（仅视觉）
python ~/.claude/skills/gpt-image-2-bridge/scripts/bridge.py \
  --category "Posters & Typography" --count 5 --dry-run

# V1.0 → gpt-image-2-voxcpm-bridge 升级（图音一体）
python ~/.claude/skills/gpt-image-2-voxcpm-bridge/scripts/bridge.py \
  --scenario "小红书图文爆款" \
  --script "..." --audio-mode tts --dry-run
```

### 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| **V1.0** | **2026-06-23** | **首版：4 adapter + 类目路由 + 案例库桥接** |
| **V1.1** | **2026-06-26** | **扩展：引用 gpt-image-2-voxcpm-bridge V1.0（5 adapter / 11 场景 / 图文音三模态）** |

### 版本信息

- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **License**: MIT
- **Last Updated**: 2026-06-23