---
license: UNKNOWN
triggers: ["spaced repetition", "间隔重复记忆系统 (Spaced Repetition)"]
---
# 间隔重复记忆系统 (Spaced Repetition)

## L0: 一句话
基于知识缺口的自适应间隔复习，精准巩固学习成果

## L1: 使用场景
- **固化苏格拉底追问链发现的"知识缺口"** ⭐V8.82/V9.0核心
- 记忆技术概念和术语
- 准备技术面试/考试
- 长期知识积累
- 复习巩固学习成果
- 碎片时间复习
- **V9.0新增**: 缺口驱动复习（先发现缺口，再针对性复习）

## L2: 核心原理

### 遗忘曲线与间隔重复

```
┌─────────────────────────────────────────────────────────────┐
│                    遗忘曲线 vs 间隔重复                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  记忆  │  遗忘曲线（无复习）                                 │
│  100% │  ╲                                                 │
│       │    ╲                                                │
│   50% │     ╲________________                               │
│       │         遗忘点                                      │
│    0% │                                                     │
│       └────────────────────────────────→ 时间              │
│                                                             │
│  记忆  │  间隔重复（有复习）                                 │
│  100% │  ╲    ╲    ╲    ╲                                 │
│       │    ╲    ╲    ╲    ╲                                │
│   50% │     ╲____╲____╲____╲                              │
│       │           ↑复习点                                  │
│    0% │                                                     │
│       └────────────────────────────────→ 时间              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### V9.0: GapAdaptiveSM2 算法（缺口自适应）

传统SM-2算法仅根据"回答正确/错误"调整间隔，但V9.0引入**知识缺口优先级**作为核心调节维度：

```
┌─────────────────────────────────────────────────────────────┐
│          V9.0 GapAdaptiveSM2 算法流程                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: 识别缺口等级 (Gap Level)                          │
│  ├── P0: 基础概念混淆（完全忘记/答错）                    │
│  ├── P1: 原理理解缺失（困难想起/部分正确）                 │
│  └── P2: 实战应用不足（良好/简单，但实战卡壳）            │
│                                                             │
│  Step 2: 计算缺口间隔乘数 (Gap Multiplier)                 │
│  ├── P0: gap_mult = 0.5x  (更频繁复习)                  │
│  ├── P1: gap_mult = 1.0x  (标准间隔)                      │
│  └── P2: gap_mult = 1.5x  (延后复习，腾出时间给P0/P1)    │
│                                                             │
│  Step 3: 复合间隔计算                                       │
│  ├── base_interval = 基础间隔（SM-2标准）                   │
│  └── final_interval = base_interval × gap_mult            │
│                                                             │
│  Step 4: 五星奖励系统 (Five-Star Rewards) ⭐V9.0新增      │
│  ├── 通关星⭐: 正确回答 → 标记为"已攻克"                   │
│  ├── 速度星🌟: 响应时间<5秒 → +间隔奖励                     │
│  ├── 坚持星💪: 连续复习30分钟 → +1天额外间隔              │
│  ├── 复习星📚: 按时复习(±1小时) → +间隔奖励               │
│  └── 连续星🔥: 连续N天复习 → ×(1 + N×0.1)                │
└─────────────────────────────────────────────────────────────┘
```

### SM-2 + GapAdaptive 参数

| 复习结果 | 难度系数调整 | 基础间隔 | Gap乘数 | P0实际 | P1实际 | P2实际 |
|---------|-------------|---------|--------|--------|--------|--------|
| 完全忘记 (0) | -0.8 | 1天 | 0.5x | **0.5天** | 1天 | 1.5天 |
| 错误但想起 (1-2) | -0.15 | 1-3天 | 0.5x | **0.5-1.5天** | 1-3天 | 1.5-4.5天 |
| 困难但想起 (3) | 0 | 3-7天 | 1.0x | **1.5-3.5天** | 3-7天 | 4.5-10.5天 |
| 良好 (4) | +0.1 | 7-14天 | 1.0x | **3.5-7天** | 7-14天 | 10.5-21天 |
| 简单 (5) | +0.15 | 14-30天 | 1.5x | **7-15天** | 14-30天 | **21-45天** |

### V9.0 知识缺口优先级策略

```yaml
# ~/.claude/learning/gap-priority-config.yaml

