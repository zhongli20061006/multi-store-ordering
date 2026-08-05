const test = require('node:test')
const assert = require('node:assert')

const storage = new Map()
global.wx = {
  getStorageSync: (k) => storage.get(k) || '',
  setStorageSync: (k, v) => storage.set(k, v),
  removeStorageSync: (k) => storage.delete(k),
  showToast: () => {},
}

const cart = require('../store/cart')

test.beforeEach(() => storage.clear())

test('ensureStore 首次创建空购物车', () => {
  cart.ensureStore(1, '中山路店')
  const c = cart.getCart()
  assert.strictEqual(c.storeId, 1)
  assert.strictEqual(c.storeName, '中山路店')
  assert.deepStrictEqual(c.items, [])
})

test('切换门店清空购物车', () => {
  cart.addItem(1, '中山路店', { menu_item_id: 1, name: '奶茶', unit_price_cents: 1200, quantity: 1 })
  cart.ensureStore(2, '万达店')
  const c = cart.getCart()
  assert.strictEqual(c.storeId, 2)
  assert.deepStrictEqual(c.items, [])
})

test('同门店更新店名不清空购物车', () => {
  cart.addItem(1, '', { menu_item_id: 1, name: '奶茶', unit_price_cents: 1200, quantity: 1 })
  cart.ensureStore(1, '中山路店')
  const c = cart.getCart()
  assert.strictEqual(c.storeName, '中山路店')
  assert.strictEqual(c.items.length, 1)
})

test('同商品合并数量，合计实时派生', () => {
  cart.addItem(1, '中山路店', { menu_item_id: 1, name: '奶茶', unit_price_cents: 500, quantity: 1 })
  cart.addItem(1, '中山路店', { menu_item_id: 1, name: '奶茶', unit_price_cents: 500, quantity: 2 })
  assert.strictEqual(cart.getTotalCount(), 3)
  assert.strictEqual(cart.getTotalCents(), 1500)
  cart.addItem(1, '中山路店', { menu_item_id: 2, name: '果茶', unit_price_cents: 500, quantity: 2 })
  assert.strictEqual(cart.getTotalCents(), 2500)
})

test('updateQuantity 小于等于 0 移除', () => {
  cart.addItem(1, '中山路店', { menu_item_id: 1, name: '奶茶', unit_price_cents: 500, quantity: 2 })
  cart.updateQuantity(1, 1, 0)
  assert.strictEqual(cart.getTotalCount(), 0)
})

test('clearCart 清空', () => {
  cart.addItem(1, '中山路店', { menu_item_id: 1, name: '奶茶', unit_price_cents: 500, quantity: 1 })
  cart.clearCart()
  assert.strictEqual(cart.getCart(), null)
})
