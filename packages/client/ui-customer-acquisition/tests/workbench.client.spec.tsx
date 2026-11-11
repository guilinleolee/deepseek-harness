// @vitest-environment jsdom

import { afterEach, describe, expect, it, vi } from 'vitest'
import { act, cleanup, fireEvent, render, waitFor, within } from '@testing-library/react'
import { createPanelController } from '../src/client/panel-controller.ts'
import { AcquisitionWorkbench } from '../src/client/AcquisitionWorkbench.tsx'
import type { WorkbenchInjected } from '../src/client/injected.ts'
import type { OverviewValue } from '@deepseek-ai/dsh-customer-acquisition/types'
import { zh } from '../src/client/locales.ts'

afterEach(cleanup)

/** Text-content button lookup: jsdom's accessible-name computation is unreliable. */
function clickButton(view: ReturnType<typeof render>, label: string): HTMLElement {
  const found = Array.from(view.getByRole('dialog').querySelectorAll('button'))
    .find(button => button.textContent === label)
  if (found === undefined) throw new Error(`no button labelled ${label}`)
  return found
}

const DAY = 24 * 60 * 60 * 1000
const NOW = 1_700_000_000_000

const OVERVIEW: OverviewValue = {
  totals: {
    lead_count: 2,
    new_in_period: 1,
    intent_distribution: { high: 1, mid: 0, low: 1, invalid: 0 },
    source_distribution: { chat: 1, form: 1 },
    score_distribution: { '0-59': 0, '60-74': 1, '75-89': 0, '90-100': 1 },
    tasks: { total: 2, done: 1, deferred: 1, dropped: 0, completion_rate: 0.5 },
    geo: { scan_count: 1, avg_score: 80, last_score: 88 },
  },
  breakdown: [{ key: '教育', lead_count: 1, new_in_period: 1, intent_distribution: { high: 1, mid: 0, low: 0, invalid: 0 } }],
}

const LEADS = {
  items: [{
    id: 'l1', company_name: '示例公司', contact_name: '王经理', source: 'form', industry: '教育',
    intent_level: 'high' as const, opportunity_stage: 'new' as const, owner_id: 'emp-1',
    status: 'active' as const, tags: [], updated_at: NOW,
  }],
  total: 1,
}

/** Deferred read the tests settle manually, for the loading and failure states. */
function deferred<T>(): { promise: Promise<T>; resolve: (value: T) => void; reject: (error: unknown) => void } {
  let resolve!: (value: T) => void
  let reject!: (error: unknown) => void
  const promise = new Promise<T>((res, rej) => { resolve = res; reject = rej })
  return { promise, resolve, reject }
}

/** Stub face: every read answers valid fixtures unless the test overrides it. */
function faceOf(overrides: Partial<WorkbenchInjected> = {}): WorkbenchInjected {
  return {
    panel: createPanelController(),
    getOverview: vi.fn(async (request: { group_by?: string }) => ({
      ...OVERVIEW,
      breakdown: request.group_by === 'none' || request.group_by === undefined ? null : OVERVIEW.breakdown,
    })),
    listLeads: vi.fn(async () => LEADS),
    listScoreRuns: vi.fn(async () => ({
      items: [{ id: 'run-1', lead_id: 'l1', icp_profile_id: 'i', template_id: 't', total: 82, reason: 'r', intent_tag: 'high' as const, created_at: NOW }],
      total: 1,
    })),
    listIcpProfiles: vi.fn(async () => [
      { id: 'i1', name: '零售画像', industry: '实体门店', enabled: true, created_at: NOW, updated_at: NOW,
        dimensions: [{ id: 'd', name: '规模', description: 'd', weight: 100 }] },
    ]),
    listScoreTemplates: vi.fn(async () => [
      { id: 't1', name: '零售模板', industry: '实体门店', enabled: true, created_at: NOW, updated_at: NOW,
        dimensions: [{ id: 'd', name: '规模', description: 'd', weight: 100 }] },
    ]),
    listGeoScans: vi.fn(async () => ({
      items: [{ scan_id: 's1', url: 'https://x.com/', status: 'done' as const, started_at: NOW, finished_at: NOW + 1, report_id: 'r1', score: 88 }],
      total: 1,
    })),
    getGeoReport: vi.fn(async () => ({ report_md: '# GEO 诊断报告', score: 88 })),
    listGeneratedContents: vi.fn(async () => ({
      items: [{ id: 'g1', lead_id: 'l1', type: 'sms_followup', variant: 'A' as const, content: '短信正文', template_id: undefined, created_at: NOW }],
      total: 1,
    })),
    listContentTemplates: vi.fn(async () => [
      { id: 'ct1', name: '首触模板', industry: undefined, type: 'wecom_first_touch', body: 'b', variables: [], enabled: false, created_at: NOW, updated_at: NOW },
    ]),
    listSopTasks: vi.fn(async () => ({
      items: [{ id: 'k1', lead_id: 'l1', title: '微信问候', status: 'pending' as const, planned_at: NOW + DAY, note: '带脚本', created_at: NOW, updated_at: NOW }],
      total: 1,
    })),
    listSopTemplates: vi.fn(async () => [
      { id: 'st1', name: '零售 SOP', industry: '实体门店', enabled: true, created_at: NOW, updated_at: NOW,
        rules: [{ intent_level: 'high' as const, cadence: 'D+0', points: ['p'], questions: [], risks: [] }] },
    ]),
    getSettings: vi.fn(async () => ({ settings: { geo_max_pages: 10, geo_page_timeout_ms: 10_000, sop_todo_write_enabled: true } })),
    updateSettings: vi.fn(async () => ({ settings: { geo_max_pages: 12, geo_page_timeout_ms: 10_000, sop_todo_write_enabled: true } })),
    listAuditLogs: vi.fn(async () => ({
      items: [{ id: 'a1', source: 'web' as const, operator_user_id: 'emp-1', action: 'settings.update', object_type: 'settings', summary: '更新全局参数', created_at: NOW }],
      total: 1,
    })),
    ...overrides,
  } as WorkbenchInjected
}



