# prediction-immutability Hook

> **盲预测铁律执行器** — 预测一旦提交，不可修改。

## 核心规则

1. 预测提交后，任何修改预测分数的行为都被拦截
2. 只有在以下情况可"更新"预测：
   - 首次复盘(T+3d)后，填写实际分数
   - 最终复盘(T+7d)后，填写最终评分
3. 预测的"说明"字段可以追加注释，但不能修改原始分数

## 触发时机

`preToolUse` — 在执行Write/Edit操作前检查

## 检查逻辑

```
当用户尝试编辑预测相关文件时:
1. 检查文件路径是否在预测目录 (~/.claude/skills/cheat-on-content/predictions/)
2. 检查文件是否处于"已提交"状态 (有 submit_timestamp 字段)
3. 如果已提交且修改了预测分 → 拦截并返回警告
4. 如果是追加注释(添加新行) → 允许
5. 如果是填写复盘分数 → 允许(但需要标注是"实际分")
```

## 预测文件状态

| 状态 | 可修改内容 | 不可修改 |
|------|-----------|----------|
| **草稿** | 全部 | 无 |
| **已提交** | 追加注释、填写复盘数据 | 预测分数、预测分说明 |
| **已归档** | 归档签字外全部锁定 | 无 |

## 锁定机制

预测目录结构:

```
~/.claude/skills/cheat-on-content/predictions/
├── 2026-05/
│   ├── 2026-05-25-01-draft.json    # 草稿，可修改
│   ├── 2026-05-25-01-submitted.json # 已提交，已锁定
│   └── 2026-05-25-01-archived.json  # 已归档，完全锁定
```

## 文件锁定实现

草稿文件转换为已提交文件时:

```python
def lock_prediction(file_path: str):
    """将草稿文件锁定为已提交状态"""
    with open(file_path, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        data['status'] = 'submitted'
        data['submit_timestamp'] = datetime.now().isoformat()
        data['_locked'] = True
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()

    # 设置只读权限
    os.chmod(file_path, stat.S_IRUSR | stat.S_IRGRP)  # owner read-only
```

## 拦截响应

当预测被锁定后尝试修改，返回:

```
❌ 预测已锁定 (盲预测铁律)

预测ID: 2026-05-25-01
状态: 已提交
提交时间: 2026-05-25 14:30:22

⚠️ 根据盲预测铁律，预测一旦提交不可修改。

如果您需要记录新信息，请:
1. 首次复盘(T+3d)后: 在预测文件末尾追加"实际分数"部分
2. 创建新预测: 使用预测模板创建新的预测文件

如需查看预测内容，请使用:
  cat ~/.claude/skills/cheat-on-content/predictions/YYYY-MM/YYYY-MM-DD-XX-submitted.json
```

## 使用方式

```bash
# 查看预测状态
python3 skills/cheat-on-content/hooks/prediction-immutability.py status --id 2026-05-25-01

# 解锁预测(仅用于修正错误，需要提供reason)
python3 skills/cheat-on-content/hooks/prediction-immutability.py unlock --id 2026-05-25-01 --reason "分数计算错误"

# 查看锁定历史
python3 skills/cheat-on-content/hooks/prediction-immutability.py history --id 2026-05-25-01
```

## 配置

```json
{
  "hooks": {
    "preToolUse": {
      "Write": {
        "paths": ["skills/cheat-on-content/predictions/"],
        "check": "prediction-immutability",
        "action": "intercept_or_allow"
      },
      "Edit": {
        "paths": ["skills/cheat-on-content/predictions/"],
        "check": "prediction-immutability",
        "action": "intercept_or_allow"
      }
    }
  }
}
```