---
name: deploy
description: 部署到生产环境
invokable: true
allowed-tools: Bash(npm test:*), Bash(pytest:*), Bash(docker build:*), Bash(docker push:*), Bash(kubectl apply:*), Bash(kubectl rollout:*)
---
## Context

- Current git status: !`git status`
- Current git diff: !`git diff HEAD`
- Current branch: !`git branch --show-current`

## Your task

执行完整的生产环境部署流程：

### 步骤 1: 运行测试
确保所有测试通过后再部署。

### 步骤 2: 构建Docker镜像
使用最新的代码构建Docker镜像，标签包含 git commit hash。

### 步骤 3: 推送到registry
将镜像推送到容器镜像仓库。

### 步骤 4: 更新k8s配置
使用 `kubectl apply` 更新 Kubernetes 配置，并执行滚动更新。

## 注意事项

- 任何步骤失败则停止部署
- 部署前必须确认不在 main/master 分支直接操作
- 部署完成后验证服务健康状态
