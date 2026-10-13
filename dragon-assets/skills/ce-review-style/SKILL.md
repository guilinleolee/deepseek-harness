# ce-review-style

> **版本**: V1.0
> **来源**: EveryInc/compound-engineering-plugin/ce-review
> **整合日期**: 2026-04-11
> **天龙引擎版本**: V8.89
> **适用岗位**: 06审查师, 03构建师

## 一句话描述

基于栈特定规则的代码风格审查，根据React/Node.js/Python/Go等栈自动应用对应规范。

## L0: 核心定义

```
ce-review-style = 栈识别 → 规范匹配 → 风格检查 → 修复建议
```

## L1: 使用场景

| 场景 | 触发条件 | 执行动作 |
|------|---------|---------|
| PR审查 | 栈特定代码变更 | 自动识别栈，应用对应规范 |
| 提交前检查 | pre-commit hook | 风格问题阻止提交 |
| 批量审查 | 多个文件/多栈混合 | 分栈处理，统一报告 |

## L2: 详细文档

### 栈识别引擎

```javascript
// 栈识别规则（按优先级）
const stackPatterns = [
  { pattern: /import\s+React/, stack: 'react', weight: 3 },
  { pattern: /from\s+'react'/, stack: 'react', weight: 3 },
  { pattern: /import\s+[^;]+from\s+'@\/, stack: 'react', weight: 2 },
  { pattern: /import\s+\{[^}]+\}\s+from\s+'react'/, stack: 'react', weight: 3 },
  { pattern: /const\s+\w+:\s+React\./, stack: 'react', weight: 3 },
  { pattern: /\.jsx\b/, stack: 'react', weight: 2 },
  { pattern: /\.tsx\b/, stack: 'react', weight: 2 },
  { pattern: /node_modules\/express/, stack: 'nodejs', weight: 2 },
  { pattern: /require\s*\(\s*['"]express['"]\s*\)/, stack: 'nodejs', weight: 3 },
  { pattern: /module\.exports/, stack: 'nodejs', weight: 2 },
  { pattern: /__dirname|process\.env/, stack: 'nodejs', weight: 2 },
  { pattern: /from\s+['"]fastapi['"]/, stack: 'python', weight: 3 },
  { pattern: /from\s+['"]django['"]/, stack: 'python', weight: 3 },
  { pattern: /def\s+\w+\s*\(/, stack: 'python', weight: 1 },
  { pattern: /import\s+\w+\s+from\s+['"]@angular/, stack: 'angular', weight: 3 },
  { pattern: /import\s+\w+\s+from\s+['"]vue['"]/, stack: 'vue', weight: 3 },
  { pattern: /import\s+\w+\s+from\s+['"]svelte['"]/, stack: 'svelte', weight: 3 },
  { pattern: /package\s+main/, stack: 'go', weight: 2 },
  { pattern: /func\s+\w+\s*\(/, stack: 'go', weight: 2 },
  { pattern: /package\s+main/, stack: 'go', weight: 2 },
  { pattern: /fmt\.Print/, stack: 'go', weight: 2 },
  { pattern: /from\s+['"]torch['"]/, stack: 'pytorch', weight: 3 },
  { pattern: /from\s+['"]tensorflow['"]/, stack: 'tensorflow', weight: 3 },
  { pattern: /from\s+['"]keras['"]/, stack: 'keras', weight: 3 },
  { pattern: /import\s+jax/, stack: 'jax', weight: 3 },
];

// 识别算法
function identifyStack(filePath, fileContent) {
  const ext = path.extname(filePath);
  const extMap = {
    '.tsx': 'react', '.jsx': 'react', '.ts': 'typescript', '.js': 'nodejs',
    '.py': 'python', '.go': 'go', '.rs': 'rust', '.java': 'java',
    '.vue': 'vue', '.svelte': 'svelte'
  };

  // 1. 按文件扩展名初步判断
  const extStack = extMap[ext];
  if (extStack) return extStack;

  // 2. 按内容模式二次确认
  for (const rule of stackPatterns) {
    if (rule.pattern.test(fileContent)) {
      return rule.stack;
    }
  }

  // 3. 默认返回通用
  return 'generic';
}
```

### 栈规范库

#### React规范 (kieran-react-reviewer)

