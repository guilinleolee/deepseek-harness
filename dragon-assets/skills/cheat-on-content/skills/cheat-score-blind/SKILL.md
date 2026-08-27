# Cheat-Score-Blind — 盲评分系统

## L0: 一句话描述
完全隔离的盲评分流程，避免上下文偏差

## L1: 使用场景
正式评分时委托盲子Agent，确保评分的客观性

## L2: 详细文档

### 触发词
- "盲评分"
- "blind score"
- "正式打分"
- "独立评分"

### 核心铁律

```
1. 盲子Agent必须隔离启动
2. 盲子Agent只能看到脚本内容和rubric
3. 盲子Agent不能看到任何历史数据
4. 评分结果由主Agent解析并输出
5. 全程无文件写入
```

### 盲评分流程

```
主Agent                          盲子Agent
   │                                  │
   ├─ 读取脚本 ──────────────────────▶│
   │                                  │
   │                                  ├─ 读取rubric
   │                                  │
   │                                  ├─ 7维度独立打分
   │                                  │
   │◀─ 输出JSON评分结果 ──────────────┤
   │                                  │
   ├─ 解析得分
   ├─ 计算综合分
   └─ 输出报告
```

### JSON输出格式（盲子Agent）

```json
{
  "ER": {"score": 4, "reasoning": "开场引发共鸣"},
  "SR": {"score": 5, "reasoning": "有传播属性"},
  "HP": {"score": 3, "reasoning": "开场平淡"},
  "QL": {"score": 2, "reasoning": "金句偏少"},
  "NA": {"score": 4, "reasoning": "结构完整"},
  "AB": {"score": 3, "reasoning": "受众较窄"},
  "SAT": {"score": 2, "reasoning": "无讽刺元素"},
  "composite": 7.3,
  "confidence": "high",
  "flags": ["HP偏低", "QL可提升"]
}
```

### 天龙引擎集成

- **天龙岗位**: 04验证师、35-02社媒运营
- **协同**: cheat-score（探索）、cheat-predict（预测）、cheat-bump（升级）