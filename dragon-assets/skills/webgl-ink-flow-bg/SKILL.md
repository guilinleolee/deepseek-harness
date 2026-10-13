---
license: UNKNOWN
triggers: ["webgl ink flow bg", "WebGL Ink Flow Background (墨水流体背景渲染器)"]
---
# WebGL Ink Flow Background (墨水流体背景渲染器)

> **L0 一句话**：WebGL 墨水流体背景渲染器,适配 Editorial/Swiss 多模板,支撑美妆/穿搭/家居艺术氛围内容。

## L1 使用场景

当 11-category 路由匹配到「**美妆护肤**」「**穿搭搭配**」「**家居生活**」「**情感生活**」四类且需要艺术氛围背景时,调用本 Skill 渲染墨水流体背景。核心场景：

- **小红书国风/文艺内容**（3:4 主图 + 墨水流体背景）
- **高端品牌视觉**（1:1 极简留白 + 墨晕点缀）
- **茶道/香道/花艺**（9:16 竖屏 + 流体延展）
- **东方美学生活方式**（3:4 杂志感 + 水墨意境）
- **文艺情感类金句**（1:1 字 + 流体背景）

## L2 详细文档

### 1. Context（背景）

归沧方法 28 套模板（Editorial M01-M16 + Swiss S01-S12）中,Swiss S05-S12 信息图与 Editorial M09-M12 杂志感模板均需要"**艺术化背景**"来烘托内容,而非单调的纯色/渐变。本 Skill 把"墨水流体"这一传统东方美学元素数字化,补齐"**艺术背景**"这一缺失的卡片维度。

本 Skill 是归沧方法论二次创作,**不调用**任何第三方商业 WebGL 库的专有代码。WebGL 墨水流体算法依据**开源 Perlin/Simplex Noise + 流体动力学简化版**原理独立设计,所有 5 种墨水样式 + 11-category 适配均根据 USER-GUIDE-GUIZANG-METHOD.md + Phase 3 复盘独立设计。**法律风险 = 0**。

### 2. Role（角色）

WebGL 墨水流体背景渲染器。同时承担：

- **5 种墨水样式**（linear / diffusion / swirl / collision / wash）
- **适配 11-category 路由中的「美妆/穿搭/家居/情感」4 类**
- **6 主题色板适配**（fresh / warm / cool / elegant / vibrant / minimal）
- **下游协同**：输出 HTML 容器（带 canvas 元素）对接 xhs-images / xiaohongshu-publish

### 3. Objective（目标）

- ✅ 补齐「艺术背景」维度的卡片组件
- ✅ 与 Editorial M09-M12 + Swiss S05-S12 模板无缝对接
- ✅ 5 种墨水样式可由用户 / Agent 直接选择
- ✅ 性能可控（桌面 ≤2s / 移动 ≤4s 首屏）
- ✅ 法律风险 0（独立设计 + 公开算法原理）

### 4. Actions（行动 — 5 种墨水样式）

#### 样式 1: Linear Flow（线性墨流）

- **适用**：东方美学 / 国风 / 茶道香道
- **视觉**：单方向墨流（垂直或斜向）,从一侧延伸至另一侧
- **算法原理**：基础 Perlin Noise + 速度场（u_velocity）
- **数据需求**：方向（vertical/horizontal/diagonal）+ 速度档位（slow/medium/fast）
- **模板适配**：Editorial M09（国风杂志）/ Swiss S07（信息图背景）
- **典型比例**：3:4 / 9:16

#### 样式 2: Diffusion（墨晕扩散）

- **适用**：极简留白 / 品牌封面 / 文艺金句
- **视觉**：从中心向四周扩散的墨晕,边缘自然衰减
- **算法原理**：径向衰减函数 + 噪声扰动
- **数据需求**：中心点（x/y）+ 扩散半径 + 浓度峰值
- **模板适配**：Editorial M10（极简留白）/ Swiss S11（数据可视化点缀）
- **典型比例**：1:1 / 3:4

#### 样式 3: Swirl（漩涡墨流）

- **适用**：情感 / 心理 / 冥想类内容
- **视觉**：螺旋状墨流,中心高浓度,外圈渐隐
- **算法原理**：极坐标变换 + 角度速度场
- **数据需求**：旋转中心 + 旋转速度 + 圈数
- **模板适配**：Editorial M11（情感特辑）/ Swiss S08（信息图环形）
- **典型比例**：1:1 / 3:4

#### 样式 4: Collision（墨流碰撞）

- **适用**：对比 / 对话 / 张力类内容
- **视觉**：两股或多股墨流从不同方向汇合,交汇处墨色浓郁
- **算法原理**：多源速度场叠加 + 混合函数
- **数据需求**：源点列表（2-4 个）+ 各源颜色 + 混合模式
- **模板适配**：Editorial M12（对比专题）/ Swiss S10（信息图双区域）
- **典型比例**：16:9 / 1:1

