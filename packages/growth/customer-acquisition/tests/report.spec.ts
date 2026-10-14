import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { completionReturning, mockClock, setupP1, FULL_OPERATOR, OWN_OPERATOR } from './helpers-p1.ts'
import type { P1Harness } from './helpers-p1.ts'
import { ReportService } from '../src/report/service.ts'
import type { GeoScanListValue } from '../src/types.ts'
import { renderOverviewMd, reportOverviewTool } from '../src/tools/report.ts'
import { P4_TOOL_NAMES, registerP4Tools } from '../src/tools/register-p4.ts'
import type { PermissionContextService } from '../src/permission/types.ts'

const NOW = 1_700_000_000_000
const DAY = 24 * 60 * 60 * 1000

/** The valid geo/score/sop row shapes the aggregation reads, ready to put. */
function geoScanRow(id: string, url: string, startedAt: number) {
  return { id, url, status: 'done' as const, started_at: startedAt, finished_at: startedAt + 1 }
}
function geoReportRow(id: string, scanId: string, score: number, createdAt: number) {
  return {
    id, scan_id: scanId, score, findings: [], llms_txt: undefined,
    artifacts: { tasks: [] }, report_md: `# 报告 ${id}`, pages_fetched: 1,
    robots_skipped_paths: [], created_at: createdAt,
  }
}
function scoreRunRow(id: string, leadId: string, total: number, createdAt: number) {
  return {
    id, lead_id: leadId, icp_profile_id: 'icp-x', template_id: 'tpl-x', total,
    reason: 'r', intent_tag: 'high' as const, created_at: createdAt,
  }
}
function sopTaskRow(id: string, leadId: string, status: 'pending' | 'done' | 'deferred' | 'dropped', plannedAt: number) {
  return {
    id, lead_id: leadId, title: `任务 ${id}`, status, planned_at: plannedAt,
    note: undefined, created_at: plannedAt, updated_at: plannedAt,
  }
}
function generatedContentRow(id: string, leadId: string, createdAt: number) {
  return { id, lead_id: leadId, type: 'sms_followup', variant: 'A' as const, content: '文案', template_id: undefined, created_at: createdAt }
}

