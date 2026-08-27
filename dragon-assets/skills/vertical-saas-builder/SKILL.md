---
license: UNKNOWN
triggers: ["vertical saas builder", "vertical-saas-builder"]
---
# vertical-saas-builder

## L0: 一句话描述 (≤15字)

**垂直SaaS：从痛点切入到产品矩阵的完整路径**

---

## L1: 使用场景 (50-100字)

**适用场景**：垂直SaaS产品规划、细分市场切入、MVP快速验证、产品矩阵扩展、PLG增长策略、定价策略设计。

**触发关键词**：`vertical-saas`、`垂直SaaS`、`Niche SaaS`、`PLG`、`产品矩阵`、`垂直切入`

---

## L2: 详细文档

### 核心能力矩阵

| 能力 | 版本 | 说明 |
|------|------|------|
| 垂直切入定位 | V1.0 | 从宽泛市场到垂直细分的选择框架 |
| MVP快速验证 | V1.0 | 垂直SaaS最小可行产品的设计方法 |
| 产品矩阵扩展 | V1.0 | 从单一产品到产品矩阵的演进路径 |
| PLG增长策略 | V1.0 | 产品驱动增长的实施策略 |
| 定价策略设计 | V1.0 | 垂直SaaS定价模型与优化 |
| 客户成功体系 | V1.0 | 垂直行业客户成功的最佳实践 |

---

### 垂直SaaS产品矩阵

```
┌─────────────────────────────────────────────────────────────┐
│                 垂直SaaS产品矩阵演进路径                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: 单一痛点工具                                      │
│  ├── 切入策略：最高频痛点，最低集成依赖                    │
│  ├── 价格区间：$29-$99/月                                  │
│  └── 目标：100个付费用户，验证PMF                          │
│                                                             │
│  Phase 2: 功能扩展包                                        │
│  ├── 扩展策略：相邻痛点，共享数据模型                      │
│  ├── 价格区间：$99-$299/月                                 │
│  └── 目标：500个付费用户，ARR>$500K                        │
│                                                             │
│  Phase 3: 工作流平台                                       │
│  ├── 扩展策略：端到端工作流，覆盖核心场景                  │
│  ├── 价格区间：$299-$999/月                                │
│  └── 目标：1000个付费用户，ARR>$1M                         │
│                                                             │
│  Phase 4: 行业解决方案                                     │
│  ├── 扩展策略：行业定制+生态集成                          │
│  ├── 价格区间：$999-$4999/月                               │
│  └── 目标：大型客户，ARR>$10M                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### AI提示词模板

#### 垂直切入定位提示词

```markdown
# Role: 垂直SaaS战略分析师

# 市场分析
- 宽泛市场：{broad_market}
- 候选垂直行业：{candidate_verticals}
- 竞争格局：{competitive_landscape}

# 选择框架
1. 痛点强度：行业痛点是否足够痛？
2. 付费能力：该行业是否有钱？
3. 可触达性：能否接触到决策者？
4. 扩展潜力：从单点产品到平台的可能性？

# 输出要求
## 推荐的垂直切入点
- 垂直行业：{vertical}
- 核心痛点：{core_pain_point}
- 差异化优势：{differentiator}
- 预估市场规模：{tam}

## 切入时机评估
- 市场成熟度：{maturity}
- 竞争窗口期：{window}

## 风险评估
- 主要风险：{key_risks}
- 缓解策略：{mitigation}
```

#### MVP快速验证提示词

```markdown
# Role: 垂直SaaS MVP设计师

# 产品信息
- 目标垂直：{vertical}
- 核心痛点：{pain_point}
- 目标用户：{target_user}
- 假设：{assumptions}

# MVP设计原则
1. 只做一件事，但做到极致
2. 集成成本最低（尽量不用API）
3. 用户上手时间<30分钟
4. 关键指标可量化

# 输出要求
## MVP功能范围
- 核心功能（3个）：{core_features}
- 不做功能：{out_of_scope}
- 集成策略：{integration_strategy}

## 验证指标
- 激活率目标：{activation_target}
- 留存目标（7天）：{retention_7d}
- 付费转化目标：{paid_conversion}

## 快速验证路径
- Week 1-2：用户访谈+竞品分析
- Week 3-4：Prototype测试
- Week 5-8：MVP发布+种子用户
```

#### 产品矩阵扩展提示词

```markdown
# Role: 垂直SaaS产品矩阵规划师

# 当前状态
- 当前产品：{current_product}
- 目标垂直：{vertical}
- 当前ARR：{current_arr}
- 客户数量：{customer_count}

# 扩展原则
1. 共享数据模型：减少迁移成本
2. 相邻痛点：基于已有客户需求
3. 定价协同：产品间自然升级路径

# 输出要求
## 产品演进路线图
- Phase 2产品：{product_v2}
- Phase 3产品：{product_v3}
- Phase 4产品：{product_v4}

## 产品间协同
- 数据共享：{data_sharing}
- 用户旅程：{user_journey}
- 定价策略：{pricing_strategy}

## 扩展风险
- 产品线稀释：{risks}
- 应对策略：{mitigation}
```

---

### 命令调用

```bash
# 垂直切入分析
vertical-saas-builder analyze --market "项目管理软件" --verticals "建筑,医疗,法律"

# MVP快速验证
vertical-saas-builder mvp --vertical "电商" --pain-point "库存管理"

# 产品矩阵规划
vertical-saas-builder roadmap --current "订单管理" --expand-to "全链路电商ERP"

# PLG增长策略
vertical-saas-builder plg --product "团队协作工具"

# 定价策略设计
vertical-saas-builder pricing --vertical "餐饮" --tier 3
```

---

### MCP工具调用

```bash
# 垂直市场分析
mcp__vertical_saas__analyze "餐饮行业" --metrics tam,competition,entry_barrier

# MVP验证跟踪
mcp__vertical_saas__mvp_validate --product "餐饮点餐系统" --metrics activation,retention,ltv

# 产品矩阵扩展
mcp__vertical_saas__expand --current "POS系统" --target "餐饮全链路" --tier 4

# PLG漏斗分析
mcp__vertical_saas__plg_funnel --product "项目管理工具" --stages trial,activation,conversion,expansion
```

---

### 与其他技能协同

| 技能 | 协同方式 | 效果 |
|------|---------|------|
| `monetization-seven-swords` | 变现七剑→垂直SaaS定价 | 垂直产品定价优化 |
| `monetization-blueprint` | 蓝图→产品矩阵 | 变现策略落地 |
| `opc-niche-positioning` | 细分定位→垂直切入 | 精准定位 |
| `saas-quick-builder` | 快速构建→MVP验证 | 开发效率提升 |

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-05 | 初始版本，垂直SaaS完整构建路径 |

---

**版本**: v1.0
**最后更新**: 2026-05-05
**技能类型**: 垂直SaaS产品构建