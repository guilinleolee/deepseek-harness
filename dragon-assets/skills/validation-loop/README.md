# 验证循环系统 - 快速开始

## 概述

验证循环系统是基于概率论的科学验证框架，提供两种核心验证模式：

- **pass@k**: 探索性验证，至少 1 次成功即通过
- **pass^k**: 严格性验证，全部成功才通过

## 文件结构

```
~/.claude/skills/validation-loop/
├── SKILL.md              # 完整理论文档
├── validation-tools.sh   # 工具库（可独立使用）
├── benchmark.sh          # A/B 基准测试
├── examples.md           # 实战案例
└── README.md             # 本文档
```

## 快速使用

### 1. pass@k 验证（探索性）

```bash
# 运行 3 次测试，至少 1 次成功即通过
validation-tools.sh pass-at 3 "npm test" "单元测试"

# 或直接调用
bash ~/.claude/skills/validation-loop/validation-tools.sh pass-at 3 "mgrep 'Find TODO'" "语义搜索"
```

**输出示例**：
```
🔍 pass@3 验证: 单元测试
  尝试 1/3...
  ⚠️  尝试 1 失败，继续...
  尝试 2/3...
  ✅ 尝试 2 成功，通过验证
```

### 2. pass^k 验证（严格性）

```bash
# 运行 3 次测试，全部成功才通过
validation-tools.sh pass-pow 3 "make build" "构建验证"

# 或直接调用
bash ~/.claude/skills/validation-loop/validation-tools.sh pass-pow 2 "curl -s https://api.example.com/health" "API健康检查"
```

**输出示例**：
```
🎯 pass^3 严格验证: 构建验证
  严格验证 1/3...
  ✅ 尝试 1 成功 (1/3)
  严格验证 2/3...
  ✅ 尝试 2 成功 (2/3)
  严格验证 3/3...
  ✅ 尝试 3 成功 (3/3)
  🎉 3次尝试全部成功，通过严格验证
```

### 3. A/B 基准测试

```bash
# 对比 grep vs mgrep 性能
bash ~/.claude/skills/benchmark.sh

# 或使用自定义 A/B 测试
validation-tools.sh ab-test "grep -r 'TODO' --include='*.ts'" "mgrep 'Find TODO in TypeScript'" 10
```

### 4. 查看概率表

```bash
# 查看 k=3 时的理论成功率
validation-tools.sh probability 3
```

**输出示例**：
```
📊 概率对比表 (k=3)

单次成功率 | pass@3   | pass^3
----------------------------------------
50%        | 87.5%    | 12.5%
60%        | 94.0%    | 21.6%
70%        | 97.3%    | 34.3%
80%        | 99.2%    | 51.2%
90%        | 99.9%    | 72.9%
```

## 与九部天龙集成

验证循环已整合到 04-验证师配置中。各宗师的验证模式映射：

| 宗师 | 探索阶段 | 严格阶段 | 评估方式 |
|------|----------|----------|----------|
| 00分析师 | pass@2 | pass^2 | Checkpoint |
| 01调研师 | pass@3 | - | Continuous |
| 02架构师 | pass@3 | pass^2 | Checkpoint |
| 03构建师 | pass@2 | pass^2 | Continuous |
| **04验证师** | **pass@3** | **pass^3** | **Checkpoint** |
| 05安全师 | pass@3 | pass^3 | Checkpoint |
| 06审查师 | pass@2 | pass^2 | Continuous |
| 07记录师 | pass@1 | pass@2 | Checkpoint |
| 08发布师 | pass@2 | pass^3 | Checkpoint |

## 实战案例

### 案例 1：代码考古（01调研师）

```bash
# pass@3: 探索技术债务
for i in {1..3}; do
  echo "考古尝试 $i/3..."
  if mgrep "Find all TODO, FIXME, and HACK comments" > debt.txt; then
    echo "✅ 发现技术债务"
    break
  fi
done
```

### 案例 2：架构验证（02架构师）

```bash
# pass^2: 严格验证核心模块
success_count=0
for i in {1..2}; do
  echo "核心模块验证 $i/2..."
  if npm run test:core; then
    success_count=$((success_count + 1))
  else
    echo "❌ 核心模块验证失败"
    exit 1
  fi
done
echo "🎉 核心模块稳定"
```

### 案例 3：生产部署（08发布师）

```bash
# pass^3: 生产级严格验证
for i in {1..3}; do
  echo "生产验证 $i/3..."
  if ! curl -f https://api.example.com/health; then
    echo "❌ 健康检查失败"
    exit 1
  fi
  sleep 5
done
echo "🚀 部署成功"
```

## Checkpoint-Based 评估

创建 `checkpoints.json` 配置文件：

```json
{
  "checkpoints": [
    {
      "name": "需求分析",
      "mode": "pass_at",
      "k": 2,
      "command": "npm run test:requirements"
    },
    {
      "name": "架构设计",
      "mode": "pass_at",
      "k": 3,
      "command": "npm run test:architecture"
    },
    {
      "name": "代码质量",
      "mode": "pass_pow",
      "k": 2,
      "command": "npm run lint"
    },
    {
      "name": "安全扫描",
      "mode": "pass_pow",
      "k": 3,
      "command": "npm run audit"
    }
  ]
}
```

运行评估：

```bash
validation-tools.sh checkpoint checkpoints.json
```

## Continuous 评估

持续运行 10 分钟，每 30 秒测试一次：

```bash
validation-tools.sh continuous 10 30 "npm test"
```

**输出示例**：
```
🔄 Continuous 评估开始
持续时间: 10分钟
测试间隔: 30秒

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
运行 #1 (14:30:00)
✅ 通过
⏱️  剩余: 9分 28秒

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
运行 #2 (14:30:30)
❌ 失败
⏱️  剩余: 8分 56秒

...

📊 持续评估结果:
  总运行: 20
  通过: 18
  失败: 2
  成功率: 90.0%
```

## 性能优化

### 选择合适的 k 值

根据单次成功率 `p` 和目标成功率 `P_target` 计算：

```
pass@k: k ≥ log(1 - P_target) / log(1 - p)
pass^k: k ≥ log(P_target) / log(p)
```

**快速参考**：

| 场景 | 单次成功率 | k (pass@k) | k (pass^k) |
|------|-----------|-----------|-----------|
| 快速原型 | 50% | 3-5 | - |
| 标准测试 | 70% | 2-3 | 2-3 |
| 生产部署 | 90% | 2 | 3 |

## 技术支持

- 完整理论文档：[SKILL.md](./SKILL.md)
- 实战案例：[examples.md](./examples.md)
- 九部天龙集成：[agents/04-validator.md](../../agents/04-validator.md)

## 版本历史

- **v1.0.0** (2026-02-08): 初始版本
  - pass@k 和 pass^k 核心实现
  - Checkpoint-Based 和 Continuous 评估
  - A/B 基准测试工具
  - 九部天龙集成

---

**维护者**: 九部天龙团队
**许可**: MIT
