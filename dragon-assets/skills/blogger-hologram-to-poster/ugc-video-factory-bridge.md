---
name: ugc-video-factory-bridge
description: 第 10 维 UGC 视频化接入设计 · XHS 爆款封面 → UGC 短视频工业化（35-06 V1.3）
version: 0.1.0
status: DRAFT · 待 ugc-video-factory spec 激活
license: MIT
last_updated: 2026-07-20
parents:
  - blogger-hologram-to-poster V2.2 (XHS 封面 8 风格)
  - 35-06 V1.2 → V1.3 (博主全息 9 维 → 第 10 维 UGC 视频化)
  - generative-media-skills V1.0 (ugc-video-factory 空 spec,待 MUAPI_API_KEY)
---

# UGC Video Factory Bridge · 第 10 维接入设计

> **核心**：把 V2.2 XHS 爆款封面 8 套风格**延展到 UGC 短视频**(封面 + 开场 3s + 全片脚本 + 字幕)。
>
> **触发**：博主全息 `dim_10_ugc_video.active = true`（V1.3 新增字段）
>
> **依赖**：ugc-video-factory spec（muapi.ai 视频模型族，待 MUAPI_API_KEY）+ VoxCPM2 TTS

---

## 一、为什么需要第 10 维

### 现有矩阵覆盖

| 资产 | 输出形态 | 维度 |
|------|---------|------|
| V2.0 guizang carousel | 5-6 张静态 PNG | 9 维 |
| V2.2 XHS 8 套封面 | 单张封面 PNG | 8 维 + `#FDFFA7` |
| VoxCPM2 tts | 39 语种音频 | 1 维（声纹）|
| ai-clipping / baoyu-youtube-transcript | 长视频 → 竖版 | 输入型 |
| **❌ UGC 短视频** | **封面 + 3s + 全片** | **第 10 维** |

**缺口**：当前流水线**只能出静态图**,UGC 时代需要"图 + 音 + 文 + 视频"的 4 模态闭环。

### 第 10 维的本质

把 XHS 8 套风格的**视觉锚点**(标题位置、人物动作、构图)→ 转化为**短视频脚本**的对应元素：

| XHS 静态风格 | UGC 短视频对应 | 转换规则 |
|--------------|---------------|---------|
| 主标题（顶部 35-45%）| 开场 3s 大字幕 | 完全沿用 `#FDFFA7` 主色 + 粗黑描边 |
| 人物表情 + 动作 | 0-3s hook 表情 | 表情 ID 直接映射（如 "shock" → 镜头 1 大笑）|
| 绿色勾选清单 | 视频 5-25s 三步要点 | 3 条清单 → 3 段画面字幕 |
| 箭头 / emoji 装饰 | 视频转场 + 贴纸 | 静态装饰 → 动态 1-2s 弹出动画 |
| 3:4 竖版 | 9:16 竖版 | 同比例，1:1 复用 |
| 底部彩色条 | 15-30s CTA 横条 | 同 `#FDFFA7` + 文字 |

---

## 二、第 10 维 schema 设计（35-06 V1.3）

```json
{
  "dim_10_ugc_video": {
    "active": true,
    "platform_targets": ["xiaohongshu", "douyin", "tiktok"],
    "duration_sec": 60,
    "aspect_ratio": "9:16",
    "voice_clone": true,
    "ugc_style": "atutun-inspired",
    "subtitles": {
      "enabled": true,
      "main_color": "#FDFFA7",
      "stroke_color": "#000000",
      "position": "bottom-third"
    },
    "hook_seconds": 3,
    "broll_strategy": "auto-generate",
    "music_bgm": null
  }
}
```

**8 套 XHS 风格 → UGC 视频模式映射**：

| XHS 风格 | UGC 视频 hook | 全片结构 | CTA |
|----------|--------------|---------|-----|
| xhs-press-top | 大字幕 + 人物震惊 | 钩子 → 3 要点 → 总结 | 关注引导 |
| xhs-split-impact | 词块轮播 | 钩子 → 词块 1-3 → 结论 | 评论引导 |
| xhs-qa-popular | 问号 + 人物托腮 | 问题 → 3 段解答 → 总结 | 评论引导 |
| xhs-checklist | 3 步骤清单 | 钩子 → 步骤 1-3 → 完成 | 收藏引导 |
| xhs-review-rank | 大数字 + 测评 | 钩子 → 测评维度 1-N → 排名 | 私信引导 |
| xhs-recommend | 人物点赞 + emoji | 钩子 → 推荐 1-3 → 行动 | 链接引导 |
| xhs-collage-intro | 卡片拼贴 | 钩子 → 卡片 1-3 → 上手 | 资源引导 |
| xhs-dark-workflow | Logo 墙 | 钩子 → 工具 1-3 → 流程 | 试用引导 |

