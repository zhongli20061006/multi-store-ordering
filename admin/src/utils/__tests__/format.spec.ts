import { describe, expect, it } from 'vitest'
import { centsToYuan, formatSpecs } from '../format'

describe('centsToYuan', () => {
  it('converts cents to yuan with two decimals', () => {
    expect(centsToYuan(1200)).toBe('12.00')
    expect(centsToYuan(5)).toBe('0.05')
  })
})

describe('formatSpecs', () => {
  it('拼接规格选项', () => {
    expect(formatSpecs({ 糖度: '少糖', 冰量: '少冰' })).toBe('少糖 · 少冰')
  })

  it('空规格返回空串', () => {
    expect(formatSpecs(null)).toBe('')
    expect(formatSpecs({})).toBe('')
  })
})
