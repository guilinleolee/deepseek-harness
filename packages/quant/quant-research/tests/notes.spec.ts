/**
 * PET research-notes tests: save, list, delete, export markdown.
 */
import { describe, expect, it } from 'vitest'
import type { KvTable } from '@deepseek-ai/dsh-storage-domain'
import { ResearchNoteId } from '../src/domain/spec.ts'
import type { ResearchNote } from '../src/domain/spec.ts'
import { deleteNote, exportNotesMarkdown, listNotes, renderNoteMarkdown, saveNote } from '../src/pet/notes.ts'

function table(): KvTable<ResearchNoteId, ResearchNote> {
  const store = new Map<ResearchNoteId, ResearchNote>()
  return {
    entries: () => store.entries(),
    get size() { return store.size },
    get: (key: ResearchNoteId) => store.get(key),
    put: async (key: ResearchNoteId, value: ResearchNote) => { store.set(key, value) },
    delete: async (key: ResearchNoteId) => { store.delete(key) },
  } as unknown as KvTable<ResearchNoteId, ResearchNote>
}

describe('saveNote / listNotes', () => {
  it('saves and lists notes with symbol and tag filtering', async () => {
    const t = table()
    await saveNote(t, { title: '动量策略回测', body: '20 日动量在测试期表现良好', symbol: '000001', tags: ['momentum', 'backtest'] }, 100, () => 'n-1')
    await saveNote(t, { title: '波动率观察', body: 'AAPL 波动率偏高', symbol: 'AAPL', tags: ['volatility'] }, 200, () => 'n-2')
    await saveNote(t, { title: '一般结论', body: '仅供研究参考', tags: ['general'] }, 300, () => 'n-3')

    const all = listNotes(t)
    expect(all).toHaveLength(3)
    expect(all[0]?.title).toBe('一般结论') // newest first

    const bySymbol = listNotes(t, { symbol: '000001' })
    expect(bySymbol).toHaveLength(1)
    expect(bySymbol[0]?.title).toBe('动量策略回测')

    const byTag = listNotes(t, { tag: 'momentum' })
    expect(byTag).toHaveLength(1)
  })

  it('deleteNote removes and rejects missing', async () => {
    const t = table()
    await saveNote(t, { title: 'test', body: 'test body' }, 1, () => 'n-1')
    await deleteNote(t, 'n-1')
    expect(listNotes(t)).toHaveLength(0)
    await expect(deleteNote(t, 'n-1')).rejects.toThrow(/未找到/)
  })
})

describe('export markdown', () => {
  it('renders a single note', () => {
    const note: ResearchNote = {
      id: ResearchNoteId('n-1'), title: '动量策略', body: '策略正文',
      symbol: '000001', tags: ['momentum'], created_at: 1,
    }
    const md = renderNoteMarkdown(note)
    expect(md).toContain('## 动量策略 (000001)')
    expect(md).toContain('[momentum]')
    expect(md).toContain('策略正文')
  })

  it('exports multiple notes as a markdown document', () => {
    const notes = [
      { id: ResearchNoteId('n-1'), title: 'A', body: 'a', tags: [] as string[], created_at: 1 },
      { id: ResearchNoteId('n-2'), title: 'B', body: 'b', symbol: 'AAPL', tags: ['x'] as string[], created_at: 2 },
    ] as ResearchNote[]
    const md = exportNotesMarkdown(notes)
    expect(md).toContain('# 量化研究笔记')
    expect(md).toContain('## A')
    expect(md).toContain('## B (AAPL) [x]')
    expect(md).toContain('仅供研究参考，不构成投资建议')
  })
})
