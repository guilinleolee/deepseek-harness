/**
 * The GEO diagnosis service: runs bounded serial scans through the web
 * capability, analyzes them deterministically, and persists scans and
 * reports into the customer-acquisition storage domain the main plugin owns.
 * It never opens the domain itself (single-open per name); it resolves the
 * already-open handle through the storage-domain facility and does not own
 * its lifetime.
 * @module @deepseek-ai/dsh-customer-acquisition-geo/service
 */

import { Service } from '@deepseek-ai/cordis'
import type { Context } from '@deepseek-ai/cordis'
import type { Domain } from '@deepseek-ai/dsh-storage-domain'
import {
  GEO_MAX_PAGES_HARD_LIMIT,
  GEO_PAGE_TIMEOUT_MS_HARD_LIMIT,
  GEO_RESPONSE_MAX_BYTES,
  appendAuditRecord,
  customerAcquisitionDomainSpec,
  newId,
  type GeoReport,
  type GeoReportId,
  type GeoScan,
  type ResolvedOperator,
} from './main-package.ts'
import { analyzeSite } from './analyze.ts'
import { crawlSite } from './fetcher.ts'
import type {
  GeoCompareValue, GeoHistoryItem, GeoHistoryRequest, GeoReportValue,
  GeoScanValue,
} from './types.ts'

/** Input of one scan run; every value here passed the boundary gate already. */
export interface ScanInput {
  readonly url: string
  readonly maxPages?: number
}

/** The already-open customer-acquisition domain, typed by its frozen spec. */
type AcquisitionDomain = Domain<typeof customerAcquisitionDomainSpec>

/**
 * Storage-backed GEO diagnosis service. The domain comes from the main
 * plugin's service; the web capability performs every fetch.
 */
export class GeoDiagnosisService extends Service {
  static inject = ['storageDomain', 'customerAcquisition', 'web'] as const

  private domain: AcquisitionDomain | undefined

  /**
   * @param ctx - Host context providing storage, the main service, and the web capability.
   */
  constructor(ctx: Context) {
    super(ctx, 'geoDiagnosis')
  }

  /** Resolve the domain the main plugin opened; never opened or closed here. */
  protected async [Service.init](): Promise<void> {
    const open = this.ctx.storageDomain.get(customerAcquisitionDomainSpec.name)
    if (open === undefined) {
      throw new Error('customer-acquisition-geo: the customer_acquisition domain is not open; the customer-acquisition plugin must load first')
    }
    this.domain = open as unknown as AcquisitionDomain
  }

  /** Authoritative domain handle, valid after init; a miss is a broken lifecycle. */
  private requireDomain(): AcquisitionDomain {
    if (this.domain === undefined) {
      throw new Error('customer-acquisition-geo: domain handle is not initialized')
    }
    return this.domain
  }

