// @vitest-environment jsdom

import { afterEach, describe, expect, it, vi } from 'vitest'
import { act, cleanup, fireEvent, render, waitFor } from '@testing-library/react'
// Type-only: pulls the LocaleNamespaceMap merge ('quant-research') into
// this program so PropsLocale<'quant-research'> resolves to { t }.
import type {} from '@deepseek-ai/dsh-client-ui-quant-research/client'
import { createPanelController } from '../src/client/panel-controller.ts'
import { apply as nodeApply } from '../src/index.ts'
import { BarRow, CompareLines, Sparkline, barGeometry, compareLinesPoints, sparklinePoints } from '../src/client/charts.tsx'
import { en } from '../src/client/locales.ts'
import { QuantEntry } from '../src/client/QuantEntry.tsx'
import { QuantPanel } from '../src/client/QuantPanel.tsx'
import type {
  AccountListValue, AccountSummaryValue, EquityCurveValue, NoteListValue, ResultSnapshotSummaryValue,
} from '@deepseek-ai/dsh-quant-research/types'

afterEach(cleanup)

/** The en locale seat, fed straight from the dictionary. */
const t = (key: keyof typeof en) => en[key]

const account = (over: Partial<AccountSummaryValue> = {}): AccountSummaryValue => ({
  account_id: 'acct-1',
  name: '研究一号',
  cash: 500_000,
  initial_cash: 1_000_000,
  equity: 750_000,
  positions: [
    { symbol: '000001', shares: 10_000, avg_cost: 10, market_value: 100_000 },
    { symbol: 'AAPL', shares: 200, avg_cost: 150, market_value: 150_000 },
  ],
  ...over,
})

const accountsValue = (accounts: AccountSummaryValue[]): AccountListValue => ({ accounts })
const notesValue: NoteListValue = {
  notes: [
    { note_id: 'n-1', title: '双均线观察', body: 'body', symbol: '000001', tags: ['strategy'], created_at: 1_700_000_000_000 },
    { note_id: 'n-2', title: '风险笔记', body: 'body', symbol: null, tags: [], created_at: 1_710_000_000_000 },
  ],
}

const snapshotValue: ResultSnapshotSummaryValue = {
  result_id: 'r-1',
  symbol: '000001',
  params: { fast: 5, slow: 20, bars: 60, initial_cash: 100_000, fee_rate: 0.0005 },
  metrics: { total_return: 0.05, annual_return: 0.4, max_drawdown: 0.03, sharpe: 1.2, win_rate: 0.6, trade_count: 4, final_equity: 105_000 },
  created_at: 1_700_000_000_000,
}

const curveValue: EquityCurveValue = {
  result_id: 'r-1',
  symbol: '000001',
  equity: [{ date: '2024-01-01', value: 100_000 }, { date: '2024-01-02', value: 102_000 }, { date: '2024-01-03', value: 105_000 }],
}

const snapshotOther: ResultSnapshotSummaryValue = {
  result_id: 'r-2',
  symbol: '000001',
  params: { fast: 10, slow: 30, bars: 60, initial_cash: 100_000, fee_rate: 0.0005 },
  metrics: { total_return: 0.12, annual_return: 0.9, max_drawdown: 0.05, sharpe: 1.5, win_rate: 0.7, trade_count: 6, final_equity: 112_000 },
  created_at: 1_710_000_000_000,
}

const curveOther: EquityCurveValue = {
  result_id: 'r-2',
  symbol: '000001',
  equity: [{ date: '2024-01-01', value: 100_000 }, { date: '2024-01-02', value: 101_000 }, { date: '2024-01-03', value: 112_000 }],
}

/** The panel's injected face with stubbed remote reads. */
function face(
  listAccounts: () => Promise<AccountListValue>,
  listNotes: () => Promise<NoteListValue>,
  getAccountState?: (ref: { account_id?: string; name?: string }) => Promise<AccountSummaryValue>,
  listResultSnapshots?: () => Promise<{ snapshots: ResultSnapshotSummaryValue[] }>,
  getEquityCurve?: (ref: { result_id: string }) => Promise<EquityCurveValue>,
) {
  const panel = createPanelController()
  return {
    panel,
    listAccounts,
    listNotes,
    getAccountState: getAccountState ?? (async () => account()),
    listResultSnapshots: listResultSnapshots ?? (async () => ({ snapshots: [] })),
    getEquityCurve: getEquityCurve ?? (async (ref: { result_id: string }) => ref.result_id === 'r-2' ? curveOther : curveValue),
    t: t as never,
  }
}

