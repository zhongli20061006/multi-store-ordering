const test = require('node:test')
const assert = require('node:assert')

const storage = new Map()
global.wx = {
  getStorageSync: (k) => storage.get(k) || '',
  setStorageSync: (k, v) => storage.set(k, v),
  removeStorageSync: (k) => storage.delete(k),
}

const notify = require('../utils/notify-store')

test.beforeEach(() => storage.clear())

test('add 新通知置顶且带本地时间', () => {
  notify.add('订单已出单，请取餐')
  const list = notify.read()
  assert.strictEqual(list.length, 1)
  assert.strictEqual(list[0].text, '订单已出单，请取餐')
  assert.match(list[0].time, /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/)
})

test('最多保留 20 条', () => {
  for (let i = 0; i < 25; i++) notify.add('n' + i)
  assert.strictEqual(notify.read().length, 20)
})

test('clear 清空', () => {
  notify.add('x')
  notify.clear()
  assert.deepStrictEqual(notify.read(), [])
})

test('textForStatus 状态文案映射', () => {
  assert.strictEqual(notify.textForStatus('served'), '订单已出单，请取餐')
  assert.strictEqual(notify.textForStatus('accepted'), '订单已接单')
  assert.strictEqual(notify.textForStatus('unknown'), '')
})
