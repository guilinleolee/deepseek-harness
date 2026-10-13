---
name: group-daily-newspaper
description: 群日报·人民日报式 A3 报纸（印刷可用），版数可变（2/4/6/8 版，一般偶数），A3 竖版，AI 分析聊天记录 + 图片Probe → layout-plan.json → HTML → chrome --print-to-pdf
license: MIT
compatibility: claude-code
metadata: author: Larkin0302
version: "2.1"
tags:
- newspaper
- layout
- image-probe
- print
- A3
triggers: ["group daily newspaper", "群日报 · 人民日报式 A3 报纸生成器"]
---

# 群日报 · 人民日报式 A3 报纸生成器

## L0: 一句话描述

AI 分析微信群聊天记录，生成可印刷的人民日报风格 A3 报纸 PDF。

## L1: 使用场景

当用户说"生成群日报"、"输出群报纸"、"把今天的群聊做成报纸"时触发。适合有图片素材的微信群日总结、活动回顾、人物专题等场景。

## L2: 详细文档

### 核心原则

#### 原则 1：真实内容优先

- 所有内容必须来自 `story.json` 或聊天记录截图
- 图说 / 引语 / 时间点 / 黑话 / 数据都必须有出处，**禁编造**
- 若 `story.json` 缺少某字段，在 plan 里用 `[待填充]` 占位，并在输出末尾标注
- AI 自己看到的图（Read 工具）= 内容判断；`image_probe.py` = 元数据测量（宽/高/KB），两者职责分离

#### 原则 2：版面高度硬约束

- **每版必须 1587px**（A3 竖版 @96dpi：`height: 1587px; overflow: hidden`）
- 打印时若 4 张尺寸不一致，装订 / 折页会乱套
- 高度差容忍阈值：≤ 5px，> 10px 必须修复

#### 原则 3：每版零空白

- 没有 > 50px 连续空白带
- 用 `timeline_strip` / `quote_wall` / `tomorrow.items` 等横通栏专栏填补空白
- 不靠 `padding` 撑空白，靠真实内容填

#### 原则 4：4 版独立 Layout

| 版 | 模板 | 图位 | 特色 |
|----|------|------|------|
| 1 | masthead + hero-with-aside | aside.figure（顶部单图） | 头版要闻、边讯briefings、合影photo-strip、数字day-stats |
| 2 | hero-with-image-right + sub-grid-pair | person_card.image（左侧人物卡） | 关键人物金句、次稿副线、今日产出、语录墙 |
| 3 | banner-image-top + sub-grid-with-image | banner_image（顶部通栏横图） | 副刊深度、复读传递链、群友催更、今日黑话 |
| 4 | highlights-portraits + appendix-grid | tomorrow.qr（右下角二维码） | 人物高光、附录 SOP/Q&A、下回分解、报尾colophon |

### 5 步强制工作流

```
Step 0: 数据准备（用户 / Agent 提供）
  ├─ story.json（group-daily skill 产出）
  ├─ avatars.json（vchat group-members --avatars 导出）
  ├─ 群图片目录（聊天截图，建议 ≥ 8 张）
  └─ layout-plan.json（AI 在 Step 3 编写）

Step 1: AI 分析聊天记录 + 运行 image_probe.py
  ├─ 用 Read 工具分析 story.json 关键节点
  ├─ 用 Bash 运行 image_probe.py：
  │   python3 scripts/image_probe.py /tmp/<群名>_images/ --date <YYYYMMDD> --min-kb 20
  ├─ 根据图片元数据（shape / kb / suggested_layout）选图填入 plan
  └─ 选图策略：
       - hero-figure（中等横图）→ 副刊 banner
       - person-card（竖图）→ 第 2 版人物卡
       - banner-image（大横图）→ 报眉横图
       - qr（二维码）→ tomorrow.qr
       - decoration（极小图）→ 慎用，可能只是表情

Step 2: AI 根据当天素材编写 layout-plan.json
  ├─ 参考 references/newspaper-schema.md（字段定义）
  ├─ 参考 references/layout-templates.md（版式模板）
  ├─ 参考 examples/layout-plan-template.json（空白模板）
  ├─ 确定版数（偶数版）：timeline 节点数 ≤ 6 → 2 版；≤ 12 → 4 版；≤ 18 → 6 版；> 18 → 8 版
  ├─ 每版填入 references/newspaper-design.md 里的硬约束字段
  └─ 输出：/tmp/layout-plan-<日期>-<群名>.json

Step 3: 渲染 HTML
  └─ Bash 运行：
     python3 scripts/render_newspaper.py \
       /tmp/story_<日期>_<群名>.json \
       /tmp/avatars.json \
       /tmp/layout-plan-<日期>-<群名>.json \
       ~/Desktop/<群名>日报_<日期>_报纸版.html

Step 4: AI 自检 + 高度验证（注入 JS）
  ├─ 用 Bash 打开浏览器控制台：
     chrome --headless --dump-dom <file> --print-to-pdf <output>.pdf
  ├─ 注入高度测量脚本，验证每版高度是否 = 1587px
  └─ 自检清单（每条必须 100% 满足）：
       [ ] 4 版高度差 ≤ 5px
       [ ] 每版 page-foot margin-top: auto（贴底）
       [ ] 无 double 双线
       [ ] 无 dashed 虚线
       [ ] 无装饰花纹（◆◇✦❖）
       [ ] 所有数字 / 引语 / 黑话有出处
       [ ] 头像 100% 加载（不允许首字 placeholder）
       [ ] 每版底部无 > 80px 空白带

Step 5: 导出 PDF
  └─ Bash：
     chrome --headless --disable-gpu \
       --print-to-pdf=<output>.pdf \
       --print-to-pdf-no-header \
       --run-all-compositor-stages-before-draw \
       --print-layout=experimental \
       ~/Desktop/<群名>日报_<日期>_报纸版.html
```

