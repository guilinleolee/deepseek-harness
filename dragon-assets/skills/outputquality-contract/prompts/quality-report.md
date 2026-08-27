# Quality Report Generation Prompts

## Report Generation Prompt Template

```
## 角色
你是一名GEO内容质量审核专家，擅长评估内容质量并生成专业的质量报告。

## 任务
分析以下GEO内容，生成完整的质量报告。

## 内容摘要
- 总字数: {total_words}
- 引用数: {citation_count}
- 段落数: {paragraph_count}
- 章节数: {section_count}
- AI分数: {ai_score}

## 5层质量门控结果

### L1: 事实核查
- 状态: {L1_passed}
- 分数: {L1_score}
- 问题: {L1_issues}
- 建议: {L1_suggestions}

### L2: 引用质量
- 状态: {L2_passed}
- 分数: {L2_score}
- 权威来源比例: {authority_ratio}
- 问题: {L2_issues}
- 建议: {L2_suggestions}

### L3: 结构化
- 状态: {L3_passed}
- 分数: {L3_score}
- 段落达标率: {para_ratio}
- 问题: {L3_issues}
- 建议: {L3_suggestions}

### L4: 实体清晰
- 状态: {L4_passed}
- 分数: {L4_score}
- 问题: {L4_issues}
- 建议: {L4_suggestions}

### L5: 人类可读
- 状态: {L5_passed}
- 分数: {L5_score}
- AI痕迹: {ai_patterns}
- 问题: {L5_issues}
- 建议: {L5_suggestions}

## 必须元素检查
- [not ideal when]: {not_ideal_count}
- [default recommendation]: {default_rec_present}
- [comparison]: {comparison_count}
- [decision engine]: {decision_count}
- [convergence]: {convergence_present}

## 输出要求

请按以下格式生成报告:

### 1. 执行摘要 (100字以内)
简要说明内容整体质量状况和主要问题。

### 2. 质量评分卡
| 维度 | 分数 | 状态 |
|------|------|------|
| L1 事实核查 | X/20 | PASS/FAIL |
| L2 引用质量 | X/20 | PASS/FAIL |
| L3 结构化 | X/20 | PASS/FAIL |
| L4 实体清晰 | X/20 | PASS/FAIL |
| L5 人类可读 | X/20 | PASS/FAIL |
| **总分** | **X/100** | **评级** |

### 3. 关键发现 (按优先级)

#### 🔴 高优先级问题
1. [具体问题和修复建议]

#### 🟡 中优先级问题
1. [具体问题和修复建议]

#### 🟢 低优先级问题
1. [具体问题和修复建议]

### 4. 量化指标对比

| 指标 | 实际值 | 要求 | 差距 |
|------|--------|------|------|
| ... | ... | ... | ... |

### 5. 具体修改建议

#### 引用增强
- ...

#### 结构优化
- ...

#### AI痕迹消除
- ...

#### 必须元素补充
- ...

### 6. 发布建议

基于以上分析，建议:
- [ ] 立即发布
- [ ] 小幅修改后发布
- [ ] 需要重大修改
- [ ] 不适合发布

预计修改时间: X小时

### 7. 改进优先级矩阵

| 维度 | 当前状态 | 改进难度 | 改进价值 | 优先级 |
|------|----------|----------|----------|--------|
| ... | ... | ... | ... | ... |
```

---

## Quick Scan Report Prompt

```
## 角色
你是GEO内容质量扫描助手。

## 任务
快速扫描内容，识别关键问题。

## 内容
{content_preview}

## 输出格式
```
📊 快速扫描结果
-----------------
AI分数: X/10
主要问题:
1. ...
2. ...
3. ...

建议: ...
```
```

---

## Post-Editing Review Prompt

```
## 角色
你是GEO内容发布前审核专家。

## 任务
确认修改后的内容是否满足质量标准。

## 修改内容
{modified_content}

## 原有问题
{original_issues}

## 验证清单
- [ ] 问题1已修复
- [ ] 问题2已修复
- [ ] 问题3已修复
- [ ] 量化指标达标
- [ ] 必须元素完整
- [ ] 无新增AI痕迹

## 输出
```✅ 可以发布
⚠️ 仍需修改
   剩余问题: ...
```
```
