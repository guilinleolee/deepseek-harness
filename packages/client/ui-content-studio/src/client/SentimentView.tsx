/**
 * The sentiment view (企业舆情分析): the six-tab opinion-monitoring surface
 * over the `_sentiment.json` faces — task management, dashboard, mention
 * list, AI report preview, alert inbox, and settings. The report generation
 * remains a static demo until the LLM report face lands; everything else
 * reads and writes the real store.
 */
import { Fragment, useCallback, useEffect, useState, type ReactNode } from 'react'
import type { PropsLocale } from '@deepseek-ai/dsh-client-ui-slots'
import type {
  SentimentAlert, SentimentAlertId, SentimentPolarity, SentimentReport, SentimentScanResult,
  SentimentSettings, SentimentSnapshot, SentimentStats, SentimentTask, SentimentTaskId,
  SentimentTaskInput,
} from '@deepseek-ai/dsh-content-outputs/types'
import type { TopicItemInput } from '@deepseek-ai/dsh-content-topics/types'
import css from './SentimentView.module.css'

type TabKey = 'tasks' | 'dashboard' | 'list' | 'report' | 'alerts' | 'settings'

/** The server faces the view drives, unwrap-wrapped by the host assembly. */
export interface SentimentGateway {
  getSentiment: () => Promise<SentimentSnapshot>
  putSentimentTask: (input: SentimentTaskInput) => Promise<SentimentTask>
  deleteSentimentTask: (id: SentimentTaskId) => Promise<void>
  setSentimentTaskEnabled: (id: SentimentTaskId, enabled: boolean) => Promise<SentimentTask>
  putSentimentSettings: (settings: SentimentSettings) => Promise<void>
  scanSentiment: () => Promise<SentimentScanResult>
  handleSentimentAlert: (id: SentimentAlertId) => Promise<void>
  adjudicateSentimentAlert: (id: SentimentAlertId) => Promise<SentimentAlert>
  sentimentStats: () => Promise<SentimentStats>
  generateSentimentReport: () => Promise<SentimentReport>
}

/** The topic-bank write face the alert→topic reflow rides. */
export interface SentimentTopicsFace {
  put: (input: TopicItemInput) => Promise<unknown>
}

/** Props: the injected gateway, the topic-bank face, and the locale seat. */
export type SentimentViewProps = { sentiment: SentimentGateway; topics: SentimentTopicsFace } & PropsLocale<'content-studio'>

const TABS = [
  { key: 'tasks', labelKey: 'sentiment.tab.tasks' },
  { key: 'dashboard', labelKey: 'sentiment.tab.dashboard' },
  { key: 'list', labelKey: 'sentiment.tab.list' },
  { key: 'report', labelKey: 'sentiment.tab.report' },
  { key: 'alerts', labelKey: 'sentiment.tab.alerts' },
  { key: 'settings', labelKey: 'sentiment.tab.settings' },
] as const

const SENTIMENT_TAG_CLASS: Record<SentimentPolarity, string | undefined> = {
  pos: css.sentimentTagPos,
  neu: css.sentimentTagNeu,
  neg: css.sentimentTagNeg,
}

const SENTIMENT_LABEL_KEYS: Record<SentimentPolarity, 'sentiment.tag.pos' | 'sentiment.tag.neu' | 'sentiment.tag.neg'> = {
  pos: 'sentiment.tag.pos',
  neu: 'sentiment.tag.neu',
  neg: 'sentiment.tag.neg',
}

/** Shared label + control row. */
function Field(props: { label: string; children: ReactNode }) {
  return (
    <label className={css.sentimentFieldRow}>
      <span className={css.sentimentFieldLabel}>{props.label}</span>
      {props.children}
    </label>
  )
}

/** The task form's editable state (dialog-local). */
interface TaskFormState {
  id: SentimentTaskId | null
  name: string
  group: string
  enabled: boolean
  subjectsText: string
  kwPositive: string
  kwNegative: string
  kwNeutral: string
  feedUrlsText: string
  useWeibo: boolean
  useBili: boolean
  intervalMinutes: number
}

function emptyForm(): TaskFormState {
  return {
    id: null, name: '', group: '品牌舆情', enabled: true, subjectsText: '',
    kwPositive: '', kwNegative: '', kwNeutral: '', feedUrlsText: '',
    useWeibo: false, useBili: false, intervalMinutes: 60,
  }
}

/** Split one textarea into trimmed terms (newlines, commas, semicolons). */
function splitTerms(text: string): string[] {
  return text.split(/[、，,；;\n]/u).map(term => term.trim()).filter(term => term.length > 0)
}

