import { mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { afterEach, describe, expect, it } from 'vitest'
import { Context } from '@deepseek-ai/cordis'
import Include from '@deepseek-ai/cordis-plugin-include'
import Loader from '@deepseek-ai/cordis-plugin-loader'
import Storage from '@deepseek-ai/dsh-storage'
import * as StorageDomain from '@deepseek-ai/dsh-storage-domain'
import * as StorageJson from '@deepseek-ai/dsh-storage-json'
import { remoteMethods } from '@deepseek-ai/dsh-typert-protocol'
import SystemPrompt from '@deepseek-ai/dsh-system-prompt'
import { ToolRuntime } from '@deepseek-ai/dsh-tools'
import apply from '../src/index.ts'

let root: string | undefined
const contexts: Context[] = []

afterEach(async () => {
  await Promise.all(contexts.splice(0).map(ctx => ctx.fiber.dispose()))
  if (root !== undefined) await rm(root, { recursive: true, force: true })
  root = undefined
})

async function loadComposition(configPath: string): Promise<Context> {
  const ctx = new Context()
  contexts.push(ctx)
  ctx.baseUrl = pathToFileURL(root as string).href + '/'
  await ctx.plugin(Loader)
  ctx.loader.builtins.include = Include
  const modules = new Map<string, unknown>([
    ['@deepseek-ai/dsh-system-prompt', SystemPrompt],
    ['@deepseek-ai/dsh-tools', ToolRuntime],
    ['@deepseek-ai/dsh-storage', Storage],
    ['@deepseek-ai/dsh-storage-json', StorageJson],
    ['@deepseek-ai/dsh-storage-domain', StorageDomain],
    ['@deepseek-ai/dsh-customer-acquisition', { default: apply }],
  ])
  ctx.loader.internal = {
    version: 'v2',
    async import(specifier: string) {
      if (!modules.has(specifier)) throw new Error(`unexpected Loader import: ${specifier}`)
      return modules.get(specifier)
    },
  } as unknown as NonNullable<typeof ctx.loader.internal>
  await ctx.loader.create({
    name: 'cordis:include',
    config: { path: pathToFileURL(configPath).href },
  })
  await ctx.loader.await()
  const unloaded = [...ctx.loader.entries()]
    .filter(entry => entry.fiber === undefined && !entry.disabled)
    .map(entry => entry.options.name)
  expect(unloaded).toEqual([])
  return ctx
}

describe('customer-acquisition through a real Loader composition', () => {
  it('installs the patch rows, provides both services, registers the P0 tools, and persists settings across a restart', async () => {
    root = await mkdtemp(join(tmpdir(), 'dsh-customer-acquisition-loader-'))
    const configPath = join(root, 'cordis.yml')
    await writeFile(configPath, [
      "- name: '@deepseek-ai/dsh-system-prompt'",
      "- name: '@deepseek-ai/dsh-tools'",
      "- name: '@deepseek-ai/dsh-storage'",
      "- name: '@deepseek-ai/dsh-storage-json'",
      '  config:',
      `    root: ${JSON.stringify(join(root, 'storage'))}`,
      "- name: '@deepseek-ai/dsh-storage-domain'",
      '  config:',
      '    backend: json',
      "- name: '@deepseek-ai/dsh-customer-acquisition'",
      '',
    ].join('\n'))

    const first = await loadComposition(configPath)
    expect(first.customerAcquisition.typertRemote.namespace).toBe('customerAcquisition')
    // remoteMethods markers carry the implementing method names; the wire
    // names (@Remote arguments) are getSettings / updateSettings / listAuditLogs.
    expect(remoteMethods(first.customerAcquisition).map(marker => marker.method))
      .toEqual(['getSettingsRemote', 'updateSettingsRemote', 'listAuditLogs'])
    for (const name of [
      'customer_acquisition_settings_get',
      'customer_acquisition_settings_set',
      'customer_acquisition_audit_list',
      'customer_acquisition_audit_export',
    ]) {
      expect(first.tools.get(name), name).toBeDefined()
    }
    const permission = await first.permissionContext.resolve({ via: 'agent' })
    expect(permission).toMatchObject({ userId: 'local-default', capabilities: { lead_scope: 'all' } })

    await first.fiber.dispose()
    contexts.splice(contexts.indexOf(first), 1)

    const second = await loadComposition(configPath)
    // The settings global slot and the audit row survive the cold restart —
    // the medium, not the process, is the authority.
    expect(second.customerAcquisition.getSettings()).toMatchObject({ geo_max_pages: 10 })
    expect(second.permissionContext.resolve !== undefined).toBe(true)
    await second.customerAcquisition.updateSettings(
      { geo_max_pages: 12 },
      await second.permissionContext.resolve({ via: 'agent' }),
      'agent',
    )
    await second.fiber.dispose()
    contexts.splice(contexts.indexOf(second), 1)

    const third = await loadComposition(configPath)
    expect(third.customerAcquisition.getSettings().geo_max_pages).toBe(12)
    expect(third.customerAcquisition.listAudit({}).total).toBe(1)
  })
})
