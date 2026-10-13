# retro-form

> **复盘表单生成器** — 生成T+3d和T+7d复盘表单。

## 复盘时间线

```
T+0 (发布日)
  │
  ├── 创建预测文件
  ├── 提交预测 (锁定)
  └── Buffer -1
  │
  ▼
T+3d (首次复盘)
  │
  ├── 填写实际分数
  ├── 计算偏差
  ├── 偏差分析
  ├── 更新Rubric观察
  └── 触发Rubric验证
  │
  ▼
T+7d (最终复盘)
  │
  ├── 填写最终评分
  ├── 预测准确度统计
  ├── 学习价值评估
  └── 归档签字
```

## 复盘类型

### T+3d首次复盘

**目的**: 收集初步数据，验证预测，识别观察偏差

**表单内容**:
1. 实际分数填写
2. 各维度偏差计算
3. 偏差原因分析
4. Rubric观察更新

### T+7d最终复盘

**目的**: 收集完整数据，统计准确度，评估学习价值

**表单内容**:
1. 最终评分确认
2. 预测准确度统计
3. 话题/平台表现总结
4. 学习价值评估
5. 归档签字

## 使用方式

### 生成复盘表单

```bash
# 生成T+3d复盘表单
python3 skills/cheat-on-content/tools/retro-form.py generate \
  --id 2026-05-22-01 \
  --type t3d \
  --output retrospectives/2026-05/2026-05-25-01-t3d.md

# 生成T+7d复盘表单
python3 skills/cheat-on-content/tools/retro-form.py generate \
  --id 2026-05-18-01 \
  --type t7d \
  --output retrospectives/2026-05/2026-05-25-01-t7d.md

# 批量生成待复盘表单
python3 skills/cheat-on-content/tools/retro-form.py generate-pending
```

### 填写复盘

```bash
# 填写T+3d复盘
python3 skills/cheat-on-content/tools/retro-form.py fill \
  --id 2026-05-22-01 \
  --type t3d \
  --actual ER=8.2 --actual SR=7.8 --actual HP=6.8 \
  --actual QL=7.2 --actual NA=6.5 --actual AB=6.0 --actual SAT=7.5

# 填写T+7d复盘
python3 skills/cheat-on-content/tools/retro-form.py fill \
  --id 2026-05-18-01 \
  --type t7d \
  --final-rating excellent \
  --learning-value high \
  --notes "职场内容ER普遍较高，本次验证了这一点"
```

### 查看复盘状态

```bash
# 查看所有复盘
python3 skills/cheat-on-content/tools/retro-form.py list

# 查看待复盘
python3 skills/cheat-on-content/tools/retro-form.py pending

# 查看复盘详情
python3 skills/cheat-on-content/tools/retro-form.py show --id 2026-05-22-01
```

## T+3d复盘表单模板

```markdown
# T+3d 首次复盘

**发布ID**: 2026-05-22-01
**平台**: 微博
**话题**: AI趋势
**发布日期**: 2026-05-22
**复盘日期**: 2026-05-25

---

## 一、实际分数填写

| 维度 | 预测分 | 实际分 | 偏差 | 偏差率 |
|------|--------|--------|------|--------|
| ER (曝光率) | 8.0 | __ | __ | __ |
| SR (互动率) | 7.5 | __ | __ | __ |
| HP (完播率) | 7.0 | __ | __ | __ |
| QL (质量分) | 7.5 | __ | __ | __ |
| NA (数值锚) | 7.0 | __ | __ | __ |
| AB (行动率) | 6.0 | __ | __ | __ |
| SAT (满意度) | 7.0 | __ | __ | __ |
| **总分** | **13.2** | **__** | **__** | **__** |

---

## 二、偏差分析

### 2.1 总体偏差
- 预测分: 13.2分
- 实际分: __分
- 偏差: __分 (__%)
- 偏差方向: ⬆️偏高 / ⬇️偏低

### 2.2 各维度偏差原因

**ER (曝光率)**
- 偏差: __分
- 可能原因:
  - [ ] 推送时间不对
  - [ ] 话题热度变化
  - [ ] 粉丝活跃度下降
  - [ ] 其他: __

**SR (互动率)**
- 偏差: __分
- 可能原因:
  - [ ] 封面不够吸引
  - [ ] 开头不够抓人
  - [ ] 选题不够吸引人
  - [ ] 其他: __

### 2.3 最大偏差维度
- 维度: __
- 偏差: __分
- 原因分析: __

---

## 三、Rubric观察更新

### 3.1 与现有观察的对比

现有相关观察:
- [观察#5] "技术话题ER普遍较高" — 匹配度: 80%
- [观察#8] "AI相关内容互动率高" — 匹配度: 75%

### 3.2 是否需要更新观察?
- [ ] 新数据支持现有观察
- [ ] 需要微调现有观察阈值
- [ ] 需要新增观察
- [ ] 现有观察被否定，需删除

### 3.3 观察更新内容
```json
{
  "observation_id": "obs_xxx",
  "content": "观察内容",
  "update_type": "confirm|adjust|add|reject",
  "evidence": {
    "supporting_samples": 1,
    "match_rate": 0.85
  }
}
```

---

## 四、复盘完成确认

- [x] 实际分数已填写
- [x] 偏差分析已完成
- [x] Rubric观察已更新
- [x] 已触发Rubric验证

**复盘完成时间**: __
**复盘人**: __
```