gap_priority_strategy:
  # 调度优先级: P0 > P1 > P2
  # 核心原则: 先攻克缺口，再巩固定已掌握
  priority_order: [P0, P1, P2]

  # 每日复习配额（按缺口等级分配）
  daily_quota:
    P0: 30%      # 基础混淆 → 优先攻克
    P1: 50%      # 原理缺失 → 稳步巩固
    P2: 20%      # 应用不足 → 延后复习

  # 间隔惩罚（答题错误时）
  failure_penalty:
    P0: 0.3     # 错一道P0 → 当天必须重学
    P1: 0.5     # 错一道P1 → 明日复习
    P2: 0.8     # 错一道P2 → 降级为P1处理

  # 升级/降级规则
  level_transitions:
    P0_to_P1: "连续3次正确回答"
    P1_to_P2: "连续5次正确回答"
    P2_to_mastered: "间隔达到60天且正确"
    any_to_P0: "完全忘记或答错"
```

### 五星奖励系统详解

```yaml
five_star_rewards:
  通关星⭐:
    trigger: "正确回答"
    effect: "记录一次成功，积累3次可升级缺口等级"
    visual: "⭐ (金色)"

  速度星🌟:
    trigger: "响应时间 < 5秒"
    effect: "间隔 × 1.2"
    visual: "🌟 (银色)"

  坚持星💪:
    trigger: "单次复习 ≥ 30分钟"
    effect: "额外 +1天间隔"
    daily_limit: 1
    visual: "💪 (紫色)"

  复习星📚:
    trigger: "按时复习(误差 ±1小时)"
    effect: "间隔 × 1.15"
    visual: "📚 (蓝色)"

  连续星🔥:
    trigger: "连续N天完成复习"
    effect: "间隔 × (1 + N × 0.1)"
    cap: 2.0  # 最多翻倍
    visual: "🔥 (橙色)"

# 五星叠加规则
stacking_rules:
  - "三星同得: 速度+按时 → 间隔 × 1.38"
  - "四星同得: 通关+速度+坚持+复习 → 间隔 × 1.66"
  - "五星全得: × 2.0 (封顶)"
```

## L3: 卡片类型

### 1. 基础记忆卡片

```
正面: 什么是JavaScript的闭包？
背面: 闭包是指一个函数能够访问其词法作用域外的变量。
      即使函数在其原始作用域之外执行，它仍然记得创建时的环境。
```

### 2. 费曼转换卡片

```
正面: 用你自己的话解释"RESTful API"
背面: RESTful API就像餐厅的点餐系统：
      - HTTP方法是点餐动作（GET/POST/PUT/DELETE）
      - URL是菜单地址
      - 响应是厨师返回的菜品
      - 无状态就像每桌独立点餐
```

### 3. 类比理解卡片

```
正面: "数据库索引"可以用什么生活比喻？
背面: 想象一本书的目录：
      - 没有目录 = 全表扫描（逐页翻找）
      - 有目录 = 索引查询（直接翻到目标页）
      - 目录越详细 = 索引越精确
```

### 4. 差异对比卡片

```
正面: var、let、const有什么区别？
背面: ┌─────────┬──────────┬─────────┐
      │  关键字  │  作用域  │  可变  │
      ├─────────┼──────────┼─────────┤
      │   var   │  函数级   │   是   │
      ├─────────┼──────────┼─────────┤
      │   let   │   块级    │   是   │
      ├─────────┼──────────┼─────────┤
      │  const  │   块级    │   否   │
      └─────────┴──────────┴─────────┘
```

### 5. 实战应用卡片

```
正面: 什么时候应该使用useMemo？
背面: 使用useMemo当：
      1. 计算成本高（大量数据处理）
      2. 结果被多个子组件依赖
      3. 值作为其他useMemo的依赖项
      ⚠️ 不要过度使用，会增加内存开销
```

### 6. V9.0 缺口驱动态势卡片 ⭐新增

```
正面: 【P0缺口】为什么async/await是Promise的语法糖？
背面: 因为编译器会将其转换为生成器+Promise执行器：
      async function foo() {
        return bar();  // 实际编译为:
      }
      // ↓ 编译后 ↓
      function foo() {
        return new Promise((resolve) => {
          resolve(bar());
        });
      }

      类比：就像快捷方式和原文件的区别，
      你点击快捷方式，系统帮你打开原文件。

