/**
 * The cover compositor: typesets a cover plan's big title over the rendered
 * cover image and exports one 1920×1080 file.
 *
 * A provider renders pictures, not legible type: every image model asked to
 * "write the title on the cover" returns glyph-shaped noise. So the title is
 * not part of the image prompt — the workbench draws it here, deterministically,
 * over whatever the provider returned. Without a rendered image the same
 * routine paints a gradient card, so a cover is always available.
 *
 * Layout is pure and tested against a measuring stub; `paintCover` takes a
 * structural subset of `CanvasRenderingContext2D` so it runs under the test
 * lane without a real canvas.
 */

/** Width of the exported cover, in pixels. */
export const COVER_WIDTH = 1920

/** Height of the exported cover, in pixels. */
export const COVER_HEIGHT = 1080

/** Widest line the title may occupy, leaving the export's side margins. */
const COVER_TEXT_WIDTH = COVER_WIDTH - 200

/** Baselines sit this far above the bottom edge. */
const COVER_TEXT_BOTTOM = 100

/** Line height as a multiple of the font size. */
const COVER_LINE_HEIGHT = 1.24

/** The largest title size, used while the title fits on one or two lines. */
const COVER_FONT_LARGE = 148

/** The reduced title size for a long title. */
const COVER_FONT_SMALL = 112

/** Unit width above which the title switches to the reduced size. */
const COVER_LONG_UNITS = 12

/** A latin letter is roughly this wide against one CJK character. */
const COVER_LATIN_UNIT = 0.55

/** Most lines the title may occupy; anything past this is dropped, not shrunk. */
const COVER_MAX_LINES = 3

/** The cover title as typeset: its lines and the size they are drawn at. */
export interface CoverTextLayout {
  /** The wrapped lines, top to bottom; empty when the title is empty. */
  readonly lines: readonly string[]
  /** The pixel size the lines are drawn at. */
  readonly fontSize: number
}

/**
 * The width one character counts as, relative to a CJK character.
 * @param character - one character of the title.
 * @returns the relative width.
 */
function unitWidth(character: string): number {
  return /[\u0000-\u024f]/u.test(character) ? COVER_LATIN_UNIT : 1
}

/**
 * The title's width in CJK-character units, which decides its font size.
 * @param text - the cover title.
 * @returns the summed unit width.
 */
export function coverTextUnits(text: string): number {
  let units = 0
  for (const character of text) units += unitWidth(character)
  return units
}

/**
 * Split one over-wide row between characters, the last resort for a token with
 * no break opportunity.
 * @param row - one non-empty row.
 * @param measure - the width of one candidate part.
 * @param maxWidth - the widest part allowed.
 * @returns the parts, in order.
 */
function splitRow(row: string, measure: (line: string) => number, maxWidth: number): string[] {
  const parts: string[] = []
  let part = ''
  for (const character of row) {
    if (part.length > 0 && measure(part + character) > maxWidth) {
      parts.push(part)
      part = character
    } else {
      part += character
    }
  }
  parts.push(part)
  return parts
}

/**
 * Split the title into drawn lines. Latin runs break at spaces; a CJK run has
 * no spaces, so it breaks between characters once a line is full, and a single
 * over-wide token is split character by character as a last resort.
 * @param text - the cover title.
 * @param measure - the width of one candidate line at the chosen font size.
 * @param maxWidth - the widest line allowed.
 * @param maxLines - the most lines kept.
 * @returns the wrapped lines, none of them blank.
 */
export function wrapCoverText(
  text: string,
  measure: (line: string) => number,
  maxWidth: number,
  maxLines: number,
): string[] {
  const tokens = text.match(/[\u0021-\u024f]+\s*|\s+|[^\s]/gu) ?? []
  const rows: string[] = []
  let line = ''
  const flush = (): void => {
    const trimmed = line.trimEnd()
    if (trimmed.length > 0) rows.push(trimmed)
    line = ''
  }
  for (const token of tokens) {
    if (measure((line + token).trimEnd()) <= maxWidth || line.trim().length === 0) {
      line += token
      continue
    }
    flush()
    line = token.trimStart()
  }
  flush()
  const wrapped: string[] = []
  for (const row of rows) {
    if (measure(row) <= maxWidth) {
      wrapped.push(row)
      continue
    }
    wrapped.push(...splitRow(row, measure, maxWidth))
  }
  return wrapped.slice(0, maxLines)
}

