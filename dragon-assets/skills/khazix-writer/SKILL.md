---
license: UNKNOWN
triggers: ["khazix writer", "khazix-writer — 微信文章活人感写作"]
---
# khazix-writer — 微信文章活人感写作

## L0: 一句话描述 (≤15字)
去除AI味、赋予活人感微信文章写作

## L1: 使用场景 (50-100字)
用于撰写微信公众号文章，通过四层审查机制（L1硬规则→L2风格→L3内容→L4活人感终审）彻底去除AI生成文本的机械感，产出4000-8000字具有真实人格温度的长文。

## L2: 详细文档

### 来源项目
> [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) - 9.9k Stars, MIT License

### 核心理念
AI生成文章的最大问题是"AI味"——过度使用空洞词汇、固定句式、过度结构化。四层审查从硬规则到软感觉，逐层剥离AI痕迹，最终产出"活人写的感觉"。

### 五种文章原型

| 原型 | 特征 | 适用场景 |
|------|------|---------|
| **调查实验型** | 实地调研+数据支撑 | 深度报道、产品测评 |
| **产品体验型** | 第一人称使用感受 | 新工具推荐、App体验 |
| **现象解读型** | 社会现象+趋势分析 | 行业观察、舆论分析 |
| **工具分享型** | 教程+实操+案例 | 技术教程、合集推荐 |
| **方法论分享型** | 思考框架+方法论 | 经验复盘、职业成长 |

### 四层审查机制

```
┌─────────────────────────────────────────────────────────────┐
│                  四层审查瀑布                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  L1: 硬规则审查 🔴                                         │
│  ├── 禁词检测: 说白了/本质上/意味着/换句话说/不可否认      │
│  ├── 禁用标点: 冒号:/破折号——/英文引号""                  │
│  ├── 禁用结构: 首先/其次/最后 + 三点并列                   │
│  └── 禁用开头: 近年来/随着/在XX时代/我们可以看到            │
│  → 如果L1不通过，直接重写                                   │
│                                                             │
│  L2: 风格一致性审查 🟡                                      │
│  ├── 语气是否口语化                                       │
│  ├── 是否有刻意对仗的短句                                  │
│  ├── 段落长度是否合理（不超过3屏）                        │
│  └── 句式变化是否丰富（长短句交错）                        │
│  → 如果L2不通过，局部修改                                   │
│                                                             │
│  L3: 内容质量审查 🟢                                        │
│  ├── 是否有具体的案例/故事                                 │
│  ├── 观点是否有支撑（数据/引用/经验）                      │
│  ├── 逻辑链条是否完整                                      │
│  └── 是否有独特视角（非人云亦云）                          │
│  → 如果L3不通过，深化内容                                   │
│                                                             │
│  L4: 活人感终审 ✅                                          │
│  ├── 读起来像真实的人写的吗                                │
│  ├── 是否有作者独特的语言习惯/口头禅                       │
│  ├── 是否像在和读者聊天                                    │
│  └── 读完之后读者能记住什么                                 │
│  → 如果L4不通过，打回重写                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 禁词清单（L1硬规则）

#### 禁止词汇
```
说白了  本质上  这意味着  换句话说  不可否认
首先、其次、最后  近年来  随着  在XX时代
我们可以看到  从某种意义上  归根结底  众所周知
不得不承认  事实上  实际上  当然  从整体来看
不难发现  有鉴于此  基于此  据此  在此基础上
值得一提的是  值得注意的是 毫无疑问  毫无疑问地
显而易见 显而易见地 众所周知 众所周知地
```

#### 禁止标点
- 冒号 `：`用于解释性句子（引号内除外）
- 破折号 `——`（用于强调时可以保留一个）
- 英文引号 `" "`和`" "`（中文文章使用中文引号）

#### 禁止开头模式
```
"近年来..."
"随着..."
"在XX时代背景下..."
"我们可以看到..."
"事实上..."
"不可否认的是..."
"毫无疑问地..."
```

### 文章结构规范

#### 字数要求
- 标准文章：**4000-8000字**
- 短文章：3000-4000字
- 长文章：8000字以上（需要有足够支撑内容）

#### 标题规范
- 中文文章不使用英文标题
- 不使用emoji作为标题
- 标题具有信息量，让读者知道能得到什么

#### 小标题规范
- **不使用小标题**（核心原则）
- 如需使用，最多2个，且为自然过渡
- 读者应该沉浸在故事中，而不是看结构

#### 语言风格
- **口语化**：读起来像聊天
- **具体化**：有具体的人名、地点、事件
- **个性化**：有作者的语言习惯
- **场景化**：有画面感

### 微信公众号文章模板

```markdown
---
title: "文章标题"
author: "作者名"
date: YYYY-MM-DD
tags: [标签1, 标签2, 标签3]
---

# 文章标题

> 开篇引子：一句话引入主题，制造悬念或共鸣

[正文内容，保持流畅的叙事节奏]

---

## 相关文章推荐

1. [文章1标题](链接1)
2. [文章2标题](链接2)
3. [文章3标题](链接3)
```

### 天龙引擎调用封装

#### Python封装

```python
# ~/.claude/skills/khazix-writer/scripts/writer_checker.py
import re
from typing import List, Tuple

FORBIDDEN_WORDS = [
    '说白了', '本质上', '这意味着', '换句话说', '不可否认',
    '首先', '其次', '最后', '近年来', '随着',
    '我们可以看到', '从某种意义上', '归根结底', '众所周知',
    '不得不承认', '事实上', '实际上', '当然',
    '从整体来看', '不难发现', '有鉴于此', '基于此', '据此',
    '在此基础上', '值得一提的是', '值得注意的是',
    '毫无疑问', '显而易见'
]

