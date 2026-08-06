const test = require('node:test')
const assert = require('node:assert')
const { filterOrders } = require('../utils/order-filter')

const orders = [
  { order_no: '1001', order_status: 'pending' },
  { order_no: '1002', order_status: 'accepted' },
  { order_no: '1003', order_status: 'served' },
  { order_no: '1004', order_status: 'completed' },
  { order_no: '1005', order_status: 'cancelled' },
]

test('全部返回原数组', () => {
  assert.strictEqual(filterOrders(orders, 'all').length, 5)
})

test('待接单', () => {
  assert.deepStrictEqual(filterOrders(orders, 'pending').map((o) => o.order_no), ['1001'])
})

test('进行中包含已接单与已出单', () => {
  assert.deepStrictEqual(filterOrders(orders, 'active').map((o) => o.order_no), ['1002', '1003'])
})

test('已完成与已取消', () => {
  assert.deepStrictEqual(filterOrders(orders, 'completed').map((o) => o.order_no), ['1004'])
  assert.deepStrictEqual(filterOrders(orders, 'cancelled').map((o) => o.order_no), ['1005'])
})
