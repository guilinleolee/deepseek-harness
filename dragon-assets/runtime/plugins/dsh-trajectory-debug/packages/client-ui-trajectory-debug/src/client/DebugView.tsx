/**
 * Debug view: waterfall + performance dashboard (projection-fed) and the
 * debug console (replay / breakpoints / edit-and-rerun / fork compare) via
 * the webserver RPC transport.
 */

import React, { useState } from 'react'
import type { ProjectionStoreLike } from './use-projections.ts'
import { DebugWaterfall } from './DebugWaterfall.tsx'
import { PerfDashboard } from './PerfDashboard.tsx'
import { BreakpointPanel, ComparePanel, RerunPanel, ReplayPanel } from './panels.tsx'

export interface DebugViewProps {
  /** Per-session projection store (injected by the slot registration). */
  projections?: ProjectionStoreLike
  /** Session id (injected; used by the RPC panels). */
  sessionId?: string
  /** Locale translate seat provided by the view runtime (ConvViewProps). */
  t?: (key: string) => string
}

type Mode = 'waterfall' | 'perf' | 'replay' | 'compare'

const identityT = (key: string): string => key

export function DebugView({ projections, sessionId, t = identityT }: DebugViewProps): React.ReactElement {
  const [mode, setMode] = useState<Mode>('waterfall')
  const tabs: Array<{ id: Mode; label: string }> = [
    { id: 'waterfall', label: '瀑布流' },
    { id: 'perf', label: t('perf.title') },
    { id: 'replay', label: t('replay.title') },
    { id: 'compare', label: '对比' },
  ]
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        minHeight: 0,
        padding: 12,
        fontFamily: 'system-ui, sans-serif',
        fontSize: 13,
      }}
    >
      <div style={{ display: 'flex', gap: 6, marginBottom: 8, flexWrap: 'wrap' }}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setMode(tab.id)}
            style={{
              background: mode === tab.id ? '#2a2a2a' : 'transparent',
              border: '1px solid #3a3a3a',
              borderRadius: 6,
              padding: '4px 10px',
              color: '#ddd',
              cursor: 'pointer',
              fontSize: 12,
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {projections === undefined ? (
        <div style={{ opacity: 0.6, padding: 16 }}>{t('session.unavailable')}</div>
      ) : mode === 'waterfall' ? (
        <DebugWaterfall projections={projections} t={t} />
      ) : mode === 'perf' ? (
        <PerfDashboard projections={projections} t={t} />
      ) : mode === 'replay' ? (
        <div style={{ overflow: 'auto', flex: 1, paddingBottom: 16 }}>
          <ReplayPanel sessionId={sessionId ?? ''} />
          <BreakpointPanel sessionId={sessionId ?? ''} />
          <RerunPanel sessionId={sessionId ?? ''} />
        </div>
      ) : (
        <div style={{ overflow: 'auto', flex: 1, paddingBottom: 16 }}>
          <ComparePanel sessionId={sessionId ?? ''} />
        </div>
      )}
    </div>
  )
}
