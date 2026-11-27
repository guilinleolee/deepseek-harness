// @vitest-environment jsdom
import { describe, expect, it } from 'vitest'
import {
  COVER_HEIGHT, COVER_WIDTH, coverDownloadName, coverTextUnits, layoutCoverText, paintCover, paintCoverElement, wrapCoverText,
  type CoverCanvas,
} from '../src/client/cover-text.ts'

/** The number of code points in one string, the unit every measure stub below counts. */
function glyphs(text: string): number {
  return Array.from(text).length
}

/** A recording context whose glyph width scales with the current font size, like a real one. */
function recordingCanvas(perEm = 1): {
  ctx: CoverCanvas
  calls: { texts: { text: string; x: number; y: number }[]; gradients: number; images: number }
} {
  const calls = { texts: [] as { text: string; x: number; y: number }[], gradients: 0, images: 0 }
  const gradient = { addColorStop: () => {} }
  const ctx: CoverCanvas = {
    fillRect: () => {},
    fillText: (text, x, y) => { calls.texts.push({ text, x, y }) },
    // A CJK glyph advances about one font size; the latin fraction rides `perEm`.
    measureText: text => ({ width: glyphs(text) * (state.fontSize ?? 100) * perEm }),
    createLinearGradient: () => { calls.gradients += 1; return gradient },
    createRadialGradient: () => { calls.gradients += 1; return gradient },
    drawImage: () => { calls.images += 1 },
    font: '',
  }
  const state: { fontSize: number | undefined } = { fontSize: undefined }
  const target = new Proxy(ctx, {
    set: (source, property, value) => {
      if (property === 'font' && typeof value === 'string') state.fontSize = Number(/(\d+)px/u.exec(value)?.[1] ?? 100)
      Reflect.set(source, property, value)
      return true
    },
  })
  return { ctx: target, calls }
}

describe('coverTextUnits', () => {
  it('counts a CJK character as one unit and a latin letter as a fraction', () => {
    expect(coverTextUnits('删掉一半')).toBe(4)
    expect(coverTextUnits('abcd')).toBeCloseTo(2.2)
    expect(coverTextUnits('')).toBe(0)
  })
})

describe('wrapCoverText', () => {
  it('breaks a latin run at spaces', () => {
    const lines = wrapCoverText('one two three', line => glyphs(line) * 100, 900, 3)
    expect(lines).toEqual(['one two', 'three'])
  })

  it('breaks a CJK run between characters once a line fills', () => {
    const lines = wrapCoverText('删掉一半效率工具', line => glyphs(line) * 100, 300, 3)
    expect(lines).toEqual(['删掉一', '半效率', '工具'])
  })

  it('splits one over-wide token character by character', () => {
    const lines = wrapCoverText('abcdefgh', line => glyphs(line) * 100, 300, 5)
    expect(lines).toEqual(['abc', 'def', 'gh'])
  })

  it('keeps at most the allowed number of lines', () => {
    expect(wrapCoverText('一二三四五六七八九', line => glyphs(line) * 200, 200, 2)).toEqual(['一', '二'])
  })

  it('drops a row that carries only whitespace', () => {
    expect(wrapCoverText('   ', () => 10, 100, 3)).toEqual([])
    expect(wrapCoverText('', () => 10, 100, 3)).toEqual([])
  })
})

describe('layoutCoverText', () => {
  it('returns no lines for an empty title and the large size', () => {
    expect(layoutCoverText('   ', () => 0)).toEqual({ lines: [], fontSize: 148 })
  })

  it('uses the large size for a short title and the reduced size for a long one', () => {
    const short = layoutCoverText('删掉一半', () => 100)
    expect(short.fontSize).toBe(148)
    const long = layoutCoverText('删掉一半效率工具，真正拉开差距的是取舍', () => 100)
    expect(long.fontSize).toBe(112)
  })
})

