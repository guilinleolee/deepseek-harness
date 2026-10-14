import { describe, expect, it } from 'vitest'
import { analyzeSite } from '../src/analyze.ts'
import type { CrawlResult } from '../src/fetcher.ts'

const GOOD_PAGE = '<!doctype html><html><head><title>示例站 - 智能客服</title>' +
  '<meta name="description" content="面向中小企业的智能客服系统"></head>' +
  '<body><h1>智能客服</h1><h2>为什么选择我们</h2>' +
  '<script type="application/ld+json">{"@type":"Organization"}</script>' +
  `<p>${'内容'.repeat(400)}</p>` +
  '<h3>常见问题</h3><p>Q: 怎么收费？A: 按坐席。</p><p>Q: 支持试用吗？A: 支持。</p><p>Q: 部署多久？A: 一天。</p>' +
  '</body></html>'

const THIN_PAGE = '<!doctype html><html><body><p>hi</p></body></html>'

function crawlOf(pages: { url: string; body: string; status?: number }[], extras: Partial<CrawlResult> = {}): CrawlResult {
  return {
    pages: pages.map(page => ({ url: page.url, statusCode: page.status ?? 200, body: page.body })),
    robotsSkippedPaths: [],
    oversizedUrls: [],
    failures: [],
    robotsFetched: true,
    ...extras,
  }
}

describe('deterministic GEO analysis', () => {
  it('scores a well-formed site far higher than a thin one', () => {
    const good = analyzeSite('https://x.com/', crawlOf([{ url: 'https://x.com/', body: GOOD_PAGE }]))
    const thin = analyzeSite('https://x.com/', crawlOf([{ url: 'https://x.com/', body: THIN_PAGE }]))
    expect(good.score).toBeGreaterThan(70)
    expect(thin.score).toBeLessThan(30)
    expect(good.findings.length).toBeLessThan(thin.findings.length)
  })

  it('produces a deployable llms.txt listing crawled pages and empty when nothing was crawled', () => {
    const good = analyzeSite('https://x.com/', crawlOf([{ url: 'https://x.com/', body: GOOD_PAGE }]))
    expect(good.llmsTxt).toContain('# 示例站 - 智能客服')
    expect(good.llmsTxt).toContain('https://x.com/')
    const empty = analyzeSite('https://x.com/', crawlOf([]))
    expect(empty.llmsTxt).toBe('')
  })

  it('marks llms_txt absent as a high-severity finding with the site origin in the detail', () => {
    const thin = analyzeSite('https://x.com/', crawlOf([{ url: 'https://x.com/', body: THIN_PAGE }]))
    const llms = thin.findings.find(finding => finding.category === 'llms_txt')
    expect(llms?.severity).toBe('high')
    expect(llms?.detail).toContain('https://x.com/llms.txt')
  })

  it('a served llms.txt clears the finding; a non-200 llms.txt does not', () => {
    const served = analyzeSite('https://x.com/', crawlOf([
      { url: 'https://x.com/', body: GOOD_PAGE },
      { url: 'https://x.com/llms.txt', body: '# 示例站\n- [首页](https://x.com/)' },
    ]))
    expect(served.findings.find(finding => finding.category === 'llms_txt')).toBeUndefined()

    const errored = analyzeSite('https://x.com/', crawlOf([
      { url: 'https://x.com/', body: GOOD_PAGE },
      { url: 'https://x.com/llms.txt', body: 'internal error', status: 503 },
    ]))
    expect(errored.findings.find(finding => finding.category === 'llms_txt')).toBeDefined()
  })

  it('names a page that has h1 but no h2 as the headings-evidence page', () => {
    const partial = analyzeSite('https://x.com/', crawlOf([
      { url: 'https://x.com/', body: GOOD_PAGE },
      { url: 'https://x.com/h1only', body: '<!doctype html><html><head><title>t</title></head><body><h1>只有一级</h1><p>正文</p></body></html>' },
    ]))
    const headings = partial.findings.find(finding => finding.category === 'headings')
    expect(headings).toBeDefined()
    expect(headings?.evidence_page).toBe('https://x.com/h1only')
  })

  it('harvests question lines into the FAQ draft, capped at ten', () => {
    const questions = Array.from({ length: 12 }, (_, index) => `<p>第${index}个常见问题怎么解决？</p>`).join('')
    const rich = analyzeSite('https://x.com/', crawlOf([
      { url: 'https://x.com/', body: `<!doctype html><html><body>${questions}</body></html>` },
    ]))
    expect(rich.faqMaterial).toContain('- 第0个常见问题怎么解决？')
    expect(rich.faqMaterial).toContain('- 第9个常见问题怎么解决？')
    expect(rich.faqMaterial).not.toContain('第10个')
    expect(rich.faqMaterial).not.toContain('起步问题')
  })

  it('is pure: identical crawls analyze identically (two-round comparability)', () => {
    const crawl = crawlOf([{ url: 'https://x.com/', body: GOOD_PAGE }])
    expect(analyzeSite('https://x.com/', crawl)).toEqual(analyzeSite('https://x.com/', crawlOf([{ url: 'https://x.com/', body: GOOD_PAGE }])))
  })

  it('orders tasks by severity and always yields artifacts', () => {
    const thin = analyzeSite('https://x.com/', crawlOf([{ url: 'https://x.com/', body: THIN_PAGE }]))
    expect(thin.tasks.length).toBe(thin.findings.length)
    expect(thin.tasks[0]).toMatch(/^\[HIGH\]/)
    expect(thin.faqMaterial).toContain('FAQ 素材草案')
    expect(thin.brandKit).toContain('https://x.com')
  })
})
