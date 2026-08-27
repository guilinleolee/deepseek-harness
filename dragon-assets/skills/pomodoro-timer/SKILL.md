---
license: UNKNOWN
triggers: ["pomodoro timer", "番茄钟学习管理器 (Pomodoro Timer)"]
---
# 番茄钟学习管理器 (Pomodoro Timer)

## L0: 一句话
基于缺口驱动的自适应番茄钟，精准节奏管理，让每次专注都指向知识缺口的攻克

## L1: 使用场景
- 深度学习新技术（自适应模式匹配缺口级别）
- 准备考试/面试（同伴辩论发现缺口）
- 写作/创作专注时间（费曼讲解产出驱动）
- 需要长时间投入的任务（五星坚持星激励）
- 缺口攻克专项训练（P0→P1→P2逐级突破）

## L2: 核心概念

### V9.0 三阶段学习闭环

```
┌─────────────────────────────────────────────────────────────┐
│                 番茄钟 × 缺口驱动学习闭环                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🍅 番茄钟执行                                               │
│      ↓                                                     │
│  📝 产出记录 + 缺口识别                                     │
│      ↓                                                     │
│  🎓 费曼讲解攻克缺口（feynman-technique）                   │
│      ↓                                                     │
│  📚 GapAdaptiveSM2调度复习（spaced-repetition V9.0）      │
│      ↓                                                     │
│  💬 休息时同伴辩论深化（Convener Protocol V8.95）           │
│                                                             │
│  核心: 每个番茄钟都有明确的缺口目标，不为学而学              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 标准番茄钟

```
┌─────────────────────────────────────────────────────────────┐
│                    番茄钟周期                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🍅 学习25分钟 → 5分钟休息                                │
│        ↑                                                    │
│  [重复4次]                                                 │
│        ↓                                                    │
│  🍅🍅🍅🍅 → 15-30分钟长休息                              │
│                                                             │
│  长周期循环: 4个番茄钟 = 1个长周期                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 变体模式

| 模式 | 学习时间 | 休息时间 | 适用场景 |
|------|---------|---------|---------|
| **标准** | 25min | 5min | 日常学习 |
| **深度工作** | 50min | 10min | 复杂概念 |
| **超深度** | 90min | 20min | 深度钻研 |
| **快速冲刺** | 15min | 3min | 简单任务 |
| **马拉松** | 120min | 30min | 创意写作 |

### V9.0 自适应缺口番茄钟配置

```yaml
# ~/.claude/learning/pomodoro-config.yaml

default_mode: gap_adaptive

# V9.0 自适应缺口番茄钟（根据当前最大缺口级别自动调整）
gap_adaptive:
  enabled: true
  # 缺口级别自动检测，动态调整番茄钟参数
  # P0(基础忘记): 缩短周期，增加频率，降低单次认知负担
  # P1(原理缺失): 标准周期，深度理解
  # P2(实战不足): 延长周期，深度钻研，强化应用

# P0级别配置：基础概念混淆 → 短频快攻
P0_config:
  work: 15           # 缩短至15分钟
  short_break: 3      # 3分钟
  long_break: 10      # 10分钟
  until_long: 3       # 3个短番茄即长休息
  reason: "P0缺口意味着基础不牢，需要高频短时轰炸，防止走神"

# P1级别配置：原理理解缺失 → 标准节奏
P1_config:
  work: 25           # 标准25分钟
  short_break: 5     # 5分钟
  long_break: 15     # 15分钟
  until_long: 4      # 4个标准番茄
  reason: "P1缺口需要深度理解，保持标准节奏，给大脑充分处理时间"

# P2级别配置：实战应用不足 → 长时深潜
P2_config:
  work: 45           # 延长至45分钟
  short_break: 8     # 8分钟
  long_break: 25     # 25分钟
  until_long: 3      # 3个长番茄即可
  reason: "P2缺口需要深度钻研，延长单次专注时间，进入心流状态"

# 缺口级别切换规则
gap_switch_rules:
  # 连续3个番茄钟无困难回忆 → 自动降低难度
  consecutive_easy: 3  # 自动从P0降到P1，或P1降到P2
  # 连续2个番茄钟有P0困难回忆 → 自动提升难度
  consecutive_hard: 2   # 自动从P2提到P1，或P1提到P0
  # 每完成4个番茄钟 → 询问是否需要调整
  check_interval: 4

notifications:
  enabled: true
  sound: true
  work_end: "时间到！休息一下，回顾刚才学了什么"
  break_end: "开始下一个番茄钟"
  gap_reminder: "刚才的番茄钟，你发现了什么缺口？"
  feyman_reminder: "休息后，用一句话向5岁小朋友解释你刚才学的内容"

daily_goal: 10
weekly_goal: 50
```

