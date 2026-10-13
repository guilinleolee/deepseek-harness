# IR Record · 投资人关系记录 V1.0

> 投资人信息管理 · 触达记录 · 状态追踪

**来源**: xiaobei/TeamWiseFlow
**License**: OpenClaw + MIT
**版本**: 1.0

---

## 我是谁

IR Record 是投资人关系管理的轻量级工具，记录投资人信息、触达历史和状态变更。

---

## 核心能力

### 添加投资人

```bash
./scripts/add.sh \
  --name "张三" \
  --firm "红杉资本" \
  --type "VC" \
  --match-score "high"
```

### 记录触达

```bash
./scripts/contact.sh \
  --investor-id inv_xxx \
  --channel "email" \
  --content "发送BP"
```

### 更新状态

```bash
./scripts/update.sh \
  --investor-id inv_xxx \
  --status "contacted"
```

---

## 数据存储

| 文件 | 说明 |
|------|------|
| `~/.dragon-engine/opc/ir/` | IR数据库 |
| `~/.dragon-engine/opc/ir/investors.json` | 投资人记录 |

---

## License

OpenClaw 开源协议 · MIT 兼容
