---
name: deeptutor
description: DeepTutor CLI - chat/deep_solve/quiz/deep_research/math学习辅导桥接
invokable: true
---
# /deeptutor

基于 DeepTutor 后端的 AI 学习辅导 CLI 工具。

## 命令

```bash
D:/Python310/python.exe c:/Users/li/.claude/skills/deeptutor-bridge/scripts/deeptutor_cli.py <command> [args]
```

## 子命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `chat` | RAG问答 | `chat "什么是梯度下降"` |
| `deep_solve` | 深度解题 | `deep_solve "证明勾股定理"` |
| `quiz` | 生成测验 | `quiz "微积分" -n 10 -d hard` |
| `deep_research` | 深度研究 | `deep_research "Transformer架构" --depth comprehensive` |
| `math` | 数学可视化 | `math "欧拉公式" --animate` |
| `kb list/create/add/delete/info` | 知识库管理 | `kb list` / `kb create math_kb` |
| `bot list/create/switch/delete` | TutorBot管理 | `bot list` / `bot create math_tutor` |
| `session list/new/export` | 会话管理 | `session new` / `session list` |

## 天龙引擎调用

```bash
[@07记录师] 用deeptutor查询量子计算的基本原理
[@10-02] 用deeptutor生成一道关于矩阵运算的测验题
[@01调研师] 用deeptutor deep_research研究强化学习的最新进展
```

## 依赖

```bash
pip install requests
# 需要后端服务: python -m deeptutor.api.run_server (端口8001)
```
