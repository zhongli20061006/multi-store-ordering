const test = require('node:test')
const assert = require('node:assert')
const { itemsFromOrder } = require('../utils/reorder')

test('itemsFromOrder 映射订单明细为购物车条目', () => {
  const items = itemsFromOrder({
    items: [
      { menu_item_id: 1, item_name: '招牌奶茶', unit_price_cents: 1200, quantity: 2 },
      { menu_item_id: 2, item_name: '每日限量奶昔', unit_price_cents: 1800, quantity: 1 },
    ],
  })
  assert.deepStrictEqual(items, [
    { menu_item_id: 1, name: '招牌奶茶', unit_price_cents: 1200, quantity: 2 },
    { menu_item_id: 2, name: '每日限量奶昔', unit_price_cents: 1800, quantity: 1 },
  ])
})

test('itemsFromOrder 空明细返回空数组', () => {
  assert.deepStrictEqual(itemsFromOrder({ items: [] }), [])
})
