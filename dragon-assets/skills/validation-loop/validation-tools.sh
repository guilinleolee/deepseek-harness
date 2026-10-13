#!/bin/bash
# validation-tools.sh - 验证循环工具库
# 提供验证循环的核心功能：pass@k、pass^k、评估、基准测试

set -e

# ============================================
# 核心验证函数
# ============================================

# pass@k: 至少 1 次成功即通过
# 参数: $1=k(尝试次数), $2=test_command(测试命令), $3=description(描述)
# 返回: 0=通过, 1=失败
pass_at_k() {
  local k=$1
  local test_command=$2
  local description=$3

  echo "🔍 pass@${k} 验证: $description"

  for attempt in $(seq 1 $k); do
    echo "  尝试 $attempt/$k..."

    if eval "$test_command"; then
      echo "  ✅ 尝试 $attempt 成功，通过验证"
      return 0
    fi

    echo "  ⚠️  尝试 $attempt 失败，继续..."
  done

  echo "  ❌ ${k}次尝试全部失败，验证未通过"
  return 1
}

# pass^k: 全部成功才通过
# 参数: $1=k(尝试次数), $2=test_command(测试命令), $3=description(描述)
# 返回: 0=通过, 1=失败
pass_pow_k() {
  local k=$1
  local test_command=$2
  local description=$3

  echo "🎯 pass^${k} 严格验证: $description"

  local success_count=0

  for attempt in $(seq 1 $k); do
    echo "  严格验证 $attempt/$k..."

    if eval "$test_command"; then
      success_count=$((success_count + 1))
      echo "  ✅ 尝试 $attempt 成功 ($success_count/$k)"
    else
      echo "  ❌ 尝试 $attempt 失败，验证不通过"
      return 1
    fi
  done

  echo "  🎉 ${k}次尝试全部成功，通过严格验证"
  return 0
}

# ============================================
# 性能测量函数
# ============================================

# 测量命令执行时间
# 参数: $1=command(要测量的命令)
# 返回: 时间(秒)
measure_time() {
  local command=$1

  local start_time=$(date +%s.%N)
  eval "$command" > /dev/null 2>&1
  local end_time=$(date +%s.%N)

  echo "$end_time - $start_time" | bc
}

# 计算改善百分比
# 参数: $1=baseline(基线时间), $2=current(当前时间)
# 返回: 改善百分比
calculate_improvement() {
  local baseline=$1
  local current=$2

  if [ "$baseline" = "0" ]; then
    echo "0.0"
    return
  fi

  echo "scale=1; ($baseline - $current) / $baseline * 100" | bc
}

# ============================================
# 评估策略函数
# ============================================

# Checkpoint-Based Evaluation
# 按顺序执行多个检查点
# 参数: $1=checkpoints_json(JSON格式的检查点配置)
run_checkpoint_evaluation() {
  local checkpoints_json=$1
  local total_checkpoints=$(echo "$checkpoints_json" | jq '. | length')
  local passed=0
  local failed=0

  echo "📋 Checkpoint-Based 评估开始"
  echo "总检查点: $total_checkpoints"
  echo ""

  for i in $(seq 0 $(($total_checkpoints - 1))); do
    local cp=$(echo "$checkpoints_json" | jq ".[$i]")
    local name=$(echo "$cp" | jq -r '.name')
    local mode=$(echo "$cp" | jq -r '.mode')
    local k=$(echo "$cp" | jq -r '.k')
    local command=$(echo "$cp" | jq -r '.command')

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "检查点 $((i+1))/$total_checkpoints: $name"

    if [ "$mode" = "pass_at" ]; then
      if pass_at_k "$k" "$command" "$name"; then
        passed=$((passed + 1))
        echo "  ✅ 通过"
      else
        failed=$((failed + 1))
        echo "  ❌ 失败"
      fi
    elif [ "$mode" = "pass_pow" ]; then
      if pass_pow_k "$k" "$command" "$name"; then
        passed=$((passed + 1))
        echo "  ✅ 通过"
      else
        failed=$((failed + 1))
        echo "  ❌ 失败"
      fi
    fi

    echo ""
  done

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📊 评估结果: $passed 通过, $failed 失败"

  if [ $failed -eq 0 ]; then
    echo "🎉 所有检查点通过"
    return 0
  else
    echo "⚠️  有 $failed 个检查点失败"
    return 1
  fi
}

