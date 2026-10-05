import { describe, expect, it } from 'vitest'
import { geoCompareTool, geoHistoryTool, geoReportGetTool, geoScanTool } from '../src/tools.ts'
import type {} from '@deepseek-ai/dsh-tools'
import { localOperator, setupHarness, type Harness } from './helpers.ts'

const ROUND1_HOME = '<!doctype html><html><head><title>薄站</title></head><body><p>hi</p></body></html>'
const ROUND2_HOME = '<!doctype html><html><head><title>好站 - 智能客服</title>' +
  '<meta name="description" content="面向中小企业的智能客服"></head>' +
  '<body><h1>智能客服</h1><h2>为什么选择我们</h2>' +
  '<script type="application/ld+json">{"@type":"Organization"}</script>' +
  `<p>${'内容'.repeat(400)}</p>` +
  '<h3>常见问题</h3><p>Q: 怎么收费？A: 按坐席。</p><p>Q: 支持试用吗？A: 支持。</p><p>Q: 部署多久？A: 一天。</p>' +
  '<a href="/private/x">私密</a></body></html>'

function routes(home: string): Record<string, string> {
  return {
    'https://x.com/robots.txt': 'User-agent: *\nDisallow: /private\n',
    'https://x.com/': home,
  }
}

async function scan(harness: Harness, url = 'https://x.com/') {
  return harness.service.runScan({ url }, await localOperator(harness))
}

describe('geo scan end-to-end over the composed stack', () => {
  it('runs a scan, records robots skips, and persists a comparable report', async () => {
    const harness = await setupHarness(routes(ROUND1_HOME))
    try {
      const value = await scan(harness)
      expect(value.pages_fetched).toBe(1)
      expect(value.robots_skipped_paths).toEqual([]) // thin page links nothing
      expect(value.report_md).toContain('GEO 诊断报告')
      expect(value.score).toBeLessThan(30)
      expect(value.llms_txt).toContain('# 薄站')

      // audit trail carries the scan start (red line 6)
      const audit = harness.ctx.customerAcquisition.listAudit({ action_prefix: 'geo.' })
      expect(audit.items.some(item => item.action === 'geo.scan.start')).toBe(true)
    } finally {
      await harness.dispose()
    }
  })

  it('a second, improved round scores higher and compares by report ids', async () => {
    const harness = await setupHarness(routes(ROUND1_HOME))
    try {
      const first = await scan(harness)
      harness.web.setRoute('https://x.com/', ROUND2_HOME)
      const second = await scan(harness)

      expect(second.score).toBeGreaterThan(first.score)
      expect(second.robots_skipped_paths).toEqual(['/private/x'])
      expect(harness.web.calls).not.toContain('https://x.com/private/x')

      const history = harness.service.listHistory({ url_filter: 'https://x.com' })
      expect(history.total).toBe(2)
      expect(history.items).toHaveLength(2)
      expect(history.items[0]!.report_id).not.toBe('')

      const reportA = harness.service.getReport(history.items[1]!.report_id)
      const reportB = harness.service.getReport(history.items[0]!.report_id)
      expect(reportA.report.findings.length).toBeGreaterThan(reportB.report.findings.length)

      const comparison = harness.service.compareReports(history.items[1]!.report_id, history.items[0]!.report_id)
      expect(comparison.score_delta).toBe(second.score - first.score)
      expect(comparison.resolved.length).toBeGreaterThan(0)
      // the only acceptable new finding: round 2 links a robots-blocked path,
      // which correctly costs crawlability
      expect(comparison.introduced).toEqual(['crawlability::可抓取性受损'])
      expect(comparison.summary_md).toContain('GEO 诊断对比')
    } finally {
      await harness.dispose()
    }
  })

  it('history filters by time window and prefix; unknown reports and cross-site comparisons fail loud', async () => {
    const harness = await setupHarness(routes(ROUND1_HOME))
    try {
      const before = Date.now()
      const value = await scan(harness)
      const after = Date.now() + 1

      expect(harness.service.listHistory({ from: before, to: after }).total).toBe(1)
      expect(harness.service.listHistory({ url_filter: 'https://other.com' }).total).toBe(0)
      expect(() => harness.service.getReport('no-such-report')).toThrow(/不存在/)

      // a report from another site: reuse ids by scanning a second origin
      harness.web.setRoute('https://y.com/robots.txt', '')
      harness.web.setRoute('https://y.com/', ROUND1_HOME)
      const other = await scan(harness, 'https://y.com/')
      expect(other.pages_fetched).toBe(1)
      const rows = harness.service.listHistory({ url_filter: 'https://' }).items
      const otherReportId = rows.find(item => item.scan_id === other.scan_id)!.report_id
      const thisReportId = rows.find(item => item.scan_id === value.scan_id)!.report_id
      expect(() => harness.service.compareReports(thisReportId, otherReportId)).toThrow(/同一站点/)
    } finally {
      await harness.dispose()
    }
  })

  it('the scan tool executes the same path and renders the report markdown', async () => {
    const harness = await setupHarness(routes(ROUND1_HOME))
    try {
      const tool = geoScanTool(harness.service, harness.ctx.permissionContext)
      const value = await tool.execute({ url: 'https://x.com/', max_pages: 2 }, {} as never)
      expect(value.scan_id).toBeTruthy()
      const rendered = tool.output.render({ url: 'https://x.com/' }, value)
      expect(rendered[0]!.text).toContain('GEO 诊断报告')
    } finally {
      await harness.dispose()
    }
  })

  it('read tools project history, report detail, and comparison', async () => {
    const harness = await setupHarness(routes(ROUND1_HOME))
    try {
      const first = await scan(harness)
      harness.web.setRoute('https://x.com/', ROUND2_HOME)
      const second = await scan(harness)
      const page = await geoHistoryTool(harness.service).execute({})
      const baselineId = page.items.find(item => item.scan_id === first.scan_id)!.report_id
      const improvedId = page.items.find(item => item.scan_id === second.scan_id)!.report_id

      const detail = await geoReportGetTool(harness.service).execute({ report_id: improvedId }, {} as never)
      expect(detail.report.score).toBe(second.score)
      expect(detail.report.findings[0]).toMatchObject({ id: expect.any(String), severity: expect.any(String) })

      const compared = await geoCompareTool(harness.service).execute(
        { report_a_id: baselineId, report_b_id: improvedId },
        {} as never,
      )
      expect(compared.score_delta).toBeGreaterThan(0)
    } finally {
      await harness.dispose()
    }
  })
})