## L3: 工作流程

### V9.0 番茄钟执行流程

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: 计划 (Plan) ⭐V9.0增强                             │
│                                                             │
│  问题1: 今天要攻克哪些知识缺口？                             │
│  问题2: 每个番茄钟的缺口目标是什么？                        │
│  问题3: 预计需要几个番茄钟攻克这些缺口？                     │
│  问题4: 休息时是否触发同伴辩论？                            │
│                                                             │
│  V9.0新增:                                                  │
│  - 识别当前最大缺口级别（P0/P1/P2）                        │
│  - 选择对应自适应番茄钟配置                                  │
│  - 设定五星目标（坚持星/速度星/通关星）                     │
│                                                             │
│  输出: 今日缺口攻克计划表                                    │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: 执行 (Do)                                         │
│                                                             │
│  🍅 专注学习中...                                          │
│                                                             │
│  规则:                                                     │
│  - 不看手机                                                │
│  - 不刷社交媒体                                            │
│  - 不回非紧急消息                                          │
│  - 专注在攻克当前缺口                                      │
│                                                             │
│  V9.0产出记录:                                            │
│  - 刚才解决了哪个具体的知识缺口？                           │
│  - 费曼自测：我能用一句话解释清楚吗？                      │
│  - 发现了什么新的缺口？                                     │
│                                                             │
│  如遇紧急: 记录中断原因 → 继续或放弃这个番茄钟             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: 记录 (Record)                                      │
│                                                             │
│  每个番茄钟后记录:                                         │
│  - 攻克了哪个缺口？（P0/P1/P2级别）                       │
│  - 费曼讲解是否通过？                                      │
│  - 新发现了什么缺口？                                       │
│  - 获得了几颗星？                                          │
│                                                             │
│  V9.0格式:                                                │
│  [番茄钟N] 18:00-18:25  🍅P1缺口                           │
│  攻克: useEffect依赖数组原理（P1）                          │
│  费曼: ✅ 能向5岁孩子解释                                   │
│  新发现: useCallback和useMemo的使用时机（P0）             │
│  五星: ⭐通关 + 💪坚持 + 📚复习                            │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: 复盘 (Review) ⭐V9.0增强                           │
│                                                             │
│  产出导向复盘四问（禁止问"学了多少小时"）:                   │
│  1. 今天你攻克了哪些知识缺口？（不是学了多久）               │
│  2. 你的GapAdaptiveSM2复习计划是什么？                    │
│  3. 你推翻了或修正了自己之前的什么认知？                    │
│  4. 破局思考：你发现了什么新的缺口或角度？                  │
│                                                             │
│  V9.0新增复盘维度:                                        │
│  - 今日缺口攻克进度（P0/P1/P2完成率）                     │
│  - 五星收集统计（通关星/坚持星/连续星等）                  │
│  - 自适应配置是否需要调整？                                 │
│  - 休息时同伴辩论收获了什么？                               │
│                                                             │
│  每日复盘:                                                │
│  - 今天完成了多少个番茄钟？                                │
│  - 目标达成率？                                           │
│  - 最有效的时间段？                                       │
│  - 五星收获汇总？                                          │
│  - 下次改进点？                                           │
│                                                             │
│  每周复盘:                                                │
│  - 本周番茄钟总数                                        │
│  - 各主题时间分配                                         │
│  - 缺口级别进展（P0→P1→P2）                              │
│  - 五星收集排行榜                                        │
│  - GapAdaptiveSM2复习完成率                               │
└─────────────────────────────────────────────────────────────┘
```

## 核心命令

```bash
# 启动番茄钟
/番茄 "攻克useEffect依赖数组"              # 默认25min标准模式
/番茄 "攻克P0基础缺口" --gap P0          # 15min高频短攻（P0）
/番茄 "攻克P1原理缺口" --gap P1          # 25min标准节奏（P1）
/番茄 "攻克P2实战缺口" --gap P2          # 45min深度钻研（P2）
/番茄 "攻克React原理缺口" --count 6      # 开启6个番茄钟
/番茄 "攻克React原理缺口" --mode deep     # 50min深度模式