describe('charts pure geometry', () => {
  it('maps bar data onto clamped width percentages', () => {
    expect(barGeometry([{ label: 'A', value: 0.25 }, { label: 'B', value: 0.5 }]))
      .toEqual([{ label: 'A', widthPercent: 25 }, { label: 'B', widthPercent: 50 }])
    expect(barGeometry([{ label: 'C', value: -1 }, { label: 'D', value: 2 }]))
      .toEqual([{ label: 'C', widthPercent: 0 }, { label: 'D', widthPercent: 100 }])
  })

  it('maps a series onto sparkline coordinates, spreading and inverting', () => {
    expect(sparklinePoints([], 100, 50, 4)).toEqual([])
    expect(sparklinePoints([5], 100, 50, 4)).toEqual([{ x: 50, y: 25 }])
    const two = sparklinePoints([0, 10], 100, 50, 4)
    expect(two[0]).toEqual({ x: 0, y: 46 })
    expect(two[1]).toEqual({ x: 100, y: 4 })
    // A flat series centers on the middle of the padded band.
    expect(sparklinePoints([3, 3, 3], 90, 50, 5)).toEqual([
      { x: 0, y: 25 }, { x: 45, y: 25 }, { x: 90, y: 25 },
    ])
  })

  it('renders BarRow rows and the Sparkline polyline (null when empty)', () => {
    const bars = render(<BarRow data={[{ label: 'X', value: 0.6 }]} ariaLabel="weights" />)
    expect(bars.getByRole('img', { name: 'weights' })).toBeDefined()
    expect(bars.getByText('60.0%')).toBeDefined()
    const line = render(<Sparkline values={[1, 2, 3]} ariaLabel="trend" />)
    expect(line.getByRole('img', { name: 'trend' }).querySelector('polyline')).not.toBeNull()
    expect(render(<Sparkline values={[]} ariaLabel="empty" />).container.firstElementChild).toBeNull()
  })
})

describe('QuantEntry', () => {
  it('opens the panel on click in both column states', () => {
    const panel = createPanelController()
    const wide = render(<QuantEntry wide={true} panel={panel} t={t as never} />)
    expect(wide.getByRole('button', { name: t('entry.aria') }).textContent).toContain(t('entry.label'))
    fireEvent.click(wide.getByRole('button'))
    expect(panel.isOpen()).toBe(true)
    wide.unmount()

    const rail = render(<QuantEntry wide={false} panel={panel} t={t as never} />)
    expect(rail.getByRole('button', { name: t('entry.aria') })).toBeDefined()
    rail.unmount()
  })
})