describe('P4 dashboard aggregation', () => {
  let p1: P1Harness
  let stopClock: () => void

  beforeEach(async () => {
    p1 = await setupP1(completionReturning('{}'))
    stopClock = mockClock(NOW)
  })

  afterEach(async () => {
    stopClock()
    await p1.harness.dispose()
  })

  function reportOf(): ReportService {
    return new ReportService(p1.harness.service.requireDomain())
  }

  it('an empty domain aggregates zeros with no last geo score and no breakdown', () => {
    const value = reportOf().overview({ period: 'week' }, FULL_OPERATOR)
    expect(value.totals).toEqual({
      lead_count: 0,
      new_in_period: 0,
      intent_distribution: { high: 0, mid: 0, low: 0, invalid: 0 },
      source_distribution: {},
      score_distribution: { '0-59': 0, '60-74': 0, '75-89': 0, '90-100': 0 },
      tasks: { total: 0, done: 0, deferred: 0, dropped: 0, completion_rate: 0 },
      geo: { scan_count: 0, avg_score: 0 },
    })
    expect(value.breakdown).toBeNull()
  })

  it('aggregates the seven metrics over leads, runs, tasks, and geo rows', async () => {
    const owned = await p1.ledger.createLead({ company_name: '自有一', source: 'form', industry: '教育' }, FULL_OPERATOR, 'agent')
    const pooled = await p1.ledger.createLead({ company_name: '公海二', source: 'chat' }, FULL_OPERATOR, 'agent')
    const domain = p1.harness.service.requireDomain()
    // a pool lead, an old lead outside every preset window, and an invalid intent
    await domain.table('leads').put(pooled.id as never, { ...pooled, owner_id: undefined } as never)
    await p1.ledger.applyIntent(owned.id, 'high')
    await p1.ledger.applyIntent(pooled.id, 'low')
    await domain.table('leads').put('lead-old' as never, {
      ...owned, id: 'lead-old', company_name: '旧线索', source: 'email', intent_level: 'invalid',
      created_at: NOW - 8 * DAY, updated_at: NOW - 8 * DAY,
    } as never)
    void owned.id

    await domain.table('score_runs').put('run-1' as never, scoreRunRow('run-1', owned.id, 82, NOW - DAY) as never)
    await domain.table('score_runs').put('run-2' as never, scoreRunRow('run-2', owned.id, 55, NOW) as never)
    await domain.table('score_runs').put('run-3' as never, scoreRunRow('run-3', pooled.id, 91, NOW - 2 * DAY) as never)
    await domain.table('score_runs').put('run-4' as never, scoreRunRow('run-4', 'lead-old', 70, NOW) as never)
    // an even older run for the same lead arriving after the newer one
    await domain.table('score_runs').put('run-5' as never, scoreRunRow('run-5', owned.id, 40, NOW - 2 * DAY) as never)

    await domain.table('sop_tasks').put('k1' as never, sopTaskRow('k1', owned.id, 'done', NOW) as never)
    await domain.table('sop_tasks').put('k2' as never, sopTaskRow('k2', owned.id, 'pending', NOW + DAY) as never)
    await domain.table('sop_tasks').put('k3' as never, sopTaskRow('k3', pooled.id, 'deferred', NOW + DAY) as never)
    await domain.table('sop_tasks').put('k4' as never, sopTaskRow('k4', 'lead-old', 'dropped', NOW) as never)

    await domain.table('geo_scans').put('s1' as never, geoScanRow('s1', 'https://a.com/', NOW - DAY) as never)
    await domain.table('geo_scans').put('s2' as never, geoScanRow('s2', 'https://b.com/', NOW) as never)
    await domain.table('geo_reports').put('r1' as never, geoReportRow('r1', 's1', 60, NOW - DAY) as never)
    await domain.table('geo_reports').put('r2' as never, geoReportRow('r2', 's2', 90, NOW) as never)
    // an older report for the first scan arriving after the newer one
    await domain.table('geo_reports').put('r3' as never, geoReportRow('r3', 's1', 50, NOW - 2 * DAY) as never)

    const value = reportOf().overview({ period: 'week' }, FULL_OPERATOR)
    expect(value.totals.lead_count).toBe(3)
    expect(value.totals.new_in_period).toBe(2)
    expect(value.totals.intent_distribution).toEqual({ high: 1, mid: 0, low: 1, invalid: 1 })
    expect(value.totals.source_distribution).toEqual({ chat: 1, email: 1, form: 1 })
    // the lead's latest run wins: 55 lands in 0-59, not 82 in 60-74
    expect(value.totals.score_distribution).toEqual({ '0-59': 1, '60-74': 1, '75-89': 0, '90-100': 1 })
    expect(value.totals.tasks).toEqual({ total: 4, done: 1, deferred: 1, dropped: 1, completion_rate: 0.25 })
    expect(value.totals.geo).toEqual({ scan_count: 2, avg_score: 67, last_score: 90 })
  })

  it('an own-scope operator counts own and pool leads only, while geo stays shared', async () => {
    const owned = await p1.ledger.createLead({ company_name: '自有一', source: 'form' }, OWN_OPERATOR, 'agent')
    const pooled = await p1.ledger.createLead({ company_name: '公海二', source: 'chat' }, OWN_OPERATOR, 'agent')
    const other = await p1.ledger.createLead({ company_name: '他人三', source: 'email' }, FULL_OPERATOR, 'agent')
    const domain = p1.harness.service.requireDomain()
    await domain.table('leads').put(pooled.id as never, { ...pooled, owner_id: undefined } as never)
    await domain.table('score_runs').put('run-x' as never, scoreRunRow('run-x', other.id, 70, NOW) as never)
    await domain.table('sop_tasks').put('k1' as never, sopTaskRow('k1', owned.id, 'done', NOW) as never)
    await domain.table('sop_tasks').put('k2' as never, sopTaskRow('k2', other.id, 'done', NOW) as never)
    await domain.table('geo_scans').put('s1' as never, geoScanRow('s1', 'https://a.com/', NOW) as never)
    await domain.table('geo_reports').put('r1' as never, geoReportRow('r1', 's1', 66, NOW) as never)

    const value = reportOf().overview({ period: 'month', group_by: 'source' }, OWN_OPERATOR)
    expect(value.totals.lead_count).toBe(2)
    expect(value.totals.source_distribution).toEqual({ chat: 1, form: 1 })
    expect(value.totals.tasks).toMatchObject({ total: 1, done: 1, completion_rate: 1 })
    expect(value.totals.geo).toEqual({ scan_count: 1, avg_score: 66, last_score: 66 })
    expect(value.breakdown).toEqual([
      { key: 'chat', lead_count: 1, new_in_period: 1, intent_distribution: { high: 0, mid: 0, low: 0, invalid: 0 } },
      { key: 'form', lead_count: 1, new_in_period: 1, intent_distribution: { high: 0, mid: 0, low: 0, invalid: 0 } },
    ])
  })

  it('resolves the preset windows and groups, and fails loud on a broken custom range', async () => {
    const domain = p1.harness.service.requireDomain()
    await domain.table('leads').put('lead-today' as never, {
      id: 'lead-today', owner_id: undefined, source: 'form', company_name: '今天', tags: [], opportunity_stage: 'new',
      status: 'active' as const, created_at: NOW, updated_at: NOW,
    } as never)
    await domain.table('leads').put('lead-old' as never, {
      id: 'lead-old', owner_id: undefined, source: 'form', company_name: '八天前', tags: [], opportunity_stage: 'new',
      status: 'active' as const, created_at: NOW - 8 * DAY, updated_at: NOW - 8 * DAY,
    } as never)

    expect(reportOf().overview({ period: 'today' }, FULL_OPERATOR).totals.new_in_period).toBe(1)
    expect(reportOf().overview({ period: 'week' }, FULL_OPERATOR).totals.new_in_period).toBe(1)
    expect(reportOf().overview({ period: 'month' }, FULL_OPERATOR).totals.new_in_period).toBe(2)

    expect(() => reportOf().overview({ period: 'custom' }, FULL_OPERATOR)).toThrow('from 与 to')
    expect(() => reportOf().overview({ period: 'custom', from: NOW, to: NOW - DAY }, FULL_OPERATOR)).toThrow('颠倒')
    const custom = reportOf().overview({ period: 'custom', from: NOW - DAY, to: NOW }, FULL_OPERATOR)
    expect(custom.totals.new_in_period).toBe(1)

    const byIndustry = reportOf().overview({ period: 'month', group_by: 'industry' }, FULL_OPERATOR)
    expect(byIndustry.breakdown).toEqual([
      { key: '未填写', lead_count: 2, new_in_period: 2, intent_distribution: { high: 0, mid: 0, low: 0, invalid: 0 } },
    ])
  })

  it('sorts breakdown groups heaviest first with deterministic key ties', async () => {
    for (const [name, source] of [['甲', 'chat'], ['乙', 'form'], ['丙', 'chat'], ['丁', 'email']] as const) {
      await p1.ledger.createLead({ company_name: name, source }, FULL_OPERATOR, 'agent')
    }
    const value = reportOf().overview({ period: 'month', group_by: 'source' }, FULL_OPERATOR)
    expect(value.breakdown?.map(group => `${group.key}:${group.lead_count}`)).toEqual(['chat:2', 'email:1', 'form:1'])
  })
})

