# 结构门禁 SOP v0.1

适用对象：阶段 4 质量门禁 `structure` 子 agent。

## 检查项

| 平台 | 标题字数 | 段落数 | 配图位 | 字数区间 |
|---|---|---|---|---|
| wechat | 14-22 | ≥ 3 个 H2 | ≥ 2 | 1500-3000 |
| xiaohongshu | ≤ 21 | 6-9 页图文 | 每页 1 张 | 正文 300-800 |
| douyin | 15-25 | 5 个时段 | 5-8 个镜头 | 45-90 秒 |
| toutiao | ≤ 20 | 1 段 | 0 | 200-500 |

## 输出

```json
{
  "gate": "structure",
  "passed": true,
  "issues": [],
  "metrics": {
    "title_chars": 18,
    "h2_count": 4,
    "image_placeholders": 3,
    "word_count": 2100
  },
  "iterations": 1,
  "checker": "scripts/run_gate.py structure",
  "checked_at": "ISO8601"
}
```

## 实现

```bash
python scripts/run_gate.py structure \
  --draft <draft_path> \
  --platform wechat \
  --output <gate_json_path>
```

脚本机械统计字数 / 段落数；模型验证是否合规。