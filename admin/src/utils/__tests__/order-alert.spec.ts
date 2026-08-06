import { describe, expect, it } from 'vitest'
import { detectNewPending } from '../order-alert'

describe('detectNewPending', () => {
  it('首载不提醒（基线已含全部）', () => {
    const orders = [
      { id: 1, order_status: 'pending' },
      { id: 2, order_status: 'accepted' },
    ]
    expect(detectNewPending([1, 2], orders)).toEqual([])
  })

  it('检测新增待接单订单', () => {
    const orders = [
      { id: 1, order_status: 'pending' },
      { id: 2, order_status: 'pending' },
    ]
    expect(detectNewPending([1], orders)).toEqual([2])
  })

  it('非 pending 状态不提醒', () => {
    const orders = [{ id: 3, order_status: 'accepted' }]
    expect(detectNewPending([1], orders)).toEqual([])
  })
})
