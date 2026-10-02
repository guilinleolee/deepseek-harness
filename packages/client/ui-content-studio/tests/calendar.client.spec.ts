import { describe, expect, it } from 'vitest'
import { formatDate, groupByDate, monthGrid } from '../src/client/calendar.ts'

describe('monthGrid', () => {
  it('covers a month with whole Monday-first weeks including padding', () => {
    // 2026-09: Sep 1 is a Tuesday → 1 leading Monday cell; 30 days → 5 rows.
    const grid = monthGrid(2026, 9)
    expect(grid[0]).toHaveLength(7)
    expect(grid).toHaveLength(5)
    // First cell borrows the last Monday of August.
    expect(grid[0]![0]!.date).toBe('2026-08-31')
    expect(grid[0]![0]!.inMonth).toBe(false)
    // Sep 1 (Tuesday) sits at row 0, index 1.
    expect(grid[0]![1]!.date).toBe('2026-09-01')
    expect(grid[0]![1]!.inMonth).toBe(true)
    // Last row borrows October days.
    expect(grid.at(-1)!.some(day => !day.inMonth)).toBe(true)
    // Dates are unique and wire-shaped.
    const dates = grid.flat().map(day => day.date)
    expect(new Set(dates).size).toBe(dates.length)
    for (const date of dates) expect(date).toMatch(/^\d{4}-\d{2}-\d{2}$/)
  })

  it('marks today among the cells', () => {
    const now = new Date()
    const grid = monthGrid(now.getFullYear(), now.getMonth() + 1)
    expect(grid.flat().some(day => day.isToday)).toBe(true)
  })

  it('rolls across years via formatDate', () => {
    expect(formatDate(2026, 12, 31)).toBe('2026-12-31')
    expect(formatDate(2027, 1, 1)).toBe('2027-01-01')
  })
})

describe('groupByDate', () => {
  it('buckets items by wire date preserving order', () => {
    const items = [
      { date: '2026-09-20', id: 'a' },
      { date: '2026-09-19', id: 'b' },
      { date: '2026-09-20', id: 'c' },
    ]
    const byDate = groupByDate(items)
    expect(byDate.get('2026-09-20')?.map(entry => entry.id)).toEqual(['a', 'c'])
    expect(byDate.get('2026-09-19')?.map(entry => entry.id)).toEqual(['b'])
    expect(byDate.get('2026-09-18')).toBeUndefined()
  })
})
