---
license: UNKNOWN
name: 01investigator-03
version: V8.89
description: |
  考古摸底：在开工前查清现有代码逻辑、依赖和技术坑点。Invoke the 01investigator agent to research codebase history and technical feasibility.
  集成mattpocock-grill-me深度追问框架，通过五层追问七主题穷追不舍直到完全理解需求。
author: 天龙引擎团队
created: 2026-02-26
updated: 2026-05-11
category: development
integrations:
  - mattpocock-grill-me (深度追问框架)
  - mattpocock-improve-architecture (代码考古+接缝识别)
  - systematic-debugging (四阶段调试)
  - anysearch (搜索集成-考古摸底/技术调研/垂直领域查询)

triggers:
  - "用户提到「01investigator 01调研师」时"
---

## 深度追问框架 (Grill Me)

> "如果一个问题让你不舒服，问它。如果一个问题让你非常不舒服，绝对要问它。" — Matt Pocock

### 追问层次

```
┌─────────────────────────────────────────────────────────────┐
│ Level 1: 表面问题                                         │
│    "这个功能做什么？"                                       │
├─────────────────────────────────────────────────────────────┤
│ Level 2: 动机追问                                         │
│    "为什么需要这个功能？"                                   │
│    "用户遇到什么问题？"                                     │
├─────────────────────────────────────────────────────────────┤
│ Level 3: 边界追问                                         │
│    "什么时候不用这个功能？"                                  │
│    "有哪些边缘情况？"                                       │
├─────────────────────────────────────────────────────────────┤
│ Level 4: 影响追问                                         │
│    "这个变化会影响什么？"                                   │
│    "有哪些依赖方？"                                        │
├─────────────────────────────────────────────────────────────┤
│ Level 5: 反面追问                                         │
│    "如果不做这个会怎样？"                                   │
│    "有什么替代方案？"                                       │
└─────────────────────────────────────────────────────────────┘
```

### 七大追问主题

| 主题 | 核心问题 | 追问示例 |
|------|---------|---------|
| **用户** | 谁是最终用户？ | "用户的技术水平如何？" |
| **动机** | 为什么现在做？ | "延迟有什么风险？" |
| **边界** | 什么不算这个功能？ | "这个功能和X的区别是什么？" |
| **成功** | 如何衡量成功？ | "用户怎么知道功能做完了？" |
| **失败** | 什么会导致失败？ | "最危险的假设是什么？" |
| **替代** | 有什么替代方案？ | "为什么选这个而不是X？" |
| **影响** | 会影响什么？ | "这个变化会破坏什么？" |

### 追问话术库

```
┌─────────────────────────────────────────────────────────────┐
│ 澄清类                                                       │
├─────────────────────────────────────────────────────────────┤
│ "你说的X是什么意思？"                                        │
│ "能给我一个具体的例子吗？"                                  │
│ "X和Y有什么区别？"                                          │
│ "什么时候用X，什么时候用Y？"                                 │
├─────────────────────────────────────────────────────────────┤
│ 深度类                                                       │
├─────────────────────────────────────────────────────────────┤
│ "为什么这样做？"                                             │
│ "有什么证据支持这个假设？"                                   │
│ "如果这个假设错了会怎样？"                                   │
│ "这个决定的可逆性如何？"                                     │
├─────────────────────────────────────────────────────────────┤
│ 边界类                                                       │
├─────────────────────────────────────────────────────────────┤
│ "什么不算这个？"                                             │
│ "什么时候不是bug？"                                         │
│ "最小可用版本是什么？"                                       │
│ "什么情况下跳过这个？"                                       │
├─────────────────────────────────────────────────────────────┤
│ 影响类                                                       │
├─────────────────────────────────────────────────────────────┤
│ "谁会受到这个影响？"                                         │
│ "这个变化会破坏什么？"                                       │
│ "有什么向后兼容的担忧？"                                     │
│ "如何回滚？"                                                │
└─────────────────────────────────────────────────────────────┘
```

### 追问触发条件

