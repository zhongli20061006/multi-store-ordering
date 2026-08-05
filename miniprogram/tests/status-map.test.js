const test = require('node:test')
const assert = require('node:assert')
const { statusText, entryTypeText, paymentStatusText } = require('../utils/status-map')

test('订单状态文案与兜底', () => {
  assert.strictEqual(statusText('pending'), '待接单')
  assert.strictEqual(statusText('accepted'), '已接单')
  assert.strictEqual(statusText('served'), '已出单')
  assert.strictEqual(statusText('completed'), '已完成')
  assert.strictEqual(statusText('cancelled'), '已取消')
  assert.strictEqual(statusText('unknown'), 'unknown')
})

test('入口类型文案', () => {
  assert.strictEqual(entryTypeText('dinein'), '到店点单')
  assert.strictEqual(entryTypeText('preorder'), '提前点单')
})

test('付款状态文案', () => {
  assert.strictEqual(paymentStatusText('unpaid'), '未付款')
  assert.strictEqual(paymentStatusText('paid'), '已付款')
})