/**
 * Typeset the cover title: pick the font size from its unit width, then wrap
 * it at that size.
 * @param text - the cover title.
 * @param measureAt - the width of one candidate line at a given font size.
 * @returns the lines and the size they are drawn at.
 */
export function layoutCoverText(
  text: string,
  measureAt: (line: string, fontSize: number) => number,
): CoverTextLayout {
  const trimmed = text.trim()
  if (trimmed.length === 0) return { lines: [], fontSize: COVER_FONT_LARGE }
  const fontSize = coverTextUnits(trimmed) > COVER_LONG_UNITS ? COVER_FONT_SMALL : COVER_FONT_LARGE
  return {
    lines: wrapCoverText(trimmed, line => measureAt(line, fontSize), COVER_TEXT_WIDTH, COVER_MAX_LINES),
    fontSize,
  }
}

/** One gradient stop the compositor paints. */
export type CoverGradientStop = readonly [offset: number, color: string]

/**
 * The canvas operations the cover needs. `CanvasRenderingContext2D` satisfies
 * this structurally; the test lane supplies a recording stub instead.
 */
export interface CoverCanvas {
  /** Whether an image may be drawn; absent on a text-only export. */
  drawImage?: (source: unknown, x: number, y: number, width: number, height: number) => void
  fillRect: (x: number, y: number, width: number, height: number) => void
  fillText: (text: string, x: number, y: number) => void
  measureText: (text: string) => { readonly width: number }
  createLinearGradient: (x0: number, y0: number, x1: number, y1: number) => {
    addColorStop: (offset: number, color: string) => void
  }
  createRadialGradient: (
    x0: number, y0: number, r0: number, x1: number, y1: number, r1: number,
  ) => { addColorStop: (offset: number, color: string) => void }
  /** Properties set by the compositor; typed loosely so a stub need not model them all. */
  [property: string]: unknown
}

/** What the compositor draws: the title text and, optionally, the rendered image. */
export interface CoverComposeOptions {
  /** The big title drawn on the cover; an empty value paints the background alone. */
  readonly text: string
  /** The provider's rendered image, when one exists. */
  readonly image?: { readonly source: unknown; readonly width: number; readonly height: number } | undefined
}

/** The background gradient painted when no image fills the frame. */
const COVER_BASE_STOPS: readonly CoverGradientStop[] = [
  [0, '#1a1b3a'],
  [0.55, '#4a2f6b'],
  [1, '#d9745a'],
]

/** The score behind the title, so light artwork keeps the type readable. */
const COVER_SHADE_STOPS: readonly CoverGradientStop[] = [
  [0, 'rgba(0, 0, 0, 0)'],
  [1, 'rgba(0, 0, 0, .72)'],
]

/** The font stack the title is set in. */
const COVER_FONT_STACK = '"Songti SC", "STSong", "Noto Serif SC", serif'

/**
 * Paint the background: the artwork cover-fitted when present, otherwise the
 * gradient card. A fitted image also gets the bottom shade the title sits on.
 * @param ctx - the canvas operations.
 * @param image - the rendered image, when one exists.
 */
function paintCoverBackground(ctx: CoverCanvas, image: CoverComposeOptions['image']): void {
  const base = ctx.createLinearGradient(0, 0, COVER_WIDTH, COVER_HEIGHT)
  for (const [offset, color] of COVER_BASE_STOPS) base.addColorStop(offset, color)
  ctx.fillStyle = base
  ctx.fillRect(0, 0, COVER_WIDTH, COVER_HEIGHT)
  const glow = ctx.createRadialGradient(
    COVER_WIDTH * 0.8, COVER_HEIGHT * 0.15, 0,
    COVER_WIDTH * 0.8, COVER_HEIGHT * 0.15, COVER_WIDTH * 0.6,
  )
  glow.addColorStop(0, 'rgba(255, 196, 150, .55)')
  glow.addColorStop(1, 'rgba(255, 196, 150, 0)')
  ctx.fillStyle = glow
  ctx.fillRect(0, 0, COVER_WIDTH, COVER_HEIGHT)
  if (image === undefined || ctx.drawImage === undefined) return
  // Cover-fit: scale to fill, then centre the overflow.
  const scale = Math.max(COVER_WIDTH / image.width, COVER_HEIGHT / image.height)
  const width = image.width * scale
  const height = image.height * scale
  ctx.drawImage(image.source, (COVER_WIDTH - width) / 2, (COVER_HEIGHT - height) / 2, width, height)
  const shade = ctx.createLinearGradient(0, COVER_HEIGHT * 0.35, 0, COVER_HEIGHT)
  for (const [offset, color] of COVER_SHADE_STOPS) shade.addColorStop(offset, color)
  ctx.fillStyle = shade
  ctx.fillRect(0, 0, COVER_WIDTH, COVER_HEIGHT)
}

