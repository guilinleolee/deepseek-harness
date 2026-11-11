import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import Storage from '@deepseek-ai/dsh-storage'
import * as StorageJson from '@deepseek-ai/dsh-storage-json'
import * as StorageDomain from '@deepseek-ai/dsh-storage-domain'
import WebRuntime from '@deepseek-ai/dsh-web'
import type { WebFetchProvider, WebFetchResult } from '@deepseek-ai/dsh-web'
import { CustomerAcquisitionService, LocalPermissionProvider } from '../src/main-package.ts'
import type {} from '../src/index.ts'
import { GeoDiagnosisService } from '../src/service.ts'

/** When false, the harness skips the geo service so a composition test can let `apply` mount it. */
export interface HarnessOptions {
  readonly premountService?: boolean
}

export interface Harness {
  readonly ctx: Context
  readonly service: GeoDiagnosisService
  readonly web: FakeWeb
  dispose(): Promise<void>
}

/**
 * A scriptable fetch provider: routes map URL → response body (string for a
 * 200 HTML page, or `{ status, body }`); missing routes 404. It records every
 * requested URL and tracks concurrency so serial-fetch assertions work.
 */
export class FakeWeb {
  readonly calls: string[] = []
  private inFlight = 0
  private maxInFlight = 0
  private readonly routes: Map<string, { status: number; body: string }>

  /**
   * @param routes - URL → response; a bare string means HTTP 200 with an HTML body.
   */
  constructor(routes: Record<string, string | { status: number; body: string }>) {
    this.routes = new Map(Object.entries(routes).map(([url, route]) => [
      url,
      typeof route === 'string' ? { status: 200, body: route } : route,
    ]))
  }

  /** Highest number of fetches simultaneously in flight during the run. */
  get peakConcurrency(): number {
    return this.maxInFlight
  }

  /**
   * Re-script one route after construction (two-round scan tests flip the
   * site between rounds).
   * @param url - the route URL.
   * @param route - the new response.
   */
  setRoute(url: string, route: string | { status: number; body: string }): void {
    this.routes.set(url, typeof route === 'string' ? { status: 200, body: route } : route)
  }

  /** @returns the provider the real WebRuntime registers. */
  toProvider(): WebFetchProvider {
    return {
      id: 'geo-test-fetch',
      available: () => true,
      fetch: async (request): Promise<WebFetchResult> => {
        this.calls.push(request.url)
        this.inFlight += 1
        this.maxInFlight = Math.max(this.maxInFlight, this.inFlight)
        try {
          await new Promise(resolve => setTimeout(resolve, 5))
          const route = this.routes.get(request.url)
          if (route === undefined) {
            return { url: request.url, statusCode: 404, body: { kind: 'text', content: 'not found' }, truncated: false }
          }
          return { url: request.url, statusCode: route.status, body: { kind: 'html', content: route.body }, truncated: false }
        } finally {
          this.inFlight -= 1
        }
      },
    }
  }
}

/** Compose the storage + web + service stack the GEO module runs on. */
export async function setupHarness(
  routes: Record<string, string | { status: number; body: string }>,
  options: HarnessOptions = {},
): Promise<Harness> {
  const premountService = options.premountService ?? true
  const root = await mkdtemp(join(tmpdir(), 'dsh-customer-acquisition-geo-test-'))
  const ctx = new Context()
  const web = new FakeWeb(routes)
  try {
    await ctx.plugin(Storage)
    await ctx.plugin(StorageJson, { root })
    await ctx.plugin(StorageDomain, { backend: 'json' })
    await ctx.plugin(LocalPermissionProvider)
    await ctx.plugin(CustomerAcquisitionService).await()
    await ctx.plugin(WebRuntime)
    ctx.web.registerFetchProvider(web.toProvider())
    if (premountService) await ctx.plugin(GeoDiagnosisService).await()
  } catch (error) {
    await ctx.fiber.dispose()
    await rm(root, { recursive: true, force: true })
    throw error
  }
  return {
    ctx,
    service: ctx.geoDiagnosis!,
    web,
    async dispose() {
      await ctx.fiber.dispose()
      await rm(root, { recursive: true, force: true })
    },
  }
}

/** The operator every local-resolution call yields. */
export async function localOperator(harness: Harness) {
  return harness.ctx.permissionContext.resolve({ via: 'agent' })
}
