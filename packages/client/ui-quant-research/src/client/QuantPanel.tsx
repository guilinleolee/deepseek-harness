/**
 * The frame-wide quant-research surface occupying the `shell.overlay` hole:
 * read-only views of the PET virtual accounts and the research notes, fed
 * by the plugin's own mounted Remote face. Escape closes; the closed state
 * renders null while the slot entry stays mounted.
 */
import { useCallback, useEffect, useState, useSyncExternalStore } from 'react'
import type {
  AccountListValue, AccountRef, AccountSummaryValue, EquityCurveValue, NoteListValue,
  ResultSnapshotSummaryValue,
} from '@deepseek-ai/dsh-quant-research/types'
import type { PropsLocale } from '@deepseek-ai/dsh-client-ui-slots'
import { BarRow, CompareLines, Sparkline } from './charts.tsx'
import type { CompareLine } from './charts.tsx'
import type { PanelController } from './panel-controller.ts'
import css from './QuantPanel.module.css'

/** Server reads the panel consumes, unwrapped from the Remote envelope. */
export interface QuantPanelInjected {
  panel: PanelController
  listAccounts: () => Promise<AccountListValue>
  listNotes: () => Promise<NoteListValue>
  getAccountState: (ref: AccountRef) => Promise<AccountSummaryValue>
  listResultSnapshots: () => Promise<{ snapshots: ResultSnapshotSummaryValue[] }>
  getEquityCurve: (ref: { result_id: string }) => Promise<EquityCurveValue>
}

/** Full surface props: the injected face plus the locale seat. */
export type QuantPanelProps = QuantPanelInjected & PropsLocale<'quant-research'>

/**
 * Render the quant-research panel.
 * @param props - the injected server reads, the shared controller, and the locale seat.
 * @returns the overlay element tree, or `null` while closed.
 */
export function QuantPanel({
  panel, listAccounts, listNotes, getAccountState, listResultSnapshots, getEquityCurve, t,
}: QuantPanelProps) {
  const subscribe = useCallback((listener: () => void) => panel.subscribe(listener), [panel])
  const getOpenState = useCallback(() => panel.isOpen(), [panel])
  const open = useSyncExternalStore(subscribe, getOpenState)
  const [accounts, setAccounts] = useState<AccountSummaryValue[]>()
  const [notes, setNotes] = useState<NoteListValue['notes']>()
  const [snapshots, setSnapshots] = useState<ResultSnapshotSummaryValue[]>()
  const [error, setError] = useState<string>()

  useEffect(() => {
    if (!open) return
    let cancelled = false
    const read = <T,>(call: () => Promise<T>, apply: (value: T) => void) => {
      call().then((value) => { if (!cancelled) apply(value) }).catch((cause: unknown) => {
        /* v8 ignore next -- the cancelled guard: a late failure after close stays silent. */
        if (!cancelled) setError(cause instanceof Error ? cause.message : String(cause))
      })
    }
    read(listAccounts, (value: AccountListValue) => { setAccounts(value.accounts) })
    read(listNotes, (value: NoteListValue) => { setNotes(value.notes) })
    read(listResultSnapshots, value => { setSnapshots(value.snapshots) })
    return () => { cancelled = true }
  }, [open, listAccounts, listNotes, listResultSnapshots])

  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') panel.close()
    }
    window.addEventListener('keydown', onKey)
    return () => { window.removeEventListener('keydown', onKey) }
  }, [open, panel])

  if (!open) return null
  /** Surface one retry failure through the error seat. */
  const fail = (cause: unknown) => {
    setError(cause instanceof Error ? cause.message : String(cause))
  }
  const retry = () => {
    setError(undefined)
    setAccounts(undefined)
    setNotes(undefined)
    setSnapshots(undefined)
    listAccounts().then(value => setAccounts(value.accounts)).catch(fail)
    listNotes().then(value => setNotes(value.notes)).catch(fail)
    listResultSnapshots().then(value => setSnapshots(value.snapshots)).catch(fail)
  }
  return (
    <div className={css.overlay} role="dialog" aria-label={t('panel.title')}>
      <div className={css.card}>
        <div className={css.header}>
          <span className={css.title}>{t('panel.title')}</span>
          <span className={css.phase}>{t('panel.phase')}</span>
        </div>
        <p className={css.intro}>{t('panel.intro')}</p>

        {error !== undefined && (
          <div className={css.error}>
            {t('panel.load.failed')}: {error}
            <button type="button" className={css.retry} onClick={retry}>{t('panel.retry')}</button>
          </div>
        )}

        <div className={css.sectionTitle}>{t('panel.accounts.title')}</div>
        {accounts !== undefined && accounts.length === 0 && (
          <div className={css.empty}>{t('panel.accounts.empty')}</div>
        )}
        {accounts?.map(account => (
          <AccountCard key={account.account_id} account={account} getAccountState={getAccountState} t={t} />
        ))}

        <div className={css.sectionTitle}>{t('panel.notes.title')}</div>
        {notes !== undefined && notes.length === 0 && (
          <div className={css.empty}>{t('panel.notes.empty')}</div>
        )}
        <ul className={css.noteList}>
          {notes?.map(note => (
            <li key={note.note_id} className={css.noteItem}>
              <span className={css.noteTitle}>{note.title}</span>
              {note.symbol !== null && <span className={css.noteSymbol}>{note.symbol}</span>}
              <span className={css.noteDate}>{new Date(note.created_at).toLocaleDateString()}</span>
            </li>
          ))}
        </ul>

        <div className={css.sectionTitle}>{t('panel.results.title')}</div>
        {snapshots !== undefined && snapshots.length === 0 && (
          <div className={css.empty}>{t('panel.results.empty')}</div>
        )}
        {snapshots?.map(snapshot => (
          <SnapshotCard key={snapshot.result_id} snapshot={snapshot} snapshots={snapshots} getEquityCurve={getEquityCurve} t={t} />
        ))}

        <button type="button" className={css.close} onClick={() => { panel.close() }}>{t('panel.close')}</button>
      </div>
    </div>
  )
}