/**
 * Paint the whole cover onto one context: background, then the typeset title
 * with its shadow, bottom-aligned.
 * @param ctx - the canvas operations.
 * @param options - the title text and the optional rendered image.
 * @returns the layout that was drawn, so the caller can size or log it.
 */
export function paintCover(ctx: CoverCanvas, options: CoverComposeOptions): CoverTextLayout {
  paintCoverBackground(ctx, options.image)
  const layout = layoutCoverText(options.text, (line, fontSize) => {
    ctx.font = `700 ${fontSize}px ${COVER_FONT_STACK}`
    return ctx.measureText(line).width
  })
  if (layout.lines.length === 0) return layout
  ctx.font = `700 ${layout.fontSize}px ${COVER_FONT_STACK}`
  ctx.fillStyle = '#fff'
  ctx.textBaseline = 'alphabetic'
  ctx.shadowColor = 'rgba(0, 0, 0, .35)'
  ctx.shadowBlur = 24
  const lineHeight = layout.fontSize * COVER_LINE_HEIGHT
  layout.lines.forEach((line, index) => {
    const baseline = COVER_HEIGHT - COVER_TEXT_BOTTOM - (layout.lines.length - 1 - index) * lineHeight
    ctx.fillText(line, 100, baseline)
  })
  return layout
}

/**
 * Paint a cover onto a real 2D context, loading the rendered image first.
 * The data URL the structure panel already holds is the image source, so no
 * second asset read is needed.
 * @param ctx - the real canvas context.
 * @param text - the big title drawn on the cover.
 * @param imageDataUrl - the rendered cover image as a data URL, or null for the gradient card.
 * @returns the layout that was drawn.
 */
export async function paintCoverElement(
  ctx: CanvasRenderingContext2D,
  text: string,
  imageDataUrl: string | null,
): Promise<CoverTextLayout> {
  const image = imageDataUrl === null ? null : await loadCoverImage(imageDataUrl)
  return paintCover(ctx as unknown as CoverCanvas, {
    text,
    image: image === null ? undefined : { source: image.element, width: image.width, height: image.height },
  })
}

/**
 * Load one rendered cover image for the compositor.
 * @param dataUrl - the image as a data URL.
 * @returns the decoded element and its intrinsic size.
 * @throws when the browser cannot decode the image.
 */
function loadCoverImage(dataUrl: string): Promise<{ element: HTMLImageElement; width: number; height: number }> {
  return new Promise((resolve, reject) => {
    const element = new Image()
    element.onload = () => { resolve({ element, width: element.naturalWidth, height: element.naturalHeight }) }
    element.onerror = () => { reject(new Error(COVER_IMAGE_READ_FAILED)) }
    element.src = dataUrl
  })
}

/** The failure the loader reports; the view translates it through its own copy. */
const COVER_IMAGE_READ_FAILED = 'cover image could not be decoded'

/**
 * The file name one cover title exports under: path separators and the
 * characters Windows rejects become spaces, and the stem is bounded.
 * @param title - the cover title, or the draft title when the plan states none.
 * @returns a safe file stem with no extension.
 */
export function coverDownloadName(title: string): string {
  const cleaned = title.replace(/[\\/:*?"<>|\s]+/gu, ' ').trim().slice(0, 40)
  return cleaned.length > 0 ? cleaned : 'cover'
}
