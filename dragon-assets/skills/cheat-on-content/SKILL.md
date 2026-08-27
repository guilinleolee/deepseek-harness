---
license: UNKNOWN
triggers: ["cheat on content", "Cheat on Content — 内容校准量化系统"]
---
# Cheat on Content — 内容校准量化系统

> 把每一条内容变成可校准的实验。通过打分、盲预测、发布、T+3天复盘循环，帮助建立**只属于自己的爆款公式**。

## L0: 一句话描述 (≤15字)
内容判断量化进化系统

## L1: 使用场景 (50-100字)
适用于社媒运营、短视频创作、文案策划等需要判断内容质量并持续优化场景。通过量化评分替代主观直觉，通过盲预测防止自欺，通过T+3d复盘实现公式进化。

## L2: 详细文档

### 三条铁律（防自欺机制）

```
1. 盲预测 (Blind Prediction)
   → 预测必须在看数据前写完，写完就不可改
   → 防止"事后诸葛亮"偏差

2. Bump = 全量重打分 (Bump = Full Re-Score)
   → 升级 rubric 必须用新公式重判所有历史样本
   → ≥4/5 样本排名匹配实际数据才放行，否则拒绝升级
   → 防止自我欺骗的"公式迭代"

3. Rubric 是工作台不是博物馆
   → 被数据推翻的观察必须删除
   → Git历史才是档案，不是 markdown 文件
```

### 核心工作流

```
打分 → 盲预测 → 发布 → T+3天复盘 → 进化评分公式
```

### 路由表

| 触发词 | 路由到 | 功能 |
|--------|---------|------|
| "打分这篇" / "打分" | `/cheat-score` | 七维内容打分 |
| "启动预测" / "盲预测" | `/cheat-predict` | 盲预测 + 决策日志 |
| "复盘" / "retro" | `/cheat-retro` | T+3d 数据回收 + 复盘 |
| "升级 rubric" / "bump" | `/cheat-bump` | rubric升级 + 全量验证 |
| "状态" / "status" | `/cheat-status` | buffer状态 + 待复盘追踪 |
| "初始化" / "init" | `/cheat-init` | 初始化 onboarding |
| "趋势" / "trends" | `/cheat-trends` | 趋势源适配 + 热点捕捉 |
| "受众画像" / "persona" | `/cheat-persona` | 受众画像 + 评分锚定 |
| "从X学到了" / "learn-from" | `/cheat-learn-from` | 判断进化 + 偏差分析 |
| "推荐" / "recommend" | `/cheat-recommend` | rubric推荐 + 话题推荐 |
| "迁移" / "migrate" | `/cheat-migrate` | 迁移历史数据到新rubric |
| "拍摄" / "shoot" | `/cheat-shoot` | 视频文件夹 + buffer+1 |
| "发布" / "publish" | `/cheat-publish` | 发布决策 + buffer管理 |

### Opinion Video 七维评分体系

**核心原则**: 平台不同，权重不同。同一内容在不同平台的爆款潜力不同。

#### YouTube 权重配置

| 维度 | 全称 | 权重 | 说明 |
|------|------|------|------|
| ER | Emotional Resonance | ×1.5 | 情感共鸣强度 |
| SR | Social Resonance | ×1.5 | 社交传播潜力 |
| HP | Hook Potential | ×1.0 | 开场钩子吸引力 |
| QL | Quotable Lines | ×1.0 | 金句/名台词密度 |
| NA | Narrativity | ×1.0 | 叙事连贯性 |
| AB | Audience Breadth | ×0.75 | 受众覆盖面 |
| SAT | Satire Depth | ×0.75 | 讽刺深度 |

**YouTube公式**: `(ER×1.5 + SR×1.5 + HP + QL + NA + AB×0.75 + SAT×0.75) / 6.5 × 2.0`

#### 小红书 权重配置