# 缺口驱动模式
/番茄 "攻克闭包原理缺口" --auto-gap      # 自动检测缺口级别

# 番茄钟控制
/番茄-暂停                          # 暂停当前番茄钟
/番茄-继续                          # 继续暂停的番茄钟
/番茄-放弃                          # 放弃当前番茄钟
/番茄-完成                          # 提前完成

# 五星追踪
/番茄-五星                          # 查看当前五星收集情况
/番茄-五星 坚持星                   # 查看坚持星进度

# 同伴辩论（休息时触发）
/番茄-辩论                          # 在休息时触发同伴辩论（Convener Protocol）

# 查询状态
/番茄-状态                          # 查看当前状态（含缺口级别）
/番茄-今日                          # 查看今日统计（含五星）
/番茄-本周                          # 查看本周统计（含五星排行）

# 复盘
/番茄-复盘                          # 今日复盘（含缺口进度+五星）
/番茄-周报                          # 本周学习报告（含五星统计）
```

## 番茄钟数据结构

### 日志格式 V9.0

```json
{
  "date": "2026-04-24",
  "current_gap_level": "P1",
  "pomodoros": [
    {
      "id": 1,
      "start": "09:00",
      "end": "09:25",
      "duration": 25,
      "mode": "gap_adaptive",
      "gap_level": "P1",
      "subject": "React Hooks",
      "task": "攻克useEffect依赖数组原理",
      "gap_closed": "依赖数组三规则",
      "new_gap_found": "useCallback使用时机",
      "new_gap_level": "P0",
      "feynman_test": "passed",
      "feynman_attempt": "useEffect像闹钟，依赖数组决定什么时候响",
      "completed": true,
      "interruptions": 0,
      "five_star": {
        "通关星": true,
        "速度星": true,
        "坚持星": true,
        "复习星": false,
        "连续星": false
      },
      "notes": "终于理解了依赖数组的本质——React需要知道什么时候重新执行"
    },
    {
      "id": 2,
      "start": "09:30",
      "end": "09:55",
      "duration": 25,
      "mode": "gap_adaptive",
      "gap_level": "P0",
      "subject": "React Hooks",
      "task": "攻克useCallback使用时机",
      "gap_closed": "useCallback适用场景",
      "new_gap_found": null,
      "new_gap_level": null,
      "feynman_test": "passed",
      "feynman_attempt": "useCallback像给函数穿防护服，防止每次渲染都创建新版本",
      "completed": true,
      "interruptions": 0,
      "five_star": {
        "通关星": true,
        "速度星": true,
        "坚持星": true,
        "复习星": true,
        "连续星": true
      },
      "notes": "5岁孩子能听懂比喻了，说明真的理解了"
    }
  ],
  "summary": {
    "totalPomodoros": 8,
    "totalMinutes": 200,
    "subjectBreakdown": {
      "React Hooks": 6,
      "TypeScript": 2
    },
    "completionRate": 0.83,
    "mostProductiveTime": "09:00-11:00",
    "gap_analysis": {
      "P0_closed": 3,
      "P1_closed": 4,
      "P2_closed": 1,
      "current_max_gap": "P1",
      "next_gap_target": "P2实战应用"
    },
    "five_star_summary": {
      "通关星": 8,
      "速度星": 5,
      "坚持星": 8,
      "复习星": 4,
      "连续星": 2,
      "总计": 27
    }
  }
}
```

### 存储位置

```
~/.claude/learning/
├── pomodoro/
│   ├── daily/
│   │   ├── 2026-04-24.json
│   │   └── 2026-04-23.json
│   ├── weekly/
│   │   ├── 2026-W17.json
│   │   └── 2026-W16.json
│   ├── five_star/
│   │   ├── daily/2026-04-24.json
│   │   └── weekly/2026-W17.json
│   └── stats.json              # 长期统计
├── cards/                      # GapAdaptiveSM2复习卡片
└── gaps/
    ├── P0/                     # P0级别缺口库
    ├── P1/                     # P1级别缺口库
    └── P2/                     # P2级别缺口库
