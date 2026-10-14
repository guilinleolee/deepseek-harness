/**
 * Registration of the P3 model-facing tools (modules 4 and 5) on the runtime
 * fiber. Kept as a pure function of its dependencies so tests can drive the
 * tools without the plugin composition; the P0/P1 tools register separately.
 * @module @deepseek-ai/dsh-customer-acquisition/tools/register-p3
 */

import type { Context } from '@deepseek-ai/cordis'
import type { NurtureContentService } from '../content/service.ts'
import type { ResolvedAiPolicy } from '../llm/oneshot.ts'
import type { SopService } from '../sop/service.ts'
import type { PermissionContextService } from '../permission/types.ts'
import {
  contentGenerateTool,
  contentListByLeadTool,
  contentTemplateCreateTool,
  contentTemplateDeleteTool,
  contentTemplateListTool,
  contentTemplateUpdateTool,
} from './content.ts'
import {
  sopGenerateTasksTool,
  sopTaskListTool,
  sopTaskUpdateTool,
  sopTemplateCreateTool,
  sopTemplateDeleteTool,
  sopTemplateListTool,
  sopTemplateUpdateTool,
} from './sop.ts'

/** Tool dependencies: the two module services plus the permission seam and AI policy. */
export interface P3ToolDeps {
  readonly content: NurtureContentService
  readonly sop: SopService
  readonly permission: PermissionContextService
  readonly policy: ResolvedAiPolicy
}

/** Every P3 tool name, in registration order. */
export const P3_TOOL_NAMES = [
  'customer_acquisition_content_generate',
  'customer_acquisition_content_list_by_lead',
  'customer_acquisition_content_template_create',
  'customer_acquisition_content_template_update',
  'customer_acquisition_content_template_list',
  'customer_acquisition_content_template_delete',
  'customer_acquisition_sop_generate_tasks',
  'customer_acquisition_sop_task_list',
  'customer_acquisition_sop_task_update',
  'customer_acquisition_sop_template_create',
  'customer_acquisition_sop_template_update',
  'customer_acquisition_sop_template_list',
  'customer_acquisition_sop_template_delete',
] as const

/**
 * Register the P3 tools (6 nurture-copy + 7 SOP).
 * @param ctx - the runtime fiber's context carrying `ctx.tools` and `ctx.llm`.
 * @param deps - content, sop, permission, and the AI policy.
 * @returns the combined disposer of every registration.
 */
export function registerP3Tools(ctx: Context, deps: P3ToolDeps): () => void {
  const contentDeps = { content: deps.content, permission: deps.permission, policy: deps.policy }
  const sopDeps = { sop: deps.sop, permission: deps.permission }
  const disposers = [
    ctx.tools.register(contentGenerateTool(contentDeps)),
    ctx.tools.register(contentListByLeadTool(contentDeps)),
    ctx.tools.register(contentTemplateCreateTool(contentDeps)),
    ctx.tools.register(contentTemplateUpdateTool(contentDeps)),
    ctx.tools.register(contentTemplateListTool(contentDeps)),
    ctx.tools.register(contentTemplateDeleteTool(contentDeps)),
    ctx.tools.register(sopGenerateTasksTool(sopDeps)),
    ctx.tools.register(sopTaskListTool(sopDeps)),
    ctx.tools.register(sopTaskUpdateTool(sopDeps)),
    ctx.tools.register(sopTemplateCreateTool(sopDeps)),
    ctx.tools.register(sopTemplateUpdateTool(sopDeps)),
    ctx.tools.register(sopTemplateListTool(sopDeps)),
    ctx.tools.register(sopTemplateDeleteTool(sopDeps)),
  ]
  return () => { for (const dispose of disposers) dispose() }
}
