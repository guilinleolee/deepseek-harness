# AGENT.md · darwin-skill × 天龙引擎

> **协议**：Agent 工作约定（与上游 darwin-skill 平级扩展，但**不修改** upstream 任何字节）

---

## 1. 何时使用本 skill

由 [SKILL.md `description`](SKILL.md) 的 trigger 词触发，主要场景：

| 触发词 | 路径 |
|---|---|
| 「优化 skill」「skill 评分」「达尔文」「自动优化」| Phase 1 基线评估 → Phase 2 hill climbing |
| 「skill 怎么样」「skill 打分」「帮我改改 skill」| Phase 0 → Phase 1 基线评估 |
| "auto optimize" / "skill review" | 英文路径 |

---

## 2. 天龙引擎协同约定

### 2.1 与 neat-freak V1.1 Apache/AGPL/MIT 红线扫描联动（**l3-specs/darwin-neat-freak-bridge.md**）

darwin 在每个优化周期前，必须先跑 `neat-freak V1.1` 红线扫描：

```
[darwin Phase 0.5] neat_check.py --target <skill>
    ├─ exit 0 → 进 Phase 1
    ├─ exit 1 (尺寸超限) → 用户手动缩减 skill 文件
    ├─ exit 2 (体量倒挂) → 重新组织子目录
    └─ exit 3 (链接断裂) → 修复交叉引用
```

防止 darwin 优化过程中**意外触碰 Apache-2.0 红线**（如把 simonlin1212 NOTICE 改成简短致谢）。

### 2.2 与 cangjie 蒸馏产物自动消费

cangjie 阶段 4 产出的 `test-prompts.json` 严格 darwin 兼容 → **直接喂 darwin Phase 1**。

```
cangjie 阶段 4 (压力测试) → test-prompts.json (darwin_compatible: true)
                                          ↓
                              darwin Phase 1 (基线评估)
                              darwin Phase 2 (hill climbing)
                              darwin Phase 3 (产出 result-card.html)
```

### 2.3 与 nuwa 蒸馏产物自动消费

nuwa 蒸馏人物的 `<person>-perspective/test-prompts.json` 同样 darwin 兼容 → 喂 darwin 进化。

---

## 3. darwin 9 维 Rubric（天龙增强版）

上游 darwin 9 维评分（结构 59 + 效果 35 + meta-skill 6 = 100）天龙额外加 4 条红线：

| # | 维度 | 权重 | 评分标准（天龙增强） |
|---|------|------|---------------------|
| 1-9 | 上游 9 维 | 100 | darwin 原版 |
| **10** | **MIT 致谢段完整** | +3 | 含 `alchaincyf/<upstream>` + 5 模板 |
| **11** | **AGPL 红线规避** | +3 | 不上传完整模板到 H5、不把方法论当课程 |
| **12** | **Apache NOTICE 完整** | +3 | 含 "Powered by" + Modified + Trademark + 第三方 |
| **13** | **neat-freak 检查通过** | +3 | darwin Phase 0.5 必跑 `neat_check.py` |

---

## 4. 关键约束

- **paired 比较 + 奇数 N 多数决**（v2.1）—— darwin 棘轮不再用绝对分数 delta，用同-judge 比较消除换尺污染
- **runtime neutrality**（参考 `references/runtime-neutrality.md`）—— 不能在 SKILL.md 写「Claude Code only」「Cursor only」等 runtime 限制
- **human-in-the-loop**（参考 Phase 2 SkillOpt 设计）—— 每个 skill 优化完后暂停等用户确认

---

## 5. 失败兜底

| 失败模式 | 兜底 |
|---|---|
| Judge 评分噪音过大（±8） | v2.1 paired 比较替代 |
| test-prompts 不存在 | 自动从 SKILL.md description 启发式生成 |
| AGPL 红线误触 | Phase 0.5 neat-freak gate |
| 优化 5 轮无提升 | 自动 break + 报告 |

---

## 6. 与 book-distiller V9.12 协同

book-distiller 蒸馏书的 DIGEST.md → darwin 评估（book-distiller 产物质量门神）。