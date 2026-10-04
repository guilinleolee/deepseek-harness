import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { customerAcquisitionDomainSpec } from '../src/domain/spec.ts'

const PACKAGE_ROOT = join(import.meta.dirname, '..')

/** Dependencies that would smuggle an automated-outreach or send channel (red lines 2-3). */
const FORBIDDEN_DEPENDENCY = /smtp|nodemailer|sendgrid|mailgun|twilio|wechaty|puppeteer|playwright|selenium|whatsapp|telegram|dingtalk/iu

/** Implementation identifiers of a send channel; prose words must not match (red line 3). */
const FORBIDDEN_SEND_IDENTIFIERS = [
  'nodemailer', 'sendgrid', 'SMTPClient', 'SMTPTransport',
  'sendEmail', 'sendMail', 'sendSms', 'sendSmsCode', 'SmsGateway', 'MailTransport',
]
const FORBIDDEN_SEND_IDENTIFIER = new RegExp(`\\b(${FORBIDDEN_SEND_IDENTIFIERS.join('|')})\\b`, 'u')

function collectSources(dir: string): string[] {
  const files: string[] = []
  for (const name of readdirSync(dir)) {
    const path = join(dir, name)
    if (statSync(path).isDirectory()) files.push(...collectSources(path))
    else if (name.endsWith('.ts') || name.endsWith('.tsx')) files.push(path)
  }
  return files
}

describe('feed-in red lines as executable checks', () => {
  it('red line 2 — no automated-outreach dependency enters either dependency list', () => {
    const manifest = JSON.parse(readFileSync(join(PACKAGE_ROOT, 'package.json'), 'utf8')) as {
      dependencies?: Record<string, string>
      peerDependencies?: Record<string, string>
    }
    const names = Object.keys({ ...manifest.dependencies, ...manifest.peerDependencies })
    expect(names.filter(name => FORBIDDEN_DEPENDENCY.test(name))).toEqual([])
  })

  it('red line 3 — no send-channel implementation identifier appears in src/', () => {
    const offenders = collectSources(join(PACKAGE_ROOT, 'src'))
      .map(path => ({ path, text: readFileSync(path, 'utf8') }))
      .filter(({ text }) => FORBIDDEN_SEND_IDENTIFIER.test(text))
    expect(offenders).toEqual([])
  })

  it('red line 4 — the four editable template tables exist in the frozen domain', () => {
    expect(Object.keys(customerAcquisitionDomainSpec.tables)).toEqual(expect.arrayContaining([
      'icp_profiles', 'score_templates', 'content_templates', 'sop_templates',
    ]))
    expect(customerAcquisitionDomainSpec.version).toBe(1)
  })

  it('red line 5 — settings live in the domain global slot, not in any external store', () => {
    expect(customerAcquisitionDomainSpec.global).toBeDefined()
    // null is the medium's "never written" sentinel; the settings schema must reject it.
    expect(customerAcquisitionDomainSpec.global.schema.safeParse(null).success).toBe(false)
  })
})
