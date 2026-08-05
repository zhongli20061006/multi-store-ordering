import { describe, expect, it } from 'vitest'
import { centsToYuan } from '../format'

describe('centsToYuan', () => {
  it('converts cents to yuan with two decimals', () => {
    expect(centsToYuan(1200)).toBe('12.00')
    expect(centsToYuan(5)).toBe('0.05')
  })
})
