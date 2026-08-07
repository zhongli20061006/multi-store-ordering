const test = require('node:test')
const assert = require('node:assert')

const { defaultSelections, buildSpecsPayload, formatSpecs } = require('../utils/specs')

test('defaultSelections 每组默认选第一项', () => {
  const groups = [
    { name: '糖度', options: ['正常', '少糖', '多糖', '无糖'] },
    { name: '冰量', options: ['正常冰', '少冰', '多冰', '去冰'] },
  ]
  assert.deepStrictEqual(defaultSelections(groups), [
    { name: '糖度', option: '正常' },
    { name: '冰量', option: '正常冰' },
  ])
})

test('defaultSelections 空数组返回空', () => {
  assert.deepStrictEqual(defaultSelections([]), [])
  assert.deepStrictEqual(defaultSelections(null), [])
})

test('buildSpecsPayload 构造下单参数', () => {
  const selections = [
    { name: '糖度', option: '少糖' },
    { name: '冰量', option: '少冰' },
  ]
  assert.deepStrictEqual(buildSpecsPayload(selections), [
    { name: '糖度', option: '少糖' },
    { name: '冰量', option: '少冰' },
  ])
})

test('formatSpecs 只展示选项值', () => {
  assert.strictEqual(formatSpecs({ 糖度: '少糖', 冰量: '少冰' }), '少糖 · 少冰')
  assert.strictEqual(formatSpecs(null), '')
  assert.strictEqual(formatSpecs({}), '')
})
