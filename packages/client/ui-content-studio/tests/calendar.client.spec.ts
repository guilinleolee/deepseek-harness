import { describe, expect, it } from 'vitest'
import type { ScheduleItem, ScheduleItemId } from '@deepseek-ai/dsh-content-schedule/types'
import {
  CALENDAR_CONFIG_VERSION,
  calendarEventsToCsv,
  detectConflicts,
  filterCalendarItems,
  formatDate,
  groupByDate,
  loadCalendarConfig,
  monthGrid,
  overdueOf,
  saveCalendarConfig,
  type CalendarConfig,
  weekGrid,
} from '../src/client/calendar.ts'

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

describe('weekGrid', () => {
  it('renders exactly the Monday-first week containing the anchor', () => {
    // 2026-09-23 is a Wednesday → the week runs Mon 09-21 … Sun 09-27.
    const week = weekGrid('2026-09-23')
    expect(week).toHaveLength(7)
    expect(week[0]!.date).toBe('2026-09-21')
    expect(week.at(-1)!.date).toBe('2026-09-27')
    expect(week.map(day => day.date)).toContain('2026-09-23')
  })

  it('keeps every cell at full opacity and crosses month edges', () => {
    const week = weekGrid('2026-10-01')
    expect(week.every(day => day.inMonth)).toBe(true)
    expect(week[0]!.date).toBe('2026-09-28')
  })
})

describe('overdueOf', () => {
  it('marks past unpublished items and spares published or future ones', () => {
    expect(overdueOf({ date: '2026-09-20', status: 'scheduled' }, '2026-09-27')).toBe(true)
    expect(overdueOf({ date: '2026-09-20', status: 'published' }, '2026-09-27')).toBe(false)
    expect(overdueOf({ date: '2026-09-27', status: 'draft' }, '2026-09-27')).toBe(false)
  })
})

describe('detectConflicts', () => {
  const item = (
    id: string,
    platform: string | null,
    time: string | null,
    status: ScheduleItem['status'] = 'scheduled',
    date = '2026-09-28',
  ): ScheduleItem => ({
    id: id as ScheduleItemId, title: 't', date, time, platform, status, kind: 'event', topic: null, url: null,
  })

  it('flags same-platform scheduled pairs inside the window only', () => {
    const conflicted = detectConflicts([
      item('a', '小红书', '10:00'),
      item('b', '小红书', '11:00'),
      item('c', '抖音', '10:30'),
      item('d', '小红书', '15:00'),
    ])
    expect(conflicted.has('a')).toBe(true)
    expect(conflicted.has('b')).toBe(true)
    expect(conflicted.has('c')).toBe(false)
    expect(conflicted.has('d')).toBe(true)
  })

  it('ignores published items, platform-less items, and other days', () => {
    const conflicted = detectConflicts([
      item('a', '小红书', '10:00', 'published'),
      item('b', '小红书', '10:30'),
      item('c', null, '10:00'),
      item('d', '小红书', '10:00', 'scheduled', '2026-09-29'),
    ])
    expect(conflicted.has('a')).toBe(false)
    expect(conflicted.has('b')).toBe(false)
    expect(conflicted.has('c')).toBe(false)
    expect(conflicted.has('d')).toBe(false)
  })

  it('marks a crowded same-platform day of three or more as a whole', () => {
    const conflicted = detectConflicts([
      item('a', '小红书', '09:00'),
      item('b', '小红书', '13:00'),
      item('c', '小红书', null),
    ])
    expect(conflicted.has('a')).toBe(true)
    expect(conflicted.has('b')).toBe(true)
    expect(conflicted.has('c')).toBe(true)
  })
})

describe('filterCalendarItems', () => {
  const items: ScheduleItem[] = [
    { id: 'a' as ScheduleItemId, title: '中秋选题', date: '2026-09-20', time: '10:00', platform: '小红书', status: 'scheduled', kind: 'content', topic: 'midautumn', url: null },
    { id: 'b' as ScheduleItemId, title: '随手记', date: '2026-09-25', time: null, platform: null, status: 'idea', kind: 'event', topic: null, url: null },
    { id: 'c' as ScheduleItemId, title: '国庆发布', date: '2026-10-01', time: '09:00', platform: '抖音', status: 'published', kind: 'content', topic: 'national', url: null },
  ]

  it('filters by kind, platform, status, range, query, and overdue', () => {
    expect(filterCalendarItems(items, { ...filterCalendarItemsFixture(), kind: 'content' }, '2026-09-27').map(entry => entry.id)).toEqual(['a', 'c'])
    expect(filterCalendarItems(items, { ...filterCalendarItemsFixture(), platforms: ['抖音'] }, '2026-09-27').map(entry => entry.id)).toEqual(['c'])
    expect(filterCalendarItems(items, { ...filterCalendarItemsFixture(), statuses: ['idea'] }, '2026-09-27').map(entry => entry.id)).toEqual(['b'])
    expect(filterCalendarItems(items, { ...filterCalendarItemsFixture(), start: '2026-09-21' }, '2026-09-27').map(entry => entry.id)).toEqual(['b', 'c'])
    expect(filterCalendarItems(items, { ...filterCalendarItemsFixture(), query: '中秋' }, '2026-09-27').map(entry => entry.id)).toEqual(['a'])
    expect(filterCalendarItems(items, { ...filterCalendarItemsFixture(), overdueOnly: true }, '2026-09-27').map(entry => entry.id)).toEqual(['a', 'b'])
  })

  it('returns everything untouched with default filters', () => {
    expect(filterCalendarItems(items, filterCalendarItemsFixture(), '2026-09-27')).toHaveLength(3)
  })
})

/** Fresh default filters for one filter case. */
function filterCalendarItemsFixture() {
  return loadCalendarConfig(null).filters
}

describe('calendarEventsToCsv', () => {
  it('emits BOM, CRLF, fixed columns, quoting, and notes', () => {
    const items: ScheduleItem[] = [
      { id: 'a' as ScheduleItemId, title: '带,逗号的标题', date: '2026-09-20', time: '10:00', platform: '小红书', status: 'scheduled', kind: 'content', topic: 'midautumn', url: null },
      { id: 'b' as ScheduleItemId, title: '全天', date: '2026-09-21', time: null, platform: null, status: 'idea', kind: 'event', topic: null, url: null },
    ]
    const csv = calendarEventsToCsv(items, { a: { text: '等素材' } })
    expect(csv.charCodeAt(0)).toBe(0xFEFF)
    expect(csv.endsWith('\r\n')).toBe(true)
    const lines = csv.slice(1).split('\r\n')
    expect(lines[0]).toBe('日期,时间,类型,状态,标题,平台,关联选题,备注')
    expect(lines[1]).toBe('2026-09-20,10:00,选题排期,已排期,"带,逗号的标题",小红书,midautumn,等素材')
    expect(lines[2]).toBe('2026-09-21,,独立日程,构思,全天,,,')
  })
})

describe('loadCalendarConfig', () => {
  it('defaults on null, garbage, and unknown versions; round-trips a save', () => {
    expect(loadCalendarConfig(null).view).toBe('month')
    expect(loadCalendarConfig('not json').filters.kind).toBe('all')
    expect(loadCalendarConfig(JSON.stringify({ version: CALENDAR_CONFIG_VERSION + 1, view: 'list' })).view).toBe('month')

    const config: CalendarConfig = { version: CALENDAR_CONFIG_VERSION, view: 'week' as const, filters: { ...filterCalendarItemsFixture(), overdueOnly: true } }
    expect(loadCalendarConfig(saveCalendarConfig(config))).toEqual(config)  })
})