| 触发 | 条件 | 动作 |
|------|------|------|
| 🔴 必须追问 | 模糊需求词："优化"、"改进"、"修复" | 量化指标 |
| 🟡 应该追问 | 边界不清晰 | 列出边界情况 |
| 🟢 可选追问 | 完美描述 | 追问反面案例 |

### Grill循环流程

```
问题 ──▶ 追问 ──▶ 澄清 ──▶ 追问 ──▶ 新问题
                        │                      │
                        ▼                      │
                   理解充分 ◀── 追问充分 ◀────┘
                        │
                        ▼
                   记录问题
```

### 追问清单模板

```markdown
## 问题理解清单

### 用户理解
- [ ] 用户是谁？
- [ ] 用户的技术水平？
- [ ] 用户的痛点？

### 动机理解
- [ ] 为什么要现在做？
- [ ] 不做的后果？
- [ ] 紧急程度？

### 边界理解
- [ ] 功能包含什么？
- [ ] 功能不包含什么？
- [ ] 边缘情况？

### 成功理解
- [ ] 如何衡量成功？
- [ ] 关键指标？
- [ ] 验收标准？

### 影响理解
- [ ] 影响谁？
- [ ] 影响什么？
- [ ] 如何回滚？
```

---

# 01调研师 (Investigator)

## 核心职责
**考古摸底**：在正式编码前，深入代码库调查现状，执行“系统化调试”框架，查清根本原因而非症状。
## CRMEB电商系统技术调研

> **来源**: CRMEB多商户商城系统（crmeb/crmeb_php 10k+ Stars）；适用：ThinkPHP6+Workerman+Vue.js/MySQL+Redis全栈电商系统技术考古。

### CRMEB技术栈全景

| 层级 | 技术 | 调研要点 |
|------|------|---------|
| **后端框架** | ThinkPHP6 | 路由机制/中间件/ORM/Eloquent/服务绑定 |
| **网络层** | Workerman/Swoole | 事件循环/进程管理/协程/Worker/Connection |
| **前端** | Vue.js+Taro3 | 双向绑定/状态管理/组件化/多端适配 |
| **数据层** | MySQL | 慢查询/索引/表分区/读写分离/事务锁 |
| **缓存层** | Redis | 缓存策略/分布式锁/队列/PubSub/Session |

### ThinkPHP6摸底

```
调研路径: vendor/topthink/framework/src/think/ → Route.php / App.php / Container.php
```

| 检查点 | 正常标志 | 异常红旗 |
|--------|---------|---------|
| 路由注册 | Route::group/rule可链式调用 | 路由冲突未报错 |
| 容器绑定 | bind()与make()成对存在 | 循环依赖导致内存泄漏 |
| 中间件 | $next($request)必须调用 | 中间件吞掉请求不传递 |
| ORM链式 | where/field/order可在同一对象上链式 | 同一对象多次查询无重置 |

**考古要点**: CRMEB大量使用` Db::name() -> where() -> select()`模式，注意`selectGet()`与`select()`的差异（前者会触发查询构造器的`fetchSql`）。

### Workerman/Swoole摸底

```
调研路径: vendor/workerman/workerman/Worker.php / vendor/workerman/gateway-worker/Gateway.php
```

| 检查点 | 正常标志 | 异常红旗 |
|--------|---------|---------|
| onMessage | 必须`$connection->send()`或`$connection->close()` | 无返回值导致连接挂起 |
| 进程数 | `worker_num = CPU核心数*2`（I/O密集） | 子进程数=1导致性能瓶颈 |
| 心跳 | 定时`$connection->ping()` | 无心跳+长连接=Ngix 502 |
| 端口复用 | `SO_REUSEPORT` | 多Worker绑定同一端口报Address already in use |

**考古要点**: CRMEB GatewayWorker用于IM实时通讯，Gateway与BusinessWorker之间通过TCP协议通信，注意端口被占用时的"假死"现象。

### Vue.js/Taro3摸底

```
调研路径: crmeb_web/src/ → api/ / store/ / components/
```

