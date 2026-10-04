/**
 * Deterministic GEO analysis: reduces one crawl into a 0-100 score, a
 * findings list, a deployable `llms.txt`, FAQ/brand material, and an
 * optimization task list. Pure functions of the crawl — no model calls, no
 * clocks — so two crawls of the same content compare exactly.
 * @module @deepseek-ai/dsh-customer-acquisition-geo/analyze
 */

import type { CrawlResult, FetchedPage } from './fetcher.ts'

/** One scored dimension of the GEO diagnosis. */
export interface FindingSeed {
  readonly category: string
  readonly severity: 'high' | 'mid' | 'low'
  readonly title: string
  readonly detail: string
  readonly evidence_page?: string
}

/** The analysis output consumed by the service when persisting a report. */
export interface GeoAnalysis {
  readonly score: number
  readonly findings: readonly FindingSeed[]
  readonly llmsTxt: string
  readonly faqMaterial: string
  readonly brandKit: string
  readonly tasks: readonly string[]
}

/** Per-check weight; the pass ratio of each check contributes weight to the score. */
const CHECKS: Readonly<Record<string, number>> = Object.freeze({
  llms_txt: 15,
  meta_description: 15,
  title: 10,
  headings: 15,
  faq: 15,
  structured_data: 10,
  content_depth: 10,
  crawlability: 10,
})

/**
 * Extract the first regex capture on a page, case-insensitive.
 * @param page - the fetched page.
 * @param regex - the pattern with exactly one capture group.
 * @returns the trimmed capture, or `undefined`.
 */
function firstMatch(page: FetchedPage, regex: RegExp): string | undefined {
  const match = page.body.match(regex)
  return match?.[1]?.trim() || undefined
}

