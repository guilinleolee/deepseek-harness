---
license: UNKNOWN
name: skill-knowledge-comic
description: |
github_repo: anthropics/claude-code
github_hash: ab3ce06c9ac0a6a0405850e642b80b0bb2c9fb25
last_updated: 2026-04-25
source_type: derived
version: 2.0.0
author: 天龙引擎团队 (基于baoyu-skills)
created: 2026-02-28
updated: 2026-03-13
category: design
triggers: ["knowledge comic", "SKILL: Knowledge-Comic"]
---

# SKILL: Knowledge-Comic

知识漫画创作器，将复杂知识转化为易理解的漫画叙事。

## 触发词
- 知识漫画
- comic
- 漫画创作
- 教育漫画
- 科普漫画

## 核心能力

### 维度系统
```
5 Art Styles × 7 Tones × 6 Layouts = 210 种风格组合
```

| 维度 | 数量 | 说明 |
|------|------|------|
| Art Style | 5种 | 视觉艺术风格 |
| Tone | 7种 | 叙述语气 |
| Layout | 6种 | 面板布局 |
| Aspect Ratio | 3种 | 页面宽高比 |

## Art Style - 艺术风格 (5种)

| Style | 描述 | 最佳场景 |
|-------|------|---------|
| `manga` | 日漫风格 | 动漫爱好者、年轻受众 |
| `comic-strip` | 美式连环画 | 报纸风格、幽默教育 |
| `webtoon` | 韩式条漫 | 移动端、竖屏阅读 |
| `chibi` | Q版卡通 | 可爱轻松、全年龄段 |
| `sketch` | 手绘草图 | 即兴教学、笔记风格 |

## Tone - 叙述语气 (7种)

| Tone | 描述 | 最佳场景 |
|-------|------|---------|
| `neutral` | 中性平衡 | 系统学习、知识传授 |
| `warm` | 温馨怀旧 | 个人故事、导师叙述 |
| `dramatic` | 戏剧张力 | 高对比、紧张场景 |
| `romantic` | 浪漫柔和 | 情感故事、美化元素 |
| `energetic` | 活力四射 | 明亮动态、年轻受众 |
| `vintage` | 复古历史 | 1950年代前、古典内容 |
| `action` | 动作激昂 | 速度线、战斗场景 |

## Layout - 布局结构 (6种)

| Layout | 描述 | 最佳场景 |
|--------|------|---------|
| `standard` | 标准四格 | 默认布局、通用场景 |
| `cinematic` | 电影宽屏 | 史诗场景、重要时刻 |
| `dense` | 高密度信息 | 知识密集、教程说明 |
| `splash` | 全页大图 | 封面、关键场景 |
| `mixed` | 混合布局 | 变化节奏、多样内容 |
| `webtoon` | 竖屏条漫 | 移动端、竖屏阅读 |

## Aspect Ratio - 宽高比 (3种)

| Aspect | 描述 | 最佳场景 |
|--------|------|---------|
| `3:4` | 竖屏 | 移动端、社交媒体（默认） |
| `4:3` | 横屏 | 桌面展示、PPT嵌入 |
| `16:9` | 宽屏 | 视频封面、演示文稿 |

## 预设快捷

| Preset | 等价组合 | 特殊规则 |
|--------|----------|---------|
| `--preset ohmsha` | manga + neutral | 视觉隐喻、无说话头像、设备揭秘 |
| `--preset wuxia` | ink-brush + action | 气场效果、武打场面、氛围渲染 |
| `--preset shoujo` | manga + romantic | 装饰元素、眼睛细节、浪漫节拍 |

## 兼容性矩阵

| Art Style | ✓✓ 最佳 | ✓ 可用 | ✗ 避免 |
|-----------|---------|--------|--------|
| ligne-claire | neutral, warm | dramatic, vintage, energetic | romantic, action |
| manga | neutral, romantic, energetic, action | warm, dramatic | vintage |
| realistic | neutral, warm, dramatic, vintage | action | romantic, energetic |
| ink-brush | neutral, dramatic, action, vintage | warm | romantic, energetic |
| chalk | neutral, warm, energetic | vintage | dramatic, action, romantic |

## 使用示例

### 指定单维度
```bash
/knowledge-comic "机器学习基础" --art manga
/knowledge-comic "气候变化" --tone warm
/knowledge-comic "量子力学入门" --layout cinematic
```