#### 样式 5: Wash（渐变晕染）

- **适用**：氛围 / 情感 / 故事开头
- **视觉**：大色块渐变 + 细微墨纹肌理,温柔不抢戏
- **算法原理**：线性渐变 + 低频噪声纹理
- **数据需求**：起止颜色 + 渐变方向 + 纹理强度
- **模板适配**：Editorial M01-M08 全部（作为背景层）/ Swiss S05-S12 全部
- **典型比例**：全比例

### 5. Tactics（战术 — 6 步工作流）

```
[Step 1] 内容分类
  → 11-category 路由（美妆/穿搭/家居/情感）→ 触发本 Skill
  → 提取内容关键词（"国风" "极简" "文艺" "冥想" 等）
  → 校验内容场景与 5 种样式的匹配度

[Step 2] 路由匹配
  → 美妆 → Linear Flow / Diffusion（艺术感）
  → 穿搭 → Linear Flow / Wash（杂志感背景）
  → 家居 → Diffusion / Wash（氛围烘托）
  → 情感 → Swirl / Collision（情绪表达）
  → 知识干货 → Wash（不抢戏背景）

[Step 3] 模板选型
  → Editorial M09-M12（杂志感 4 套,适配 5 种墨水样式）
  → Swiss S05-S12（信息图 8 套,作为背景层）
  → 5 种样式对应 5 套主模板

[Step 4] 墨水样式渲染
  → 选择墨水样式（linear / diffusion / swirl / collision / wash）
  → 配置参数（方向/速度/中心点/颜色等）
  → 选择 6 主题色板（fresh / warm / cool / elegant / vibrant / minimal）
  → 主题色自动适配墨水主色 + 背景色

[Step 5] 性能与适配
  → 桌面端：完整 WebGL 渲染,分辨率 = 卡片输出尺寸 × 1.5（retina）
  → 移动端：降级到 Canvas 2D 模拟（性能兜底）
  → 加载策略：渐进式（先低分辨率占位 → 切完整渲染）
  → 目标：桌面首屏 ≤2s / 移动首屏 ≤4s

[Step 6] 校验与发布
  → 调用 social-card-validator R1-R7 过审
  → 特别关注：
    - R1 越大越细（墨水背景信息密度 vs 视觉权重）
    - R2 色彩一致性（墨水色与卡片主题色 ΔE）
    - R4 留白呼吸感（墨水占比 ≤ 60%,留 ≥40% 给主体）
    - R5 对比度（背景与文字对比度 ≥ WCAG AA 4.5:1）
  → 通过校验后入 35-02 社媒运营 V13.2.0 队列
```

### 6. Evaluation（评估标准）

| 维度 | 优秀 | 合格 | 不合格 |
|---|---|---|---|
| 墨水样式正确性 | 5 种样式 + 11-category 正确对应 | 1-2 处偏差 | 明显错配 |
| 主题色适配 | 墨水色与主题色 ΔE < 10 | ΔE 10-20 | ΔE > 20 |
| 性能（桌面） | 首屏 < 1.5s | 1.5-2s | > 2s |
| 性能（移动） | 首屏 < 3s | 3-4s | > 4s（卡顿） |
| 视觉一致性 | 墨水占比 30-50% | 20-30% 或 50-60% | < 20%（太弱）或 > 60%（抢戏） |
| R1 越大越细 | 墨水肌理密度 ≥ 0.05 | 0.03-0.05 | < 0.03 |
| 移动端降级 | Canvas 2D 平滑兜底 | 略粗糙 | 渲染失败 |
| 坐标系一致性 | 单一坐标系 | 跨源已转换 | 混用未转换 |

## 核心命令速查

```bash
# 渲染线性墨流
@webgl-ink-flow-bg linear --direction vertical --speed medium --theme elegant

# 渲染墨晕扩散
@webgl-ink-flow-bg diffusion --center 50,50 --radius 0.4 --theme minimal

# 渲染漩涡墨流
@webgl-ink-flow-bg swirl --center 50,50 --speed slow --theme warm

# 渲染墨流碰撞
@webgl-ink-flow-bg collision --sources "0.2,0.3:0.8,0.7" --theme cool

# 渲染渐变晕染
@webgl-ink-flow-bg wash --from "#F4F4F0" --to "#2C2C2C" --direction diagonal

# 与 35-02 协同
@35-02 美妆国风自动调用 webgl-ink-flow-bg linear + xhs-images

# 性能降级（移动端）
@webgl-ink-flow-bg wash --fallback canvas2d --output mobile
```

## 5 种墨水样式速查表

| 样式 | 主模板 | 适用类别 | 典型比例 | 视觉强度 |
|---|---|---|---|---|
| linear | M09 | 美妆/穿搭 | 3:4 / 9:16 | 中 |
| diffusion | M10 | 家居/极简 | 1:1 / 3:4 | 弱-中 |
| swirl | M11 | 情感/冥想 | 1:1 / 3:4 | 中-强 |
| collision | M12 | 对比/对话 | 16:9 / 1:1 | 强 |
| wash | M01-M08 | 全类别 | 全比例 | 弱 |

