const test = require('node:test')
const assert = require('node:assert')

function mockWx(handler) {
  global.wx = {
    request: handler,
    showToast: () => {},
    showLoading: () => {},
    hideLoading: () => {},
  }
}

test('请求成功返回 data', async () => {
  mockWx((opts) => opts.success({ statusCode: 200, data: { code: 0, message: 'ok', data: { id: 1 } } }))
  const { request } = require('../utils/request')
  const out = await request({ url: '/stores' })
  assert.deepStrictEqual(out, { id: 1 })
})

test('业务失败 reject 并携带 message', async () => {
  mockWx((opts) => opts.success({ statusCode: 200, data: { code: 404, message: '订单不存在' } }))
  const { request } = require('../utils/request')
  await assert.rejects(() => request({ url: '/orders' }), /订单不存在/)
})

test('网络失败 reject 网络异常', async () => {
  mockWx((opts) => opts.fail({ errMsg: 'request:fail' }))
  const { request } = require('../utils/request')
  await assert.rejects(() => request({ url: '/stores' }), /网络异常/)
})
