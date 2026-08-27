# BD Record · BD记录管理 V1.0

> 商业拓展记录 · 潜客追踪 · 触达历史

**来源**: xiaobei/TeamWiseFlow
**License**: OpenClaw + MIT
**版本**: 1.0

---

## 我是谁

BD Record 是商业拓展的记录工具，帮助追踪潜客信息、记录触达历史、管理跟进状态。

---

## 核心能力

### 添加潜客

```bash
./scripts/add.sh \
  --platform xiaohongshu \
  --creator-id abc123 \
  --nickname "某博主" \
  --qualified 1 \
  --notes "有电商经验"
```

### 记录触达

```bash
./scripts/contact.sh \
  --lead-id lead_xxx \
  --channel dm \
  --content "发送合作邀约"
```

### 状态更新

```bash
./scripts/update.sh \
  --lead-id lead_xxx \
  --status interested
```

---

## 数据存储

| 文件 | 说明 |
|------|------|
| `~/.dragon-engine/opc/bd/` | BD数据库 |
| `~/.dragon-engine/opc/bd/leads.json` | 潜客记录 |
| `~/.dragon-engine/opc/bd/outreach.json` | 触达记录 |

---

## License

OpenClaw 开源协议 · MIT 兼容