  /**
   * Run one bounded serial scan: record the running scan, crawl the seed's
   * origin, analyze, persist the report, and close the scan. Fetch failures
   * on individual pages degrade the report; a total failure marks the scan
   * `failed` and rethrows friendly.
   * @param input - the gated scan input (URL, optional page cap).
   * @param operator - the caller's resolved operator, for the audit write.
   * @returns the canonical scan value.
   */
  async runScan(input: ScanInput, operator: ResolvedOperator): Promise<GeoScanValue> {
    const domain = this.requireDomain()
    const settings = domain.global.get()
    const scanId = newId<'GeoScanId'>()
    const maxPages = Math.min(input.maxPages ?? settings.geo_max_pages, GEO_MAX_PAGES_HARD_LIMIT)
    const timeoutMs = Math.min(settings.geo_page_timeout_ms, GEO_PAGE_TIMEOUT_MS_HARD_LIMIT)
    const scanTable = domain.table('geo_scans')
    const reportTable = domain.table('geo_reports')

    await scanTable.put(scanId, {
      id: scanId,
      url: input.url,
      status: 'running',
      started_at: Date.now(),
    })
    await appendAuditRecord(domain.table('audit_logs'), {
      action: 'geo.scan.start',
      object_type: 'geo_scan',
      object_id: scanId,
      summary: `开始 GEO 诊断：${input.url}（页数上限 ${maxPages}）`,
    }, operator, 'agent')

    try {
      const crawl = await crawlSite(
        (url, signal) => this.ctx.web.fetch({ url }, signal),
        input.url,
        { maxPages, timeoutMs, maxBytes: GEO_RESPONSE_MAX_BYTES },
      )
      const analysis = analyzeSite(input.url, crawl)
      const scan = scanTable.get(scanId)
      if (scan === undefined) throw new Error(`GEO 扫描不存在：${scanId}`)
      const finishedScan: GeoScan = { ...scan, status: 'done', finished_at: Date.now() }
      await scanTable.put(scanId, finishedScan)
      const reportId = newId<'GeoReportId'>()
      const report: GeoReport = {
        id: reportId,
        scan_id: scanId,
        score: analysis.score,
        findings: analysis.findings.map((finding, index) => ({ id: `f${index + 1}`, ...finding })),
        llms_txt: analysis.llmsTxt,
        artifacts: {
          faq_material: analysis.faqMaterial,
          brand_kit: analysis.brandKit,
          tasks: [...analysis.tasks],
        },
        report_md: renderReportMd(
          input.url, analysis.score, analysis.findings, crawl.robotsSkippedPaths, analysis.tasks, crawl.pages.length),
        pages_fetched: crawl.pages.length,
        robots_skipped_paths: [...crawl.robotsSkippedPaths],
        created_at: Date.now(),
      }
      await reportTable.put(reportId, report)
      return {
        scan_id: scanId,
        score: report.score,
        findings_count: report.findings.length,
        pages_fetched: report.pages_fetched,
        robots_skipped_paths: report.robots_skipped_paths,
        llms_txt: report.llms_txt ?? '',
        report_md: report.report_md,
      }
    } catch (error) {
      const scan = scanTable.get(scanId)
      if (scan === undefined) throw new Error(`GEO 扫描不存在：${scanId}`)
      await scanTable.put(scanId, { ...scan, status: 'failed', finished_at: Date.now(), error: String(error) })
      throw error instanceof Error ? error : new Error(`GEO 诊断失败：${String(error)}`)
    }
  }

  /**
   * List scans joined with their reports, newest first, optionally filtered
   * by URL prefix and time window.
   * @param request - filters plus paging bounds.
   * @returns the matching page with the unfiltered total.
   */
  listHistory(request: GeoHistoryRequest): { items: GeoHistoryItem[]; total: number } {
    const domain = this.requireDomain()
    const reportTable = domain.table('geo_reports')
    const rows: GeoHistoryItem[] = []
    for (const [scanId, scan] of domain.table('geo_scans').entries()) {
      const report = [...reportTable.entries()].find(([, candidate]) => candidate.scan_id === scanId)?.[1]
      if (request.url_filter !== undefined && !scan.url.startsWith(request.url_filter)) continue
      if (request.from !== undefined && scan.started_at < request.from) continue
      if (request.to !== undefined && scan.started_at > request.to) continue
      rows.push({
        scan_id: scanId,
        report_id: report?.id ?? '',
        url: scan.url,
        status: scan.status,
        score: report?.score ?? 0,
        pages_fetched: report?.pages_fetched ?? 0,
        started_at: scan.started_at,
      })
    }
    rows.sort((left, right) => right.started_at - left.started_at)
    const offset = request.offset ?? 0
    const limit = request.limit ?? 20
    return { items: rows.slice(offset, offset + limit), total: rows.length }
  }

  /**
   * Read one full report with its scan's URL.
   * @param reportId - the report id.
   * @returns the projected report.
   */
  getReport(reportId: string): GeoReportValue {
    const domain = this.requireDomain()
    const report = domain.table('geo_reports').get(reportId as GeoReportId)
    if (report === undefined) {
      throw new Error(`GEO 报告不存在：${reportId}`)
    }
    const scan = domain.table('geo_scans').get(report.scan_id)
    return {
      report: {
        id: report.id,
        scan_id: report.scan_id,
        url: scan?.url ?? '',
        score: report.score,
        findings: report.findings.map(finding => ({
          id: finding.id,
          category: finding.category,
          severity: finding.severity,
          title: finding.title,
          detail: finding.detail,
          ...(finding.evidence_page === undefined ? {} : { evidence_page: finding.evidence_page }),
        })),
        llms_txt: report.llms_txt ?? '',
        report_md: report.report_md,
        robots_skipped_paths: report.robots_skipped_paths,
        created_at: report.created_at,
      },
    }
  }

