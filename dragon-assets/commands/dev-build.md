---
name: dev-build
description: 开发构建 - 项目编译打包流程
invokable: true
allowed-tools: Read, Glob, Bash, Write, Edit, TodoWrite
---
## Context

- Build tool: !`ls -la package.json Cargo.toml pom.xml build.gradle Makefile 2>/dev/null | head -3`
- Current branch: !`git branch --show-current`

## Your Task

执行构建流程：

### 步骤 1: 预检查
- 确认代码已提交或stash
- 检查环境变量配置
- 验证依赖完整性

### 步骤 2: 清理构建
```bash
# 清理旧的构建产物
npm run clean || rm -rf dist/ build/ target/
```

### 步骤 3: 类型检查
```bash
# 运行类型检查（如果有）
npm run type-check || tsc --noEmit
```

### 步骤 4: 打包构建
```bash
# 执行构建
npm run build || npm run build:prod
```

### 步骤 5: 产物验证
- 验证构建产物存在
- 检查产物大小
- 确认入口文件正确

## 构建产物检查清单

```markdown
- [ ] 构建成功无错误
- [ ] 产物文件大小合理
- [ ] Source map 生成（如需要）
- [ ] 环境变量替换正确
- [ ] Bundle 分析（如需要）
```

## 注意事项

- 生产构建不使用watch模式
- 确保Tree-shaking生效
- 验证代码分割结果
- 检查产物可被正确加载
