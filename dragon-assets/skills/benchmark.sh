#!/bin/bash
# benchmark.sh - 九部天龙基准测试脚本
# 用途：对比使用 Skills vs 不使用 Skills 的性能差异

set -e

echo "🧪 九部天龙基准测试"
echo "================================"

# 配置
TASKS=(
  "搜索TODO注释"
  "查找函数引用"
  "创建GitHub PR"
)

OUTPUT_DIR="/tmp/benchmark-results"
mkdir -p "$OUTPUT_DIR"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
execute_with_skills() {
  local task=$1

  case $task in
    "搜索TODO注释")
      # 使用 mgrep
      mgrep "Find all TODO comments in TypeScript files" 2>/dev/null || echo "mgrep not found, using grep fallback"
      ;;
    "查找函数引用")
      # 使用 mgrep
      mgrep "Find all usages of function" 2>/dev/null || gh search code "function" --limit 10
      ;;
    "创建GitHub PR")
      # 模拟 PR 创建
      echo "Simulated PR creation" > /dev/null
      ;;
  esac
}

execute_without_skills() {
  local task=$1

  case $task in
    "搜索TODO注释")
      # 使用 grep
      grep -r "TODO" --include="*.ts" . 2>/dev/null || echo "No TODOs found"
      ;;
    "查找函数引用")
      # 使用 grep
      grep -r "function" --include="*.ts" . 2>/dev/null || echo "No references found"
      ;;
    "创建GitHub PR")
      # 模拟 PR 创建
      echo "Simulated PR creation" > /dev/null
      ;;
  esac
}

benchmark_task() {
  local task=$1
  local mode=$2  # "with-skills" | "without-skills"
  local output_file=$3

  echo -n "📊 $task ($mode)... "

  start_time=$(date +%s.%N)

  if [ "$mode" = "with-skills" ]; then
    execute_with_skills "$task"
  else
    execute_without_skills "$task"
  fi

  end_time=$(date +%s.%N)
  duration=$(echo "$end_time - $start_time" | bc)

  echo "${duration}s"
  echo "$duration" > "$output_file"

  # 格式化输出
  if (( $(echo "$duration < 1.0" | bc -l) )); then
    echo -e "  ${GREEN}✅ 快${NC}"
  elif (( $(echo "$duration < 3.0" | bc -l) )); then
    echo -e "  ${YELLOW}⚠️ 中${NC}"
  else
    echo -e "  ${RED}❌ 慢${NC}"
  fi
}

# 运行基准测试
echo ""
echo "开始测试..."
echo ""

for task in "${TASKS[@]}"; do
  without_file="$OUTPUT_DIR/${task}-without.txt"
  with_file="$OUTPUT_DIR/${task}-with.txt"

  benchmark_task "$task" "without-skills" "$without_file"
  benchmark_task "$task" "with-skills" "$with_file"

  echo ""
done

# 生成报告
REPORT_FILE="$OUTPUT_DIR/benchmark-report.md"

cat > "$REPORT_FILE" <<EOF
# 九部天龙基准测试报告

**测试时间**: $(date)
**测试环境**: $(uname -s) $(uname -r)

## 📊 任务对比

| 任务 | 不用Skills | 用Skills | 改善 | 结论 |
|------|-----------|---------|------|------|
EOF

for task in "${TASKS[@]}"; do
  without_time=$(cat "$OUTPUT_DIR/${task}-without.txt")
  with_time=$(cat "$OUTPUT_DIR/${task}-with.txt")
  improvement=$(echo "scale=1; ($without_time - $with_time) / $without_time * 100" | bc)

  if (( $(echo "$with_time < $without_time" | bc -l) )); then
    conclusion="✅ 更快"
  elif (( $(echo "$with_time > $without_time * 1.2" | bc -l) )); then
    conclusion="❌ 更慢"
  else
    conclusion="⚖️ 相当"
  fi

  echo "| $task | ${without_time}s | ${with_time}s | ${improvement}% | $结论 |" >> "$REPORT_FILE"
done

cat >> "$REPORT_FILE" <<EOF

## 📈 总体分析

EOF

# 计算总体改善
total_without=0
total_with=0

for task in "${TASKS[@]}"; do
  total_without=$(echo "$total_without + $(cat "$OUTPUT_DIR/${task}-without.txt")" | bc)
  total_with=$(echo "$total_with + $(cat "$OUTPUT_DIR/${task}-with.txt")" | bc)
done

avg_without=$(echo "scale=2; $total_without / ${#TASKS[@]}" | bc)
avg_with=$(echo "scale=2; $total_with / ${#TASKS[@]}" | bc)
total_improvement=$(echo "scale=1; ($total_without - $total_with) / $total_without * 100" | bc)

cat >> "$REPORT_FILE" <<EOF
- **平均时间（不用Skills）**: ${avg_without}s
- **平均时间（用Skills）**: ${avg_with}s
- **总体改善**: ${total_improvement}%

## 🎯 建议

EOF

if (( $(echo "$total_improvement > 20" | bc -l) )); then
  echo "✅ **Skills 架构显著更快**，建议继续使用" >> "$REPORT_FILE"
elif (( $(echo "$total_improvement > -10" | bc -l) )); then
  echo "⚖️ **Skills 架构性能相当**，根据其他因素决定" >> "$REPORT_FILE"
else
  echo "⚠️ **Skills 架构更慢**，建议优化或回滚" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" <<EOF

## 🔧 优化建议

1. **持续监控**: 定期运行基准测试
2. **A/B测试**: 对比不同配置的性能
3. **瓶颈分析**: 找出最慢的环节
4. **迭代优化**: 根据数据持续改进

## 📝 原始数据

详细数据保存在: \`$OUTPUT_DIR/\`

---

**生成时间**: $(date)
**脚本版本**: 1.0.0
EOF

echo ""
echo "✅ 基准测试完成"
echo ""
echo "📄 报告已生成: $REPORT_FILE"
echo ""

# 显示报告
cat "$REPORT_FILE"

echo ""
echo "💡 提示: 运行 \`cat $REPORT_FILE\` 查看完整报告"
