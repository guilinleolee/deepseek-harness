import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import Storage from '@deepseek-ai/dsh-storage'
import * as StorageJson from '@deepseek-ai/dsh-storage-json'
import * as StorageDomain from '@deepseek-ai/dsh-storage-domain'
import { QuantResearchService } from '../src/service.ts'
import { saveNote } from '../src/pet/notes.ts'
import type { Account } from '../src/domain/spec.ts'

export interface Harness {
  readonly ctx: Context
  readonly service: QuantResearchService
  seedAccount(account: Account): Promise<void>
  seedNote(input: { title: string; body: string; symbol?: string; tags?: string[] }): Promise<void>
  dispose(): Promise<void>
}

/** Compose the real storage stack and the service over it. */
export async function setupHarness(): Promise<Harness> {
  const root = await mkdtemp(join(tmpdir(), 'dsh-quant-service-test-'))
  const ctx = new Context()
  try {
    await ctx.plugin(Storage)
    await ctx.plugin(StorageJson, { root })
    await ctx.plugin(StorageDomain, { backend: 'json' })
    await ctx.plugin(QuantResearchService).await()
    const service = ctx.quantResearch
    // Seed through the service's own domain handle: the reservation is
    // single-open, so a second open() would trip 'already-open'.
    const domain = service.requireDomain()
    return {
      ctx,
      service,
      async seedAccount(account) {
        await domain.table('accounts').put(account.id, account)
      },
      async seedNote(input) {
        await saveNote(domain.table('research_notes'), input)
      },
      async dispose() {
        await ctx.fiber.dispose()
        await rm(root, { recursive: true, force: true })
      },
    }
  } catch (error) {
    await ctx.fiber.dispose()
    await rm(root, { recursive: true, force: true })
    throw error
  }
}
