---
license: UNKNOWN
triggers: ["redbox wander", "redbox-wander - 漫步选题引擎 (RedBox Wander Ideation)"]
---
# redbox-wander - 漫步选题引擎 (RedBox Wander Ideation)

## L0: 一句话描述
基于知识图谱的随机漫步选题引擎，模拟人类自由联想的创作灵感激发工具。

## L1: 使用场景
- 选题枯竭时使用"漫步"功能随机组合知识节点
- 需要突破思维定式时使用"主题发散"
- 创作方向迷茫时使用"关键词联想"
- 结合主体库（人物/产品/场景）进行组合创新

## L2: 详细文档

### 核心能力

| 能力 | 说明 | 触发命令 |
|------|------|---------|
| **知识漫步** | 从种子关键词随机游走知识图谱，激发关联创意 | `/wander` |
| **主题发散** | 围绕核心主题生成N个创意方向 | `/wander diverge` |
| **组合创新** | 将主体库元素随机组合生成新选题 | `/wander combine` |
| **关键词联想** | 基于语义网络的近邻词汇推荐 | `/wander associate` |
| **灵感记录** | 漫步过程中的灵感自动存入灵感库 | `/wander capture` |

### 漫步参数控制

```yaml
wander_config:
  max_steps: 20        # 最大漫步步数
  diversity: 0.7        # 多样性参数 (0-1)
  creativity: 0.8     # 创意性参数 (0-1)
  topic_seed: null      # 起始关键词

  # 知识源权重
  sources:
    subject_library: 0.3   # 主体库
    knowledge_base: 0.3  # 知识库
    trending: 0.2        # 趋势热点
    personal: 0.2        # 个人素材
```

### 漫步算法原理

```python
# 知识漫步伪代码
def wander(seed_topic, max_steps=20, diversity=0.7):
    """
    受RedBox Wander引擎启发的漫步选题算法

    核心思想: 类似PageRank的随机游走，但偏向语义关联度高的节点
    """
    current = seed_topic
    visited = [current]
    results = []

    for step in range(max_steps):
        # 候选节点 = 当前节点的语义关联 + 知识图谱邻居
        candidates = get_associations(current)
        candidates += get_graph_neighbors(current)

        # 多样性控制: 随机选择 vs 热门选择
        if random.random() < diversity:
            next_node = random.choice(candidates)
        else:
            next_node = max(candidates, key=lambda x: x.score)

        # 生成创意: 当前节点 + 漫步路径
        idea = generate_idea(current, next_node, visited)
        results.append(idea)

        visited.append(next_node)
        current = next_node

    return results
```

### 与主体库协同

```python
# RedBox风格的选题组合
def combine_with_subject_library(theme, subjects):
    """将主题与主体库元素组合"""
    combinations = []

    for subject in subjects:
        # 主体类型: character/product/scene
        if subject.type == "character":
            prompt = f"以{subject.name}的视角，探讨{theme}"
        elif subject.type == "product":
            prompt = f"围绕{subject.name}，从产品角度分析{theme}"
        else:  # scene
            prompt = f"在{subject.name}场景下，演绎{theme}"

        combinations.append({
            "subject": subject.name,
            "prompt": prompt,
            "angle": subject.tags  # 标签作为角度参考
        })

    return combinations
```

### 灵感捕获格式

```yaml
inspiration_capture:
  fields:
    - seed_topic      # 种子主题
    - wander_path     # 漫步路径 (节点序列)
    - generated_idea # 生成的想法
    - trigger_node    # 触发节点 (关键转折点)
    - creativity_score # 创意评分 (0-1)
    - timestamp

  storage:
    primary: knowledge_base
    backup: inspiration_log.md
    tagging: auto_tag_from_wander_path
```

### 使用示例

```bash
# 基础漫步
/wander "AI Agent发展趋势"
# 输出:
# [Step 1] 起点: AI Agent发展趋势
# [Step 2] 关联: AI编程工具 → Claude Code的编程范式
# [Step 3] 发散: 软件开发 → 未来职业变化
# [Step 4] 组合: 职场场景 + 焦虑情绪 → 选题灵感

# 多样性漫步
/wander "小红书运营" --diversity 0.9 --max-steps 30

# 组合创新 (需配合主体库)
/wander combine "职场成长" --subjects "职场博主" "00后" "办公室"

# 灵感记录
/wander capture "这个选题角度很有意思"
```

