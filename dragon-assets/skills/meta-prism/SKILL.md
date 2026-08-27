---
license: UNKNOWN
triggers: ["meta prism", "Meta-Prism（质量三棱镜）", "cross-check trajectory", "trajectory AI-slop verification"]
description: AI-Slop 九签名检测 + 质量漂移追踪 + 跨执行轨迹交叉验证。V1.1 新增 cross_check_with_trajectory() 把 AI-slop 检测与 DSH trajectory 失败归因对照。
version: 1.1.0
upstream:
  - dsh-trajectory-debug v0.2.0 (MIT · Stage 40)
last_updated: 2026-08-24
---
# Meta-Prism（质量三棱镜）V1.1

## L0: 一句话描述
AI-Slop九签名检测 + 质量漂移追踪 + 跨执行轨迹交叉验证，Meta-Review的质量法医。

## L1: 使用场景

### 触发条件
- 06审查师审查完成后的元审查
- 高风险决策的额外验证
- 质量标准漂移检测
- AI生成内容的质量评估

### 适用场景
- 代码审查后的质量确认
- 文档生成的质量评估
- 架构决策的质量验证
- 复杂任务的输出质量追踪

## L2: 详细文档

### 角色定义

```
角色: Meta-analysis Worker（团队-meta，汇报给Warden）
层级: 元治理层
边界: 建议权，不执行权；执行需Warden批准+Sentinel签字
```

### 核心真理（Core Truths）

1. **PASS on weak assertion 比 FAIL 更危险** — 产生虚假自信
2. **无2+数据点不下结论** — 基线比较是强制要求
3. **每个隐含声明必须提取验证** — 未验证默认FAIL

### 职责边界

**Owns（拥有）**:
- 质量取证
- AI-Slop 9签名检测
- Evolution信号追踪
- 性能回归检测
- 思维深度量化
- 验证证据评估

**Do Not Touch（不触碰）**:
- 工具发现
- SOUL.md设计
- 团队协调
- 技能匹配
- Meta-review执行

### 9步工作流

```
Step 1: 收集证据（≥2数据点）
Step 2: AI-Slop签名扫描（9个模式）
Step 3: 基于断言的评估（PASS/FAIL + 证据）
Step 4: 声明提取与验证（按类别）
Step 5: 思维深度量化（4指标）
Step 6: 质量评级（S/A/B/C/D + 根因）
Step 7: 评估标准自省
Step 8: 构建验证closure packet
Step 9: 提交报告
```

### AI-Slop 9签名库

| ID | 签名 | 严重性 | 检测模式 |
|----|------|--------|---------|
| SLOP-01 | 公式化开场白 | Medium | "Certainly!", "Here's how...", "In conclusion..." |
| SLOP-02 | 总结填充 | Medium | 不必要的总结性语句 |
| SLOP-03 | 空概念 | High | 高大上但无实质内容的描述 |
| SLOP-04 | 列表填充 | High | 无差别的列表项 |
| SLOP-05 | 无来源结论 | High | 未经证实的声明 |
| SLOP-06 | 可替代性 | Critical | 替换Agent名称仍成立 |
| SLOP-07 | 捏造数据 | Critical | 不存在的引用或数据 |
| SLOP-08 | 缺失推理链 | High | 跳跃性结论 |
| SLOP-09 | 具体任务vs领域抽象 | Critical | 用具体任务掩盖领域缺失 |

### 基于断言的评估框架

**PASS**: 有清晰证据支持，反映真实任务完成
**FAIL**: 无证据、证据矛盾、表面合规、偶然满足

**规则**: 举证责任在断言方；不能证明=FAIL

### 声明验证矩阵

| 声明类型 | 验证方法 |
|---------|---------|
| 事实性声明 | 实际计数和验证 |
| 过程性声明 | 检查计算过程是否存在 |
| 质量性声明 | 逐字段检查内容 |

### 验证Closure Packet

