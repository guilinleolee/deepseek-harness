# 风格门禁 SOP v0.1

适用对象：阶段 4 质量门禁 `tone` 子 agent。
单轮决策，输出 JSON。

## 输入

- `draft_path`: 草稿 Markdown
- `style`: 用户指定的风格（professional / humorous / warm / academic / case_study）
- `style_dna_path`: 默认 `prompts/style/style-dna.md`

## 检查项

| 检查 | 通过条件 |
|---|---|
| 语气 | 与 `style` 一致；不混入其它语气 |
| 品牌一致性 | 与 `style-dna.md` 的核心人设不冲突 |
| 读者视角 | 朋友视角，不是说教 |
| 禁用词 | 不出现禁用词清单中的词 |
| 内容比例 | 草稿类型与本周内容比例不冲突（粗略）|

## 输出

```json
{
  "gate": "tone",
  "passed": true,
  "issues": [],
  "iterations": 1,
  "checker": "scripts/run_gate.py tone",
  "checked_at": "ISO8601"
}
```

## 实现

```bash
python scripts/run_gate.py tone \
  --draft <draft_path> \
  --style professional \
  --style-dna prompts/style/style-dna.md \
  --output <gate_json_path>
```

模型读完 style-dna.md 后裁决。