import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'
import {
  PERSONAS_FILENAME, deletePersonaFile, parsePersonasManifest, personaDigest, putPersonaFile,
  putPersonaReportFile, readPersonasFile,
} from '../src/persona/store.ts'
import type { PersonaEntry, PersonaField, PersonaFieldKey, PersonaInput, PersonasManifest } from '../src/types.ts'
import { PERSONA_FIELD_KEYS } from '../src/persona/types.ts'

let dir: string | undefined

afterEach(async () => {
  if (dir !== undefined) await rm(dir, { recursive: true, force: true })
  dir = undefined
})

async function storeFile(): Promise<string> {
  dir = await mkdtemp(join(tmpdir(), 'persona-store-'))
  return join(dir, PERSONAS_FILENAME)
}

/** One full valid input over the required fields, overridden per test. */
function input(overrides: Partial<PersonaInput> = {}): PersonaInput {
  const fields = {} as Record<PersonaFieldKey, PersonaField>
  for (const key of PERSONA_FIELD_KEYS) fields[key] = { value: null, source: 'user', aiMeta: null }
  fields.audience = { value: '25-40 岁职场人群', source: 'ai', aiMeta: { promptVersion: 'persona-fill@1', at: '2026-09-25T00:00:00.000Z' } }
  return {
    name: 'AI 工具测评老李',
    platforms: ['xhs', 'douyin'],
    accountStage: 'fresh',
    fields,
    links: [{ platform: 'xhs', url: 'https://xhs.example/laoli', bio: null, sampleText: null }],
    site: { url: null, pastedText: null },
    style: { preset: 'humor', customText: null, strength: 'strict', bannedWords: ['最好'], redLines: ['医疗断言'] },
    assets: { resumeText: null, resumeName: null },
    report: null,
    clonedFrom: null,
    ...overrides,
  }
}

/** One valid stored entry (as a prior put would persist it). */
function entry(overrides: Partial<Omit<PersonaEntry, 'id'>> & { id?: string } = {}): PersonaEntry {
  const { id, ...rest } = overrides
  const fields = {} as Record<PersonaFieldKey, PersonaField>
  for (const key of PERSONA_FIELD_KEYS) fields[key] = { value: null, source: 'user', aiMeta: null }
  return {
    id: (id ?? 'p-1') as PersonaEntry['id'],
    name: '老李',
    platforms: ['xhs'],
    accountStage: 'fresh',
    revision: 3,
    digest: '老李（v3）',
    fields,
    links: [],
    site: { url: null, pastedText: null },
    style: { preset: null, customText: null, strength: 'light', bannedWords: [], redLines: [] },
    assets: { resumeText: null, resumeName: null },
    report: null,
    clonedFrom: null,
    createdAt: '2026-09-25T00:00:00.000Z',
    updatedAt: '2026-09-25T00:00:00.000Z',
    ...rest,
  }
}

function manifest(overrides: Partial<PersonasManifest> = {}): PersonasManifest {
  return { formatVersion: 0, personas: [entry()], ...overrides }
}

describe('parsePersonasManifest', () => {
  it('reads an empty body as the first-write state', () => {
    expect(parsePersonasManifest('')).toEqual({ kind: 'empty' })
  })

  it('names invalid JSON and unsupported versions as refuse-write states', () => {
    expect(parsePersonasManifest('{nope')).toMatchObject({ kind: 'invalid' })
    const wrongVersion = parsePersonasManifest(JSON.stringify({ ...manifest(), formatVersion: 1 }))
    expect(wrongVersion.kind).toBe('invalid')
    if (wrongVersion.kind === 'invalid') expect(wrongVersion.problem).toContain('formatVersion')
    const noArray = parsePersonasManifest(JSON.stringify({ formatVersion: 0 }))
    expect(noArray.kind).toBe('invalid')
  })

  it('round-trips a valid manifest and drops invalid entries by name', () => {
    const invalid = [
      entry({ id: 'p-2', platforms: ['twitter' as never] }),
      entry({ id: 'p-3', fields: { ...entry().fields, whoAmI: { value: 'x', source: 'robot' } } } as unknown as PersonaEntry),
      entry({ id: 'p-4', style: { preset: 'nope' } } as unknown as PersonaEntry),
      entry({ id: 'p-5', report: { markdown: '', sourceRevision: 0, editedByUser: false, generatedAt: '', promptVersion: '' } }),
    ]
    const parsed = parsePersonasManifest(JSON.stringify(manifest({ personas: [entry(), ...invalid] })))
    expect(parsed.kind).toBe('ok')
    if (parsed.kind !== 'ok') return
    expect(parsed.manifest.personas.map(candidate => candidate.id)).toEqual(['p-1'])
    expect(parsed.problems).toHaveLength(4)
    expect(parsed.problems[0]).toContain('dropped one invalid persona record')
  })

  it('sorts stored entries newest-first', () => {
    const parsed = parsePersonasManifest(JSON.stringify(manifest({
      personas: [entry({ id: 'p-old', updatedAt: '2026-09-24T00:00:00.000Z' }), entry({ id: 'p-new', updatedAt: '2026-09-26T00:00:00.000Z' })],
    })))
    expect(parsed.kind).toBe('ok')
    if (parsed.kind !== 'ok') return
    expect(parsed.manifest.personas.map(candidate => candidate.id)).toEqual(['p-new', 'p-old'])
  })
})