```yaml
naming:
  components: PascalCase
  hooks: camelCase with 'use' prefix
  utils: camelCase
  constants: SCREAMING_SNAKE_CASE

fileStructure:
  components: "ComponentName/index.tsx" or "ComponentName.tsx"
  hooks: "hooks/use{name}.ts"
  utils: "utils/{name}.ts"
  types: "types/{name}.ts"

patterns:
  preferred:
    - functional components with hooks
    - React.memo for pure components
    - useCallback for callbacks in deps
    - useMemo for expensive computations
    - forwardRef for ref forwarding
    - children composition over props.children
  avoided:
    - class components (new code)
    - this.setState pattern
    - findDOMNode usage
    - string refs

typescript:
  strict: true
  prefer: interfaces over types (for props)
  avoid: any type
```

#### Node.js规范 (kieran-nodejs-reviewer)

```yaml
naming:
  files: kebab-case or camelCase (保持一致)
  functions: camelCase
  classes: PascalCase
  constants: SCREAMING_SNAKE_CASE

patterns:
  preferred:
    - async/await over .then/.catch
    - error-first callbacks (for legacy)
    - try-catch around async
    - early return for error handling
    - const over let, never var
  avoided:
    - callback hell (>3 levels)
    - synchronous fs methods in request handlers
    - process.exit in library code
    - .bind in render props

security:
  - no eval()
  - sanitize user input before SQL
  - use helmet for HTTP headers
  - validate env vars at startup
```

#### Python规范 (kieran-python-reviewer)

```yaml
naming:
  modules: lowercase_with_underscores
  classes: PascalCase
  functions: lowercase_with_underscores
  constants: SCREAMING_SNAKE_CASE

style:
  guide: pep8
  max_line_length: 88 (Black default)
  quotes: double quotes preferred

patterns:
  preferred:
    - type hints for function signatures
    - dataclasses for simple data containers
    - context managers (with statement)
    - f-strings over .format()
    - path.join over string concatenation
  avoided:
    - wildcard imports (from x import *)
    - mutable default arguments
    - bare except clauses
    - = True for singleton comparison
```

#### Go规范 (kieran-go-reviewer)

```yaml
naming:
  files: lowercase_with_underscores
  functions: PascalCase (exported), camelCase (unexported)
  variables: camelCase or short names for short scope
  constants: PascalCase or camelCase

patterns:
  preferred:
    - error wrapping with fmt.Errorf("context: %w", err)
    - early return (guard clauses)
    - functional options pattern for config
    - bufio.Scanner for line-by-line
    - io.Copy for streaming
  avoided:
    - panic for normal error handling
    - blank identifiers for ignored returns
    - init() functions (hard to test)
    - goroutine leaks (always provide exit)

format:
  - gofmt must pass
  - golint/gci for import organization
  - errcheck for unchecked errors
```

### 检查执行流程

```javascript
// ce-review-style 检查流程
async function performStyleCheck(files, options = {}) {
  const {
    stack = 'auto',           // 'auto' 或指定栈
    mode = 'report',          // 'report' | 'fix' | 'strict'
    severity = 'warning',     // 'error' | 'warning' | 'info'
    autoFix = false
  } = options;

  const results = [];
  const fixes = [];

  // 1. 批量栈识别
  const fileStacks = new Map();
  for (const file of files) {
    const identified = stack === 'auto'
      ? identifyStack(file.path, file.content)
      : stack;
    fileStacks.set(file.path, identified);
  }

  // 2. 按栈分组
  const groupedByStack = groupBy(files, f => fileStacks.get(f.path));

  // 3. 分栈执行检查
  for (const [stackName, stackFiles] of groupedByStack) {
    const spec = stackSpecs[stackName] || stackSpecs.generic;

    for (const file of stackFiles) {
      const findings = checkFile(file, spec);

      for (const finding of findings) {
        if (finding.severity === 'error' ||
            (finding.severity === 'warning' && severity !== 'info')) {
          results.push({
            file: file.path,
            stack: stackName,
            ...finding
          });

          if (autoFix && finding.canFix) {
            fixes.push({
              file: file.path,
              original: finding.code,
              fixed: applyFix(finding)
            });
          }
        }
      }
    }
  }

  // 4. 输出报告
  return {
    summary: {
      total: files.length,
      byStack: countBy(groupedByStack),
      findings: results.length,
      bySeverity: countBySeverity(results)
    },
    findings: results,
    fixes: autoFix ? fixes : []
  };
}

// 检查器注册表
const checkers = {
  react: [
    { rule: 'component-name', check: checkComponentNaming },
    { rule: 'hooks-prefix', check: checkHooksNaming },
    { rule: 'prop-types', check: checkPropsType },
    { rule: 'deps-complete', check: checkUseEffectDeps },
    { rule: 'pure-component', check: checkPureComponent },
  ],
  nodejs: [
    { rule: 'async-pattern', check: checkAsyncAwait },
    { rule: 'error-handling', check: checkErrorHandling },
    { rule: 'security', check: checkSecurityIssues },
  ],
  python: [
    { rule: 'naming', check: checkNamingConventions },
    { rule: 'type-hints', check: checkTypeHints },
    { rule: 'imports', check: checkImports },
  ],
  go: [
    { rule: 'error-wrap', check: checkErrorWrapping },
    { rule: 'goroutine-safe', check: checkGoroutineSafety },
  ]
};
```