/** Compose terms back into the textarea representation. */
function joinTerms(terms: readonly string[]): string {
  return terms.join('；')
}

/** Build the wire input from the dialog state (skipping empty groups). */
function toTaskInput(form: TaskFormState): SentimentTaskInput | { error: string } {
  if (form.name.trim().length === 0) return { error: 'sentiment.error.taskName' }
  const subjects = splitTerms(form.subjectsText)
  if (subjects.length === 0) return { error: 'sentiment.error.subjects' }
  const groups: Array<SentimentTaskInput['keywordGroups'][number]> = []
  const pos = splitTerms(form.kwPositive)
  if (pos.length > 0) groups.push({ polarity: 'pos', terms: pos })
  const neg = splitTerms(form.kwNegative)
  if (neg.length > 0) groups.push({ polarity: 'neg', terms: neg })
  const neu = splitTerms(form.kwNeutral)
  if (neu.length > 0) groups.push({ polarity: 'any', terms: neu })
  const feedUrls = splitTerms(form.feedUrlsText)
  const sources: SentimentTaskInput['sources'] = ['rss', ...(form.useWeibo ? ['weibo' as const] : []), ...(form.useBili ? ['bili' as const] : [])]
  if (feedUrls.length === 0 && !form.useWeibo && !form.useBili) return { error: 'sentiment.error.sources' }
  return {
    ...(form.id === null ? {} : { id: form.id }),
    name: form.name,
    group: form.group,
    enabled: form.enabled,
    subjects,
    keywordGroups: groups,
    sources,
    feedUrls,
    intervalMinutes: Math.max(30, form.intervalMinutes),
  }
}

/**
 * Render the sentiment module: six tabs of live UI over the sentiment faces.
 * @param props - the injected gateway and the locale seat.
 * @returns the page element tree.
 */
