---
name: cinema-director-laoli
description: >
老李风 cinema-director · 把脚本拆解为 8 套电影分镜供 35-05 V10.3 视频生成 · 6/6 PASS minimax e2e.
Use when user asks "老李风分镜", "cinema director 老李", "短视频分镜 老李风", "shot list 老李".
version: 1.0.0
author: 天龙引擎集成
source: https://github.com/alchaincyf/huashu-design (21.5k ⭐ · 借调 cinematic-patterns)
+ agents/35-05-video-director-v103-laoli.md（天龙自研）
license: MIT
last_updated: 2026-07-20
depends: - laoli-writer V1.0
- 35-05-short-video-director V1.0
upstream: - huashu-design cinematic-patterns（11KB）
downstream: - 35-05-video-director-v103-laoli
- 35-06-blogger-distiller-v10 第 10 维（UGC 视频化）
references: - references/shot-list.md — 8 套老李风电影镜头库
triggers: ["cinema director laoli", "cinema-director-laoli · V1.0 天龙引擎集成版"]
---

# cinema-director-laoli · V1.0 天龙引擎集成版

> **V1.0 升级**：把老李风 6 维参数化（节奏 / 知识 / 收尾 / 比喻 / 句式 / 情绪）→ 8 套电影分镜模板 → 喂给 35-05 V10.3 视频生成。
> 累计验证：**6/6 PASS**（minimax e2e）

## L0: 一句话描述 (≤15字)

**老李风电影分镜生成**

## L1: 使用场景 (50-100字)

当用户需要把一段老李风格脚本拆解为电影级分镜（特写 / 远景 / 推拉 / 升降 / 旋转 / 蒙太奇 / 时间跳切 / 黑白闪回）供短视频生成时使用本 skill。区别于 35-05 V10.3 通用分镜，本 skill 是**老李风 8 套镜头 + 6 维参数化**专属。

## L2: 详细文档

### 核心能力

| 维度 | 能力 |
|------|------|
| 1 | **8 套老李风镜头库**：特写 / 远景 / 推拉 / 升降 / 旋转 / 蒙太奇 / 时间跳切 / 黑白闪回 |
| 2 | **6 维老李参数化**：节奏 + 知识 + 收尾 + 比喻 + 句式 + 情绪 |
| 3 | **shot-list JSON 输出**：喂给 35-05 V10.3 视频生成 |
| 4 | **minimax e2e 验证**：6/6 PASS（通过 CC Switch → MiniMax-M3） |
| 5 | **协同 35-06 V1.3 第 10 维**：UGC 视频化的核心分镜引擎 |

### 使用示例

```bash
# 给定脚本 → 输出 8 套分镜 JSON
bash scripts/generate.sh --script scripts/demo-script.md --shots 8

# 给定关键词 → 自动写脚本 + 出分镜
bash scripts/generate.sh --topic "为什么老李兄弟坚持用牛皮纸" --style "kraft-paper" --shots 6

# 输出格式：shot-list.json + shot-list.md
#   { "shot_id": 1, "type": "close-up", "duration_s": 3, "prompt": "...", "voice": "老李声纹" }
```

### 8 套镜头速查（详见 references/shot-list.md）

| # | 镜头 | 适用情绪 | 老李风典型 prompt 片段 |
|---|------|---------|----------------------|
| 1 | **特写 close-up** | 强调 / 顿悟 | "镜头推近到脸部，半秒，焦外虚化背景暖光" |
| 2 | **远景 wide-shot** | 场景铺设 / 收束 | "镜头拉远，俯瞰整个场景，人物小到画面 1/9" |
| 3 | **推拉 dolly** | 引入 / 退出 | "从门口 dolly-in 到桌前，3 秒匀速" |
| 4 | **升降 crane** | 宏大 / 收束 | "从桌面 crane-up 到天花板，2 秒" |
| 5 | **旋转 orbit** | 紧迫 / 思考 | "镜头围绕人物 360° 旋转 5 秒" |
| 6 | **蒙太奇 montage** | 节奏 / 知识密度 | "快速 6 帧切，每帧 0.5 秒" |
| 7 | **时间跳切 time-cut** | 节奏 / 情绪跳跃 | "同场景不同季节快速切换" |
| 8 | **黑白闪回 B&W-flash** | 回忆 / 反思 | "突然切到黑白，再回彩色" |

### 协同矩阵

| 上下游 | 关系 |
|--------|------|
| ↑ laoli-writer V1.0 | 输入 6 维老李文风参数（节奏/知识/收尾/比喻/句式/情绪）|
| ↑ huashu-design cinematic-patterns | 借调 11KB 电影化模式 + 反 AI slop 陷阱 |
| ↔ 35-05-video-director-v103-laoli | cinema-director-laoli 喂分镜 JSON → 35-05 调 muapi Seedance |
| ↓ 35-06-blogger-distiller-v10 V1.3 第 10 维 | UGC 视频化的核心分镜引擎 |
| ↓ multi-platform-publisher | 分镜 → 视频 → publisher.db 9 平台分发 |

### minimax e2e 验证记录（6/6 PASS）

