---
license: UNKNOWN
triggers: ["style calibration", "Style Calibration"]
---
# Style Calibration

## L0: 一句话描述 (≤15字)
学习文风，个性化输出

## L1: 使用场景 (50-100字)
适用于07记录师在生成文档、报告、文章时，根据用户历史文风自动校准输出风格。与ARS academic-paper的Style Calibration对齐，解决"AI味"问题，让输出更符合个人写作习惯。融合V8.84 Meta-Prism的AI-Slop检测，形成"文风校准+AI味去除"双保险。

## L2: 详细文档

### 核心原理

Style Calibration通过分析用户的历史文档，学习其独特的写作风格特征，然后在生成新内容时应用这些特征：

```
┌─────────────────────────────────────────────────────────────┐
│              Style Calibration 三阶段流程                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: 风格学习 (Style Learning)                       │
│  ├── 收集用户历史文档（.md/.txt/.docx）                    │
│  ├── 分析词汇偏好、句式结构、段落组织                      │
│  └── 生成风格指纹 (Style Fingerprint)                     │
│                                                             │
│  Phase 2: 风格校准 (Style Calibration)                     │
│  ├── 将风格指纹应用到新内容生成                            │
│  ├── 调整词汇选择、句式长度、语气                          │
│  └── 保持一致性，减少"AI味"                               │
│                                                             │
│  Phase 3: 质量检查 (Quality Check)                        │
│  ├── Meta-Prism AI-Slop检测                                │
│  ├── 与remove-model-cliche协同                             │
│  └── 输出个性化、去AI味的最终内容                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 风格指纹维度

ARS的Style Calibration分析了以下10个维度：

| 维度 | 描述 | 分析指标 |
|------|------|---------|
| **词汇丰富度** | 词汇选择偏好 | 学术词/口语词/技术词比例 |
| **句式长度** | 句子平均长度 | 简单句/复合句比例 |
| **段落结构** | 段落组织方式 | 主题句位置/支持句数量 |
| **语气** | 正式程度 | 1(口语)-5(正式) |
| **主动/被动** | 语态偏好 | 主动句/被动句比例 |
| **连接词** | 过渡词偏好 | 因此/然而/此外等 |
| **论证风格** | 论证方式 | 归纳/演绎/类比 |
| **引用习惯** | 引用方式 | 直接引用/间接引用/无引用 |
| **标题风格** | 标题格式 | 长标题/短标题/问句式 |
| **结尾风格** | 结论表达 | 总结/开放/行动号召 |

### 风格指纹示例

```yaml
# 用户风格指纹示例 (style_fingerprint.yaml)
user_profile:
  name: "default"
  source_docs: 5
  created: 2026-04-10

dimensions:
  vocabulary_richness:
    score: 0.75
    features:
      academic_ratio: 0.4
      technical_ratio: 0.35
      colloquial_ratio: 0.25

  sentence_length:
    score: 0.65
    features:
      avg_length: 18
      simple_ratio: 0.3
      complex_ratio: 0.7

  formality:
    score: 0.8
    features:
      tone: 4  # 1-5, 4=较正式

  voice:
    score: 0.7
    features:
      active_ratio: 0.75
      passive_ratio: 0.25

  connectors:
    score: 0.6
    features:
      preferred: ["因此", "然而", "此外", "综上所述"]
      avoided: ["所以", "但是"]

  argumentation:
    score: 0.8
    features:
      style: "inductive"  # inductive/deductive/analogic

  citation:
    score: 0.5
    features:
      style: "inline"  # inline/superscript/none

  title_style:
    score: 0.7
    features:
      format: "descriptive"  # descriptive/interrogative/short

  conclusion_style:
    score: 0.6
    features:
      type: "summary"  # summary/open/action

# 个性化调整规则
adjustments:
  # 词汇替换规则
  vocabulary_replacements:
    ai_suggested: "解决方案"
    user_preferred: "应对策略"

    ai_suggested: "非常"
    user_preferred: ""  # 删除过度使用的词

  # 句式调整
  sentence_rules:
    max_length: 25  # 用户偏好短句
    prefer_short_paragraph: true

  # 语气调整
  tone_rules:
    remove_hedging: true  # 去除"可能"、"也许"等模糊词
    add_personal_perspective: true
```

### 与Meta-Prism的协同

Style Calibration与V8.84 Meta-Prism AI-Slop检测形成双保险：

```
┌─────────────────────────────────────────────────────────────┐
│          Style Calibration × Meta-Prism 双保险              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  输入内容 → Style Calibration → 去除AI味 → Meta-Prism      │
│             (匹配用户风格)          (9签名检测)            │
│                          ↓                    ↓             │
│                      个性化风格              无AI味           │
│                          ↓                    ↓             │
│                      ┌────────────────────┐               │
│                      │   最终输出          │               │
│                      │  个性化 + 无AI味    │               │
│                      └────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### ARS定义的AI典型模式（需去除）

