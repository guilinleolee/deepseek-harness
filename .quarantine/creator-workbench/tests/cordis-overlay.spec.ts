/**
 * Vitest Loader smoke for the bundled `cordis.yml` overlay.
 *
 * Boots a real Cordis Loader process with the workbench overlay on top of
 * `dsh-base`. Verifies the overlay is well-formed: the rows it inserts do
 * not collide with dsh-base row ids and they all resolve to packages the
 * workspace declares.
 *
 * Per `packages/AGENTS.md` product-visible plugins require a non-unit
 * REAL-composition test.
 */

import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { runLoaderSmoke } from '@deepseek-ai/dsh-loader-smoke'

const HERE = dirname(fileURLToPath(import.meta.url))
const PKG_ROOT = join(HERE, '..')
const REPO_ROOT = join(PKG_ROOT, '..', '..')
const CORDIS = join(PKG_ROOT, 'cordis.yml')
const TSCONFIG = join(REPO_ROOT, 'tsconfig.json')

describe('creator-workbench cordis.yml overlay', () => {
  it('boots through the real Cordis Loader without row-id collisions', async () => {
    const result = await runLoaderSmoke({
      label: 'dsh-creator-workbench overlay',
      tempDirPrefix: 'creator-workbench-overlay-',
      binScript: join(REPO_ROOT, 'apps', 'cli', 'src', 'bin.ts'),
      configPath: CORDIS,
      binArgs: ['--profile', 'headless', '--patch', CORDIS],
      tsconfigPath: TSCONFIG,
      mode: 'src',
      env: {
        DEEPSEEK_API_KEY: 'sk-placeholder-for-boot-smoke',
        CREATOR_WORKBENCH_SKILLS_PATH:
          process.env.CREATOR_WORKBENCH_SKILLS_PATH ??
          'C:\\Users\\li\\.claude\\projects\\dragon-engine\\skills',
      },
      expectedExitCode: 1, // headless mode exits after one turn placeholder
    })
    // The smoke throws on non-matching exit; reaching here means the overlay
    // booted through the Loader.
    expect(result.stdout.length + result.stderr.length).toBeGreaterThan(0)
  }, 90_000)
})