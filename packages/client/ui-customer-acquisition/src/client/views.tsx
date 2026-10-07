/**
 * The eight workbench pages (tools manifest §9; P4 phase). Every page is a
 * pure function of its injected Remote reads plus the shared read hook —
 * the loading/failed states render through {@link ReadFallback}, so the
 * pages themselves stay branch-free.
 * @module @deepseek-ai/dsh-client-ui-customer-acquisition/client/views
 */

import { useCallback, useState } from 'react'
import type {
  AuditListValue, GeoScanListValue, GeoStats, IntentDistribution, LeadListValue,
  OverviewRequest, OverviewValue, ScoreDistribution, SettingsPatchInput,
  SettingsSnapshotValue, TaskStats,
} from '@deepseek-ai/dsh-customer-acquisition/types'
import type {
  ContentTemplate, GeneratedContent, GeoReport, IcpProfileValue, ScoreRun,
  ScoreTemplateValue, SopTask, SopTemplate,
} from '@deepseek-ai/dsh-customer-acquisition'
import type { PropsLocale } from '@deepseek-ai/dsh-client-ui-slots'
import { ReadFallback, useRemoteRead, type ReadState } from './read.tsx'
import css from './panel.module.css'

/** The locale seat every page carries. */
type PageLocale = PropsLocale<'customer-acquisition'>

/** One epoch-ms value as the page-local timestamp. */
function when(value: number): string {
  return new Date(value).toLocaleString()
}

/** Optional-string cell: the value or the em-dash placeholder. */
function orDash(value: string | undefined): string {
  return value ?? '—'
}

/**
 * The dashboard page: the seven metrics with period and drill-down
 * selectors; every selector change refetches the aggregation.
 */