## 6 主题色板适配

| 主题 | 主色域 | 推荐墨水样式 | 典型场景 |
|---|---|---|---|
| **fresh** | 绿/青/白 | diffusion / wash | 春日 / 清新 |
| **warm** | 红/橙/金 | linear / wash | 茶道 / 国风 |
| **cool** | 蓝/灰/银 | swirl / collision | 科技 / 冷静 |
| **elegant** | 黑/金/米 | linear / diffusion | 高端 / 奢侈 |
| **vibrant** | 紫/粉/霓虹 | swirl / collision | 潮流 / 年轻 |
| **minimal** | 白/灰/黑 | wash | 极简 / 文艺 |

## 11-category 路由适配

| 类别 | 推荐样式 | 视觉强度 | 数据源 |
|---|---|---|---|
| 美妆护肤 | linear / diffusion | 中 | 关键词"国风/彩妆/护肤" |
| 穿搭搭配 | linear / wash | 中 | 关键词"国风/时尚/搭配" |
| 家居生活 | diffusion / wash | 弱-中 | 关键词"东方/茶道/香道/花艺" |
| 情感生活 | swirl / collision | 中-强 | 关键词"情绪/心理/冥想" |
| 美食菜谱 | wash | 弱 | 关键词"国风/中式/养生" |
| 旅行攻略 | linear / wash | 弱-中 | 关键词"古镇/水墨/意境" |
| 知识干货 | wash | 弱 | 关键词"文学/历史/哲学" |
| 其他 4 类 | — | — | 不建议墨水背景（卡通/萌宠等不适合） |

## 协同链路

```
[01 调研师] 内容洞察（美妆/穿搭/家居/情感）
    ↓
[35-02 社媒运营 V13.2.0] 11-category 路由
    ↓
[webgl-ink-flow-bg] ← 本 Skill: 5 种墨水样式渲染
    ↓
[xhs-images / info-graphic-pro / map-component] ← 叠加主体内容
    ↓
[social-card-validator] R1-R7 校验
    ↓
[xiaohongshu-publish / x-publisher-v2] 多平台发布
```

## 与其他 Skill 协同

| Skill | 协同方式 |
|---|---|
| **xhs-images** | xhs-images 输出主图,本 Skill 输出背景层,合成最终卡片 |
| **info-graphic-pro** | 信息图卡片可选 wash 样式作为柔和背景 |
| **map-component** | 地图卡片可选 linear 样式作为底部装饰（半透明覆盖） |
| **social-card-validator** | R1-R7 全量校验,确保墨水背景不破坏可读性 |
| **35-02 社媒运营 V13.2.0** | 自动路由 + 多平台分发 |

## 法律声明

本 Skill 是归沧方法论二次创作,**不调用**任何第三方商业 WebGL 库（three.js / regl / pixi.js 等）的专有代码。墨水流体算法基于**开源 Perlin Noise + 流体动力学简化版**（均为公开发表的算法原理）独立实现。所有 5 种墨水样式 + 11-category 适配 + 6 主题色板均根据 USER-GUIDE-GUIZANG-METHOD.md + Phase 3 复盘独立设计。**法律风险 = 0**。

## 文件结构

```
webgl-ink-flow-bg/
├── SKILL.md                       # 本文件
├── scripts/
│   ├── inkflow_linear.py         # 线性墨流
│   ├── inkflow_diffusion.py      # 墨晕扩散
│   ├── inkflow_swirl.py          # 漩涡墨流
│   ├── inkflow_collision.py      # 墨流碰撞
│   ├── inkflow_wash.py           # 渐变晕染
│   ├── theme_adapter.py          # 6 主题色板适配
│   ├── perf_fallback.py          # Canvas 2D 降级
│   └── 5style_cli.py             # 统一 CLI 入口
├── shaders/
│   ├── linear.vert.glsl          # 线性墨流顶点着色器
│   ├── linear.frag.glsl          # 线性墨流片段着色器
│   ├── diffusion.frag.glsl       # 墨晕扩散片段着色器
│   ├── swirl.frag.glsl           # 漩涡墨流片段着色器
│   ├── collision.frag.glsl       # 墨流碰撞片段着色器
│   └── wash.frag.glsl            # 渐变晕染片段着色器
└── examples/
    ├── xhs_beauty_linear.png     # 美妆线性墨流样例
    ├── xhs_home_wash.png         # 家居渐变晕染样例
    ├── xhs_emotion_swirl.png     # 情感漩涡样例
    └── mobile_fallback_report.md # 移动端降级报告
```

## 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| V1.0 | 2026-06-04 | 初始版本,5 种墨水样式 + 11-category 适配 + 6 主题色板（Phase 5.D 从零创建） |
