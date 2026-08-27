# mano-p-core

本地GUI-VLA推理引擎 - 天龙引擎V9.04核心技能

## 功能
- 本地GUI-VLA推理（数据不上云）
- 无API跨系统集成
- think-act-verify循环推理
- OSWorld Specialized #1 (58.2%)

## 安装
```bash
cd ~/.claude/skills/mano-p-core
# 参照SKILL.md安装指南
```

## 使用
```python
from mano_vla_client import mano_vla_execute

result = await mano_vla_execute("打开Chrome访问Google")
```

## 协同
- 所属岗位: 17-07 GUI-VLA集成工程师
- 协同技能: mano-p-skills, turix-desktop-agent