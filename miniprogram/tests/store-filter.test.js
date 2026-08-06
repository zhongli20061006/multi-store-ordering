const test = require('node:test')
const assert = require('node:assert')
const { filterStores } = require('../utils/store-filter')

const stores = [
  { id: 1, name: '中山路店' },
  { id: 2, name: '万达店' },
]

test('无关键词返回全部', () => {
  assert.deepStrictEqual(filterStores(stores, ''), stores)
})

test('按店名过滤', () => {
  assert.deepStrictEqual(filterStores(stores, '万达').map((s) => s.id), [2])
})

test('无命中返回空数组', () => {
  assert.deepStrictEqual(filterStores(stores, '不存在的店'), [])
})
