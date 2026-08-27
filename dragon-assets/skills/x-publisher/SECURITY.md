# SECURITY.md - X Publisher 社媒发布安全指南

> ⚠️ 本Skill涉及社交媒体发布，请务必阅读本文档

---

## 🔴 高风险操作

### 发布到X/Twitter (publish.sh)

**风险**: 发布后内容公开可见，无法完全撤回

**症状**:
- 发布了错误的内容
- 发布了敏感信息
- 发布了未审核的内容

**安全操作流程**:
```bash
# 1. 先预览内容
./publish.sh --preview

# 2. 确认图片和链接
./publish.sh --check-media

# 3. 发布
./publish.sh "内容" --images img1.png,img2.png
```

### 批量发布

**风险**: 批量发布可能被平台识别为垃圾信息

**安全操作流程**:
```bash
# 1. 检查发布间隔（建议≥5分钟）
./publish.sh --interval 300

# 2. 限制单次发布数量（建议≤10条）
./publish.sh --batch-limit 10
```

---

## 🟡 中风险操作

### 定时发布

**风险**: 定时发布可能在敏感时期触发

**安全操作流程**:
```bash
# 1. 检查发布时间是否合适
./publish.sh --schedule "2026-03-18 10:00" --check

# 2. 设置发布提醒
./publish.sh --schedule "2026-03-18 10:00" --reminder
```

### 带图片发布

**风险**: 图片可能包含敏感信息（EXIF、背景等）

**安全操作流程**:
```bash
# 1. 检查图片EXIF信息
./publish.sh --check-exif image.png

# 2. 移除敏感EXIF
./publish.sh --strip-exif image.png

# 3. 发布
./publish.sh "内容" --images image.png
```

---

## 📋 平台限制

| 平台 | 字符限制 | 图片限制 | 频率限制 |
|------|---------|---------|---------|
| X/Twitter | 280字符 | 4张 | 300条/3小时 |
| Twitter Blue | 4000字符 | 4张 | 同上 |

---

## 🐛 常见陷阱

### 陷阱1: 发布了测试内容

**症状**: 测试内容被发布到生产账号

**原因**: 未检查账号环境

**解决方案**:
```bash
# 发布前确认账号
./publish.sh --whoami

# 使用测试账号预览
./publish.sh --test-account "内容"
```

### 陷阱2: 图片包含敏感信息

**症状**: 发布后发现在图片中泄露了敏感信息

**原因**: 未检查图片背景/EXIF

**解决方案**:
```bash
# 发布前自动检查图片
./publish.sh "内容" --images img.png --auto-check
```

### 陷阱3: 链接错误

**症状**: 发布的链接无法访问或指向错误页面

**原因**: 未验证链接

**解决方案**:
```bash
# 发布前验证所有链接
./publish.sh "内容 https://example.com" --validate-links
```

---

## 📞 紧急处理

如果发布了错误内容：

1. **立即删除**: 在X上删除推文
2. **截图保存**: 删除前截图用于记录
3. **通知团队**: 在内部频道说明情况
4. **复盘改进**: 记录教训到lessons.md

---

**版本**: 1.0.0
**更新时间**: 2026-03-18