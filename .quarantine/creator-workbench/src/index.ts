/**
 * Creator Workbench Cordis plugin.
 *
 * This package exposes the SOPs, platform prompt templates, quality-gate
 * scripts, and export transforms as a single DSH-native composition. The
 * package's primary surface is the `cordis.yml` overlay loaded via
 * `--patch`; this `apply` function is the in-process equivalent for tests
 * and for users who want to drive the workbench through the JSON-RPC
 * runtime.
 *
 * The plugin intentionally exposes named exports only because the Loader
 * default-export unwrap would discard the `Config` schema (see
 * docs/postmortem/0001-acp-default-export-drops-inject.md).
 *
 * @module @deepseek-ai/dsh-creator-workbench
 */

import type { Context } from '@deepseek-ai/cordis'
import * as fs from 'node:fs'
import * as path from 'node:path'
import { fileURLToPath } from 'node:url'

/** Resolved path of this package root. */
export const packageRoot: string = (() => {
  const here = path.dirname(fileURLToPath(import.meta.url))
  // Source location during development; `lib/` location in a published build.
  return path.resolve(here, '..')
})()

/** Resolved path of the bundled `cordis.yml` overlay. */
export const cordisConfigPath: string = path.join(packageRoot, 'cordis.yml')

/** Resolved path of the bundled SOP directory. */
export const sopRoot: string = path.join(packageRoot, 'sop')

/** Resolved path of the bundled platform prompt templates. */
export const promptsRoot: string = path.join(packageRoot, 'prompts', 'platforms')

/** Resolved path of the bundled CLI scripts. */
export const scriptsRoot: string = path.join(packageRoot, 'scripts')

/** List of platforms for which this package ships a default prompt template. */
export const supportedPlatforms: readonly string[] = [
  'wechat',
  'xiaohongshu',
  'douyin',
  'toutiao',
  'zhihu',
  'bilibili',
] as const

/** Config schema for the Creator Workbench plugin. */
export interface Config {
  /** Override the agent spine persona. Defaults to the value in `cordis.yml`. */
  readonly persona?: string
  /** Override the Tianlong Engine skills root. */
  readonly skillsPath?: string
  /** Override the workbench working directory. Defaults to `process.cwd()`. */
  readonly workRoot?: string
}

export const name = 'creator-workbench'

export const inject = ['agent-instructions']

/**
 * Apply the Creator Workbench plugin to a Cordis context. The agent spine
 * the patch overlay configures already owns the persona; this function only
 * contributes a workspace-level agent instruction pointing the agent at the
 * SOP and the platform prompt templates. The instruction is short so it
 * does not invalidate the KV cache across turns.
 */
export function apply(ctx: Context, config: Config = {}): void {
  const workRoot = config.workRoot ?? process.cwd()
  const sopPath = path.join(sopRoot, 'creator-workflow.md')
  const persona = config.persona ?? readDefaultPersona(workRoot)

  ctx.effect(() => {
    ctx.agentInstructions.register({
      id: 'creator-workbench:sop',
      priority: 50,
      body: [
        '# Creator Workbench SOP',
        '',
        persona ? `Role: ${persona}\n` : '',
        `Authoritative SOP path (read with the fs tool): ${sopPath}`,
        `Authoritative platform prompt templates: ${promptsRoot}`,
        'Available CLI scripts (invoke via bash tool):',
        `  - python ${path.join(scriptsRoot, 'run_gate.py')} <gate> --draft <path>`,
        `  - pwsh ${path.join(scriptsRoot, 'export_content.ps1')} -TaskId ... -Platforms ...`,
        `  - pwsh ${path.join(scriptsRoot, 'illustrate.ps1')} -InputPath ... -OutputDir ...`,
      ].filter(Boolean).join('\n'),
    })
  })
}

function readDefaultPersona(workRoot: string): string {
  const candidates = [
    path.join(workRoot, 'sop', 'creator-workflow.md'),
    sopPath,
  ]
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      // The persona block in the SOP is intentionally minimal; this function
      // returns an empty string so the cordis.yml persona takes precedence.
      return ''
    }
  }
  return ''
}