describe('QuantPanel', () => {
  it('renders null while closed and the loaded surface while open', async () => {
    const props = face(
      () => Promise.resolve(accountsValue([account()])),
      () => Promise.resolve(notesValue),
    )
    const view = render(<QuantPanel {...props} />)
    expect(view.container.firstElementChild).toBeNull()

    act(() => { props.panel.open() })
    const dialog = await waitFor(() => view.getByRole('dialog', { name: t('panel.title') }))
    expect(dialog.textContent).toContain(t('panel.intro'))
    // The account card: name, equity, cash, and the position-weight bars.
    expect(dialog.textContent).toContain('研究一号')
    expect(dialog.textContent).toContain('750000.00')
    expect(dialog.textContent).toContain('500000.00')
    expect(view.getByText('40.0%')).toBeDefined()
    expect(view.getByText('60.0%')).toBeDefined()
    // The note list renders both notes.
    expect(dialog.textContent).toContain('双均线观察')
    expect(dialog.textContent).toContain('风险笔记')
    expect(dialog.textContent).toContain('000001')
  })

  it('shows the empty states when the domain holds nothing', async () => {
    const props = face(
      () => Promise.resolve(accountsValue([])),
      () => Promise.resolve({ notes: [] }),
    )
    act(() => { props.panel.open() })
    const view = render(<QuantPanel {...props} />)
    const dialog = await waitFor(() => view.getByRole('dialog', { name: t('panel.title') }))
    expect(dialog.textContent).toContain(t('panel.accounts.empty'))
    expect(dialog.textContent).toContain(t('panel.notes.empty'))
  })

  it('shows the no-positions empty state inside an account card', async () => {
    const flat = account({ name: '空仓户', positions: [], equity: 1_000_000, cash: 1_000_000 })
    const props = face(
      () => Promise.resolve(accountsValue([flat])),
      () => Promise.resolve(notesValue),
    )
    act(() => { props.panel.open() })
    const view = render(<QuantPanel {...props} />)
    const dialog = await waitFor(() => view.getByRole('dialog', { name: t('panel.title') }))
    expect(dialog.textContent).toContain(t('panel.accounts.noPositions'))
  })

  it('renders the load failure and recovers through retry', async () => {
    let failing = true
    const props = face(
      () => failing ? Promise.reject(new Error('storage down')) : Promise.resolve(accountsValue([account()])),
      () => Promise.resolve(notesValue),
    )
    act(() => { props.panel.open() })
    const view = render(<QuantPanel {...props} />)
    const dialog = await waitFor(() => view.getByRole('dialog', { name: t('panel.title') }))
    await waitFor(() => { expect(dialog.textContent).toContain(t('panel.load.failed')) })
    failing = false
    await act(async () => { fireEvent.click(view.getByRole('button', { name: t('panel.retry') })) })
    await waitFor(() => { expect(dialog.textContent).toContain('研究一号') })
  })

  it('expands an account card and refetches through getAccountState', async () => {
    const getAccountState = vi.fn(async () => account({ name: '详情', positions: [{ symbol: 'BABA', shares: 1, avg_cost: 1, market_value: 1 }] }))
    const props = face(
      () => Promise.resolve(accountsValue([account()])),
      () => Promise.resolve(notesValue),
      getAccountState,
    )
    act(() => { props.panel.open() })
    const view = render(<QuantPanel {...props} />)
    await waitFor(() => view.getByText('40.0%'))
    await act(async () => { fireEvent.click(view.getByRole('button', { name: /研究一号/ })) })
    expect(getAccountState).toHaveBeenCalledWith({ account_id: 'acct-1' })
    // The detail read surfaces the position count from the refetched state.
    await waitFor(() => {
      expect(view.getByRole('dialog', { name: t('panel.title') }).textContent).toContain('Positions 1')
    })
  })

  it('surfaces a notes failure while accounts succeed, then retry heals both', async () => {
    let notesFailing = true
    const props = face(
      () => Promise.resolve(accountsValue([account()])),
      () => notesFailing ? Promise.reject(new Error('notes down')) : Promise.resolve(notesValue),
    )
    act(() => { props.panel.open() })
    const view = render(<QuantPanel {...props} />)
    const dialog = await waitFor(() => view.getByRole('dialog', { name: t('panel.title') }))
    await waitFor(() => { expect(dialog.textContent).toContain('notes down') })
    // The account section still rendered from its own successful read.
    expect(dialog.textContent).toContain('研究一号')
    notesFailing = false
    await act(async () => { fireEvent.click(view.getByRole('button', { name: t('panel.retry') })) })
    await waitFor(() => { expect(dialog.textContent).toContain('双均线观察') })
  })

  it('surfaces a retry failure through the same error seat', async () => {
    // First load fails (retry button renders); the retry fails differently.
    let message = 'storage down'
    const props = face(
      () => Promise.reject(new Error(message)),
      () => Promise.resolve(notesValue),
    )
    act(() => { props.panel.open() })
    const view = render(<QuantPanel {...props} />)
    const retryButton = await waitFor(() => view.getByRole('button', { name: t('panel.retry') }))
    await waitFor(() => { expect(view.getByRole('dialog', { name: t('panel.title') }).textContent).toContain('storage down') })
    message = 'retry down'
    await act(async () => { fireEvent.click(retryButton) })
    await waitFor(() => { expect(view.getByRole('dialog', { name: t('panel.title') }).textContent).toContain('retry down') })
  })

  it('stringifies a non-Error retry rejection through the error seat', async () => {
    let message: unknown = 'storage down'
    const props = face(
      () => Promise.reject(message),
      () => Promise.resolve(notesValue),
    )
    act(() => { props.panel.open() })
    const view = render(<QuantPanel {...props} />)
    const retryButton = await waitFor(() => view.getByRole('button', { name: t('panel.retry') }))
    message = { code: 'WEIRD' } // a non-Error rejection
    await act(async () => { fireEvent.click(retryButton) })
    await waitFor(() => {
      expect(view.getByRole('dialog', { name: t('panel.title') }).textContent).toContain('[object Object]')
    })
  })

  it('cancels in-flight reads when the panel closes before they settle', async () => {
    let release: (() => void) | undefined
    const slow: () => Promise<AccountListValue> = () => new Promise(resolve => {
      release = () => { resolve(accountsValue([account()])) }
    })
    const props = face(slow, () => Promise.resolve(notesValue))
    const view = render(<QuantPanel {...props} />)
    act(() => { props.panel.open() })
    // Close before the read settles: the cancelled guard must drop the result.
    act(() => { props.panel.close() })
    await act(async () => { release?.() })
    act(() => { props.panel.open() })
    await waitFor(() => { expect(view.getByRole('dialog', { name: t('panel.title') })).toBeDefined() })
    // The late-arriving value from the first (cancelled) effect must not render.
    expect(view.container.textContent ?? '').not.toContain('研究一号')
  })

  it('collapses an expanded account card without refetching', async () => {
    const getAccountState = vi.fn(async () => account())
    const props = face(
      () => Promise.resolve(accountsValue([account()])),
      () => Promise.resolve(notesValue),
      getAccountState,
    )
    act(() => { props.panel.open() })
    const view = render(<QuantPanel {...props} />)
    const head = await waitFor(() => view.getByRole('button', { name: /研究一号/ }))
    await act(async () => { fireEvent.click(head) })
    expect(getAccountState).toHaveBeenCalledTimes(1)
    await act(async () => { fireEvent.click(view.getByRole('button', { name: /研究一号/ })) })
    expect(getAccountState).toHaveBeenCalledTimes(1) // collapse does not refetch
  })

  it('keeps the headline when the detail refetch fails', async () => {
    const props = face(
      () => Promise.resolve(accountsValue([account()])),
      () => Promise.resolve(notesValue),
      async () => { throw new Error('detail down') },
    )
    act(() => { props.panel.open() })
    const view = render(<QuantPanel {...props} />)
    const head = await waitFor(() => view.getByRole('button', { name: /研究一号/ }))
    await act(async () => { fireEvent.click(head) })
    await waitFor(() => {
      expect(view.getByRole('dialog', { name: t('panel.title') }).textContent).toContain('40.0%')
    })
  })

  it('closes through the button and through Escape', async () => {
    const props = face(
      () => Promise.resolve(accountsValue([account()])),
      () => Promise.resolve(notesValue),
    )
    const view = render(<QuantPanel {...props} />)
    act(() => { props.panel.open() })
    await waitFor(() => view.getByRole('dialog', { name: t('panel.title') }))
    fireEvent.click(view.getByRole('button', { name: t('panel.close') }))
    expect(props.panel.isOpen()).toBe(false)

    act(() => { props.panel.open() })
    fireEvent.keyDown(window, { key: 'Tab' })
    expect(props.panel.isOpen()).toBe(true)
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(props.panel.isOpen()).toBe(false)
  })
})

