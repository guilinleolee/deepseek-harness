---
license: UNKNOWN
name: seo-competitor
description: >
  Competitor SEO analysis and gap identification. Covers keyword gap analysis,
  content gap analysis, backlink gap analysis, SERP feature tracking, and
  competitive positioning. Use when user says "competitor analysis",
  "competitive analysis", "SEO gap", "keyword gap", or "content gap".
user-invokable: true
argument-hint: "[your domain] and [competitor domains]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - WebFetch
  - WebSearch
triggers:
  - "seo competitor"
  - "competitor analysis"
  - "竞品分析"
  - "关键词差距"
---

# SEO Competitor Analysis

## Overview

Competitive analysis helps identify opportunities by understanding what competitors rank for and where gaps exist.

## Competitor Analysis Framework

### 1. Competitor Identification

| Type | Description | How to Find |
|------|-------------|-------------|
| **Direct** | Sell same products/services | Same keywords in SERPs |
| **Indirect** | Solve same problems | Different product, same audience |
| **Substitute** | Alternative solutions | Different category, same need |

### 2. Keyword Gap Analysis

Compare keywords you rank for vs competitors:

| Category | Definition | Action |
|----------|------------|--------|
| **Unique to You** | Keywords only you rank for | Protect and expand |
| **Shared** | Both you and competitor rank | Improve positions |
| **Competitor Only** | Keywords competitor ranks for, you don't | High opportunity |

### 3. Content Gap Analysis

| Gap Type | Description | Priority |
|----------|-------------|----------|
| **Topic Gaps** | Entire subjects they cover that you don't | High |
| **Depth Gaps** | More comprehensive content on shared topics | Medium |
| **Format Gaps** | Content formats (videos, tools, calculators) | Medium |

### 4. Backlink Gap Analysis

| Metric | What to Analyze |
|--------|-----------------|
| **Referring Domains** | Unique sites linking to competitor but not you |
| **Domain Authority** | Average DA of competitor's link sources |
| **Link Types** | Guest posts, editorials, resource pages, broken link building |
| **Anchor Text** | Keywords used in links |

### 5. SERP Feature Analysis

| Feature | Opportunity |
|---------|-------------|
| **Featured Snippet** | Optimize for position 0 |
| **People Also Ask** | FAQ content opportunities |
| **Local Pack** | For local businesses |
| **Video Results** | Video content opportunities |
| **Image Pack** | Image optimization opportunities |

## Analysis Workflow

### Step 1: Identify Competitors
```
1. Search main keywords in Google
2. Note top 5-10 non-branded results
3. Use tools: Ahrefs "Competing Domains", SEMrush "Competitors"
```

### Step 2: Keyword Gap Analysis
```
1. List your top 50 keywords
2. Compare with each competitor
3. Identify shared and unique keywords
4. Note keyword difficulty and volume
```

### Step 3: Content Audit
```
1. Analyze competitor's top content
2. Note content length, structure, format
3. Identify topics they cover that you don't
4. Assess E-E-A-T signals on their pages
```

### Step 4: Backlink Analysis
```
1. Identify competitor's top backlinks
2. Note link types and sources
3. Identify link opportunities
4. Prioritize by domain authority
```

## Data Sources

### Free
- Google Search (manual SERP analysis)
- Google Trends (trend comparison)
- Ubersuggest (limited free tier)

### Paid (via MCP)
- **DataForSEO**: `domain_analytics_competitors_domain_competitors`, `domain_analytics_organic_organic`
- Ahrefs
- SEMrush

## Output Format

Generate `COMPETITOR-ANALYSIS-{domain}.md`:

```markdown
# SEO Competitor Analysis: [Your Site]

## Competitors Identified
| Competitor | Domain | Threat Level |
|------------|--------|--------------|
| Competitor 1 | example.com | High |

## Keyword Gap Analysis
### Opportunities (Competitor Only)
| Keyword | Volume | KD | Priority |
|---------|--------|-----|----------|
| keyword | 1K-10K | 45 | High |

## Content Gaps
| Gap Type | Topic | Your Status | Recommendation |
|----------|-------|-------------|----------------|
| Topic | [topic] | Missing | Create comprehensive guide |

## Backlink Opportunities
| Source | DA | Link Type | Outreach Difficulty |
|--------|----|-----------|---------------------|
| site.com | 65 | Guest Post | Medium |

## Top Priority Actions
1. [Action with highest impact]
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Competitor data unavailable | Use proxy data, manual SERP analysis |
| Too many competitors | Focus on top 3-5 by keyword overlap |
| No clear gaps | Analyze deeper metrics (SERP features, E-E-A-T) |

## Related Skills

- `seo-keyword` - Identify keyword opportunities
- `seo-content` - Content gap filling
- `seo-link-building` - Backlink opportunity implementation
- `seo-technical` - Technical foundation