| 维度 | 全称 | 权重 | 说明 |
|------|------|------|------|
| ER | Emotional Resonance | ×1.0 | 情感共鸣强度 |
| SR | Social Resonance | ×2.0 | 收藏驱动，社交传播 |
| HP | Hook Potential | ×1.0 | 开场钩子吸引力 |
| QL | Quotable Lines | ×1.5 | 金句/名台词密度（收藏素材） |
| NA | Narrativity | ×1.0 | 叙事连贯性 |
| AB | Audience Breadth | ×1.5 | 受众覆盖面 |
| SAT | Satire Depth | ×0.5 | 讽刺深度（弱化） |

**小红书公式**: `(ER + SR×2.0 + HP + QL×1.5 + NA + AB×1.5 + SAT×0.5) / 8.5 × 2.0`

#### 抖音 权重配置

| 维度 | 全称 | 权重 | 说明 |
|------|------|------|------|
| ER | Emotional Resonance | ×1.5 | 情感共鸣强度 |
| SR | Social Resonance | ×1.0 | 社交传播潜力 |
| HP | Hook Potential | ×2.0 | 完播优先，开场定生死 |
| QL | Quotable Lines | ×0.5 | 金句密度（弱化） |
| NA | Narrativity | ×1.5 | 叙事连贯性 |
| AB | Audience Breadth | ×1.0 | 受众覆盖面 |
| SAT | Satire Depth | ×0.5 | 讽刺深度（弱化） |

**抖音公式**: `(ER×1.5 + SR + HP×2.0 + QL×0.5 + NA×1.5 + AB + SAT×0.5) / 8.0 × 2.0`

#### Twitter/X 权重配置

| 维度 | 全称 | 权重 | 说明 |
|------|------|------|------|
| ER | Emotional Resonance | ×2.0 | 曝光驱动，情感引爆 |
| SR | Social Resonance | ×1.0 | 社交传播潜力 |
| HP | Hook Potential | ×0.5 | 推文短，钩子权重低 |
| QL | Quotable Lines | ×1.5 | 金句密度（高转发素材） |
| NA | Narrativity | ×1.5 | 叙事连贯性 |
| AB | Audience Breadth | ×1.0 | 受众覆盖面 |
| SAT | Satire Depth | ×1.5 | 讽刺深度（核心武器） |

**Twitter/X公式**: `(ER×2.0 + SR + HP×0.5 + QL×1.5 + NA×1.5 + AB + SAT×1.5) / 9.0 × 2.0`

#### 微博 权重配置

| 维度 | 全称 | 权重 | 说明 |
|------|------|------|------|
| ER | Emotional Resonance | ×2.0 | 热搜驱动，情感引爆 |
| SR | Social Resonance | ×1.5 | 热搜转发潜力 |
| HP | Hook Potential | ×0.5 | 长文本，钩子权重低 |
| QL | Quotable Lines | ×1.0 | 金句密度 |
| NA | Narrativity | ×1.5 | 叙事连贯性 |
| AB | Audience Breadth | ×1.0 | 受众覆盖面 |
| SAT | Satire Depth | ×2.0 | 讽刺深度（热搜引爆器） |

**微博公式**: `(ER×2.0 + SR×1.5 + HP×0.5 + QL + NA×1.5 + AB + SAT×2.0) / 8.5 × 2.0`

### 文件结构

```
cheat-on-content/
├── SKILL.md                      # 技能主文件
├── adapters/                     # 平台适配器
│   ├── youtube-adapter.json      # YouTube评分适配器
│   ├── xiaohongshu-adapter.json # 小红书评分适配器
│   ├── douyin-adapter.json      # 抖音评分适配器
│   ├── twitter-adapter.json     # Twitter/X评分适配器
│   └── weibo-adapter.json      # 微博评分适配器
├── tools/                        # 评分工具
│   ├── diff_pct.py              # 预测偏差百分比计算
│   └── score_curve.py            # 评分曲线可视化
├── platforms/                    # 平台数据
│   ├── youtube/
│   │   ├── video-metrics.json   # YouTube视频指标
│   │   ├── trend-analysis.json  # YouTube趋势分析
│   │   └── competitor-benchmark.json # YouTube竞品基准
│   ├── xiaohongshu/
│   │   └── competitor-benchmark.json # 小红书竞品基准
│   ├── douyin/
│   │   └── trend-analysis.json  # 抖音趋势分析
│   ├── twitter/
│   │   └── sentiment-analysis.json # Twitter情感分析
│   └── weibo/
│       └── hot-search.json     # 微博热搜追踪
├── project/                      # 用户项目
│   ├── scripts/                 # 内容脚本
│   ├── predictions/              # 盲预测日志
│   ├── videos/                  # 视频发布记录
│   ├── samples/                 # 校准样本
│   ├── rubric_notes.md          # 评分rubric
│   ├── WORKFLOW.md             # 工作流文档
│   ├── STATUS.md               # 状态报告
│   └── .cheat-state.json      # 状态文件
└── CHEAT-GUIDE.md             # Cheat-on-Content使用指南
```

