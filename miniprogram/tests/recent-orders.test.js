const test = require('node:test')
const assert = require('node:assert')

const storage = new Map()
global.wx = {
  getStorageSync: (k) => storage.get(k) || '',
  setStorageSync: (k, v) => storage.set(k, v),
  removeStorageSync: (k) => storage.delete(k),
  showToast: () => {},
}

const recent = require('../store/recent-orders')

test.beforeEach(() => storage.clear())

const order = (no, seq) => ({
  order_no: no,
  store_id: 1,
  customer_phone: '13800000001',
  total_cents: 100 * seq,
  order_status: 'pending',
})

test('upsert 新单置顶', () => {
  recent.upsert(order('1111', 1))
  recent.upsert(order('2222', 2))
  assert.deepStrictEqual(recent.list().map((o) => o.order_no), ['2222', '1111'])
})

test('upsert 同单去重并置顶', () => {
  recent.upsert(order('1111', 1))
  recent.upsert(order('2222', 2))
  recent.upsert(order('1111', 3))
  const list = recent.list()
  assert.strictEqual(list.length, 2)
  assert.strictEqual(list[0].order_no, '1111')
  assert.strictEqual(list[0].total_cents, 300)
})

test('最多保留 5 条', () => {
  for (let i = 1; i <= 6; i++) recent.upsert(order(String(1000 + i), i))
  const list = recent.list()
  assert.strictEqual(list.length, 5)
  assert.strictEqual(list[0].order_no, '1006')
  assert.strictEqual(list[4].order_no, '1002')
})

test('remove 按订单号删除', () => {
  recent.upsert(order('1111', 1))
  recent.upsert(order('2222', 2))
  recent.remove('1111')
  assert.deepStrictEqual(recent.list().map((o) => o.order_no), ['2222'])
})

test('clear 清空', () => {
  recent.upsert(order('1111', 1))
  recent.clear()
  assert.deepStrictEqual(recent.list(), [])
})
