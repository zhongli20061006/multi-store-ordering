const test = require('node:test')
const assert = require('node:assert')
const { filterHistory, categoriesOf } = require('../utils/history-filter')

const orders = [
  { order_no: '1111', items: [{ category_name: '招牌饮品' }] },
  { order_no: '2222', items: [{ category_name: '汉堡' }] },
  { order_no: '3333', items: [{ category_name: '招牌饮品' }, { category_name: '汉堡' }] },
]

test('categoriesOf 去重提取类别', () => {
  assert.deepStrictEqual(categoriesOf(orders), ['招牌饮品', '汉堡'])
})

test('按订单号搜索', () => {
  assert.deepStrictEqual(filterHistory(orders, { keyword: '22' }).map((o) => o.order_no), ['2222'])
})

test('按类别筛选', () => {
  assert.deepStrictEqual(filterHistory(orders, { category: '汉堡' }).map((o) => o.order_no), ['2222', '3333'])
})

test('关键词+类别组合', () => {
  assert.deepStrictEqual(filterHistory(orders, { keyword: '3', category: '招牌饮品' }).map((o) => o.order_no), ['3333'])
})
