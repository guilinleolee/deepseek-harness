// Dragon Engine brand wordmark. The legacy artwork combined the whale mark
// with "deepseek-official" letterforms and an HARNESS badge plate (figma
// 356:14644); the replacement renders only the Chinese wordmark "卡巴格AI"
// because the leading mark now lives in the dedicated image served at
// `/dragon-icon.png` and the badge plate no longer applies.

import type { IconProps } from './icons/props.ts'

/** Display options for the official brand wordmark. */
export interface BrandWordmarkProps extends IconProps {
  /** Whether to include the leading whale mark; defaults to true. The Dragon
   *  Engine build passes `includeMark={false}` from `OfficialBrandName` since
   *  the mark now rides its own image. */
  includeMark?: boolean | undefined
}

/**
 * Render the brand wordmark as a text element sized to `size`.
 * @param props.size - font height in px (default 24).
 * @param props.className - extra class for layout placement.
 * @param props.includeMark - retained for the official brand hook; unused here.
 * @returns the wordmark span (aria-hidden decorative brand art).
 */
export function BrandWordmark({ size = 24, className, includeMark: _includeMark = true }: BrandWordmarkProps) {
  return (
    <span
      className={className}
      style={{ fontSize: `${size}px`, fontWeight: 600, lineHeight: 1 }}
      aria-hidden="true"
    >
      卡巴格AI
    </span>
  )
}
