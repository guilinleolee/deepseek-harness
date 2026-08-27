# context_audit 调用模板（DSH 模型提示词）

> **使用场景**：在 DSH 会话里直接复制粘贴下面任一提示词到发送框，模型会自动调 `context_audit` 工具并返回报告。

---

## 模板 1：首次基线审计（推荐首次跑）

```
请运行 context_audit（detail=developer），把完整报告贴回对话。
特别关注：
1. 指令链总 token 是否偏高（>8k 应报警）
2. 技能 catalog 描述 token 是否偏高（>3k 应报警）
3. MCP 工具面是否有膨胀（>20 个工具 或 >4k token 应报警）
4. 是否有同名 skill shadow 冲突
5. 是否有跨文件重复段落
最后给一个"今日上下文健康度评分"（0-100）。
```

---

## 模板 2：周度回归对比

```
请运行 context_audit（detail=developer，includeSkillBodies=true maxSkillBodies=20）。

与 7 天前的基线对比：
1. 指令链总 token 变化量（应 ≤ baseline + 5%）
2. 技能 catalog 描述 token 变化量（应 ≤ baseline + 10%）
3. MCP 工具面新增工具（应明确说明新增来源）
4. 新增 high 严重度告警（必须为 0）
5. 重复段落变化（应有收敛）

输出"本周上下文治理周报"，含 3 张表格：
- 表 1: 本周 vs 上周 4 项 token 对比
- 表 2: 本周 high/medium/low 告警清单
- 表 3: 本周执行 / 待执行 / 已跳过的裁剪建议
```

---

## 模板 3：上线前 Skill 审计

```
我准备发布新 skill「[skill_name]」，请运行 context_audit 帮我做上线前体检：
1. 新 skill 加入后，catalog 描述 token 总增量
2. 是否会触发 catalog 阈值告警（>3k → medium）
3. 是否有同名 skill shadow 冲突
4. 是否有 MCP 工具面新增
5. 新 skill description 是否与已有 skill 重复

输出"上线风险评估"：通过 / 有条件通过 / 不通过。
```

---

## 模板 4：Agent 上线前 Schema 审计

```
我准备让 agent「[agent_name]」上线，请运行 context_audit 帮我评估：
1. 当前 agent 可见工具总数与 schema token
2. MCP 工具面是否在该 agent 上下文内膨胀
3. 加载该 agent 后指令链总 token 变化

特别关注：可见工具数 >40 应报警（>10k token 高严重度）。
```

---

## 模板 5：headless / CLI 模式（无 Web UI）

```
环境无 httpServer（dsh --profile headless），请直接调 context_audit 工具。

如需把报告落盘：
1. 把 report JSON 写到 ~/.dsh/audit/YYYY-MM-DD-HHMM.json
2. 把 renderReport() 的 markdown 文本写到 ~/.dsh/audit/YYYY-MM-DD-HHMM.md
3. 在控制台只打印摘要（suggestions 与 conflicts 计数 + high 告警列表）
```

---

## 模板 6：裁剪建议执行确认

```
context_audit 返回了 N 条裁剪建议，请按以下原则处理：

【立刻执行】high 严重度：
- 指令链 >8k → 拆分到分层 AGENTS.md，删除重复段落
- MCP 工具面 >20 个 → 关闭非必要 MCP server
- catalog 描述 >3k → 缩短 description 至 ≤80 字 / 合并同类

【本周处理】medium 严重度：
- 重复段落 / 重复描述 → 合并到一处，其余改链接
- 同名 skill shadow → 删除被 shadow 的低优先级源

【回退 / 跳过】low 严重度：
- 可见工具 >40 但无明显膨胀 → 保留观察
- 技能正文 >20k token → 默认按需加载不调整

每执行一条建议，请重跑一次 context_audit 验证 token 变化。
```

---

## 模板 7：阶段结束审计报告（每阶段末尾必跑）

```
本阶段（阶段 N）已结束，请跑 context_audit（detail=developer，includeSkillBodies=true maxSkillBodies=30），
输出"阶段 N 上下文审计报告"，归档到 analysis/STAGE_Nx_CONTEXT_AUDIT.md。

报告必须含：
- 阶段 N 启动前 vs 结束的 4 项 token 对比表
- 本阶段新增 skill / agent 对 catalog 的影响
- 本阶段删除/合并/裁剪的资产清单
- 下阶段预估 token 预算

作为该阶段 COMPLETION_REPORT 的附件。
```

---

## 关键参数速查

| 参数 | 取值 | 说明 |
|------|------|------|
| `cwd` | 默认当前会话 cwd | 可指定其他目录审计 |
| `includeSkillBodies` | `false`（默认）/ `true` | true 会逐个加载技能正文统计（较慢）|
| `maxSkillBodies` | 20（默认）· 上限 100 | includeSkillBodies=true 时有效 |
| `detail` | `summary`（默认）/ `developer` | developer 额外附 receipt（可定位的条目）|

---

## 阈值表（来自上游 buildSuggestions）

| 触发条件 | 严重度 | 建议 |
|----------|--------|------|
| 指令链总 token > 8000 | **high** | 精简 AGENTS.md/CLAUDE.md，删除跨层重复 |
| 技能 catalog 描述 > 3000 token | medium | 缩短 description 或减少技能数量 |
| 重复段落 ≥ 2 个文件 | medium | 只保留一处，其余改链接 |
| 重复描述 ≥ 2 个技能 | medium | 合并或差异化描述 |
| MCP 工具 > 20 个 或 schema > 4000 token | **high** | 裁剪不需要的 MCP server/工具 |
| 可见工具 > 40 | low | 检查是否全部需要 |
| 同名 skill 多来源 | medium | 删除被 shadow 的低优先级源 |
