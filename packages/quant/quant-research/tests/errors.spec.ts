import { describe, expect, it } from 'vitest'
import { QuantError, errorEnvelope, isQuantError, okEnvelope } from '../src/errors.ts'

describe('QuantError', () => {
  it('carries the tier and the cause', () => {
    const cause = new Error('detail')
    const error = new QuantError('DATA', '数据缺失', { cause })
    expect(error.code).toBe('DATA')
    expect(error.message).toBe('数据缺失')
    expect(error.cause).toBe(cause)
    expect(error.name).toBe('QuantError')
  })

  it('isQuantError narrows only plugin errors', () => {
    expect(isQuantError(new QuantError('RISK', 'x'))).toBe(true)
    expect(isQuantError(new Error('plain'))).toBe(false)
    expect(isQuantError('string')).toBe(false)
  })
})

describe('envelopes', () => {
  it('wraps success with code 0', () => {
    expect(okEnvelope({ value: 1 })).toEqual({ code: 0, msg: 'ok', data: { value: 1 } })
  })

  it('projects QuantError onto its tier', () => {
    expect(errorEnvelope(new QuantError('NETWORK', '数据源超时'))).toEqual({
      code: 1001,
      msg: '数据源超时',
      data: null,
    })
  })

  it('collapses unknown errors to INTERNAL without leaking detail', () => {
    const envelope = errorEnvelope(new Error('secret stack detail'))
    expect(envelope).toEqual({
      code: 1999,
      msg: '量化研究插件内部错误，请稍后重试或查看会话诊断记录',
      data: null,
    })
    expect(JSON.stringify(envelope)).not.toContain('secret stack detail')
  })
})
