# Obsidian CLI 快速命令参考

## Vault 管理

```bash
# 添加 vault
notesmd-cli add-vault /path/to/vault --set-default

# 列出所有 vault
notesmd-cli list-vaults

# 获取默认 vault 路径
notesmd-cli list-vaults --default --path-only

# 设置默认 vault
notesmd-cli set-default-vault "vault-name"
```

## 笔记操作

```bash
# 创建
notesmd-cli create "笔记名.md" --content "内容"
notesmd-cli create "笔记名.md" --content "内容" --append    # 追加
notesmd-cli create "笔记名.md" --content "内容" --overwrite  # 覆盖

# 读取
notesmd-cli print "笔记名.md"
notesmd-cli open "笔记名.md"              # 在 Obsidian 打开
notesmd-cli open "笔记名.md" --editor    # 在编辑器打开

# 更新
notesmd-cli move "旧名.md" "新名.md"     # 重命名
notesmd-cli move "旧名.md" "新名.md" --open  # 重命名后打开

# 删除
notesmd-cli delete "笔记名.md"
```

## 搜索

```bash
# 模糊搜索文件名
notesmd-cli search

# 搜索内容（非交互）
notesmd-cli search-content "关键词" --no-interactive

# 搜索并输出 JSON
notesmd-cli search-content "关键词" --format json
```

## 每日日记

```bash
# 打开/创建今日日记
notesmd-cli daily

# 带内容
notesmd-cli daily --content "今日完成：xxx"

# 在编辑器打开
notesmd-cli daily --editor
```

## Frontmatter

```bash
# 查看
notesmd-cli frontmatter "笔记.md" --print

# 编辑
notesmd-cli frontmatter "笔记.md" --edit --key "tags" --value "[a, b]"
notesmd-cli frontmatter "笔记.md" --edit --key "status" --value "done"

# 删除
notesmd-cli frontmatter "笔记.md" --delete --key "draft"
```

## 常用组合

```bash
# 快速记录灵感
notesmd-cli create "灵感-$(date +%Y%m%d).md" --content "# 灵感\n$(date +%H:%M) "

# 批量标签
for f in *.md; do
  notesmd-cli frontmatter "$f" --edit --key "tags" --value "[archived]"
done

# 导出 vault 搜索结果
notesmd-cli search-content "关键词" --format json > results.json
```

## 快捷变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `$(date +%Y-%m-%d)` | 当前日期 | 2026-08-16 |
| `$(date +%Y%m%d)` | 当前日期(无分隔) | 20260816 |
| `$(date +%H:%M)` | 当前时间 | 14:30 |
| `$VAULT_PATH` | 默认 vault 路径 | /path/to/vault |
