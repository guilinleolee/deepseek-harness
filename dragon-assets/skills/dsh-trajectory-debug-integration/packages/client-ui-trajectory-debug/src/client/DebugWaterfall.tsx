/**
 * Waterfall view: the P0 trajectory ledger, fed entirely by the
 * `trajectoryDebug/trajectory` session projection (rows + whole-log counts).
 * Windowed rendering keeps huge ledgers smooth; `#step=<seq>` deep links
 * scroll to and highlight a row.
 */

import React, { useEffect, useMemo, useRef, useState } from 'react'
import type { TrajectoryRow } from 'dsh-trajectory-debug'
import type { ProjectionStoreLike } from './use-projections.ts'
import { useProjectionValueTyped } from './use-projections.ts'

export interface TrajectoryProjectionValue {
  rows: TrajectoryRow[]
  stepCount: number
  turnCount: number
}

const EMPTY: TrajectoryProjectionValue = { rows: [], stepCount: 0, turnCount: 0 }

function statusColor(status: string): string {
  switch (status) {
    case 'error':
      return '#e5484d'
    case 'running':
    case 'pending':
      return '#b98300'
    case 'ok':
      return '#30a46c'
    default:
      return '#8d8d8d'
  }
}

function RowLine({ row }: { row: TrajectoryRow }): React.ReactElement {
  switch (row.kind) {
    case 'turn':
      return (
        <div style={{ marginTop: 8, fontWeight: 600, borderTop: '1px solid #303030', paddingTop: 4 }}>
          Turn {row.turn}
          {row.reason !== undefined ? ` (${row.reason})` : ''}
          {row.durationMs !== undefined ? ` · ${row.durationMs}ms` : ''}
        </div>
      )
    case 'step':
      return (
        <div style={{ paddingLeft: 16, color: '#c8c8c8' }}>
          step {row.step} [{row.status}]
          {row.modelMs !== undefined ? ` · ${row.modelMs}ms` : ''}
          {row.inputTokens !== undefined ? ` · ${row.inputTokens}→${row.outputTokens} tok` : ''}
          {row.reasoningSnippet !== undefined ? ` · 💭 ${row.reasoningSnippet}` : ''}
        </div>
      )
    case 'tool': {
      const color = statusColor(row.status)
      return (
        <div style={{ paddingLeft: 32, color: '#b0b0b0', fontFamily: 'monospace', fontSize: 12 }}>
          <span style={{ color }}>{row.status === 'error' ? '✗' : row.status === 'pending' ? '…' : '✓'}</span>{' '}
          {row.name}{' '}
          <span style={{ color: '#707070' }}>
            {JSON.stringify(row.args).slice(0, 160)}
            {row.durationMs !== undefined ? ` · ${row.durationMs}ms` : ''}
          </span>
          {row.result?.code !== undefined ? <span style={{ color }}> [{row.result.code}]</span> : null}
          {row.result?.isError === true && row.result.message !== undefined ? (
            <span style={{ color: '#e5484d' }}> — {row.result.message.slice(0, 120)}</span>
          ) : null}
        </div>
      )
    }
  }
}

/** Estimated row height per kind (windowed rendering budget). */
function rowHeight(row: TrajectoryRow): number {
  switch (row.kind) {
    case 'turn':
      return 34
    case 'step':
      return 24
    case 'tool':
      return 22
  }
}

const OVERSCAN = 6
const WINDOW = 60

export interface WaterfallProps {
  projections: ProjectionStoreLike | undefined
  t: (key: string) => string
}

export function DebugWaterfall({ projections, t }: WaterfallProps): React.ReactElement {
  const { rows, stepCount, turnCount } = useProjectionValueTyped(
    projections,
    'trajectoryDebug/trajectory',
    EMPTY,
  )
  const scrollRef = useRef<HTMLDivElement | null>(null)
  const [scrollTop, setScrollTop] = useState(0)
  const [highlightSeq, setHighlightSeq] = useState<number | null>(null)

  // Precomputed row offsets for window math + deep-link scroll.
  const offsets = useMemo(() => {
    const out: number[] = new Array(rows.length)
    let acc = 0
    for (let i = 0; i < rows.length; i += 1) {
      out[i] = acc
      acc += rowHeight(rows[i]!)
    }
    return { offsets: out, total: acc }
  }, [rows])

  const start = Math.max(0, Math.floor(scrollTop / 24) - OVERSCAN)
  const end = Math.min(rows.length, start + WINDOW + OVERSCAN * 2)
  const visible = rows.slice(start, end)
  const topPad = offsets.offsets[start] ?? 0
  const bottomPad = offsets.total - (offsets.offsets[end - 1] ?? 0) - (end > 0 ? rowHeight(rows[end - 1]!) : 0)

  // Deep link: #step=<seq> → scroll + highlight.
  useEffect(() => {
    const match = /#step=(\d+)/.exec(window.location.hash)
    if (match === null || scrollRef.current === null) return
    const seq = Number(match[1])
    const index = rows.findIndex((r) => r.seq === seq)
    if (index < 0) return
    const offset = offsets.offsets[index] ?? 0
    scrollRef.current.scrollTop = Math.max(0, offset - 20)
    setHighlightSeq(seq)
    const timer = setTimeout(() => setHighlightSeq(null), 1500)
    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const openStep = (seq: number) => {
    window.location.hash = `step=${seq}`
    setHighlightSeq(seq)
    const timer = setTimeout(() => setHighlightSeq(null), 1500)
    return () => clearTimeout(timer)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, minHeight: 0 }}>
      <div style={{ opacity: 0.7, fontSize: 12 }}>
        {t('waterfall.steps').replace('{{turns}}', String(turnCount)).replace('{{steps}}', String(stepCount))}
        <span style={{ marginLeft: 8, opacity: 0.5 }}>（{rows.length} 行 · 窗口化渲染 · 点击行可深链 #step）</span>
      </div>
      <div
        ref={scrollRef}
        onScroll={(e) => setScrollTop((e.target as HTMLDivElement).scrollTop)}
        style={{ overflow: 'auto', flex: 1, paddingBottom: 16 }}
      >
        <div style={{ height: topPad }} />
        {visible.length === 0 ? (
          <div style={{ opacity: 0.5, padding: 16 }}>{t('waterfall.empty')}</div>
        ) : (
          visible.map((row) => (
            <div
              key={`${row.kind}-${row.seq}`}
              onClick={() => void openStep(row.seq)}
              style={{
                cursor: 'pointer',
                borderRadius: 4,
                background: highlightSeq === row.seq ? 'rgba(48,164,108,0.18)' : undefined,
              }}
            >
              <RowLine row={row} />
            </div>
          ))
        )}
        <div style={{ height: bottomPad }} />
      </div>
    </div>
  )
}
