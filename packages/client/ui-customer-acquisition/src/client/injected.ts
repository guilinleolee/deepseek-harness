/**
 * The server reads the workbench consumes, unwrapped from the Remote
 * envelope by the plugin body. Every wrapper is a stable closure so the
 * pages' read hooks refetch only on their own selector changes.
 * @module @deepseek-ai/dsh-client-ui-customer-acquisition/client/injected
 */

import type {
  AuditListValue, GeoScanListValue, LeadListRequest, LeadListValue,
  OverviewRequest, OverviewValue, SettingsPatchInput, SettingsSnapshotValue,
} from '@deepseek-ai/dsh-customer-acquisition/types'
import type {
  ContentTemplate, GeneratedContent, GeoReport, IcpProfileValue, ScoreRun,
  ScoreTemplateValue, SopTask, SopTemplate,
} from '@deepseek-ai/dsh-customer-acquisition'
import type { PanelController } from './panel-controller.ts'

/** Server reads the panel consumes. */
export interface WorkbenchInjected {
  panel: PanelController
  getOverview: (request: OverviewRequest) => Promise<OverviewValue>
  listLeads: (request?: LeadListRequest) => Promise<LeadListValue>
  listScoreRuns: (request?: { lead_id?: string; limit?: number }) => Promise<{ items: ScoreRun[]; total: number }>
  listIcpProfiles: (enabledOnly?: boolean) => Promise<IcpProfileValue[]>
  listScoreTemplates: (enabledOnly?: boolean) => Promise<ScoreTemplateValue[]>
  listGeoScans: (limit?: number) => Promise<GeoScanListValue>
  getGeoReport: (reportId: string) => Promise<GeoReport>
  listGeneratedContents: (request?: { lead_id?: string; limit?: number }) => Promise<{ items: GeneratedContent[]; total: number }>
  listContentTemplates: (filters?: { type?: string; enabled_only?: boolean }) => Promise<ContentTemplate[]>
  listSopTasks: (request?: { lead_id?: string; status?: 'pending' | 'done' | 'deferred' | 'dropped'; limit?: number; offset?: number }) => Promise<{ items: SopTask[]; total: number }>
  listSopTemplates: (enabledOnly?: boolean) => Promise<SopTemplate[]>
  getSettings: () => Promise<SettingsSnapshotValue>
  updateSettings: (patch: SettingsPatchInput) => Promise<SettingsSnapshotValue>
  listAuditLogs: () => Promise<AuditListValue>
}