---

## 三、模块组成（V1.3 待落盘）

```
dragon-engine/skills/blogger-hologram-to-poster/
├── pipeline/
│   ├── cover-style-selector.mjs          (V2.1 已有)
│   ├── cover-question-bank.mjs           (V2.2 已有)
│   ├── xhs-template-renderer.mjs         (V2.2 已有)
│   ├── to-xhs-publisher.mjs              (V2.2 已有)
│   ├── ugc-script-generator.mjs          (V1.3 新) ← 把 prompt 拆成 [封面/hook/3-要点/CTA]
│   ├── ugc-video-renderer.mjs            (V1.3 新) ← 调 ugc-video-factory + VoxCPM2
│   └── ugc-to-publisher.mjs              (V1.3 新) ← 视频 tasks.jsonl (platforms: douyin/xhs/tiktok)
```

### 1. `ugc-script-generator.mjs`

输入：XHS cover prompt + meta + profile
输出：60s 短视频分镜脚本 JSON

```javascript
export async function generateUGCScript({ coverPrompt, coverMeta, profile, options }) {
  const { style, duration_sec, hook_seconds, ugc_style } = options;
  const voiceStyle = profile.dim_7_writing_style.style_name;  // 老李风 / Lily 风 / khazix 风
  const voiceId = profile.dim_1_timbre;  // 调 VoxCPM2 voice clone

  // 1. 提取封面关键视觉
  const visualAnchors = extractVisualAnchors(coverPrompt);

  // 2. 生成 60s 分镜（按 XHS 8 风格映射）
  const storyboard = match(style)
    .case("xhs-press-top"):       return pressTopStoryboard(visualAnchors, voiceStyle, hook_seconds)
    .case("xhs-checklist"):       return checklistStoryboard(visualAnchors, voiceStyle, hook_seconds)
    // ... 8 套

  return { storyboard, voiceStyle, voiceId, visualAnchors };
}
```

### 2. `ugc-video-renderer.mjs`

输入：分镜 + 博主声纹 ID
输出：60s MP4 + 字幕 SRT

```javascript
export async function renderUGCVideo({ storyboard, voiceId, options }) {
  // 1. 调 VoxCPM2 生成 60s 旁白音频
  const audioPath = await voxcpmSynthesize({
    voice_id: voiceId,
    script: storyboard.narration,
    speed: profile.dim_2_speed.chars_per_sec
  });

  // 2. 调 ugc-video-factory（muapi）生成 60s 视频
  const videoPath = await muapiVideoGen({
    script: storyboard.shots,
    audio: audioPath,
    aspect_ratio: "9:16",
    duration_sec: options.duration_sec
  });

  // 3. 烧字幕（#FDFFA7 主色 + 粗黑描边）
  const finalVideo = await burnSubtitles(videoPath, storyboard.subtitles);

  return { videoPath, audioPath, finalVideo };
}
```

### 3. `ugc-to-publisher.mjs`

输入：MP4 视频 + storyboard JSON
输出：tasks-ugc.jsonl → publisher.py batch → 抖音/小红书/TikTok 入表

```javascript
export async function publishUGCToPublisher({ videoPath, storyboard, profile, meta }) {
  const platforms = ["xiaohongshu", "douyin", "tiktok"];
  const task = {
    blogger_id: profile.blogger_id,
    content_type: "video",
    content_path: videoPath,
    title: storyboard.title,
    description: storyboard.description,
    tags: [...meta.tags, "ugc-v1.3", "xhs_atutun"],
    platforms,
    duration_sec: storyboard.duration_sec,
    aspect_ratio: "9:16",
    has_subtitles: true,
    watermark: true
  };
  // 复用 V2.2 to-xhs-publisher 的 publisher.py 入口
  return writeTasksJsonl({ tasks: [task], outputDir: "output/" });
}
```

---

## 四、与 9 维博主全息的协同

### 输入联动