export function OverviewPage({ getOverview, t }: { getOverview: (request: OverviewRequest) => Promise<OverviewValue> } & PageLocale) {
  const [period, setPeriod] = useState<OverviewRequest['period']>('week')
  const [groupBy, setGroupBy] = useState<'none' | 'industry' | 'source'>('none')
  const read = useRemoteRead(useCallback(() => {
    const request: Parameters<typeof getOverview>[0] = { period }
    if (groupBy !== 'none') request.group_by = groupBy
    return getOverview(request)
  }, [getOverview, period, groupBy]))
  if (read.state !== 'ok') return <ReadFallback state={read} t={t} />
  const totals = read.value.totals
  return (
    <div>
      <div className={css.selectorRow}>
        <span className={css.selectorLabel}>{t('overview.period')}</span>
        {(['today', 'week', 'month'] as const).map(option => (
          <button
            key={option}
            type="button"
            className={css.selectorButton}
            aria-pressed={period === option}
            onClick={() => { setPeriod(option) }}
          >
            {t(`overview.period.${option}`)}
          </button>
        ))}
        <span className={css.selectorLabel}>{t('overview.group')}</span>
        {(['none', 'industry', 'source'] as const).map(option => (
          <button
            key={option}
            type="button"
            className={css.selectorButton}
            aria-pressed={groupBy === option}
            onClick={() => { setGroupBy(option) }}
          >
            {t(`overview.group.${option}`)}
          </button>
        ))}
      </div>
      <dl className={css.settingsList}>
        <dt className={css.settingsKey}>{t('overview.leadCount')}</dt>
        <dd>{totals.lead_count}</dd>
        <dt className={css.settingsKey}>{t('overview.newInPeriod')}</dt>
        <dd>{totals.new_in_period}</dd>
        <dt className={css.settingsKey}>{t('overview.intent')}</dt>
        <dd>{intentLine(totals.intent_distribution)}</dd>
        <dt className={css.settingsKey}>{t('overview.sources')}</dt>
        <dd>{Object.entries(totals.source_distribution).map(([source, count]) => `${source} ${count}`).join('、') || '—'}</dd>
        <dt className={css.settingsKey}>{t('overview.scores')}</dt>
        <dd>{scoreLine(totals.score_distribution)}</dd>
        <dt className={css.settingsKey}>{t('overview.tasks')}</dt>
        <dd>{taskLine(totals.tasks)}</dd>
        <dt className={css.settingsKey}>{t('overview.geo')}</dt>
        <dd>{geoLine(totals.geo)}</dd>
      </dl>
      {read.value.breakdown !== null && (
        <table className={css.table}>
          <caption className={css.sectionTitle}>{t('overview.breakdown')}</caption>
          <thead>
            <tr><th>{t('overview.group')}</th><th>{t('overview.leadCount')}</th><th>{t('overview.newInPeriod')}</th><th>{t('overview.intent')}</th></tr>
          </thead>
          <tbody>
            {read.value.breakdown.map(group => (
              <tr key={group.key}>
                <td>{group.key}</td>
                <td>{group.lead_count}</td>
                <td>{group.new_in_period}</td>
                <td>{intentLine(group.intent_distribution)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

/** `高 x / 中 y / 低 z / 无效 w`. */
function intentLine(intent: IntentDistribution): string {
  return `${intent.high} / ${intent.mid} / ${intent.low} / ${intent.invalid}`
}

/** `0-59 a，60-74 b，75-89 c，90-100 d`. */
function scoreLine(scores: ScoreDistribution): string {
  return `${scores['0-59']}，${scores['60-74']}，${scores['75-89']}，${scores['90-100']}`
}

/** `共 n，成 d，延 f，弃 p（完成率 r%）`. */
function taskLine(tasks: TaskStats): string {
  return `${tasks.total}，${tasks.done}，${tasks.deferred}，${tasks.dropped}（${Math.round(tasks.completion_rate * 100)}%）`
}

/** `s 轮，平均 a 分，最近 l 分`（无报告时最近分为 —）。 */
function geoLine(geo: GeoStats): string {
  return `${geo.scan_count}，${geo.avg_score}，${geo.last_score === undefined ? '—' : geo.last_score}`
}

/** The lead ledger page: the visible leads, newest first. */
export function LeadsPage({ listLeads, t }: { listLeads: () => Promise<LeadListValue> } & PageLocale) {
  const read = useRemoteRead(listLeads)
  if (read.state !== 'ok') return <ReadFallback state={read} t={t} />
  if (read.value.items.length === 0) return <p className={css.reading}>{t('read.empty')}</p>
  return (
    <table className={css.table}>
      <thead>
        <tr>
          <th>{t('leads.company')}</th><th>{t('leads.contact')}</th><th>{t('leads.source')}</th>
          <th>{t('leads.industry')}</th><th>{t('leads.intent')}</th><th>{t('leads.status')}</th>
          <th>{t('leads.owner')}</th><th>{t('leads.updated')}</th>
        </tr>
      </thead>
      <tbody>
        {read.value.items.map(lead => (
          <tr key={lead.id}>
            <td>{lead.company_name}</td>
            <td>{orDash(lead.contact_name)}</td>
            <td>{lead.source}</td>
            <td>{orDash(lead.industry)}</td>
            <td>{orDash(lead.intent_level)}</td>
            <td>{lead.status}</td>
            <td>{orDash(lead.owner_id)}</td>
            <td>{when(lead.updated_at)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

/** The scoring page: run history plus the ICP and score-template catalogs. */
export function ScoringPage(props: {
  listScoreRuns: () => Promise<{ items: ScoreRun[]; total: number }>
  listIcpProfiles: () => Promise<IcpProfileValue[]>
  listScoreTemplates: () => Promise<ScoreTemplateValue[]>
} & PageLocale) {
  const { t } = props
  const runs = useRemoteRead(props.listScoreRuns)
  const profiles = useRemoteRead(props.listIcpProfiles)
  const templates = useRemoteRead(props.listScoreTemplates)
  return (
    <div>
      <div className={css.sectionTitle}>{t('scoring.runs')}</div>
      {runs.state !== 'ok'
        ? <ReadFallback state={runs} t={t} />
        : (
          <table className={css.table}>
            <thead><tr><th>{t('scoring.runLead')}</th><th>{t('scoring.runTotal')}</th><th>{t('scoring.runTag')}</th><th>{t('scoring.runAt')}</th></tr></thead>
            <tbody>
              {runs.value.items.map(run => (
                <tr key={run.id}>
                  <td>{run.lead_id}</td>
                  <td>{run.total}</td>
                  <td>{run.intent_tag}</td>
                  <td>{when(run.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      <div className={css.sectionTitle}>{t('scoring.icp')}</div>
      {profiles.state !== 'ok'
        ? <ReadFallback state={profiles} t={t} />
        : (
          <table className={css.table}>
            <thead><tr><th>{t('templates.name')}</th><th>{t('templates.industry')}</th><th>{t('scoring.weight')}</th></tr></thead>
            <tbody>
              {profiles.value.map(profile => (
                <tr key={profile.id}>
                  <td>{profile.name}</td>
                  <td>{orDash(profile.industry)}</td>
                  <td>{profile.dimensions.reduce((sum, dimension) => sum + dimension.weight, 0)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      <div className={css.sectionTitle}>{t('scoring.templates')}</div>
      {templates.state !== 'ok'
        ? <ReadFallback state={templates} t={t} />
        : (
          <ul className={css.list}>
            {templates.value.map(template => (
              <li key={template.id}>{template.name}{template.enabled ? '' : `（${t('templates.disabled')}）`}</li>
            ))}
          </ul>
        )}
    </div>
  )
}

/** The GEO page: scan history plus one expandable full report per row. */
export function GeoPage({ listGeoScans, getGeoReport, t }: {
  listGeoScans: () => Promise<GeoScanListValue>
  getGeoReport: (reportId: string) => Promise<GeoReport>
} & PageLocale) {
  const scans = useRemoteRead(listGeoScans)
  const [openReport, setOpenReport] = useState<{ id: string; read: ReadState<Pick<GeoReport, 'report_md' | 'score'>> } | undefined>(undefined)
  const open = useCallback((reportId: string) => {
    setOpenReport({ id: reportId, read: { state: 'loading' } })
    getGeoReport(reportId).then(
      report => { setOpenReport({ id: reportId, read: { state: 'ok', value: report } }) },
      (error: unknown) => {
        setOpenReport({ id: reportId, read: { state: 'failed', detail: error instanceof Error ? error.message : String(error) } })
      },
    )
  }, [getGeoReport])
  if (scans.state !== 'ok') return <ReadFallback state={scans} t={t} />
  return (
    <div>
      <div className={css.sectionTitle}>{t('geo.scans')}</div>
      <table className={css.table}>
        <thead>
          <tr><th>{t('geo.url')}</th><th>{t('geo.scanStatus')}</th><th>{t('geo.startedAt')}</th><th>{t('geo.score')}</th><th>{t('geo.report')}</th></tr>
        </thead>
        <tbody>
          {scans.value.items.map(scan => {
            const reportId = scan.report_id
            return (
              <tr key={scan.scan_id}>
                <td>{scan.url}</td>
                <td>{scan.status}</td>
                <td>{when(scan.started_at)}</td>
                <td>{scan.score ?? '—'}</td>
                <td>
                  {reportId === undefined ? '—' : (
                    <button type="button" className={css.selectorButton} onClick={() => { open(reportId) }}>
                      {t('geo.reportOpen')}
                    </button>
                  )}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
      {openReport !== undefined && (
        <div className={css.reportBox}>
          <div className={css.sectionTitle}>
            {`${t('geo.report')} · ${openReport.id}`}
            <button type="button" className={css.selectorButton} onClick={() => { setOpenReport(undefined) }}>
              {t('geo.reportClose')}
            </button>
          </div>
          <ReportBody state={openReport.read} t={t} />
        </div>
      )}
    </div>
  )
}

/** One report's body through the shared read fallback. */
function ReportBody({ state, t }: { state: ReadState<Pick<GeoReport, 'report_md' | 'score'>> } & PageLocale) {
  if (state.state !== 'ok') return <ReadFallback state={state} t={t} />
  return <pre className={css.reportPre}>{state.value.report_md}</pre>
}

/** The nurture-copy page: generation records and the copy-template catalog. */
export function CopyPage(props: {
  listGeneratedContents: () => Promise<{ items: GeneratedContent[]; total: number }>
  listContentTemplates: () => Promise<ContentTemplate[]>
} & PageLocale) {
  const { t } = props
  const contents = useRemoteRead(props.listGeneratedContents)
  const templates = useRemoteRead(props.listContentTemplates)
  return (
    <div>
      <div className={css.sectionTitle}>{t('copy.contents')}</div>
      {contents.state !== 'ok'
        ? <ReadFallback state={contents} t={t} />
        : (
          <table className={css.table}>
            <thead><tr><th>{t('leads.company')}</th><th>{t('copy.type')}</th><th>{t('copy.variant')}</th><th>{t('copy.content')}</th><th>{t('copy.createdAt')}</th></tr></thead>
            <tbody>
              {contents.value.items.map(content => (
                <tr key={content.id}>
                  <td>{content.lead_id}</td>
                  <td>{content.type}</td>
                  <td>{content.variant}</td>
                  <td>{content.content}</td>
                  <td>{when(content.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      <div className={css.sectionTitle}>{t('templates.copy')}</div>
      {templates.state !== 'ok'
        ? <ReadFallback state={templates} t={t} />
        : (
          <ul className={css.list}>
            {templates.value.map(template => (
              <li key={template.id}>{template.name}（{template.type}）{template.enabled ? '' : `（${t('templates.disabled')}）`}</li>
            ))}
          </ul>
        )}
    </div>
  )
}

/** The SOP page: tasks in plan order plus the SOP-template catalog. */
export function SopPage(props: {
  listSopTasks: () => Promise<{ items: SopTask[]; total: number }>
  listSopTemplates: () => Promise<SopTemplate[]>
} & PageLocale) {
  const { t } = props
  const tasks = useRemoteRead(props.listSopTasks)
  const templates = useRemoteRead(props.listSopTemplates)
  return (
    <div>
      <div className={css.sectionTitle}>{t('sop.tasks')}</div>
      {tasks.state !== 'ok'
        ? <ReadFallback state={tasks} t={t} />
        : (
          <table className={css.table}>
            <thead><tr><th>{t('sop.taskTitle')}</th><th>{t('sop.taskStatus')}</th><th>{t('sop.plannedAt')}</th><th>{t('sop.note')}</th></tr></thead>
            <tbody>
              {tasks.value.items.map(task => (
                <tr key={task.id}>
                  <td>{task.title}</td>
                  <td>{task.status}</td>
                  <td>{when(task.planned_at)}</td>
                  <td>{orDash(task.note)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      <div className={css.sectionTitle}>{t('templates.sop')}</div>
      {templates.state !== 'ok'
        ? <ReadFallback state={templates} t={t} />
        : (
          <ul className={css.list}>
            {templates.value.map(template => (
              <li key={template.id}>{template.name}{template.enabled ? '' : `（${t('templates.disabled')}）`}</li>
            ))}
          </ul>
        )}
    </div>
  )
}

/** The template-center page: all four template kinds side by side. */
export function TemplatesPage(props: {
  listIcpProfiles: () => Promise<IcpProfileValue[]>
  listScoreTemplates: () => Promise<ScoreTemplateValue[]>
  listContentTemplates: () => Promise<ContentTemplate[]>
  listSopTemplates: () => Promise<SopTemplate[]>
} & PageLocale) {
  const { t } = props
  const icp = useRemoteRead(props.listIcpProfiles)
  const score = useRemoteRead(props.listScoreTemplates)
  const copy = useRemoteRead(props.listContentTemplates)
  const sop = useRemoteRead(props.listSopTemplates)
  const enabledLabel = (enabled: boolean) => (enabled ? t('templates.enabled') : t('templates.disabled'))
  return (
    <div>
      <div className={css.sectionTitle}>{t('templates.icp')}</div>
      {icp.state !== 'ok' ? <ReadFallback state={icp} t={t} /> : (
        <ul className={css.list}>
          {icp.value.map(profile => <li key={profile.id}>{profile.name}（{orDash(profile.industry)}）</li>)}
        </ul>
      )}
      <div className={css.sectionTitle}>{t('templates.score')}</div>
      {score.state !== 'ok' ? <ReadFallback state={score} t={t} /> : (
        <ul className={css.list}>
          {score.value.map(template => <li key={template.id}>{template.name}（{enabledLabel(template.enabled)}）</li>)}
        </ul>
      )}
      <div className={css.sectionTitle}>{t('templates.copy')}</div>
      {copy.state !== 'ok' ? <ReadFallback state={copy} t={t} /> : (
        <ul className={css.list}>
          {copy.value.map(template => <li key={template.id}>{template.name}（{enabledLabel(template.enabled)}）</li>)}
        </ul>
      )}
      <div className={css.sectionTitle}>{t('templates.sop')}</div>
      {sop.state !== 'ok' ? <ReadFallback state={sop} t={t} /> : (
        <ul className={css.list}>
          {sop.value.map(template => <li key={template.id}>{template.name}（{enabledLabel(template.enabled)}）</li>)}
        </ul>
      )}
    </div>
  )
}

/** The settings page: the P0 settings snapshot and audit tail, plus the page-cap write. */
export function SettingsPage(props: {
  getSettings: () => Promise<SettingsSnapshotValue>
  updateSettings: (patch: SettingsPatchInput) => Promise<SettingsSnapshotValue>
  listAuditLogs: () => Promise<AuditListValue>
} & PageLocale) {
  const { t } = props
  const settings = useRemoteRead(props.getSettings)
  const audit = useRemoteRead(props.listAuditLogs)
  const [pageCap, setPageCap] = useState<string | undefined>(undefined)
  const [saved, setSaved] = useState(false)
  const save = useCallback(() => {
    const parsed = Number(pageCap)
    if (!Number.isInteger(parsed) || parsed < 1) return
    void props.updateSettings({ geo_max_pages: parsed }).then(() => { setSaved(true) })
  }, [pageCap, props])
  const s = settings.state === 'ok' ? settings.value.settings : undefined
  return (
    <div>
      <div className={css.sectionTitle}>{t('panel.settings.title')}</div>
      <ReadFallback state={settings} t={t} />
      {s !== undefined && (
        <dl className={css.settingsList}>
          <dt className={css.settingsKey}>{t('panel.settings.geoMaxPages')}</dt>
          <dd>
            <input
              className={css.input}
              value={pageCap ?? String(s.geo_max_pages)}
              onChange={event => { setPageCap(event.target.value); setSaved(false) }}
            />
            <button type="button" className={css.selectorButton} onClick={() => { save() }}>
              {t('panel.settings.save')}
            </button>
            {saved && <span className={css.saved}>{t('panel.settings.saved')}</span>}
          </dd>
          <dt className={css.settingsKey}>{t('panel.settings.geoTimeout')}</dt>
          <dd>{s.geo_page_timeout_ms}</dd>
          <dt className={css.settingsKey}>{t('panel.settings.todo')}</dt>
          <dd>{s.sop_todo_write_enabled ? '✓' : '✗'}</dd>
          <dt className={css.settingsKey}>{t('panel.settings.defaultIcp')}</dt>
          <dd>{orDash(s.default_icp_profile_id)}</dd>
          <dt className={css.settingsKey}>{t('panel.settings.defaultScore')}</dt>
          <dd>{orDash(s.default_score_template_id)}</dd>
        </dl>
      )}
      <div className={css.sectionTitle}>{t('panel.audit.title')}</div>
      {audit.state !== 'ok'
        ? <ReadFallback state={audit} t={t} />
        : audit.value.items.length === 0
          ? <p className={css.reading}>{t('panel.audit.empty')}</p>
          : (
            <ol className={css.auditList}>
              {audit.value.items.map(record => (
                <li key={record.id}>
                  [{when(record.created_at)}] {record.source}/{record.operator_user_id} {record.action} — {record.summary}
                </li>
              ))}
            </ol>
          )}
    </div>
  )
}
