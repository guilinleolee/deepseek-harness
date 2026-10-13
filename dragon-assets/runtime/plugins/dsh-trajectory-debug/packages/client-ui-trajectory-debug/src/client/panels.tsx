/**
 * Debug console panels: deterministic replay, breakpoints, edit-and-rerun and
 * fork compare. All four call the host through the webserver RPC transport
 * (`POST /api/trajectory-debug/rpc`) — the typert-free browser channel.
 */

import React, { useCallback, useEffect, useState } from 'react'
import type { CompareResult, ReplayCursor, StepContext, ToolCallRecord, Variant } from 'dsh-trajectory-debug'
import { rpc } from './rpc.ts'

const btnStyle: React.CSSProperties = {
  background: '#2a2a2a',
  border: '1px solid #3a3a3a',
  borderRadius: 6,
  padding: '3px 10px',
  color: '#ddd',
  cursor: 'pointer',
  fontSize: 12,
  marginRight: 6,
}
const inputStyle: React.CSSProperties = {
  background: '#1b1b1b',
  border: '1px solid #3a3a3a',
  borderRadius: 6,
  padding: '3px 8px',
  color: '#ddd',
  fontSize: 12,
  fontFamily: 'monospace',
  width: 180,
  marginRight: 6,
}
const labelStyle: React.CSSProperties = { fontSize: 12, opacity: 0.7, marginBottom: 4 }

function toolLines(tools: readonly ToolCallRecord[]): string[] {
  return tools.map((tool) =>
    `${tool.status === 'error' ? '✗' : '✓'} ${tool.name} ${JSON.stringify(tool.args).slice(0, 140)}${tool.result?.code !== undefined ? ` [${tool.result.code}]` : ''}`,
  )
}

export function ReplayPanel({ sessionId }: { sessionId: string }): React.ReactElement {
  const [cursor, setCursor] = useState<ReplayCursor | null>(null)
  const [context, setContext] = useState<StepContext | null>(null)
  const [status, setStatus] = useState<string>('idle')
  const [error, setError] = useState<string | null>(null)

  const run = useCallback(
    async (action: () => Promise<unknown>) => {
      setError(null)
      try {
        await action()
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e))
      }
    },
    [],
  )

  const start = () =>
    run(async () => {
      const c = await rpc<ReplayCursor>('replay.start', { sessionId })
      setCursor(c)
      setContext(null)
      setStatus('started')
    })
  const step = () =>
    run(async () => {
      if (cursor === null) return start()
      const frame = await rpc<{ status: string; context?: StepContext; cursor: ReplayCursor }>('replay.step', { cursor })
      setCursor(frame.cursor)
      setContext(frame.context ?? null)
      setStatus(frame.status)
    })
  const seek = (index: number) =>
    run(async () => {
      if (cursor === null) return
      const frame = await rpc<{ status: string; context?: StepContext; cursor: ReplayCursor }>('replay.seek', {
        cursor,
        stepIndex: index,
      })
      setCursor(frame.cursor)
      setContext(frame.context ?? null)
      setStatus(frame.status)
    })

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={labelStyle}>确定性回放（零 Token，纯日志投影）</div>
      <div>
        <button type="button" style={btnStyle} onClick={start}>开始</button>
        <button type="button" style={btnStyle} onClick={step}>下一步</button>
        <button type="button" style={btnStyle} onClick={() => seek(0)}>跳到 0</button>
        <span style={{ fontSize: 12, opacity: 0.6 }}>
          {cursor === null ? '未开始' : `step ${cursor.stepIndex} · ${status}`}
        </span>
      </div>
      {context !== null && (
        <pre
          style={{
            background: '#161616',
            border: '1px solid #2a2a2a',
            borderRadius: 6,
            padding: 8,
            fontSize: 11,
            overflow: 'auto',
            maxHeight: 180,
          }}
        >
          {`seq ${context.seq} · 模型视角 ${context.modelView.length} 条消息`}
          {toolLines(context.action.tools).join('\n')}
        </pre>
      )}
      {error !== null && <div style={{ color: '#e5484d', fontSize: 12 }}>{error}</div>}
    </div>
  )
}

