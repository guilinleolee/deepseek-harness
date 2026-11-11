---
name: render-deck
description: >
  Render an HTML page deck into publication-ready PNG images at several platform
  ratios (Xiaohongshu 3:4, WeChat 21:9 + 1:1, square, 9:16). Use when the user asks
  to 出图, 把方案渲染成图, 生成小红书图文, 生成公众号封面, or wants a visual plan
  turned into finished images. Pairs with xhs-visual-director for the planning step.
version: 1.0.0
license: MIT
commercial_use: yes
triggers: ["render deck", "出图", "渲染成图", "图文卡片", "公众号封面"]
---

# render-deck · HTML → PNG 图文渲染器

把一份 HTML 页面方案渲染成可直接发布的 PNG。一次输入，多比例输出。

## 为什么用这个而不是别人的渲染 skill

- **零 AGPL**：MIT 自研，不进客户内网技能库没有合规负担。
- **零 npm 依赖**：用系统 headless Chrome 截图，不装 Playwright。
- **一次多比例**：同一份 HTML 出 3:4 / 21:9 / 1:1 / 1:1 方形 / 9:16。

## 用法

```bash
python render-deck.py --input deck.html --out ./out --sizes all
python render-deck.py --input deck.html --out ./out --sizes xhs
python render-deck.py --input deck.html --out ./out --sizes 1080x1440,900x900
```

| 参数 | 说明 |
|---|---|
| `--input` | 源 HTML 文件（必填） |
| `--out` | 输出目录（必填） |
| `--sizes` | 预设名或 `宽x高` 列表（默认 `xhs`） |
| `--name` | 输出文件名词干，默认取输入文件名 |
| `--chrome` | 指定 Chrome/Chromium 可执行文件 |

### 尺寸预设

| 预设 | 尺寸 | 用途 |
|---|---|---|
| `xhs` | 1080×1440 | 小红书 3:4 |
| `square` | 1080×1080 | 方形封面 |
| `story` | 1080×1920 | 视频号 / 抖音 9:16 |
| `wechat` | 900×383 + 900×900 | 公众号 21:9 主封面 + 1:1 副封面 |
| `all` | 上述全部 | 一次出全套 |

## 退出码

| 码 | 含义 |
|---|---|
| 0 | 全部渲染成功 |
| 2 | 输入文件缺失或尺寸参数非法 |
| 4 | 找不到 Chrome/Chromium |

## 环境要求

- 系统 Chrome 或 Chromium。查找顺序：`--chrome` 参数 → `CHROME_PATH` 环境变量 → 常见安装路径 → `PATH` 中的 `google-chrome` / `chromium`。
- 无需 Node.js、Playwright、Puppeteer。

## 配合用法

标准链路是三段：

1. **策划** — `xhs-visual-director` 产出页面结构、风格与出图提示词。
2. **渲染** — 本 skill 把方案写成 HTML 并渲染成 PNG。
3. **素材** — `baoyu-*` 系列处理图库素材、截图、长文转图。

## 已知限制

- HTML 必须自带固定尺寸；同一份 HTML 在极端比例下可能截断（21:9 尤其明显）。多比例交付时，为每个比例单独调版式或用自适应 CSS。
- 只渲染静态页面，不执行交互脚本后的状态。
- Live Photo 动图拼图不在本 skill 范围内，需要 ffmpeg 单独合成。

## 授权

MIT，随仓库分发。
