/**
 * Per-platform metadata for the social-capture faces: where the headed
 * login browser goes, which cookie proves a logged-in session, and which
 * profile URLs belong to the platform. Detection keys on cookies (stable
 * across DOM redesigns) rather than page structure.
 */

import type { SocialPlatform } from '../persona/types.ts'

/** One supported platform's login and URL facts. */
export interface SocialPlatformMeta {
  readonly platform: SocialPlatform
  readonly label: string
  /** The page the headed login browser opens. */
  readonly loginUrl: string
  /** The URL whose cookie jar is polled for the session cookie. */
  readonly loginSuccessUrl: string
  /** Presence of this (non-empty) cookie means the user is logged in. */
  readonly sessionCookie: string
  /** A user-pasted profile URL must match this to be captured. */
  readonly profileUrlPattern: RegExp
}

export const SOCIAL_PLATFORM_META: Readonly<Record<SocialPlatform, SocialPlatformMeta>> = {
  xhs: {
    platform: 'xhs',
    label: '小红书',
    loginUrl: 'https://www.xiaohongshu.com',
    loginSuccessUrl: 'https://www.xiaohongshu.com',
    sessionCookie: 'web_session',
    profileUrlPattern: /^https:\/\/www\.xiaohongshu\.com\/user\/profile\//u,
  },
  douyin: {
    platform: 'douyin',
    label: '抖音',
    loginUrl: 'https://www.douyin.com',
    loginSuccessUrl: 'https://www.douyin.com',
    sessionCookie: 'sessionid',
    profileUrlPattern: /^https:\/\/(www\.)?douyin\.com\/user\//u,
  },
  weibo: {
    platform: 'weibo',
    label: '微博',
    loginUrl: 'https://weibo.com/login.php',
    loginSuccessUrl: 'https://weibo.com',
    sessionCookie: 'SUB',
    profileUrlPattern: /^https:\/\/(m\.)?weibo\.(com|cn)\/u\//u,
  },
  bili: {
    platform: 'bili',
    label: 'B 站',
    loginUrl: 'https://passport.bilibili.com/login',
    loginSuccessUrl: 'https://www.bilibili.com',
    sessionCookie: 'SESSDATA',
    profileUrlPattern: /^https:\/\/space\.bilibili\.com\/\d+/u,
  },
}
