---
license: UNKNOWN
name: validation-loop
description: 验证循环系统 - 基于概率论的科学验证策略。pass@k（至少1次成功）vs pass^k（全部成功），适用于九部天龙各阶段的验证需求。
version: 1.0.0
author: 九部天龙
created: 2026-02-26
triggers: ["validation loop", "验证循环系统"]
---

# 验证循环系统

## 核心概念

验证循环是基于概率论的科学验证策略，通过 **pass@k** 和 **pass^k** 两种模式，优化验证成本和质量的平衡。

### 数学原理

假设单次尝试成功率为 **p = 70%**：

| k | pass@k (至少1次) | pass^k (全部成功) | 差异 |
|---|----------------|-----------------|------|
| 1 | 70% | 70% | 相同 |
| 3 | 97% | 34% | **显著** |
| 5 | 100% | 17% | **巨大** |

**公式**:
```python
# pass@k: k次尝试中至少1次成功
P(pass@k) = 1 - (1-p)^k

# pass^k: k次尝试必须全部成功
P(pass^k) = p^k
```

## 两种验证模式

### 1. pass@k 模式（探索性验证）

**定义**: k次尝试中至少1次成功即通过

**适用场景**:
- 代码生成（03构建师）
- 方案设计（02架构师）
- 需求理解（00分析师）
- 快速原型开发

**特点**:
- ✅ 高成功率（k=3 时 97%）
- ✅ 成本优化（成功即停）
- ✅ 适合探索性任务

**示例**:
```bash
#!/bin/bash
# pass@3 实现

MAX_ATTEMPTS=3

for attempt in $(seq 1 $MAX_ATTEMPTS); do
  echo "🔄 尝试 $attempt/$MAX_ATTEMPTS..."

  if run_test; then
    echo "✅ 尝试 $attempt 成功，停止验证"
    exit 0
  else
    echo "❌ 尝试 $attempt 失败"
    # 继续下一次尝试
  fi
done

echo "⚠️  $MAX_ATTEMPTS 次尝试均失败"
exit 1
```

### 2. pass^k 模式（严格验证）

**定义**: k次尝试必须全部成功才通过

**适用场景**:
- 安全检查（05安全师）
- 生产部署（08发布师）
- 性能测试（04验证师）
- Bug回归测试

**特点**:
- ✅ 高稳定性要求
- ✅ 确保每次都成功
- ✅ 适合关键任务

**示例**:
```bash
#!/bin/bash
# pass^3 实现

REQUIRED_SUCCESSES=3
actual_successes=0

for attempt in $(seq 1 $REQUIRED_SUCCESSES); do
  echo "🔒 严格验证 $attempt/$REQUIRED_SUCCESSES..."

  if run_test; then
    actual_successes=$((actual_successes + 1))
    echo "✅ 尝试 $attempt 成功"
  else
    echo "❌ 尝试 $attempt 失败，验证不通过"
    exit 1
  fi
done

echo "✅ $REQUIRED_SUCCESSES 次尝试全部成功"
exit 0
```

## 验证策略矩阵

### 九部天龙验证模式映射

| 宗师 | 任务类型 | 验证模式 | k值 | 成功率 | 容错策略 |
|------|----------|----------|-----|--------|----------|
| 00分析师 | 需求理解 | pass@3 | 3 | 97% | 快速迭代 |
| 02架构师 | 方案设计 | pass@3 | 3 | 97% | 方案对比 |
| 03构建师 | 代码生成 | pass@5 | 5 | 100% | 多次重试 |
| 04验证师 | 功能测试 | pass@3 | 3 | 97% | 测试套件 |
| 05安全师 | 安全检查 | pass^5 | 5 | 17% | 零容忍 |
| 06审查师 | 代码审查 | pass@1 | 1 | 70% | 单次审查 |
| 08发布师 | 生产部署 | pass^3 | 3 | 34% | 预发布验证 |

## 评估模式

### Checkpoint-Based Evals（检查点模式）

**定义**: 设置明确的检查点，验证是否符合标准，通过后不继续。

**适用场景**:
- 代码编译检查
- 单元测试验证
- 集成测试关卡
- PR 合并前检查

**示例**:
```bash
#!/bin/bash
# 检查点验证

checkpoints=(
  "编译代码"
  "运行单元测试"
  "运行集成测试"
  "运行E2E测试"
)

for checkpoint in "${checkpoints[@]}"; do
  echo "📍 检查点: $checkpoint"

  if ! run_checkpoint "$checkpoint"; then
    echo "❌ 检查点失败: $checkpoint"
    exit 1
  fi

  echo "✅ 检查点通过: $checkpoint"
done

echo "✅ 所有检查点通过"
```

### Continuous Evals（持续评估）

**定义**: 每隔N分钟或大改动后，运行完整测试套件。

**适用场景**:
- 持续集成（CI/CD）
- 长期运行的服务
- 监控生产环境

