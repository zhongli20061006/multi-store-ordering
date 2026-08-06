import { describe, expect, it } from 'vitest'
import { auditActionText } from '../order-audit'

describe('auditActionText', () => {
  it('已知动作转中文', () => {
    expect(auditActionText('accepted')).toBe('接单')
    expect(auditActionText('customer_pickup')).toBe('顾客取单')
  })

  it('未知动作原样返回', () => {
    expect(auditActionText('whatever')).toBe('whatever')
  })
})
