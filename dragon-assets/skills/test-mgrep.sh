#!/bin/bash
# test-mgrep.sh - mgrep 集成测试脚本

echo "🧪 mgrep 集成测试开始..."

# 测试计数
total=0
passed=0
failed=0

# 测试函数
run_test() {
  local name=$1
  local command=$2
  local expected=$3

  total=$((total + 1))
  echo -n "[$total] $name... "

  result=$(eval "$command" 2>&1)

  if echo "$result" | grep -q "$expected"; then
    echo "✅ PASS"
    passed=$((passed + 1))
  else
    echo "❌ FAIL"
    echo "   预期: $expected"
    echo "   实际: $result"
    failed=$((failed + 1))
  fi
}

# 1. 检查 mgrep 安装
run_test "mgrep 版本检查" \
  "mgrep --version" \
  "mgrep"

# 2. 语义搜索测试
run_test "搜索 TypeScript 文件" \
  "mgrep 'Find TypeScript files' | head -1" \
  ".ts"

# 3. 技术债务搜索
run_test "搜索 TODO 注释" \
  "mgrep 'Find TODO comments'" \
  "TODO"

# 4. 与 grep 对比
echo ""
echo "📊 性能对比测试:"

# grep 方式
start_time=$(date +%s.%N)
grep -r "import" --include="*.ts" . > /tmp/grep_result.txt 2>/dev/null
grep_time=$(echo "$(date +%s.%N) - $start_time" | bc)
grep_count=$(wc -l < /tmp/grep_result.txt)

# mgrep 方式
start_time=$(date +%s.%N)
mgrep "Find import statements in TypeScript" > /tmp/mgrep_result.txt 2>/dev/null
mgrep_time=$(echo "$(date +%s.%N) - $start_time" | bc)
mgrep_count=$(wc -l < /tmp/mgrep_result.txt)

echo "grep: ${grep_time}s (${grep_count} 结果)"
echo "mgrep: ${mgrep_time}s (${mgrep_count} 结果)"

# 计算改善百分比
if [ "$grep_time" != "0" ]; then
  improvement=$(echo "scale=1; ($grep_time - $mgrep_time) / $grep_time * 100" | bc)
  echo "速度提升: ${improvement}%"
fi

# 总结
echo ""
echo "📊 测试结果:"
echo "   总计: $total"
echo "   通过: $passed"
echo "   失败: $failed"

if [ $failed -eq 0 ]; then
  echo "✅ 所有测试通过"
  exit 0
else
  echo "❌ 有 $failed 个测试失败"
  exit 1
fi
