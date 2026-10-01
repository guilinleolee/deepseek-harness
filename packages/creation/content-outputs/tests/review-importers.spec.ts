import { describe, expect, it } from 'vitest'
import type { ReviewImportPreviewRequest } from '../src/review/types.ts'
import {
  mapImportColumns, parseCsvRows, parseDateCell, parseImportFile, parseMetricCell,
} from '../src/review/importers.ts'

function preview(overrides: Partial<ReviewImportPreviewRequest> = {}): ReviewImportPreviewRequest {
  return {
    platformId: 'xhs',
    fileName: 'notes.csv',
    text: '笔记ID,笔记标题,发布时间,曝光量,观看量,点赞量,收藏量,评论量\n'
      + 'abc123,第一篇,2026/9/1 10:00,10000,2000,100,50,10\n'
      + 'def456,第二篇,2026-09-05,2.5万,5000,80,20,5\n',
    ...overrides,
  }
}

describe('parseCsvRows', () => {
  it('splits plain rows on commas and newlines', () => {
    expect(parseCsvRows('a,b,c\nd,e,f')).toEqual([['a', 'b', 'c'], ['d', 'e', 'f']])
  })

  it('handles CR and CRLF endings and a trailing newline', () => {
    expect(parseCsvRows('a,b\r\nc,d\ne,f\r\n')).toEqual([['a', 'b'], ['c', 'd'], ['e', 'f']])
  })

  it('keeps quoted commas, doubled quotes, and embedded newlines', () => {
    expect(parseCsvRows('"a,b","say ""hi""","line1\nline2"')).toEqual([['a,b', 'say "hi"', 'line1\nline2']])
  })

  it('strips a UTF-8 BOM from the first header cell', () => {
    expect(parseCsvRows('\uFEFFa,b')[0]).toEqual(['a', 'b'])
  })
})

describe('mapImportColumns', () => {
  it('maps every known alias and lists unknown headers', () => {
    const { columns, unknownColumns } = mapImportColumns(['笔记ID', '标题', '发布时间', '曝光量', '自定义列'])
    expect(columns.workId).toBe(0)
    expect(columns.title).toBe(1)
    expect(columns.publishedAt).toBe(2)
    expect(columns.impressions).toBe(3)
    expect(columns.reads).toBe(-1)
    expect(unknownColumns).toEqual(['自定义列'])
  })

  it('matches case-insensitively with full-width parens normalized', () => {
    const { columns } = mapImportColumns(['BV号', 'Title（主）'])
    expect(columns.workId).toBe(0)
    expect(columns.title).toBe(1)
  })
})

describe('parseMetricCell', () => {
  it('passes numbers and nulls blanks, dashes, and missing columns', () => {
    expect(parseMetricCell('42')).toBe(42)
    expect(parseMetricCell('1,234')).toBe(1234)
    expect(parseMetricCell('')).toBeNull()
    expect(parseMetricCell('-')).toBeNull()
    expect(parseMetricCell(undefined)).toBeNull()
  })

  it('scales 万/w suffixes to units and rejects other text', () => {
    expect(parseMetricCell('2.5万')).toBe(25_000)
    expect(parseMetricCell('3w')).toBe(30_000)
    expect(() => parseMetricCell('很多')).toThrow(/non-numeric/)
  })
})

describe('parseDateCell', () => {
  it('normalizes slash and dash forms to ISO instants', () => {
    expect(parseDateCell('2026/9/1 10:00')).toBe('2026-09-01T10:00:00.000Z')
    expect(parseDateCell('2026-09-05')).toBe('2026-09-05T00:00:00.000Z')
    expect(parseDateCell('2026/9/1 10:00:30')).toBe('2026-09-01T10:00:30.000Z')
  })

  it('reads blanks as null and rejects unparseable text', () => {
    expect(parseDateCell('')).toBeNull()
    expect(parseDateCell(undefined)).toBeNull()
    expect(() => parseDateCell('昨天')).toThrow(/unparseable date/)
  })
})

describe('parseImportFile', () => {
  it('maps aliased headers into normalized rows', () => {
    const result = parseImportFile(preview())
    expect(result.rows).toHaveLength(2)
    expect(result.rejected).toEqual([])
    expect(result.unknownColumns).toEqual([])
    expect(result.totalRows).toBe(2)
    const first = result.rows[0]
    expect(first?.platformWorkId).toBe('abc123')
    expect(first?.title).toBe('第一篇')
    expect(first?.publishedAt).toBe('2026-09-01T10:00:00.000Z')
    expect(first?.metrics.impressions).toBe(10_000)
    expect(first?.metrics.reads).toBe(2000)
    expect(first?.metrics.followersGained).toBeNull()
  })

  it('scales 万-suffixed cells and skips absent columns as null', () => {
    const result = parseImportFile(preview())
    const second = result.rows[1]
    expect(second?.metrics.impressions).toBe(25_000)
  })

  it('rejects rows with a numbered reason and keeps the rest', () => {
    const result = parseImportFile(preview({
      text: '笔记ID,笔记标题,曝光量\nabc123,第一篇,100\n,第二篇,200\nabc123,重复ID,300\n',
    }))
    expect(result.rows).toHaveLength(1)
    expect(result.rejected).toEqual([
      { row: 3, reason: 'missing work id' },
      { row: 4, reason: 'duplicate work id "abc123" in file' },
    ])
    expect(result.totalRows).toBe(3)
  })

  it('surfaces unknown columns for the user to check', () => {
    const result = parseImportFile(preview({
      text: '笔记ID,笔记标题,曝光量,神秘列\nabc123,第一篇,100,x\n',
    }))
    expect(result.unknownColumns).toEqual(['神秘列'])
    expect(result.rows).toHaveLength(1)
  })

  it('rejects the whole file when the work-id or title column cannot resolve', () => {
    expect(() => parseImportFile(preview({ text: '列A,列B\n1,2\n' }))).toThrow(/work-id and title columns/)
  })

  it('rejects an empty file and an oversized one', () => {
    expect(() => parseImportFile(preview({ text: '' }))).toThrow(/empty/)
    expect(() => parseImportFile(preview({ text: `笔记ID,标题\n${'a'.repeat(2_000_000)}` }))).toThrow(/character cap/)
  })

  it('rejects rows carrying non-numeric metric text without stopping the batch', () => {
    const result = parseImportFile(preview({
      text: '笔记ID,笔记标题,曝光量\nabc123,第一篇,100\ndef456,第二篇,很多\n',
    }))
    expect(result.rows).toHaveLength(1)
    expect(result.rejected).toHaveLength(1)
    expect(result.rejected[0]?.row).toBe(3)
    expect(result.rejected[0]?.reason).toContain('non-numeric')
  })
})
