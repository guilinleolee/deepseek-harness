---
license: UNKNOWN
triggers: ["wiki ai slop detector", "Wiki AI味检测器"]
---
# Wiki AI味检测器

检测Wiki笔记中的AI生成内容特征，评估知识质量，防止AI味内容污染知识库。

## 功能

- **AI特征短语检测**: 识别6大类AI特征短语（认知限制、过度确定性、免责声明等）
- **多维质量评估**: 5个维度评分（句式多样性、观点表达、具体细节、结构自然度）
- **等级分类**: A/B/C/D四级评分，量化AI概率
- **健康度监控**: 实时监控知识库整体健康状态
- **历史趋势**: 追踪质量变化趋势

## 目录结构

```
wiki-ai-slop-detector/
├── SKILL.md                    # 本文件
├── prompts/
│   └── ai_taste_prompt.md     # AI味检测评估提示词
└── scripts/
    ├── detector.py             # 检测核心逻辑
    └── dashboard.py           # 仪表盘可视化
```

## 使用方法

### 扫描所有笔记

```bash
python3 ~/.claude/skills/wiki-ai-slop-detector/scripts/detector.py --scan
```

### 检测单条笔记

```bash
python3 ~/.claude/skills/wiki-ai-slop-detector/scripts/detector.py --note "笔记内容"
```

### 批量检测JSON输出

```bash
python3 ~/.claude/skills/wiki-ai-slop-detector/scripts/detector.py --scan --batch --json
```

### 查看仪表盘

```bash
# 完整仪表盘
python3 ~/.claude/skills/wiki-ai-slop-detector/scripts/dashboard.py

# 紧凑模式
python3 ~/.claude/skills/wiki-ai-slop-detector/scripts/dashboard.py --compact

# 历史趋势
python3 ~/.claude/skills/wiki-ai-slop-detector/scripts/dashboard.py --history

# 监听模式（实时监控）
python3 ~/.claude/skills/wiki-ai-slop-detector/scripts/dashboard.py --watch
```

## 评估维度

| 维度 | 分值 | 说明 |
|------|------|------|
| AI特征短语 | 0-4 | 识别AI特有的表达模式 |
| 句式多样性 | 0-3 | 长短句变化、复合句比例 |
| 观点表达 | 0-3 | 第一人称、经验性表达、个人立场 |
| 具体细节 | 0-2 | 数字、代码、链接、时间戳 |
| 结构自然度 | 0-2 | 模板化程度、过渡短语 |

## 等级标准

| 等级 | 分值 | AI概率 | 说明 |
|------|------|--------|------|
| A | 12-14 | <10% | 几乎确定是人类写作 |
| B | 9-11 | 10-40% | 可能是人类写作，少量AI味 |
| C | 5-8 | 40-70% | AI味较重，需要修订 |
| D | 0-4 | >70% | 几乎确定是AI生成 |

## AI特征短语分类

### 认知限制类
```
As an AI, I cannot, I do not have, my knowledge cutoff,
based on my training, I'm not able to, I don't possess
```

### 过度确定性
```
It's important to note, It is worth noting, It should be noted,
it is crucial to, it is essential to, it is vital to
```

### 免责声明
```
Please note that, Keep in mind that, It is important to remember,
you should consult, you may want to consider, it is recommended that
```

### 过度量化
```
in today's rapidly, in the ever-changing, in today's digital age,
increasingly important, plays a crucial role, is of paramount importance
```

### 公式化开头
```
Let me explain, In this article, In this guide, In this post,
In today's world, When it comes to, First and foremost
```

### 公式化结尾
```
I hope this helps, Feel free to, Please let me know,
If you have any questions, Thank you for reading
```

## 健康度计算

```
health_score = 100
  - min(30, D级笔记比例 × 30)
  - min(15, C级笔记比例 × 15)
  - D级笔记数量 × 5
```

| 健康度 | 状态 |
|--------|------|
| ≥80 | 🟢 优秀 |
| 60-79 | 🟡 良好 |
| 40-59 | 🟠 警告 |
| <40 | 🔴 危险 |

## 优化建议

检测到问题时，系统会提供针对性建议：

- 删除或改写AI特征短语
- 添加个人实践经验或观点
- 加入具体案例、数据或代码示例
- 减少公式化结构，增加自然过渡

## 集成到Wiki工作流

### 在Wiki归档后自动检测

```python
from wiki_mempalace_bridge.scripts.auto_sync import WikiMemPalaceBridge

bridge = WikiMemPalaceBridge()

# 归档笔记后自动检测AI味
bridge.auto_archive_and_detect("微服务架构最佳实践")
```

### 与MemPalace复利系统联动

```python
# 高AI味笔记降低复利值
bridge.compound_value *= (1 - ai_probability / 100)

# 手动改进后提升复利值
if improved_score >= 12:
    bridge.compound_value *= 1.1
```

## 适用场景

- Wiki知识库质量维护
- 个人笔记AI味检查
- 团队知识贡献审核
- AI辅助写作内容检测