describe('personaDigest', () => {
  it('joins the non-empty fields in a fixed order and appends the revision', () => {
    const digest = personaDigest(entry({
      name: '老李',
      revision: 7,
      style: { preset: 'humor', customText: null, strength: 'strict', bannedWords: ['最好'], redLines: [] },
    }))
    expect(digest).toContain('（v7）')
    expect(digest).toContain('幽默网感（严格遵循）')
    expect(digest).not.toContain('最好')
    expect(digest.length).toBeLessThanOrEqual(200)
  })

  it('is deterministic and capped at 200 characters', () => {
    const source = entry({ revision: 12 })
    const first = personaDigest({ ...source, fields: { ...source.fields, whoAmI: { value: '很'.repeat(300), source: 'user', aiMeta: null } } })
    const second = personaDigest({ ...source, fields: { ...source.fields, whoAmI: { value: '很'.repeat(300), source: 'user', aiMeta: null } } })
    expect(first).toBe(second)
    expect(first.length).toBeLessThanOrEqual(200)
  })

  it('falls back to the name when every field is empty', () => {
    expect(personaDigest(entry({ name: '老李' }))).toBe('老李（v3）')
  })
})

describe('putPersonaFile', () => {
  it('creates with revision 1 and recomputes the digest', async () => {
    const file = await storeFile()
    const stored = await putPersonaFile(file, input())
    expect(stored.revision).toBe(1)
    expect(stored.id).toMatch(/^p-|^[0-9a-f-]{36}$/u)
    expect(stored.digest).toContain('25-40 岁职场人群（AI 推断，供参考）'.slice(0, 4))
    expect(stored.digest).toContain('幽默网感（严格遵循）')
    expect(stored.createdAt).toBe(stored.updatedAt)
    const raw = JSON.parse(await readFile(file, 'utf8')) as PersonasManifest
    expect(raw.formatVersion).toBe(0)
    expect(raw.personas).toHaveLength(1)
  })

  it('increments the revision on update and keeps createdAt', async () => {
    const file = await storeFile()
    const created = await putPersonaFile(file, input())
    const updated = await putPersonaFile(file, input({ id: created.id, name: '老李改名' }))
    expect(updated.revision).toBe(2)
    expect(updated.createdAt).toBe(created.createdAt)
    expect(updated.name).toBe('老李改名')
  })

  it('rejects updating an id that no longer exists', async () => {
    const file = await storeFile()
    await putPersonaFile(file, input())
    await expect(putPersonaFile(file, input({ id: 'p-gone' as PersonaEntry['id'] }))).rejects.toThrow('unknown persona')
  })

  it('rejects invalid inputs with the reason', async () => {
    const file = await storeFile()
    await expect(putPersonaFile(file, input({ name: '  ' }))).rejects.toThrow('name')
    await expect(putPersonaFile(file, input({ platforms: ['twitter' as never] }))).rejects.toThrow('unknown platform')
    await expect(putPersonaFile(file, input({ platforms: ['xhs', 'xhs'] }))).rejects.toThrow('must not repeat')
    const noMeta = input({ fields: { ...input().fields, audience: { value: 'x', source: 'ai', aiMeta: null } } })
    await expect(putPersonaFile(file, noMeta)).rejects.toThrow('promptVersion')
  })

  it('refuses to write a file with an unsupported version or dropped entries', async () => {
    const file = await storeFile()
    await writeFile(file, JSON.stringify({ formatVersion: 1, personas: [] }), 'utf8')
    await expect(putPersonaFile(file, input())).rejects.toThrow('refusing to write')
    await writeFile(file, JSON.stringify({ formatVersion: 0, personas: [{ id: 'p-bad' }] }), 'utf8')
    await expect(putPersonaFile(file, input())).rejects.toThrow('resolve the stored invalid entries')
  })
})

describe('putPersonaReportFile', () => {
  it('replaces the report without bumping revision or digest', async () => {
    const file = await storeFile()
    const created = await putPersonaFile(file, input())
    const report = { markdown: '# 账号画像报告', sourceRevision: created.revision, editedByUser: false, generatedAt: '2026-09-25T01:00:00.000Z', promptVersion: 'persona-report@1' }
    const updated = await putPersonaReportFile(file, created.id, report)
    expect(updated.report).toEqual(report)
    expect(updated.revision).toBe(created.revision)
    expect(updated.digest).toBe(created.digest)
  })

  it('keeps editedByUser on a manual edit and rejects unknown ids', async () => {
    const file = await storeFile()
    const created = await putPersonaFile(file, input())
    const report = { markdown: '# 编辑后', sourceRevision: 1, editedByUser: true, generatedAt: '2026-09-25T01:00:00.000Z', promptVersion: 'persona-report@1' }
    await putPersonaReportFile(file, created.id, report)
    const snapshot = await readPersonasFile(file)
    expect(snapshot.personas[0]?.report?.editedByUser).toBe(true)
    await expect(putPersonaReportFile(file, 'p-gone', report)).rejects.toThrow('unknown persona')
    await expect(putPersonaReportFile(file, created.id, { ...report, markdown: '' })).rejects.toThrow('report markdown')
  })
})

describe('deletePersonaFile and readPersonasFile', () => {
  it('removes an entry, ignores unknown ids, and reads back', async () => {
    const file = await storeFile()
    const created = await putPersonaFile(file, input())
    await deletePersonaFile(file, created.id)
    await deletePersonaFile(file, 'p-unknown')
    const snapshot = await readPersonasFile(file)
    expect(snapshot.personas).toEqual([])
    expect(snapshot.problems).toEqual([])
  })

  it('reads a missing file as empty and an unreadable one as a problem', async () => {
    const file = await storeFile()
    expect(await readPersonasFile(file)).toEqual({ personas: [], problems: [] })
    await writeFile(file, 'not json', 'utf8')
    const snapshot = await readPersonasFile(file)
    expect(snapshot.personas).toEqual([])
    expect(snapshot.problems[0]).toContain('not valid JSON')
  })
})