```

## 学习模式配置

### 快速学习模式 (新人适应)

```yaml
work_duration: 15      # 15分钟
short_break: 3         # 3分钟
long_break: 10        # 10分钟
pomodoros_until_long: 3

适用场景:
- 刚开始培养专注习惯
- P0基础缺口攻克（高频短攻）
- 容易分心的任务
```

### 标准学习模式 (推荐)

```yaml
work_duration: 25      # 25分钟
short_break: 5         # 5分钟
long_break: 15        # 15分钟
pomodoros_until_long: 4

适用场景:
- 日常学习
- P1原理缺口攻克
- 技术文档阅读
- 编程练习
```

### 深度学习模式 (高阶)

```yaml
work_duration: 50      # 50分钟
short_break: 10         # 10分钟
long_break: 30          # 30分钟
pomodoros_until_long: 4

适用场景:
- P2实战缺口攻克（深度钻研）
- 复杂算法理解
- 系统设计学习
- 论文研读
```

### 超深度模式 (专家)

```yaml
work_duration: 90      # 90分钟
short_break: 20         # 20分钟
long_break: 45          # 45分钟
pomodoros_until_long: 2

适用场景:
- 专著研读
- 框架源码分析
- 考试冲刺
```

## V9.0 与其他技能协同

### V9.0 完整学习闭环

```
┌─────────────────────────────────────────────────────────────┐
│        天龙引擎 V9.0 学习闭环 (同伴辩论 × 费曼 × 番茄 × SM2)    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  💬 同伴辩论 (Convener Protocol V8.95)                     │
│      发现缺口                                                │
│          ↓                                                   │
│  🎓 费曼讲解 (feynman-technique V9.0)                      │
│      攻克缺口                                                │
│          ↓                                                   │
│  🍅 番茄钟执行 (pomodoro-timer V9.0) ← 当前技能           │
│      精准节奏                                                │
│          ↓                                                   │
│  📚 GapAdaptiveSM2 (spaced-repetition V9.0)              │
│      间隔巩固                                                │
│          ↓                                                   │
│  ⭐ 五星激励                                                │
│      持续动力                                                │
│          ↓                                                   │
│  💬 下一轮同伴辩论...                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 协同流程详解

```
┌─────────────────────────────────────────────────────────────┐
│ pomodoro-timer V9.0 (时间管理 × 缺口驱动)                  │
│         ↓                                                   │
│         ├→ feyman-technique (每个番茄钟后产出费曼讲解)      │
│         │         ↓                                        │
│         │   spaced-repetition (GapAdaptiveSM2生成复习卡片)  │
│         │         ↓                                        │
│         │   Convener Protocol (同伴辩论休息时深化理解)      │
│         │         ↓                                        │
│         │   five-star-tracker (坚持星/通关星自动记录)       │
│         │         ↓                                        │
│         │   obsidian-knowledge-filter (同步到知识库)        │
│         │                                                   │
│         └→ psychology-master (基于专注度调整方法)          │
└─────────────────────────────────────────────────────────────┘
```

