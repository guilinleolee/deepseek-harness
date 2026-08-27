# Presentation Coach

> AI演示教练 - 分析演示文稿内容，提供演讲建议和节奏优化

## 模块定位

本模块帮助用户优化演示文稿的演讲效果，提供内容分析、节奏建议和练习反馈。

## 核心能力

### 1. 内容分析

**评估维度**:

| 维度 | 权重 | 说明 |
|------|------|------|
| 信息密度 | 25% | 每页信息量是否适中 |
| 逻辑清晰度 | 25% | 内容逻辑是否连贯 |
| 重点突出度 | 25% | 核心信息是否突出 |
| 受众适配度 | 25% | 是否适合目标受众 |

### 2. 节奏建议

**演讲节奏评估**:

| 节奏类型 | 每页建议时长 | 适用场景 |
|----------|--------------|----------|
| 慢节奏 | 2-3分钟 | 重点强调、情感高潮 |
| 正常节奏 | 1-2分钟 | 常规内容 |
| 快节奏 | 30秒-1分钟 | 过渡页、背景信息 |

### 3. 过渡语建议

**页面间过渡**:

```markdown
## 过渡语示例

### 从问题到方案
"面对这个挑战，我们提出了..."
"基于以上分析，解决方案是..."
"那么，如何解决这个问题呢？"

### 从数据到结论
"从数据中我们发现..."
"这组数字说明了一个关键点..."
"透过现象看本质，..."

### 从观点到行动
"因此，我们建议..."
"基于这些发现，接下来应该..."
"总结一下，我们的行动计划是..."
```

### 4. 重点强调建议

**强调方式**:

| 强调类型 | 视觉手段 | 口头表达 |
|----------|----------|----------|
| 数据强调 | 放大、颜色 | "关键数字是..." |
| 对比强调 | 前后对比 | "与此相比..." |
| 重复强调 | 反复出现 | "记住这三点..." |
| 停顿强调 | 留白 | [停顿] |

## 分析流程

```python
# 分析流程示例
async def analyze_presentation(pptx_path):
    # 1. 提取内容
    content = extract_slides(pptx_path)

    # 2. 分析密度
    density = analyze_density(content)

    # 3. 评估节奏
    rhythm = evaluate_rhythm(content)

    # 4. 生成建议
    suggestions = generate_suggestions(content, density, rhythm)

    return CoachReport(
        density=density,
        rhythm=rhythm,
        suggestions=suggestions,
        timing=estimate_timing(content)
    )
```

## 报告格式

```markdown
# 演示教练分析报告

## 📊 内容分析

### 信息密度评估
| 页面 | 当前密度 | 建议密度 | 建议 |
|------|----------|----------|------|
| P1 封面 | 低 | - | OK |
| P2 背景 | 中 | 低 | 精简背景信息 |
| P3 核心 | 高 | 中 | 拆分为2页 |

### 逻辑流程
- ✅ 逻辑清晰
- ⚠️ P5-P6 连接较弱
- ❌ P8 与 P7 逻辑冲突

## ⏱️ 时间估算

| 页面 | 建议时长 | 关键词 |
|------|----------|--------|
| P1 封面 | 30秒 | 问候 |
| P2 背景 | 1分钟 | 设定场景 |
| P3 核心 | 2分钟 | 重点强调 |

**总时长**: 约 15-20 分钟

## 💡 优化建议

### 1. 内容优化
- 精简 P2 背景信息
- 拆分 P3 核心内容
- 增强 P7 结论说服力

### 2. 节奏优化
- P4 数据页增加停顿
- P6-P7 添加过渡语
- 结尾页增加号召行动

### 3. 表达技巧
- 数据页："注意这个数字..."
- 结论页："总结来说..."
- QA页："感谢聆听"
```

## 练习模式

### 模拟演讲计时

```python
class PracticeMode:
    """练习模式"""

    def start(self, pptx_path):
        """开始练习"""
        slides = extract_slides(pptx_path)
        return PracticeSession(slides)

    def record(self, slide_index, duration):
        """记录每页用时"""
        self.timings[slide_index] = duration

    def analyze(self):
        """分析练习结果"""
        return {
            "total_time": sum(self.timings.values()),
            "average_per_slide": average(self.timings),
            "slow_slides": identify_slow(self.timings),
            "fast_slides": identify_fast(self.timings),
            "suggestions": generate_practice_suggestions(self.timings)
        }
```

### 反馈指标

| 指标 | 优秀 | 良好 | 需改进 |
|------|------|------|--------|
| 每页平均时长 | 1-2分钟 | 2-3分钟 | >3分钟 |
| 总体时长 | 符合预期 | 略超/略短 | 严重超时 |
| 节奏稳定性 | ±15秒 | ±30秒 | >30秒 |

## 集成说明

### 与 Strategist 集成

```python
async def coach_integration(content):
    # 生成PPT后自动分析
    analysis = await analyze_presentation(content)

    # 生成演讲建议
    coach_report = CoachReport(
        timing=analysis.timing,
        emphasis=analysis.emphasis,
        transition=analysis.transitions
    )

    # 添加到设计规范
    return DesignSpec(
        content=content,
        coach=coach_report
    )
```

## 使用场景

### 场景1: 演讲准备

```bash
/ppt-coach presentation.pptx --mode analyze
```

### 场景2: 模拟练习

```bash
/ppt-coach presentation.pptx --mode practice
```

### 场景3: 改进建议

```bash
/ppt-coach presentation.pptx --mode improve
```

---

**版本**: 1.0
**更新日期**: 2026-08-20