| 9 维字段 | V1.3 UGC 用法 |
|---------|--------------|
| dim_1_timbre（声纹）| VoxCPM2 voice clone input |
| dim_2_speed（语速）| TTS speed 参数 |
| dim_4_emotion（情绪）| 视频分镜情绪曲线 |
| dim_6_vocabulary.top_words | 文案高频词 |
| dim_7_writing_style.style_name | 视频文案母公式 |
| dim_8_ip_visual.color_palette | 视频色调映射 |
| dim_8_ip_visual.composition | 视频镜头构图继承 |
| **dim_10_ugc_video** ⭐NEW | UGC 短视频总开关 |

### 输出回写

UGC 视频发布成功后,反馈写回 `dim_10_ugc_video.last_published` + views/likes:
```json
{
  "dim_10_ugc_video": {
    "active": true,
    "last_published": "2026-07-20",
    "history": [
      { "video_path": "...", "views": 12345, "likes": 567, "platform": "douyin" }
    ]
  }
}
```

---

## 五、V1.3 集成 checklist

- [ ] `ugc-script-generator.mjs` 落盘（按 8 套 XHS 风格实现 storyboard 生成）
- [ ] `ugc-video-renderer.mjs` 落盘（VoxCPM2 + muapi adapter）
- [ ] `ugc-to-publisher.mjs` 落盘（视频版 tasks.jsonl，复用 publisher.py）
- [ ] `ip_profile_*.json` 3 博主全息 dim_10 字段初始化（active=false 默认）
- [ ] MUAPI_API_KEY 拿到 → 激活 ugc-video-factory spec
- [ ] 端到端 dry-run：laoli_bro_2026 xhs-checklist → 60s MP4 + tasks-ugc.jsonl
- [ ] 单元测试 8 套 × 3 博主 = 24 用例

---

## 六、与现有 skill 的协同矩阵

```
XHS 封面 prompt (V2.2)
       │
       ▼
ugc-script-generator.mjs  ← 把 prompt 拆 60s 分镜
       │
       ├─► VoxCPM2 TTS  ← 旁白音频
       │
       └─► ugc-video-factory (muapi)  ← 视频生成
              │
              ▼
       burn-subtitles (#FDFFA7) ← 字幕烧录
              │
              ▼
       60s MP4 + SRT
              │
              ▼
       ugc-to-publisher.mjs → publisher.py batch
              │
              ▼
       抖音 / 小红书 / TikTok 入表
```

---

## 七、风险与红线

1. **License**：ugc-video-factory 上游 SamurAIGPT/Generative-Media-Skills MIT ✅（阶段 21 已确认）
2. **真人出镜** + VoxCPM2 voice clone → 必须有 IP 授权（laoli_bro_2026 已签 2027-07-03 到期）
3. **`#FDFFA7` 主色硬约束**：字幕烧录必须沿用 XHS palette
4. **3:4 / 9:16 兼容**：封面 3:4 + 视频 9:16 复用同构图（避免人物变形）
5. **dep 风险**：MUAPI_API_KEY 未到位 → V1.3 spec 为空，先写代码骨架

---

## 八、与 ugc-video-factory spec 的接口约定

```javascript
// ugc-video-factory 调用契约（从 muapi 推断，待 KEY 激活后实测）
{
  input: {
    script: [...],         // 分镜数组
    audio_path: "...",     // VoxCPM2 输出音频
    aspect_ratio: "9:16",
    duration_sec: 60,
    style: "atutun-inspired"  // 可选
  },
  output: {
    video_path: "...",
    thumbnail_path: "...",  // 自动抽帧封面
    duration_actual: 60.2,
    metadata: { ... }
  }
}
```

---

## 九、版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V0.1.0 DRAFT | 2026-07-20 | 初版接入设计稿，与 V2.2 XHS 8 套封面 + VoxCPM2 + muapi 协同 |

---

## 十、参考

- V2.2 XHS 8 套模板：[`xhs-template-renderer.mjs`](../skills/blogger-hologram-to-poster/pipeline/xhs-template-renderer.mjs)
- 阶段 21 generative-media-skills：[`generative-media-skills-integration.md`](../../../../memory/generative-media-skills-integration.md) §待激活
- 阶段 16 VoxCPM2：[`voxcpm-integration.md`](../../../../memory/voxcpm-integration.md)
- 35-06 V1.3 第 10 维：MEMORY.md §70