# OPC Investor Pipeline · 投资人关系管理 V1.0

> 投资人发掘 · 触达材料生成 · 状态机推进

**来源**: xiaobei/TeamWiseFlow
**License**: OpenClaw + MIT
**版本**: 1.0

---

## 我是谁

OPC Investor Pipeline 是创业公司融资的智能助手，帮助发掘目标投资人、管理触达记录、推进融资状态机。

---

## 核心能力

### 投资人发掘

```bash
# 按行业发掘
./scripts/discover.sh --industry "消费,电商" --stage "A轮"

# 按关键词搜索
./scripts/search.sh --keywords "消费投资,新品牌"
```

### 触达材料生成

```bash
# 生成 BP 摘要
./scripts/generate-deck.sh \
  --investor-id inv_xxx \
  --company-name "XX品牌" \
  --stage "pre-A"
```

### 状态机管理

```bash
# 更新状态
./scripts/update-status.sh --investor-id inv_xxx --status contacted

# 查看详情
./scripts/view.sh --investor-id inv_xxx
```

---

## 投资人状态机

```
new → identified → researched → pitched → meeting → DD → term → closed
                        ↓
                    not_interested (终态)
```

| 状态 | 说明 |
|------|------|
| new | 新发现 |
| identified | 已确认身份 |
| researched | 已调研完毕 |
| pitched | 已投递 |
| meeting | 约到 meetings |
| DD | 尽职调查中 |
| term | 谈 term sheet |
| closed | 融资关闭 |
| not_interested | 无兴趣 |

---

## 数据存储

| 文件 | 说明 |
|------|------|
| `~/.dragon-engine/opc/investors/` | 投资人数据库 |
| `~/.dragon-engine/opc/investors/index.json` | 投资人索引 |
| `~/.dragon-engine/opc/outreach/` | 触达记录 |

---

## License

OpenClaw 开源协议 · MIT 兼容
