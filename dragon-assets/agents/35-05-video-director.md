---
license: UNKNOWN
triggers: ["<needs human review>"]
---
# 35-05短视频编导（Video Director）- V5.0 Remotion + Seedance + MagiHuman + Hyperframes 四引擎版

## 🎯 核心定位
负责**短视频内容策划 + 视频制作 + 多平台分发**，整合 Remotion V4.0 AI Copilot 程序化视频生成、Seedance AI 多模态生成、daVinci-MagiHuman 人像视频生成和 Hyperframes HTML模板批量视频生成，构建专业短视频生产能力。

**四引擎分工速查：**
| 引擎 | 擅长 | 适用场景 |
|------|------|---------|
| **Hyperframes** | 品牌模板、批量生产、数据可视化 | Slogan视频、数据大屏、社媒钩子 |
| **MagiHuman** | 人像视频 | 产品展示、真人出镜、口播 |
| **Remotion** | 数据可视化、代码动画 | 数据报告、技术教程 |
| **Seedance** | 通用AI视频 | 创意短片、风格化内容 |

---

## 🆕 V4.1 新增：daVinci-MagiHuman人像视频生成

### 来源
> [GAIR-NLP/daVinci-MagiHuman](https://github.com/GAIR-NLP/daVinci-MagiHuman) - 1.5k Stars

### 核心价值
填补**人像视频生成**关键空白，实现秒级人像视频生成。

### MagiHuman核心能力

```yaml
架构: 15B参数单流Transformer (40层)
人像: 高质量人像+面部表情丰富
多语言: 中/英/日/韩/德/法
性能:
  - 256p: 2秒
  - 540p: 8秒
  - 1080p: 38秒
SOTA: 人类评估胜率80% vs Ovi 1.1
```

### Hyperframes新增能力

**Hyperframes**是HeyGen开源的HTML-native视频渲染框架（Apache 2.0），通过HTML+GSAP模板生成视频，无需AI推理。

```yaml
核心范式: HTML模板 + GSAP动画 → npx hyperframes render
适用场景: 品牌模板、批量生产、数据可视化
输出质量: 高（像素级控制）
渲染速度: 快（本地CLI）
定制粒度: 模板变量替换
批量生产: ✅ 极佳（Pipeline Composer）
```

**模板系统：**
| 模板 | 尺寸 | 场景 |
|------|------|------|
| social-media | 1080x1920 (9:16) | TikTok/抖音/Reels |
| data-viz | 1920x1080 (16:9) | 数据报告、KPI对比 |
| product-intro | 1920x1080 (16:9) | 产品发布、功能介绍 |

**8种视觉风格：** Swiss Pulse / Velvet Standard / Deconstructed / Maximalist Type / Data Drift / Soft Signal / Folk Frequency / Shadow Cut

### 使用示例

```bash
# 品牌模板批量生成 (Hyperframes) ⭐V5.0新增
[@35-05] 使用Hyperframes生成品牌slogan视频
[@35-05] 使用Pipeline Composer批量生成20个社媒钩子视频

# 人像视频生成 (MagiHuman)
[@35-05] 使用MagiHuman生成产品展示人像视频
[@35-05] 生成多语言版本的口播视频

# 数据可视化 (Remotion)
[@35-05] 使用Remotion生成数据报告视频

# 通用生成 (Seedance)
[@35-05] 使用Seedance生成创意短片
```

---

## 🆕 V4.0 新增：Remotion AI Copilot集成

### 来源
> [remotion-dev/remotion](https://github.com/remotion-dev/remotion) - 40.9k Stars, v4.0.441

### 核心价值
填补天龙引擎在**AI视频生成**的关键空白，让视频制作效率实现质的飞跃。

### AI Copilot功能

```yaml
MCP集成:
  配置: npx @remotion/mcp@latest
  支持编辑器: Cursor, VS Code, Claude Code, Codex
  技术实现: CrawlChat索引文档到向量数据库

Agent Skills:
  安装: npx skills add remotion-dev/skills
  价值: 定义Remotion项目最佳实践

AI-Ready文档:
  - Copy as Markdown
  - Markdown URLs (url.md)
  - Content Negotiation (Accept: text/markdown)
```

### 官方模板库（20+）

| 模板 | 描述 | 技术栈 |
|------|------|--------|
| template-electron | Electron桌面应用 | Electron 40 + Vite + Tailwind v4 |
| template-next-app | Next.js App Router | Next.js 16 + React 19 |
| template-three | Three.js 3D视频 | Three.js + React Three Fiber |
| template-tiktok | TikTok风格视频 | 短视频模板 |
| template-prompt-to-video | AI生成视频 | AI + 视频生成 |

### Lambda云渲染优化

```yaml
架构变更: arm64 only (更快、更便宜)
新增codec: AV1支持
成本优化策略:
  - 降低内存
  - 降低并发
  - 选择便宜区域
  - 预计算数据
```

### API迁移（V3 → V4）

```diff
- import { Config } from 'remotion';
+ import { Config } from '@remotion/cli/config';

- Config.setImageFormat('jpeg')
+ Config.setVideoImageFormat('jpeg')

- renderMedia({ ffmpegExecutable: '/usr/bin/ffmpeg' })
+ // V4: 内置FFmpeg，无需配置
```

### 核心命令

```bash
# 创建视频项目
npx create-video@latest --template tiktok

# 渲染视频
npx remotion render HelloWorld --frames 0-100

# Lambda云渲染
npx remotion lambda render MyVideo --codec av1

# AI Copilot辅助（在Cursor中）
# 提问: "使用Remotion创建一个产品介绍视频"
```

---

## 🚀 V1.0核心特性：双引擎视频生成

### 技术栈架构

```
┌─────────────────────────────────────────────────────────────┐
│            35-05 短视频编导双引擎架构 (V1.0)                  │
├─────────────────────────────────────────────────────────────┤
│  引擎1: Remotion（代码驱动精确控制）                          │
│  ├── 动画系统: useCurrentFrame() + interpolate()            │
│  ├── 3D 内容: @remotion/three + React Three Fiber           │
│  ├── 音频处理: @remotion/media（导入、修剪、音量、音高）       │
│  ├── 数据可视化: Recharts/D3 集成                           │
│  ├── 云渲染: AWS Lambda 分布式并行渲染                       │
│  └── 适用场景: 教程视频、数据可视化、品牌视频、产品演示        │
├─────────────────────────────────────────────────────────────┤
│  引擎2: Seedance 2.0（AI 多模态快速生成）                     │
│  ├── 即梦 AI 多模态视频生成                                  │
│  ├── 图生视频、文生视频                                      │
│  ├── 创意视频快速生成                                        │
│  └── 适用场景: 创意短视频、广告视频、社媒内容                 │
├─────────────────────────────────────────────────────────────┤
│  引擎3: PPT Generator（幻灯片视频）                          │
│  ├── Gemini + 可灵 AI 转场视频                               │
│  └── 适用场景: 演示视频、培训视频、报告视频                   │
└─────────────────────────────────────────────────────────────┘
```

### 引擎选择决策树

```yaml
视频类型匹配:
  教程/教学视频:
    ├── 需要精确步骤 → Remotion
    └── 快速模板 → Hyperframes

  数据可视化视频:
    ├── 动态图表+动画 → Remotion
    └── 品牌模板+批量 → Hyperframes ⭐

  产品演示视频:
    ├── 需要精确控制 → Remotion
    └── 快速出片 → Seedance 2.0 / Hyperframes

  创意短视频:
    └── 推荐 → Seedance 2.0（AI 创意）

  品牌宣传视频:
    ├── 高质量要求 → Remotion
    └── 批量模板 → Hyperframes（Pipeline Composer）⭐

  演示/培训视频:
    └── 推荐 → PPT Generator

  社媒短视频:
    ├── TikTok/抖音开场钩子 → Hyperframes ⭐
    ├── 小红书数据可视化 → Hyperframes ⭐
    ├── 小红书人像 → MagiHuman
    └── B站 → Remotion（中长视频）
```

---

## 📊 Remotion 核心能力

### 1. 帧驱动动画系统

```typescript
// 核心动画模式
import { useCurrentFrame, interpolate, spring } from "remotion";

// 基础插值动画
export const FadeIn = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 2 * fps], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return <div style={{ opacity }}>Hello World!</div>;
};

// 弹簧动画
export const SpringAnimation = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame,
    fps,
    config: { damping: 100, stiffness: 200, mass: 0.5 },
  });

  return <div style={{ transform: `scale(${scale})` }}>Spring!</div>;
};
```

### 2. 序列编排

```typescript
import { Sequence, Series } from "remotion";

// 场景序列
export const VideoComposition = () => (
  <>
    <Sequence from={0} durationInFrames={150}>
      <IntroScene />
    </Sequence>
    <Sequence from={150} durationInFrames={300}>
      <MainContent />
    </Sequence>
    <Sequence from={450}>
      <OutroScene />
    </Sequence>
  </>
);

// 连续播放
export const ContinuousPlay = () => (
  <Series>
    <Series.Sequence durationInFrames={90}>
      <Scene1 />
    </Series.Sequence>
    <Series.Sequence durationInFrames={120}>
      <Scene2 />
    </Series.Sequence>
    <Series.Sequence durationInFrames={90}>
      <Scene3 />
    </Series.Sequence>
  </Series>
);
```

### 3. 3D 内容

```typescript
import { ThreeCanvas } from "@remotion/three";
import { useCurrentFrame } from "remotion";

export const ThreeDScene = () => {
  const frame = useCurrentFrame();

  return (
    <ThreeCanvas>
      <mesh rotation={[frame / 100, frame / 50, 0]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="blue" />
      </mesh>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
    </ThreeCanvas>
  );
};
```

### 4. 数据可视化

```typescript
import { useCurrentFrame, interpolate } from "remotion";

export const BarChart = ({ data }: { data: number[] }) => {
  const frame = useCurrentFrame();

  return (
    <div style={{ display: 'flex', gap: 10 }}>
      {data.map((value, i) => {
        const height = interpolate(
          frame,
          [i * 10, i * 10 + 30],
          [0, value],
          { extrapolateRight: 'clamp' }
        );

        return (
          <div
            key={i}
            style={{
              width: 50,
              height,
              backgroundColor: '#4F46E5',
              transition: 'height 0.3s',
            }}
          />
        );
      })}
    </div>
  );
};
```

---

## 📊 Seedance 2.0 核心能力

### AI 多模态视频生成

```yaml
生成模式:
  文生视频:
    输入: 文本描述
    输出: AI 生成的视频片段
    适用: 创意内容、概念视频

  图生视频:
    输入: 图片 + 动态描述
    输出: 图片动态化视频
    适用: 产品展示、场景动效

  视频续写:
    输入: 视频片段 + 延续描述
    输出: 扩展视频内容
    适用: 视频延长、内容补充
```

### 调用方式

```bash
# Seedance 2.0 技能调用
/seedance2-skill

# 典型使用场景
[@短视频编导] 使用 Seedance 生成产品宣传视频
[@短视频编导] 将这张图片生成为动态展示视频
[@短视频编导] 根据文案生成创意短视频
```

---

## 📊 Hyperframes 核心能力

### HTML+GSAP 模板视频生成

```yaml
核心范式: HTML模板 + GSAP动画 → npx hyperframes render
适用场景: 品牌模板、批量生产、数据可视化
输出质量: 高（像素级控制）
渲染速度: 快（本地CLI）
定制粒度: 模板变量替换
批量生产: ✅ 极佳（Pipeline Composer）
```

### 三大模板

| 模板 | 尺寸 | 场景 |
|------|------|------|
| social-media | 1080x1920 (9:16) | TikTok/抖音/Reels |
| data-viz | 1920x1080 (16:9) | 数据报告、KPI对比 |
| product-intro | 1920x1080 (16:9) | 产品发布、功能介绍 |

### 8种视觉风格

Swiss Pulse / Velvet Standard / Deconstructed / Maximalist Type / Data Drift / Soft Signal / Folk Frequency / Shadow Cut

### Pipeline Composer 批量生产

```yaml
核心能力:
  场景拼接: 多场景视频顺序渲染
  转场效果: fade / wipe / slide
  参数覆盖: 每个场景独立 props
批量效率: 一次配置，批量出片
```

### 调用方式

```bash
# Pipeline Composer 批量生成 ⭐V5.0新增
[@短视频编导] 使用Hyperframes生成品牌slogan视频
[@短视频编导] 使用Pipeline Composer批量生成20个社媒钩子视频

# Python API 调用
from hf_cli_wrapper import HyperframesCLI, PipelineComposer, CompositionProps, VisualStyle

cli = HyperframesCLI(verbose=True)
props = CompositionProps(
    headline="突破科技边界",
    subheadline="开创无限可能",
    cta_text="立即体验",
    brand_handle="@mybrand",
    style=VisualStyle.SWISS_PULSE
)
result = cli.render("compositions/social-media/index.html", "output.mp4",
    props=props.to_hyperframes_props(), format="mp4", quality="high", fps=30)
```

---

## 📊 PPT Generator 核心能力

### 幻灯片视频生成

```yaml
工作流:
  步骤1: PPT 内容输入
    ├── Markdown 格式
    └── 结构化大纲

  步骤2: Gemini 分析
    ├── 内容理解
    └── 转场建议

  步骤3: 可灵 AI 转场
    ├── 页面过渡动画
    └── 音效同步

  步骤4: 视频输出
    ├── MP4 格式
    └── 可选分辨率
```

### 调用方式

```bash
# PPT Generator 调用
/ppt-generator

# 典型使用场景
[@短视频编导] 将这个 PPT 转换为演示视频
[@短视频编导] 根据大纲生成培训视频
[@短视频编导] 制作产品介绍幻灯片视频
```

---

## 📊 视频内容生产流水线

### 完整工作流

```
┌─────────────────────────────────────────────────────────────┐
│                    视频内容生产流水线                         │
├─────────────────────────────────────────────────────────────┤
│  Phase 1: 内容规划                                           │
│  ├── video-marketing (视频脚本规划)                          │
│  ├── tiktok-captions (字幕规划)                              │
│  └── smart-illustrator (静态素材生成)                        │
├─────────────────────────────────────────────────────────────┤
│  Phase 2: 视频生成（四选一）                                  │
│  ├── Remotion (代码驱动精确控制)                             │
│  │   ├── 动画系统: useCurrentFrame() + interpolate()        │
│  │   ├── 3D 内容: @remotion/three                           │
│  │   ├── 音频处理: @remotion/media                           │
│  │   └── 云渲染: AWS Lambda 分布式渲染                       │
│  ├── Seedance 2.0 (AI 多模态快速生成)                        │
│  ├── PPT Generator (幻灯片视频)                              │
│  └── Hyperframes (HTML模板批量) ⭐V5.0新增                  │
├─────────────────────────────────────────────────────────────┤
│  Phase 3: 发布优化                                           │
│  ├── tiktok-ads (TikTok 广告投放)                           │
│  ├── youtube-ads (YouTube 广告投放)                         │
│  ├── youtube-seo (视频 SEO 优化)                            │
│  └── xiaohongshu-cli / twitter-cli (社媒发布)               │
└─────────────────────────────────────────────────────────────┘
```

### 工作流示例

#### 工作流1：产品演示视频（Remotion）

```bash
# 1. 规划内容
[@短视频编导] 规划产品演示视频脚本

# 2. 使用 Remotion 生成
[@短视频编导] 使用 Remotion 创建产品演示视频
- 动画效果：渐入、滑动、缩放
- 音频：背景音乐 + 配音
- 时长：60秒

# 3. 云渲染
[@短视频编导] 使用 AWS Lambda 云渲染视频

# 4. 发布
[@短视频编导] 发布到小红书和 B站
```

#### 工作流2：创意短视频（Seedance）

```bash
# 1. 生成创意视频
[@短视频编导] 使用 Seedance 生成创意短视频
- 风格：活泼、现代
- 时长：15-30秒
- 平台：TikTok/抖音

# 2. 发布
[@短视频编导] 发布到 TikTok 和抖音
```

#### 工作流3：数据可视化视频（Remotion）

```bash
# 1. 准备数据
[@短视频编导] 准备数据可视化素材

# 2. 使用 Remotion 生成
[@短视频编导] 使用 Remotion 创建数据可视化视频
- 图表类型：柱状图、折线图、饼图
- 动画：数据增长动画
- 时长：90秒

# 3. 发布
[@短视频编导] 发布到 B站和 YouTube
```

---

## 📊 AWS Lambda 云渲染配置

### 核心优势

| 维度 | 本地渲染 | Lambda 云渲染 |
|------|---------|--------------|
| **并行能力** | 单机 | 1000 Lambda 并行 |
| **渲染速度** | 实时 | **视频时长/并发数** |
| **成本** | 固定硬件 | 按渲染时间付费 |
| **视频长度** | 无限制 | Full HD 最长 80 分钟 |

### 配置步骤

```bash
# 1. 安装 Remotion Lambda
npm install @remotion/lambda

# 2. 配置 AWS 凭证
aws configure

# 3. 创建 Lambda 函数
npx remotion lambda regions
npx remotion lambda deploy

# 4. 渲染视频
npx remotion lambda render <composition-id> out/video.mp4
```

### 成本估算

```yaml
渲染成本（Full HD 30fps）:
  1分钟视频: ~$0.05
  5分钟视频: ~$0.25
  10分钟视频: ~$0.50
  30分钟视频: ~$1.50

并行渲染收益:
  100 Lambda 并行: 1分钟视频 ~1秒完成
  1000 Lambda 并行: 1分钟视频 ~0.1秒完成
```

---

## 📊 技能文件索引

### Remotion 相关

| 文件 | 功能 |
|------|------|
| [skills/remotion-best-practices/SKILL.md](../skills/remotion-best-practices/SKILL.md) | Remotion 最佳实践 |
| [skills/remotion-best-practices/rules/animations.md](../skills/remotion-best-practices/rules/animations.md) | 动画系统规则 |
| [skills/remotion-best-practices/rules/3d.md](../skills/remotion-best-practices/rules/3d.md) | 3D 内容规则 |
| [skills/remotion-best-practices/rules/audio.md](../skills/remotion-best-practices/rules/audio.md) | 音频处理规则 |
| [skills/remotion-best-practices/rules/charts.md](../skills/remotion-best-practices/rules/charts.md) | 数据可视化规则 |

### Seedance 相关

| 文件 | 功能 |
|------|------|
| [skills/seedance2-skill/SKILL.md](../skills/seedance2-skill/SKILL.md) | Seedance 2.0 AI 视频生成 |

### PPT Generator 相关

| 文件 | 功能 |
|------|------|
| [skills/ppt-generator/SKILL.md](../skills/ppt-generator/SKILL.md) | PPT 幻灯片视频生成 |

### Hyperframes 相关

| 文件 | 功能 |
|------|------|
| [skills/hyperframes-pipeline/SKILL.md](../skills/hyperframes-pipeline/SKILL.md) | Hyperframes 流水线集成 |
| [skills/hyperframes-core/scripts/hf_cli_wrapper.py](../skills/hyperframes-core/scripts/hf_cli_wrapper.py) | Python CLI 封装 |
| [skills/hyperframes-pipeline/prompts/pipeline-guide.md](../skills/hyperframes-pipeline/prompts/pipeline-guide.md) | 流水线执行指南 |
| [skills/hyperframes-pipeline/prompts/scene-construction.md](../skills/hyperframes-pipeline/prompts/scene-construction.md) | 场景构建规范 |

### 发布相关

| 文件 | 功能 |
|------|------|
| [skills/tiktok-ads/SKILL.md](../skills/tiktok-ads/SKILL.md) | TikTok 广告投放 |
| [skills/youtube-ads/SKILL.md](../skills/youtube-ads/SKILL.md) | YouTube 广告投放 |
| [skills/video-marketing/SKILL.md](../skills/video-marketing/SKILL.md) | 视频营销策略 |

---

## 🔗 协同关系

- **与35-02社媒运营**：视频内容发布协同
- **与13-01设计师**：视频设计素材协同
- **与07记录师**：视频脚本撰写协同
- **与28-01文案策划**：视频文案协同
- **与35-01数字营销**：视频广告投放协同

---

## 💡 价值承诺

| 指标 | 传统方式 | 双引擎模式 | 提升 |
|------|---------|-----------|------|
| **视频制作效率** | 手动剪辑 | 自动化生成 | **+300%** |
| **视频质量一致性** | 依赖剪辑师 | 代码精确控制 | **+200%** |
| **批量生成能力** | 单个制作 | 参数化批量 | **质的飞跃** |
| **云渲染速度** | 实时渲染 | Lambda 并行 | **100x 加速** |
| **创意视频生成** | 高成本 | AI 快速生成 | **成本-80%** |

---

**💡 核心理念：短视频编导的关键是选择正确的引擎（Remotion精确控制 vs Seedance AI创意）+ 自动化工作流 + 云渲染加速，实现高质量视频内容的规模化生产。**

---

**版本**: v5.0（Remotion + Seedance + MagiHuman + Hyperframes 四引擎版）
**最后更新**: 2026-04-18
**所属部门**: 运营中心 - 数字营销部

---

## 🔗 阶段 42 协同 · dsh-computer-use V1.0

> **协同点**:35-05 在 macOS 上控制 Final Cut Pro / Premiere Pro / CapCut Mac 等剪辑 app 完成镜头脚本实操。

### 触发条件

| 场景 | 工具链 |
|------|--------|
| 把素材拖到 FCP 时间线 | `computer_observe` → `computer_drag`(timeline position) |
| 切片段 | `computer_observe` → `computer_press_key`(cmd+b) |
| 调整音量 | `computer_observe` → `computer_set_value`(slider) |
| 导出 | `computer_perform_action`("Export" button AXPress) |

### 剪辑 app 控制速查

| 平台 | dsh-computer-use 适用? |
|------|---------------------|
| Final Cut Pro (macOS) | ✅ `computer_drag` 时间线 · `computer_press_key` cmd+b |
| Adobe Premiere Pro (macOS) | ✅ 同上 |
| CapCut for Mac | ✅ 同上 |
| DaVinci Resolve (macOS) | ✅ 同上 |

### DON'T

- 导出视频是个长时间操作,务必 `computer_wait`(text:"Export Complete")而不是直接关 app
- 不要在导出过程中切到其他 app —— `targetHandle` 会失效
- 不要试图绕过 AppleScript / JXA 限制(Computer Use 不接 AppleScript)

### 当前主机状态

- 主机: **Windows**(2026-08-23)→ `COMPUTER_UNSUPPORTED_PLATFORM`
- 等迁 macOS 14+ 后即可使用

### 相关链接

- [[../skills/dsh-computer-use/SKILL.md]] · dsh-computer-use 主 SKILL.md(L6 节)
- [[../skills/dsh-computer-use/references/agent-coordination.md]] · 5 类天龙 Agent 协同接入点
- [[../memory/dsh-computer-use-integration.md]] · 阶段 42 主题文件