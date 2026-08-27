# DeerFlow Skill Creator

## Overview

技能创建工具 - 迭代开发、测试评估。

## Core Loop

```
确定目标 → 起草技能 → 创建测试 → 运行评估 →
用户评估 → 重写技能 → 重复直到满意 → 扩展测试
```

## Steps

### 1. 捕获意图
理解技能应该让AI做什么，何时触发，预期输出

### 2. 访谈与研究
询问边缘情况、输入输出格式、示例文件、成功标准

### 3. 编写 SKILL.md
```markdown
skill-name/
├── SKILL.md (必需)
└── Bundled Resources (可选)
    ├── scripts/
    ├── references/
    └── assets/
```

### 4. 测试用例
```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description",
      "files": []
    }
  ]
}
```

### 5. 运行评估
```bash
# With-skill vs Baseline比较
python -m scripts.aggregate_benchmark <workspace>/iteration-N

# 启动查看器
python eval-viewer/generate_review.py <workspace>/iteration-N
```

## Description Optimization

### Step 1: 生成20个触发评估查询
8-10个should-trigger，8-10个should-not-trigger

### Step 2: 用户审查
HTML模板呈现评估集

### Step 3: 运行优化循环
```bash
python -m scripts.run_loop \
  --eval-set <path> \
  --skill-path <path> \
  --model <model-id> \
  --max-iterations 5
```

## Progressive Disclosure

三级加载系统：
1. **元数据** (name + description) - 始终在上下文
2. **SKILL.md正文** - 触发时在上下文
3. **捆绑资源** - 按需使用
