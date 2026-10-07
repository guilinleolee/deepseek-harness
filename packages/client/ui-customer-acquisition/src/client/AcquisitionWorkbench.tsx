/**
 * The frame-wide P4 workbench surface occupying the `shell.overlay` hole:
 * eight pages over the Remote read faces, one shared open/close controller,
 * Escape closes, and the closed state renders null while the slot entry
 * stays mounted.
 * @module @deepseek-ai/dsh-client-ui-customer-acquisition/client/workbench
 */

import { useCallback, useEffect, useState, useSyncExternalStore } from 'react'
import type { PropsLocale } from '@deepseek-ai/dsh-client-ui-slots'
import {
  CopyPage, GeoPage, LeadsPage, OverviewPage, ScoringPage, SettingsPage, SopPage, TemplatesPage,
} from './views.tsx'
import type { WorkbenchInjected } from './injected.ts'
import css from './panel.module.css'

/** Full surface props: the injected server reads plus the locale seat. */
export type AcquisitionWorkbenchProps = WorkbenchInjected & PropsLocale<'customer-acquisition'>

/** The page order and identity of the workbench tabs. */
const PAGES = ['overview', 'leads', 'scoring', 'geo', 'copy', 'sop', 'templates', 'settings'] as const

/** One workbench page id. */
export type WorkbenchPage = (typeof PAGES)[number]

/**
 * Render the eight-page acquisition workbench.
 * @param props - the injected server reads, the shared controller, and the locale seat.
 * @returns the overlay element tree, or `null` while closed.
 */
export function AcquisitionWorkbench(props: AcquisitionWorkbenchProps) {
  const { panel, t } = props
  const subscribe = useCallback((listener: () => void) => panel.subscribe(listener), [panel])
  const getOpenState = useCallback(() => panel.isOpen(), [panel])
  const open = useSyncExternalStore(subscribe, getOpenState)
  const [page, setPage] = useState<WorkbenchPage>('overview')

  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') panel.close()
    }
    window.addEventListener('keydown', onKey)
    return () => { window.removeEventListener('keydown', onKey) }
  }, [open, panel])

  if (!open) return null
  return (
    <div className={css.overlay} role="dialog" aria-label={t('panel.title')}>
      <div className={css.card}>
        <div className={css.header}>
          <span className={css.title}>{t('panel.title')}</span>
          <button type="button" className={css.closeButton} onClick={() => { panel.close() }}>
            {t('panel.close')}
          </button>
        </div>
        <nav className={css.tabRow} aria-label={t('panel.title')}>
          {PAGES.map(id => (
            <button
              key={id}
              type="button"
              className={css.tabButton}
              aria-pressed={page === id}
              onClick={() => { setPage(id) }}
            >
              {t(`page.${id}`)}
            </button>
          ))}
        </nav>
        <div className={css.pageBody}>
          {page === 'overview' && <OverviewPage getOverview={props.getOverview} t={t} />}
          {page === 'leads' && <LeadsPage listLeads={props.listLeads} t={t} />}
          {page === 'scoring' && (
            <ScoringPage
              listScoreRuns={props.listScoreRuns}
              listIcpProfiles={props.listIcpProfiles}
              listScoreTemplates={props.listScoreTemplates}
              t={t}
            />
          )}
          {page === 'geo' && <GeoPage listGeoScans={props.listGeoScans} getGeoReport={props.getGeoReport} t={t} />}
          {page === 'copy' && (
            <CopyPage
              listGeneratedContents={props.listGeneratedContents}
              listContentTemplates={props.listContentTemplates}
              t={t}
            />
          )}
          {page === 'sop' && (
            <SopPage listSopTasks={props.listSopTasks} listSopTemplates={props.listSopTemplates} t={t} />
          )}
          {page === 'templates' && (
            <TemplatesPage
              listIcpProfiles={props.listIcpProfiles}
              listScoreTemplates={props.listScoreTemplates}
              listContentTemplates={props.listContentTemplates}
              listSopTemplates={props.listSopTemplates}
              t={t}
            />
          )}
          {page === 'settings' && (
            <SettingsPage
              getSettings={props.getSettings}
              updateSettings={props.updateSettings}
              listAuditLogs={props.listAuditLogs}
              t={t}
            />
          )}
        </div>
      </div>
    </div>
  )
}
