---
name: pre-sales-survey
description: FDE售前调研——为cold outreach提供客户背景+决策链+切入点情报
invokable: true
allowed-tools: WebSearch, mcp__brave_search__*, mcp__exa__*, mcp__web_reader__webReader, mcp__fetch__fetch, Write, Read
argument-hint: [公司名] [行业]
model: sonnet
---
# FDE 售前调研（pre-sales-survey）

FDE 工作流 **land** 阶段的售前情报采集。在 cold outreach 前生成"知己知彼"包，提高命中率。

## 参数

- **公司名**: $1 (必需) - 目标客户公司
- **行业**: $2 (可选) - 默认自动识别

## 与 /find-clients 的差异

| 维度 | /find-clients | /pre-sales-survey |
|---|---|---|
| 输入 | 行业 + 地区 + 数量 | 具体公司名 |
| 输出 | CSV 客户名单 | 单家公司深度情报 |
| 目的 | 批量获客 | 单家转化 |
| 触发 | 销售线索阶段 | 销售触达前 |

## 执行流程

### 1. 加载售前情报模板

读取 `~/.claude/skills/customer-interview-template/SKILL.md` 的"售前情报包"部分：

### 2. 多源情报采集

调用多源（搜索引擎 + 企业信息平台 + 招聘网站 + 公开报道）：

| 维度 | 来源 | 产出字段 |
|---|---|---|
| **公司画像** | 官网/天眼查/企查查 | 行业/规模/成立时间/营收估算/股权结构 |
| **业务现状** | 官网/公开报道 | 主营产品/客户群/竞品/商业模式 |
| **技术栈** | 招聘 JD/GitHub | 主要语言/框架/云厂商/数据栈 |
| **近期动态** | 36氪/IT桔子/官方公众号 | 融资/新产品/组织调整/数字化项目 |
| **决策链** | LinkedIn/脉脉/官网高管介绍 | CEO/CTO/CIO/CDO + 影响力评估 |
| **痛点信号** | 招聘 JD/吐槽帖/客户案例 | 业务痛点 + 我们能切入的角度 |
| **切入点** | 综合判断 | 我们能提供什么 + 为什么是"现在" |

### 3. 写入 ~/customers/$1-pre-sales/ 临时目录

```
~/customers/$1-pre-sales/
├── profile.md            # 公司画像
├── signals.md            # 痛点信号 + 切入点
├── decision-chain.md     # 决策链 + 影响力
├── outreach-draft.md     # cold outreach 剧本初稿
└── README.md             # 情报包索引
```

### 4. 调用 [[agents/38-sales-manager]]

把情报包传给销售管理，生成：
- cold outreach 邮件/微信模板（3 套：A 直接/B 间接/C 转介绍）
- 切入话术（5-10 条，针对不同角色）
- 报价区间建议（参考 [[05-FDE定价与SOW模板]]）

### 5. 决策判断

基于情报包，输出 3 选 1：
- **A 高优触达**（决策链清晰 + 痛点明确 + 近期有动作）
- **B 中优培育**（痛点有但决策链不清，先养关系 3 月）
- **C 放弃**（信息不足 / 不符定位）

### 6. 在天龙 memory 追加

```
## [YYYY-MM-DD] pre-sales-survey | $1
- 情报等级: 高 / 中 / 低
- 切入角度: [一句话]
- 下一步: A 触达 / B 培育 / C 放弃
```

## 使用示例

```bash
# 完整售前调研
/pre-sales-survey acme-corp

# 指定行业
/pre-sales-survey acme-corp 制造业

# 配合 /find-clients 使用
/find-clients SaaS 50  # 先批量
/pre-sales-survey 公司A  # 再针对性
```

## 反向链接

- [[agents/38-sales-manager]] — 销售管理接管
- [[04-FDE客户获取与冷启动]] — cold outreach 剧本
- [[05-FDE定价与SOW模板]] — 报价区间
- [[Quivly Skills]] `account-360` — 国际版本参考
- [[天龙引擎-CEC客户工程中心-蓝图]] — 情报目录