  /**
   * Compare two reports of the same site: score movement, resolved and newly
   * introduced shortcomings, and a Markdown summary.
   * @param reportAId - the baseline report id.
   * @param reportBId - the comparison report id.
   * @returns the comparison value.
   */
  compareReports(reportAId: string, reportBId: string): GeoCompareValue {
    const domain = this.requireDomain()
    const scanTable = domain.table('geo_scans')
    const reportTable = domain.table('geo_reports')
    const reportA = reportTable.get(reportAId as GeoReportId)
    const reportB = reportTable.get(reportBId as GeoReportId)
    if (reportA === undefined) throw new Error(`GEO 报告不存在：${reportAId}`)
    if (reportB === undefined) throw new Error(`GEO 报告不存在：${reportBId}`)
    const originA = new URL(scanTable.get(reportA.scan_id)?.url ?? '').origin
    const originB = new URL(scanTable.get(reportB.scan_id)?.url ?? '').origin
    if (originA !== originB) {
      throw new Error(`两份报告须来自同一站点：${originA} 与 ${originB} 不一致`)
    }
    const keyOf = (finding: GeoReport['findings'][number]) => `${finding.category}::${finding.title}`
    const keysA = new Set(reportA.findings.map(keyOf))
    const keysB = new Set(reportB.findings.map(keyOf))
    const resolved = [...keysA].filter(key => !keysB.has(key))
    const introduced = [...keysB].filter(key => !keysA.has(key))
    const delta = reportB.score - reportA.score
    const summary = [
      `# GEO 诊断对比：${originB}`,
      '',
      `- 综合分：${reportA.score} → ${reportB.score}（${delta >= 0 ? '+' : ''}${delta}）`,
      `- 已解决短板：${resolved.length} 项${resolved.length > 0 ? `\n${resolved.map(key => `  - ✅ ${key.split('::')[1]}`).join('\n')}` : ''}`,
      `- 新增短板：${introduced.length} 项${introduced.length > 0 ? `\n${introduced.map(key => `  - ⚠️ ${key.split('::')[1]}`).join('\n')}` : ''}`,
    ].join('\n')
    return {
      score_a: reportA.score,
      score_b: reportB.score,
      score_delta: delta,
      resolved,
      introduced,
      summary_md: summary,
    }
  }
}

/**
 * Render the durable Markdown report for one scan. Pure function of the
 * analysis so the persisted `report_md` replays identically.
 * @param url - the diagnosed seed URL.
 * @param score - the overall score.
 * @param findings - the diagnosis findings.
 * @param robotsSkipped - paths skipped by robots.txt.
 * @param tasks - the ordered optimization task list.
 * @param pagesFetched - how many pages the crawl retrieved.
 * @returns the Markdown report.
 */
export function renderReportMd(
  url: string,
  score: number,
  findings: readonly { severity: string; title: string; detail: string }[],
  robotsSkipped: readonly string[],
  tasks: readonly string[],
  pagesFetched: number,
): string {
  const lines = [
    `# GEO 诊断报告：${url}`,
    '',
    `- 综合分：**${score}/100**`,
    `- 抓取页数：${pagesFetched}`,
    `- robots.txt 跳过路径：${robotsSkipped.length === 0 ? '无' : robotsSkipped.join('、')}`,
    '',
    '## 短板发现',
    '',
    ...(findings.length === 0
      ? ['未发现明显短板。']
      : findings.map(finding => `- **[${finding.severity.toUpperCase()}] ${finding.title}**：${finding.detail}`)),
    '',
    '## 优化任务清单',
    '',
    ...(tasks.length === 0 ? ['暂无。'] : tasks.map(task => `- ${task}`)),
  ]
  return lines.join('\n')
}

export default GeoDiagnosisService