describe('panel controller guards', () => {
  it('ignores redundant open and close transitions', () => {
    const panel = createPanelController()
    const seen: boolean[] = []
    const unsubscribe = panel.subscribe(() => { seen.push(panel.isOpen()) })
    panel.open()
    panel.open() // redundant: no second emission
    expect(seen).toEqual([true])
    panel.close()
    panel.close() // redundant: no second emission
    expect(seen).toEqual([true, false])
    unsubscribe()
  })
})

describe('node half', () => {
  it('node-half apply is a no-op host placeholder', () => {
    nodeApply() // reaching here without throwing is the no-op contract
  })
})

describe('QuantPanel result snapshots', () => {
  it('renders the empty state when no snapshots exist', async () => {
    const props = face(
      () => Promise.resolve(accountsValue([])),
      () => Promise.resolve({ notes: [] }),
      undefined,
      () => Promise.resolve({ snapshots: [] }),
    )
    const view = render(<QuantPanel {...props} />)
    act(() => { props.panel.open() })
    const dialog = await waitFor(() => view.getByRole('dialog'))
    await waitFor(() => expect(dialog.textContent).toContain(t('panel.results.empty')))
  })

  it('renders a snapshot card and draws the curve on expand', async () => {
    const getEquityCurve = vi.fn(async () => curveValue)
    const props = face(
      () => Promise.resolve(accountsValue([])),
      () => Promise.resolve({ notes: [] }),
      undefined,
      () => Promise.resolve({ snapshots: [snapshotValue] }),
      getEquityCurve as never,
    )
    const view = render(<QuantPanel {...props} />)
    act(() => { props.panel.open() })
    const dialog = await waitFor(() => view.getByRole('dialog'))
    // Collapsed head: symbol, windows, and the headline metrics.
    await waitFor(() => expect(dialog.textContent).toContain('000001 SMA(5/20)'))
    expect(dialog.textContent).toContain('5.00%')
    expect(dialog.textContent).toContain('3.00%')
    expect(getEquityCurve).not.toHaveBeenCalled()
    expect(dialog.querySelector('svg')).toBeNull()

    const head = view.getAllByRole('button').find(button => button.textContent?.includes('SMA(5/20)'))
    expect(head).toBeDefined()
    fireEvent.click(head!)
    await waitFor(() => expect(getEquityCurve).toHaveBeenCalledWith({ result_id: 'r-1' }))
    const chart = await waitFor(() => dialog.querySelector('svg[aria-label="000001 净值曲线"]'))
    expect(chart?.querySelector('polyline')).not.toBeNull()
  })
})

