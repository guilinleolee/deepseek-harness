# Git提交规范 Skill

## 概述
提供标准化的Git提交信息格式规范，包含格式验证、模板生成和自动化检查功能。

## 核心功能

### 1. 提交信息格式规范
支持多种主流的提交信息格式：
- Conventional Commits (推荐)
- Angular 规范
- 自定义格式模板

### 2. 格式验证
- 实时验证提交信息格式
- 检查必要字段完整性
- 长度和格式限制检查

### 3. 模板生成
- 根据类型自动生成提交信息模板
- 提供常用场景的预设模板
- 支持自定义模板配置

### 4. 自动化集成
- Git hooks 集成
- CI/CD 流程集成
- IDE 插件支持

## 使用方法

### 基本使用
```
git-commit-standard --type feat --description "添加用户登录功能" --scope auth
```

### 交互式生成
```
git-commit-standard --interactive
```

### 验证提交信息
```
git-commit-standard --validate "feat(auth): 添加用户登录功能"
```

### 安装Git hooks
```
git-commit-standard --install-hooks
```

## 配置文件
项目根目录创建 `.git-commit-standard.json`:

```json
{
  "format": "conventional",
  "types": ["feat", "fix", "docs", "style", "refactor", "test", "chore"],
  "scopes": ["auth", "api", "ui", "utils"],
  "maxLength": 100,
  "requireScope": false,
  "requireDescription": true
}
```

## 支持的提交类型

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 重构代码
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动
- `perf`: 性能优化
- `ci`: CI配置文件和脚本的变动
- `build`: 构建系统或外部依赖的变动

## 模板示例

### Conventional Commits格式
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### 示例
```
feat(auth): 添加用户登录功能

实现了基于JWT的用户认证系统：
- 用户登录接口
- Token生成和验证
- 登录状态管理

Closes #123
```

## 自动化检查

### Pre-commit Hook
```bash
#!/bin/sh
git-commit-standard --validate "$(git log -1 --pretty=%B)"
```

### CI集成
```yaml
# .github/workflows/commit-check.yml
name: Commit Message Check
on: [push, pull_request]
jobs:
  check-commits:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check commit messages
        run: git-commit-standard --check-all
```

## 最佳实践

1. **使用现在时态**: "添加" 而不是 "添加了"
2. **描述具体改动**: 避免模糊的描述
3. **关联issue**: 使用 `Closes #123` 格式
4. **保持简洁**: 标题不超过50字符，正文不超过72字符
5. **原子性提交**: 每次提交只做一件事

## 团队协作

### 统一配置
在团队中共享 `.git-commit-standard.json` 配置文件，确保所有成员使用相同的规范。

### 代码审查
使用统一的提交规范便于代码审查和生成变更日志。

### 变更日志生成
```bash
git-commit-standard --changelog --since "v1.0.0"
```

## 故障排除

### 常见问题
1. 提交信息过长 → 检查字符限制
2. 缺少必要字段 → 查看格式要求
3. 类型不支持 → 检查配置文件中的类型列表

### 调试模式
```bash
git-commit-standard --debug --validate "提交信息"
```