# Continuous Evaluation
# 持续执行测试，直到达到时间限制
# 参数: $1=duration_minutes(持续时间), $2=interval_seconds(间隔), $3=test_command(测试命令)
run_continuous_evaluation() {
  local duration_minutes=$1
  local interval_seconds=$2
  local test_command=$3

  local end_time=$(($(date +%s) + duration_minutes * 60))
  local run_count=0
  local passed=0
  local failed=0

  echo "🔄 Continuous 评估开始"
  echo "持续时间: ${duration_minutes}分钟"
  echo "测试间隔: ${interval_seconds}秒"
  echo ""

  while [ $(date +%s) -lt $end_time ]; do
    run_count=$((run_count + 1))
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "运行 #$run_count ($(date +%H:%M:%S))"

    if eval "$test_command"; then
      passed=$((passed + 1))
      echo "✅ 通过"
    else
      failed=$((failed + 1))
      echo "❌ 失败"
    fi

    local remaining=$((end_time - $(date +%s)))
    echo "⏱️  剩余: $((remaining / 60))分 $((remaining % 60))秒"
    echo ""

    if [ $remaining -gt $interval_seconds ]; then
      sleep $interval_seconds
    fi
  done

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📊 持续评估结果:"
  echo "  总运行: $run_count"
  echo "  通过: $passed"
  echo "  失败: $failed"
  echo "  成功率: $(echo "scale=1; $passed * 100 / $run_count" | bc)%"

  return 0
}

# ============================================
# A/B Testing 函数
# ============================================

# 对比两种方法的性能
# 参数: $1=method_a(方法A命令), $2=method_b(方法B命令), $3=iterations(迭代次数)
run_ab_test() {
  local method_a=$1
  local method_b=$2
  local iterations=$3

  echo "📊 A/B Testing 开始"
  echo "迭代次数: $iterations"
  echo ""

  # 测试方法 A
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "测试方法 A..."
  local total_time_a=0
  for i in $(seq 1 $iterations); do
    echo "  运行 $i/$iterations..."
    local time=$(measure_time "$method_a")
    total_time_a=$(echo "$total_time_a + $time" | bc)
  done
  local avg_time_a=$(echo "scale=3; $total_time_a / $iterations" | bc)
  echo "  平均时间: ${avg_time_a}s"
  echo ""

  # 测试方法 B
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "测试方法 B..."
  local total_time_b=0
  for i in $(seq 1 $iterations); do
    echo "  运行 $i/$iterations..."
    local time=$(measure_time "$method_b")
    total_time_b=$(echo "$total_time_b + $time" | bc)
  done
  local avg_time_b=$(echo "scale=3; $total_time_b / $iterations" | bc)
  echo "  平均时间: ${avg_time_b}s"
  echo ""

  # 计算改善
  local improvement=$(calculate_improvement "$avg_time_a" "$avg_time_b")

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📈 A/B Testing 结果:"
  echo "  方法 A: ${avg_time_a}s"
  echo "  方法 B: ${avg_time_b}s"
  echo "  改善: ${improvement}%"

  if [ "$(echo "$improvement > 0" | bc)" -eq 1 ]; then
    echo "  ✅ 方法 B 更快"
  else
    echo "  ⚠️  方法 A 更快"
  fi

  return 0
}

# ============================================
# 概率计算函数
# ============================================

# 计算 pass@k 的理论成功率
# 参数: $1=p(单次成功率), $2=k(尝试次数)
calc_pass_at_probability() {
  local p=$1
  local k=$2

  # P(at least 1) = 1 - (1-p)^k
  echo "scale=3; 1 - (1 - $p) ^ $k" | bc
}

# 计算 pass^k 的理论成功率
# 参数: $1=p(单次成功率), $2=k(尝试次数)
calc_pass_pow_probability() {
  local p=$1
  local k=$2

  # P(all) = p^k
  echo "scale=3; $p ^ $k" | bc
}

