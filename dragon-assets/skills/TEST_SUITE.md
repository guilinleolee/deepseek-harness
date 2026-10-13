# 迁移验证测试套件

## 测试目的
验证 CLI + Skills 架构迁移后的功能完整性。

## 测试环境

```bash
# 检查 MCP 服务
cat c:\Users\li\.claude\mcp_servers.json | jq '.mcpServers | length'
# 预期: 4

# 检查 Skills
ls -la c:\Users\li\.claude\skills\github-cli
ls -la c:\Users\li\.claude\skills\search-cli
ls -la c:\Users\li\.claude\skills\web-fetch
```

## 测试用例

### 1. GitHub CLI 测试

#### 1.1 列出仓库 Issues
```bash
gh issue list --repo cli/cli --limit 5
# 预期: 输出 5 个 issue 列表
```

#### 1.2 创建 Issue（测试模式）
```bash
# 使用 --web 参数打开浏览器（避免实际创建）
gh issue create --repo OWNER/REPO --title "测试" --web
```

#### 1.3 查看 PR
```bash
gh pr view 123 --repo OWNER/REPO
# 预期: 显示 PR 详情
```

#### 1.4 搜索代码
```bash
gh search code --repo OWNER/REPO "TODO" --limit 10
# 预期: 输出包含 TODO 的代码列表
```

**通过标准**: 所有命令无错误输出

---

### 2. Search CLI 测试

#### 2.1 Brave Search
```bash
export BRAVE_API_KEY="BSAAXosKZM5x1_vIjBY3j2kBKOtI3Fx"

curl -s "https://api.search.brave.com/res/v1/web/search?q=test&count=5" \
  -H "X-Subscription-Token: $BRAVE_API_KEY" | jq '.web.results | length'
# 预期: 输出 5
```

#### 2.2 Exa Search
```bash
export EXA_API_KEY="a0bd7e7d-407e-4299-ba28-a7ece01d0e95"

curl -s "https://api.exa.ai/search" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-api-key: $EXA_API_KEY" \
  -d '{"query": "machine learning", "numResults": 5}' | \
  jq '.results | length'
# 预期: 输出 5
```

**通过标准**: 返回正确数量的结果

---

### 3. Web Fetch 测试

#### 3.1 HTTP GET 请求
```bash
curl -s "https://api.github.com/users/torvalds" | jq '.name'
# 预期: "Linus Torvalds"
```

#### 3.2 JSON 解析
```bash
curl -s "https://api.github.com/repos/cli/cli" | \
  jq '{name: .name, stars: .stargazers_count}'
# 预期: 输出 name 和 stars
```

#### 3.3 错误处理
```bash
curl -s "https://httpstat.us/404" | jq '.status'
# 预期: 404
```

**通过标准**: 返回预期数据

---

### 4. 核心 MCP 测试

#### 4.1 Memory MCP
```bash
# 验证 memory 目录存在
ls -la ./ai-automation-memory
# 预期: 目录存在
```

#### 4.2 Chrome MCP
```bash
# 检查 chrome-bridge 是否安装
ls -la D:/NODE/npm-global/node_modules/mcp-chrome-bridge
# 预期: 目录存在
```

#### 4.3 Sequential-thinking
```bash
# 验证 sequential-thinking MCP 可启动
npx -y @modelcontextprotocol/server-sequential-thinking --help
# 预期: 无错误
```

#### 4.4 Context7
```bash
# 验证 context7 API key
echo $CONTEXT7_API_KEY | grep -q "ctx7sk"
# 预期: 匹配成功
```

**通过标准**: 所有 MCP 可用

---

## 性能测试

### 启动时间测试

```bash
# 测试 Claude Code 启动时间（手动）
# 1. 完全关闭 Claude Code
# 2. 重新启动
# 3. 记录到可用状态的时间

# 预期: < 5 秒
```

### 内存占用测试

```bash
# Windows 任务管理器
# 观察 Claude Code 进程内存占用

# 预期: < 300MB
```

## 回归测试

### 功能对比

| 功能 | 原 MCP | 新 Skills | 状态 |
|------|--------|-----------|------|
| GitHub Issue | ✅ | ✅ | [ ] 测试 |
| GitHub PR | ✅ | ✅ | [ ] 测试 |
| Web Search | ✅ | ✅ | [ ] 测试 |
| HTTP Fetch | ✅ | ✅ | [ ] 测试 |
| Memory | ✅ | ✅ | [ ] 测试 |
| Chrome DevTools | ✅ | ✅ | [ ] 测试 |

## 自动化测试脚本

```bash
#!/bin/bash
# test-migration.sh

echo "🧪 开始迁移验证测试..."

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

# GitHub CLI 测试
run_test "gh --version" "gh --version" "gh version"

# Search API 测试
run_test "Brave API" \
  'curl -s "https://api.search.brave.com/res/v1/web/search?q=test&count=1" -H "X-Subscription-Token: $BRAVE_API_KEY"' \
  "results"

# Web Fetch 测试
run_test "HTTP GET" \
  'curl -s "https://api.github.com/users/torvalds"' \
  "Linus Torvalds"

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
```

## 测试执行

```bash
# 运行测试
bash test-migration.sh

# 或手动逐项测试
# 参考"测试用例"部分
```

## 测试报告模板

```markdown
## 迁移验证报告

**测试日期**: 2026-02-08
**测试人员**: [姓名]
**架构版本**: CLI + Skills v1.0

### 测试结果
- 总测试数: X
- 通过: X
- 失败: X
- 通过率: XX%

### 失败详情
1. [描述失败情况]
   - 预期: ...
   - 实际: ...
   - 原因: ...
   - 解决方案: ...

### 性能数据
- 启动时间: X 秒
- 内存占用: X MB
- 请求延迟: X ms

### 建议
- [ ] 修复失败项
- [ ] 性能优化
- [ ] 文档更新

### 结论
[ ] 通过 / [ ] 不通过
```

## 回滚决策树

```
测试通过率 >= 90%？
├── 是 → 继续使用新架构
└── 否 → 性能可接受？
    ├── 是 → 记录问题，继续使用
    └── 否 → 回滚到原配置
```

---

**维护者**: 九部天龙团队
**更新日期**: 2026-02-08