export function SentimentView({ sentiment, topics, t }: SentimentViewProps) {
  const [tab, setTab] = useState<TabKey>('tasks')
  const [snapshot, setSnapshot] = useState<SentimentSnapshot | null>(null)
  const [stats, setStats] = useState<SentimentStats | null>(null)
  const [loadError, setLoadError] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)

  const [taskDialogOpen, setTaskDialogOpen] = useState(false)
  const [taskForm, setTaskForm] = useState<TaskFormState>(emptyForm())
  const [formError, setFormError] = useState<string | null>(null)
  const [settingsDraft, setSettingsDraft] = useState<SentimentSettings | null>(null)
  const [reportGenerating, setReportGenerating] = useState(false)
  const [adjudicatingId, setAdjudicatingId] = useState<SentimentAlertId | null>(null)
  const [adjudicationOpenId, setAdjudicationOpenId] = useState<SentimentAlertId | null>(null)

  const load = useCallback(async () => {
    try {
      const [snap, stat] = await Promise.all([sentiment.getSentiment(), sentiment.sentimentStats()])
      setSnapshot(snap)
      setStats(stat)
      setSettingsDraft(snap.settings)
      setLoadError(false)
    } catch {
      setLoadError(true)
    }
  }, [sentiment])

  useEffect(() => { void load() }, [load])

  const flashNotice = (message: string): void => {
    setNotice(message)
    setTimeout(() => { setNotice(current => (current === message ? null : current)) }, 2500)
  }

  const saveTask = async (): Promise<void> => {
    const input = toTaskInput(taskForm)
    if ('error' in input) {
      setFormError(t(input.error as 'sentiment.error.sources'))
      return
    }
    try {
      await sentiment.putSentimentTask(input)
      setTaskDialogOpen(false)
      setFormError(null)
      await load()
      flashNotice(t('sentiment.saved'))
    } catch (error) {
      setFormError(error instanceof Error ? error.message.slice(0, 200) : t('sentiment.saveFailed'))
    }
  }

  const toggleTask = async (task: SentimentTask): Promise<void> => {
    await sentiment.setSentimentTaskEnabled(task.id, !task.enabled)
    await load()
  }

  const deleteTask = async (task: SentimentTask): Promise<void> => {
    await sentiment.deleteSentimentTask(task.id)
    await load()
  }

  const runScan = async (): Promise<void> => {
    setNotice(t('sentiment.scan.running'))
    try {
      const result = await sentiment.scanSentiment()
      setNotice(t('sentiment.scan.done', { n: result.captured }))
      await load()
    } catch (error) {
      setNotice(error instanceof Error ? `${t('sentiment.scan.failed')}：${error.message.slice(0, 160)}` : t('sentiment.scan.failed'))
      await load()
    }
  }

  const markAlertHandled = async (id: SentimentAlertId): Promise<void> => {
    await sentiment.handleSentimentAlert(id)
    await load()
  }

  const adjudicateAlert = async (id: SentimentAlertId): Promise<void> => {
    setAdjudicatingId(id)
    try {
      const updated = await sentiment.adjudicateSentimentAlert(id)
      setSnapshot(current => (current === null ? current : {
        ...current,
        alerts: current.alerts.map(alert => (alert.id === id ? updated : alert)),
      }))
      flashNotice(t('sentiment.adjudicate.done'))
    } catch (error) {
      setNotice(error instanceof Error ? `${t('sentiment.adjudicate.failed')}：${error.message.slice(0, 160)}` : t('sentiment.adjudicate.failed'))
    } finally {
      setAdjudicatingId(null)
    }
  }

  const runReport = async (): Promise<void> => {
    if (reportGenerating) return
    setReportGenerating(true)
    try {
      const report = await sentiment.generateSentimentReport()
      setSnapshot(current => (current === null ? current : { ...current, report }))
      flashNotice(report.degraded ? t('sentiment.report.degraded') : t('sentiment.report.done'))
    } catch (error) {
      setNotice(error instanceof Error ? `${t('sentiment.report.failed')}：${error.message.slice(0, 160)}` : t('sentiment.report.failed'))
    } finally {
      setReportGenerating(false)
    }
  }

  const reflowToTopicBank = async (alertId: SentimentAlertId): Promise<void> => {
    const alert = snapshot?.alerts.find(candidate => candidate.id === alertId)
    if (alert === undefined) return
    const taskName = snapshot?.tasks.find(task => task.id === alert.taskId)?.name ?? alert.taskId
    try {
      await topics.put({
        title: `${taskName}：${alert.summary.slice(0, 60)}`,
        oneLiner: alert.reason,
        status: 'idea',
        source: { type: 'manual', refId: null, url: null, snapshot: null },
        tags: ['舆情'],
        description: [
          `来源：企业舆情分析告警（${alert.createdAt.slice(0, 10)}，风险等级 ${String(alert.level)}）`,
          '',
          alert.reason,
        ].join('\n'),
        score: null,
        planDate: null,
        scheduleItemId: null,
        topicDir: null,
      })
      flashNotice(t('sentiment.alerts.topicAdded'))
    } catch (error) {
      setNotice(error instanceof Error ? `${t('sentiment.alerts.topicFailed')}：${error.message.slice(0, 160)}` : t('sentiment.alerts.topicFailed'))
    }
  }

  const saveSettings = async (): Promise<void> => {
    if (settingsDraft === null) return
    try {
      await sentiment.putSentimentSettings(settingsDraft)
      await load()
      flashNotice(t('sentiment.saved'))
    } catch (error) {
      setNotice(error instanceof Error ? `${t('sentiment.saveFailed')}：${error.message.slice(0, 160)}` : t('sentiment.saveFailed'))
    }
  }

  const editTask = (task: SentimentTask): void => {
    const groupOf = (polarity: SentimentPolarity | 'any'): string =>
      joinTerms(task.keywordGroups.filter(group => group.polarity === polarity).flatMap(group => [...group.terms]))
    setTaskForm({
      id: task.id,
      name: task.name,
      group: task.group,
      enabled: task.enabled,
      subjectsText: joinTerms(task.subjects),
      kwPositive: groupOf('pos'),
      kwNegative: groupOf('neg'),
      kwNeutral: groupOf('any'),
      feedUrlsText: joinTerms(task.feedUrls),
      useWeibo: task.sources.includes('weibo'),
      useBili: task.sources.includes('bili'),
      intervalMinutes: task.intervalMinutes,
    })
    setFormError(null)
    setTaskDialogOpen(true)
  }

  return (
    <div className={css.sentiment}>
      <div className={css.sentimentHead}>
        <div>
          <h2 className={css.sentimentTitle}>{t('sentiment.title')}</h2>
          <p className={css.sentimentSub}>{t('sentiment.subtitle')}</p>
        </div>
        <button
          type="button"
          className={css.sentimentPrimary}
          disabled={snapshot?.scanning === true}
          onClick={() => { void runScan() }}
        >
          {snapshot?.scanning === true ? t('sentiment.scan.running') : t('sentiment.scan.button')}
        </button>
      </div>

      {notice !== null && <div className={css.sentimentMockSaved} role="status">{notice}</div>}
      {loadError && <div className={css.sentimentMockSaved} role="alert">{t('sentiment.loadFailed')}</div>}

      <div className={css.sentimentTabs} role="tablist">
        {TABS.map(({ key, labelKey }) => (
          <button
            key={key}
            type="button"
            role="tab"
            aria-selected={tab === key || undefined}
            className={tab === key ? css.sentimentTabOn : css.sentimentTab}
            onClick={() => { setTab(key) }}
          >
            {t(labelKey)}
          </button>
        ))}
      </div>

      {tab === 'tasks' && (
        <section className={css.sentimentSection}>
          <div className={css.sentimentActionBar}>
            <button type="button" className={css.sentimentPrimary} onClick={() => { setTaskForm(emptyForm()); setFormError(null); setTaskDialogOpen(true) }}>
              {t('sentiment.tasks.new')}
            </button>
            <input className={css.sentimentInput} placeholder={t('sentiment.search.placeholder')} />
          </div>
          <table className={css.sentimentTable}>
            <thead>
              <tr>
                {[t('sentiment.col.name'), t('sentiment.col.subject'), t('sentiment.col.keywords'), t('sentiment.col.frequency'), t('sentiment.col.status'), t('sentiment.col.lastRun'), t('sentiment.col.actions')].map(h => <th key={h}>{h}</th>)}
              </tr>
            </thead>
            <tbody>
              {(snapshot?.tasks ?? []).map(task => (
                <tr key={task.id}>
                  <td>{task.name}</td>
                  <td>{task.subjects.join('、')}</td>
                  <td>{task.keywordGroups.map(group => joinTerms(group.terms)).join(' / ')}</td>
                  <td>{t('sentiment.minutes', { n: task.intervalMinutes })}</td>
                  <td><span className={task.enabled ? css.sentimentTagOn : css.sentimentTagOff}>{task.enabled ? t('sentiment.status.on') : t('sentiment.status.off')}</span></td>
                  <td>{snapshot?.lastScan?.at.slice(0, 16).replace('T', ' ') ?? '—'}</td>
                  <td className={css.sentimentRowActions}>
                    <button type="button" className={css.sentimentGhost} onClick={() => { editTask(task) }}>{t('sentiment.task.edit')}</button>
                    <button type="button" className={css.sentimentGhost} onClick={() => { void toggleTask(task) }}>
                      {task.enabled ? t('sentiment.task.disable') : t('sentiment.task.enable')}
                    </button>
                    <button type="button" className={css.sentimentGhost} onClick={() => { void deleteTask(task) }}>{t('sentiment.task.delete')}</button>
                  </td>
                </tr>
              ))}
              {(snapshot?.tasks.length ?? 0) === 0 && (
                <tr><td colSpan={7} className={css.sentimentHint}>{t('sentiment.tasks.empty')}</td></tr>
              )}
            </tbody>
          </table>

          {taskDialogOpen && (
            <div className={css.sentimentModal} role="dialog" aria-modal="true" aria-label={t('sentiment.task.dialogTitle')}>
              <div className={css.sentimentModalCard}>
                <div className={css.sentimentModalHead}>
                  <strong>{taskForm.id === null ? t('sentiment.task.dialogTitle') : t('sentiment.task.editTitle')}</strong>
                  <button type="button" className={css.sentimentGhost} onClick={() => { setTaskDialogOpen(false) }}>{t('sentiment.task.cancel')}</button>
                </div>
                <div className={css.sentimentForm}>
                  <Field label={t('sentiment.field.taskName')}><input className={css.sentimentInput} value={taskForm.name} onChange={(event) => { setTaskForm({ ...taskForm, name: event.currentTarget.value }) }} /></Field>
                  <Field label={t('sentiment.field.group')}>
                    <select
                      className={css.sentimentInput}
                      value={taskForm.group}
                      onChange={(event) => { setTaskForm({ ...taskForm, group: event.currentTarget.value }) }}
                    >
                      {([
                        ['brand', t('sentiment.group.brand'), t('sentiment.group.hint.brand')],
                        ['complaint', t('sentiment.group.complaint'), t('sentiment.group.hint.complaint')],
                        ['competitor', t('sentiment.group.competitor'), t('sentiment.group.hint.competitor')],
                        ['policy', t('sentiment.group.policy'), t('sentiment.group.hint.policy')],
                      ] as const).map(([, label, hint]) => <option key={label} value={label}>{label}{hint}</option>)}
                    </select>
                  </Field>
                  <Field label={t('sentiment.field.enable')}>
                    <select className={css.sentimentInput} value={taskForm.enabled ? 'on' : 'off'} onChange={(event) => { setTaskForm({ ...taskForm, enabled: event.currentTarget.value === 'on' }) }}>
                      <option value="on">{t('sentiment.status.on')}</option>
                      <option value="off">{t('sentiment.status.off')}</option>
                    </select>
                  </Field>
                  <Field label={t('sentiment.field.subjects')}><textarea className={css.sentimentInput} rows={2} value={taskForm.subjectsText} onChange={(event) => { setTaskForm({ ...taskForm, subjectsText: event.currentTarget.value }) }} /></Field>
                  <Field label={t('sentiment.field.kwPositive')}><input className={css.sentimentInput} value={taskForm.kwPositive} onChange={(event) => { setTaskForm({ ...taskForm, kwPositive: event.currentTarget.value }) }} /></Field>
                  <Field label={t('sentiment.field.kwNegative')}><input className={css.sentimentInput} value={taskForm.kwNegative} onChange={(event) => { setTaskForm({ ...taskForm, kwNegative: event.currentTarget.value }) }} /></Field>
                  <Field label={t('sentiment.field.kwNeutral')}><input className={css.sentimentInput} value={taskForm.kwNeutral} onChange={(event) => { setTaskForm({ ...taskForm, kwNeutral: event.currentTarget.value }) }} /></Field>
                  <Field label={t('sentiment.field.feeds')}><textarea className={css.sentimentInput} rows={2} value={taskForm.feedUrlsText} onChange={(event) => { setTaskForm({ ...taskForm, feedUrlsText: event.currentTarget.value }) }} /></Field>
                  <Field label={t('sentiment.field.sources')}>
                    <div className={css.sentimentChecks}>
                      <label className={css.sentimentCheck}><input type="checkbox" checked readOnly />{t('sentiment.src.rss')}</label>
                      <label className={css.sentimentCheck}>
                        <input
                          type="checkbox"
                          checked={taskForm.useWeibo}
                          onChange={(event) => { setTaskForm({ ...taskForm, useWeibo: event.currentTarget.checked }) }}
                        />
                        {t('sentiment.src.weibo')}
                      </label>
                      <label className={css.sentimentCheck}>
                        <input
                          type="checkbox"
                          checked={taskForm.useBili}
                          onChange={(event) => { setTaskForm({ ...taskForm, useBili: event.currentTarget.checked }) }}
                        />
                        {t('sentiment.src.bili')}
                      </label>
                      <span className={css.sentimentFieldHint}>{t('sentiment.sources.hint')}</span>
                    </div>
                  </Field>
                  <Field label={t('sentiment.field.frequency')}>
                    <select
                      className={css.sentimentInput}
                      value={String(taskForm.intervalMinutes)}
                      onChange={(event) => { setTaskForm({ ...taskForm, intervalMinutes: Number(event.currentTarget.value) }) }}
                    >
                      <option value="30">{t('sentiment.minutes', { n: 30 })}</option>
                      <option value="60">{t('sentiment.minutes', { n: 60 })}</option>
                      <option value="1440">{t('sentiment.minutes', { n: 1440 })}</option>
                    </select>
                  </Field>
                  <Field label={t('sentiment.field.kbBind')}><select className={css.sentimentInput}><option>{t('sentiment.kb.placeholder')}</option></select></Field>
                  <p className={css.sentimentHint}>{t('sentiment.uiOnly')}</p>
                  {formError !== null && <p className={css.sentimentFieldError} role="alert">{formError}</p>}
                </div>
                <div className={css.sentimentModalFoot}>
                  <button type="button" className={css.sentimentPrimary} onClick={() => { void saveTask() }}>{t('sentiment.task.save')}</button>
                  <button type="button" className={css.sentimentGhost} onClick={() => { setTaskDialogOpen(false) }}>{t('sentiment.task.cancel')}</button>
                </div>
              </div>
            </div>
          )}
        </section>
      )}

      {tab === 'dashboard' && (
        <section className={css.sentimentSection}>
          <div className={css.sentimentStatRow}>
            {[
              { label: t('sentiment.stat.total'), value: String(stats?.total ?? 0) },
              { label: t('sentiment.stat.positive'), value: stats === null || stats.total === 0 ? '—' : `${String(Math.round((stats.positive / stats.total) * 100))}%` },
              { label: t('sentiment.stat.neutral'), value: stats === null || stats.total === 0 ? '—' : `${String(Math.round((stats.neutral / stats.total) * 100))}%` },
              { label: t('sentiment.stat.negative'), value: stats === null || stats.total === 0 ? '—' : `${String(Math.round((stats.negative / stats.total) * 100))}%` },
              { label: t('sentiment.stat.risk'), value: String(stats?.negative ?? 0) },
              { label: t('sentiment.stat.tasks'), value: String(stats?.taskCount ?? 0) },
            ].map(stat => (
              <div key={stat.label} className={css.sentimentStatCard}>
                <span className={css.sentimentStatValue}>{stat.value}</span>
                <span className={css.sentimentStatLabel}>{stat.label}</span>
              </div>
            ))}
          </div>
          <div className={css.sentimentChartCard}>
            <strong>{t('sentiment.chart.trend')}</strong>
            <div className={css.sentimentTrend}>
              {(stats?.trend ?? []).map((day) => {
                const max = Math.max(1, day.pos + day.neu + day.neg)
                return (
                  <div key={day.day} className={css.sentimentTrendCol} title={`${day.day}: +${String(day.pos)} ~${String(day.neu)} -${String(day.neg)}`}>
                    <div className={css.sentimentTrendBar} style={{ height: `${String(Math.round(((day.pos + day.neu + day.neg) / max) * 80))}px` }} />
                    <span className={css.sentimentTrendDay}>{day.day.slice(5)}</span>
                  </div>
                )
              })}
            </div>
          </div>
          <div className={css.sentimentChartCard}>
            <strong>{t('sentiment.chart.platforms')}</strong>
            {(stats?.platforms.length ?? 0) === 0
              ? <p className={css.sentimentHint}>{t('sentiment.list.empty')}</p>
              : (
                <ul className={css.sentimentAlertList}>
                  {(stats?.platforms ?? []).map(entry => (
                    <li key={entry.platform}>{`${entry.platform} — ${String(entry.count)}`}</li>
                  ))}
                </ul>
              )}
          </div>
        </section>
      )}

      {tab === 'list' && (
        <section className={css.sentimentSection}>
          <table className={css.sentimentTable}>
            <thead>
              <tr>
                {[t('sentiment.col.platform'), t('sentiment.col.time'), t('sentiment.col.summary'), t('sentiment.col.sentiment'), t('sentiment.col.actions')].map(h => <th key={h}>{h}</th>)}
              </tr>
            </thead>
            <tbody>
              {(snapshot?.mentions ?? []).slice(0, 100).map(mention => (
                <tr key={mention.id}>
                  <td>{mention.platform}</td>
                  <td>{mention.capturedAt.slice(0, 16).replace('T', ' ')}</td>
                  <td className={css.sentimentSummary}>{mention.title}</td>
                  <td><span className={SENTIMENT_TAG_CLASS[mention.polarity]}>{t(SENTIMENT_LABEL_KEYS[mention.polarity])}</span></td>
                  <td>
                    <a href={mention.url} target="_blank" rel="noreferrer" className={css.sentimentGhost}>{t('sentiment.task.view')}</a>
                  </td>
                </tr>
              ))}
              {(snapshot?.mentions.length ?? 0) === 0 && (
                <tr><td colSpan={5} className={css.sentimentHint}>{t('sentiment.list.empty')}</td></tr>
              )}
            </tbody>
          </table>
        </section>
      )}

      {tab === 'report' && (
        <section className={css.sentimentSection}>
          <div className={css.sentimentActionBar}>
            <button
              type="button"
              className={css.sentimentPrimary}
              disabled={reportGenerating}
              onClick={() => { void runReport() }}
            >
              {reportGenerating ? t('sentiment.report.generatingReal') : t('sentiment.report.generate')}
            </button>
            {snapshot?.report !== null && snapshot?.report !== undefined && (
              <a
                className={css.sentimentGhost}
                download={`sentiment-report-${snapshot.report.generatedAt.slice(0, 10)}.md`}
                href={`data:text/markdown;charset=utf-8,${encodeURIComponent(snapshot.report.markdown)}`}
              >
                {t('sentiment.report.dlMd')}
              </a>
            )}
          </div>
          {snapshot?.report?.degraded === true && (
            <p className={css.sentimentFieldError} role="status">{t('sentiment.report.degradedHint')}</p>
          )}
          <div className={css.sentimentReportPreview}>
            {snapshot?.report === null || snapshot?.report === undefined
              ? <pre className={css.sentimentReportText}>{t('sentiment.report.emptyReal')}</pre>
              : <pre className={css.sentimentReportText}>{snapshot.report.markdown}</pre>}
          </div>
        </section>
      )}

      {tab === 'alerts' && (
        <section className={css.sentimentSection}>
          <table className={css.sentimentTable}>
            <thead>
              <tr>
                {[t('sentiment.col.time'), t('sentiment.col.name'), t('sentiment.col.level'), t('sentiment.alerts.summary'), t('sentiment.alerts.reason'), t('sentiment.alerts.state'), t('sentiment.col.actions')].map(h => <th key={h}>{h}</th>)}
              </tr>
            </thead>
            <tbody>
              {(snapshot?.alerts ?? []).map(alert => (
                <Fragment key={alert.id}>
                  <tr>
                    <td>{alert.createdAt.slice(0, 16).replace('T', ' ')}</td>
                    <td>{(snapshot?.tasks ?? []).find(task => task.id === alert.taskId)?.name ?? alert.taskId}</td>
                    <td><span className={css[`sentimentLevel${alert.level}`]}>{t(`sentiment.level.${alert.level}`)}</span></td>
                    <td className={css.sentimentSummary}>{alert.summary}</td>
                    <td>{alert.reason}</td>
                    <td>{alert.handled ? t('sentiment.alerts.state.done') : t('sentiment.alerts.state.open')}</td>
                    <td className={css.sentimentRowActions}>
                      <button type="button" className={css.sentimentGhost} disabled={adjudicatingId === alert.id} onClick={() => { void adjudicateAlert(alert.id) }}>
                        {adjudicatingId === alert.id ? t('sentiment.adjudicate.running') : t('sentiment.adjudicate.run')}
                      </button>
                      {alert.adjudication != null && (
                        <button type="button" className={css.sentimentGhost} onClick={() => { setAdjudicationOpenId(current => (current === alert.id ? null : alert.id)) }}>
                          {adjudicationOpenId === alert.id ? t('sentiment.adjudicate.hide') : t('sentiment.adjudicate.show')}
                        </button>
                      )}
                      <button type="button" className={css.sentimentGhost} onClick={() => { void reflowToTopicBank(alert.id) }}>
                        {t('sentiment.alerts.toTopic')}
                      </button>
                      {!alert.handled && (
                        <button type="button" className={css.sentimentGhost} onClick={() => { void markAlertHandled(alert.id) }}>
                          {t('sentiment.alerts.markDone')}
                        </button>
                      )}
                    </td>
                  </tr>
                  {adjudicationOpenId === alert.id && alert.adjudication != null && (
                    <tr>
                      <td colSpan={7}>
                        <div className={css.sentimentAdjudication}>
                          <p><strong>{t('sentiment.adjudicate.optimistic')}</strong>{alert.adjudication.optimistic}</p>
                          <p><strong>{t('sentiment.adjudicate.cautious')}</strong>{alert.adjudication.cautious}</p>
                          <p><strong>{t('sentiment.adjudicate.conclusion')}</strong>{alert.adjudication.conclusion}</p>
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
              {(snapshot?.alerts.length ?? 0) === 0 && (
                <tr><td colSpan={7} className={css.sentimentHint}>{t('sentiment.alerts.empty')}</td></tr>
              )}
            </tbody>
          </table>
        </section>
      )}

      {tab === 'settings' && settingsDraft !== null && (
        <section className={css.sentimentSection}>
          <div className={css.sentimentForm}>
            <strong>{t('sentiment.settings.notify')}</strong>
            <Field label={t('sentiment.settings.notifySwitch')}>
              <select className={css.sentimentInput} value={settingsDraft.notifyEnabled ? 'on' : 'off'} onChange={(event) => { setSettingsDraft({ ...settingsDraft, notifyEnabled: event.currentTarget.value === 'on' }) }}>
                <option value="on">{t('sentiment.status.on')}</option>
                <option value="off">{t('sentiment.status.off')}</option>
              </select>
            </Field>
            <Field label={t('sentiment.settings.chDingtalk')}><input className={css.sentimentInput} value={settingsDraft.dingtalkWebhook ?? ''} onChange={(event) => { setSettingsDraft({ ...settingsDraft, dingtalkWebhook: event.currentTarget.value.trim().length === 0 ? null : event.currentTarget.value.trim() }) }} /></Field>
            <Field label={t('sentiment.settings.chWecom')}><input className={css.sentimentInput} value={settingsDraft.wecomWebhook ?? ''} onChange={(event) => { setSettingsDraft({ ...settingsDraft, wecomWebhook: event.currentTarget.value.trim().length === 0 ? null : event.currentTarget.value.trim() }) }} /></Field>
            <Field label={t('sentiment.settings.chEmail')}><input className={css.sentimentInput} value={settingsDraft.email ?? ''} onChange={(event) => { setSettingsDraft({ ...settingsDraft, email: event.currentTarget.value.trim().length === 0 ? null : event.currentTarget.value.trim() }) }} /></Field>
            <Field label={t('sentiment.settings.smtpHost')}><input className={css.sentimentInput} value={settingsDraft.smtpHost ?? ''} onChange={(event) => { setSettingsDraft({ ...settingsDraft, smtpHost: event.currentTarget.value.trim().length === 0 ? null : event.currentTarget.value.trim() }) }} /></Field>
            <Field label={t('sentiment.settings.smtpPort')}>
              <input className={css.sentimentInput} type="number" min={1} max={65535} value={settingsDraft.smtpPort} onChange={(event) => { setSettingsDraft({ ...settingsDraft, smtpPort: Math.max(1, Math.min(65535, Number(event.currentTarget.value) || 465)) }) }} />
            </Field>
            <Field label={t('sentiment.settings.smtpUser')}><input className={css.sentimentInput} value={settingsDraft.smtpUser ?? ''} onChange={(event) => { setSettingsDraft({ ...settingsDraft, smtpUser: event.currentTarget.value.trim().length === 0 ? null : event.currentTarget.value.trim() }) }} /></Field>
            <Field label={t('sentiment.settings.smtpPassword')}><input className={css.sentimentInput} type="password" value={settingsDraft.smtpPassword ?? ''} onChange={(event) => { setSettingsDraft({ ...settingsDraft, smtpPassword: event.currentTarget.value.length === 0 ? null : event.currentTarget.value }) }} /></Field>
            <Field label={t('sentiment.settings.smtpFrom')}><input className={css.sentimentInput} value={settingsDraft.smtpFrom ?? ''} onChange={(event) => { setSettingsDraft({ ...settingsDraft, smtpFrom: event.currentTarget.value.trim().length === 0 ? null : event.currentTarget.value.trim() }) }} /></Field>
            <strong>{t('sentiment.settings.threshold')}</strong>
            <Field label={`${t('sentiment.settings.thNegative')}（${String(settingsDraft.negativeHeatThreshold)}）`}>
              <input type="range" min={50} max={5000} step={50} value={settingsDraft.negativeHeatThreshold} onChange={(event) => { setSettingsDraft({ ...settingsDraft, negativeHeatThreshold: Number(event.currentTarget.value) }) }} />
            </Field>
            <Field label={`${t('sentiment.settings.thSurge')}（${String(settingsDraft.negativeSurgePercent)}%）`}>
              <input type="range" min={10} max={1000} step={10} value={settingsDraft.negativeSurgePercent} onChange={(event) => { setSettingsDraft({ ...settingsDraft, negativeSurgePercent: Number(event.currentTarget.value) }) }} />
            </Field>
            <strong>{t('sentiment.settings.capture')}</strong>
            <Field label={t('sentiment.settings.blacklist')}><textarea className={css.sentimentInput} rows={2} value={joinTerms(settingsDraft.domainBlacklist)} onChange={(event) => { setSettingsDraft({ ...settingsDraft, domainBlacklist: splitTerms(event.currentTarget.value) }) }} /></Field>
            <Field label={t('sentiment.settings.accountBlacklist')}><textarea className={css.sentimentInput} rows={2} value={joinTerms(settingsDraft.accountBlacklist)} onChange={(event) => { setSettingsDraft({ ...settingsDraft, accountBlacklist: splitTerms(event.currentTarget.value) }) }} /></Field>
            <Field label={t('sentiment.settings.retention')}>
              <input className={css.sentimentInput} type="number" min={1} max={365} value={settingsDraft.retentionDays} onChange={(event) => { setSettingsDraft({ ...settingsDraft, retentionDays: Math.max(1, Math.min(365, Number(event.currentTarget.value) || 90)) }) }} />
            </Field>
            <p className={css.sentimentHint}>{t('sentiment.settings.pushHint')}</p>
          </div>
          <button type="button" className={css.sentimentPrimary} onClick={() => { void saveSettings() }}>{t('sentiment.settings.save')}</button>
        </section>
      )}
    </div>
  )
}