标签: [P0缺口, async-await, Promise, 编译原理]
```

```
正面: 【P1缺口】HTTP/2的多路复用和HTTP/1.1的pipeline有什么区别？
背面: ┌────────────────┬──────────────────┬─────────────────┐
      │       特性      │     HTTP/1.1     │     HTTP/2       │
      ├────────────────┼──────────────────┼─────────────────┤
      │  请求方式      │  串行（需排队）  │  并行（可复用） │
      │  队头阻塞      │     有           │     无          │
      │  连接复用      │     无           │     有          │
      │  Header压缩   │     无           │     HPACK       │
      └────────────────┴──────────────────┴─────────────────┘

标签: [P1缺口, HTTP, 网络协议, 性能优化]
```

## L4: 工作流程

### V9.0 缺口驱动复习流程（与V8.82深度整合）

```
┌─────────────────────────────────────────────────────────────┐
│  V9.0 核心学习闭环 ⭐V8.82 → V9.0 升级                      │
│                                                             │
│  同伴辩论发现缺口 → 费曼讲解攻克缺口 → GapAdaptiveSM2巩固  │
│        ↑                                                        │
│        └──────────── 循环迭代 ──────────────────────────┘
└─────────────────────────────────────────────────────────────┘
```

### 完整工作流程（4步）

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: 缺口识别 ⭐V9.0核心                                  │
│                                                             │
│ 来源:                                                      │
│ - 同伴辩论(Convener Protocol) → 发现理解分歧                 │
│ - 费曼讲解(feynman-technique) → 发现解释卡壳点              │
│ - 实战应用 → 发现无法迁移的知识                            │
│                                                             │
│ 识别规则:                                                  │
│ - 完全忘记 = P0                                             │
│ - 困难想起 = P1                                             │
│ - 良好/简单但实战卡 = P2                                    │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: 卡片生成（基于缺口）                                │
│                                                             │
│ 生成规则:                                                  │
│ - 每张卡片标注缺口等级 (P0/P1/P2)                          │
│ - P0优先 → 立即生成                                       │
│ - P1 → 当日内生成                                         │
│ - P2 → 批量生成，延后复习                                  │
│                                                             │
│ 卡片格式增强:                                              │
│ - 新增gap_level字段（P0/P1/P2）                            │
│ - 新增discovery_source字段（socratic/feynman/practice）     │
│ - 新增five_star字段（通关/速度/坚持/复习/连续）           │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: GapAdaptiveSM2调度 ⭐V9.0核心                       │
│                                                             │
│ 调度规则:                                                  │
│ - P0先于P1先于P2                                          │
│ - 每日配额: P0=30%, P1=50%, P2=20%                         │
│ - 间隔乘数: P0=0.5x, P1=1.0x, P2=1.5x                      │
│                                                             │
│ 奖励叠加:                                                  │
│ - 五星同得: 间隔最高×2.0                                   │
│ - 连续星: 间隔 × (1 + 连续天数×0.1)                       │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: 复习与迭代                                         │
│                                                             │
│ 复习过程:                                                  │
│ 1. 看到问题 → 尝试回忆                                    │
│ 2. 点击显示答案                                           │
│ 3. 评估难度 (忘记/困难/良好/简单)                         │
│ 4. 评估缺口等级是否变化                                    │
│ 5. 进入下一张                                             │
│                                                             │
│ 迭代规则:                                                  │
│ - P0连续3次正确 → 升级为P1                               │
│ - P1连续5次正确 → 升级为P2                               │
│ - 任何错误 → 降级为P0                                      │
│                                                             │
│ 建议时间: 每天15-30分钟                                    │
└─────────────────────────────────────────────────────────────┘
```

## 核心命令

```bash
# 卡片管理
/间隔 添卡 "什么是闭包" "闭包是..."    # 添加卡片
/间隔 添卡 "async-await是语法糖" "因为..." --gap P0  # 缺口卡片
/间隔 生成 "React"                     # 从主题生成卡片
/间隔 生成 "React" --gap-priority     # 仅生成P0/P1缺口卡片
/间隔 导入 "笔记.md"                   # 从笔记导入
/间隔 导出                              # 导出所有卡片

# 复习
/间隔 复习                              # 开始今日复习
/间隔 复习 --gap-first                 # 缺口优先复习
/间隔 快速复习 "React"                  # 复习特定主题
/间隔 统计                              # 查看统计
/间隔 缺口统计                          # 查看P0/P1/P2分布

# 维护
/间隔 待复习                            # 查看待复习数量
/间隔 待复习 --gap                      # 查看各等级待复习
/间隔 清除 100天                       # 清除100天未复习的卡片
/间隔 标签 管理                        # 管理标签
/间隔 升级 P0 --card-id card_001     # 手动升级缺口等级
```