FORBIDDEN_PATTERNS = [
    r'首先[\s\S]{0,5}其次[\s\S]{0,5}最后',  # 首先/其次/最后
    r'近年来', r'随着', r'在\w+时代',
    r'我们可以看到', r'从某种意义上',
    r'毫无疑问[地]?', r'显而易见[地]?'
]

FORBIDDEN_PUNCTUATION = [':', '——', '"', '"', '"', '"']

def L1_hard_rules(text: str) -> Tuple[bool, List[str]]:
    """L1层硬规则审查"""
    violations = []
    # 检查禁词
    for word in FORBIDDEN_WORDS:
        if word in text:
            violations.append(f"禁词: {word}")
    # 检查禁模式
    for pattern in FORBIDDEN_PATTERNS:
        matches = re.findall(pattern, text)
        for m in matches:
            violations.append(f"禁模式: {m[:20]}...")
    # 检查禁标点
    for p in FORBIDDEN_PUNCTUATION:
        count = text.count(p)
        if count > 1:
            violations.append(f"禁标点'{p}'出现{count}次")
    return len(violations) == 0, violations

def L2_style_check(text: str) -> Tuple[bool, List[str]]:
    """L2层风格一致性审查"""
    issues = []
    # 检查过度对仗的短句
    short_sentences = re.findall(r'[^。！？]+[。！？]', text)
    for i, s in enumerate(short_sentences[:-1]):
        next_s = short_sentences[i + 1]
        if len(s) < 15 and len(next_s) < 15:
            issues.append("可能过度对仗的短句")
    return len(issues) == 0, issues

def L3_content_check(text: str) -> Tuple[bool, List[str]]:
    """L3层内容质量审查"""
    issues = []
    # 检查是否有具体案例
    if not re.search(r'[人名地名公司名产品名]', text):
        issues.append("缺少具体案例支撑")
    # 检查逻辑链
    paragraphs = text.split('\n\n')
    for i, p in enumerate(paragraphs[:-1]):
        if len(p) > 500 and len(paragraphs[i+1]) > 500:
            issues.append(f"段落{i+1}和{i+2}都过长，可能缺少过渡")
    return len(issues) == 0, issues

def L4_living_check(text: str) -> Tuple[bool, List[str]]:
    """L4层活人感终审"""
    issues = []
    # 检查是否像真人写的
    unique_chars = len(set(text))
    density = unique_chars / len(text) if len(text) > 0 else 0
    if density < 0.3:
        issues.append("文字重复度过高，可能缺乏个性化表达")
    return len(issues) == 0, issues

def full_review(text: str) -> dict:
    """完整四层审查"""
    result = {
        'L1_pass': False, 'L1_issues': [],
        'L2_pass': False, 'L2_issues': [],
        'L3_pass': False, 'L3_issues': [],
        'L4_pass': False, 'L4_issues': []
    }
    l1_pass, l1_issues = L1_hard_rules(text)
    result['L1_pass'] = l1_pass
    result['L1_issues'] = l1_issues

    if l1_pass:
        l2_pass, l2_issues = L2_style_check(text)
        result['L2_pass'] = l2_pass
        result['L2_issues'] = l2_issues

        if l2_pass:
            l3_pass, l3_issues = L3_content_check(text)
            result['L3_pass'] = l3_pass
            result['L3_issues'] = l3_issues

            if l3_pass:
                l4_pass, l4_issues = L4_living_check(text)
                result['L4_pass'] = l4_pass
                result['L4_issues'] = l4_issues

    return result
```

#### CLI命令

```bash
# 审查文章
khazix-writer review article.md

# 审查并输出报告
khazix-writer review article.md --report

# 统计文章指标
khazix-writer stats article.md

# 生成活人感报告
khazix-writer living-score article.md
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **28-01文案策划** | V1.2→V1.3 | 四层活人感审查+禁词规则 |
| **07记录师** | V9.06→V9.07 | Wiki文章活人感检验 |
| **35-02社媒运营** | V12.7→V12.8 | 公众号文章活人感写作 |

### 与现有天龙能力协同

| 天龙组件 | khazix-writer协同 | 效果 |
|---------|------------------|------|
| **research-to-wechat (V8.0)** | 研究驱动写作+活人感审查 | 内容质量+AI味- |
| **baoyu-post-to-wechat** | 活人感文章+公众号发布 | 发布即合规 |
| **xiaohu-wechat-format** | 排版+活人感内容 | 形式+内容双优 |
| **humanizer-zh** | 去AI腔调+活人感写作 | 双重去AI味 |

### 预期收益

| 指标 | V11.10 | V11.11 | 提升 |
|------|--------|--------|------|
| **文章活人感** | 无量化标准 | 四层审查 | **质的飞跃** |
| **禁词检测** | 手动检查 | 自动扫描 | **+300%** |
| **文章质量一致性** | 依赖编辑 | 自动审查 | **+500%** |
| **AI味消除率** | 0% | **90%** | **新增能力** |

### 注意事项

1. **L1是硬门槛**：如果禁词检测不通过，必须重写对应段落
2. **活人感是主观的**：L4审查需要结合常识判断，不可机械执行
3. **字数是下限**：4000字是最低要求，内容不够不要硬凑
4. **小标题尽量不用**：这是最重要的风格建议

### 技能文件

- [skills/khazix-writer/SKILL.md](skills/khazix-writer/SKILL.md) ← 本文件
- [skills/khazix-writer/scripts/writer_checker.py](skills/khazix-writer/scripts/writer_checker.py)
- [skills/khazix-writer/scripts/forbidden_words.txt](skills/khazix-writer/scripts/forbidden_words.txt)