export function BreakpointPanel({ sessionId }: { sessionId: string }): React.ReactElement {
  const [items, setItems] = useState<Array<{ id: string; spec: { at: string; seq?: number; turn?: number } }>>([])
  const [seq, setSeq] = useState('')
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(() => {
    rpc<unknown[]>('breakpoint.list', { sessionId })
      .then((list) => setItems(list as Array<{ id: string; spec: { at: string; seq?: number; turn?: number } }>))
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
  }, [sessionId])

  useEffect(refresh, [refresh])

  const add = () => {
    const n = parseInt(seq, 10)
    if (!Number.isFinite(n)) return
    rpc<string>('breakpoint.set', { sessionId, spec: { at: 'step', seq: n } })
      .then(() => {
        setSeq('')
        refresh()
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
  }
  const remove = (id: string) =>
    rpc<null>('breakpoint.remove', { sessionId, id }).then(refresh).catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={labelStyle}>断点（step 边界；命中后 agent 暂停，浏览器/命令可 resume）</div>
      <div>
        <input style={inputStyle} placeholder="seq" value={seq} onChange={(e) => setSeq(e.target.value)} />
        <button type="button" style={btnStyle} onClick={add}>添加</button>
        <button type="button" style={btnStyle} onClick={() => rpc<null>('breakpoint.resume', { sessionId, cause: 'user' })}>resume</button>
      </div>
      {items.map((item) => (
        <div key={item.id} style={{ fontSize: 12, fontFamily: 'monospace', marginTop: 2 }}>
          {item.id} · {item.spec.at === 'step' ? `step@${item.spec.seq}` : `turn@${item.spec.turn}`}
          <button type="button" style={{ ...btnStyle, marginLeft: 8, fontSize: 11 }} onClick={() => remove(item.id)}>删除</button>
        </div>
      ))}
      {error !== null && <div style={{ color: '#e5484d', fontSize: 12 }}>{error}</div>}
    </div>
  )
}

export function RerunPanel({ sessionId }: { sessionId: string }): React.ReactElement {
  const [seq, setSeq] = useState('')
  const [args, setArgs] = useState('{}')
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const rerun = () => {
    const n = parseInt(seq, 10)
    if (!Number.isFinite(n)) return
    let editedArgs: unknown
    try {
      editedArgs = JSON.parse(args)
    } catch {
      setError('args 不是合法 JSON')
      return
    }
    rpc<{ toolName: string; newResult?: { isError: boolean; code?: string; message?: string; value?: unknown } }>(
      'intervention.rerunTool',
      { sessionId, seq: n, editedArgs },
    )
      .then((record) => {
        setResult(`${record.toolName} → ${JSON.stringify(record.newResult ?? null).slice(0, 400)}`)
        setError(null)
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
  }

  return (
    <div>
      <div style={labelStyle}>改参重跑（策略 record|sandbox|ask 由 host 配置决定）</div>
      <div>
        <input style={inputStyle} placeholder="tool/call seq" value={seq} onChange={(e) => setSeq(e.target.value)} />
        <input style={{ ...inputStyle, width: 240 }} placeholder='{"url": "…"}' value={args} onChange={(e) => setArgs(e.target.value)} />
        <button type="button" style={btnStyle} onClick={rerun}>重跑</button>
      </div>
      {result !== null && <pre style={{ fontSize: 11, background: '#161616', padding: 6, borderRadius: 6 }}>{result}</pre>}
      {error !== null && <div style={{ color: '#e5484d', fontSize: 12 }}>{error}</div>}
    </div>
  )
}

export function ComparePanel({ sessionId }: { sessionId: string }): React.ReactElement {
  const [variants, setVariants] = useState<Variant[]>([])
  const [base, setBase] = useState('')
  const [head, setHead] = useState('')
  const [result, setResult] = useState<CompareResult | null>(null)
  const [forkSeq, setForkSeq] = useState('')
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(() => {
    rpc<Variant[]>('variant.list', { sessionId })
      .then((list) => {
        setVariants(list)
        if (list.length >= 2) {
          setBase((b) => b || list[0]!.id)
          setHead((h) => h || list[1]!.id)
        }
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
  }, [sessionId])

  useEffect(refresh, [refresh])

  const fork = () => {
    const n = parseInt(forkSeq, 10)
    if (!Number.isFinite(n)) return
    rpc<Variant>('variant.fork', { sessionId, req: { boundarySeq: n, label: `fork@${n}` } })
      .then(() => {
        setForkSeq('')
        refresh()
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
  }
  const compare = () => {
    if (base === '' || head === '' || base === head) return
    rpc<CompareResult>('variant.compare', { base, head })
      .then(setResult)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
  }

  return (
    <div>
      <div style={labelStyle}>分叉对比（先在瀑布流选一个 step 分叉，再对比两个分支）</div>
      <div>
        <input style={inputStyle} placeholder="分叉 boundary seq" value={forkSeq} onChange={(e) => setForkSeq(e.target.value)} />
        <button type="button" style={btnStyle} onClick={fork}>分叉</button>
        <select style={inputStyle} value={base} onChange={(e) => setBase(e.target.value)}>
          <option value="">base…</option>
          {variants.map((v) => (
            <option key={v.id} value={v.id}>{v.label} ({v.status})</option>
          ))}
        </select>
        <select style={inputStyle} value={head} onChange={(e) => setHead(e.target.value)}>
          <option value="">head…</option>
          {variants.map((v) => (
            <option key={v.id} value={v.id}>{v.label} ({v.status})</option>
          ))}
        </select>
        <button type="button" style={btnStyle} onClick={compare}>对比</button>
      </div>
      {result !== null && (
        <div style={{ fontSize: 12, marginTop: 8 }}>
          <div style={{ opacity: 0.85 }}>{result.summary}</div>
          {result.toolsChanged.map((t, i) => (
            <div key={i} style={{ fontFamily: 'monospace', fontSize: 11, marginTop: 2 }}>
              step {t.step} · {t.kind}: {t.diff.join('; ')}
            </div>
          ))}
          {result.resultDiffs.map((d, i) => (
            <div key={`r${i}`} style={{ fontFamily: 'monospace', fontSize: 11, marginTop: 2 }}>
              step {d.step} result: {d.basePreview.slice(0, 60)} → {d.headPreview.slice(0, 60)}
            </div>
          ))}
        </div>
      )}
      {error !== null && <div style={{ color: '#e5484d', fontSize: 12 }}>{error}</div>}
    </div>
  )
}
