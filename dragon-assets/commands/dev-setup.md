---
name: dev-setup
description: 开发环境配置 - 项目初始化和环境搭建
invokable: true
allowed-tools: Read, Glob, Bash, Write, Edit, TodoWrite
---
## Context

- Project type: !`ls -la package.json pyproject.toml Cargo.toml go.mod pom.xml 2>/dev/null | head -5`
- Node version: !`node --version 2>/dev/null || echo "N/A"`
- Python version: !`python --version 2>/dev/null || echo "N/A"`

## Your Task

执行开发环境配置：

### 步骤 1: 环境检查
- 检查系统依赖
- 验证工具链版本
- 确认必要权限

### 步骤 2: 依赖安装
- 安装项目依赖
- 配置环境变量
- 设置配置文件

### 步骤 3: 环境验证
- 运行健康检查
- 验证编译构建
- 测试开发服务器

### 步骤 4: 文档更新
- 更新 README.md
- 创建 .env.example
- 记录环境要求

## 环境检查清单

```markdown
- [ ] Node.js/Python/Go 等运行时
- [ ] 数据库客户端
- [ ] Docker (如需要)
- [ ] 代码格式化工具
- [ ] Git hooks 配置
- [ ] IDE 配置同步
```

## 注意事项

- 遵循项目已有的配置约定
- 确保开发/生产环境差异明确
- 记录所有必需的环境变量