/** Whether the page carries a `<meta name="description">`. */
function hasMetaDescription(page: FetchedPage): boolean {
  return /<meta\b[^>]*name\s*=\s*["']description["'][^>]*>/i.test(page.body)
}

/** Whether the page carries any JSON-LD structured-data block. */
function hasJsonLd(page: FetchedPage): boolean {
  return /<script\b[^>]*type\s*=\s*["']application\/ld\+json["']/i.test(page.body)
}

/** Whether the page reads like an FAQ (Q-marked lines or an explicit section). */
function looksLikeFaq(page: FetchedPage): boolean {
  if (/<(section|h[1-6]|div)\b[^>]*>\s*(faq|常见问题|常见问答)/i.test(page.body)) return true
  const questions = page.body.match(/<[^>]+>[^<]{4,80}[?？]/g) ?? []
  return questions.length >= 3
}

/** Visible text length of an HTML page, tags and scripts removed. */
function visibleTextLength(page: FetchedPage): number {
  return page.body
    .replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1>/gi, '')
    .replace(/<[^>]*>/g, '')
    .trim().length
}

/**
 * Analyze one crawl deterministically.
 * @param seedUrl - the user-provided seed URL (the site under diagnosis).
 * @param crawl - the crawl result.
 * @returns score, findings, llms.txt, and material artifacts.
 */
export function analyzeSite(seedUrl: string, crawl: CrawlResult): GeoAnalysis {
  const pages = crawl.pages.filter(page => looksLikeHtml(page))
  const crawled = pages.length
  const pass: Record<string, number> = {}
  const evidence: Record<string, string | undefined> = {}

  const llmsPage = crawl.pages.find(page => new URL(page.url).pathname === '/llms.txt')
  pass.llms_txt = llmsPage !== undefined && llmsPage.statusCode === 200 ? 1 : 0
  evidence.llms_txt = `${new URL(seedUrl).origin}/llms.txt`

  const withMeta = pages.filter(hasMetaDescription)
  pass.meta_description = crawled === 0 ? 0 : withMeta.length / crawled
  evidence.meta_description = withMeta.length < crawled
    ? pages.find(page => !hasMetaDescription(page))?.url
    : undefined

  const withTitle = pages.filter(page => firstMatch(page, /<title[^>]*>([\s\S]*?)<\/title>/i) !== undefined)
  pass.title = crawled === 0 ? 0 : withTitle.length / crawled
  evidence.title = withTitle.length < crawled
    ? pages.find(page => firstMatch(page, /<title[^>]*>([\s\S]*?)<\/title>/i) === undefined)?.url
    : undefined

  const withHeadings = pages.filter(page => /<h1\b/i.test(page.body) && /<h2\b/i.test(page.body))
  pass.headings = crawled === 0 ? 0 : withHeadings.length / crawled
  evidence.headings = withHeadings.length < crawled
    ? pages.find(page => !( /<h1\b/i.test(page.body) && /<h2\b/i.test(page.body)))?.url
    : undefined

  const faqPages = pages.filter(looksLikeFaq)
  pass.faq = crawled === 0 ? 0 : Math.min(1, faqPages.length)
  const firstFaq = faqPages[0]
  evidence.faq = firstFaq !== undefined ? firstFaq.url : pages[0]?.url

  const withJsonLd = pages.filter(hasJsonLd)
  pass.structured_data = crawled === 0 ? 0 : Math.min(1, withJsonLd.length)
  const firstJsonLd = withJsonLd[0]
  evidence.structured_data = firstJsonLd !== undefined ? firstJsonLd.url : pages[0]?.url

  const avgDepth = crawled === 0 ? 0 : pages.reduce((sum, page) => sum + visibleTextLength(page), 0) / crawled
  pass.content_depth = avgDepth >= 600 ? 1 : avgDepth / 600

  const blocked = crawl.robotsSkippedPaths.length + crawl.oversizedUrls.length
  pass.crawlability = blocked === 0 ? 1 : Math.max(0, 1 - blocked / 10)

  let score = 0
  for (const [name, weight] of Object.entries(CHECKS)) {
    score += weight * (pass[name] ?? 0)
  }
  score = Math.round(Math.max(0, Math.min(100, score)))

  const findings: FindingSeed[] = []
  const pushFinding = (name: string, title: string, detail: string) => {
    const ratio = pass[name] ?? 0
    if (ratio >= 1) return
    const weight = CHECKS[name]
    if (weight === undefined) return
    findings.push({
      category: name,
      severity: weight >= 15 ? 'high' : weight >= 10 ? 'mid' : 'low',
      title,
      detail,
      ...(evidence[name] === undefined ? {} : { evidence_page: evidence[name] }),
    })
  }

  const siteOrigin = new URL(seedUrl).origin
  pushFinding('llms_txt', '缺少 llms.txt', `站点根目录未提供 llms.txt（${siteOrigin}/llms.txt）。生成式引擎依赖它了解站点结构与可引用内容，建议部署本报告生成的 llms.txt。`)
  pushFinding('meta_description', 'meta description 覆盖不足', `${crawled - withMeta.length}/${crawled} 个页面缺少 meta description。生成式引擎常以描述文本作为引用摘要，逐页补齐可提高被引用概率。`)
  pushFinding('title', '页面标题覆盖不足', `${crawled - withTitle.length}/${crawled} 个页面缺少 <title>。标题是引擎理解页面主题的第一信号。`)
  pushFinding('headings', '标题层级结构不完整', `${crawled - withHeadings.length}/${crawled} 个页面缺少 h1/h2 层级。清晰的层级帮助引擎切分主题与要点。`)
  pushFinding('faq', '缺少 FAQ/问答式内容', '未检测到 FAQ 式问答内容。问答结构直接对应生成式引擎的提问-回答形态，建议新增 FAQ 页或在关键页内嵌问答段落。')
  pushFinding('structured_data', '缺少结构化数据', '未检测到 JSON-LD 结构化数据。补充 Organization/Product/FAQPage 等 schema 可提升引擎对实体与答案的置信度。')
  pushFinding('content_depth', '正文深度不足', `页面平均可见文本约 ${Math.round(avgDepth)} 字符（建议 ≥600）。过薄的页面难以成为引用来源。`)
  pushFinding('crawlability', '可抓取性受损', `本轮有 ${crawl.robotsSkippedPaths.length} 条路径被 robots.txt Disallow、${crawl.oversizedUrls.length} 个页面超出体积上限被跳过。确认这些限制是否有意为之。`)

  const llmsTxt = buildLlmsTxt(pages, new URL(seedUrl).origin)
  const faqMaterial = buildFaqMaterial(pages)
  const brandKit = buildBrandKit(pages, new URL(seedUrl).origin)
  const tasks = buildTasks(findings)

  return { score, findings, llmsTxt, faqMaterial, brandKit, tasks }
}

/**
 * Whether a page is HTML (heuristic: an opening tag in the first chunk).
 * @param page - the fetched page.
 * @returns true when the body should be treated as HTML.
 */
function looksLikeHtml(page: FetchedPage): boolean {
  return /<html|<!doctype|<body|<div|<p\b/i.test(page.body.slice(0, 2000))
}

/**
 * Build a deployable llms.txt from the crawled pages.
 * @param pages - HTML pages with titles and descriptions.
 * @param origin - the site origin.
 * @returns the llms.txt content, or an empty string when nothing was crawlable.
 */
function buildLlmsTxt(pages: readonly FetchedPage[], origin: string): string {
  const home = pages[0]
  if (home === undefined) return ''
  const siteTitle = firstMatch(home, /<title[^>]*>([\s\S]*?)<\/title>/i) ?? origin
  const lines = [`# ${siteTitle}`, '', '## Pages', '']
  for (const page of pages) {
    const title = firstMatch(page, /<title[^>]*>([\s\S]*?)<\/title>/i) ?? new URL(page.url).pathname
    const description = firstMatch(page, /<meta\b[^>]*name\s*=\s*["']description["'][^>]*content\s*=\s*["']([^"']*)["']/i)
    lines.push(`- [${title}](${page.url})${description === undefined ? '' : `: ${description}`}`)
  }
  lines.push('', '## FAQ', '', '（补充 3-5 条目标客户最常问的问题与直答，引擎会优先引用问答式内容。）')
  return lines.join('\n')
}

/**
 * Build the FAQ draft material from question-like lines found on the site.
 * @param pages - HTML pages.
 * @returns a Markdown draft for the panel.
 */
function buildFaqMaterial(pages: readonly FetchedPage[]): string {
  const questions = new Set<string>()
  for (const page of pages) {
    for (const match of page.body.matchAll(/<[^>]+>([^<>]{6,80}[?？])</g)) {
      if (questions.size >= 10) break
      const question = match[1]
      if (question !== undefined) questions.add(question.trim())
    }
  }
  const lines = ['# FAQ 素材草案', '']
  if (questions.size === 0) {
    lines.push('站点上未发现现成的问答内容，以下为目标客户视角的起步问题，请补充直答：', '', '- 你们解决什么问题？', '- 价格怎么算？', '- 与同类产品相比差异在哪？', '- 怎么开始试用？')
  } else {
    for (const question of questions) lines.push(`- ${question}`)
  }
  return lines.join('\n')
}

/**
 * Build the brand-kit material: site name, description, and page topics.
 * @param pages - HTML pages.
 * @param origin - the site origin.
 * @returns a Markdown brand summary.
 */
function buildBrandKit(pages: readonly FetchedPage[], origin: string): string {
  const home = pages[0]
  if (home === undefined) return `# 品牌素材\n\n- 站点：${origin}\n\n（本轮未能抓取到可分析的页面，无素材。）`
  const name = firstMatch(home, /<title[^>]*>([\s\S]*?)<\/title>/i) ?? origin
  const description = firstMatch(home, /<meta\b[^>]*name\s*=\s*["']description["'][^>]*content\s*=\s*["']([^"']*)["']/i)
  const topics = pages
    .map(page => firstMatch(page, /<h1[^>]*>([\s\S]*?)<\/h1>/i))
    .filter((heading): heading is string => heading !== undefined)
    .slice(0, 8)
  const lines = ['# 品牌素材', '', `- 站点名：${name}`, `- 站点：${origin}`, description === undefined ? '- 站点描述：待补充' : `- 站点描述：${description}`]
  if (topics.length > 0) lines.push('', '## 主题词', '', ...topics.map(topic => `- ${topic}`))
  return lines.join('\n')
}

/**
 * Turn findings into an ordered optimization task list, highest severity first.
 * @param findings - the diagnosis findings.
 * @returns one-line tasks for the report and the artifacts.
 */
function buildTasks(findings: readonly FindingSeed[]): string[] {
  const order = { high: 0, mid: 1, low: 2 } as const
  return [...findings]
    .sort((left, right) => order[left.severity] - order[right.severity])
    .map(finding => `[${finding.severity.toUpperCase()}] ${finding.category}：${finding.title} — ${finding.detail}`)
}
