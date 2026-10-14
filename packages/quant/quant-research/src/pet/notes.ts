/**
 * PET research notes: save, list, delete, and export research conclusions
 * over the domain's `research_notes` table. Plain table functions.
 * @module @deepseek-ai/dsh-quant-research/pet/notes
 */

import { randomUUID } from 'node:crypto'
import type { KvTable } from '@deepseek-ai/dsh-storage-domain'
import { ResearchNoteId } from '../domain/spec.ts'
import type { ResearchNote } from '../domain/spec.ts'
import { QuantError } from '../errors.ts'

/** The research-notes table handle. */
export type NotesTable = KvTable<ResearchNoteId, ResearchNote>

/** Fields the save-note caller supplies; id and timestamp fill here. */
export interface NoteSaveInput {
  /** Note title. */
  readonly title: string
  /** Note body. */
  readonly body: string
  /** Associated symbol, when the note is about a specific instrument. */
  readonly symbol?: string
  /** Research tags for filtering. */
  readonly tags?: readonly string[]
}

/**
 * Save one research note durably.
 * @param table - the research-notes table.
 * @param input - title, body, symbol, and tags.
 * @param now - the save timestamp (injected for tests).
 * @param newId - the id factory (injected for tests).
 * @returns the stored note.
 */
export async function saveNote(
  table: NotesTable,
  input: NoteSaveInput,
  now: number = Date.now(),
  newId: () => string = () => randomUUID(),
): Promise<ResearchNote> {
  const note: ResearchNote = {
    id: ResearchNoteId(newId()),
    title: input.title,
    body: input.body,
    ...(input.symbol === undefined ? {} : { symbol: input.symbol }),
    tags: [...(input.tags ?? [])],
    created_at: now,
  }
  await table.put(note.id, note)
  return note
}

/**
 * List all research notes, newest first.
 * @param table - the research-notes table.
 * @param filter - optional symbol or tag filter.
 * @returns matching notes, newest first.
 */
export function listNotes(
  table: NotesTable,
  filter?: { symbol?: string; tag?: string },
): ResearchNote[] {
  return [...table.entries()].map(([, note]) => note)
    .filter(note => {
      if (filter?.symbol !== undefined && note.symbol !== filter.symbol) return false
      if (filter?.tag !== undefined && !note.tags.includes(filter.tag)) return false
      return true
    })
    .sort((left, right) => right.created_at - left.created_at)
}

/**
 * Delete one research note.
 * @param table - the research-notes table.
 * @param id - the note id.
 * @throws {@link QuantError} code `DATA` when the note does not exist.
 */
export async function deleteNote(table: NotesTable, id: string): Promise<void> {
  const existing = table.get(ResearchNoteId(id))
  if (existing === undefined) {
    throw new QuantError('DATA', `未找到研究笔记：${id}`)
  }
  await table.delete(ResearchNoteId(id))
}

/**
 * Render one research note as markdown.
 * @param note - the note to render.
 * @returns the markdown string.
 */
export function renderNoteMarkdown(note: ResearchNote): string {
  const tags = note.tags.length > 0 ? ` [${note.tags.join(', ')}]` : ''
  const symbol = note.symbol !== undefined ? ` (${note.symbol})` : ''
  return `## ${note.title}${symbol}${tags}\n\n${note.body}\n`
}

/**
 * Export multiple notes as one markdown document.
 * @param notes - the notes to export.
 * @returns the markdown document.
 */
export function exportNotesMarkdown(notes: readonly ResearchNote[]): string {
  const header = '# 量化研究笔记\n\n仅供研究参考，不构成投资建议。\n'
  const body = notes.map(renderNoteMarkdown).join('\n---\n\n')
  return `${header}\n${body}`
}