describe('paintCover', () => {
  it('paints the gradient card and the title when no image is given', () => {
    const { ctx, calls } = recordingCanvas()
    const layout = paintCover(ctx, { text: '删掉一半' })
    expect(layout.lines).toEqual(['删掉一半'])
    expect(calls.gradients).toBe(2)
    expect(calls.images).toBe(0)
    expect(calls.texts).toHaveLength(1)
    expect(calls.texts[0]?.x).toBe(100)
  })

  it('draws the rendered image over the card and shades the title area', () => {
    const { ctx, calls } = recordingCanvas()
    paintCover(ctx, { text: '标题', image: { source: {}, width: 1000, height: 1000 } })
    expect(calls.images).toBe(1)
    expect(calls.gradients).toBe(3)
  })

  it('paints only the background for an empty title', () => {
    const { ctx, calls } = recordingCanvas()
    paintCover(ctx, { text: '   ' })
    expect(calls.texts).toEqual([])
  })

  it('stacks multiple lines upward from the bottom margin', () => {
    const { ctx, calls } = recordingCanvas()
    // A long title at the reduced 112px size overflows one 1720px line, so it wraps.
    paintCover(ctx, { text: '删掉一半效率工具真正拉开差距的是取舍不是工具数量' })
    expect(calls.texts.length).toBeGreaterThan(1)
    const baselines = calls.texts.map(entry => entry.y)
    expect(new Set(baselines).size).toBe(calls.texts.length)
    for (const baseline of baselines) expect(baseline).toBeLessThan(COVER_HEIGHT)
  })
})

describe('paintCoverElement', () => {
  /** Replace the global image constructor for one case; jsdom cannot decode real bytes. */
  async function withImageStub(
    behavior: 'load' | 'error',
    run: () => Promise<void>,
  ): Promise<void> {
    const original = globalThis.Image
    class StubImage {
      naturalWidth = 800
      naturalHeight = 600
      onload: ((event: Event) => void) | null = null
      onerror: ((event: Event) => void) | null = null
      set src(_value: string) {
        queueMicrotask(() => {
          if (behavior === 'load') this.onload?.(new Event('load'))
          else this.onerror?.(new Event('error'))
        })
      }
    }
    Object.defineProperty(globalThis, 'Image', { value: StubImage, writable: true, configurable: true })
    try {
      await run()
    } finally {
      Object.defineProperty(globalThis, 'Image', { value: original, writable: true, configurable: true })
    }
  }

  it('paints without an image when no data URL is supplied', async () => {
    const { ctx, calls } = recordingCanvas()
    const layout = await paintCoverElement(ctx as unknown as CanvasRenderingContext2D, '标题', null)
    expect(layout.lines).toEqual(['标题'])
    expect(calls.images).toBe(0)
  })

  it('paints with the decoded image when a data URL loads', async () => {
    const { ctx, calls } = recordingCanvas()
    await withImageStub('load', async () => {
      await paintCoverElement(ctx as unknown as CanvasRenderingContext2D, '标题', 'data:image/png;base64,AA')
    })
    expect(calls.images).toBe(1)
  })

  it('rejects when the image cannot be decoded', async () => {
    const { ctx } = recordingCanvas()
    await withImageStub('error', async () => {
      await expect(paintCoverElement(ctx as unknown as CanvasRenderingContext2D, '标题', 'data:image/png;base64,AA'))
        .rejects.toThrow('could not be decoded')
    })
  })
})

describe('coverDownloadName', () => {
  it('replaces path separators and trims the stem', () => {
    expect(coverDownloadName('删掉/一半:效率*工具?')).toBe('删掉 一半 效率 工具')
  })

  it('falls back to a fixed stem for an all-separator title', () => {
    expect(coverDownloadName('   ')).toBe('cover')
    expect(coverDownloadName('///')).toBe('cover')
  })

  it('bounds a long title', () => {
    expect(coverDownloadName('一'.repeat(80))).toHaveLength(40)
  })
})

describe('cover dimensions', () => {
  it('exports a 1920×1080 frame', () => {
    expect([COVER_WIDTH, COVER_HEIGHT]).toEqual([1920, 1080])
  })
})