/** Props of one account card. */
interface AccountCardProps {
  readonly account: AccountSummaryValue
  readonly getAccountState: QuantPanelInjected['getAccountState']
  readonly t: QuantPanelProps['t']
}

/**
 * One account card: headline numbers plus the position-weight bar chart.
 * The bars read the list payload directly; expanding refetches the full
 * state through `getAccountState` to show the position count.
 * @param props - the account summary, the refetch face, and the locale seat.
 * @returns the card element tree.
 */
function AccountCard({ account, getAccountState, t }: AccountCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [detail, setDetail] = useState<AccountSummaryValue>()
  const totalValue = account.positions.reduce((sum, p) => sum + p.market_value, 0) || 1
  const bars = account.positions.map(p => ({
    label: p.symbol,
    value: p.market_value / totalValue,
  }))
  const expand = () => {
    const next = !expanded
    setExpanded(next)
    if (next && detail === undefined) {
      getAccountState({ account_id: account.account_id })
        .then(value => setDetail(value))
        .catch(() => { /* the headline already renders; the detail stays collapsed */ })
    }
  }
  return (
    <div className={css.accountCard}>
      <button type="button" className={css.accountHead} onClick={expand}>
        <span className={css.accountName}>{account.name}</span>
        <span className={css.accountEquity}>{t('panel.accounts.equity')} {account.equity.toFixed(2)}</span>
      </button>
      <div className={css.accountMeta}>
        {t('panel.accounts.cash')} {account.cash.toFixed(2)}
        {detail !== undefined && ` · ${t('panel.accounts.positions')} ${String(detail.positions.length)}`}
      </div>
      {account.positions.length > 0
        ? <BarRow data={bars} ariaLabel={`${account.name} ${t('panel.accounts.weight')}`} />
        : <div className={css.empty}>{t('panel.accounts.noPositions')}</div>}
    </div>
  )
}