### V9.0 新增命令

```bash
# 缺口管理
/间隔 缺口列表                          # 列出所有P0/P1/P2缺口
/间隔 缺口转移 P0 --from socratic     # 转移来源为苏格拉底的P0缺口
/间隔 缺口分析                          # 分析缺口分布和趋势

# 五星查询
/间隔 五星统计                          # 查看五星获得情况
/间隔 五星排行                          # 连续星、通关星排行

# 学习闭环
/间隔 闭环状态                          # 查看同伴辩论→费曼→间隔重复状态
```

## 卡片存储格式

### V9.0 JSON格式

```json
{
  "id": "card_001",
  "deck": "JavaScript",
  "tags": ["闭包", "核心概念", "面试高频"],
  "gap_level": "P1",
  "gap_tags": ["P1缺口", "原理理解缺失"],
  "discovery_source": "feynman",
  "front": "什么是JavaScript的闭包？",
  "back": "闭包是指函数能够记住并访问其创建时的词法作用域。\n\n类比：就像一个有记忆的机器人，\n即使被带到不同的地方，\n它还记得当初被创造时的环境。",
  "difficulty": "medium",
  "ease_factor": 2.5,
  "interval": 7,
  "repetitions": 3,
  "gap_multiplier": 1.0,
  "next_review": "2026-04-10",
  "created": "2026-03-01",
  "last_reviewed": "2026-04-03",
  "five_star": {
    "通关星": 3,
    "速度星": 2,
    "坚持星": 1,
    "复习星": 5,
    "连续星": 7
  },
  "consecutive_correct": 3,
  "total_reviews": 10,
  "total_correct": 8
}
```

### 存储位置

```
~/.claude/learning/
├── cards/
│   ├── all_cards.json              # 所有卡片（含gap_level）
│   ├── gap_p0.json                 # P0缺口卡片
│   ├── gap_p1.json                 # P1缺口卡片
│   ├── gap_p2.json                 # P2缺口卡片
│   ├── decks/
│   │   ├── JavaScript.json
│   │   ├── React.json
│   │   └── TypeScript.json
│   ├── reviews/
│   │   ├── 2026-04-03.json        # 今日复习记录（含五星）
│   │   └── 2026-04-02.json
│   └── stats.json                  # 统计数据（含五星统计）
├── five_star/
│   ├── daily.json                  # 每日五星记录
│   ├── weekly.json                 # 每周五星汇总
│   └── achievements.json            # 五星成就
└── anki_export/
    └── spaced_repetition.apkg      # Anki可导入格式
```

## 与Anki同步

### 导出到Anki

```bash
# 导出为Anki可读的CSV格式
python ~/.claude/skills/spaced-repetition/scripts/export_anki.py \
  --deck JavaScript \
  --output ~/.claude/learning/anki_export/js_cards.csv

# V9.0: 仅导出缺口卡片
python ~/.claude/skills/spaced-repetition/scripts/export_anki.py \
  --deck JavaScript \
  --gap-only \
  --gap-levels P0,P1 \
  --output ~/.claude/learning/anki_export/js_gap_cards.csv

# 导入到Anki Desktop
# File → Import → 选择csv文件
```

### CSV格式（含缺口等级）

```csv
front,back,tags,gap_level,gap_tags
"什么是闭包？","闭包是指函数能访问其词法作用域外的变量。","JavaScript;核心概念","P1","P1缺口;原理理解"
"async-await是语法糖？","因为会被编译为生成器+Promise执行器。","JavaScript;异步","P0","P0缺口;基础概念混淆"
```

## 学习师协同（V9.0完整闭环）

### V9.0 三阶段学习闭环