describe('CompareLines', () => {
  it('maps both series onto one shared scale', () => {
    const lines = [
      { label: 'A', values: [0, 10], color: 'blue' },
      { label: 'B', values: [5, 5], color: 'red' },
    ]
    const [a, b] = compareLinesPoints(lines, 100, 50, 5)
    // Shared y scale: union range [0,10] → A spans the full padded band.
    expect(a?.[0]?.y).toBe(45)
    expect(a?.[1]?.y).toBe(5)
    expect(b?.[0]?.y).toBe(25)
    // Both series spread over the full width.
    expect(a?.[1]?.x).toBe(100)
    expect(b?.[1]?.x).toBe(100)
  })

  it('renders two polylines with a legend and returns null on empty input', () => {
    const view = render(
      <CompareLines
        lines={[
          { label: 'primary', values: [1, 2, 3], color: 'blue' },
          { label: 'other', values: [3, 2, 1], color: 'red' },
        ]}
        ariaLabel="comparison"
      />,
    )
    const region = view.getByRole('img', { name: 'comparison' })
    expect(region.querySelectorAll('polyline')).toHaveLength(2)
    expect(view.getByText('primary')).toBeDefined()
    expect(view.getByText('other')).toBeDefined()
    view.unmount()
    const empty = render(
      <CompareLines lines={[{ label: 'a', values: [], color: 'blue' }, { label: 'b', values: [1], color: 'red' }]} ariaLabel="empty" />,
    )
    expect(empty.container.firstElementChild).toBeNull()
    empty.unmount()
  })
})

describe('QuantPanel snapshot comparison', () => {
  it('expands a card, picks another snapshot, and draws both curves', async () => {
    const props = face(
      () => Promise.resolve(accountsValue([])),
      () => Promise.resolve({ notes: [] }),
      undefined,
      () => Promise.resolve({ snapshots: [snapshotValue, snapshotOther] }),
    )
    const view = render(<QuantPanel {...props} />)
    act(() => { props.panel.open() })
    const dialog = await waitFor(() => view.getByRole('dialog'))
    await waitFor(() => expect(dialog.textContent).toContain('000001 SMA(5/20)'))

    const head = view.getAllByRole('button').find(button => button.textContent?.includes('SMA(5/20)'))
    expect(head).toBeDefined()
    fireEvent.click(head!)
    const select = await waitFor(() => dialog.querySelector('select'))
    expect(select).not.toBeNull()
    // Before a pick: only the single sparkline, no comparison.
    expect(dialog.querySelector('.quant-compare')).toBeNull()

    act(() => { fireEvent.change(select!, { target: { value: 'r-2' } }) })
    // The second curve fetch resolves outside act's flush; give the microtask
    // queue one beat before polling.
    await new Promise(resolve => setTimeout(resolve, 20))
    const compare = await waitFor(
      () => dialog.querySelector(`[role="img"][aria-label="000001 ${t('panel.results.compareLabel')}"]`)?.querySelectorAll('polyline'),
      { timeout: 3000 },
    )
    expect(compare).not.toBeNull()
    expect(compare).toHaveLength(2)
    expect(dialog.textContent).toContain('SMA(10/30)')
  })
})