/** Props of one backtest-snapshot card. */
interface SnapshotCardProps {
  readonly snapshot: ResultSnapshotSummaryValue
  readonly snapshots: readonly ResultSnapshotSummaryValue[]
  readonly getEquityCurve: QuantPanelInjected['getEquityCurve']
  readonly t: QuantPanelProps['t']
}

/** Format a ratio as a signed percentage with two decimals. */
function percent(ratio: number): string {
  return `${(ratio * 100).toFixed(2)}%`
}

/**
 * One persisted backtest card: symbol, SMA windows, and headline metrics in
 * the collapsed head; expanding fetches the stored equity curve once and
 * draws it as an inline-SVG sparkline.
 * @param props - the snapshot summary, the curve fetch face, and the locale seat.
 * @returns the card element tree.
 */
function SnapshotCard({ snapshot, snapshots, getEquityCurve, t }: SnapshotCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [curve, setCurve] = useState<EquityCurveValue>()
  const [otherId, setOtherId] = useState('')
  const [otherCurve, setOtherCurve] = useState<EquityCurveValue>()
  const others = snapshots.filter(candidate => candidate.result_id !== snapshot.result_id)
  const expand = () => {
    const next = !expanded
    setExpanded(next)
    if (next && curve === undefined) {
      getEquityCurve({ result_id: snapshot.result_id })
        .then(value => setCurve(value))
        .catch(() => { /* the headline already renders; the curve stays collapsed */ })
    }
  }
  const pickOther = (id: string) => {
    setOtherId(id)
    setOtherCurve(undefined)
    if (id !== '') {
      getEquityCurve({ result_id: id })
        .then(value => setOtherCurve(value))
        .catch(() => { /* the primary curve already renders; the comparison simply stays unselected */ })
    }
  }
  const compareLines: CompareLine[] | undefined = curve !== undefined && otherCurve !== undefined
    ? [
      { label: `${snapshot.symbol} SMA(${String(snapshot.params.fast)}/${String(snapshot.params.slow)})`, values: curve.equity.map(point => point.value), color: 'var(--dsh-accent, #4a7dff)' },
      { label: `${otherCurve.symbol} SMA(${String(snapshots.find(c => c.result_id === otherId)?.params.fast ?? '?')}/${String(snapshots.find(c => c.result_id === otherId)?.params.slow ?? '?')})`, values: otherCurve.equity.map(point => point.value), color: 'var(--dsh-danger, #e06666)' },
    ]
    : undefined
  return (
    <div className={css.accountCard}>
      <button type="button" className={css.accountHead} onClick={expand}>
        <span className={css.accountName}>
          {snapshot.symbol} SMA({String(snapshot.params.fast)}/{String(snapshot.params.slow)})
        </span>
        <span className={css.accountEquity}>{t('panel.results.return')} {percent(snapshot.metrics.total_return)}</span>
      </button>
      <div className={css.accountMeta}>
        {t('panel.results.drawdown')} {percent(snapshot.metrics.max_drawdown)}
        {` · ${t('panel.results.trades')} ${String(snapshot.metrics.trade_count)}`}
        {` · ${new Date(snapshot.created_at).toLocaleDateString()}`}
      </div>
      {expanded && curve !== undefined && curve.equity.length > 1 && (
        <Sparkline
          values={curve.equity.map(point => point.value)}
          ariaLabel={`${snapshot.symbol} ${t('panel.results.curve')}`}
          width={320}
          height={72}
        />
      )}
      {expanded && others.length > 0 && (
        <label className={css.accountMeta}>
          {t('panel.results.compareWith')}
          <select value={otherId} onChange={event => { pickOther(event.target.value) }}>
            <option value="">{t('panel.results.compareNone')}</option>
            {others.map(other => (
              <option key={other.result_id} value={other.result_id}>
                {other.symbol} SMA({String(other.params.fast)}/{String(other.params.slow)}) · {percent(other.metrics.total_return)}
              </option>
            ))}
          </select>
        </label>
      )}
      {expanded && compareLines !== undefined && (
        <CompareLines
          lines={compareLines}
          ariaLabel={`${snapshot.symbol} ${t('panel.results.compareLabel')}`}
        />
      )}
    </div>
  )
}