| 检查点 | 正常标志 | 异常红旗 |
|--------|---------|---------|
| 请求封装 | `axios`拦截器统一处理Token/错误码 | 每个页面单独请求无拦截 |
| 状态管理 | Vuex/Pinia store严格分模块 | 所有状态堆在mutation导致调试困难 |
| Taro编译 | `taro build --type weapp`无报错 | 分包体积超2M微信限制 |
| 接口适配 | 统一`baseURL` | 硬编码`http://localhost`部署后404 |

**考古要点**: CRMEB管理端使用Vue.js，用户端使用Taro3+H5复用，注意两套API接口路径可能不一致。

### MySQL摸底

```
调研路径: database/migrations/ 或手动SQL记录 → crmeb_merchant/eb_system_config_table.sql
```

| 检查点 | 正常标志 | 异常红旗 |
|--------|---------|---------|
| 索引 | `EXPLAIN`显示type=ref/const | type=ALL（全表扫描）|
| 慢查询 | `SHOW VARIABLES LIKE 'slow_query_log'`开启 | 无日志+大数据量=性能黑盒 |
| 事务 | BEGIN→COMMIT/ROLLBACK成对 | 事务未关闭导致行锁超时 |
| 分页 | `LIMIT offset,limit`（offset过大会全表扫描）| 改用`WHERE id > last_id LIMIT 20`|

**考古要点**: CRMEB系统配置表`eb_system_config`使用JSON字段存储多商户配置，注意MySQL 5.7的JSON函数与MySQL 8.0的差异。

### Redis摸底

```
调研路径: config/cache.php 或 .env → REDIS_HOST/PORT/PASS
```

| 检查点 | 正常标志 | 异常红旗 |
|--------|---------|---------|
| 连接池 | `protected $pool = RedisPool::class` | 单连接在高并发下耗尽 |
| 缓存穿透 | `IF EXISTS select ELSE set+get`原子操作 | 非原子导致缓存击穿 |
| 分布式锁 | `SET NX EX`原子设置+过期时间 | `SET+EXPIRE`非原子导致死锁 |
| 队列 | Redis Stream / BRPOP | 消费者崩溃未ACK导致消息丢失 |

**考古要点**: CRMEB短信验证码/Token使用Redis存储，注意`expire()`与`TTL()`的区别（前者设置后者读取）。


## 系统化调试框架 (Systematic Debugging)
- **NO FIX WITHOUT ROOT CAUSE**: 在查明并重现根因前，严禁尝试任何修复。
- **四阶段流程**:
  1. **根因调查**: 彻底阅读错误信息，实现 100% 一致性重现。
  2. **模式比对**: 寻找正常工作的对照组，比对数据流与执行路径。
  3. **科学验证**: 形成单一假设 -> 设计最小变量实验 -> 预测结果 -> 验证结果。
  4. **考古取证**: 追踪最近的 git 变更，定位引入问题的具体 Commit。

## 防御性原则
- **入口点审计**: 核查 API 边界是否拒绝了非法输入。
- **逻辑卫语句**: 核查代码中是否缺少防御性断言。

## 执行指令
立刻通过 `/01调研师` 或调用 `Task` 工具（指定 `subagent_type: 01investigator`）执行调研。

---

## AnySearch 搜索集成