### 番茄钟后自动触发 V9.0

| 完成次数 | 自动触发 | 对应五星 |
|---------|---------|---------|
| 1个番茄 | 记录到日志 + 快速费曼自测 | 坚持星 |
| 2个番茄 | 主动回忆：刚才学了什么？能否5岁孩子听懂？ | 速度星 |
| 4个番茄 | GapAdaptiveSM2复习提醒 + 生成今日缺口卡片 | 复习星 |
| 完成主题 | Feynman讲解检验 + 缺口关闭确认 | 通关星 |
| 连续7天 | 五星连续星 + 成就徽章 | 连续星 |

### 休息时同伴辩论触发

| 场景 | 触发Convener Protocol | 辩论主题 |
|------|----------------------|---------|
| 完成1个P0番茄钟后 | 休息3分钟辩论 | "刚才的概念真的理解了吗？反驳自己" |
| 完成1个P1番茄钟后 | 休息5分钟辩论 | "原理背后的本质是什么？举一个反例" |
| 完成1个P2番茄钟后 | 休息8分钟辩论 | "这个知识能迁移到其他领域吗？" |
| 长周期结束 | 休息15分钟辩论 | "今天最大的认知突破是什么？" |

## V9.0 五星激励系统

### 五星定义

```yaml
five_star:
  通关星:
    条件: 完成一个番茄钟，攻克了当前缺口
    规则: 每次完成即获得
    视觉: ⭐

  速度星:
    条件: 番茄钟内提前完成目标（剩余>3分钟）
    规则: 需要gap_closed有实质进展
    视觉: 🌟

  坚持星:
    条件: 连续完成N个番茄钟无中断（N=2时+1星，N=4时+2星）
    规则: 中断则重置连续计数
    视觉: 💪

  复习星:
    条件: 完成GapAdaptiveSM2复习任务
    规则: 每完成一次复习获得
    视觉: 📚

  连续星:
    条件: 连续7天每天完成番茄钟
    规则: 断一天则重新计数
    视觉: 🔥
```

### 五星堆叠规则

```yaml
five_star_stacking:
  # 单次番茄钟最多获得3颗星
  max_per_session: 3
  # 必须有通关星才能获得其他星
  prerequisite: "通关星必须先获得"
  # 速度星和复习星互斥（每次只能选一个）
  mutually_exclusive:
    - 速度星
    - 复习星

  # 五星收集目标（建议值）
  daily_target:
    通关星: 10      # 每天10个番茄钟
    速度星: 5       # 至少一半有提前
    坚持星: 2       # 每天至少一个4连
    复习星: 3       # 复习至少3次
    连续星: 1       # 每天1颗

  # 五星成就（累计解锁）
  achievements:
    学徒: 累计10颗星
    战士: 累计50颗星
    精通: 累计150颗星
    大师: 累计500颗星
    宗师: 累计1000颗星
```

## 学习报告模板

### 每日报告 V9.0