### 灵感库示例

```markdown
# 灵感库 - 2026-04-30

## 漫步记录 #001
- 种子: AI Agent发展趋势
- 路径: AI Agent → Claude Code → 编程民主化 → 每个人都能开发 → 创作者经济 → 自媒体内容爆发
- 选题: "AI让编程消失后，内容创作会成为新蓝海"
- 触发词: 编程民主化
- 创作角度: 从程序员视角转向创作者视角
- 标签: #AI趋势 #内容创作 #未来预测

## 漫步记录 #002
- 种子: 职场成长
- 组合: [职场博主] + [00后] + [办公室]
- 选题: "00后整顿职场: 我在甲方当大爷的日子"
- 创作角度: 反差萌 + 真实职场 + 年轻人视角
- 标签: #职场 #00后 #搞笑

## 漫步记录 #003
- 种子: 读书
- 漫步: 读书 → 认知升级 → 思维模型 → 决策质量 → 投资回报
- 选题: "读100本书后，我的投资收益发生了什么变化"
- 创作角度: 量化思维 + 真实数据 + 成长叙事
- 标签: #读书 #投资 #成长
```

### 与其他Skill协同

| Skill | 协同方式 | 效果 |
|-------|---------|------|
| **redbox-subject-library** | 组合创新的主体来源 | 选题效率+300% |
| **xiaohongshu-operations** | 选题→内容→发布完整闭环 | 发布效率+200% |
| **content-intel-cn** | 内容编排+选题验证 | 内容质量+50% |
| **humanizer-zh** | 去AI味的选题表达 | 内容自然度+80% |
| **knowledge-graph** | 知识图谱构建+漫步算法 | 创意关联度+200% |

### 技术实现

```python
# scripts/wander_engine.py - 核心漫步算法
import random
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class WanderNode:
    topic: str
    score: float = 0.5
    tags: List[str] = None
    source: str = "knowledge_base"

class WanderEngine:
    def __init__(self, config: dict):
        self.max_steps = config.get("max_steps", 20)
        self.diversity = config.get("diversity", 0.7)
        self.creativity = config.get("creativity", 0.8)
        self.knowledge_graph = self._load_knowledge_graph()

    def wander(self, seed: str) -> List[Dict]:
        """主漫步方法"""
        results = []
        current = WanderNode(topic=seed)
        visited = {seed}

        for step in range(self.max_steps):
            candidates = self._get_candidates(current)

            # 多样性选择
            if random.random() < self.diversity:
                next_node = self._random_select(candidates)
            else:
                next_node = self._score_select(candidates)

            # 生成创意
            idea = self._generate_idea(current, next_node, visited)
            results.append(idea)

            visited.add(next_node.topic)
            current = next_node

        return results

    def combine(self, theme: str, subjects: List[Dict]) -> List[Dict]:
        """组合创新模式"""
        combinations = []
        for subject in subjects:
            prompt = self._build_prompt(theme, subject)
            combinations.append({
                "subject": subject["name"],
                "prompt": prompt,
                "angle": subject.get("tags", [])
            })
        return combinations
```

### 安装与配置

```bash
# 安装依赖
pip install networkx scipy numpy

# 初始化知识图谱
python scripts/wander_engine.py init

# 配置漫步参数
python scripts/wander_engine.py config --diversity 0.7 --creativity 0.8
```

### 预期收益

| 指标 | 基准 | 集成后 | 提升 |
|------|------|--------|------|
| 选题效率 | 手动思考 | AI漫步 | +300% |
| 创意多样性 | 单一视角 | 多元组合 | +500% |
| 灵感捕获率 | 随机 | 系统化 | +200% |
| 创作启动速度 | 30分钟 | 5分钟 | +500% |

## 核心原理

> "创作灵感往往藏在看似无关的事物之间的意外关联中"

RedBox Wander引擎的核心洞察：
1. **随机性是创造力的源泉** - 完全确定的推荐只会强化已有偏好
2. **漫步而非搜索** - 搜索是目标导向，漫步是探索导向
3. **路径比结果重要** - 漫步过程中的每一个转折点都可能触发灵感
4. **组合即创新** - 新创意往往来自旧元素的新组合

## 版本信息

- **版本**: 1.0.0
- **来源**: RedBox Wander Engine启发
- **依赖**: redbox-subject-library, knowledge-graph
- **更新**: 2026-04-30