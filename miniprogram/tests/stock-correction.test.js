const test = require('node:test')
const assert = require('node:assert')

const { applyStockCorrection } = require('../utils/stock-correction')

test('无不足明细原样返回', () => {
  const items = [{ menu_item_id: 1, quantity: 2 }]
  assert.deepStrictEqual(applyStockCorrection(items, []), items)
})

test('超量商品钳制到可售量并同步 stock', () => {
  const items = [
    { menu_item_id: 1, name: '限量', quantity: 5, stock: 5 },
    { menu_item_id: 2, name: '奶茶', quantity: 1, stock: null },
  ]
  const corrected = applyStockCorrection(items, [
    { menu_item_id: 1, name: '限量', available_stock: 2 },
  ])
  assert.deepStrictEqual(corrected, [
    { menu_item_id: 1, name: '限量', quantity: 2, stock: 2 },
    { menu_item_id: 2, name: '奶茶', quantity: 1, stock: null },
  ])
})

test('未涉及商品不受影响', () => {
  const items = [{ menu_item_id: 1, quantity: 3, stock: 3 }]
  const corrected = applyStockCorrection(items, [{ menu_item_id: 9, available_stock: 1 }])
  assert.deepStrictEqual(corrected, items)
})
