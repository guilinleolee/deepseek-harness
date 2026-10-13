---
license: UNKNOWN
name: seo-link-building
description: >
  Link building strategy and execution. Covers backlink analysis, link
  opportunity identification, domain authority assessment, outreach template
  generation, and link quality evaluation. Use when user says "link building",
  "backlinks", "backlink analysis", "outreach", or "external links".
user-invokable: true
argument-hint: "[target domain or topic]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - WebFetch
  - WebSearch
triggers:
  - "seo link building"
  - "backlink"
  - "外链建设"
  - "link outreach"
---

# SEO Link Building

## Overview

Link building remains a crucial ranking factor. This skill helps identify opportunities, assess link quality, and generate outreach content.

## Link Building Framework

### 1. Link Quality Assessment

| Metric | What It Means | Target |
|--------|---------------|--------|
| **Domain Authority (DA)** | Overall site authority | 30+ for link sources |
| **Domain Rating (DR)** | Ahrefs metric | 25+ |
| **Trust Flow** | Majestic metric | 15+ |
| **Citation Flow** | Majestic metric | Match or exceed Trust Flow |

### 2. Link Type Classification

| Type | Quality | Effort | Best For |
|------|---------|--------|----------|
| **Editorial** | High | High | Authority building |
| **Guest Post** | Medium-High | Medium | Scalable growth |
| **Resource Page** | Medium | Low-Medium | Niche links |
| **Broken Link Building** | Medium-High | Medium | Quick wins |
| **HARO/Connectively** | High | Low | Expert positioning |
| **Testimonial** | Medium | Low | Easy links |
| **Social Links** | Low | None | Not for SEO |

### 3. Link Opportunity Identification

| Method | Description | Success Rate |
|--------|-------------|--------------|
| **Competitor Backlinks** | Find where competitors get links | Medium |
| **Resource Pages** | "Best [topic]" roundups | High |
| **Guest Post Outreach** | Pitch relevant content ideas | Low-Medium |
| **Broken Link Building** | Find 404s, suggest your content | Medium-High |
| **Skyscraper Technique** | Create better content, request links | Medium |
| **Digital PR** | Newsworthy content, journalist outreach | High |

### 4. Outreach Template Generation

#### Guest Post Pitch Template
```
Subject: Guest Post Pitch - [Unique Angle]

Hi [Name],

I noticed [site] publishes content about [topic]. I've been working in this space for [X years] and have published on [publication 1], [publication 2].

I'd like to contribute a guest post on: [Specific Title]

Here's a quick outline:
- [Point 1]
- [Point 2]
- [Point 3]

Would you be open to a guest post from me?

Best,
[Your Name]
```

#### Broken Link Building Template
```
Subject: Found a Broken Link on [Page]

Hi [Name],

I was reading your [page title] and noticed a broken link to [broken URL].

The page this links to seems to be down. I actually have a similar resource on [your URL] that might be a good replacement.

Would you consider updating the link?

Best,
[Your Name]
```

## Link Building Workflow

### Step 1: Backlink Audit
```
1. Analyze existing backlink profile
2. Identify link types and sources
3. Note any toxic links
4. Assess anchor text distribution
```

### Step 2: Opportunity Research
```
1. Find competitor backlinks
2. Identify resource pages in niche
3. Note relevant directories
4. Research journalist platforms
```

### Step 3: Outreach Execution
```
1. Prioritize opportunities by quality
2. Personalize each outreach email
3. Track outreach in CRM
4. Follow up once (after 5-7 days)
```

### Step 4: Monitoring
```
1. Track new links acquired
2. Monitor lost links
3. Assess impact on rankings
4. Adjust strategy based on results
```

## Data Sources

### Free
- Google Search (resource pages, roundups)
- Twitter/X (journalist queries)
- LinkedIn (expert positioning)

### Paid (via MCP)
- **DataForSEO**: domain_analytics_backlinks内的all backlinks, backlinks_analysis_live
- Ahrefs
- Moz Link Explorer

## Output Format

Generate `LINK-BUILDING-{domain}.md`:

```markdown
# Link Building Strategy: [Domain]

## Current Backlink Profile
- Total Backlinks: XX
- Unique Domains: XX
- Average DA: XX

## Opportunity Pipeline
### High Priority
| Source | DA | Type | URL | Status |
|--------|----|------|-----|--------|
| site.com | 55 | Guest Post | URL | Pending |

### Medium Priority
| Source | DA | Type | URL | Status |
|--------|----|------|-----|--------|
| site2.com | 40 | Resource | URL | Pending |

## Outreach Tracker
| Target | Contact | Email Sent | Response | Link Acquired |
|--------|---------|------------|----------|---------------|
| site.com | Name | 2024-01-01 | Yes | 2024-01-08 |

## Quick Wins Identified
1. [Easy link opportunity]

## Monthly Goals
- Guest posts: 2
- Resource page links: 3
- Digital PR mentions: 1
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Outreach not getting responses | Improve personalization, try different approach |
| Competitor links unattainable | Target similar sites, not exact same |
| Low quality link opportunities | Focus on content-led link earning |

## Related Skills

- `seo-competitor` - Find competitor link sources
- `seo-content` - Create linkable assets
- `seo-keyword` - Identify keyword-relevant link opportunities