```
┌─────────────────────────────────────────────────────────────┐
│           V9.0 核心学习闭环 ⭐V8.82 → V9.0 升级                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Phase 1: 同伴辩论 → 发现缺口                       │  │
│  │ (Convener Protocol V8.95)                          │  │
│  │         ↓                                          │  │
│  │  多个视角辩论 → 识别理解分歧点                     │  │
│  │  输出: 知识缺口列表 (P0/P1/P2)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Phase 2: 费曼讲解 → 攻克缺口                       │  │
│  │ (feynman-technique V8.82)                           │  │
│  │         ↓                                          │  │
│  │  用简单语言解释 → 发现卡壳点                        │  │
│  │  输出: 费曼讲解内容 + 新发现的缺口                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Phase 3: GapAdaptiveSM2 → 巩固成果                 │  │
│  │ (spaced-repetition V9.0) ⭐本Skill                  │  │
│  │         ↓                                          │  │
│  │  基于缺口等级调度 → 精准复习                        │  │
│  │  输出: 掌握度提升 + 五星奖励                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                  │
│                         ↺                                 │
└─────────────────────────────────────────────────────────────┘
```

### 自动生成卡片流程（V9.0增强）

```
┌─────────────────────────────────────────────────────────────┐
│ feyman-technique (费曼讲解 V8.82)                           │
│         ↓                                                   │
│         生成费曼讲解内容                                      │
│         ↓                                                   │
│         识别知识缺口 (P0/P1/P2)                             │
│         ↓                                                   │
│ spaced-repetition (间隔重复 V9.0)                           │
│         ↓                                                   │
│    自动提取生成Anki卡片:                                     │
│    - 正面: 费曼讲解的核心问题                                │
│    - 背面: 简化后的解释 + 类比                               │
│    - 标签: 主题 + 概念 + 来源                               │
│    - gap_level: P0/P1/P2 (V9.0新增)                        │
│    - discovery_source: socratic/feynman/practice         │
└─────────────────────────────────────────────────────────────┘
```

### 学习流程整合

```
┌─────────────────────────────────────────────────────────────┐
│                    完整学习工作流 (V9.0)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🍅 番茄钟学习 (pomodoro-timer)                             │
│         ↓                                                 │
│  💬 同伴辩论 (Convener Protocol) → 发现P0/P1/P2缺口          │
│         ↓                                                 │
│  📝 费曼讲解 (feynman-technique) → 攻克缺口                 │
│         ↓                                                 │
│  🃏 生成Anki卡片 (spaced-repetition V9.0)                   │
│         ↓                                                 │
│  📚 每日复习 (GapAdaptiveSM2调度)                           │
│         ↓                                                 │
│  ⭐ 获取五星奖励 (通关/速度/坚持/复习/连续)                │
│         ↓                                                 │
│  📊 掌握度追踪 (gap分析 + 五星统计)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 复习策略

### 每日复习配置（V9.0）

```yaml
# ~/.claude/learning/spaced-repetition-config.yaml

daily_review:
  enabled: true
  target_new: 20        # 每天最多学习新卡片数
  target_review: 100   # 每天复习卡片上限
  max_time: 30         # 单次最长30分钟

# V9.0 缺口优先配置
gap_priority:
  enabled: true
  daily_quota:
    P0: 30%           # 基础混淆 → 优先攻克
    P1: 50%           # 原理缺失 → 稳步巩固
    P2: 20%           # 应用不足 → 延后复习
  force_order: true   # 必须按P0→P1→P2顺序复习

reminder:
  enabled: true
  times: ["09:00", "14:00", "20:00"]
  message: "📚 是时候复习了！今天还有 {count} 张卡片待复习，其中 P0缺口 {p0_count} 张"

five_star:
  enabled: true
  daily_goal:
    通关星: 20
    速度星: 15
    坚持星: 1
    复习星: 20
    连续星: 1

priority_rules:
  # V9.0: 缺口等级优先
  - type: "gap_level"   # P0先于P1先于P2
  - type: "overdue"     # 过期卡片优先
  - type: "failed"      # 之前失败的卡片
  - type: "new"         # 新卡片其次

  # 延后复习
  - type: "mature"      # 熟练卡片延后
    threshold: 30        # 间隔超过30天的
```

### 卡片生命周期（V9.0）

| 阶段 | 名称 | Gap乘数 | 间隔范围 | 升级条件 |
|------|------|---------|---------|---------|
| Stage 1 | P0缺口（基础混淆） | 0.5x | 0.5-3天 | 连续3次正确 |
| Stage 2 | P1缺口（原理缺失） | 1.0x | 3-14天 | 连续5次正确 |
| Stage 3 | P2缺口（应用不足） | 1.5x | 7-30天 | 间隔达60天 |
| Stage 4 | 熟练 | 1.5x | 30-60天 | 极少复习 |
| Stage 5 | 精通 | 2.0x | 90-180天 | 五星累计达标 |

## 统计数据

### 核心指标（V9.0）

```markdown
# 📊 记忆统计: 2026-04-03

