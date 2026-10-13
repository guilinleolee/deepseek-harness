/**
 * The frame-wide placeholder surface occupying the `shell.overlay` hole. It
 * proves the whole P0 chain — the Remote contributions mounted by this
 * plugin's apply feed the settings snapshot and the newest audit rows — and
 * states what ships when. Escape closes; the closed state renders null while
 * the slot entry stays mounted.
 */
import { useCallback, useEffect, useState, useSyncExternalStore } from 'react'
import type { AuditListValue, SettingsSnapshotValue } from '@deepseek-ai/dsh-customer-acquisition/types'
import type { PropsLocale } from '@deepseek-ai/dsh-client-ui-slots'
import type { PanelController } from './panel-controller.ts'
import css from './panel.module.css'

/** Server reads the panel consumes, unwrapped from the Remote envelope. */
export interface AcquisitionPanelInjected {
  panel: PanelController
  getSettings: () => Promise<SettingsSnapshotValue>
  listAuditLogs: () => Promise<AuditListValue>
}

/** Full surface props: the injected face plus the locale seat. */
export type AcquisitionPanelProps = AcquisitionPanelInjected & PropsLocale<'customer-acquisition'>

/**
 * Render the placeholder acquisition panel.
 * @param props - the injected server reads, the shared controller, and the locale seat.
 * @returns the overlay element tree, or `null` while closed.
 */
export function AcquisitionPanel({ panel, getSettings, listAuditLogs, t }: AcquisitionPanelProps) {
  const subscribe = useCallback((listener: () => void) => panel.subscribe(listener), [panel])
  const getOpenState = useCallback(() => panel.isOpen(), [panel])
  const open = useSyncExternalStore(subscribe, getOpenState)
  const [settings, setSettings] = useState<SettingsSnapshotValue>()
  const [audit, setAudit] = useState<AuditListValue>()
  const [error, setError] = useState<string>()

  useEffect(() => {
    if (!open) return
    let cancelled = false
    const fail = (cause: unknown) => {
      if (!cancelled) setError(cause instanceof Error ? cause.message : String(cause))
    }
    getSettings().then((value) => { if (!cancelled) setSettings(value) }).catch(fail)
    listAuditLogs().then((value) => { if (!cancelled) setAudit(value) }).catch(fail)
    return () => { cancelled = true }
  }, [open, getSettings, listAuditLogs])

  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') panel.close()
    }
    window.addEventListener('keydown', onKey)
    return () => { window.removeEventListener('keydown', onKey) }
  }, [open, panel])

  if (!open) return null
  const s = settings?.settings
  return (
    <div className={css.overlay} role="dialog" aria-label={t('panel.title')}>
      <div className={css.card}>
        <div className={css.header}>
          <span className={css.title}>{t('panel.title')}</span>
          <span className={css.phase}>{t('panel.phase')}</span>
        </div>
        <p className={css.intro}>{t('panel.intro')}</p>

        <div className={css.sectionTitle}>{t('panel.settings.title')}</div>
        {error !== undefined && <div className={css.error}>{t('panel.load.failed')}: {error}</div>}
        {s !== undefined && (
          <dl className={css.settingsList}>
            <dt className={css.settingsKey}>{t('panel.settings.geoMaxPages')}</dt>
            <dd>{s.geo_max_pages}</dd>
            <dt className={css.settingsKey}>{t('panel.settings.geoTimeout')}</dt>
            <dd>{s.geo_page_timeout_ms}</dd>
            <dt className={css.settingsKey}>{t('panel.settings.todo')}</dt>
            <dd>{s.sop_todo_write_enabled ? '✓' : '✗'}</dd>
            <dt className={css.settingsKey}>{t('panel.settings.defaultIcp')}</dt>
            <dd>{s.default_icp_profile_id ?? '—'}</dd>
            <dt className={css.settingsKey}>{t('panel.settings.defaultScore')}</dt>
            <dd>{s.default_score_template_id ?? '—'}</dd>
          </dl>
        )}

        <div className={css.sectionTitle}>{t('panel.audit.title')}</div>
        {audit === undefined && error === undefined
          ? <div className={css.empty}>{t('panel.audit.empty')}</div>
          : (
            <ol className={css.auditList}>
              {audit?.items.map(record => (
                <li key={record.id}>
                  [{new Date(record.created_at).toLocaleString()}] {record.source}/{record.operator_user_id}{' '}
                  {record.action} — {record.summary}
                </li>
              ))}
            </ol>
          )}

        <div className={css.closeRow}>
          <button type="button" className={css.closeButton} onClick={() => { panel.close() }}>
            {t('panel.close')}
          </button>
        </div>
      </div>
    </div>
  )
}