| 模式 | 识别特征 | 替换建议 |
|------|---------|---------|
| **过度hedging** | "可能"、"也许"、"似乎"过多 | 删除或减少到合理范围 |
| **公式化开头** | "首先"、"其次"、"最后"滥用 | 使用用户习惯的过渡方式 |
| **模板化结尾** | "综上所述"、"总之"固定模式 | 使用用户风格的结尾方式 |
| **空洞形容词** | "非常"、"极其"、"显著"滥用 | 具体数据或删除 |
| **重复强调** | 同一观点多次重复 | 精简到一次明确表达 |
| **被动语态过多** | "被"、"由"开头的句子过多 | 转换为用户偏好的主动语态 |

### 核心命令

```bash
# 风格学习
/style-calibration learn --docs ./my_writing/
style-calibration learn --source github:username/repo

# 风格查看
/style-calibration profile
style-calibration profile --user "custom_profile"

# 风格校准
/style-calibration calibrate "生成一篇关于AI的研究报告"
style-calibration calibrate --input report.md --output personalized.md

# 组合使用（校准+AI味检测）
style-calibration calibrate --input draft.md --check-ai-slop

# 风格对比
style-calibration compare --doc1 user_sample.md --doc2 generated.md

# 更新风格指纹
style-calibration update --approve-iterations 3
```

### 使用流程

#### 首次使用（冷启动）

```bash
# 1. 收集历史文档
[@07记录师] 请收集你的历史文档到 ~/.claude/style-profiles/
# 支持格式: .md, .txt, .docx, .pdf

# 2. 学习风格
/style-calibration learn --docs ~/.claude/style-profiles/

# 3. 生成风格指纹
# 输出到 ~/.claude/style-profiles/default/fingerprint.yaml

# 4. 测试输出
/style-calibration calibrate "写一篇关于云计算的报告"
```

#### 持续优化（热更新）

```bash
# 每次生成后，用户可以：
/style-calibration approve    # 批准，纳入风格学习
/style-calibration reject     # 拒绝，说明原因
/style-calibration edit      # 修改后批准

# 系统自动积累 approved 内容，更新风格指纹
```

### 与天龙引擎协同

| 天龙组件 | Style Calibration协同 | 效果 |
|---------|---------------------|------|
| **07记录师** | 文档生成自动校准 | 个性化+300% |
| **06审查师** | Writing Quality Check融合 | AI味检测+100% |
| **V8.84 Meta-Prism** | 9签名AI-Slop检测 | 双保险 |
| **remove-model-cliche** | AI典型模式去除 | 去AI味 |
| **humanizer-zh** | 中文去AI味 | 中文内容优化 |

### 输出质量评估

```yaml
style_calibration_check:
  dimensions:
    - name: "vocabulary_match"
      threshold: 0.7
      measure: "n-gram overlap with user vocabulary"

    - name: "sentence_structure"
      threshold: 0.6
      measure: "avg sentence length similarity"

    - name: "formality_match"
      threshold: 0.8
      measure: "tone score difference"

    - name: "ai_pattern_score"
      threshold: 0.3  # 越低越好
      measure: "Meta-Prism 9-signature score"

    - name: "style_fingerprint_match"
      threshold: 0.75
      measure: "overall fingerprint similarity"

  pass_criteria: "all dimensions above threshold"
  fail_action: "auto-recalibrate with more user samples"
```

### 预期收益

| 指标 | 融合前 | 融合后 | 提升 |
|------|--------|--------|------|
| **文档个性化** | 通用风格 | 用户风格 | +300% |
| **AI味感知度** | 明显 | 无感知 | -95% |
| **用户满意度** | 基准 | +80% | 质的飞跃 |
| **修订次数** | 3-5次 | 1次 | -80% |
| **文风一致性** | 分散 | 统一 | +200% |

### 技能文件

- 本文件: `skills/style-calibration/SKILL.md`
- 风格学习器: `skills/style-calibration/scripts/style_learner.py`
- 风格校准器: `skills/style-calibration/scripts/style_calibrator.py`
- 风格指纹模板: `skills/style-calibration/templates/fingerprint.yaml`
- AI典型模式: `skills/style-calibration/references/ai_patterns.md`

### 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-10 | 初始集成，基于ARS v3.3 Style Calibration |