## T+7d最终复盘表单模板

```markdown
# T+7d 最终复盘

**发布ID**: 2026-05-18-01
**平台**: 抖音
**话题**: 效率工具
**发布日期**: 2026-05-18
**最终复盘日期**: 2026-05-25

---

## 一、最终评分确认

### 1.1 完整数据

| 指标 | 数值 |
|------|------|
| 最终曝光量 | __ |
| 最终互动量 | __ |
| 最终完播率 | __ |
| 评论数 | __ |
| 收藏数 | __ |
| 分享数 | __ |

### 1.2 最终评分

| 维度 | 预测 | T+3d实际 | T+7d实际 | 最终确认 |
|------|------|----------|----------|----------|
| ER | 7.5 | 7.8 | 8.0 | __ |
| SR | 7.0 | 7.2 | 7.5 | __ |
| HP | 6.5 | 6.8 | 7.0 | __ |
| QL | 7.0 | 7.2 | 7.5 | __ |
| NA | 6.5 | 6.5 | 6.5 | __ |
| AB | 6.0 | 6.0 | 6.2 | __ |
| SAT | 7.0 | 7.0 | 7.2 | __ |
| **总分** | **12.3** | **12.6** | **13.0** | **__** |

---

## 二、预测准确度统计

### 2.1 准确度评分

| 评分项 | 得分 | 说明 |
|--------|------|------|
| 方向准确 | 8/10 | 预测偏高/偏低 |
| 幅度准确 | 7/10 | 偏差在±2分内 |
| 趋势准确 | 8/10 | 数据变化方向正确 |

**综合准确度**: __/10 (__%)

### 2.2 准确度分析

- 预测最准的维度: __ (偏差__分)
- 预测最差的维度: __ (偏差__分)
- 准确度变化: ⬆️提升 / ⬇️下降 / ➡️持平

---

## 三、话题/平台表现总结

### 3.1 本次内容表现
- 最高维度: __ (__分)
- 最低维度: __ (__分)
- 与同类内容对比: 超过/持平/不如

### 3.2 可复用的经验
1. __
2. __
3. __

### 3.3 需要改进的地方
1. __
2. __
3. __

---

## 四、学习价值评估

### 4.1 学习价值
- [ ] 高 — 有重要新发现，可更新Rubric
- [ ] 中 — 验证了现有认知
- [ ] 低 — 无明显新价值

### 4.2 新观察/假设
```json
{
  "new_observation": "观察内容",
  "confidence": "high|medium|low",
  "requires_validation": true,
  "validation_plan": "下次做类似内容时验证"
}
```

---

## 五、归档签字

### 5.1 复盘确认
- [x] 所有分数已确认
- [x] 分析已完成
- [x] 学习价值已评估
- [x] 新观察已记录

### 5.2 Rubric更新
- [ ] 无需更新
- [ ] 已更新观察: obs_xxx
- [ ] 已触发Bump

### 5.3 归档信息
**最终复盘完成时间**: __
**最终复盘人**: __
**归档时间**: __

---

## 六、复盘签字

| 角色 | 签字 | 日期 |
|------|------|------|
| 内容创作者 | __ | __ |
| 复盘审核 | __ | __ |
```

## 配置

```json
{
  "retro": {
    "t3d_form_template": "templates/retro-t3d-template.md",
    "t7d_form_template": "templates/retro-t7d-template.md",
    "auto_reminder_days": {
      "t3d": [3, 4, 5],
      "t7d": [7, 8, 9]
    },
    "lock_publish_until_t3d": true,
    "archive_after_t7d": true
  }
}
```

## 数据存储

```
~/.claude/skills/cheat-on-content/
├── retrospectives/
│   └── YYYY-MM/
│       ├── YYYY-MM-DD-XX-t3d.md
│       └── YYYY-MM-DD-XX-t7d.md
├── retrospective-logs/
│   └── retrospective-events.jsonl
└── templates/
    ├── retro-t3d-template.md
    └── retro-t7d-template.md
```
