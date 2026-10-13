---
license: UNKNOWN
name: seo-monitor
description: >
  SEO monitoring and reporting. Covers rank tracking, technical issue
  monitoring, competitor tracking, traffic analysis, and scheduled
  reporting. Use when user says "SEO monitoring", "rank tracking",
  "SEO reports", "ranking reports", or "automated SEO".
user-invokable: true
argument-hint: "[domain] and [monitoring scope]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - WebFetch
  - WebSearch
triggers:
  - "seo monitor"
  - "rank tracking"
  - "SEO监控"
  - "排名追踪"
  - "SEO报告"
---

# SEO Monitoring

## Overview

Continuous SEO monitoring ensures you catch issues early and track progress. This skill provides structured monitoring and reporting workflows.

## Monitoring Framework

### 1. Rank Tracking

| Metric | Frequency | Tools |
|--------|-----------|-------|
| **Position Tracking** | Weekly | DataForSEO, Ahrefs, SEMrush |
| **SERP Features** | Weekly | Manual, tools |
| **Local Rankings** | Weekly | Google Maps, local tools |
| **Brand Mentions** | Daily | Alerts |

### 2. Technical Monitoring

| Check | Frequency | Alert Threshold |
|-------|-----------|-----------------|
| **Crawl Errors** | Weekly | >1 new error |
| **Index Coverage** | Weekly | Any drop |
| **Core Web Vitals** | Monthly | LCP >2.5s, INP >200ms, CLS >0.1 |
| **HTTPS Status** | Daily | Any issue |
| **XML Sitemap** | Weekly | Missing pages, errors |

### 3. Traffic Monitoring

| Metric | Frequency | Tools |
|--------|-----------|-------|
| **Organic Traffic** | Weekly | Google Analytics 4 |
| **Landing Pages** | Weekly | GA4 |
| **Conversions** | Weekly | GA4 |
| **Bounce Rate** | Weekly | GA4 |

### 4. Competitor Monitoring

| Check | Frequency | What to Watch |
|-------|-----------|---------------|
| **Ranking Changes** | Weekly | Keywords they outrank you on |
| **New Content** | Weekly | Content gaps |
| **Backlink Changes** | Monthly | New links they acquire |
| **SERP Feature Ownership** | Weekly | Featured snippets, etc. |

## Monitoring Workflow

### Weekly Review
```
1. Check rank tracking report
2. Review Google Search Console data
3. Note any technical issues
4. Check competitor position changes
5. Document findings in report
```

### Monthly Analysis
```
1. Comprehensive rank analysis
2. Traffic trend analysis
3. Content performance review
4. Link profile changes
5. Competitor comparison
6. Update strategy based on findings
```

### Quarterly Strategy Review
```
1. Goal progress assessment
2. Strategy effectiveness evaluation
3. Competitive landscape update
4. Budget allocation review
5. Strategy adjustments
```

## Alert Thresholds

| Issue | Severity | Response Time |
|-------|----------|---------------|
| **Site down** | Critical | Immediate |
| **Large traffic drop (>20%)** | Critical | Within 4 hours |
| **Index coverage drop** | High | Within 24 hours |
| **Manual action notification** | Critical | Immediate |
| **Rank drop >10 positions** | Medium | Within 48 hours |
| **New competitor ranking well** | Medium | Within 1 week |

## Report Templates

### Weekly SEO Report
Generate `WEEKLY-SEO-REPORT-{date}.md`:

```markdown
# Weekly SEO Report: [Date Range]

## Executive Summary
- Overall traffic: [+/-% vs last week]
- Keywords in top 10: [count]
- Technical issues: [count]

## Rankings Overview
| Keyword | Current | Last Week | Change |
|---------|---------|-----------|--------|
| keyword | 5 | 6 | +1 |

## Traffic Data
| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Sessions | 10,000 | 9,500 | +5.3% |
| Users | 8,000 | 7,600 | +5.3% |

## Technical Issues
- [ ] Issue 1: [status]
- [ ] Issue 2: [status]

## This Week's Actions
1. [Action taken]

## Next Week's Plan
1. [Planned action]
```

### Monthly SEO Report
Generate `MONTHLY-SEO-REPORT-{month}.md`:

```markdown
# Monthly SEO Report: [Month Year]

## Performance Summary
| Metric | This Month | Last Month | YoY | Trend |
|--------|------------|------------|-----|-------|
| Organic Traffic | XX | XX | XX% | [icon] |
| Conversions | XX | XX | XX% | [icon] |
| Keywords Top 10 | XX | XX | XX | [icon] |

## Wins This Month
1. [Achievement]

## Issues Resolved
1. [Issue fixed]

## Key Insights
- [Insight 1]
- [Insight 2]

## Recommendations
1. [Recommendation]

## Budget vs Actual (if applicable)
| Category | Budget | Spent | Variance |
|----------|--------|-------|----------|
```

## Data Sources

### Monitoring Tools
- **DataForSEO API** (via MCP): Rank tracking, SERP features
- **Google Search Console**: Performance data, coverage
- **Google Analytics 4**: Traffic, conversions
- **Third-party tools**: Ahrefs, SEMrush, Moz

### Alert Systems
- Google Search Console notifications
- Custom API monitoring
- Third-party rank tracking alerts

## Error Handling

| Scenario | Action |
|----------|--------|
| Data discrepancy between tools | Note the difference, explain likely cause |
| Missing data (new property) | Start fresh tracking, note limitation |
| Algorithm update detected | Analyze impact, adjust strategy |

## Related Skills

- `seo-technical` - Technical issue resolution
- `seo-keyword` - Ranking strategy
- `seo-competitor` - Competitive monitoring
- `seo-content` - Content performance optimization
