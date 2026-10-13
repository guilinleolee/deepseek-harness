/**
 * Browser-session (storage state) persistence for the social-capture faces:
 * one Playwright storage-state JSON per platform under the configured
 * directory, written 0600 like every other credential-adjacent dsh file.
 * The user's login never leaves this machine — that is the compliance
 * property the whole capture design rests on.
 */

import { mkdir, readFile, rm } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import { writeFileAtomic } from '@deepseek-ai/dsh-atomic-write'
import type { SocialPlatform } from '../persona/types.ts'

/** Validate one stored storage-state body: parseable JSON with at least one cookie. */
function isUsableState(raw: string): boolean {
  try {
    const parsed = JSON.parse(raw) as { cookies?: unknown }
    return Array.isArray(parsed.cookies) && parsed.cookies.length > 0
  } catch {
    return false
  }
}

/** The per-platform storage-state file path. */
export function sessionPath(dir: string, platform: SocialPlatform): string {
  return join(dir, `${platform}.json`)
}

/** Persist one Playwright storage state; the directory is created 0700 on demand. */
export async function saveSession(dir: string, platform: SocialPlatform, storageState: string): Promise<void> {
  const file = sessionPath(dir, platform)
  await mkdir(dirname(file), { recursive: true, mode: 0o700 })
  await writeFileAtomic(file, storageState, { mode: 0o600, dirMode: 0o700 })
}

/** Read the stored storage state, or null when absent/unusable. */
export async function readSession(dir: string, platform: SocialPlatform): Promise<string | null> {
  let raw: string
  try {
    raw = await readFile(sessionPath(dir, platform), 'utf8')
  } catch {
    return null
  }
  return isUsableState(raw) ? raw : null
}

/** Whether a usable storage state exists. */
export async function hasSession(dir: string, platform: SocialPlatform): Promise<boolean> {
  return (await readSession(dir, platform)) !== null
}

/** Drop the stored session (the user asks to log out). Absent file is a no-op. */
export async function forgetSession(dir: string, platform: SocialPlatform): Promise<void> {
  await rm(sessionPath(dir, platform), { force: true })
}