describe('P4 overview tool and render', () => {
  const OVERVIEW = {
    totals: {
      lead_count: 3,
      new_in_period: 2,
      intent_distribution: { high: 1, mid: 0, low: 1, invalid: 1 },
      source_distribution: { chat: 1, form: 2 },
      score_distribution: { '0-59': 1, '60-74': 0, '75-89': 0, '90-100': 1 },
      tasks: { total: 4, done: 1, deferred: 1, dropped: 1, completion_rate: 0.25 },
      geo: { scan_count: 2, avg_score: 75, last_score: 90 },
    },
    breakdown: [
      { key: 'chat', lead_count: 1, new_in_period: 0, intent_distribution: { high: 0, mid: 0, low: 1, invalid: 0 } },
    ],
  }

  function permissionOf(): PermissionContextService {
    return { resolve: async () => FULL_OPERATOR } as never
  }

  it('registers exactly the P4 tool names', () => {
    expect(P4_TOOL_NAMES).toEqual(['customer_acquisition_report_overview'])
    const registered: string[] = []
    const disposer = registerP4Tools({ tools: { register: (tool: { name: string }) => {
      registered.push(tool.name)
      return () => {}
    } } } as never, { report: {} as never, permission: permissionOf() })
    disposer()
    expect(registered).toEqual(P4_TOOL_NAMES)
  })

  it('executes through the report service and renders the metric table', async () => {
    const overview = vi.fn(async () => OVERVIEW)
    const tool = reportOverviewTool({
      report: { overview } as never,
      permission: permissionOf(),
    })
    const value = await tool.execute({ period: 'custom', from: 1, to: 2, group_by: 'industry' }, { agent: { id: 'a1' } } as never) as { totals: { lead_count: number } }
    expect(overview).toHaveBeenLastCalledWith({ period: 'custom', from: 1, to: 2, group_by: 'industry' }, FULL_OPERATOR)
    await tool.execute({ period: 'week' }, { agent: { id: 'a1' } } as never)
    expect(overview).toHaveBeenLastCalledWith({ period: 'week' }, FULL_OPERATOR)
    expect(value.totals.lead_count).toBe(3)
    const blocks = tool.output.render({}, value as never)
    expect((blocks[0] as { text: string }).text).toContain('获客数据看板')
    const call = tool.presentCall?.({ period: 'week', group_by: 'industry' })
    expect((call as { title?: string }).title).toBe('获客数据看板')
    expect((call as { rawInput?: string }).rawInput).toBe('week / industry')
    const bare = tool.presentCall?.({ period: 'today' })
    expect((bare as { rawInput?: string }).rawInput).toBe('today')

    const rendered = renderOverviewMd(OVERVIEW)
    expect(rendered).toContain('线索总量：3（区间新增 2）')
    expect(rendered).toContain('高 1 / 中 0 / 低 1 / 无效 1')
    expect(rendered).toContain('form 2')
    expect(rendered).toContain('完成率 25%')
    expect(rendered).toContain('平均 75 分，最近 90 分')
    expect(rendered).toContain('| chat | 1 | 0 | 0/0/1/0 |')
  })

  it('renders the no-breakdown and empty-source shapes', () => {
    const bare = renderOverviewMd({
      totals: {
        lead_count: 0, new_in_period: 0,
        intent_distribution: { high: 0, mid: 0, low: 0, invalid: 0 },
        source_distribution: {},
        score_distribution: { '0-59': 0, '60-74': 0, '75-89': 0, '90-100': 0 },
        tasks: { total: 0, done: 0, deferred: 0, dropped: 0, completion_rate: 0 },
        geo: { scan_count: 1, avg_score: 0 },
      },
      breakdown: null,
    })
    expect(bare).toContain('来源分布：（无）')
    expect(bare).toContain('GEO 诊断：1 轮，平均 0 分')
    expect(bare).not.toContain('| 分组')
  })
})

