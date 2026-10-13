import { Context } from '@deepseek-ai/cordis'
import { describe, expect, it } from 'vitest'
import LicensePolicy from '../src/index'

interface Harness {
  ctx: Context
  cleanup: () => void
}

async function makeHarness(config?: { rejectUnknown?: boolean; agplAttribution?: string }): Promise<Harness> {
  const ctx = new Context()
  await ctx.plugin(LicensePolicy, config ?? {})
  return {
    ctx,
    cleanup: () => undefined,
  }
}

describe('licensePolicy', () => {
  it('classifies MIT and Apache-2.0 variants case-insensitively', async () => {
    const h = await makeHarness()
    expect(h.ctx.licensePolicy.normalize('MIT')).toBe('mit')
    expect(h.ctx.licensePolicy.normalize('mit')).toBe('mit')
    expect(h.ctx.licensePolicy.normalize(' Apache-2.0 ')).toBe('apache-2.0')
    expect(h.ctx.licensePolicy.normalize('APACHE-2.0')).toBe('apache-2.0')
    expect(h.ctx.licensePolicy.normalize('(Apache-2.0)')).toBe('apache-2.0')
  })

  it('classifies BSD-3-Clause variants correctly', async () => {
    const h = await makeHarness()
    expect(h.ctx.licensePolicy.normalize('BSD-3-Clause')).toBe('bsd-3-clause')
    expect(h.ctx.licensePolicy.normalize('BSD 3-Clause')).toBe('bsd-3-clause')
    expect(h.ctx.licensePolicy.normalize('BSD_3-Clause')).toBe('bsd-3-clause')
  })

  it('classifies bare BSD strings (without -3) as unknown', async () => {
    const h = await makeHarness()
    expect(h.ctx.licensePolicy.normalize('BSD-2-Clause')).toBe('unknown')
    expect(h.ctx.licensePolicy.normalize('BSD-4-Clause')).toBe('unknown')
    expect(h.ctx.licensePolicy.normalize('0BSD')).toBe('unknown')
  })

  it('classifies AGPL-3.0 and rejects other GPL variants as unknown', async () => {
    const h = await makeHarness()
    expect(h.ctx.licensePolicy.normalize('AGPL-3.0')).toBe('agpl-3.0')
    expect(h.ctx.licensePolicy.normalize('agpl-3.0-only')).toBe('agpl-3.0')
    expect(h.ctx.licensePolicy.normalize('GPL-2.0')).toBe('unknown')
  })

  it('classifies NOASSERTION distinctly from unknown', async () => {
    const h = await makeHarness()
    expect(h.ctx.licensePolicy.normalize('NOASSERTION')).toBe('noassertion')
    expect(h.ctx.licensePolicy.normalize('NO-ASSERTION')).toBe('noassertion')
    expect(h.ctx.licensePolicy.normalize('noassertion')).toBe('noassertion')
  })

  it('treats null / undefined / empty strings as unknown', async () => {
    const h = await makeHarness()
    expect(h.ctx.licensePolicy.normalize(null)).toBe('unknown')
    expect(h.ctx.licensePolicy.normalize(undefined)).toBe('unknown')
    expect(h.ctx.licensePolicy.normalize('')).toBe('unknown')
    expect(h.ctx.licensePolicy.normalize('   ')).toBe('unknown')
    expect(h.ctx.licensePolicy.normalize('UNKNOWN')).toBe('unknown')
  })

  it('maps severity buckets per tier', async () => {
    const h = await makeHarness()
    expect(h.ctx.licensePolicy.evaluate('MIT').severity).toBe('green')
    expect(h.ctx.licensePolicy.evaluate('Apache-2.0').severity).toBe('green')
    expect(h.ctx.licensePolicy.evaluate('BSD-3-Clause').severity).toBe('green')
    expect(h.ctx.licensePolicy.evaluate('AGPL-3.0').severity).toBe('red')
    expect(h.ctx.licensePolicy.evaluate('NOASSERTION').severity).toBe('black')
    expect(h.ctx.licensePolicy.evaluate(null).severity).toBe('amber')
  })

  it('maps decisions per tier (default config)', async () => {
    const h = await makeHarness()
    expect(h.ctx.licensePolicy.evaluate('MIT').decision).toBe('allow')
    expect(h.ctx.licensePolicy.evaluate('Apache-2.0').decision).toBe('attribute')
    expect(h.ctx.licensePolicy.evaluate('BSD-3-Clause').decision).toBe('attribute')
    expect(h.ctx.licensePolicy.evaluate('AGPL-3.0').decision).toBe('artifact-only')
    expect(h.ctx.licensePolicy.evaluate('NOASSERTION').decision).toBe('reject')
    expect(h.ctx.licensePolicy.evaluate(null).decision).toBe('attribute')
  })

  it('upgrades unknown to reject when rejectUnknown is enabled', async () => {
    const h = await makeHarness({ rejectUnknown: true })
    expect(h.ctx.licensePolicy.rejectsUnknown).toBe(true)
    expect(h.ctx.licensePolicy.evaluate(null).decision).toBe('reject')
    expect(h.ctx.licensePolicy.evaluate('GPL-2.0').decision).toBe('reject')
  })

  it('attaches the AGPL red-line notice for AGPL decisions', async () => {
    const h = await makeHarness()
    const evaluation = h.ctx.licensePolicy.evaluate('AGPL-3.0')
    expect(evaluation.decision).toBe('artifact-only')
    expect(evaluation.reason).toContain('AGPL-3.0 red-line')
    expect(h.ctx.licensePolicy.agplNotice).toContain('AGPL-3.0')
  })

  it('attaches attribution text for apache-2.0 / bsd-3-clause / unknown tiers', async () => {
    const h = await makeHarness()
    expect(h.ctx.licensePolicy.evaluate('Apache-2.0').attribution).toContain('NOTICE')
    expect(h.ctx.licensePolicy.evaluate('BSD-3-Clause').attribution).toContain('endorsement')
    expect(h.ctx.licensePolicy.evaluate(null).attribution).toContain('Unknown license')
  })

  it('attaches rejection reason for NOASSERTION', async () => {
    const h = await makeHarness()
    const evaluation = h.ctx.licensePolicy.evaluate('NOASSERTION')
    expect(evaluation.decision).toBe('reject')
    expect(evaluation.reason).toContain('NOASSERTION')
    expect(evaluation.reason).toContain('DSH ecosystem governance')
  })

  it('honors a custom AGPL attribution string', async () => {
    const custom = 'CUSTOM-AGPL-NOTICE'
    const h = await makeHarness({ agplAttribution: custom })
    expect(h.ctx.licensePolicy.agplNotice).toBe(custom)
    // The custom text replaces the default in evaluate() output via the
    // tier-keyed branch. Indirect: evaluated result for AGPL-3.0 still
    // emits the standard attribution message; the custom field is exposed
    // for downstream composition rather than overriding the per-tier text.
    expect(h.ctx.licensePolicy.evaluate('AGPL-3.0').decision).toBe('artifact-only')
  })

  it('assertAllowed() passes when decision is in the allowed set', async () => {
    const h = await makeHarness()
    const evaluation = h.ctx.licensePolicy.assertAllowed('MIT', ['allow', 'attribute'])
    expect(evaluation.decision).toBe('allow')
  })

  it('assertAllowed() throws when decision is outside the allowed set', async () => {
    const h = await makeHarness()
    expect(() => h.ctx.licensePolicy.assertAllowed('AGPL-3.0', ['allow'])).toThrow(/artifact-only/)
    expect(() => h.ctx.licensePolicy.assertAllowed('NOASSERTION', ['allow', 'attribute'])).toThrow(/noassertion/)
  })

  it('disposes the registry cleanly (HMR safety)', async () => {
    const ctx = new Context()
    const fiber = await ctx.plugin(LicensePolicy)
    expect(ctx.licensePolicy.evaluate('MIT').decision).toBe('allow')
    await fiber.dispose()
    expect((ctx as unknown as { licensePolicy?: unknown }).licensePolicy).toBeUndefined()
  })

  it('round-trips every tier through normalize + evaluate (no exceptions)', async () => {
    const h = await makeHarness()
    const tiers = ['MIT', 'Apache-2.0', 'BSD-3-Clause', 'AGPL-3.0', 'NOASSERTION', null, undefined, '']
    for (const t of tiers) {
      expect(() => h.ctx.licensePolicy.evaluate(t)).not.toThrow()
    }
  })
})