### 指定多维度
```bash
/knowledge-comic "量子力学入门" --art sketch --tone dramatic
/knowledge-comic "武侠故事" --preset wuxia
```

### 指定宽高比
```bash
/knowledge-comic "教程内容" --aspect 16:9  # 宽屏，适合视频封面
/knowledge-comic "移动端漫画" --aspect 3:4  # 竖屏，适合手机阅读
```

### 部分工作流选项
```bash
# 仅生成分镜脚本
/knowledge-comic "主题" --storyboard-only

# 生成分镜+提示词，跳过图像
/knowledge-comic "主题" --prompts-only

# 从已有提示词生成图像
/knowledge-comic "主题" --images-only

# 重新生成特定页面
/knowledge-comic "主题" --regenerate 3
/knowledge-comic "主题" --regenerate 2,5,8
```

### 预设组合
```bash
# 科学教程预设
/knowledge-comic "黑洞原理" --preset ohmsha

# 武侠风格预设
/knowledge-comic "太极之道" --preset wuxia

# 少女漫预设
/knowledge-comic "校园故事" --preset shoujo
```

## EXTEND.md 自定义

在 `~/.claude/skills/knowledge-comic/EXTEND.md` 中添加：

```markdown
## Custom Art Styles

### my-custom-art
- description: 我的艺术风格
- style-guide: 风格指导
- best-for: 特定场景

## Custom Tones

### my-custom-tone
- description: 我的语气风格
- voice: 叙述声音
- best-for: 特定内容
```

## 漫画结构模板

### 四格漫画
```
┌─────────┬─────────┐
│ Panel 1 │ Panel 2 │
│  Intro  │ Problem │
├─────────┼─────────┤
│ Panel 3 │ Panel 4 │
│ Solution│ Conclusion│
└─────────┴─────────┘
```

### 条漫 (Webtoon)
```
┌─────────────────┐
│     Panel 1     │
│     Intro       │
├─────────────────┤
│     Panel 2     │
│     Develop     │
├─────────────────┤
│     Panel 3     │
│     Climax      │
├─────────────────┤
│     Panel 4     │
│     Ending      │
└─────────────────┘
```

## 自动推荐逻辑

| 内容信号 | 推荐组合 |
|---------|---------|
| 教程、编程、教育 | **preset ohmsha** |
| 1950年代前、古典 | realistic + vintage |
| 个人故事、导师 | ligne-claire + warm |
| 武侠、功夫 | **preset wuxia** |
| 浪漫、校园 | **preset shoujo** |
| 传记、平衡 | ligne-claire + neutral |

## 输出目录结构

```
comic/{topic-slug}/
├── source-{slug}.{ext}      # 源文件
├── analysis.md              # 内容分析
├── storyboard.md            # 分镜脚本
├── characters/
│   ├── characters.md        # 角色定义
│   └── characters.png       # 角色参考图
├── prompts/
│   └── NN-page-slug.md      # 生成提示词
├── NN-page-slug.png         # 生成的漫画页
└── {topic-slug}.pdf         # 最终合并PDF
```

## 集成功能

### 多后端AI路由器
自动选择最优AI后端生成漫画脚本和图像。

### EXTEND.md机制
支持项目级和用户级两级自定义配置。

## 文件结构

```
knowledge-comic/
├── SKILL.md                 # 技能定义
├── EXTEND.md                # 默认配置
├── dimensional-system.md    # 维度系统详细说明
├── arts/                    # 艺术风格系统
│   ├── art-manga.md
│   ├── art-comic-strip.md
│   └── ...
└── tones/                   # 语气系统
    ├── tone-educational.md
    ├── tone-humorous.md
    └── ...
```

## 最佳实践

1. **内容优先**：先理解知识点核心，再设计叙事
2. **视觉匹配**：根据受众选择合适的艺术风格
3. **语气一致**：保持叙述语气的一致性
4. **分镜设计**：合理规划漫画分镜和节奏
5. **预设优先**：使用预设快速开始，节省时间
6. **兼容性检查**：参考兼容性矩阵避免风格冲突

---

## 版本历史

- **v2.0.0** (2026-03-13) - 合并 baoyu-comic v1.56.1，新增布局系统、预设快捷、兼容性矩阵、部分工作流
- **v1.0.0** (2026-02-28) - 初始版本，5×7=35组合

---

🤖 Generated with [Claude Code](https://github.com/anthropics/claude-code)
