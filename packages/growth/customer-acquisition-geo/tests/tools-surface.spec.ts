import { describe, expect, it, vi } from 'vitest'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import type { GeoDiagnosisService } from '../src/service.ts'
import type { PermissionContextService } from '../src/main-package.ts'
import {
  geoCompareTool,
  geoHistoryTool,
  geoReportGetTool,
  geoScanTool,
  registerGeoTools,
} from '../src/tools.ts'

const EXEC = { callId: 'c', rootCallId: 'c', name: 'probe', arguments: {}, signal: new AbortController().signal, agent: { id: 'a1' } } as never

const LOCAL_OPERATOR = { userId: 'u', displayName: 'n', capabilities: {} }

function permissionOf(): PermissionContextService {
  return { resolve: async () => LOCAL_OPERATOR } as never
}

/** The scan value the stub service returns; mirrors the frozen wire shape. */
const SCAN_VALUE = {
  scan_id: 'scan-1',
  score: 72,
  findings_count: 3,
  pages_fetched: 2,
  robots_skipped_paths: ['/private'],
  llms_txt: '# 站点',
  report_md: '# GEO 诊断报告\n\n正文',
}

function serviceOf(overrides: Record<string, unknown> = {}): GeoDiagnosisService {
  return {
    runScan: async () => SCAN_VALUE,
    listHistory: () => ({
      items: [{
        scan_id: 'scan-1', report_id: 'rep-1', url: 'https://x.com/', status: 'done',
        score: 72, pages_fetched: 2, started_at: 0,
      }],
      total: 1,
    }),
    getReport: () => ({
      report: {
        id: 'rep-1', scan_id: 'scan-1', url: 'https://x.com/', score: 72,
        findings: [{ id: 'f1', category: 'llms_txt', severity: 'high', title: '缺 llms.txt', detail: '详情' }],
        llms_txt: '# 站点',
        report_md: '# GEO 诊断报告',
        robots_skipped_paths: ['/private'],
        created_at: 0,
      },
    }),
    compareReports: () => ({
      score_a: 72, score_b: 85, score_delta: 13,
      resolved: ['缺 llms.txt'], introduced: [], summary_md: '提升 13 分',
    }),
    ...overrides,
  } as never
}

function renderText(tool: ToolDefinition, value: unknown): string {
  const [block] = tool.output.render({}, value as never)
  return (block as { text: string }).text
}

describe('GEO tools full-surface sweep', () => {
  it('all four call cards are generic with Chinese titles', () => {
    const deps = { service: serviceOf(), permission: permissionOf() }
    const tools = [
      geoScanTool(deps.service, deps.permission),
      geoHistoryTool(deps.service),
      geoReportGetTool(deps.service),
      geoCompareTool(deps.service),
    ]
    for (const tool of tools) {
      const view = tool.presentCall?.(sampleArgs(tool.name))
      expect(view?.card, tool.name).toBe('generic')
      expect((view as { title?: string }).title, tool.name).toBeTruthy()
    }
    expect(geoScanTool(deps.service, deps.permission).timeoutMs).toBe(300_000)
  })

  it('scan renders the report and forwards minimal and maximal inputs', async () => {
    const runScan = vi.fn(async () => SCAN_VALUE)
    const tool = geoScanTool(serviceOf({ runScan }), permissionOf())
    expect(renderText(tool, SCAN_VALUE)).toContain('GEO 诊断报告')

    await tool.execute({ url: 'https://x.com/' }, EXEC)
    expect(runScan).toHaveBeenLastCalledWith({ url: 'https://x.com/' }, LOCAL_OPERATOR)

    await tool.execute({ url: 'https://x.com/', max_pages: 5 }, EXEC)
    expect(runScan).toHaveBeenLastCalledWith({ url: 'https://x.com/', maxPages: 5 }, LOCAL_OPERATOR)
  })

  it('history renders empty and populated pages', () => {
    const tool = geoHistoryTool(serviceOf())
    expect(renderText(tool, { items: [], total: 0 })).toContain('暂无 GEO 诊断记录')
    expect(renderText(tool, {
      items: [{
        scan_id: 'scan-1', report_id: 'rep-1', url: 'https://x.com/', status: 'done',
        score: 72, pages_fetched: 2, started_at: 0,
      }],
      total: 1,
    })).toContain('共 1 条 GEO 诊断记录')
  })

  it('report-get renders the report body', () => {
    const tool = geoReportGetTool(serviceOf())
    expect(renderText(tool, {
      report: {
        id: 'rep-1', scan_id: 'scan-1', url: 'https://x.com/', score: 72,
        findings: [{ id: 'f1', category: 'llms_txt', severity: 'high', title: '缺 llms.txt', detail: '详情' }],
        llms_txt: '# 站点',
        report_md: '# GEO 诊断报告',
        robots_skipped_paths: ['/private'],
        created_at: 0,
      },
    })).toContain('GEO 诊断报告')
  })

  it('compare renders the summary', () => {
    const tool = geoCompareTool(serviceOf())
    expect(renderText(tool, { score_a: 72, score_b: 85, score_delta: 13, resolved: [], introduced: [], summary_md: '提升 13 分' })).toContain('提升 13 分')
  })

  it('registerGeoTools registers the four tools and disposes them together', () => {
    const registered: string[] = []
    const disposers: (() => void)[] = []
    const ctx = {
      tools: {
        register: (tool: { name: string }) => {
          registered.push(tool.name)
          disposers.push(() => {})
          return () => {}
        },
      },
    } as never
    const disposer = registerGeoTools(ctx, serviceOf(), permissionOf())
    expect(registered).toEqual([
      'customer_acquisition_geo_scan',
      'customer_acquisition_geo_history',
      'customer_acquisition_geo_report_get',
      'customer_acquisition_geo_compare',
    ])
    disposer()
  })
})

/** Minimal args each presentCall accepts. */
function sampleArgs(name: string): Record<string, unknown> {
  if (name.endsWith('geo_scan')) return { url: 'https://x.com/' }
  if (name.endsWith('geo_history')) return { url_filter: 'https://x.com/' }
  if (name.endsWith('geo_report_get')) return { report_id: 'rep-1' }
  if (name.endsWith('geo_compare')) return { report_a_id: 'a', report_b_id: 'b' }
  return {}
}
