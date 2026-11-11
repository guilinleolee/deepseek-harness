# 合规门禁 SOP v0.1

适用对象：阶段 4 质量门禁 `compliance` 子 agent。
单轮决策，输出 JSON，不允许混入自然语言。

## 检查项

| 检查 | 规则 |
|---|---|
| 广告法 | 不出现"最 / 第一 / 唯一 / 顶级 / 国家级 / 销量冠军"等绝对化用语 |
| 违禁词 | 不出现医疗效果保证（治愈 / 根治 / 100% 有效）、投资回报承诺（保本 / 稳赚）|
| 夸大收益 | 不出现"月入 X 万 / 一周 X 倍"等无来源收益承诺 |
| 政治敏感 | 不出现敏感政治人物 / 事件 / 言论 |
| 平台禁词 | 平台特定的禁词清单（`prompts/style/compliance-wechat.md` 等）|

## 输出

```json
{
  "gate": "compliance",
  "passed": false,
  "issues": [
    {"line": 8, "phrase": "稳赚不赔", "category": "投资承诺", "fix": "改为'据历史数据'"}
  ],
  "iterations": 5,
  "checker": "scripts/run_gate.py compliance",
  "checked_at": "ISO8601"
}
```

## 边界

- ❌ 不评估风格（那是 `tone` 的事）
- ❌ 不替用户决定"夸大"的具体阈值，由 agent 在 prompt 中配置

## 实现

```bash
python scripts/run_gate.py compliance \
  --draft <draft_path> \
  --platform wechat \
  --output <gate_json_path>
```

脚本加载禁词清单（`prompts/style/banned-words.json`），机械匹配；模型裁决边界。