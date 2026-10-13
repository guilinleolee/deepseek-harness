# 事实门禁 SOP v0.1

适用对象：阶段 4 质量门禁 `factual` 子 agent。
单轮决策，输出 JSON，不允许混入自然语言。

## 输入

- `draft_path`: 草稿 Markdown 文件路径
- `research_path`: `.work/<task_id>/research.json`

## 检查项

| 检查 | 通过条件 |
|---|---|
| 数据引用 | 草稿中每个具体数字（百分比 / 金额 / 日期）都能在 `research.json` 中找到来源 |
| 案例引用 | 草稿中提到的案例 / 公司 / 人物都能在 `research.json` 中找到出处 |
| 因果关系 | 草稿中"因为 X 所以 Y"的逻辑 X 必须存在 |
| 工具声明 | 草稿声明的功能 / 工具 / 价格必须真实存在 |

## 输出

```json
{
  "gate": "factual",
  "passed": false,
  "issues": [
    {"line": 23, "claim": "X 工具 99 元", "verdict": "unverifiable", "fix": "删除或注明'据用户实测'"}
  ],
  "iterations": 1,
  "checker": "scripts/run_gate.py factual",
  "checked_at": "ISO8601"
}
```

## 边界

- ❌ 不评估观点对错（那是 `tone` 的事）
- ❌ 不联网补充事实（只比对已有素材）
- ❌ 不修改草稿

## 实现

```bash
python scripts/run_gate.py factual \
  --draft <draft_path> \
  --research <research_path> \
  --output <gate_json_path>
```

模型从草稿中提取所有"可证伪陈述"，脚本对每条去 research.json 检索，模型做最后裁决。