**示例**:
```bash
#!/bin/bash
# 持续评估

INTERVAL=600  # 10分钟

while true; do
  echo "⏰ $(date) - 运行持续评估..."

  # 运行完整测试套件
  run_full_test_suite
  run_lint
  check_coverage

  # 记录结果
  log_results

  echo "💤 等待 $INTERVAL 秒..."
  sleep $INTERVAL
done
```

## 基准测试

### Fork 对比测试

**方法**: 创建两个分支，一个用 Skills，一个不用，对比输出差异。

**步骤**:
```bash
# 1. 创建基准分支
git checkout -b baseline/no-skills
run_benchmark > baseline.json

# 2. 创建测试分支
git checkout -b experiment/with-skills
run_benchmark > experiment.json

# 3. 对比分析
diff baseline.json experiment.json

# 4. 生成报告
generate_report baseline.json experiment.json
```

### A/B 测试框架

```bash
#!/bin/bash
# ab-test.sh

TASK=$1
MODE=$2  # "with-skills" | "without-skills"

echo "🧪 A/B测试: $TASK ($MODE)"

start_time=$(date +%s.%N)

if [ "$MODE" = "with-skills" ]; then
  result=$(execute_with_skills "$TASK")
else
  result=$(execute_without_skills "$TASK")
fi

end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc)

echo "结果: $result"
echo "耗时: ${duration}s"

echo $duration
```

## 使用指南

### 选择验证模式

**决策树**:
```
任务是否关键？
├── 是 → 需要稳定一致？
│   ├── 是 → pass^k (严格验证)
│   └── 否 → pass@k (探索性验证)
└── 否 → pass@k (节省成本)
```

### 选择 k 值

| 预期成功率 | k值 | 成本 | 推荐场景 |
|-----------|-----|------|----------|
| 70% | 1 | 低 | 快速验证 |
| 91% | 3 | 中 | 标准验证 |
| 97% | 5 | 高 | 重要验证 |
| 100% | 7+ | 很高 | 关键验证 |

### 选择评估模式

| 需求 | 推荐模式 | 原因 |
|------|----------|------|
| PR检查 | Checkpoint-Based | 快速反馈 |
| CI/CD | Continuous | 自动化 |
| 本地开发 | Checkpoint-Based | 按需运行 |
| 生产监控 | Continuous | 持续监控 |

## 最佳实践

### 1. 分层验证

```markdown
## L1: 快速验证（pass@1）
- 成本: 低
- 成功率: 70%
- 适用: 日常开发

## L2: 标准验证（pass@3）
- 成本: 中
- 成功率: 97%
- 适用: 功能开发

## L3: 严格验证（pass^3）
- 成本: 高
- 成功率: 34%
- 适用: 生产部署

## L4: 关键验证（pass^5）
- 成本: 很高
- 成功率: 17%
- 适用: 安全检查
```

### 2. 容错策略

```bash
# pass@k 容错
retry_with_backoff() {
  local max_attempts=$1
  local base_delay=$2  # 基础延迟（秒）

  for i in $(seq 1 $max_attempts); do
    if run_test; then
      return 0
    fi

    # 指数退避
    delay=$((base_delay * 2 ** (i-1)))
    echo "等待 ${delay}s 后重试..."
    sleep $delay
  done

  return 1
}

# 使用
retry_with_backoff 3 5  # 最多3次，基础延迟5秒
```

### 3. 结果记录

```bash
# 记录验证结果
log_validation() {
  local mode=$1  # "pass@" or "pass^"
  local k=$2
  local result=$3  # "success" or "failure"
  local duration=$4

  cat >> validation.log <<EOF
$(date): $mode$k, $result, ${duration}s
EOF
}
```

## 实战案例

### 案例 1: 03构建师代码生成

```bash
#!/bin/bash
# builder-validation.sh

TASK="生成React组件"

# pass@5: 多次尝试，至少1次成功
for attempt in {1..5}; do
  echo "🔨 代码生成尝试 $attempt/5..."

  if generate_component "$TASK"; then
    echo "✅ 代码生成成功"
    exit 0
  else
    echo "❌ 代码生成失败，重试..."
  fi
done

echo "❌ 代码生成失败（5次尝试）"
exit 1
```

### 案例 2: 05安全师安全检查

```bash
#!/bin/bash
# security-validation.sh

# pass^3: 必须全部通过

checks=(
  "SQL注入检测"
  "XSS漏洞检测"
  "密钥泄露检测"
)

for check in "${checks[@]}"; do
  echo "🔒 安全检查: $check"

  if ! run_security_check "$check"; then
    echo "❌ 安全检查失败: $check"
    echo "🚫 阻止继续"
    exit 1
  fi
done

echo "✅ 所有安全检查通过"
```

### 案例 3: 08发布师生产部署