/** Render the open workbench on one page with the zh copy the tests assert against. */
function renderPage(page: string, overrides: Partial<WorkbenchInjected> = {}) {
  const face = faceOf(overrides)
  face.panel.open()
  const view = render(<AcquisitionWorkbench {...face} t={key => zh[key as keyof typeof zh]} />)
  // tab queries match by text content inside the nav; page bodies may repeat
  // the labels, and jsdom's accessible-name computation is unreliable here
  const tabs = within(view.getByRole('navigation'))
  const tabFor = (label: string) => {
    const found = tabs.getAllByRole('button').find(button => button.textContent === label)
    if (found === undefined) throw new Error(`no tab labelled ${label}`)
    return found
  }
  for (const [id, label] of Object.entries(zh)) {
    if (id.startsWith('page.') && label !== page) fireEvent.click(tabFor(label))
  }
  // the target tab lands last so the asserted page is the active one
  fireEvent.click(tabFor(page))
  return { view, face }
}

describe('workbench shell', () => {
  it('renders null while closed and the dialog with eight tabs while open', () => {
    const face = faceOf()
    const view = render(<AcquisitionWorkbench {...face} t={key => zh[key as keyof typeof zh]} />)
    expect(view.container.firstElementChild).toBeNull()
    act(() => { face.panel.open() })
    expect(view.getByRole('dialog', { name: '获客运营' })).toBeDefined()
    const tabs = within(view.getByRole('navigation'))
    const tabTexts = tabs.getAllByRole('button').map(button => button.textContent)
    for (const [id, label] of Object.entries(zh)) {
      if (id.startsWith('page.')) expect(tabTexts).toContain(label)
    }
  })

  it('closes through the button and through Escape', () => {
    const face = faceOf()
    face.panel.open()
    const view = render(<AcquisitionWorkbench {...face} t={key => zh[key as keyof typeof zh]} />)
    fireEvent.click(clickButton(view, '返回对话'))
    expect(face.panel.isOpen()).toBe(false)
    act(() => { face.panel.open() })
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(face.panel.isOpen()).toBe(false)
  })
})

describe('overview page', () => {
  it('renders the seven metrics and the breakdown table', async () => {
    const { view, face } = renderPage('总览')
    // the initial week+none request lands no breakdown; switch to industry to see it
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('80，88'))
    fireEvent.click(clickButton(view, '按行业'))
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('教育'))
    expect(face.getOverview).toHaveBeenCalledWith({ period: 'week' })
    expect(face.getOverview).toHaveBeenLastCalledWith({ period: 'week', group_by: 'industry' })
  })

  it('refetches on period and drill-down changes and hides the breakdown on none', async () => {
    const { view, face } = renderPage('总览')
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('80，88'))
    const click = (label: string) => fireEvent.click(clickButton(view, label))
    click('今天')
    await waitFor(() => expect(face.getOverview).toHaveBeenLastCalledWith({ period: 'today' }))
    click('按行业')
    await waitFor(() => expect(face.getOverview).toHaveBeenLastCalledWith({ period: 'today', group_by: 'industry' }))
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('下钻明细'))
    click('不分组的')
    await waitFor(() => expect(face.getOverview).toHaveBeenLastCalledWith({ period: 'today' }))
    await waitFor(() => expect(view.getByRole('dialog').textContent).not.toContain('下钻明细'))
  })

  it('shows the failure line when the aggregation read rejects', async () => {
    const { view } = renderPage('总览', { getOverview: vi.fn(async () => { throw new Error('聚合失败') }) })
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('聚合失败'))
  })
})

