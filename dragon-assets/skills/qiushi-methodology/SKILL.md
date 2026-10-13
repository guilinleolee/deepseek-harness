---
license: UNKNOWN
triggers: ["qiushi methodology", "求是方法论工具包 (Qiushi Methodology Toolkit)"]
---
# 求是方法论工具包 (Qiushi Methodology Toolkit)

## 版本信息
- **版本**: V1.0
- **日期**: 2026-04-08
- **来源**: HughYau/qiushi-skill (835 Stars)
- **集成**: 天龙引擎V8.86

## 核心理念
> "实事求是" —— 一切从实际出发，理论联系实际，在实践中检验真理和发展真理。

## 四大哲学基座

```
┌─────────────────────────────────────────────────────────────┐
│                    求是方法论 四层架构                        │
├─────────────────────────────────────────────────────────────┤
│  总原则: 实事求是                                             │
│  ├── 事实先于结论，不对事实挑三拣四                          │
│  ├── 结论必须由事实推导，不能先有结论再找证据               │
│  └── 承认"不知道"是诚实的调查结论                           │
├─────────────────────────────────────────────────────────────┤
│  第一层·哲学基座                                            │
│  ├── 矛盾分析法 (maodun-fenxi)                           │
│  └── 实践认识论 (shijian-renshi)                          │
├─────────────────────────────────────────────────────────────┤
│  第二层·工作方法                                            │
│  ├── 调查研究 (diaoyan-yanjiu)                             │
│  ├── 群众路线 (qunzhong-luxian)                           │
│  └── 批评与自我批评 (piping-ziwo)                         │
├─────────────────────────────────────────────────────────────┤
│  第三层·战略战术                                            │
│  ├── 持久战略 (chijiujizhan)                              │
│  ├── 集中兵力 (jizhong-bingli)                            │
│  ├── 星火燎原 (xinghuo-liaoyuan)                          │
│  └── 统筹兼顾 (tongchou-jianbei)                         │
└─────────────────────────────────────────────────────────────┘
```

## 11个核心Skill

| Skill | 教员思想 | 核心功能 |
|-------|---------|---------|
| **shijiuqishi** | 实事求是（总原则） | 一切判断的元规则 |
| **maodun-fenxi** | 矛盾分析法 | 六步分析框架 |
| **shijian-renshi** | 实践认识论 | 认知-实践-再认知迭代 |
| **diaoyan-yanjiu** | 调查研究 | 七项注意+五步流程 |
| **qunzhong-luxian** | 群众路线 | 命令主义/尾巴主义双避 |
| **piping-ziwo** | 批评与自我批评 | 治病救人+建设性改进 |
| **chijiujizhan** | 持久战略 | 阶段划分+耐心坚持 |
| **jizhong-bingli** | 集中兵力 | 优先级矩阵+彻底解决 |
| **xinghuo-liaoyuan** | 星火燎原 | MVP+根据地四要素 |
| **tongchou-jianbei** | 统筹兼顾 | 六步动态平衡法 |

## 与天龙引擎协同

| 天龙组件 | 求是Skill协同 | 效果 |
|---------|--------------|------|
| 00分析师 | 矛盾分析法+统筹兼顾 | 决策质量+25% |
| 01调研师 | 调查研究+实践认识论 | 调研系统性质的飞跃 |
| 02架构师 | 统筹兼顾+持久战略 | 长期架构分阶段策略 |
| 06审查师 | 批评与自我批评 | 治病救人原则升级 |
| 09-05求是协调师 | 九大工具统一调度 | 方法论完整闭环 |

## 核心命令

```bash
# 总原则启动
/qiushi [问题描述]         # 启动求是方法论流程
/shijiuqishi              # 实事求是检查

# 哲学基座
/maodun [复杂问题]        # 矛盾分析法
/shijian-renshi           # 实践认识论

# 工作方法
/diaoyan [调研主题]       # 调查研究
/qunzhong                 # 群众路线
/piping-ziwo              # 批评与自我批评

# 战略战术
/chijiujizhan             # 持久战略
/jizhong-bingli           # 集中兵力
/xinghuo-liaoyuan         # 星火燎原
/tongchou-jianbei         # 统筹兼顾
```

## 使用场景

| 场景 | 推荐Skill | 触发条件 |
|------|---------|---------|
| 复杂问题决策 | maodun-fenxi | 多个矛盾力量冲突 |
| 陌生领域调研 | diaoyan-yanjiu | 信息不足、凭直觉判断 |
| 团队意见整合 | qunzhong-luxian | 多方意见不一致 |
| 质量审查改进 | piping-ziwo | 工作成果需要复盘 |
| 长期复杂任务 | chijiujizhan | 工期>2周、多个阶段 |
| 资源有限聚焦 | jizhong-bingli | 并行任务>3个 |
| 从零起步项目 | xinghuo-liaoyuan | MVP切入口不明确 |
| 多维度权衡 | tongchou-jianbei | 速度vs质量、短期vs长期 |

## 文件结构

```
qiushi-methodology/
├── SKILL.md                    # 本文件
├── shijiuqishi/SKILL.md       # 实事求是
├── maodun-fenxi/SKILL.md     # 矛盾分析法
├── shijian-renshi/SKILL.md    # 实践认识论
├── diaoyan-yanjiu/SKILL.md    # 调查研究
├── qunzhong-luxian/SKILL.md  # 群众路线
├── piping-ziwo/SKILL.md       # 批评与自我批评
├── chijiujizhan/SKILL.md     # 持久战略
├── jizhong-bingli/SKILL.md   # 集中兵力
├── xinghuo-liaoyuan/SKILL.md # 星火燎原
└── tongchou-jianbei/SKILL.md # 统筹兼顾
```
