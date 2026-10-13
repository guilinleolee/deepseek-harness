# OPC融合报告 · xiaobei × dragon-engine

> **融合日期**: 2026-08-17
> **来源**: TeamWiseFlow/xiaobei (OpenClaw开源)
> **License**: OpenClaw开源 + MIT

---

## 执行摘要

| 项目 | 内容 |
|------|------|
| **来源项目** | xiaobei (TeamWiseFlow/OpenClaw) |
| **目标项目** | dragon-engine (天龙引擎) |
| **融合方式** | 技术借鉴 + 能力嫁接 |
| **新增阶段** | 36-37 (OPC融合 + OPC×天龙融合) |
| **新增资产** | 3 skills + 1 agent + 4 scripts |

---

## 一、融合内容清单

### 1.1 新增Skills (3个)

| Skill | 版本 | 来源 | 用途 |
|-------|------|------|------|
| `opc-content-calibrator/` | V1.0 | xiaobei | 7维内容打分+盲预测+复盘+rubric进化 |
| `opc-lead-hunting/` | V1.0 | xiaobei | 潜客挖掘（策略A/B）+多平台联动 |
| `opc-investor-pipeline/` | V1.0 | xiaobei | 投资人发掘→材料→触达→状态跟踪 |

### 1.2 新增Agent (1个)

| Agent | 版本 | 用途 |
|-------|------|------|
| `agents/opc-suite/` | V1.0 | OPC套件协调Agent（融合xiaobei+天龙） |

### 1.3 新增Scripts (4个)

| Script | 用途 |
|--------|------|
| `opc-content-calibrator/scripts/score-only.sh` | 7维打分校验 |
| `opc-content-calibrator/scripts/init.sh` | 校准系统初始化 |
| `opc-content-calibrator/scripts/cal-toggle.sh` | 平台校准开关管理 |
| `opc-content-calibrator/scripts/commit-prediction.sh` | 打分+预测落盘 |

---

## 二、融合架构

```
┌─────────────────────────────────────────────────────────────┐
│                 xiaobei OPC能力 (来源)                        │
├─────────────────────────────────────────────────────────────┤
│  Content Calibrator  │  Lead Hunting  │  Investor Pipeline  │
│  (7维打分+预测)     │  (潜客挖掘)    │  (投资人关系)       │
└─────────┬───────────┴───────┬────────┴────────┬──────────┘
          │                   │                │
          ▼                   ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│              dragon-engine 融合层                           │
├─────────────────────────────────────────────────────────────┤
│                    OPC Suite Agent                          │
│  (协调三个OPC能力 + 天龙引擎核心能力)                       │
└─────────┬───────────┴───────┬────────┴────────┬──────────┘
          │                   │                │
          ▼                   ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│              dragon-engine 核心能力 (赋能)                   │
├─────────────────────────────────────────────────────────────┤
│  博主全息克隆  │  三模态生成  │  9平台分发  │  28-10财经底座 │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、融合点详解

### 3.1 内容校准 × 天龙引擎

| 天龙能力 | × OPC校准 | = 融合效果 |
|----------|-----------|------------|
| 博主全息克隆 | 7维打分 | **博主风格内容自动评估** |
| 三模态生成 | 质量门控 | **产出质量标准化** |
| 老李风分镜 | rubric进化 | **内容风格持续优化** |
| viral-chaser | 追爆打分 | **爆款规律提炼** |

### 3.2 潜客挖掘 × 天龙引擎

| 天龙能力 | × OPC潜客 | = 融合效果 |
|----------|-----------|------------|
| 博主全息克隆 | 粉丝画像 | **博主粉丝价值评估** |
| 9平台分发 | 评论区挖掘 | **全域用户触达** |
| 三模态生成 | 个性化话术 | **AI个性化触达** |
| viral-chaser | 竞对分析 | **竞对用户转化** |

### 3.3 投资人关系 × 天龙引擎

| 天龙能力 | × OPC IR | = 融合效果 |
|----------|---------|------------|
| 28-10财经底座 | 投资人发掘 | **行业投资动态监控** |
| 博主克隆 | 创始人包装 | **创始人IP打造** |
| 三模态生成 | 路演材料 | **可视化融资呈现** |
| A股金融底座 | 尽职调查 | **数据驱动DD** |

---

## 四、典型工作流

### 4.1 内容生产 → 发布 → 复盘

```
1. 天龙引擎生成内容（小红书图文/视频脚本）
   ↓
2. OPC Content Calibration 7维打分
   ↓
3. 达标 → 9平台分发
   ↓
4. T+3d → 数据复盘 → rubric进化
```

### 4.2 竞对分析 → 潜客触达

```
1. viral-chaser追竞对爆款
   ↓
2. OPC Lead Hunting挖掘竞对粉丝
   ↓
3. 天龙引擎生成个性化触达内容
   ↓
4. 多平台触达
```

### 4.3 创业融资

```
1. 28-10财经底座分析行业动态
   ↓
2. OPC Investor Pipeline发掘投资人
   ↓
3. 天龙引擎生成数据驱动BP
   ↓
4. 个性化触达 → 跟进
```

---

## 五、License合规

| 来源 | License | 天龙融合 | 合规状态 |
|------|---------|----------|----------|
| xiaobei | OpenClaw开源 | MIT兼容 | ✅ 合规 |
| dragon-engine | MIT为主 | - | ✅ 合规 |

**注意**: OpenClaw开源协议允许商业使用，天龙引擎MIT协议允许自由融合。

---

## 六、版本演进

| 版本 | 日期 | 关键变更 |
|------|------|----------|
| V1.0 | 2026-08-17 | 初始融合：3 skills + 1 agent |

---

## 七、后续计划

| 优先级 | 任务 | 状态 |
|--------|------|------|
| P0 | ✅ content-calibrator 7维打分 | 完成 |
| P0 | ✅ lead-hunting 潜客挖掘 | 完成 |
| P0 | ✅ investor-pipeline 投资人关系 | 完成 |
| P1 | ⏳ 集成smart-search零key搜索 | 待办 |
| P1 | ⏳ 与bd-record数据打通 | 待办 |
| P2 | ⏳ 与天龙引擎9平台分发联动 | 待办 |
| P2 | ⏳ 与28-10财经底座打通 | 待办 |

---

## 八、验证

### 8.1 文件验证

```bash
# 检查skill文件
ls -la skills/opc-content-calibrator/
ls -la skills/opc-lead-hunting/
ls -la skills/opc-investor-pipeline/

# 检查agent文件
ls -la agents/opc-suite/

# 检查脚本
ls -la skills/opc-content-calibrator/scripts/
```

### 8.2 索引验证

```bash
# 检查BIBLE.md
grep -n "OPC融合" BIBLE.md

# 检查00-INDEX.md
grep -n "OPC" skills/00-INDEX.md
```

---

## 九、参考资源

- **xiaobei原仓**: https://github.com/TeamWiseFlow/xiaobei
- **OpenClaw底座**: https://github.com/openclaw/openclaw
- **dragon-engine**: C:/Users/li/.claude/projects/dragon-engine/
