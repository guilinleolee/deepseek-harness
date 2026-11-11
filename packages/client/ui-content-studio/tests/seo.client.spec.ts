import { describe, expect, it } from 'vitest'
import { extractKeywords, geoKeywords, layoutSuggestions } from '../src/client/seo.ts'
import { CREATE_TYPES } from '../src/client/create.ts'
import { en, zh } from '../src/client/locales.ts'

describe('extractKeywords', () => {
  it('ranks repeated CJK bigrams first and drops stopwords', () => {
    const text = '杭州探店真的值。杭州探店攻略来了。杭州探店避坑。'
    const keywords = extractKeywords(text, 5)
    expect(keywords[0]).toBe('杭州')
    expect(keywords).toContain('探店')
    expect(keywords).not.toContain('真的')
  })

  it('counts latin words case-insensitively and merges with CJK', () => {
    const keywords = extractKeywords('Notion 教程：Notion 入门。效率工具效率工具。')
    expect(keywords).toContain('notion')
    expect(keywords).toContain('效率')
  })

  it('requires at least two occurrences and honors the cap', () => {
    expect(extractKeywords('山有木兮', 8)).toEqual([])
    const text = Array.from({ length: 6 }, (_, group) => `关键词${group}${group}重复重复。`).join('')
    expect(extractKeywords(text, 3).length).toBeLessThanOrEqual(3)
  })
})

describe('layoutSuggestions', () => {
  it('differs per content type and reads as locale stems', () => {
    expect(layoutSuggestions('gzh-article')).toEqual(['title', 'hook', 'sections', 'cta', 'tags'])
    expect(layoutSuggestions('xhs-note')).toEqual(['title', 'firstImage', 'cards', 'tags'])
    expect(layoutSuggestions('product-page')).toContain('trust')
  })

  it('advises the shot structure for a storyboard and the cover fields for a cover plan', () => {
    expect(layoutSuggestions('storyboard')).toEqual(['shots', 'visual', 'line', 'duration'])
    expect(layoutSuggestions('cover')).toEqual(['title', 'subtitle', 'composition', 'palette', 'style'])
  })

  it('names only stems the dictionary carries', () => {
    for (const contentType of CREATE_TYPES.map(entry => entry.id)) {
      for (const stem of layoutSuggestions(contentType)) {
        expect(zh).toHaveProperty(`create.seo.layout.${stem}`)
        expect(en).toHaveProperty(`create.seo.layout.${stem}`)
      }
    }
  })
})

describe('geoKeywords', () => {
  it('combines the region with the strongest keywords', () => {
    expect(geoKeywords('杭州', ['探店', '咖啡', '露营'], 2)).toEqual(['杭州探店', '杭州咖啡'])
  })

  it('returns empty without a region or keywords', () => {
    expect(geoKeywords('  ', ['探店'])).toEqual([])
    expect(geoKeywords('杭州', [])).toEqual([])
  })
})
