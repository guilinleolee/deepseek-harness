---
name: xhs-visual-director-to-image-gen
version: 1.0.0
stage: 22
license: MIT（仅规范部分，引用 upstream 名称作接口说明）
date: 2026-07-20
status: spec · 待 MUAPI_API_KEY / 真集成 e2e
---

# L3 Spec · xhs-visual-director → 出图器 桥接规范

## 0. 目标

让 `xhs-visual-director-skill` 的**风格判断报告 + 视觉母版 + 逐页 prompt** 真正下发到 3 个本地下游出图器之一，输出图片文件（而不是停在文本 prompt）。

```
┌────────────────────────────────────────────┐
│  xhs-visual-director-skill  (upstream)      │
│  输出: 风格判断报告 + 6-8 页 prompt 列表    │
└────────────────────────────────────────────┘
                  │
                  │  桥接（本 spec）
                  ▼
┌──────────────────────────────────────────────────────────────┐
│  下游出图器（任选其一）                                       │
│                                                              │
│  ① gpt-image-2-style-library (21 模板 + 24 风格回灌映射)     │
│  ② baoyu-xhs-images        (12 风格 × 8 版式 × 3 调色板)    │
│  ③ xhs-images              (88 模板 + 12 AI 创意封面)        │
└──────────────────────────────────────────────────────────────┘
                  │
                  ▼
        multi-platform-publisher → xhs / wechat / web
```

## 1. 输入契约（来自 xhs-visual-director）

`xhs-visual-director` 的完整输出有 4 部分，本 spec 只关心可下发到出图器的子集：

```yaml
visual_director_output:
  style_judgment:
    content_type: string  # 11 类之一（观点型 / 教程型 / 工具推荐型 / 案例拆解型 / ...）
    goal: string           # 7 类之一（吸引点击 / 建立专业度 / 促成收藏 / 引发评论 / ...）
    audience_emotion: string
    info_density: enum[low, medium, high, extreme]
    main_style: string     # 24 风格之一
    sub_style: string      # 24 风格之一
    excluded_styles: [string]

  visual_master:
    palette: [hex, hex, hex]   # 主 + 辅 + 点缀
    typography:
      title: string    # 思源黑体 / Inter / ...
      body: string
    canvas: "1080x1440, 3:4 vertical portrait"
    background: string
    recurring_elements: [string]  # 网格 / 玻璃面板 / 代码窗口 / ...

  per_page_prompts:
    - page: 1
      role: cover | opening | body | closing
      prompt: string  # 完整英文/中文 prompt，含画幅约束
      negative: [string]
      text_safe_zone: rect  # 中文后期叠加区
```

## 2. 桥接逻辑（按下游 backend 分支）

### 2.1 → gpt-image-2-style-library

**触发条件**：用户偏高端 / 商业 / 工业级质感 / 信息密度 high 以上。

**映射步骤**：

1. `main_style + sub_style` → 查 `style-24-to-gpt-image-2-mapping.md` 找最匹配的 gpt-image-2 模板（category × template）
2. 把 `visual_master.palette` 转成 `style-library.md` 的 color tokens
3. 把 `per_page_prompts[].prompt` 作为 **subject and task** 块
4. 模板自带的 `guidance` + `pitfalls` 强制注入 prompt 末尾（防坑）
5. 加 `aspect_ratio: "3:4"`，`canvas_size: "1080x1440"`

**示例**：

```yaml
# 输入
main_style: "9. 高级商业提案风"
sub_style: "10. 全球贸易网络风"
info_density: high

# 桥接到
gpt_image_2:
  category: "海报与排版"  # 第 3 类
  template: "Poster Layout System / 海报排版系统"
  fallback_template: "Brand Touchpoint Board / 品牌触点视觉板"
  prompt_blocks:
    subject: "全球贸易网络海报，义乌商户 AI 外贸主题..."
    composition: "左侧大标题区（40%），右侧全球点状地图..."
    style: "深蓝黑底 + 暖金细线 + 银灰文字，国际商务无衬线..."
    text: "中文标题区 35% 高度，英文副标题 12pt..."
    palette: ["#0a1929", "#f0e6d2", "#d4af37", "#c0c0c0"]
    pitfalls_avoid: ["蓝紫渐变", "卡通图标", "地图过花"]
```

### 2.2 → baoyu-xhs-images

**触发条件**：用户想要纯小红书图文卡片 / 12 风格 × 8 版式 / 1-10 张图。

**映射步骤**：

1. `main_style` → baoyu 的 12 风格（手工映射，见 §3 表）
2. `visual_master.palette` → 3 调色板（暖色 / 冷色 / 黑白）选 1
3. 版式：根据 `page.role` 选 8 版式之一
4. 每页 prompt 直接喂 baoyu 的 `EXTEND.md`

### 2.3 → xhs-images（天龙自研）

**触发条件**：需要 88 模板的丰富版式 + 12 AI 创意封面惊喜感。

**映射步骤**：

1. 风格判断报告 → xhs-images 的"内容类型"标签
2. 视觉母版 → 选 88 模板的版式与配色组合
3. AI 封面模式：用 `main_style` + 1-2 句核心观点生成惊喜感封面

## 3. 风格 → 风格 去重映射（核心）

24 风格 与 3 个下游风格的对应关系：

