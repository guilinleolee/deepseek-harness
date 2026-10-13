import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import Storage from '@deepseek-ai/dsh-storage'
import * as StorageJson from '@deepseek-ai/dsh-storage-json'
import * as StorageDomain from '@deepseek-ai/dsh-storage-domain'
import { LocalPermissionProvider } from '../src/permission/local-provider.ts'
import CustomerAcquisitionService from '../src/service.ts'

export interface Harness {
  readonly ctx: Context
  readonly service: CustomerAcquisitionService
  dispose(): Promise<void>
}

/** Compose only the storage stack — plugin-composition tests install the services themselves. */
export async function setupStorageOnly(): Promise<{ readonly ctx: Context; dispose(): Promise<void> }> {
  const root = await mkdtemp(join(tmpdir(), 'dsh-customer-acquisition-test-'))
  const ctx = new Context()
  try {
    await ctx.plugin(Storage)
    await ctx.plugin(StorageJson, { root })
    await ctx.plugin(StorageDomain, { backend: 'json' })
  } catch (error) {
    await ctx.fiber.dispose()
    await rm(root, { recursive: true, force: true })
    throw error
  }
  return {
    ctx,
    async dispose() {
      await ctx.fiber.dispose()
      await rm(root, { recursive: true, force: true })
    },
  }
}

/** Compose the full service over the real storage hub/domain/JSON backend. */
export async function setupHarness(): Promise<Harness> {
  const storage = await setupStorageOnly()
  const { ctx } = storage
  try {
    await ctx.plugin(LocalPermissionProvider)
    await ctx.plugin(CustomerAcquisitionService).await()
  } catch (error) {
    await storage.dispose()
    throw error
  }
  return {
    ctx,
    service: ctx.customerAcquisition,
    dispose: () => storage.dispose(),
  }
}
