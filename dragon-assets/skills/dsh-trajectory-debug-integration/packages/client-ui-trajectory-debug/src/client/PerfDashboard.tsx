/**
 * Performance dashboard: KPI cards + per-tool bars + failure classification,
 * fed entirely by the `trajectoryDebug/perf` session projection.
 */

import React from 'react'
import type { PerfSnapshot } from 'dsh-trajectory-debug'
import type { ProjectionStoreLike } from './use-projections.ts'
import { useProjectionValueTyped } from './use-projections.ts'

function Kpi({ label, value }: { label: string; value: string }): React.ReactElement {
  return (
    <div style={{ border: '1px solid #303030', borderRadius: 6, padding: '8px 12px', minWidth: 110 }}>
      <div style={{ fontSize: 11, opacity: 0.6 }}>{label}</div>
      <div style={{ fontSize: 16, fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>{value}</div>
    </div>
  )
}

export interface PerfDashboardProps {
  projections: ProjectionStoreLike | undefined
  t: (key: string) => string
}

export function PerfDashboard({ projections, t }: PerfDashboardProps): React.ReactElement {
  const perf = useProjectionValueTyped<PerfSnapshot | undefined>(projections, 'trajectoryDebug/perf', undefined)
  if (perf === undefined || perf.turns.steps === 0) {
    return <div style={{ opacity: 0.5, padding: 16 }}>{t('perf.noData')}</div>
  }
  const toolEntries = Object.entries(perf.tools).sort((a, b) => b[1].calls - a[1].calls)
  const maxCalls = Math.max(1, ...toolEntries.map(([, v]) => v.calls))
  const totalTokens = perf.tokens.totalInput + perf.tokens.totalOutput
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <Kpi label={t('perf.steps')} value={String(perf.turns.steps)} />
        <Kpi label={t('perf.turns')} value={String(perf.turns.count)} />
        <Kpi label={t('perf.tokens')} value={String(totalTokens)} />
        <Kpi label={t('perf.llmMs')} value={`${Math.round(perf.timing.llmMs)}ms`} />
        <Kpi label={t('perf.toolMs')} value={`${Math.round(perf.timing.toolMs)}ms`} />
      </div>

      <div>
        <div style={{ fontSize: 12, opacity: 0.7, marginBottom: 4 }}>{t('perf.toolCalls')}</div>
        {toolEntries.length === 0 ? (
          <div style={{ opacity: 0.5 }}>—</div>
        ) : (
          toolEntries.map(([name, v]) => (
            <div key={name} style={{ marginBottom: 4 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'monospace', fontSize: 12 }}>
                <span>
                  {name} · {v.calls} calls · {v.failed} failed · p50 {v.ms.p50}ms
                </span>
                <span style={{ opacity: 0.6 }}>
                  {((v.ok / Math.max(1, v.calls)) * 100).toFixed(0)}%
                </span>
              </div>
              <div style={{ background: '#222', borderRadius: 3, height: 6 }}>
                <div
                  style={{
                    background: v.failed > 0 ? '#e5484d' : '#30a46c',
                    height: 6,
                    borderRadius: 3,
                    width: `${Math.max(2, (v.calls / maxCalls) * 100)}%`,
                  }}
                />
              </div>
            </div>
          ))
        )}
      </div>

      {perf.failures.length > 0 ? (
        <div>
          <div style={{ fontSize: 12, opacity: 0.7, marginBottom: 4 }}>{t('perf.failures')}</div>
          {perf.failures.map((f, i) => (
            <div key={i} style={{ fontFamily: 'monospace', fontSize: 12, color: '#e5484d' }}>
              {JSON.stringify(f.category)} × {f.count}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  )
}