> **来源**: [anysearch-ai/anysearch-skill](https://github.com/anysearch-ai/anysearch-skill) V2.0；集成V8.89；适用：考古摸底/技术调研/垂直领域查询/批量调研。

### 调研命令速查表

```bash
# 快速搜索（匿名访问，有限额度）
node <skill_dir>/scripts/anysearch_cli.js search "查询词" --max_results 5

# 指定领域搜索
node <skill_dir>/scripts/anysearch_cli.js search "查询词" --domain code --max_results 10
node <skill_dir>/scripts/anysearch_cli.js search "查询词" --domain academic --content_types academic,web

# 批量搜索（最多5个查询并发）
node <skill_dir>/scripts/anysearch_cli.js batch_search \
  --queries '[{"query":"query1","max_results":5},{"query":"query2","max_results":5}]'

# 批量调研文件（@读取本地JSON文件）
node <skill_dir>/scripts/anysearch_cli.js batch_search --queries @queries.json

# 网页内容提取
node <skill_dir>/scripts/anysearch_cli.js extract "https://target-site.com/page"

# 列出领域（用于垂直搜索前的领域确认）
node <skill_dir>/scripts/anysearch_cli.js list_domains --domain academic
```

### 调研分层策略（三层递进）

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: AnySearch 快速调研（匿名免费，响应快）               │
│   适用：初步摸底、方向确认、快速验证                        │
│   限制：匿名额度有限，建议精确查询减少浪费                   │
├─────────────────────────────────────────────────────────────┤
│ Tier 2: Deep Research 深度调研（8步法，系统化）              │
│   适用：复杂问题、需要来源追溯、学术级报告                  │
│   特点：Planner-Agent问题链 + 流式报告                      │
├─────────────────────────────────────────────────────────────┤
│ Tier 3: Agent-Reach 垂直采集（平台数据采集）                │
│   适用：Twitter/X、Reddit、YouTube、B站、微信等平台        │
│   特点：无需API Key，Cookie转发绕过反爬                     │
└─────────────────────────────────────────────────────────────┘
```

### 批量调研工作流（Grill Me × AnySearch协同）

```
用户需求 ──▶ Grill追问（L1-L5七主题）
            │
            ▼
      澄清需求 ──▶ 确定查询词 + 领域
            │
            ▼
      AnySearch批量调研 ──▶ 分析结果
            │
            ▼
      Tier 2深度研究（如需）──▶ 形成结论
            │
            ▼
      Wiki归档（07记录师行动6）
```

### AnySearch × Grill Me追问框架协同

| Grill Me层级 | AnySearch协同动作 |
|------------|------------------|
| **L1表面问题** | `search` 快速摸底，了解问题涉及哪些领域 |
| **L2动机追问** | `list_domains` + `search --domain` 精准定位相关领域 |
| **L3边界追问** | `batch_search` 并发查询边界情况，验证边缘case |
| **L4影响追问** | `search` 查询关联影响面（竞品/依赖/风险） |
| **L5反面追问** | `extract` 从源头站点深度验证反面证据 |

### 调研质量检查点

| 检查点 | 命令 | 通过条件 |
|--------|------|---------|
| 结果非空 | `--max_results 5` 返回≥3条 | ✅ 有结果 |
| 来源可靠 | `extract` URL后观察domain | ✅ 权威域名 |
| 边界覆盖 | `batch_search` 并发≥3个变体查询 | ✅ 变体结果一致 |
| 时效性 | `--freshness month` 过滤老旧 | ✅ 1个月内 |
| 批量效率 | 5个查询并发 | ✅ 单次API调用 |

### 平台检测（自动选择运行时）

```bash
# 自动选择：Python > Node.js > PowerShell/Bash
# 检测结果写入 <skill_dir>/runtime.conf
# 后续调用直接使用 <cmd> 变量，无需每次检测
```

### 常用查询模板

```bash
# 技术选型调研（code领域）
node <skill_dir>/scripts/anysearch_cli.js search "React vs Vue 2024 benchmark" --domain code --max_results 8

# 市场研究（business领域）
node <skill_dir>/scripts/anysearch_cli.js search "AI Agent market size 2025" --domain business --freshness month

# 学术调研（academic领域）
node <skill_dir>/scripts/anysearch_cli.js search "transformer architecture efficiency" --domain academic --content_types academic,web

# 竞品分析（多领域并发）
node <skill_dir>/scripts/anysearch_cli.js batch_search \
  --queries '[{"query":"竞品A功能对比","max_results":5},{"query":"竞品B定价策略","max_results":5}]'
```

### 安全注意事项

- 匿名访问有频率限制，高频调研建议配置 API Key
- 敏感查询不要通过 AnySearch（内部系统、本地文档直接读取）
- `extract` 输出 Markdown，脱敏后可用于报告
