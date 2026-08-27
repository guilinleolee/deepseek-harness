---
license: UNKNOWN
name: content-intel-cn
description: 中文内容情报编排层：统一调度微信公众号/小红书/X 的趋势研究、选题生成、发帖草案与复盘入库（Notion）。用于多平台内容运营而不重复造轮子。支持Free LLM Provider零成本推理。
metadata: openclaw:
emoji: "🧭"
category: "orchestration"
tags: ["content", "wechat", "xiaohongshu", "twitter", "notion", "orchestration", "free-llm"]
triggers: ["content intel cn", "Content Intel CN（编排层）V1.1"]
---

# Content Intel CN（编排层）V1.1

这是一个**编排型 skill**，不直接替代底层能力，而是统一调用现有技能：

- `xiaohongshu-mcp`（小红书搜索/详情/发布）
- `opentwitter`（X 数据检索与趋势）
- `notion`（结果沉淀、选题池、复盘）
- 微信相关能力（先以手工/第三方接口方式接入，后续可替换为稳定 API）

## 🆕 V1.1 新特性：Free LLM Provider零成本推理

### 核心价值
内容编排现在可以使用**完全免费的LLM提供商**，实现多平台内容创作的零成本AI推理。

### 推荐免费提供商

| 编排阶段 | 推荐提供商 | 路由策略 | 成本 |
|---------|-----------|---------|------|
| **趋势分析** | Groq (DeepSeek R1) | selectWithReasoningPriority() | **$0** |
| **选题生成** | Google AI Studio | selectWithQualityPriority() | **$0** |
| **内容创作** | Groq (Llama 3.3) | selectWithFreePriority() | **$0** |
| **批量发布** | Groq | selectWithLatencyPriority() | **$0** |

### AI Router API调用

```javascript
const router = new AIRouter();

// A. 研究模式：趋势分析（推理模型，零成本）
const trendProvider = router.selectWithReasoningPriority();

// B. 发帖模式：选题生成（高质量，零成本）
const topicProvider = router.selectWithQualityPriority();

// C. 复盘模式：内容创作（批量处理，零成本）
const contentProvider = router.selectWithFreePriority({
  taskType: 'text'
});
```

### 配额监控集成

```javascript
const { quotaMonitor } = require('../shared/quota-monitor');

// 编排前检查配额
const provider = quotaMonitor.getBestAvailableProvider('P0');
if (!provider) {
  // 降级到P1或P2
  const fallback = quotaMonitor.getBestAvailableProvider('P1');
}
```

### 预期收益

| 指标 | V1.0 | V1.1 | 提升 |
|------|------|------|------|
| **内容编排成本** | $0.02/篇 | **$0** | **-100%** |
| **批量处理延迟** | 2-5s | **100-500ms** | **-90%** |
| **零成本推理率** | 60% | **95%+** | **+35%** |

---

## 适用场景

1. 主题研究：输入关键词，输出多平台趋势与高互动样本
2. 选题策划：按受众和目标生成 7 天选题清单
3. 发帖准备：生成平台化草稿（X/小红书/公众号）
4. 复盘归档：把发布结果、互动、复盘写入 Notion

## 标准工作流

### A. 研究模式（Research）
- 输入：`关键词 + 时间范围 + 平台`
- 动作：
  - X：抓取热门话题、代表帖子
  - 小红书：搜索同主题高互动笔记
  - 微信：补充头部账号/相关文章（可手工）
- 输出：
  - 热点摘要（3-5 条）
  - 可执行选题（5-10 条）
  - 风险提示（同质化、敏感词、平台限制）

### B. 发帖模式（Draft/Post）
- 输入：`平台 + 主题 + 语气 + CTA`
- 输出：
  - 草稿 A/B 版
  - 标题、开头钩子、标签建议
  - 如用户明确确认，再执行发布

### C. 复盘模式（Review）
- 输入：`发布时间段`
- 输出：
  - 平台对比（曝光/互动）
  - 结构复盘（标题、首屏、话题）
  - 下一轮优化建议

## 融合原则（防冲突）

1. **不覆盖同名 skill**：避免命名为 `github`、`notion` 这类已存在官方名
2. **编排优先**：已有技能负责执行，本 skill 负责路由与产出结构
3. **高风险操作需确认**：外发动作默认二次确认
4. **结果可追溯**：关键结论写明来源平台与时间

## 你的当前本地能力映射

- 内容采集：`xiaohongshu-mcp` + `opentwitter`
- 结构化沉淀：`notion`
- 编排入口：`content-intel-cn`

## 下一步建议

1. 补一份 Notion 数据库结构（选题池/发布记录/复盘）
2. 增加一个 `scripts/` 下的日更汇总脚本（可选）
3. 把微信来源先做“半自动”，等稳定 API 后替换
