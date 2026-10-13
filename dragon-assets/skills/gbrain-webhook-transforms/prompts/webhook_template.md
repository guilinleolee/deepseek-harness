# GBrain Webhook Event Template
# Webhook 事件模板

---

## 自定义 Webhook 格式

```json
{
  "source": "custom",
  "entity_type": "company",
  "slug": "acme-corp",
  "event": {
    "type": "funding_round",
    "data": {
      "round": "Series C",
      "amount": "$100M",
      "date": "2026-01-15",
      "investors": ["a16z", "Sequoia"]
    }
  },
  "confidence": 0.95,
  "raw": {}
}
```

---

## GitHub Push Event

```json
{
  "repository": {
    "full_name": "owner/repo",
    "html_url": "https://github.com/owner/repo"
  },
  "ref": "refs/heads/main",
  "commits": [
    {
      "id": "abc123def456",
      "timestamp": "2026-04-18T10:30:00Z",
      "author": {
        "name": "Author Name",
        "email": "author@example.com",
        "username": "author"
      },
      "message": "feat: add new feature",
      "url": "https://github.com/owner/repo/commit/abc123"
    }
  ],
  "pusher": {
    "name": "pusher",
    "email": "pusher@example.com"
  }
}
```

---

## GitHub Pull Request Event

```json
{
  "action": "opened",
  "number": 42,
  "repository": {
    "full_name": "owner/repo"
  },
  "pull_request": {
    "id": 987654321,
    "number": 42,
    "title": "Add amazing feature",
    "body": "This PR adds an amazing feature.",
    "state": "open",
    "html_url": "https://github.com/owner/repo/pull/42",
    "user": {
      "login": "contributor",
      "avatar_url": "https://avatars.githubusercontent.com/u/123"
    },
    "labels": [
      {"name": "enhancement", "color": "84b6eb"},
      {"name": "needs-review", "color": "fbca04"}
    ],
    "created_at": "2026-04-18T10:00:00Z",
    "updated_at": "2026-04-18T10:30:00Z"
  }
}
```

---

## GitHub Issue Event

```json
{
  "action": "opened",
  "repository": {
    "full_name": "owner/repo"
  },
  "issue": {
    "id": 123456789,
    "number": 100,
    "title": "Bug: Something is broken",
    "body": "Description of the bug...",
    "state": "open",
    "html_url": "https://github.com/owner/repo/issues/100",
    "user": {
      "login": "reporter",
      "avatar_url": "https://avatars.githubusercontent.com/u/456"
    },
    "labels": [
      {"name": "bug", "color": "d73a4a"},
      {"name": "priority-high", "color": "b60205"}
    ],
    "assignees": [
      {"login": "maintainer1"},
      {"login": "maintainer2"}
    ],
    "created_at": "2026-04-18T09:00:00Z"
  }
}
```

---

## Slack Message Event

```json
{
  "channel": {
    "id": "C0123456789",
    "name": "engineering"
  },
  "user": {
    "id": "U0123456789",
    "name": "alice",
    "real_name": "Alice Chen"
  },
  "text": "The deployment is complete!",
  "ts": "1713430200.123456",
  "thread_ts": "1713430000.000000",
  "reply_count": 3,
  "reactions": [
    {"name": "rocket", "users": ["U111111", "U222222"], "count": 2}
  ]
}
```

---

## RSS Entry

```json
{
  "title": "Article Title",
  "link": "https://example.com/article",
  "published": "2026-04-18T08:00:00Z",
  "author": "Author Name",
  "summary": "Brief summary of the article content...",
  "content": "Full article content in HTML..."
}
```

---

## Calendar Event

```json
{
  "id": "event_123",
  "summary": "Team Standup Meeting",
  "description": "Daily standup - 15 minutes",
  "start": {
    "dateTime": "2026-04-18T09:00:00+08:00",
    "timeZone": "Asia/Shanghai"
  },
  "end": {
    "dateTime": "2026-04-18T09:15:00+08:00",
    "timeZone": "Asia/Shanghai"
  },
  "attendees": [
    {"email": "alice@example.com", "responseStatus": "accepted"},
    {"email": "bob@example.com", "responseStatus": "accepted"},
    {"email": "carol@example.com", "responseStatus": "declined"}
  ],
  "conferenceData": {
    "entryPoints": [
      {"entryPointType": "video", "uri": "https://meet.example.com/abc123"}
    ]
  }
}
```

---

## 字段映射参考

| Webhook 字段 | GBrain frontmatter | 说明 |
|-------------|-------------------|------|
| `title` | `title` | 实体标题 |
| `type` / `event.type` | `type` | 实体类型: timeline-event/discussion/external-info |
| `source` | `source` | 来源: github/slack/rss/calendar/custom |
| `timestamp` / `created_at` | `created` | 创建时间 |
| `author` / `user.login` | `author` | 作者/提交者 |
| `url` / `html_url` | `url` | 原始链接 |
| `tags` | `tags` | 标签数组 |

---

*模板由 GBrain Webhook Transforms Skill 使用*
