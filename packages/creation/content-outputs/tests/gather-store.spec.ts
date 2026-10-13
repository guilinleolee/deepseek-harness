import { mkdtemp, mkdir, readFile, readdir, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import type { GatherAssetMove, GatherAssetWrite, GatherManifest, GatherMaterial } from '../src/types.ts'
import {
  GATHER_MANIFEST_FILENAME, GATHER_QUOTA_PER_SOURCE, applyRetentionQuota,
  deleteAssetFile, moveAssetFile, parseGatherManifest, readGatherAssetFile,
  resolveAssetPath, resolveAssetsDir, writeAssetFile, writeGatherManifestFile,
} from '../src/gather/store.ts'

async function library(): Promise<string> {
  return mkdtemp(join(tmpdir(), 'dsh-gather-store-'))
}

/** One valid manifest entry over the required fields, overridden per test. */
function material(overrides: Partial<Omit<GatherMaterial, 'id'>> & { id?: string } = {}): GatherMaterial {
  const { id, ...rest } = overrides
  return {
    id: (id ?? 'guid-1') as GatherMaterial['id'],
    sourceId: 'source-1',
    sourceName: '示例源',
    title: '一条素材',
    url: 'https://example.com/post-1',
    gatheredAt: '2026-09-25T00:00:00.000Z',
    status: 'unread',
    ...rest,
  }
}

describe('gather path guards', () => {
  it('rejects theme names that are not plain project directories', () => {
    for (const theme of ['', '.', '..', 'a/b', 'a\\b', '_system', '.hidden', 'a\nb']) {
      expect(() => resolveAssetsDir('/root', theme)).toThrow()
    }
    expect(resolveAssetsDir('/root', 'autumn-note')).toBe(join('/root', 'autumn-note', 'assets'))
  })

  it('rejects asset file names that could escape the assets directory', () => {
    for (const file of ['', '.', '..', 'a/b', 'a\\b', '.env', 'a\nb']) {
      expect(() => resolveAssetPath('/root', 'theme', file)).toThrow()
    }
    expect(resolveAssetPath('/root', 'theme', 'body-1.html')).toBe(join('/root', 'theme', 'assets', 'body-1.html'))
  })
})

describe('parseGatherManifest', () => {
  it('accepts a valid document', () => {
    const { manifest, problems } = parseGatherManifest(JSON.stringify({ formatVersion: 0, materials: [material()] }))
    expect(problems).toEqual([])
    expect(manifest.materials).toHaveLength(1)
  })

  it('names broken JSON, wrong versions, and invalid entries without dropping the rest', () => {
    const broken = parseGatherManifest('{not json')
    expect(broken.manifest.materials).toEqual([])
    expect(broken.problems).toEqual(['gather manifest is not valid JSON'])

    const future = parseGatherManifest(JSON.stringify({ formatVersion: 1, materials: [] }))
    expect(future.problems).toEqual(['unsupported gather manifest formatVersion 1'])

    const mixed = parseGatherManifest(JSON.stringify({
      formatVersion: 0,
      materials: [material(), { id: 'bad', status: 'unread' }],
    }))
    expect(mixed.manifest.materials).toHaveLength(1)
    expect(mixed.problems).toHaveLength(1)
  })
})

describe('applyRetentionQuota', () => {
  it('keeps favorite and picked entries regardless of quota', () => {
    const exempt = [
      material({ id: 'a', status: 'favorite' }),
      material({ id: 'b', status: 'picked' }),
    ]
    const result = applyRetentionQuota(exempt)
    expect(result.dropped).toEqual([])
    expect(result.kept).toHaveLength(2)
  })

  it('keeps only the newest unread/read entries per source', () => {
    const materials: GatherMaterial[] = []
    for (let index = 0; index < GATHER_QUOTA_PER_SOURCE + 3; index += 1) {
      materials.push(material({
        id: `old-${index}`,
        sourceId: 'source-1',
        gatheredAt: new Date(Date.UTC(2026, 0, 1 + index)).toISOString(),
      }))
    }
    materials.push(material({ id: 'other-source', sourceId: 'source-2' }))
    const result = applyRetentionQuota(materials)
    expect(result.dropped.map(entry => entry.id)).toEqual(['old-2', 'old-1', 'old-0'])
    expect(result.kept.some(entry => entry.id === 'other-source')).toBe(true)
  })
})

describe('writeAssetFile', () => {
  it('sanitizes html snapshots before they reach disk', async () => {
    const root = await library()
    const write: GatherAssetWrite = {
      theme: 'autumn-note',
      file: 'body-1.html',
      content: '<p>正文</p><script>alert(1)</script><a href="javascript:alert(2)">x</a>',
    }
    const result = await writeAssetFile(root, write)
    expect(result.truncated).toBe(false)
    const stored = await readFile(resolveAssetPath(root, 'autumn-note', 'body-1.html'), 'utf8')
    expect(stored).toContain('<p>正文</p>')
    expect(stored).not.toContain('script')
    expect(stored).not.toContain('javascript:')
  })

  it('truncates oversized snapshots at a tag boundary', async () => {
    const root = await library()
    const result = await writeAssetFile(root, {
      theme: 'autumn-note',
      file: 'body-big.html',
      content: `<p>${'字'.repeat(100_100)}</p>`,
    })
    expect(result.truncated).toBe(true)
    const stored = await readFile(resolveAssetPath(root, 'autumn-note', 'body-big.html'), 'utf8')
    expect(stored.length).toBeLessThan(100_100)
    // The cut lands right after a complete tag (the opening `<p>` here), never
    // inside one — no dangling `<` may survive at the end.
    expect(stored.startsWith('<p>')).toBe(true)
    expect(stored.endsWith('<')).toBe(false)
  })

  it('stores non-html assets verbatim under the hard cap', async () => {
    const root = await library()
    await writeAssetFile(root, { theme: 'autumn-note', file: 'note.md', content: '# 记录' })
    await expect(readFile(resolveAssetPath(root, 'autumn-note', 'note.md'), 'utf8')).resolves.toBe('# 记录')
    await expect(writeAssetFile(root, { theme: 'autumn-note', file: 'huge.md', content: 'x'.repeat(2_000_001) }))
      .rejects.toThrow('exceeds')
  })
})

describe('readGatherAssetFile', () => {
  it('reads a stored snapshot and answers undefined for absent files', async () => {
    const root = await library()
    await writeAssetFile(root, { theme: 'theme', file: 'body-1.html', content: '<p>ok</p>' })
    await expect(readGatherAssetFile(root, 'theme', 'body-1.html')).resolves.toBe('<p>ok</p>')
    await expect(readGatherAssetFile(root, 'theme', 'absent.html')).resolves.toBeUndefined()
  })
})

describe('moveAssetFile', () => {
  it('renames within one theme and refuses an existing destination', async () => {
    const root = await library()
    await writeAssetFile(root, { theme: 'theme', file: 'a.html', content: '<p>a</p>' })
    const rename: GatherAssetMove = { fromTheme: 'theme', from: 'a.html', toTheme: 'theme', to: 'b.html' }
    await moveAssetFile(root, rename)
    await expect(readFile(resolveAssetPath(root, 'theme', 'b.html'), 'utf8')).resolves.toBe('<p>a</p>')
    await expect(moveAssetFile(root, { fromTheme: 'theme', from: 'a.html', toTheme: 'theme', to: 'b.html' }))
      .rejects.toThrow('already exists')
  })

  it('moves a snapshot across themes, creating the destination assets directory', async () => {
    const root = await library()
    await writeAssetFile(root, { theme: 'from-theme', file: 'body-1.html', content: '<p>正文</p>' })
    await moveAssetFile(root, { fromTheme: 'from-theme', from: 'body-1.html', toTheme: 'to-theme', to: 'body-1.html' })
    await expect(readFile(resolveAssetPath(root, 'to-theme', 'body-1.html'), 'utf8')).resolves.toBe('<p>正文</p>')
    await expect(readGatherAssetFile(root, 'from-theme', 'body-1.html')).resolves.toBeUndefined()
  })
})

describe('writeGatherManifestFile', () => {
  it('stores the manifest and deletes snapshots only for quota-dropped entries', async () => {
    const root = await library()
    // One favorite (old, exempt), the newest unread up to the quota, and one
    // unread older than the quota whose snapshot must be removed.
    const favorite = material({ id: 'favorite', status: 'favorite', bodyFile: 'favorite.html', gatheredAt: '2026-01-01T00:00:00.000Z' })
    const dropped = material({ id: 'dropped', bodyFile: 'dropped.html', gatheredAt: '2026-01-02T00:00:00.000Z' })
    const kept: GatherMaterial[] = Array.from({ length: GATHER_QUOTA_PER_SOURCE }, (_, index) => material({
      id: `kept-${index}`,
      gatheredAt: new Date(Date.UTC(2026, 0, 3 + index)).toISOString(),
    }))
    await writeAssetFile(root, { theme: 'theme', file: 'favorite.html', content: '<p>f</p>' })
    await writeAssetFile(root, { theme: 'theme', file: 'dropped.html', content: '<p>d</p>' })

    const stored = await writeGatherManifestFile(root, 'theme', { formatVersion: 0, materials: [favorite, dropped, ...kept] })
    expect(stored.materials).toHaveLength(GATHER_QUOTA_PER_SOURCE + 1)
    expect(stored.materials.some(entry => entry.id === 'dropped')).toBe(false)
    expect(stored.materials.some(entry => entry.id === 'favorite')).toBe(true)
    const onDisk = JSON.parse(await readFile(join(resolveAssetsDir(root, 'theme'), GATHER_MANIFEST_FILENAME), 'utf8')) as GatherManifest
    expect(onDisk.materials).toHaveLength(GATHER_QUOTA_PER_SOURCE + 1)
    // The trimmed entry's snapshot is removed only after the trimmed manifest
    // is durable; the favorite's exempt snapshot stays.
    await expect(readGatherAssetFile(root, 'theme', 'dropped.html')).resolves.toBeUndefined()
    await expect(readGatherAssetFile(root, 'theme', 'favorite.html')).resolves.toBe('<p>f</p>')
  })

  it('rejects an invalid manifest instead of repairing it', async () => {
    const root = await library()
    const broken = { formatVersion: 0, materials: [{ id: 'bad' }] } as unknown as GatherManifest
    await expect(writeGatherManifestFile(root, 'theme', broken)).rejects.toThrow('invalid gather material')
  })
})

describe('deleteAssetFile and sweepOrphanTempFiles', () => {
  it('deletes an asset as a no-op when absent', async () => {
    const root = await library()
    await expect(deleteAssetFile(root, 'theme', 'absent.html')).resolves.toBeUndefined()
  })

  it('sweeps orphan temp files across themes without touching named assets', async () => {
    const { sweepOrphanTempFiles } = await import('../src/gather/store.ts')
    const root = await library()
    await writeAssetFile(root, { theme: 'theme', file: 'body.html', content: '<p>x</p>' })
    const assetsDir = resolveAssetsDir(root, 'theme')
    await writeFile(join(assetsDir, 'body.abc123.tmp'), 'orphan')
    await sweepOrphanTempFiles(root)
    const names = await readdir(assetsDir)
    expect(names).toContain('body.html')
    expect(names).not.toContain('body.abc123.tmp')
  })

  it('answers an absent library root with no sweep and no error', async () => {
    const { sweepOrphanTempFiles } = await import('../src/gather/store.ts')
    await expect(sweepOrphanTempFiles(join(await library(), 'absent'))).resolves.toBeUndefined()
  })
})

describe('gather manifest directory convention', () => {
  it('writes the manifest under assets/ with the underscore-prefixed name', async () => {
    const root = await library()
    await writeGatherManifestFile(root, 'theme', { formatVersion: 0, materials: [] })
    const assetsDir = resolveAssetsDir(root, 'theme')
    await expect(readFile(join(assetsDir, GATHER_MANIFEST_FILENAME), 'utf8')).resolves.toBe('{\n  "formatVersion": 0,\n  "materials": []\n}\n')
  })
})

describe('manifest problems guard read', () => {
  it('readGatherManifestFile reports problems from a damaged file', async () => {
    const { readGatherManifestFile } = await import('../src/gather/store.ts')
    const root = await library()
    await mkdir(resolveAssetsDir(root, 'theme'), { recursive: true })
    await writeFile(join(resolveAssetsDir(root, 'theme'), GATHER_MANIFEST_FILENAME), '{broken')
    const read = await readGatherManifestFile(root, 'theme')
    expect(read.manifest.materials).toEqual([])
    expect(read.problems).toEqual(['gather manifest is not valid JSON'])
    const missing = await readGatherManifestFile(root, 'other')
    expect(missing.problems).toEqual([])
  })
})