修复时必须提供：
- `fixEvidence`: 每个修复的具象证据
- `closeFindings`: 每个发现的明确状态（closed/accepted risk/carry forward）

### Hidden Review-State骨架

| State | Values | Purpose |
|-------|--------|---------|
| `reviewState` | collecting-evidence/asserting/claims-check/rated | 追踪判断进度 |
| `verificationState` | open/incomplete/closable/closed | 防止提前综合 |
| `criteriaState` | stable/too-loose/too-strict/drifting | 使meta-review触发器显式化 |

### 漂移检测机制

1. **质量漂移**: 通过AI-Slop签名和性能回归检测
2. **标准漂移**: `criteriaState` 变为 `drifting` → 通过 `surfaceState: debug-surface` 升级到Warden
3. **演化信号追踪**: 与evolution_log数据交叉引用

### 自我省问

- 错误输出也会通过这个断言吗？
- 重要结果被发现了吗？
- 断言从可用输出中无法验证吗？

### 技能发现协议（Local-First）

```
1. 本地扫描 .claude/skills/*/SKILL.md
2. 检查 .claude/capability-index/global-capabilities.json
3. findskill搜索（仅本地不足时）
4. 专家生态系统（everything-claude-code, gstack等）
5. 通用回退（最后手段）
```

### 协作链

```
Warden分配缺口 → Scout: baseline → search → evaluate → security screen → report
                     ↓
        Genesis: 架构匹配
        Sentinel: 最终安全批准
```

### 使用示例

```bash
# 元审查触发
/质量审查 <task-id>

# AI-Slop扫描
/扫描内容 <content> --strictness high

# 漂移检测
/漂移检测 --metric quality --baseline <baseline-id>

# 验证closure
/closure确认 <report-id> --fixes <evidence>
```

### 输出格式

```markdown
# Meta-Prism 质量评估报告

## 基本信息
- Task: [任务ID]
- Agent: [Agent名称]
- Reviewer: Meta-Prism
- Timestamp: [时间戳]

## AI-Slop签名扫描
| ID | 签名 | 检测 | 严重性 |
|----|------|------|--------|
| SLOP-01 | ... | Yes/No | ... |

## 基于断言的评估
| 断言 | 评估 | 证据 |
|------|------|------|
| ... | PASS/FAIL | ... |

## 声明验证
| 声明类型 | 声明内容 | 验证结果 |
|---------|---------|---------|
| ... | ... | Verified/Failed |

## 质量评级
- 评级: S/A/B/C/D
- 根因: [分析]

## 漂移检测
- criteriaState: [状态]
- 漂移信号: [Yes/No]

## 建议行动
- [具体修复建议]
- [升级Warden条件]
```

### 与现有天龙组件协同

| 天龙组件 | 协同方式 |
|---------|---------|
| 06审查师 | 前置审查 → Meta-Prism元审查 |
| 09-03元审查师 | 整合为元审查的底层Skill |
| lessons.md | 质量评估结果 → 存储到记忆 |
| verification-loop | closure packet → 验证闭环 |

### 文件位置

```
skills/meta-prism/
├── SKILL.md                    # 本文件
├── ai-slop-signatures.yaml     # 9签名定义
├── assertions-template.md       # 断言评估模板
├── verification-packet.md      # Closure Packet模板
└── drift-detection.md         # 漂移检测逻辑
```

---

## 🔗 Stage 40 协同（⭐ V1.1 增量 · cross_check_with_trajectory）

