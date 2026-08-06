const test = require('node:test')
const assert = require('node:assert')

const { canNavigate, canCall } = require('../utils/store-actions')

test('canNavigate：坐标齐全可导航', () => {
  assert.strictEqual(canNavigate({ latitude: 30.25, longitude: 120.16 }), true)
  assert.strictEqual(canNavigate({ latitude: '30.25', longitude: '120.16' }), true)
})

test('canNavigate：缺失或非法坐标不可导航', () => {
  assert.strictEqual(canNavigate({ latitude: null, longitude: null }), false)
  assert.strictEqual(canNavigate({ latitude: 30.1, longitude: null }), false)
  assert.strictEqual(canNavigate({ latitude: 'abc', longitude: 120 }), false)
  assert.strictEqual(canNavigate(null), false)
})

test('canCall：电话非空可拨号', () => {
  assert.strictEqual(canCall({ phone: '0571-88880001' }), true)
  assert.strictEqual(canCall({ phone: '' }), false)
  assert.strictEqual(canCall({ phone: '   ' }), false)
  assert.strictEqual(canCall(null), false)
})