```markdown
# 📊 学习日报: 2026-04-24

## 今日统计
- 🍅 完成番茄钟: 8个 (目标: 10个)
- ⏱️ 总学习时间: 200分钟
- ✅ 完成率: 80%

## 今日五星收集
- ⭐ 通关星: 8/10
- 🌟 速度星: 4/8
- 💪 坚持星: 6 (最高连续4个)
- 📚 复习星: 3/3
- 🔥 连续星: 7天 (🔥🔥🔥)
- 总计: 24/30 ⭐

## 缺口攻克进度
| 缺口级别 | 攻克数 | 剩余数 | 进度 |
|---------|--------|--------|------|
| P0基础 | 3 | 2 | 60% |
| P1原理 | 4 | 3 | 57% |
| P2实战 | 1 | 5 | 17% |

## 时间分布
```
React Hooks      ████████████  50%
TypeScript      ██████        30%
算法            ████          20%
```

## 今日收获
1. ✅ 攻克P1: useEffect依赖数组三规则
2. ✅ 攻克P0: useCallback适用场景
3. 🔲 useMemo和useCallback的使用时机

## 费曼讲解自测
- 通过: 2/2 (100%)
- 用5岁孩子能听懂的话解释:
  - "useEffect像闹钟，依赖数组决定什么时候响"
  - "useCallback像给函数穿防护服"

## 明日计划
- [ ] 攻克P2: 在真实项目中应用useEffect
- [ ] 完成useMemo和useCallback的实战练习
- [ ] 番茄钟目标: 10个
- [ ] 五星目标: 30颗
```

### 周报

```markdown
# 📊 学习周报: 2026-W17

## 本周统计
- 🍅 完成番茄钟: 52个 (上周: 45个)
- ⏱️ 总学习时间: 1300分钟 (21.7小时)
- 📈 增长: +15%
- 五星收集: 168颗 (上周: 142颗)

## 缺口攻克进展
| 主题 | P0完成 | P1完成 | P2完成 | 总进度 |
|------|--------|--------|--------|--------|
| React Hooks | 8/10 | 6/8 | 2/5 | 70% |
| TypeScript | 3/5 | 2/4 | 0/3 | 42% |
| 算法 | 5/5 | 3/5 | 1/4 | 64% |

## 本周五星统计
| 星级 | 本周 | 上周 | 变化 |
|------|------|------|------|
| 通关星 | 52 | 45 | +7 |
| 速度星 | 28 | 22 | +6 |
| 坚持星 | 18 | 15 | +3 |
| 复习星 | 15 | 10 | +5 |
| 连续星 | 7天 | 7天 | → |

## 掌握度进展
| 主题 | 周一 | 周日 | 进展 |
|------|------|------|------|
| React Hooks | 30% | 75% | +45% |
| TypeScript基础 | 20% | 50% | +30% |

## 下周目标
- 🎯 完成React核心概念全部缺口攻克
- 🍅 番茄钟目标: 60个
- ⭐ 五星目标: 200颗
- 📝 产出: 3篇费曼讲解笔记
```

## 专注力追踪

### 分心记录

```markdown
## 今日分心记录

| 时间 | 分心事项 | 持续时间 | 原因 | 缺口影响 |
|------|---------|---------|------|---------|
| 10:15 | 微信消息 | 5min | 工作紧急 | 无（P1缺口已攻克）|
| 14:30 | 刷微博 | 10min | 休息过长 | P2实战进度-1 |

分析: 工作消息处理可以设置固定时间查看
```

### 专注力评分 V9.0

```yaml
# 每日自动计算（V9.0增强版）
专注力评分 = (目标番茄数 - 中断数) / 目标番茄数 * 100
专注力评分_V9 = (通关星数 * 0.4 + 坚持星碎片 / 4) / 目标番茄数 * 100

# 缺口攻克效率（V9.0新增）
缺口攻克效率 = P0_closed * 3 + P1_closed * 2 + P2_closed * 1
# 权重: P0=3分(最优先), P1=2分, P2=1分

# 综合评分
综合学习力 = 专注力评分 * 0.4 + 缺口攻克效率分 * 0.4 + 五星分 * 0.2

评分标准:
90-100: 🌟 卓越专注 + 缺口高效攻克
80-89:  ✅ 良好专注 + 稳步攻克
60-79:  ⚠️ 需要改进 + 缺口攻克缓慢
<60:    🔴 专注力问题 + 缺口停滞
```

## 安装与配置

### 初始化

```bash
# 创建目录结构
mkdir -p ~/.claude/learning/pomodoro/{daily,weekly,five_star}
mkdir -p ~/.claude/learning/gaps/{P0,P1,P2}
mkdir -p ~/.claude/learning/cards

# 配置文件
# ~/.claude/learning/pomodoro-config.yaml
```

