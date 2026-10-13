import { describe, expect, it } from 'vitest'
import type { CreateManifest, CreateVersion } from '@deepseek-ai/dsh-content-outputs/types'
import {
  MANUAL_MERGE_WINDOW_MS, VERSION_CAP, appendHashtagBlock, appendVersion, buildExportMarkdown,
  contentTypeKind, countWords, defaultManifest, deliverableName, exportFileName, formatHashtags,
  isBatchable, lineDiff, localMetrics, mergeManualSave, newId, pinVersion, pruneVersions,
  readingMinutes, replaceRange, slugify, suggestHashtags, triggerClass, versionContent,
} from '../src/client/create.ts'
import { scanBannedWords } from '../src/client/banned-words.ts'

function version(v: number, overrides: Partial<CreateVersion> = {}): CreateVersion {
  return { v, ts: '2026-09-25T00:00:00.000Z', trigger: 'manual-save', words: 1, content: `v${v}`, pinned: false, profileRef: null, ...overrides }
}

function manifest(versions: readonly CreateVersion[] = [], overrides: Partial<CreateManifest> = {}): CreateManifest {
  return {
    formatVersion: 0, contentId: 'cc-test0001', contentType: 'gzh-article', currentVersion: versions.at(-1)?.v ?? 0,
    context: { audience: null, points: null, references: null }, topicRef: null, sources: [], versions, ...overrides,
  }
}

describe('countWords and readingMinutes', () => {
  it('counts CJK characters and latin word runs', () => {
    expect(countWords('你好世界')).toBe(4)
    expect(countWords('hello world')).toBe(2)
    expect(countWords('你好 world 第3天')).toBe(6)
    expect(countWords('')).toBe(0)
  })

  it('paces voiceover faster and never returns zero', () => {
    expect(readingMinutes(400, 'gzh-article')).toBe(1)
    expect(readingMinutes(1200, 'gzh-article')).toBe(3)
    expect(readingMinutes(480, 'voiceover')).toBe(2)
    expect(readingMinutes(1200, 'voiceover')).toBe(5)
    expect(readingMinutes(0, 'gzh-article')).toBe(1)
  })
})

describe('version list operations', () => {
  it('appends versions with a continuing counter and computed words', () => {
    const next = appendVersion(manifest([version(1)]), { content: '正文一二三', trigger: 'ai-generate', now: 't2', profileRef: null })
    expect(next.currentVersion).toBe(2)
    expect(next.versions.at(-1)).toMatchObject({ v: 2, trigger: 'ai-generate', words: 5, content: '正文一二三', pinned: false, profileRef: null })
  })

  it('prunes to the quota, keeping pinned versions and the newest unpinned', () => {
    const versions = [
      version(1, { pinned: true }),
      ...Array.from({ length: VERSION_CAP + 2 }, (_, index) => version(index + 2)),
    ]
    const pruned = pruneVersions(versions)
    expect(pruned.some(entry => entry.v === 1 && entry.pinned)).toBe(true)
    expect(pruned.filter(entry => !entry.pinned)).toHaveLength(VERSION_CAP)
    expect(pruned.some(entry => entry.v === 2)).toBe(false)
    expect(pruned.at(-1)?.v).toBe(versions.length)
    expect([...pruned].sort((a, b) => a.v - b.v)).toEqual(pruned)
  })

  it('folds a manual save inside the merge window and stacks one outside', () => {
    const now = '2026-09-25T01:00:00.000Z'
    const recent = new Date(Date.parse(now) - 60_000).toISOString()
    const old = new Date(Date.parse(now) - MANUAL_MERGE_WINDOW_MS - 1000).toISOString()
    const inside = mergeManualSave(manifest([version(1, { trigger: 'manual-save', ts: recent })]), { content: '更新', now, profileRef: null })
    expect(inside.created).toBe(false)
    expect(inside.manifest.currentVersion).toBe(1)
    expect(inside.manifest.versions).toHaveLength(1)
    expect(inside.manifest.versions[0]?.content).toBe('更新')
    const outside = mergeManualSave(manifest([version(1, { trigger: 'manual-save', ts: old })]), { content: '更新', now, profileRef: null })
    expect(outside.created).toBe(true)
    expect(outside.manifest.currentVersion).toBe(2)
    const afterGenerate = mergeManualSave(manifest([version(1, { trigger: 'ai-generate', ts: recent })]), { content: '更新', now, profileRef: null })
    expect(afterGenerate.created).toBe(true)
    const unparseable = mergeManualSave(manifest([version(1, { trigger: 'manual-save', ts: 'not-a-date' })]), { content: '更新', now, profileRef: null })
    expect(unparseable.created).toBe(true)
  })

  it('toggles pins, reads stored text, and ignores unknown versions', () => {
    const pinned = pinVersion(manifest([version(1), version(2)]), 1)
    expect(pinned.versions[0]?.pinned).toBe(true)
    expect(pinVersion(pinned, 1).versions[0]?.pinned).toBe(false)
    expect(pinVersion(manifest([version(1)]), 9)).toEqual(manifest([version(1)]))
    expect(versionContent(manifest([version(1, { content: '正文' })]), 1)).toBe('正文')
    expect(versionContent(manifest([version(1)]), 9)).toBeNull()
  })
})

