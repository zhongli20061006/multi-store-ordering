const test = require('node:test')
const assert = require('node:assert')
const { filterMenu } = require('../utils/menu-filter')

const groups = [
  { id: 1, name: '招牌饮品', items: [{ id: 1, name: '招牌奶茶' }, { id: 2, name: '生椰拿铁' }] },
  { id: 2, name: '清爽果茶', items: [{ id: 3, name: '满杯百香果' }] },
]

test('无关键词返回原分组', () => {
  assert.deepStrictEqual(filterMenu(groups, ''), groups)
  assert.deepStrictEqual(filterMenu(groups, '   '), groups)
})

test('按商品名过滤（不区分大小写）', () => {
  const out = filterMenu(groups, '奶')
  assert.strictEqual(out.length, 1)
  assert.deepStrictEqual(out[0].items.map((i) => i.name), ['招牌奶茶'])
})

test('匹配后空分类被剔除', () => {
  const out = filterMenu(groups, '百香果')
  assert.strictEqual(out.length, 1)
  assert.strictEqual(out[0].id, 2)
})

test('无命中返回空数组', () => {
  assert.deepStrictEqual(filterMenu(groups, '不存在的商品'), [])
})