### 输出格式

```yaml
# ce-review-style 输出报告模板
---
title: "代码风格审查报告"
date: "YYYY-MM-DD HH:mm"
files_analyzed: 12
stacks_detected:
  react: 5
  nodejs: 4
  python: 2
  go: 1
summary:
  total_findings: 8
  by_severity:
    error: 1
    warning: 4
    info: 3
  by_stack:
    react: 3
    nodejs: 3
    python: 1
    go: 1
findings:
  - file: "src/components/Button.tsx"
    stack: react
    line: 15
    rule: "component-name"
    severity: error
    message: "组件名 'button' 应使用 PascalCase: 'Button'"
    can_fix: true
  - file: "src/hooks/useAuth.ts"
    stack: react
    line: 8
    rule: "hooks-prefix"
    severity: warning
    message: "Hook名 'getAuth' 应以 'use' 开头"
    can_fix: false
    suggestion: "重命名为 'useGetAuth' 或合并到 'useAuth'"
fixes_applied: 0
fixes_available: 1
---
```

### 与06审查师集成

```yaml
# 在06审查师触发
/ce-review-style --files "src/**/*.tsx" --mode report
/ce-review-style --files "src/**/*.ts" --stack react --mode fix --auto-fix

# 在CI/CD中集成
ce-review-style:
  command: npx ce-review-style --reporter github-pr
  files: ${{ github.event.pull_request.changed_files }}
```

## 使用示例

### 示例1: 自动栈识别

```bash
# 分析整个仓库，自动识别栈
npx ce-review-style analyze ./src

# 输出:
# Analyzing 45 files...
# Stack distribution:
#   react: 23 files (51%)
#   nodejs: 15 files (33%)
#   python: 5 files (11%)
#   go: 2 files (4%)
#
# Findings: 12 issues (1 error, 7 warnings, 4 info)
```

### 示例2: 指定栈审查

```bash
# 只审查React代码
npx ce-review-style check "src/**/*.tsx" --stack react --severity error

# 只审查Python代码
npx ce-review-style check "services/**/*.py" --stack python
```

### 示例3: 自动修复

```bash
# 预览修复
npx ce-review-style fix "src/**/*.tsx" --preview

# 应用修复
npx ce-review-style fix "src/**/*.tsx" --apply

# 输出:
# Applying fixes...
# [FIXED] Button.tsx:15 - component-name → 'Button'
# [PREVIEW] useAuth.ts:8 - hooks-prefix (manual change required)
```

### 示例4: CI集成

```yaml
# .github/workflows/style-check.yml
name: Code Style Check
on: [pull_request]
jobs:
  style:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npx ce-review-style check "src/**/*.{ts,tsx}" --reporter github-pr --fail-on error
```

## 规范对比矩阵

| 维度 | React | Node.js | Python | Go |
|------|-------|---------|--------|-----|
| **命名约定** | PascalCase组件 | camelCase函数 | snake_case函数 | PascalCase导出 |
| **类型检查** | TypeScript必须 | TypeScript推荐 | type hints可选 | 静态类型 |
| **错误处理** | Error Boundaries | try-catch/回调 | try-except | error返回值 |
| **代码组织** | 按功能/页面 | 按职责/层 | 按模块/包 | 按包/域 |
| **测试位置** | 组件旁或__tests__ | tests目录 | tests目录 | _test.go旁 |

## 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| **栈特定检查覆盖率** | 无 | 5栈(R/N/P/G/通用) | 质的飞跃 |
| **风格一致性** | 手动 | 自动 | +300% |
| **PR审查效率** | 30分钟 | 5分钟 | +500% |
| **自动修复率** | 无 | ~70% | 新增能力 |

## 文件结构

```
ce-review-style/
├── SKILL.md                    # 本文件
├── SPEC.md                     # 栈规范详细定义
├── stack-detector.js           # 栈识别引擎
├── checkers/
│   ├── index.js               # 检查器注册表
│   ├── react.js               # React检查器
│   ├── nodejs.js              # Node.js检查器
│   ├── python.js              # Python检查器
│   └── go.js                 # Go检查器
├── cli.js                     # CLI入口
└── templates/
    └── report.md             # 报告模板
```