## 今日复习
- 🆕 新卡片: 10张
- 🔄 复习卡片: 50张
- ✅ 正确率: 85%
- ⏱️ 用时: 25分钟

## V9.0 缺口分析
- 🔴 P0缺口: 5张 (优先攻克中)
- 🟡 P1缺口: 15张 (稳步巩固中)
- 🟢 P2缺口: 30张 (延后复习中)
- 📈 P0攻克率: 80% (上周70%)

## V9.0 五星统计
- 通关星⭐: 8/20 (今日)
- 速度星🌟: 12/15 (今日)
- 坚持星💪: 1/1 (已达成)
- 复习星📚: 18/20 (今日)
- 连续星🔥: 7天 (连续7天完成复习)
- 🏆 本周五星: 45/50 (90%达成率)

## 本周进展
- 📈 总复习: 280张
- 📊 正确率趋势: 75% → 85%
- 🔥 连续学习: 14天
- 📉 P0缺口趋势: 12 → 5 (减少58%)

## 卡片分布
| 状态 | 数量 | 占比 |
|------|------|------|
| P0缺口 | 30 | 6% |
| P1缺口 | 100 | 20% |
| P2缺口 | 120 | 24% |
| 熟练 | 150 | 30% |
| 精通 | 100 | 20% |

## 掌握度
| 主题 | 卡片数 | P0缺口 | P1缺口 | P2缺口 | 掌握度 |
|------|--------|--------|--------|--------|--------|
| JavaScript | 120 | 10 | 30 | 35 | 65% |
| React | 80 | 8 | 20 | 25 | 45% |
| TypeScript | 50 | 12 | 20 | 10 | 30% |
```

## DSPy Signatures (V9.0) ⭐新增

V9.0为AI行为引入声明式DSPy Signature，让LLM自动适应复习策略：

### 1. GapBasedCardGenerator

```python
import dspy

class GapBasedCardGenerator(dspy.Signature):
    """从费曼讲解内容或同伴辩论中识别知识缺口并生成卡片"""
    feynman_content: str = dspy.InputField(
        desc="费曼讲解内容，包含解释和例子"
    )
    debate_insights: str = dspy.InputField(
        desc="同伴辩论中发现的理解分歧点"
    )
    topic: str = dspy.InputField(
        desc="主题标签，如'JavaScript闭包'"
    )

    # 输出
    cards: list[dict] = dspy.OutputField(
        desc="卡片列表，每张包含: front, back, gap_level(P0/P1/P2), gap_tags"
    )
    gap_summary: str = dspy.OutputField(
        desc="缺口分析摘要，如'发现2个P0缺口，3个P1缺口'"
    )
```

### 2. AdaptiveSM2Scheduler

```python
class AdaptiveSM2Scheduler(dspy.Signature):
    """基于GapAdaptiveSM2算法计算下次复习时间"""
    card_id: str = dspy.InputField(desc="卡片ID")
    current_interval: int = dspy.InputField(desc="当前间隔天数")
    current_ease: float = dspy.InputField(desc="当前难度因子")
    review_result: int = dspy.InputField(
        desc="复习结果0-5: 0忘记/1-2错误/3困难/4良好/5简单"
    )
    gap_level: str = dspy.InputField(
        desc="缺口等级: P0/P1/P2"
    )
    five_star: dict = dspy.InputField(
        desc="当前五星状态: 通关/速度/坚持/复习/连续"
    )

    # 输出
    next_interval: int = dspy.OutputField(
        desc="下次复习间隔天数"
    )
    new_ease_factor: float = dspy.OutputField(
        desc="更新后的难度因子"
    )
    new_gap_level: str = dspy.OutputField(
        desc="可能升级/降级的缺口等级"
    )
    reward_message: str = dspy.OutputField(
        desc="获得的五星奖励说明"
    )
