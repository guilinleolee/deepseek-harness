---
name: refactor-code
description: 代码重构 - 提升代码质量而不改变外部行为
invokable: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, TodoWrite
---
## Context

- Target files: !`echo "请指定要重构的文件或目录"`
- Code climate: !`ls -la .codeclimate.yml eslint.config.* .eslintrc* 2>/dev/null || echo "无代码检查配置"`

## Your Task

执行代码重构：

### 步骤 1: 现状分析
```bash
# 分析代码复杂度
npx complexity-report src/

# 检查代码风格
npm run lint

# 运行测试确保正常
npm test
```

### 步骤 2: 识别问题
- **重复代码**: 提取公共函数/组件
- **过长函数**: 拆分为小函数
- **过多参数**: 使用配置对象或类
- **命名不清**: 重命名为描述性名称
- **紧耦合**: 引入抽象解耦

### 步骤 3: 制定重构计划
```markdown
## 重构计划

### Phase 1: 提取公共函数
- [ ] functionA 和 functionB 提取为 useSharedFunction
- [ ] 更新所有调用点

### Phase 2: 简化参数
- [ ] 将 10 个参数改为配置对象
- [ ] 添加类型定义

### Phase 3: 命名优化
- [ ] `fn` → `calculateTotalPrice`
- [ ] `temp` → `pendingTransactions`
```

### 步骤 4: 小步执行
```bash
# 每次重构后运行测试
npm test -- --watch

# 保持重构原子性
git commit -m "refactor: 简化XX函数的参数"
```

### 步骤 5: 验证重构
```bash
# 运行完整测试
npm test

# 检查覆盖率
npm run coverage

# 审查代码
npm run lint
```

## 重构安全准则

| 原则 | 说明 |
|------|------|
| 童子军规则 | 每次离开时比来时更干净 |
| 祖母测试 | 重构后能向祖母解释代码 |
| 三次法则 | 发现三次重复才提取 |
| YAGNI | 不要过度设计 |

## 注意事项

- 重构前必须有测试保护
- 小步提交，便于回滚
- 保持重构和功能分离
- 重构后运行完整测试套件
