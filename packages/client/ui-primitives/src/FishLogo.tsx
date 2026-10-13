// Dragon Engine brand mark: served from the web shell's public assets at
// `/dragon-icon.png`. The earlier DeepSeek fish SVG (figma I39:24057) was
// retired for the 卡巴格AI build; the replacement is an <img> so the file
// supplied at build time wins regardless of theme. Size keeps the historical
// 23.16:17.04 ratio so callers that previously scaled the fish see the same
// outer dimensions.

import type { IconProps } from './icons/props.ts'

/** Public-path source for the Dragon Engine brand mark. */
const DRAGON_BRAND_SRC = '/dragon-icon.png'

/** Native mark ratio (matches the legacy fish artwork's 23.16:17.04). */
const NATIVE_RATIO = 17.04 / 23.16

/**
 * Render the brand mark as an image sized to `size`.
 * @param props.size - width in px (default 24; height keeps the legacy ratio).
 * @param props.className - extra class for layout placement.
 * @returns the mark image (aria-hidden; pair with the wordmark for accessibility).
 */
export function FishLogo({ size = 24, className }: IconProps) {
  return (
    <img
      src={DRAGON_BRAND_SRC}
      width={size}
      height={size * NATIVE_RATIO}
      className={className}
      alt=""
      aria-hidden="true"
    />
  )
}