describe('text helpers', () => {
  it('splices a selection range', () => {
    expect(replaceRange('abcdef', 2, 4, 'XY')).toBe('abXYef')
  })

  it('diffs lines with common head and tail trimmed', () => {
    expect(lineDiff('a\nb\nc', 'a\nb\nc').every(row => row.kind === 'same')).toBe(true)
    const rows = lineDiff('a\n老句\n尾', 'a\n新句一\n新句二\n尾')
    expect(rows.map(row => row.kind)).toEqual(['same', 'del', 'add', 'add', 'same'])
    const bounded = lineDiff(
      Array.from({ length: 250 }, (_, i) => `旧${i}`).join('\n'),
      Array.from({ length: 250 }, (_, i) => `新${i}`).join('\n'),
    )
    expect(bounded.filter(row => row.kind === 'del')).toHaveLength(250)
    expect(bounded.filter(row => row.kind === 'add')).toHaveLength(250)
  })

  it('slugifies titles for file naming', () => {
    expect(slugify('  AI 工具，测评！  ')).toBe('ai-工具-测评')
    expect(slugify('!!!')).toBe('draft')
    expect(slugify('一二三四五六七八九十甲乙丙丁戊己庚辛壬癸子丑寅卯')).toBe('一二三四五六七八九十甲乙丙丁戊己庚辛壬癸子丑寅卯')
  })

  it('names deliverables and exports after the title and id stem', () => {
    expect(deliverableName('我的标题', 'cc-abcd1234x')).toBe('我的标题-bcd1234x.md')
    expect(exportFileName('标题', 'cc-1234')).toMatch(/^export-标题-cc1234\.md$/)
    expect(deliverableName('!!!', 'xx')).toBe('draft-xx.md')
  })

  it('renders the export frontmatter around the body', () => {
    const markdown = buildExportMarkdown({
      title: '标题', contentType: 'gzh-article', status: 'published', version: 3, exportedAt: '2026-09-25T00:00:00.000Z',
    }, '正文')
    expect(markdown).toContain('---\ntitle: 标题\n')
    expect(markdown).toContain('contentType: gzh-article')
    expect(markdown).toContain('version: 3')
    expect(markdown.trimEnd().endsWith('正文')).toBe(true)
  })

  it('classifies triggers into locale stems', () => {
    expect(triggerClass('ai-generate')).toBe('ai')
    expect(triggerClass('ai-generate#2')).toBe('ai')
    expect(triggerClass('manual-save')).toBe('manual')
    expect(triggerClass('restore')).toBe('restore')
    expect(triggerClass('retarget')).toBe('retarget')
    expect(triggerClass('rewrite:condense')).toBe('rewrite')
  })

  it('maps content types onto the coarse output kinds', () => {
    expect(contentTypeKind('gzh-article')).toBe('article')
    expect(contentTypeKind('xhs-note')).toBe('xhs-note')
    expect(contentTypeKind('video-script')).toBe('video')
    expect(contentTypeKind('voiceover')).toBe('audio')
    expect(contentTypeKind('product-page')).toBe('other')
  })

  it('creates ids and default manifests', () => {
    const id = newId()
    expect(id.startsWith('cc-')).toBe(true)
    expect(new Set(Array.from({ length: 20 }, () => newId())).size).toBe(20)
    const empty = defaultManifest(id, 'gzh-article')
    expect(empty).toMatchObject({
      formatVersion: 0, contentId: id, contentType: 'gzh-article', currentVersion: 0,
      context: { audience: null, points: null, references: null }, topicRef: null, sources: [], versions: [],
    })
  })
})

