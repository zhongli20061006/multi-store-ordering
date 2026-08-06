const test = require('node:test')
const assert = require('node:assert')

const storage = new Map()
global.wx = {
  getStorageSync: (k) => storage.get(k) || '',
  setStorageSync: (k, v) => storage.set(k, v),
  removeStorageSync: (k) => storage.delete(k),
  showToast: () => {},
}

const watcher = require('../utils/order-watcher')

test('isActiveStatus 只认进行中状态', () => {
  assert.strictEqual(watcher.isActiveStatus('pending'), true)
  assert.strictEqual(watcher.isActiveStatus('accepted'), true)
  assert.strictEqual(watcher.isActiveStatus('served'), true)
  assert.strictEqual(watcher.isActiveStatus('completed'), false)
  assert.strictEqual(watcher.isActiveStatus('cancelled'), false)
})

test('nextNotificationText 状态未变不通知', () => {
  assert.strictEqual(watcher.nextNotificationText('pending', 'pending', '1234'), '')
})

test('nextNotificationText 出单生成带单号文案', () => {
  assert.strictEqual(watcher.nextNotificationText('accepted', 'served', '1234'), '订单 1234 已出单，请取餐')
})

test('nextNotificationText 未知状态不通知', () => {
  assert.strictEqual(watcher.nextNotificationText('pending', 'unknown', '1234'), '')
})
