# OPC 一人企业方法论 - 技能索引

> 来源: [easychen/opc-methodology](https://github.com/easychen/opc-methodology)
> 作者: Easy (方糖)
> 授权: CC-BY-NC-SA 4.0

## 技能总览

| # | 技能名称 | 目录 | 阶段类型 | 核心功能 |
|---|---------|------|---------|---------|
| 1 | [opc-orchestration](#01-opc-orchestration-总编排) | sk-orchestration | 线性(00) | 阶段判断 + 进度恢复 |
| 2 | [opc-resource-inventory](#02-opc-resource-inventory-资源盘点) | sk-resource-inventory | 线性(01) | 8类资源盘点 |
| 3 | [opc-niche-positioning](#03-opc-niche-positioning-利基定位) | sk-niche-positioning | 线性(02) | 三环定位 + 6维评分 |
| 4 | [opc-value-proposition](#04-opc-value-proposition-价值主张) | sk-value-proposition | 线性(03) | Jobs/Pains/Gains |
| 5 | [opc-business-model](#05-opc-business-model-商业模式) | sk-business-model | 线性(04) | Lean Canvas |
| 6 | [opc-mvp-design](#06-opc-mvp-design-mvp设计) | sk-mvp-design | 线性(05) | MVP验证设计 |
| 7 | [opc-conversion-loop](#07-opc-conversion-loop-转化闭环) | sk-conversion-loop | 触发(06) | 转化闭环设计 |
| 8 | [opc-asset-accumulation](#08-opc-asset-accumulation-资产沉淀) | sk-asset-accumulation | 触发(08) | 资产沉淀规划 |
| 9 | [opc-review](#09-opc-review-经营复盘) | sk-review | 触发(09) | 经营复盘诊断 |

## 快速命令

```bash
# 启动OPC方法论
/opc 开始一人企业规划

# 线性阶段
/opc-resource 开始资源盘点
/opc-niche 开始利基定位
/opc-value 开始价值主张
/opc-canvas 开始Lean Canvas
/opc-mvp 开始MVP设计
/opc-conversion 开始转化闭环

# 触发阶段
/opc-asset 开始资产沉淀
/opc-review 开始经营复盘
```

---

## 技能详情

### 01. opc-orchestration (总编排)

| 属性 | 值 |
|------|-----|
| **文件** | [sk-orchestration/SKILL.md](sk-orchestration/SKILL.md) |
| **阶段编号** | 00 |
| **阶段类型** | 线性阶段（起点） |
| **核心功能** | 阶段判断 + 进度恢复 + 任务分发 |

**命令**:
- `/opc` - 开始总编排
- `/opc-status` - 查看当前阶段
- `/opc-progress` - 查看进度
- `/opc-resume` - 恢复进度

---

### 02. opc-resource-inventory (资源盘点)

| 属性 | 值 |
|------|-----|
| **文件** | [sk-resource-inventory/SKILL.md](sk-resource-inventory/SKILL.md) |
| **阶段编号** | 01 |
| **阶段类型** | 线性阶段 |
| **核心功能** | 8类资源盘点（经验/人群/能力/关系/渠道/资产/约束/硬性边界） |

**命令**:
- `/opc-resource` - 开始资源盘点
- `/opc-resource 经验` - 盘点经验资源
- `/opc-resource 人群` - 盘点人群资源
- `/opc-resource 能力` - 盘点能力资源
- `/opc-resource 关系` - 盘点关系资源
- `/opc-resource 渠道` - 盘点渠道资源
- `/opc-resource 资产` - 盘点资产资源
- `/opc-resource 约束` - 盘点约束条件
- `/opc-resource 边界` - 盘点硬性边界
- `/opc-resource 报告` - 生成资源盘点报告

---

### 03. opc-niche-positioning (利基定位)

| 属性 | 值 |
|------|-----|
| **文件** | [sk-niche-positioning/SKILL.md](sk-niche-positioning/SKILL.md) |
| **阶段编号** | 02 |
| **阶段类型** | 线性阶段 |
| **核心功能** | 三环定位（能力×需求×杠杆）+ 6维机会评分 |

**命令**:
- `/opc-niche` - 开始利基定位
- `/opc-niche 三环` - 执行三环分析
- `/opc-niche 评分` - 6维机会评分
- `/opc-niche 对比` - 多选项对比
- `/opc-niche 确定` - 确定最终定位

---

### 04. opc-value-proposition (价值主张)

| 属性 | 值 |
|------|-----|
| **文件** | [sk-value-proposition/SKILL.md](sk-value-proposition/SKILL.md) |
| **阶段编号** | 03 |
| **阶段类型** | 线性阶段 |
| **核心功能** | Jobs/Pains/Gains框架 + 价值主张桥接 |

**命令**:
- `/opc-value` - 开始价值主张设计
- `/opc-value jobs` - 分析Jobs（要做的事）
- `/opc-value pains` - 分析Pains（痛苦点）
- `/opc-value gains` - 分析Gains（期望收益）
- `/opc-value 桥接` - 设计价值桥接
- `/opc-value 反向` - 反向价值主张

---

### 05. opc-business-model (商业模式)

| 属性 | 值 |
|------|-----|
| **文件** | [sk-business-model/SKILL.md](sk-business-model/SKILL.md) |
| **阶段编号** | 04 |
| **阶段类型** | 线性阶段 |
| **核心功能** | Lean Canvas九宫格 + 高风险假设识别 |

**命令**:
- `/opc-canvas` - 开始Lean Canvas
- `/opc-canvas 假设` - 识别高风险假设
- `/opc-canvas 验证` - 验证指定假设
- `/opc-canvas 打印` - 输出完整画布

---

### 06. opc-mvp-design (MVP设计)

| 属性 | 值 |
|------|-----|
| **文件** | [sk-mvp-design/SKILL.md](sk-mvp-design/SKILL.md) |
| **阶段编号** | 05 |
| **阶段类型** | 线性阶段 |
| **核心功能** | MVP三阶段模式（手工→流程化→产品化）+ 假设验证 |

**命令**:
- `/opc-mvp` - 开始MVP设计
- `/opc-mvp 假设` - 分析假设验证
- `/opc-mvp 类型` - 选择MVP类型
- `/opc-mvp 实验` - 设计验证实验
- `/opc-mvp 标准` - 定义成功标准

---

### 07. opc-conversion-loop (转化闭环)

| 属性 | 值 |
|------|-----|
| **文件** | [sk-conversion-loop/SKILL.md](sk-conversion-loop/SKILL.md) |
| **阶段编号** | 06 |
| **阶段类型** | 触发阶段（06） |
| **核心功能** | 触达→承接→信任→成交完整转化路径 |

**命令**:
- `/opc-conversion` - 开始转化闭环设计
- `/opc-conversion 漏斗` - 分析转化漏斗
- `/opc-conversion 触达` - 分析触达渠道
- `/opc-conversion 信任` - 设计信任建立
- `/opc-conversion 追销` - 设计追销体系
- `/opc-conversion 优化` - 优化指定阶段

---

### 08. opc-asset-accumulation (资产沉淀)

| 属性 | 值 |
|------|-----|
| **文件** | [sk-asset-accumulation/SKILL.md](sk-asset-accumulation/SKILL.md) |
| **阶段编号** | 08 |
| **阶段类型** | 触发阶段（取得成果后） |
| **核心功能** | 内容资产+方法论资产+客户资产+系统资产沉淀 |

**命令**:
- `/opc-asset` - 开始资产沉淀
- `/opc-asset 内容` - 评估内容资产
- `/opc-asset 方法` - 评估方法论资产
- `/opc-asset 客户` - 评估客户资产
- `/opc-asset 系统` - 评估系统资产
- `/opc-asset 优先级` - 确定沉淀优先级

---

### 09. opc-review (经营复盘)

| 属性 | 值 |
|------|-----|
| **文件** | [sk-review/SKILL.md](sk-review/SKILL.md) |
| **阶段编号** | 09 |
| **阶段类型** | 触发阶段（遇到瓶颈或定期） |
| **核心功能** | 瓶颈诊断 + 唯一重点 + 持续改进 |

**命令**:
- `/opc-review` - 开始经营复盘
- `/opc-review 日报` - 每日快速复盘
- `/opc-review 周报` - 每周定期复盘
- `/opc-review 月报` - 每月深度复盘
- `/opc-review 瓶颈` - 诊断当前瓶颈
- `/opc-review 唯一` - 确定唯一重点

---

## 与天龙引擎协同

| 天龙组件 | 协同方式 |
|---------|---------|
| **09-02 编排协调师** | OPC总编排集成，阶段调度 |
| **25-02 精益创业导师** | 与Minimalist Entrepreneur互补 |
| **50-01 产品策划** | 利基定位与PRD协同 |
| **35-02 社媒运营** | 转化闭环与渠道运营协同 |

## 相关资源

- [OPC技能集网站](https://opc-skills.ft07.com/)
- [视频讲解(B站)](https://www.bilibili.com/video/BV1JMDQBiEjx)
- [方糖真实创业模拟器](https://ft07.com/real-business-simulator/)
- [GitHub源码](https://github.com/easychen/opc-methodology)