```

### 3. SpacedRepetitionStateMonitor

```python
class SpacedRepetitionStateMonitor(dspy.Signature):
    """监控整体复习状态，生成洞察和改进建议"""
    daily_stats: dict = dspy.InputField(
        desc="今日统计数据: 复习数/正确率/五星/缺口攻克"
    )
    weekly_trend: dict = dspy.InputField(
        desc="本周趋势: 正确率变化/缺口变化/五星达成"
    )
    gap_distribution: dict = dspy.InputField(
        desc="P0/P1/P2缺口分布"
    )

    # 输出
    insights: list[str] = dspy.OutputField(
        desc="3-5条洞察，如'P0攻克率提升15%'"
    )
    warnings: list[str] = dspy.OutputField(
        desc="警告，如'连续3天P0缺口增加'"
    )
    suggestions: list[str] = dspy.OutputField(
        desc="改进建议，如'建议增加每日P0复习配额'"
    )
```

### DSPy调用示例

```python
import dspy

# 配置MiniMax作为后端
minimax = dspy.LM(
    'openai/MiniMax-M2',
    api_key='YOUR_API_KEY',
    base_url='https://api.minimax.chat/v1',
    max_tokens=2048,
)
dspy.configure(lm=minimax)

# 1. 缺口识别 + 卡片生成
card_generator = dspy.ChainOfThought(GapBasedCardGenerator)
result = card_generator(
    feynman_content="闭包是指函数能记住并访问创建时的作用域...",
    debate_insights="辩手A认为闭包只是作用域延伸，辩手B认为闭包是独特机制",
    topic="JavaScript闭包"
)
print(f"生成卡片: {result.cards}")
print(f"缺口摘要: {result.gap_summary}")

# 2. GapAdaptiveSM2调度
scheduler = dspy.ChainOfThought(AdaptiveSM2Scheduler)
review = scheduler(
    card_id="card_001",
    current_interval=7,
    current_ease=2.5,
    review_result=3,  # 困难但想起
    gap_level="P1",
    five_star={"通关星": 5, "速度星": 3, "坚持星": 0, "复习星": 4, "连续星": 3}
)
print(f"下次间隔: {review.next_interval}天")
print(f"缺口等级: {review.new_gap_level}")
print(f"奖励: {review.reward_message}")

# 3. 状态监控
monitor = dspy.ChainOfThought(SpacedRepetitionStateMonitor)
state = monitor(
    daily_stats={"复习数": 50, "正确率": 85, "五星达成": 45},
    weekly_trend={"正确率变化": "+5%", "缺口变化": "-3"},
    gap_distribution={"P0": 30, "P1": 100, "P2": 120}
)
for insight in state.insights:
    print(f"💡 {insight}")
for warning in state.warnings:
    print(f"⚠️ {warning}")
for suggestion in state.suggestions:
    print(f"💡 {suggestion}")
```

## 文件结构

```
skills/spaced-repetition/
├── SKILL.md                          # 本文件 (V9.0)
├── prompts/
│   ├── card-template.md              # 卡片模板
│   ├── anki-export.md                # Anki导出说明
│   ├── review-template.md             # 复习报告模板
│   └── gap-card-generator.md         # 缺口卡片生成模板 ⭐V9.0新增
├── scripts/
│   ├── card_manager.py               # 卡片管理
│   ├── sm2_algorithm.py             # SM-2算法 ⭐V9.0升级为GapAdaptiveSM2
│   ├── gap_adaptive_sm2.py          # GapAdaptiveSM2算法 ⭐V9.0新增
│   ├── five_star_tracker.py         # 五星追踪器 ⭐V9.0新增
│   ├── anki_export.py               # Anki导出
│   └── stats.py                     # 统计生成
├── dspy/
│   ├── gap_based_card_generator.py  # DSPy签名实现 ⭐V9.0新增
│   ├── adaptive_sm2_scheduler.py    # DSPy签名实现 ⭐V9.0新增
│   └── state_monitor.py              # DSPy签名实现 ⭐V9.0新增
└── templates/
    └── card-template.json            # 卡片JSON模板 ⭐V9.0含gap_level
```

## 版本历史

| 版本 | 日期 | 核心更新 |
|------|------|---------|
| **V9.0** | 2026-04-24 | **GapAdaptiveSM2算法 + 五星奖励 + DSPy Signatures**（缺口自适应间隔乘数P0:0.5x/P1:1.0x/P2:1.5x；五星系统通关/速度/坚持/复习/连续；DSPy声明式Signature×3；与V8.82深度整合：同伴辩论→费曼讲解→GapAdaptiveSM2三阶段闭环） |
| **V8.82** | 2026-04-07 | 与DeepTutor深度整合，五步学习闭环 |
| **V8.80** | 2026-04-03 | 学习师岗位集成，SM-2算法 |