```bash
#!/bin/bash
# production-validation.sh

# pass^3: 预发布验证

STAGES=(
  "代码审查通过"
  "所有测试通过"
  "性能测试通过"
)

for stage in "${STAGES[@]}"; do
  echo "🎯 预发布检查: $stage"

  if ! check_stage "$stage"; then
    echo "❌ 预发布失败: $stage"
    echo "🚫 阻止部署"
    exit 1
  fi
done

echo "✅ 预发布通过，可以部署"
```

## 性能优化

### 减少不必要的尝试

```bash
# 智能终止：连续失败后停止
max_consecutive_failures=3
consecutive_failures=0

for attempt in $(seq 1 10); do
  if run_test; then
    consecutive_failures=0  # 重置计数
  else
    consecutive_failures=$((consecutive_failures + 1))

    if [ $consecutive_failures -ge $max_consecutive_failures ]; then
      echo "⚠️ 连续失败 $max_consecutive_failures 次，停止验证"
      exit 1
    fi
  fi
done
```

### 并行验证

```bash
# 并行运行多个验证
validate_parallel() {
  local checks=("$@")
  local pids=()

  for check in "${checks[@]}"; do
    run_check "$check" &
    pids+=($!)
  done

  # 等待所有检查完成
  for pid in "${pids[@]}"; do
    wait $pid
  done
}

# 使用
validate_parallel "test1" "test2" "test3"
```

## 错误处理

### 失败分析

```bash
# 记录失败原因
analyze_failure() {
  local attempt=$1
  local error=$2

  cat >> failures.log <<EOF
$(date): Attempt $attempt failed
Reason: $error
Context: $(get_context)
EOF
}

# 使用
if ! run_test; then
  analyze_failure $attempt "$(get_error_message)"
fi
```

### 恢复策略

```bash
# 失败后恢复
recover_and_retry() {
  local last_successful_state=$1

  echo "🔄 恢复到上次成功状态..."
  restore_state "$last_successful_state"

  echo "♻️ 重新尝试..."
  run_test
}
```

## 监控与报告

### 实时监控

```bash
# 监控验证成功率
monitor_success_rate() {
  local mode=$1
  local k=$2

  total=$(grep -c "$mode$k" validation.log)
  success=$(grep -c "$mode$k, success" validation.log)

  rate=$(echo "scale=2; $success / $total * 100" | bc)

  echo "📊 $mode$k 成功率: $rate% ($success/$total)"
}
```

### 生成报告

```bash
# 生成验证报告
generate_report() {
  cat <<EOF
# 验证循环报告

## 验证模式统计
| 模式 | 总次数 | 成功次数 | 成功率 |
|------|--------|----------|--------|
| pass@1 | $(grep -c "pass@1" validation.log) | $(grep -c "pass@1, success" validation.log) | $(calculate_rate "pass@1") |
| pass@3 | $(grep -c "pass@3" validation.log) | $(grep -c "pass@3, success" validation.log) | $(calculate_rate "pass@3") |
| pass@5 | $(grep -c "pass@5" validation.log) | $(grep -c "pass@5, success" validation.log) | $(calculate_rate "pass@5") |
| pass^1 | $(grep -c "pass^1" validation.log) | $(grep -c "pass^1, success" validation.log) | $(calculate_rate "pass^1") |
| pass^3 | $(grep -c "pass^3" validation.log) | $(grep -c "pass^3, success" validation.log) | $(calculate_rate "pass^3") |

## 趋势分析
$(analyze_trends)

## 建议
$(generate_recommendations)
EOF
}
```

## 工具集成

### 与 CI/CD 集成

```yaml
# .github/workflows/validation.yml
name: Validation Loop

on: [pull_request, push]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run pass@3 validation
        run: |
          bash scripts/validate-pass-at.sh 3

      - name: Run Checkpoint validation
        run: |
          bash scripts/validate-checkpoint.sh
```

### 与九部天龙集成

```markdown
## 宗器使用验证循环

### 00分析师
- 模式: pass@3
- 理由: 快速迭代，91% 成功率足够

### 02架构师
- 模式: pass@3
- 理由: 方案对比，97% 成功率

### 03构建师
- 模式: pass@5
- 理由: 代码生成，100% 成功率

### 04验证师
- 模式: pass@3（功能）+ pass^5（性能）
- 理由: 功能探索 + 性能严格

### 05安全师
- 模式: pass^5
- 理由: 安全零容忍

### 08发布师
- 模式: pass^3
- 理由: 生产稳定，34% 成功率可接受（预发布验证）
```

## 参考资源

- [概率论基础](https://www.khanacademy.org/math/statistics-probability)
- [A/B 测试最佳实践](https://optimizely.com/ab-testing/)
- [CI/CD 验证策略](https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery)

---

**维护者**: 九部天龙团队
**更新日期**: 2026-02-08
**版本**: 1.0.0
