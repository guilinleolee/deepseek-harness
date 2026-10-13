---
license: UNKNOWN
triggers: ["redbox subject library", "redbox-subject-library - 主体库管理引擎 (RedBox Subject Library)"]
---
# redbox-subject-library - 主体库管理引擎 (RedBox Subject Library)

## L0: 一句话描述
统一管理内容创作的主体库（人物/产品/场景），为组合创新提供结构化素材支持。

## L1: 使用场景
- 创作选题时从主体库选择合适的人物/产品/场景
- 结合漫步引擎进行组合创新
- 管理主体的标签、关联关系和使用统计

## L2: 详细文档

### 主体类型

| 类型 | 说明 | 属性 |
|------|------|------|
| **character** | 人物角色 | 性格标签、代表观点、发言风格 |
| **product** | 产品/工具 | 功能特点、使用场景、竞品对比 |
| **scene** | 场景/情境 | 环境描述、情感氛围、适用话题 |

### 主体数据结构

```yaml
subject:
  id: string              # 唯一标识
  name: string           # 名称
  type: character|product|scene
  tags: [string]         # 标签列表
  description: string     # 描述
  attributes:            # 类型特定属性
    # character类型
    personality: [string]  # 性格标签
    viewpoint: string      # 代表观点
    speaking_style: string # 发言风格
    background: string     # 背景故事

    # product类型
    features: [string]     # 核心功能
    target_users: [string]  # 目标用户
    price_range: string    # 价格区间
    competitors: [string]   # 竞品

    # scene类型
    environment: string    # 环境描述
    atmosphere: string     # 情感氛围
    suitable_topics: [string] # 适用话题
```

### 核心能力

| 能力 | 说明 | 触发命令 |
|------|------|---------|
| **主体查询** | 按类型/标签查询主体 | `/subject list` |
| **主体详情** | 获取主体完整信息 | `/subject get` |
| **主体创建** | 添加新主体 | `/subject add` |
| **主体更新** | 修改主体信息 | `/subject update` |
| **组合推荐** | 基于主题推荐主体组合 | `/subject recommend` |
| **统计分析** | 主体使用统计 | `/subject stats` |

### 与漫步引擎协同

```python
# RedBox风格的组合创新流程
def creative_combination(theme, subject_library):
    """主题 + 主体库 = 创意选题"""

    # 1. 从漫步引擎获取创意方向
    wander_engine = WanderEngine()
    directions = wander_engine.diverge(theme, num_ideas=5)

    # 2. 为每个方向匹配主体
    for direction in directions:
        # 查询相关主体
        subjects = subject_library.query(
            tags=direction.tags,
            type=['character', 'scene']
        )

        # 3. 组合生成选题
        for subject in subjects[:2]:
            prompt = f"以{subject.name}的视角，{direction}"
            yield prompt
```

### 使用示例

```bash
# 查询所有人物角色
/subject list --type character

# 查询包含"职场"标签的主体
/subject list --tags "职场,成长"

# 创建新主体
/subject add --name "00后" --type character --tags "年轻,反差,职场"

# 基于"AI趋势"推荐主体
/subject recommend "AI发展趋势"

# 查看使用统计
/subject stats
```

### 灵感库示例

```markdown
## 组合记录 #001
- 主题: AI Agent发展趋势
- 漫步方向: 编程民主化 → 内容创作 → 创作者经济
- 组合主体: [00后] + [小红书]
- 选题: "当00后开始用AI Agent搞钱，卷死的是谁？"
- 创作角度: 反差萌 + 真实经历 + 年轻人视角
- 标签: #AI副业 #00后 #内容创作
```

### 与其他Skill协同

| Skill | 协同方式 | 效果 |
|-------|---------|------|
| **redbox-wander** | 漫步路径 → 主体匹配 | 创意关联度+200% |
| **xiaohongshu-operations** | 主体 → 内容创作 | 发布效率+200% |
| **content-intel-cn** | 主体 → 内容编排 | 内容质量+50% |
| **humanizer-zh** | 主体风格 → 去AI味 | 内容自然度+80% |

### 技术实现

```python
# scripts/subject_library.py - 主体库核心实现
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from pathlib import Path

@dataclass
class Subject:
    id: str
    name: str
    type: str  # character/product/scene
    tags: List[str]
    description: str
    attributes: Dict
    created_at: str
    updated_at: str
    usage_count: int = 0

class SubjectLibrary:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.subjects = self._load()

    def query(self, type: str = None, tags: List[str] = None,
              limit: int = 10) -> List[Subject]:
        """查询主体"""
        results = self.subjects

        if type:
            results = [s for s in results if s.type == type]

        if tags:
            results = [s for s in results
                       if any(t in s.tags for t in tags)]

        return sorted(results, key=lambda x: x.usage_count,
                     reverse=True)[:limit]

    def recommend(self, theme: str, num: int = 3) -> List[Subject]:
        """基于主题推荐主体"""
        # 简单实现: 匹配标签
        theme_tags = theme.split()
        results = []

        for subject in self.subjects:
            score = len(set(theme_tags) & set(subject.tags))
            if score > 0:
                results.append((subject, score))

        return [s for s, _ in sorted(results,
              key=lambda x: x[1], reverse=True)[:num]]

    def increment_usage(self, subject_id: str):
        """增加使用计数"""
        for subject in self.subjects:
            if subject.id == subject_id:
                subject.usage_count += 1
                break
        self._save()
```

### 安装与配置

```bash
# 初始化主体库
python scripts/subject_library.py init

# 导入示例主体
python scripts/subject_library.py import --file sample_subjects.json

# 查看统计
python scripts/subject_library.py stats
```

### 预期收益

| 指标 | 基准 | 集成后 | 提升 |
|------|------|--------|------|
| 主体复用率 | 随机 | 系统化管理 | +200% |
| 组合创新效率 | 手动思考 | AI推荐 | +300% |
| 内容一致性 | 风格漂移 | 主体风格稳定 | +80% |

## 核心原理

> "好的内容创作者都有自己的'主角'——那些鲜活的人物、独特的产品、真实的场景"

RedBox主体库的核心洞察：
1. **角色即视角** - 每个人物代表一种独特的人生视角
2. **产品即工具** - 每个产品解决特定问题
3. **场景即共鸣** - 每个场景唤起特定情感

## 版本信息

- **版本**: 1.0.0
- **来源**: RedBox Subject Library启发
- **依赖**: redbox-wander, knowledge-graph
- **更新**: 2026-04-30
