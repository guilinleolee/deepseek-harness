import { describe, expect, it } from 'vitest'
import type { GatherSource } from '../src/client/gather/types.ts'
import { exportSourcesAsOpml, previewOpmlImport } from '../src/client/gather/opml.ts'

function source(overrides: Partial<GatherSource> & { name: string; url: string }): GatherSource {
  return {
    intervalMinutes: 60,
    enabled: true,
    tags: [],
    excludeKeywords: [],
    createdAt: '2026-09-25T00:00:00.000Z',
    lastFetchedAt: null,
    lastStatus: null,
    consecutiveFailures: 0,
    etag: null,
    lastModified: null,
    ...overrides,
  } as GatherSource
}

const SAMPLE_OPML = `<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head><title>subscriptions</title></head>
  <body>
    <outline text="科技">
      <outline type="rss" text="源一" xmlUrl="https://a.example/feed"/>
      <outline type="rss" text="重复源" xmlUrl="https://dup.example/feed"/>
    </outline>
    <outline type="rss" text="源二" xmlUrl="https://b.example/feed"/>
    <outline text="空壳分组"/>
  </body>
</opml>`

describe('gather OPML import preview', () => {
  it('flattens folder grouping and marks duplicates against the current list', () => {
    const sources = [source({ name: '重复源', url: 'https://dup.example/feed' })]
    const { rows, problem } = previewOpmlImport(SAMPLE_OPML, sources)
    expect(problem).toBeUndefined()
    expect(rows).toBeDefined()
    const byUrl = new Map(rows!.map(row => [row.url, row]))
    expect(byUrl.get('https://a.example/feed')?.folder).toEqual(['科技'])
    expect(byUrl.get('https://a.example/feed')?.duplicate).toBe(false)
    expect(byUrl.get('https://dup.example/feed')?.duplicate).toBe(true)
    expect(byUrl.get('https://b.example/feed')?.folder).toEqual([])
    // The bare group outline carries no xmlUrl: flagged invalid, skipped on import.
    expect(rows!.some(row => row.invalid)).toBe(true)
  })

  it('names the parse problem for a non-OPML document', () => {
    const { problem } = previewOpmlImport('<html><body>not opml</body></html>', [])
    expect(typeof problem).toBe('string')
  })
})

describe('gather OPML export', () => {
  it('groups by the first tag and round-trips through the importer', () => {
    const sources = [
      source({ name: '源一', url: 'https://a.example/feed', tags: ['科技'] }),
      source({ name: '源二', url: 'https://b.example/feed', tags: ['科技'] }),
      source({ name: '独立源', url: 'https://c.example/feed' }),
    ]
    const opml = exportSourcesAsOpml(sources)
    expect(opml).toContain('xmlUrl="https://a.example/feed"')
    const { rows } = previewOpmlImport(opml, [])
    expect(rows).toBeDefined()
    const byUrl = new Map(rows!.map(row => [row.url, row]))
    expect(byUrl.get('https://a.example/feed')?.folder).toEqual(['科技'])
    expect(byUrl.get('https://c.example/feed')?.folder).toEqual([])
  })
})
