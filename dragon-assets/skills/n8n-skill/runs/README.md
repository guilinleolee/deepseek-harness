# 此目录用于存储每次工作流构建的运行数据

每次执行 10 步工作流构建系统时，会创建一个独立的时间戳目录，格式为：

```
runs/{timestamp}-{slug}/
```

例如：

```
runs/20260226-100000-email-notification/
```

## 目录内容

```
runs/{timestamp}-{slug}/
├── requirements.md       # Step 01: 需求规格
├── research.md           # Step 02: 研究发现
├── discussion.md         # Step 03: 讨论记录
├── knowledge.md          # Step 04: 知识库查询
├── design.md             # Step 05: 架构设计
├── workflow.json         # Step 06: 工作流构建（原始）
├── credentials-report.md # Step 07: 凭据报告
├── validation-report.md  # Step 08: 验证报告
├── deploy-report.md      # Step 09: 部署报告
├── workflow-export.json  # Step 10: 最终工作流
├── summary.md            # Step 10: 总结报告
└── progress.json         # 进度追踪
```

## 用途

1. **断点恢复**: 通过 progress.json 恢复中断的构建
2. **历史追溯**: 查看每次构建的完整过程
3. **文档记录**: 保留设计决策和实现细节
4. **问题排查**: 出现问题时可回溯查看

## 清理策略

- 建议定期归档旧的运行目录
- 保留最近 10 次运行记录
- 重要项目可以永久保存

## 示例

查看最新的运行记录：

```bash
ls -lt runs/ | head -11
```

查看特定运行的总结：

```bash
cat runs/20260226-100000-email-notification/summary.md
```

查看进度状态：

```bash
cat runs/20260226-100000-email-notification/progress.json | jq
```
