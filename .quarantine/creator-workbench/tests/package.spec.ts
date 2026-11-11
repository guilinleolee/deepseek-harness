/**
 * Vitest spec for `@deepseek-ai/dsh-creator-workbench`.
 *
 * Covers the package's pure exports (paths, supported platforms, plugin
 * shape) and the bundled `cordis.yml` overlay.
 */

import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import {
  cordisConfigPath,
  name,
  packageRoot,
  promptsRoot,
  scriptsRoot,
  sopRoot,
  supportedPlatforms,
} from '../src/index.ts'

describe('@deepseek-ai/dsh-creator-workbench', () => {
  it('exposes named plugin metadata expected by the Loader', () => {
    expect(name).toBe('creator-workbench')
  })

  it('bundles the SOP, prompts, scripts, and cordis overlay at known paths', () => {
    expect(cordisConfigPath).toBe(join(packageRoot, 'cordis.yml'))
    expect(sopRoot).toBe(join(packageRoot, 'sop'))
    expect(promptsRoot).toBe(join(packageRoot, 'prompts', 'platforms'))
    expect(scriptsRoot).toBe(join(packageRoot, 'scripts'))
    expect(existsSync(cordisConfigPath)).toBe(true)
    expect(existsSync(join(sopRoot, 'creator-workflow.md'))).toBe(true)
    expect(existsSync(scriptsRoot)).toBe(true)
  })

  it('ships a default prompt template for every supported platform', () => {
    for (const platform of supportedPlatforms) {
      const template = join(promptsRoot, `${platform}.md`)
      expect(existsSync(template), `missing template for ${platform}`).toBe(true)
    }
  })

  it('ships an SOP plus five gate SOPs', () => {
    const expected = [
      'creator-workflow.md',
      'gate-grammar.md',
      'gate-factual.md',
      'gate-compliance.md',
      'gate-tone.md',
      'gate-structure.md',
    ]
    for (const file of expected) {
      expect(existsSync(join(sopRoot, file)), `missing SOP ${file}`).toBe(true)
    }
  })

  it('packages the export and gate scripts', () => {
    for (const script of ['run_gate.py', 'export_content.ps1', 'illustrate.ps1', 'scan_inputs.ps1']) {
      expect(existsSync(join(scriptsRoot, script)), `missing script ${script}`).toBe(true)
    }
  })

  it('cordis.yml is a single patch overlay, not a full composition', () => {
    const yaml = readFileSync(cordisConfigPath, 'utf-8')
    // The patch starts with a top-level `- insert:` block; full compositions
    // start with a flat `- id: ...` row.
    expect(yaml).toMatch(/^\s*-\s*insert:/m)
  })
})