describe('scanBannedWords', () => {
  it('finds hits with category, count, and reading order', () => {
    const hits = scanBannedWords('这是最佳选择，稳赚不赔，真的最佳！')
    expect(hits.map(hit => hit.word)).toEqual(['最佳', '稳赚不赔'])
    expect(hits[0]).toMatchObject({ category: 'absolute', count: 2 })
    expect(hits[1]).toMatchObject({ category: 'finance', count: 1 })
    expect(hits[0]!.firstIndex).toBeLessThan(hits[1]!.firstIndex)
  })

  it('is case-insensitive for latin entries and returns empty on clean text', () => {
    expect(scanBannedWords('疗效 100%')[0]?.word).toBe('100%')
    expect(scanBannedWords('一篇干净的文章')).toEqual([])
  })
})

describe('hashtags and local metrics', () => {
  it('batches only the short content type in one request', () => {
    expect(isBatchable('xhs-note')).toBe(true)
    expect(isBatchable('gzh-article')).toBe(false)
  })

  it('suggests pool tags by match, title hits first, capped at eight', () => {
    const suggestions = suggestHashtags('AI工具测评', '聊聊效率提升与自媒体副业'.repeat(3))
    expect(suggestions[0]).toBe('AI工具')
    expect(suggestions).toContain('效率提升')
    expect(suggestions.length).toBeLessThanOrEqual(8)
    expect(suggestHashtags('无匹配', '正文')).toEqual([])
  })

  it('formats per platform: xhs open tags, gzh/zhihu closed tags', () => {
    expect(formatHashtags(['AI工具', '副业'], 'xhs-note')).toBe('#AI工具 #副业')
    expect(formatHashtags(['AI工具', '副业'], 'gzh-article')).toBe('#AI工具# #副业#')
    expect(formatHashtags(['AI工具'], 'voiceover')).toBe('#AI工具#')
    expect(formatHashtags([], 'gzh-article')).toBe('')
    expect(formatHashtags([' x ', ''], 'xhs-note')).toBe('#x')
  })

  it('appends the block on its own line and ignores an empty block', () => {
    expect(appendHashtagBlock('正文', '#AI工具')).toBe('正文\n\n#AI工具\n')
    expect(appendHashtagBlock('正文  \n', '#x')).toBe('正文\n\n#x\n')
    expect(appendHashtagBlock('', '#x')).toBe('\n\n#x\n')
    expect(appendHashtagBlock('正文', '')).toBe('正文')
  })

  it('computes the deterministic local metrics', () => {
    expect(localMetrics('# 标题在这里\n\n第一段。\n\n第二段。')).toEqual({ words: 11, paragraphs: 2, titleLength: 5 })
    expect(localMetrics('')).toEqual({ words: 0, paragraphs: 0, titleLength: 0 })
  })
})