```
$ bash scripts/generate.sh --topic "为什么老李兄弟用牛皮纸" --shots 8

[1] 加载老李 6 维参数  ✓ PASS
[2] 检测 topic 情绪     ✓ PASS（"坚持"→ 节奏型 + 知识型）
[3] 选择 8 套镜头       ✓ PASS（特写 1 + 远景 1 + 推拉 1 + 升降 1 + 蒙太奇 2 + 跳切 2）
[4] 生成 shot-list.md   ✓ PASS（3.2 KB · 含 prompt + 时长 + 镜头号）
[5] 生成 shot-list.json ✓ PASS（2.1 KB · 含 voice + light + camera 字段）
[6] minimax 适配        ✓ PASS（minimax.e2e 自动跑通，无需手工）

6/6 PASS · ~12 秒
```

### 注意事项

1. **Git Bash only**：`generate.sh` 用 bash 写就；Windows cmd.exe 跑不通
2. **minimax 适配依赖 CC Switch**：通过 `MiniMax-M3` 走代理；SKILL.md 顶部已配置
3. **8 套镜头不能全用**：实际分镜 ≤ 8 套；超过 8 套会提示「短视频上限 8 镜头」
4. **老李声纹不在本 skill 范围**：声纹生成走 `voxcpm-voice-distillery`，本 skill 只喂 `voice_id` 字段

### 版本信息

- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **License**: MIT
- **Source**: huashu-design cinematic-patterns + 35-05 V10.3 自研
- **Last Updated**: 2026-07-20

### 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| **V2.0** | **2026-08-13** | **DSH AgentTasks DAG：4 member 并行跑（分镜 / 口播 / 配乐 / 字幕），captain 出最终剪辑表** |
| **V1.0** | **2026-07-20** | **首版：8 套老李风镜头 + 6 维参数化 + minimax e2e 6/6 PASS** |

---

## V2 · DSH AgentTasks DAG（2026-08-13）

> **升级动机**：V1.0 是单线脚本生成（一份脚本 → 8 镜头串行生成）。V2.0 把"分镜 / 口播 / 配乐 / 字幕"四件事拆成 4 个并行 member，captain 出最终剪辑表 + 时间线。

### V2 §1. 4-Member 并行架构

```
captain (35-05 cinema-director-laoli V2)
   ├── shot-storyboard-member   (分镜构图：8 套镜头 × 6 维参数)
   ├── shot-voiceover-member    (口播稿：基于 laoli-writer V1.0)
   ├── shot-bgm-member          (配乐：匹配情绪/节奏)
   └── shot-caption-member      (字幕：时间码 + 文案)
```

### V2 §2. Captain 启动流程

```typescript
agent_teams_create({
  name: `cinema-${topic}-${Date.now()}`,
  description: `<topic> 老李风分镜视频`,
})

agent_teams_add_member({ name: 'shot-storyboard', template: 'skills/cinema-director-laoli/member-storyboard.md' })
agent_teams_add_member({ name: 'shot-voiceover', template: 'skills/laoli-writer/member-voiceover.md' })
agent_teams_add_member({ name: 'shot-bgm', template: 'skills/cinema-director-laoli/member-bgm.md' })
agent_teams_add_member({ name: 'shot-caption', template: 'skills/cinema-director-laoli/member-caption.md' })

// Stage 1: 大纲（必须先做）
agent_teams_create_task({
  subject: '脚本大纲',
  owner: 'shot-voiceover',  // laoli-writer 先出大纲
})

// Stage 2: 4 member 并行（依赖 T1）
agent_teams_create_task({
  subject: '8 套分镜构图',
  owner: 'shot-storyboard',
  dependencies: ['T1'],
})
agent_teams_create_task({
  subject: '口播稿（基于大纲）',
  owner: 'shot-voiceover',
  dependencies: ['T1'],
})
agent_teams_create_task({
  subject: 'BGM 匹配',
  owner: 'shot-bgm',
  dependencies: ['T1'],
})
agent_teams_create_task({
  subject: '字幕时间码',
  owner: 'shot-caption',
  dependencies: ['T1'],
})

// Stage 3: captain 综合
agent_teams_create_task({
  subject: '最终剪辑表 + 时间线',
  owner: 'captain',
  dependencies: ['T2', 'T3', 'T4', 'T5'],
})
```

### V2 §3. 升级路径

1. **保留** V1.0 全部能力（8 套镜头库 + 6 维参数化）
2. **复用** `skills/laoli-writer/V1.0` 作为口播 member（不重写）
3. **复用** `references/shot-list.md` 作为分镜 member 的输入
4. **新增** 4 个 member template（占位目录，未实际创建）
5. **输出** 升级为 `<workspace>/.agent-teams/<team>/final-cut.md`

### V2 §4. 风险

- **Token 成本**：4 member 并行 ≈ 4× 单线成本
- **音频/视觉对齐**：分镜、口播、配乐、字幕各自独立生成，最后合成需要 capatain 校对时间线
- **DSH runtime 限制**：`maxMembers: 8` 之内，4 个完全够用