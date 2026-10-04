/**
 * GEO (generative-engine optimization) website AI-search-visibility
 * diagnosis — module 1 of the customer-acquisition feature, shipped as a
 * sibling package so P1 and P2 file ownership never intersect. Depends
 * one-way on the main plugin's frozen v1 data contract (types + zod
 * schemas) and its audit service; the main plugin never depends on this
 * package.
 * @module @deepseek-ai/dsh-customer-acquisition-geo
 */

import type { Context } from '@deepseek-ai/cordis'
import { installGeoBoundaryGate } from './boundary.ts'
import { operatorRequest } from './main-package.ts'
import { GeoDiagnosisService } from './service.ts'
import { registerGeoTools } from './tools.ts'

export { GEO_TOOL_PREFIX, inspectGeoToolCall, installGeoBoundaryGate } from './boundary.ts'
export { GEO_USER_AGENT, ALLOW_ALL_ROBOTS, isDisallowed, parseRobots } from './robots.ts'
export type { DisallowRule, RobotsRules } from './robots.ts'
export { crawlSite, extractSameOriginLinks } from './fetcher.ts'
export type { CrawlOptions, CrawlResult, FetchedPage, FetchOne } from './fetcher.ts'
export { analyzeSite } from './analyze.ts'
export type { FindingSeed, GeoAnalysis } from './analyze.ts'
export { GeoDiagnosisService, renderReportMd } from './service.ts'
export type { ScanInput } from './service.ts'
export { geoCompareTool, geoHistoryTool, geoReportGetTool, geoScanTool, registerGeoTools } from './tools.ts'
export type {
  GeoCompareValue, GeoFindingValue, GeoHistoryItem, GeoHistoryRequest,
  GeoReportValue, GeoScanValue,
} from './types.ts'

declare module '@deepseek-ai/cordis' {
  interface Context {
    geoDiagnosis: GeoDiagnosisService
  }
}

/** Services required before the plugin body runs. */
export const inject = ['storageDomain', 'tools', 'customerAcquisition', 'web'] as const

/**
 * Compose the plugin: the GEO diagnosis service installs first (it resolves
 * the domain the main plugin opened), then a runtime fiber declares `tools`,
 * `web`, the permission seam, and the service, and registers the four GEO
 * tools plus the geo fetch-boundary gate. Every registration is an effect;
 * the returned disposer unwinds runtime and service.
 * @param ctx - host context providing storage, tools, the web capability, and the main plugin's service.
 * @returns resolution to the disposer releasing every registration.
 */
export async function apply(ctx: Context): Promise<() => Promise<void>> {
  const serviceFiber = await ctx.plugin(GeoDiagnosisService).await()
  const runtimeFiber = await ctx.plugin({
    name: 'customer-acquisition-geo:runtime',
    inject: ['tools', 'web', 'permissionContext', 'geoDiagnosis'],
    apply: (runtimeCtx: Context) => {
      const service = runtimeCtx.geoDiagnosis
      const permission = runtimeCtx.permissionContext
      const unregisterTools = registerGeoTools(runtimeCtx, service, permission)
      const uninstallGate = installGeoBoundaryGate(runtimeCtx, (name, reason, agentId) => {
        // A failed denial audit never un-denies the call; containment is
        // warn-and-continue, mirroring the main plugin's gate.
        void runtimeCtx.customerAcquisition.recordComplianceDeny(name, reason, operatorRequest('agent', agentId))
          .catch((error: unknown) => { runtimeCtx.logger.warn(`customer-acquisition-geo: denial audit failed: ${String(error)}`) })
      })
      return () => {
        uninstallGate()
        unregisterTools()
      }
    },
  }).await()
  return async () => {
    await runtimeFiber.dispose()
    await serviceFiber.dispose()
  }
}

export default apply
