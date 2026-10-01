import { mkdtemp, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { CALENDAR_FILENAME, readNotes, writeNote } from '../src/calendar-notes.ts'

async function tempFile(): Promise<string> {
  const dir = await mkdtemp(join(tmpdir(), 'dsh-content-schedule-notes-'))
  return join(dir, CALENDAR_FILENAME)
}

describe('readNotes', () => {
  it('reads an absent file as empty notes', async () => {
    const snapshot = await readNotes(await tempFile())
    expect(snapshot.notes).toEqual({})
    expect(snapshot.problems).toEqual([])
  })

  it('rejects unknown format versions and broken shapes as a whole', async () => {
    const first = await tempFile()
    await writeFile(first, JSON.stringify({ formatVersion: 1, notes: {} }))
    expect((await readNotes(first)).problems).toHaveLength(1)

    const second = await tempFile()
    await writeFile(second, JSON.stringify({ formatVersion: 0, notes: [] }))
    expect((await readNotes(second)).problems).toHaveLength(1)

    const third = await tempFile()
    await writeFile(third, '{truncated')
    expect((await readNotes(third)).notes).toEqual({})
    expect((await readNotes(third)).problems).toHaveLength(1)
  })

  it('names one malformed entry and keeps the valid rest', async () => {
    const file = await tempFile()
    await writeFile(file, JSON.stringify({ formatVersion: 0, notes: {
      a: { text: '等素材', updatedAt: '2026-09-27T10:00:00+08:00' },
      b: { text: '' },
      c: 'not-an-object',
    } }))
    const snapshot = await readNotes(file)
    expect(Object.keys(snapshot.notes)).toEqual(['a'])
    expect(snapshot.problems).toHaveLength(2)
  })
})

describe('writeNote', () => {
  it('upserts one entry with a fresh timestamp', async () => {
    const file = await tempFile()
    await writeNote(file, 'a', '等素材')
    const first = await readNotes(file)
    expect(first.notes.a?.text).toBe('等素材')
    await writeNote(file, 'a', '改周三')
    const second = await readNotes(file)
    expect(Object.keys(second.notes)).toEqual(['a'])
    expect(second.notes.a?.text).toBe('改周三')
    expect(second.notes.a!.updatedAt >= first.notes.a!.updatedAt).toBe(true)
  })

  it('clears an entry on an empty write and trims whitespace', async () => {
    const file = await tempFile()
    await writeNote(file, 'a', '  等素材  ')
    expect((await readNotes(file)).notes.a?.text).toBe('等素材')
    await writeNote(file, 'a', '   ')
    expect((await readNotes(file)).notes).toEqual({})
  })
})
