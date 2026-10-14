# 语法门禁 SOP v0.1

适用对象：阶段 4 质量门禁 `grammar` 子 agent。
单轮决策，输出 JSON，不允许混入自然语言。

## 输入

- `draft_path`: 草稿 Markdown 文件路径
- `platform`: 平台标识

## 检查项

| 检查 | 通过条件 |
|---|---|
| 错别字 | 中文错别字（用 pypinyin / 通用词典比对）= 0 |
| 标点 | 中英文标点不混用（中文段落用全角，引号用「」或 ""）|
| 重复 | 连续 3 行重复内容 = 0 |
| 长度异常 | 段落 < 3 字 或 > 500 字 = 0 |
| 残缺 | 段落末尾无标点 + 无省略号 = 0 |

## 输出

```json
{
  "gate": "grammar",
  "passed": true,
  "issues": [
    {"line": 12, "type": "typo", "text": "...", "fix": "..."}
  ],
  "iterations": 1,
  "checker": "scripts/run_gate.py grammar",
  "checked_at": "ISO8601"
}
```

## 边界

- ❌ 不评估内容观点（那是 `tone` / `compliance` 的事）
- ❌ 不修改草稿，只读
- ❌ 不联网（除非需要查词典）

## 实现

```bash
python scripts/run_gate.py grammar --draft <draft_path> --output <gate_json_path>
```

脚本内置正则 + 词典；模型负责最终判断，脚本负责机械化检测。