### 工具脚本

| 工具 | 功能 |
|------|------|
| `diff_pct.py` | 计算预测与实际偏差百分比 |
| `score_curve.py` | 评分曲线可视化 |

### Hooks

| Hook | 功能 |
|------|------|
| `log-event.sh` | 事件日志记录 |
| `prediction-immutability.sh` | 预测不可变性保护 |
| `session-start.sh` | Session启动检查 |

### 与天龙引擎协同

```
35-02社媒运营 ──┬─ cheat-score ──→ 七维内容打分
               ├─ cheat-predict ──→ 盲预测赌注
               ├─ cheat-retro ──→ T+3d复盘对账
               └─ cheat-bump ──→ rubric进化升级

35-05短视频编导 ──┬─ cheat-shoot ──→ 视频文件夹创建
                 └─ cheat-publish ──→ 发布决策

28-01文案策划 ──┬─ cheat-score ──→ 文案七维评分
               └─ cheat-learn-from ──→ 判断进化

04验证师 ──┬─ cheat-score-blind ──→ 盲评分验证
          └─ cheat-bump ──→ 升级刹车验证
```

## 安装命令

```bash
# 克隆仓库
git clone https://github.com/XBuilderLAB/cheat-on-content.git
cd cheat-on-content
bash install.sh

# 天龙引擎技能链接
cd ~/.claude/skills
ln -s cheat-on-content/skills/* cheat-on-content/
```

## 天龙引擎集成版本

### 变更日志

| 版本 | 日期 | 变更类型 | 描述 |
|------|------|---------|------|
| **V11.22** | 2026-05-25 | 新增 | **五平台适配器集成**：统一评分公式 → 五平台独立权重矩阵 + 评分公式（YouTube HP×2.0完播驱动 / 小红书 SR×2.0收藏驱动 / 抖音 HP×2.0完播优先 / Twitter ER×2.0曝光驱动 / 微博 ER×2.0热搜驱动） |
| **V11.22** | 2026-05-25 | 新增 | **扩展文件结构**：`project/` → `adapters/`(5平台适配器) + `tools/`(2脚本) + `platforms/`(5平台数据) + `project/` + `CHEAT-GUIDE.md` |
| **V11.22** | 2026-05-25 | 新增 | **五平台独立适配器**：统一 rubric → 5平台专属适配器（youtube-adapter / xiaohongshu-adapter / douyin-adapter / twitter-adapter / weibo-adapter） |
| **V8.91** | 2026-04-11 | 初始 | cheat-on-content 核心技能集成 |

### 天龙引擎协同链路

```
35-02社媒运营 ──┬─ cheat-score ──→ 七维内容打分
               ├─ cheat-predict ──→ 盲预测赌注
               ├─ cheat-retro ──→ T+3d复盘对账
               └─ cheat-bump ──→ rubric进化升级

35-05短视频编导 ──┬─ cheat-shoot ──→ 视频文件夹创建
                 └─ cheat-publish ──→ 发布决策

28-01文案策划 ──┬─ cheat-score ──→ 文案七维评分
               └─ cheat-learn-from ──→ 判断进化

04验证师 ──┬─ cheat-score-blind ──→ 盲评分验证
          └─ cheat-bump ──→ 升级刹车验证
```

### 来源

- **来源**: XBuilderLAB/cheat-on-content (2.7k Stars, MIT License)
