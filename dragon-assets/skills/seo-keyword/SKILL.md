---
license: UNKNOWN
name: seo-keyword
description: >
  Keyword research and analysis for SEO. Covers keyword discovery, search volume
  analysis, competition assessment, search intent classification, and keyword
  clustering. Use when user says "keyword research", "keyword analysis",
  "search volume", "long-tail keywords", "keyword opportunities",
  or "keyword clustering".
user-invokable: true
argument-hint: "[seed keyword or topic]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - WebFetch
  - WebSearch
triggers:
  - "seo keyword"
  - "keyword research"
  - "关键词研究"
  - "搜索量分析"
---

# SEO Keyword Research

## Overview

Keyword research is the foundation of SEO strategy. This skill helps identify high-value keywords that drive targeted traffic.

## Keyword Research Framework

### 1. Seed Keyword Expansion

Start with a seed keyword and expand using:

| Method | Tools/Sources |
|--------|---------------|
| **Brainstorming** | Related searches, "People also ask", autocomplete |
| **Competitor Analysis** | Top ranking pages for seed keyword |
| **Question Mining** | Forums, Quora, Reddit, "how to" patterns |
| **LSI Keywords** | Semantic variations and related terms |
| **Google Suggest** | Autocomplete and related searches |

### 2. Keyword Metrics Analysis

| Metric | Description | Target Range |
|--------|-------------|--------------|
| **Search Volume** | Monthly searches | 100-10,000 (varies by niche) |
| **Keyword Difficulty (KD)** | Competition level | <40 for new sites, <60 for established |
| **CPC** | Commercial value indicator | Higher = more commercial intent |
| **Trends** | Seasonality and trend direction | Growing or stable preferred |

### 3. Search Intent Classification

| Intent | User Goal | Content Type |
|--------|-----------|--------------|
| **Informational** | Learn something | Blog posts, guides, tutorials |
| **Navigational** | Find a specific site | Brand pages, login pages |
| **Transactional** | Buy something | Product pages, checkout |
| **Commercial Investigation** | Compare before buying | Comparisons, reviews |

### 4. Keyword Clustering

Group related keywords to create topic-focused content:

```
Cluster: "CRM Software"
├── Primary: "best CRM software"
├── Secondary: "CRM software for small business"
├── Secondary: "affordable CRM"
└── Long-tail: "easy to use CRM for sales teams"
```

## Data Sources

### Free Tools
- Google Keyword Planner (requires ad account)
- Google Trends
- Google Search Console (your own data)
- Ubersuggest
- AnswerThePublic

### Paid Tools (via MCP)
- **DataForSEO**: `kw_data_google_ads_search_volume`, `dataforseo_labs_bulk_keyword_difficulty`, `dataforseo_labs_search_intent`
- Ahrefs API
- SEMrush API

## Keyword Research Workflow

### Step 1: Seed Selection
```
1. Identify main product/topic
2. List 5-10 seed keywords
3. Note user's target audience
```

### Step 2: Expansion
```
1. Generate 50-100 related keywords
2. Include question modifiers (how, what, why, where)
3. Include long-tail variations
4. Note search intent for each
```

### Step 3: Analysis
```
1. Gather search volume data
2. Assess keyword difficulty
3. Classify search intent
4. Identify seasonality
```

### Step 4: Prioritization
```
1. Score by opportunity (Volume × Intent × Difficulty)
2. Identify quick wins (low KD, good volume)
3. Plan content for high-value targets
```

## Output Format

Generate `KEYWORD-RESEARCH-{topic}.md`:

```markdown
# Keyword Research Report: [Topic]

## Executive Summary
- Total keywords analyzed: XX
- High opportunity keywords: XX
- Quick win keywords: XX

## Keyword Clusters

### Cluster 1: [Name]
| Keyword | Volume | KD | Intent | Priority |
|---------|--------|-----|--------|----------|
| keyword | 1K-10K | 35 | Informational | High |

## Quick Win Opportunities
1. [Low difficulty, decent volume keywords]

## Content Gaps
- Keywords competitors rank for that you don't

## Recommended Content Plan
| Week | Target Keywords | Content Type |
|------|----------------|--------------|
| 1 | keyword1, keyword2 | Blog post |
```

## Error Handling

| Scenario | Action |
|----------|--------|
| No search volume data | Note limitation, use proxy metrics (CPC, competition) |
| Very high difficulty | Recommend building authority first, target easier variations |
| No results for seed | Suggest broader terms or different angles |

## Related Skills

- `seo-content` - Content optimization for keywords
- `seo-competitor` - Competitor keyword gap analysis
- `seo-technical` - Technical SEO foundation
