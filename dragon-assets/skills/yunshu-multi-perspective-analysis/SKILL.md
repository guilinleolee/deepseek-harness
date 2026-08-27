---
license: UNKNOWN
name: yunshu-multi-perspective-analysis
description: 多视角深度分析——用10个独立Sub-agent分别扮演全球最强大脑的顾问，对同一素材做并行分析，然后交叉汇总共识与分歧，产出结构化诊断报告。当用户说"帮我多视角分析"、"多维分析"、"用多个视角看看"、"帮我诊断一下"时触发。
github_repo: yunshu0909/yunshu_skillshub
github_hash: 17eca94c7b1468d0810364825683918f3a3cb829
last_updated: 2026-04-25
source_type: derived
triggers: ["yunshu multi perspective analysis", "yunshu-multi-perspective-analysis"]
---

# yunshu-multi-perspective-analysis

> 来源: [yunshu0909/yunshu_skillshub](https://github.com/yunshu0909/yunshu_skillshub) multi-perspective-analysis, 10个全球最强大脑并行顾问框架

## 核心价值

**独立分析但结论趋同时可信度极高，结论分歧时往往是最有价值的洞察。**

10个独立 Sub-agent 分别扮演全球顶级思想家/企业家的顾问：
Dan Sullivan（10x增长）| 马斯克（第一性原理）| 张小龙（产品直觉）| MrBeast（创作者增长）| 芒格（多元思维）| 蒂尔（垄断思维）| 乔布斯（极致体验）| 贝佐斯（客户至上）| 张一鸣（算法思维）| 任正非（战略生存）

## 5阶段工作流

| 阶段 | 名称 | 执行方式 |
|---|---|---|
| 1 | 收敛需求 | 对话确认 |
| 2 | 准备素材 | 整理+压缩 |
| 3 | **并行分析** | Agent工具并行启动10个Sub-agent |
| 4 | **交叉汇总** | 找共识、找分歧、提炼可执行建议 |
| 5 | 输出报告 | 结构化报告保存到文件 |

## 触发词

- "帮我多视角分析"
- "多维分析"
- "用多个视角看看"
- "帮我诊断一下"
- "用全球最强大脑分析"
- "多视角诊断"

## 视角匹配推荐

| 分析对象类型 | 推荐视角 |
|---|---|
| 个人/创作者全面复盘 | 全部10个 |
| 产品策略 | 马斯克+张小龙+乔布斯+贝佐斯 |
| 内容增长 | MrBeast+张小龙+张一鸣+任正非 |
| 商业决策 | 芒格+蒂尔+贝索斯+Dan Sullivan |
| 职业方向 | Dan Sullivan+马斯克+蒂尔+任正非 |
| 竞争策略 | 任正非+蒂尔+芒格 |
| 战略复盘 | 任正非+芒格+马斯克 |

## 并行执行架构

使用 Agent 工具一次性并行启动所有选定的 Sub-agent，每个 agent：
1. 自己读取对应的 reference 文件作为分析框架语料
2. 基于框架语料对用户素材做独立分析
3. 写完后将报告保存到指定文件
4. 主 agent 不预读 reference，不预注入语料到 prompt

## 交叉汇总框架

1. **共识发现** — 3个或以上视角得出相同结论 = 高可信度硬事实
2. **有趣的分歧** — 视角间矛盾 = 高价值洞察，往往暴露问题多面性
3. **独家洞察** — 只有一个视角提出 = 被忽视的盲区
4. **可执行建议** — 按"重要性×可执行性"收敛为3-5条关键行动

## 输出格式

```markdown
# [分析主题] — 多视角诊断报告

## 多人共识（高可信度）
[3-5个多数视角一致的核心结论]

## 有意思的分歧
[视角之间的矛盾点及其原因分析]

## 独家洞察
[只有某个视角提出的重要观点]

## 最刺耳的话（每人一句）
| 视角 | 最刺耳的一句 |
|------|------------|
| ... | ... |

## 下一步行动（3-5条）
[按优先级排序的具体行动建议]
```

## 核心原则

1. **独立性是生命线** — 每个agent必须完全独立分析，不可见其他agent输出
2. **必须并行** — 所有agent在同一条消息中启动
3. **深度优先** — 宁可每个视角3000字深度报告，不要5个500字浅层总结
4. **必须有锐度** — 每个视角都要给出"最刺耳的一句话"
5. **汇总要有主见** — 交叉汇总不是简单罗列，要分析共识为什么形成、分歧为什么产生
6. **用户决策权** — 分析是工具，决策是用户的，不替用户做决定

## 内部参考文件

分析框架语料库位于：
`~/.claude/skills/yunshu_skillshub/multi-perspective-analysis/reference/`

| 视角 | reference文件 |
|------|------------|
| Dan Sullivan | `01-10x-growth-dan-sullivan.md` |
| 马斯克 | `02-first-principles-elon-musk.md` |
| 张小龙 | `03-product-intuition-zhang-xiaolong.md` |
| MrBeast | `04-creator-growth-mrbeast.md` |
| 芒格 | `05-mental-models-charlie-munger.md` |
| 蒂尔 | `06-zero-to-one-peter-thiel.md` |
| 乔布斯 | `07-product-vision-steve-jobs.md` |
| 贝佐斯 | `08-customer-obsession-jeff-bezos.md` |
| 张一鸣 | `09-algorithm-thinking-zhang-yiming.md` |
| 任正非 | `10-strategic-survival-ren-zhengfei.md` |

## 与09-02编排协调师集成

当09-02编排协调师收到多视角分析请求时，自动切换到此工作流模式，以编排协调师身份作为主控Agent，负责任务收敛→素材准备→并行编排→交叉汇总→报告输出全流程。
