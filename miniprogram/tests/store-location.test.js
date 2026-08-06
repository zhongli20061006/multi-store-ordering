const test = require('node:test')
const assert = require('node:assert')

const { buildLocationPayload } = require('../utils/store-location')

test('正常门店返回 openLocation 参数', () => {
  const payload = buildLocationPayload({
    name: '中山路店',
    address: '中山路 88 号',
    latitude: 30.2741,
    longitude: 120.1551,
  })
  assert.deepStrictEqual(payload, {
    latitude: 30.2741,
    longitude: 120.1551,
    name: '中山路店',
    address: '中山路 88 号',
  })
})

test('字符串坐标转为数字', () => {
  const payload = buildLocationPayload({ name: 'a', address: 'b', latitude: '30.25', longitude: '120.16' })
  assert.deepStrictEqual(payload, { latitude: 30.25, longitude: 120.16, name: 'a', address: 'b' })
})

test('缺坐标返回 null', () => {
  assert.strictEqual(buildLocationPayload({ latitude: null, longitude: null, name: 'a' }), null)
  assert.strictEqual(buildLocationPayload({ latitude: 30.1, longitude: null, name: 'a' }), null)
  assert.strictEqual(buildLocationPayload({ latitude: undefined, longitude: undefined, name: 'a' }), null)
  assert.strictEqual(buildLocationPayload(null), null)
})

test('非法坐标返回 null', () => {
  assert.strictEqual(buildLocationPayload({ latitude: 'abc', longitude: 120, name: 'a' }), null)
  assert.strictEqual(buildLocationPayload({ latitude: NaN, longitude: 120, name: 'a' }), null)
})
