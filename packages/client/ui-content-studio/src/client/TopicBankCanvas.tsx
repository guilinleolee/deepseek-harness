/**
 * The idea wall: the topic bank's canvas face. Topics render as draggable
 * cards on one pannable, zoomable world; a keyword pulls matching cards into
 * a dense cluster around the world center. Positions persist through the
 * topic upsert (the `layout` field); the keyword cluster is display-only.
 * Geometry lives in the pure `topic-bank.ts` module; this surface only
 * orchestrates pointer state.
 */
import { useRef, useState, type PointerEvent } from 'react'
import { clsx } from 'clsx'
import type { TopicItem, TopicLayout } from '@deepseek-ai/dsh-content-topics/types'
import type { PropsLocale } from '@deepseek-ai/dsh-client-ui-slots'
import {
  TOPIC_CANVAS_SIZE, TOPIC_CANVAS_ZOOM, canvasPlacements, clampCanvasPosition, gatheredCanvasPlacements,
} from './topic-bank.ts'
import tb from './TopicBankView.module.css'

/** The pointer interaction in flight: which card, and where the grab started. */
interface CardDrag {
  readonly id: TopicItem['id']
  readonly grabX: number
  readonly grabY: number
}

/** The background pan in flight. */
interface CanvasPan {
  readonly startX: number
  readonly startY: number
  readonly originX: number
  readonly originY: number
}

/** Injected face of the idea wall. */
export interface TopicBankCanvasProps {
  readonly items: readonly TopicItem[]
  /** Persist one card's dragged position through the topics upsert. */
  readonly onMove: (item: TopicItem, position: TopicLayout) => void | Promise<void>
  readonly t: PropsLocale<'content-studio'>['t']
}

/**
 * Render the idea wall over the given topics.
 * @param props - the visible topics, the move face, and the locale seat.
 * @returns the canvas element tree.
 */
export function TopicBankCanvas({ items, onMove, t }: TopicBankCanvasProps) {
  const [keyword, setKeyword] = useState('')
  const [zoom, setZoom] = useState(0.8)
  const [offset, setOffset] = useState({ x: 0, y: 0 })
  const [drafts, setDrafts] = useState<Readonly<Record<string, TopicLayout>>>({})
  const [drag, setDrag] = useState<CardDrag | null>(null)
  const [pan, setPan] = useState<CanvasPan | null>(null)
  const viewportRef = useRef<HTMLDivElement | null>(null)

  const anchor = { x: TOPIC_CANVAS_SIZE.width / 2, y: TOPIC_CANVAS_SIZE.height / 2 }
  const placed = gatheredCanvasPlacements(canvasPlacements(items), keyword, anchor)

  /** Convert one viewport (client) coordinate into world coordinates under the current pan and zoom. */
  function viewportToWorld(clientX: number, clientY: number): TopicLayout {
    const rect = viewportRef.current?.getBoundingClientRect()
    const left = rect === undefined ? 0 : clientX - rect.left
    const top = rect === undefined ? 0 : clientY - rect.top
    return { x: (left - offset.x) / zoom, y: (top - offset.y) / zoom }
  }

  const startCardDrag = (event: PointerEvent, item: TopicItem, position: TopicLayout): void => {
    event.stopPropagation()
    const world = viewportToWorld(event.clientX, event.clientY)
    setDrag({ id: item.id, grabX: world.x - position.x, grabY: world.y - position.y })
    ;(event.target as HTMLElement).setPointerCapture(event.pointerId)
  }

  const moveCardDrag = (event: PointerEvent): void => {
    if (drag === null) return
    const world = viewportToWorld(event.clientX, event.clientY)
    const next = clampCanvasPosition({ x: world.x - drag.grabX, y: world.y - drag.grabY })
    setDrafts(current => ({ ...current, [drag.id]: next }))
  }

  const endCardDrag = (item: TopicItem): void => {
    setDrag(null)
    const moved = drafts[item.id]
    if (moved === undefined) return
    setDrafts((current) => {
      const next: Record<string, TopicLayout> = {}
      for (const [key, value] of Object.entries(current)) {
        if (key !== item.id) next[key] = value
      }
      return next
    })
    void onMove(item, moved)
  }

  const startPan = (event: PointerEvent): void => {
    if (drag !== null) return
    setPan({ startX: event.clientX, startY: event.clientY, originX: offset.x, originY: offset.y })
    ;(event.currentTarget as HTMLElement).setPointerCapture(event.pointerId)
  }

  const movePan = (event: PointerEvent): void => {
    if (pan === null) return
    setOffset({ x: pan.originX + event.clientX - pan.startX, y: pan.originY + event.clientY - pan.startY })
  }

  return (
    <div>
      <div className={tb.canvasToolbar}>
        <input
          className={tb.control}
          value={keyword}
          placeholder={t('topicBank.canvas.keyword')}
          aria-label={t('topicBank.canvas.keyword')}
          onChange={(event) => { setKeyword(event.target.value) }}
        />
        <span className={tb.canvasHint}>{t('topicBank.canvas.hint')}</span>
        <button type="button" className={tb.btn} aria-label={t('topicBank.canvas.zoomOut')} onClick={() => { setZoom(current => Math.max(TOPIC_CANVAS_ZOOM.min, current - TOPIC_CANVAS_ZOOM.step)) }}>
          −
        </button>
        <span className={tb.canvasZoom}>{Math.round(zoom * 100)}%</span>
        <button type="button" className={tb.btn} aria-label={t('topicBank.canvas.zoomIn')} onClick={() => { setZoom(current => Math.min(TOPIC_CANVAS_ZOOM.max, current + TOPIC_CANVAS_ZOOM.step)) }}>
          +
        </button>
        <button type="button" className={tb.btn} onClick={() => { setZoom(0.8); setOffset({ x: 0, y: 0 }) }}>{t('topicBank.canvas.reset')}</button>
      </div>
      <div
        ref={viewportRef}
        className={clsx(tb.canvasViewport, pan !== null && tb.canvasPanning)}
        onPointerDown={startPan}
        onPointerMove={movePan}
        onPointerUp={() => { setPan(null) }}
        onPointerLeave={() => { setPan(null) }}
      >
        <div
          className={tb.canvasWorld}
          style={{
            width: TOPIC_CANVAS_SIZE.width,
            height: TOPIC_CANVAS_SIZE.height,
            transform: `translate(${offset.x}px, ${offset.y}px) scale(${zoom})`,
          }}
        >
          {placed.map(({ item, position }) => {
            const show = drafts[item.id] ?? position
            const dragging = drag !== null && drag.id === item.id
            return (
              <div
                key={item.id}
                className={clsx(tb.canvasCard, dragging && tb.canvasCardDragging)}
                style={{ left: show.x, top: show.y }}
                onPointerDown={(event) => { startCardDrag(event, item, position) }}
                onPointerMove={(event) => { moveCardDrag(event) }}
                onPointerUp={() => { endCardDrag(item) }}
              >
                <div className={tb.canvasCardTitle}>{item.title}</div>
                {item.oneLiner !== null && <div className={tb.canvasCardPitch}>{item.oneLiner}</div>}
                {item.tags.length > 0 && <div className={tb.canvasCardTags}>{item.tags.join(' · ')}</div>}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