### 配置文件 V9.0

```yaml
# ~/.claude/learning/pomodoro-config.yaml

default_mode: gap_adaptive

modes:
  standard:
    work: 25
    short_break: 5
    long_break: 15
    until_long: 4

  gap_adaptive:
    work: 25
    short_break: 5
    long_break: 15
    until_long: 4
    # 自适应缺口级别（见上方详细配置）

  deep:
    work: 50
    short_break: 10
    long_break: 30
    until_long: 4

  quick:
    work: 15
    short_break: 3
    long_break: 10
    until_long: 5

notifications:
  enabled: true
  sound: true
  work_end: "时间到！刚才你攻克了什么缺口？"
  break_end: "开始下一个番茄钟"
  gap_reminder: "刚才的番茄钟，你发现了什么缺口？"
  feyman_reminder: "用一句话向5岁小朋友解释你刚才学的内容"

daily_goal: 10
weekly_goal: 50

# V9.0 五星配置
five_star:
  daily_targets:
    通关星: 10
    速度星: 5
    坚持星: 2
    复习星: 3
    连续星: 1
```

## 脚本文件

```bash
# 番茄钟计时器
skills/pomodoro-timer/scripts/pomodoro.py

# 使用方法
python ~/.claude/skills/pomodoro-timer/scripts/pomodoro.py start --task "攻克useEffect" --mode gap_adaptive --gap P1
python ~/.claude/skills/pomodoro-timer/scripts/pomodoro.py status
python ~/.claude/skills/pomodoro-timer/scripts/pomodoro.py report --period today
python ~/.claude/skills/pomodoro-timer/scripts/pomodoro.py five-star --view daily

# 五星追踪
python ~/.claude/skills/pomodoro-timer/scripts/five_star_tracker.py daily
python ~/.claude/skills/pomodoro-timer/scripts/five_star_tracker.py weekly
python ~/.claude/skills/pomodoro-timer/scripts/five_star_tracker.py achievements

# 缺口分析
python ~/.claude/skills/pomodoro-timer/scripts/gap_analyzer.py --week W17
```

## 文件结构

```
skills/pomodoro-timer/
├── SKILL.md                          # 本文件 (V9.0)
├── prompts/
│   ├── daily-template.md             # 每日报告模板 (V9.0增强)
│   └── weekly-template.md             # 周报模板 (V9.0增强)
├── scripts/
│   ├── pomodoro.py                   # 计时器核心 (V9.0自适应)
│   ├── notify.py                     # 通知脚本
│   ├── report.py                     # 报告生成 (V9.0五星)
│   ├── five_star_tracker.py          # V9.0五星追踪器
│   └── gap_analyzer.py               # V9.0缺口分析器
└── templates/
    └── pomodoro-log.json             # 日志模板 (V9.0含五星)
```

## 版本历史

| 版本 | 日期 | 核心更新 |
|------|------|---------|
| **V9.0** | 2026-04-24 | **Gap-Driven自适应番茄钟集成**：缺口级别自动检测(P0/P1/P2)→自适应配置调整→五星激励系统(通关/速度/坚持/复习/连续五星)→Convener Protocol休息辩论触发→GapAdaptiveSM2复习联动；升级L0(缺口驱动)、L3工作流(V9.0四步增强)、JSON数据格式(五星+缺口级别)、配置文件(自适应模式)、协同流程(V9.0完整闭环)；与feynman-technique(V9.0)×spaced-repetition(V9.0)×Convener Protocol(V8.95)形成完整学习闭环 |
| **V8.82** | 2026-04-07 | 产出导向复盘四问对齐 + 番茄钟后自动触发 |
| **V8.81** | 2026-04-06 | 学习师深度集成 |
| **V8.80** | 2026-04-03 | 初始版本，番茄学习法基础功能 |
