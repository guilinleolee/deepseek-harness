---
license: UNKNOWN
name: content-curator-framework
description: General-purpose content curation framework that wraps any RSS/JSON feed sources with customizable remix prompts. Configure feeds, customize prompts, and deliver curated digests via stdout, Telegram, or email. No API keys required for feed ingestion.
triggers: ["content curator framework", "Content Curator Framework"]
---

# Content Curator Framework

A reusable framework for building feed-based content digests. Provide any set of RSS feeds or JSON endpoints,
customize the remix prompts, and get a polished digest delivered anywhere.

## Architecture

```
Feed Sources (RSS/JSON)
    ↓
prepare-digest.js  ← configurable feed URLs + prompt priority chain
    ↓
Single JSON blob  ← podcasts, feeds, prompts
    ↓
LLM Remix  ← follows prompt files
    ↓
Digest Output  → stdout / Telegram / Email / Feishu
```

## Configuration

Create `~/.content-curator/config.json`:

```json
{
  "platform": "other",
  "language": "en",
  "frequency": "daily",
  "deliveryTime": "08:00",
  "delivery": { "method": "stdout" },
  "feeds": {
    "x": "https://example.com/feed-x.json",
    "podcasts": "https://example.com/feed-podcasts.json",
    "blogs": "https://example.com/feed-blogs.json"
  },
  "onboardingComplete": true
}
```

## Prompt Priority Chain

Prompts are loaded in this order (first found wins):

1. **User custom** — `~/.content-curator/prompts/<file>`
2. **Remote** — fetched from `promptRemoteBase` URL in config
3. **Local default** — `prompts/<file>` shipped with this skill

This lets you customize prompts locally without losing central updates.

## Prompt Files

Five prompt files control how content is remixed:

| File | Key | Purpose |
|------|-----|---------|
| `digest-intro.md` | `digest_intro` | Overall framing, section order, formatting rules |
| `summarize-tweets.md` | `summarize_tweets` | How to remix X/Twitter posts |
| `summarize-podcasts.md` | `summarize_podcasts` | How to remix podcast transcripts |
| `summarize-blogs.md` | `summarize_blogs` | How to remix blog posts |
| `translate.md` | `translate` | Chinese translation rules |

### Prompt Authoring Guidelines

**digest-intro.md** (section order + formatting):
- Section order: Official Blogs → X/Twitter → Podcasts
- Every item MUST include its source URL
- No @ handles on Twitter (write full names instead)
- Never fabricate content — only remix what is in the JSON
- Footer: "Curated through the Content Curator Framework"

**summarize-tweets.md**:
- 2-4 sentences per builder
- Format: "Full Name, Role/Company" (e.g. "Box CEO Aaron Levie")
- Bold predictions and hot takes lead
- Skip mundane tweets and self-promotion
- Include the tweet URL from the JSON

**summarize-podcasts.md**:
- 200-400 words
- "The Takeaway:" as the first sentence
- Include a memorable direct quote
- Write for a non-expert audience
- Include the podcast URL and episode title from the JSON

**summarize-blogs.md**:
- 100-300 words
- Lead with the core announcement or finding
- Include specific numbers and named features
- At least one direct quote
- Call out practical implications for practitioners
- Include the blog URL from the JSON

**translate.md**:
- Full natural simplified Mandarin
- English for: AI, LLM, GPU, API, fine-tuning, RAG, token, prompt, agent, transformer
- Proper nouns in English
- No em-dashes
- Professional but conversational tone

## Content Types

### X / Twitter

Expected JSON shape:
```json
{
  "generatedAt": "ISO timestamp",
  "x": [{
    "name": "Display Name",
    "bio": "Short bio, e.g. 'CEO @company'",
    "handle": "@handle",
    "tweets": [{
      "text": "Tweet text",
      "url": "https://x.com/user/status/123",
      "createdAt": "ISO timestamp"
    }]
  }]
}
```

### Podcasts

Expected JSON shape:
```json
{
  "generatedAt": "ISO timestamp",
  "lookbackHours": 72,
  "podcasts": [{
    "name": "Podcast Name",
    "title": "Episode Title",
    "url": "https://youtube.com/watch?v=...",
    "publishedAt": "ISO timestamp",
    "transcript": "Full transcript text..."
  }]
}
```

### Blogs

Expected JSON shape:
```json
{
  "generatedAt": "ISO timestamp",
  "lookbackHours": 72,
  "blogs": [{
    "name": "Blog Name",
    "title": "Post Title",
    "url": "https://example.com/post",
    "publishedAt": "ISO timestamp",
    "author": "Author Name",
    "content": "Full article text..."
  }]
}
```

## Digest Output

The LLM assembles the digest following `digest_intro`:

```
## Official Blog Posts

[Blog Name]
[Title]
Summary paragraph (100-300 words)
Author Name | [Link]

## X / Twitter

[Name, Role] on what they said and why it matters.
[Link]

[Next builder...]

## Podcasts

[Podcast Name]
[Episode Title](URL)
Summary paragraph (200-400 words)
"The Takeaway: ..."
```

## Content Ordering

Content appears in this order: Official Blogs → X/Twitter → Podcasts.
Each section is only shown if content exists.

## Language Modes

- **en** — full digest in English
- **zh** — full digest in simplified Mandarin, following `translate` prompt
- **bilingual** — interleaved paragraph-by-paragraph English then Chinese

## Delivery

Set `delivery.method` in config:

- **stdout** — print digest to terminal (default)
- **telegram** — send via Telegram bot (requires `TELEGRAM_BOT_TOKEN` + `chatId`)
- **email** — send via Resend (requires `RESEND_API_KEY` + `email` address)
- **feishu** — send via Feishu/Lark IM (reads credentials from `~/.openclaw/openclaw.json`, no extra config needed)

---

Curated through the Content Curator Framework