| # | xhs-visual-director 风格 | gpt-image-2 模板 | baoyu 12 风格 | xhs-images |
|---|---|---|---|---|
| 1 | 深色科技杂志风 | Poster Layout / Ink Double Exposure | 极简科技 | 科技极简 |
| 2 | 黑白灰 + 荧光绿冲击风 | Conceptual Typography Poster | 极简黑白 | 视觉冲击 |
| 3 | Notion 高级卡片风 | Infographic Engine | 知识卡片 | 知识科普 |
| 4 | 液态玻璃 / 弥散极光风 | UI Screenshot System | 玻璃拟态 | 未来感 |
| 5 | 极简产品发布会风 | Concept Product Breakdown | 产品展示 | 极简产品 |
| 6 | 反差冲击封面风 | Sports Campaign Poster | 强对比 | 视觉冲击 |
| 7 | 架构图 / 系统拆解风 | Infographic Engine | 系统图 | 信息图 |
| 8 | 手机截图改造风 | UI Screenshot System | UI 截图 | UI 展示 |
| **9** | **高级商业提案风** ⚠️本地缺 | **Brand Touchpoint Board**（新增）| ⚠️ 商务提案 | ⚠️ 商务提案 |
| **10** | **全球贸易网络风** ⚠️本地缺 | **Poster Layout + Architecture & Space** 拼 | ⚠️ 地图叙事 | ⚠️ 地图叙事 |
| 11 | 高级白底杂志风 | Poster Layout | 白底简约 | 编辑感 |
| 12 | 红绿对错对比风 | Infographic Engine | 对比 | 对比 |
| **13** | **赛博档案 / 黑客文件风** ⚠️本地缺 | **UI Screenshot**（暗色变体）| ⚠️ 暗黑 | ⚠️ 暗黑极客 |
| **14** | **未来实验室风** ⚠️本地缺 | **Concept Product Breakdown** | ⚠️ 实验感 | ⚠️ 实验 |
| 15 | 设计师灵感板风 | Brand Touchpoint Board | 设计灵感 | 灵感板 |
| **16** | **高级极简黑金风** ⚠️本地缺 | **Brand Identity Package** | ⚠️ 黑金 | ⚠️ 黑金 |
| 17 | 软件界面 UI 风 | UI Screenshot System | UI 截图 | UI 展示 |
| 18 | 课程讲义 / 高级黑板风 | Nature Science Poster | 教学 | 课程 |
| 19 | 个人品牌宣言风 | Brand Identity Package | 个人 IP | 品牌 |
| 20 | 情绪共鸣 / 夜间独白风 | Conceptual Typography Poster | 情感 | 情绪 |
| 21 | 数据报告 / 趋势洞察风 | Infographic Engine + Poster | 数据 | 信息图 |
| **22** | **故事漫画分镜风** ⚠️本地缺 | **Scene Storytelling** | ⚠️ 漫画 | ⚠️ 漫画分镜 |
| **23** | **极简黑金风（同 16，重命名）** | - | - | - |
| **24** | **课程讲义（同 18）** | - | - | - |

**24 风格实际有效 = 21 条**（22-24 是分类细化或重命名，详见 `style-24-to-gpt-image-2-mapping.md`）。

**关键发现**：
- 21 条里有 **7 条**本地之前缺（标 ⚠️）：9 高级商业提案 / 10 全球贸易网络 / 13 赛博档案 / 14 未来实验室 / 16 黑金 / 22 故事漫画分镜 / 部分细分
- 这 7 条的回灌会显著扩展 [gpt-image-2-style-library](C:\Users\li\.claude\skills\gpt-image-2-style-library\SKILL.md) 的覆盖
- 24 风格中第 4 液态玻璃 / 第 11 白底杂志 / 第 21 数据报告 本地覆盖较弱，回灌后会显著增强

## 4. 触发脚本（建议路径）

```bash
# 触发：从 xhs-visual-director 输出 → 出图
dragon-engine/skills/xhs-visual-director-skill/l3-specs/scripts/render.sh \
  --visual-director-output ./tmp/xhs-visual-director-output.yaml \
  --backend gpt-image-2 \  # or baoyu-xhs-images / xhs-images
  --output-dir ./tmp/xhs-png/

# 流程
# 1. 解析 visual_director_output
# 2. 根据 --backend 路由到对应 adapter
# 3. adapter 把 yaml → backend schema
# 4. 调用 backend 出图
# 5. 返回本地路径列表 + 比例自检结果
```

## 5. PASS 判定（e2e 验证）

| 项 | 判定标准 |
|---|---|
| 桥接正确性 | visual_director 24 风格 → 3 backend 中至少 1 个能映射成功 |
| 风格一致 | 实际出图与 visual_director 风格判断报告的主+辅风格匹配 |
| 画幅正确 | 所有图 3:4（1080×1440）严格保留 |
| 中文安全 | 文字区有 safe zone，后期可叠加真实中文 |
| 自检通过 | `templates/visual_review_checklist.md` 6 维全部 PASS |

**当前状态**：spec 已写完，等待**真集成 e2e**（需要 backend 在线 + visual-director 真跑通一次完整 10 问流程）。

## 6. 与已有 21 阶段流水线的接入点

| 接入点 | 阶段 | 资产 |
|---|---|---|
| 上游触发 | 35-06 V1.3 第 10 维（UGC 视频化） | [35-06-social-media-v12-laoli.md](C:\Users\li\.claude\projects\dragon-engine\agents\35-06-social-media-v12-laoli.md) |
| 风格决策 | 28-04 内容策划师 V2.0 | - |
| 出图 | 35-02 V13.3 / 35-05 V10.3 / 35-06 V1.2 | - |
| 发布 | multi-platform-publisher V1.0 | [multi-platform-publisher](C:\Users\li\.claude\skills\multi-platform-publisher\SKILL.md) |

## 7. 已知约束

- ⚠️ xhs-visual-director 的 10 问协议需要交互输入，本 spec 默认 visual-director 已完成问询并产出 yaml
- ⚠️ 中文渲染在 AI 图像生成中不稳定 → 本 spec 强制 `text_safe_zone` + 后期叠加
- ⚠️ 3 个 downstream backend 都需要各自的 API key / runtime，本 spec 只做规范层定义