### image_probe.py 用法

```bash
# 基本扫描（全部日期）
python3 scripts/image_probe.py /tmp/<群名>_images/ > /tmp/image_probe.json

# 指定日期 + 过滤小图
python3 scripts/image_probe.py /tmp/<群名>_images/ \
  --date 20260511 --min-kb 20 > /tmp/image_probe.json

# 输出示例（JSON 数组）
[
  {
    "path": "/tmp/.../20260511_213357_xxx.png",
    "filename": "...",
    "ts": "21:33",
    "width": 1920,
    "height": 1080,
    "aspect": 1.78,
    "shape": "landscape",
    "kb": 824,
    "suggested_layout": {
      "role": "banner-image",
      "max_width_px": 1090,
      "display_height_px": 412,
      "note": "大横图，副刊/深度版 banner 跨栏首选"
    }
  }
]
```

### layout-plan.json 字段速查

```
masthead（报头）          → references/newspaper-schema.md #masthead-字段
page1（头版）            → references/newspaper-schema.md #page1（头版）字段
page2（共建·人物卡）      → references/newspaper-schema.md #page2（共建·人物卡）字段
page3（副刊·横图 banner） → references/newspaper-schema.md #page3（副刊·横图 banner）字段
page4（人物·附录）        → references/newspaper-schema.md #page4（人物·附录）字段
自动读 story.json 的字段  → references/newspaper-schema.md #自动读-storyjson-的字段（不需在-plan-写）
```

### 渲染失败排错

| 现象 | 根因 | 修法 |
|------|------|------|
| KeyError: 'masthead' | plan.json 缺顶层字段 | 复制 `examples/layout-plan-template.json` 重写 |
| 某版超 1587px | 该版 plan 内容总和过多 | 缩 timeline_strip items / 缩 lingo items / 缩 desc 字数 |
| 某版 < 1582px 留空白 | plan 内容不够 | 加 briefings / timeline_strip / qw items 条数；或加专栏 |
| 图 404 不显示 | `image` 路径错或文件已删 | 确认 `file://` 路径绝对 + 文件存在 |
| 头像首字 placeholder | wxid 错或 avatars.json 缺 | 用 `vchat group-members --avatars` 重导 |
| `cast_pick_extra_t8_filter_name` 不生效 | 该 timeline cast 里没匹配名字 | 检查 story.json 对应 timeline 的 cast 数组 |

### 设计硬约束速查

| 约束 | 值 |
|------|-----|
| 版数 | 偶数（2/4/6/8） |
| 每版高度 | **1587px**（A3 竖版） |
| 高度差容忍 | ≤ 5px |
| 底色 | `#fdfcf8` |
| 报名红 | `#c41e1e`（仅报名 + drop cap + 引语竖线） |
| 章节色（次要） | `#1f2d4a`（深蓝） |
| 标题字体 | Noto Serif SC（宋体） |
| 正文字体 | Noto Serif SC |
| 英文/数字字体 | Playfair Display |
| 总线条数 | ≤ 30 条全报纸 |
| 8px 粗黑实线 | 仅第 1 版报头顶部，其他禁用 |
| double 双线 | **禁用全部** |
| dashed 虚线 | **禁用全部** |
| 装饰花纹 | **禁用全部** |

### 打包资源

```
scripts/
  render_newspaper.py    # 数据驱动 HTML 渲染器（支持 2/4/6/8 版）
  image_probe.py         # PIL 图片元数据探测（shape / role / 尺寸）

references/
  newspaper-design.md    # A3 设计硬约束（17 轮迭代踩坑记录）
  newspaper-schema.md     # layout-plan.json 完整字段文档
  layout-templates.md     # 15 种版式模板 + CSS 类名 + 高度预算表

examples/
  layout-plan-template.json  # 空白 JSON 模板（v1.2）
```

## 失败模式

| 失败原因 | 表现 | 解决 |
|---------|------|------|
| `story.json` 缺少字段 | KeyError 或空白 | 读取错误后用 `[待填充]` 占位，告知用户 |
| 群图片目录不存在 | image_probe.py 无输出 | 提示用户提供图片目录路径 |
| 版面超 1587px | 某版溢出 | 按 references/newspaper-design.md 9. 空白处理流程精简内容 |
| 高度不一致（> 10px） | 打印错位 | 用 flex:1 撑开 + 加 timeline_strip / quote_wall 填补 |
| 头像 404 | 首字 placeholder | 重新导出 avatars.json 并检查路径 |
