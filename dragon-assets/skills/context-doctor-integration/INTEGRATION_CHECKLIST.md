# Context Doctor Integration · 11 项上线 Checklist（天龙阶段 26）

> **执行人**：老李（DSH 宿主页）+ 40-01 上下文治理师（自动化审计）
> **完成日期**：_______

---

## 一、DSH 宿主页执行（老李手动 · 5 项）

| # | 步骤 | 命令 | 预期 | ✅ |
|---|------|------|------|----|
| 1 | 检查 DSH 版本 | `dsh --version` | ≥ 0.1.0-rc.6 或 0.1.1-rc.x | [ ] |
| 2 | 安装插件 | `dsh plugin --profile web add "github:Zhenyu98/dsh-context-doctor#main"` | stderr 无报错 | [ ] |
| 3 | 验证合成树 | `dsh --profile web --dump-config \| grep context-doctor` | 看到 `- id: context-doctor` | [ ] |
| 4 | 重启 dsh web | `Ctrl+C` + `dsh web` | 启动成功 | [ ] |
| 5 | 验证 Web UI | 进已有会话，看 composer 左侧圆环 | 看到 Context Doctor 控件 | [ ] |

---

## 二、首次 Audit（模型自动 · 4 项）

| # | 步骤 | 命令 | 预期 | ✅ |
|---|------|------|------|----|
| 6 | 跑摘要 | 在 DSH 新会话让模型调 `context_audit` | 返回分节报告 | [ ] |
| 7 | 跑详情 | `context_audit detail=developer` | 返回含 receipt 的完整报告 | [ ] |
| 8 | 跑正文 | `context_audit includeSkillBodies=true maxSkillBodies=20` | 返回技能正文总 token | [ ] |
| 9 | 跑冲突 | 检查 `conflicts[]` 字段 | 列出 rank shadow 列表 | [ ] |

---

## 三、归档基准（40-01 自动 · 2 项）

| # | 步骤 | 命令 | 预期 | ✅ |
|---|------|------|------|----|
| 10 | 存基准报告 | `~/.dsh/audit/2026-08-23-baseline.json` | JSON 文件落盘 | [ ] |
| 11 | 写主题文件 | `memory/context-doctor-integration.md` | 含本次基准数据 + 累计 PASS | [ ] |

---

## 四、问题速查（FAQ）

**装不上？**
- 看 `dsh plugin --profile web add` 的 stderr，常见原因：网络不通 / DSH 版本不匹配
- 解决：升级 DSH 到最新 rc 版

**圆环不显示？**
- 必须重启 dsh web + 必须进**已有会话**（new session 无 sessionId 时不显示会话级控件）

**工具调不动？**
- headless 模式（无 httpServer）下圆环不显示，但 `context_audit` 工具照常可用
- 优先用工具审计

**Audit 结果与计量条对不上？**
- 正常。context-doctor 用启发式估算（ASCII 4字符/token · 中文 1.5字符/token）
- 计量条是模型 tokenizer 的精确值
- 用于**相对比较**，不要追求数字一致

---

## 五、回归验证（每 7 天一次）

- [ ] catalog 总描述 token ≤ 3000（baseline 4k+ 应有显著下降）
- [ ] 指令链总 token ≤ 8000（baseline 65k 应有显著下降）
- [ ] MCP 工具面 token ≤ 4000 且 ≤ 20 个工具
- [ ] 无新增 high 严重度告警
- [ ] 重复段落数 ≤ baseline 的 50%
