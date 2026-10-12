/**
 * Inline-SVG chart primitives for the quant-research panel: a horizontal
 * bar row for position weights and a sparkline for small numeric series.
 * Zero dependencies — the coordinate mapping is a pure function of the
 * data, so unit tests pin the geometry without rendering.
 * @module @deepseek-ai/dsh-client-ui-quant-research/client/charts
 */

/** One labeled bar for {@link BarRow}. */
export interface BarDatum {
  /** Bar label (the position symbol). */
  readonly label: string
  /** Bar value in `[0, 1]` (the weight within the account). */
  readonly value: number
}

/**
 * Map bar data onto row geometry: each bar's width as a percentage of the
 * track and its clamped label. Pure — the JSX renders from these numbers.
 * @param data - the bars, in display order.
 * @returns per-bar geometry (width percent, label).
 */
export function barGeometry(data: readonly BarDatum[]): { label: string; widthPercent: number }[] {
  return data.map((datum) => ({
    label: datum.label,
    widthPercent: Math.max(0, Math.min(1, datum.value)) * 100,
  }))
}

/**
 * Map a numeric series onto sparkline point coordinates inside a fixed
 * viewBox. The x axis spreads the points evenly; the y axis maps the
 * value range onto the padded height, inverted so larger values sit
 * higher. Pure — unit tests pin the geometry without rendering.
 * @param values - the series (at least one point).
 * @param width - the viewBox width.
 * @param height - the viewBox height.
 * @param pad - the vertical padding inside the viewBox.
 * @returns the polyline points, left to right.
 */
export function sparklinePoints(
  values: readonly number[],
  width: number,
  height: number,
  pad: number,
): { x: number; y: number }[] {
  if (values.length === 0) return []
  const min = Math.min(...values)
  const max = Math.max(...values)
  const span = max - min
  const inner = height - pad * 2
  return values.map((value, index) => ({
    x: values.length === 1 ? width / 2 : (index / (values.length - 1)) * width,
    y: pad + inner - (span === 0 ? inner / 2 : ((value - min) / span) * inner),
  }))
}

/** Props of the horizontal bar row. */
export interface BarRowProps {
  /** The bars, in display order. */
  readonly data: readonly BarDatum[]
  /** Accessible label for the chart region. */
  readonly ariaLabel: string
}

/**
 * Render a horizontal bar chart as inline SVG: one track per datum with a
 * filled width proportional to the value.
 * @param props - the bars and the accessible label.
 * @returns the SVG element tree.
 */
export function BarRow({ data, ariaLabel }: BarRowProps) {
  const rows = barGeometry(data)
  return (
    <div role="img" aria-label={ariaLabel} className="quant-bar-row">
      {rows.map(row => (
        <div key={row.label} className="quant-bar-row-item">
          <span className="quant-bar-row-label">{row.label}</span>
          <span className="quant-bar-row-track">
            <span className="quant-bar-row-fill" style={{ width: `${row.widthPercent}%` }} />
          </span>
          <span className="quant-bar-row-value">{row.widthPercent.toFixed(1)}%</span>
        </div>
      ))}
    </div>
  )
}

/** Props of the sparkline. */
export interface SparklineProps {
  /** The numeric series. */
  readonly values: readonly number[]
  /** Accessible label for the chart region. */
  readonly ariaLabel: string
  /** ViewBox width (default 160). */
  readonly width?: number
  /** ViewBox height (default 48). */
  readonly height?: number
}

/**
 * Render a numeric series as an inline-SVG polyline.
 * @param props - the series, the accessible label, and optional box size.
 * @returns the SVG element tree, or `null` for an empty series.
 */
export function Sparkline({ values, ariaLabel, width = 160, height = 48 }: SparklineProps) {
  const pad = 4
  const points = sparklinePoints(values, width, height, pad)
  if (points.length === 0) return null
  const path = points.map(p => `${p.x.toFixed(2)},${p.y.toFixed(2)}`).join(' ')
  return (
    <svg
      role="img"
      aria-label={ariaLabel}
      className="quant-sparkline"
      viewBox={`0 0 ${String(width)} ${String(height)}`}
      width={width}
      height={height}
    >
      <polyline points={path} fill="none" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  )
}