# 生成概率对比表
# 参数: $1=k(尝试次数)
generate_probability_table() {
  local k=$1

  echo "📊 概率对比表 (k=$k)"
  echo ""
  printf "%-10s | %-12s | %-12s\n" "单次成功率" "pass@${k}" "pass^${k}"
  echo "----------------------------------------"

  for p in 0.5 0.6 0.7 0.8 0.9; do
    local pass_at=$(calc_pass_at_probability $p $k)
    local pass_pow=$(calc_pass_pow_probability $p $k)
    printf "%-10s | %-12s | %-12s\n" \
      "$(echo "scale=0; $p * 100" | bc)%" \
      "$(echo "scale=1; $pass_at * 100" | bc)%" \
      "$(echo "scale=1; $pass_pow * 100" | bc)%"
  done
}

# ============================================
# 报告生成函数
# ============================================

# 生成验证报告
# 参数: $1=output_file(输出文件), $2=test_data(测试数据JSON)
generate_validation_report() {
  local output_file=$1
  local test_data=$2

  cat > "$output_file" <<EOF
# 验证循环测试报告

**生成时间**: $(date)
**测试版本**: 1.0.0

## 📊 测试概览

$(echo "$test_data" | jq -r '.overview')

## 🔍 详细结果

### pass@k 测试

| 测试名称 | k | 成功次数 | 失败次数 | 成功率 |
|---------|---|---------|---------|--------|
$(echo "$test_data" | jq -r '.pass_at_tests[] | "| \(.name) | \(.k) | \(.successes) | \(.failures) | \(.success_rate) |"')

### pass^k 测试

| 测试名称 | k | 成功次数 | 失败次数 | 成功率 |
|---------|---|---------|---------|--------|
$(echo "$test_data" | jq -r '.pass_pow_tests[] | "| \(.name) | \(.k) | \(.successes) | \(.failures) | \(.success_rate) |"')

## 📈 性能对比

| 方法 | 平均时间 | 改善 |
|------|---------|------|
$(echo "$test_data" | jq -r '.performance[] | "| \(.method) | \(.avg_time)s | \(.improvement)% |"')

## 💡 建议

$(echo "$test_data" | jq -r '.recommendations')

---

**生成者**: 九部天龙验证循环系统
EOF

  echo "📄 报告已生成: $output_file"
}

# ============================================
# CLI 接口
# ============================================

# 显示帮助信息
show_help() {
  cat <<EOF
验证循环工具库 v1.0.0

用法:
  validation-tools.sh <command> [options]

命令:
  pass-at <k> <command> <description>     执行 pass@k 验证
  pass-pow <k> <command> <description>    执行 pass^k 验证
  checkpoint <config.json>                执行 Checkpoint-Based 评估
  continuous <minutes> <interval> <cmd>   执行 Continuous 评估
  ab-test <method_a> <method_b> <n>       执行 A/B 测试
  probability <k>                         显示概率对比表
  report <output.json> <output.md>        生成验证报告

示例:
  # pass@3 验证
  validation-tools.sh pass-at 3 "npm test" "单元测试"

  # pass^2 严格验证
  validation-tools.sh pass-pow 2 "make build" "构建验证"

  # Checkpoint 评估
  validation-tools.sh checkpoint checkpoints.json

  # A/B 测试
  validation-tools.sh ab-test "grep -r 'TODO'" "mgrep 'Find TODO'" 10

  # 概率表
  validation-tools.sh probability 3

EOF
}

# 主入口
case "${1:-}" in
  pass-at)
    pass_at_k "$2" "$3" "$4"
    ;;
  pass-pow)
    pass_pow_k "$2" "$3" "$4"
    ;;
  checkpoint)
    run_checkpoint_evaluation "$(cat "$2")"
    ;;
  continuous)
    run_continuous_evaluation "$2" "$3" "$4"
    ;;
  ab-test)
    run_ab_test "$2" "$3" "$4"
    ;;
  probability)
    generate_probability_table "$2"
    ;;
  report)
    generate_validation_report "$2" "$(cat "$3")"
    ;;
  help|--help|-h)
    show_help
    ;;
  *)
    show_help
    exit 1
    ;;
esac