describe('P4 panel Remote read faces', () => {
  let p1: P1Harness
  let stopClock: () => void

  beforeEach(async () => {
    p1 = await setupP1(completionReturning('{}'))
    stopClock = mockClock(NOW)
  })

  afterEach(async () => {
    stopClock()
    await p1.harness.dispose()
  })

  it('serves every panel read through the customerAcquisition Remote face', async () => {
    const service = p1.harness.service
    const owned = await p1.ledger.createLead({ company_name: '自有一', source: 'form', industry: '教育' }, OWN_OPERATOR, 'agent')
    const other = await p1.ledger.createLead({ company_name: '他人二', source: 'chat' }, FULL_OPERATOR, 'agent')
    const domain = service.requireDomain()
    await domain.table('score_runs').put('run-1' as never, scoreRunRow('run-1', owned.id, 82, NOW) as never)
    await domain.table('score_runs').put('run-2' as never, scoreRunRow('run-2', owned.id, 71, NOW + 1) as never)
    await domain.table('sop_tasks').put('k1' as never, sopTaskRow('k1', owned.id, 'pending', NOW + DAY) as never)
    await domain.table('generated_contents').put('g1' as never, generatedContentRow('g1', owned.id, NOW) as never)
    await domain.table('generated_contents').put('g2' as never, generatedContentRow('g2', other.id, NOW + 1) as never)
    await domain.table('generated_contents').put('g3' as never, generatedContentRow('g3', owned.id, NOW - 1) as never)
    await domain.table('geo_scans').put('s1' as never, geoScanRow('s1', 'https://a.com/', NOW) as never)
    await domain.table('geo_scans').put('s2' as never, { id: 's2', url: 'https://b.com/', status: 'running' as const, started_at: NOW + 1 } as never)
    await domain.table('geo_scans').put('s3' as never, geoScanRow('s3', 'https://c.com/', NOW + 2) as never)
    await domain.table('geo_reports').put('r1' as never, geoReportRow('r1', 's1', 88, NOW) as never)
    await domain.table('geo_reports').put('r2' as never, geoReportRow('r2', 's1', 92, NOW + 1) as never)
    // an older report for the same scan arriving last never replaces the latest
    await domain.table('geo_reports').put('r3' as never, geoReportRow('r3', 's1', 70, NOW - 1) as never)
    // the panel resolves the web operator per call; this employee sees only emp-1 leads + pool
    vi.spyOn((service as unknown as { ctx: { permissionContext: { resolve: () => Promise<typeof OWN_OPERATOR> } } }).ctx.permissionContext, 'resolve').mockImplementation(async () => OWN_OPERATOR)

    const leads = await service.listLeadsRemote({ owner: 'me' })
    expect(leads.items.map(lead => lead.company_name)).toEqual(['自有一'])
    // the panel may omit the filter object entirely: own + pool scope applies
    await expect(service.listLeadsRemote()).resolves.toMatchObject({ total: 1 })

    const runs = await service.listScoreRunsRemote({ limit: 10 })
    expect(runs.items.map(run => run.id)).toEqual(['run-2', 'run-1'])
    // the lead filter never smuggles another operator's runs through
    await expect(service.listScoreRunsRemote({ lead_id: other.id })).resolves.toMatchObject({ total: 0 })
    await expect(service.listScoreRunsRemote()).resolves.toMatchObject({ total: 2 })

    await p1.scoring.seedTemplates()
    const icp = await service.listIcpProfilesRemote()
    const templates = await service.listScoreTemplatesRemote()
    expect(icp.length).toBeGreaterThan(0)
    expect(templates.length).toBeGreaterThan(0)

    const geo = await service.listGeoScansRemote() as GeoScanListValue
    expect(geo.total).toBe(3)
    expect(geo.items.map(row => row.scan_id)).toEqual(['s3', 's2', 's1'])
    expect(geo.items[2]).toMatchObject({ score: 92, report_id: 'r2', finished_at: NOW + 1 })
    expect(geo.items[1]).not.toHaveProperty('finished_at')
    expect(geo.items[1]).not.toHaveProperty('score')
    expect((await service.listGeoScansRemote(1)).items).toHaveLength(1)

    await expect(service.getGeoReportRemote('r1')).resolves.toMatchObject({ score: 88 })
    await expect(service.getGeoReportRemote('ghost')).rejects.toThrow('GEO 报告不存在')

    const contents = await service.listGeneratedContentsRemote({})
    expect(contents.items.map(content => content.id)).toEqual(['g1', 'g3'])
    await expect(service.listGeneratedContentsRemote({ lead_id: other.id })).resolves.toMatchObject({ total: 0 })
    await expect(service.listGeneratedContentsRemote()).resolves.toMatchObject({ total: 2 })

    // the seeded industries ship copy and SOP templates
    await expect(service.listContentTemplatesRemote({})).resolves.toHaveLength(6)
    await expect(service.listSopTasksRemote({ status: 'pending' })).resolves.toMatchObject({ total: 1 })
    await expect(service.listSopTasksRemote()).resolves.toMatchObject({ total: 1 })
    await expect(service.listSopTemplatesRemote(true)).resolves.toHaveLength(3)

    // the web operator's own scope: emp-1 sees their lead, not the other operator's
    const overview = await service.getOverviewRemote({ period: 'today' })
    expect(overview.totals.lead_count).toBe(1)
  })
})
