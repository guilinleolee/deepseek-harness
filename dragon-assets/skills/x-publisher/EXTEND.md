# X-Publisher EXTEND.md

## 默认配置扩展

---

## 自定义发布配置 (Custom Publishing Settings)

在 `~/.claude/skills/x-publisher/EXTEND.md` 中添加：

```markdown
## Custom Publishing

### my-account-config
- account: "@myhandle"
- default_mode: thread
- auto_split: true
- max_length: 280
- image_compression: true
```

---

## 自定义Thread模板 (Custom Thread Templates)

```markdown
## Thread Templates

### article-thread
- template: |
    1/{total}: {intro}
    |
    {thread_body}
    |
    {total}/{total}: {conclusion}
- separator: "\n\n🧵\n\n"
```

---

## Cookie管理配置

```markdown
## Cookie Management

### cookie-paths
- storage: ~/.claude/skills/x-publisher/cookies/
- format: json
- encryption: true
```

---

## 调试选项

```markdown
## Debug Options

### verbose-logging
- log_level: debug
- save_screenshot: true
- save_html: true
- trace_errors: true
```

---

## 加载优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/x-publisher/EXTEND.md`
- **用户级**: `~/.claude/skills/x-publisher/EXTEND.md`
- **默认级**: `skills/x-publisher/EXTEND.md`

---

## 使用示例

### 自定义账号配置
```markdown
## Custom Publishing

### brand-account
- account: "@BrandName"
- default_mode: thread
- hashtag_strategy: auto
- mention_strategy: first_only
- publish_time: 09:00,18:00
```

### 自定义Thread分割规则
```markdown
## Thread Rules

### my-split-rules
- max_chars_per_tweet: 270
- preserve_sentences: true
- split_at_paragraphs: true
- add_continuation: true
```