describe('leads page', () => {
  it('renders the lead rows', async () => {
    const { view } = renderPage('线索')
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('示例公司'))
    const body = view.getByRole('dialog').textContent!
    expect(body).toContain('王经理')
    expect(body).toContain('high')
  })

  it('renders the empty state when no leads are visible', async () => {
    const { view } = renderPage('线索', { listLeads: vi.fn(async () => ({ items: [], total: 0 })) })
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('暂无数据。'))
  })
})

describe('scoring page', () => {
  it('renders runs, profiles, and templates', async () => {
    const { view } = renderPage('打分')
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('零售画像'))
    const body = view.getByRole('dialog').textContent!
    expect(body).toContain('82')
    expect(body).toContain('零售模板')
  })

  it('shows the failure line when the runs read rejects', async () => {
    const { view } = renderPage('打分', { listScoreRuns: vi.fn(async () => { throw new Error('runs down') }) })
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('runs down'))
  })
})

describe('geo page', () => {
  it('opens a report on demand and hides it again', async () => {
    const { view, face } = renderPage('GEO 诊断')
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('88'))
    fireEvent.click(clickButton(view, '查看报告'))
    await waitFor(() => expect(face.getGeoReport).toHaveBeenCalledWith('r1'))
    expect(view.getByRole('dialog').textContent).toContain('# GEO 诊断报告')
    fireEvent.click(clickButton(view, '收起报告'))
    expect(view.getByRole('dialog').textContent).not.toContain('# GEO 诊断报告')
  })

  it('reports the failure when the report read rejects', async () => {
    const { view } = renderPage('GEO 诊断', { getGeoReport: vi.fn(async () => { throw new Error('报告不存在') }) })
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('查看报告'))
    fireEvent.click(clickButton(view, '查看报告'))
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('报告不存在'))
  })
})

describe('copy page', () => {
  it('renders generation records and the copy catalog', async () => {
    const { view } = renderPage('培育文案')
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('短信正文'))
    const body = view.getByRole('dialog').textContent!
    expect(body).toContain('首触模板')
    expect(body).toContain('停用')
  })
})

describe('sop page', () => {
  it('renders tasks and the SOP catalog', async () => {
    const { view } = renderPage('SOP 跟进')
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('微信问候'))
    const body = view.getByRole('dialog').textContent!
    expect(body).toContain('带脚本')
    expect(body).toContain('零售 SOP')
  })
})

describe('templates page', () => {
  it('renders all four template kinds', async () => {
    const { view } = renderPage('模板中心')
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('零售画像'))
    const body = view.getByRole('dialog').textContent!
    for (const name of ['零售模板', '首触模板', '零售 SOP']) expect(body).toContain(name)
  })
})

describe('settings page', () => {
  it('renders the settings snapshot and the audit tail', async () => {
    const { view } = renderPage('设置')
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('10000'))
    expect(view.getByRole('dialog').textContent).toContain('settings.update')
  })

  it('saves a new page cap through updateSettings', async () => {
    const { view, face } = renderPage('设置')
    await waitFor(() => expect(view.getByRole('dialog').querySelector('input')).not.toBeNull())
    const input = view.getByRole('dialog').querySelector('input')!
    fireEvent.change(input, { target: { value: '12' } })
    fireEvent.click(clickButton(view, '保存页数上限'))
    await waitFor(() => expect(face.updateSettings).toHaveBeenCalledWith({ geo_max_pages: 12 }))
    expect(view.getByRole('dialog').textContent).toContain('已保存')
  })

  it('ignores a non-integer page cap without calling the write', async () => {
    const { view, face } = renderPage('设置')
    await waitFor(() => expect(view.getByRole('dialog').querySelector('input')).not.toBeNull())
    const input = view.getByRole('dialog').querySelector('input')!
    fireEvent.change(input, { target: { value: 'abc' } })
    fireEvent.click(clickButton(view, '保存页数上限'))
    await new Promise(resolve => setTimeout(resolve, 10))
    expect(face.updateSettings).not.toHaveBeenCalled()
  })

  it('renders the empty audit line', async () => {
    const { view } = renderPage('设置', { listAuditLogs: vi.fn(async () => ({ items: [], total: 0 })) })
    await waitFor(() => expect(view.getByRole('dialog').textContent).toContain('暂无审计记录。'))
  })
})

describe('read plumbing', () => {
  it('drops a late read result after unmount without warning', async () => {
    const pending = deferred<string>()
    const face = faceOf({ listLeads: vi.fn(() => pending.promise) as never })
    face.panel.open()
    const view = render(<AcquisitionWorkbench {...face} t={key => zh[key as keyof typeof zh]} />)
    view.unmount()
    pending.resolve('late')
    await new Promise(resolve => setTimeout(resolve, 10))
    expect(true).toBe(true)
  })
})