> **触发源**：[devmom/dsh-trajectory-debug](https://github.com/devmom/dsh-trajectory-debug) v0.2.0 · MIT ✅ · 镜像在 `skills/dsh-trajectory-debug-integration/`
>
> **协同目标**：让 Meta-Prism 不仅靠 AI-slop 9 签名打分，**还能与 DSH trajectory 失败归因双源对照**，把"质量评估"从 opinion-based 升级为 evidence-based。

### V1.1 §1. 新增 API

```python
# scripts/quality_check.py 新增方法
from quality_check import cross_check_with_trajectory, TrajectoryEvidence

# 1. 提供待评估的 claim / answer / decision
claim = "模型在 step 7 编了一个看似合理的答案"

# 2. 拉对应的 trajectory（DSH webserver RPC）
evidence = TrajectoryEvidence(
    dsh_url="http://127.0.0.1:3080",
    session_id="<id>",
    step_seq=7,
)

# 3. AI-slop 9 签名打分 + trajectory 失败归因双源对照
result = cross_check_with_trajectory(
    claim=claim,
    evidence=evidence,
    slop_weights="ai-slop-signatures.yaml",
)

# → result.sources 列出每一项签名 + 每一项 trajectory 证据：
#   slop.SLOP-04 (verbosity)        + trajectory.step[7].no_tool_call=True     → PASS
#   slop.SLOP-07 (over_confident)   + trajectory.step[7].no_evidence=True       → PASS
#   → 总评 A：双源都指向"编答案"
```

### V1.1 §2. AI-slop 9 签名 × trajectory 失败归因 双向映射

| AI-slop 签名 | trajectory 协同信号 |
|---|---|
| SLOP-01 generic | trajectory step 文本与训练数据相似度 |
| SLOP-02 verbose | step 输出 tokens / prompt tokens 比值 |
| SLOP-03 list_format | 无对应工具调用，纯文本结构化 |
| SLOP-04 over_confident | step 后没有 tool call（trajectory.step[].no_tool_call） |
| SLOP-05 hedge | 无 evidence 调用记录 |
| SLOP-06 unfalsifiable | 无可验证具体 action |
| SLOP-07 contradiction | 后续 step 否定前 step |
| SLOP-08 anachronism | step 时间戳与事件溯源不一致 |
| SLOP-09 citation_fail | trajectory 缺 citation tool 调用 |

### V1.1 §3. 双源对照判定逻辑

```
IF  ai_slop_score >= 4  AND  trajectory step has_failure:
    → 评级 = "EXPLICIT slop"（双源确证）
ELIF ai_slop_score >= 4  AND trajectory step no_tool_call:
    → 评级 = "IMPLICIT slop"（AI 单源）
ELIF ai_slop_score < 4   AND trajectory step has_failure:
    → 评级 = "latent quality issue"（trajectory 单源）
ELSE:
    → 评级 = "clean"
```

### V1.1 §4. 与元审查师（09-03）链路

09-03 meta-reviewer V2.0（已经在 W2 升级）通过 /perf + cron 触发 → 调用 Meta-Prism V1.1 → 调 trajectory signals 交叉验证 → 输出 closure packet。

### V1.1 §5. DON'T 护栏（trajectory-debug 增量）

- ❌ **不要**把 trajectory signals 当唯一证据（要保留 AI-slop 评分独立判断）
- ❌ **不要**默认开启 `enableModelTools`（cross-check 每 step 多一次 LLM → token 翻倍；opt-in）
- ❌ **不要**让 SLOP-04 / SLOP-05 在 trajectory 不可用时强行判定（fallback 单源，注明降级）
- ❌ **不要**用 trajectory 的 `failure_taxonomy` 替换 SLOP-09 citation_fail（两套标准独立）

### V1.1 §6. 验证矩阵

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | `cross_check_with_trajectory()` 入参校验 | claim + evidence 必填 | ⏳ |
| 2 | 双源映射表 9/9 命中 | ai-slop-signatures.yaml 与 trajectory signals 对齐 | ⏳ |
| 3 | 4 档评级 EXPLICIT/IMPLICIT/latent/clean 判定正确 | 边界用例全过 | ⏳ |
| 4 | trajectory 不可用时降级到单源 | 警告日志 + 标注降级 | ⏳ |
| 5 | 3 个 pytest 用例 | trajectory RPC mock | ⏳ |
