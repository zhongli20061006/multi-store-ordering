const test = require('node:test')
const assert = require('node:assert')

const { resolveContact } = require('../utils/contact-prefill')

const fullProfile = { nickname: '小明', phone: '13800000001' }
const defaultProfile = { nickname: '微信用户', phone: '' }

test('个人资料优先于最近一单', () => {
  const recent = [{ customer_name: '老王', customer_phone: '13900000002' }]
  assert.deepStrictEqual(resolveContact(fullProfile, recent), { name: '小明', phone: '13800000001' })
})

test('资料仅存手机号时姓名取最近一单', () => {
  const profile = { nickname: '微信用户', phone: '13800000001' }
  const recent = [{ customer_name: '老王', customer_phone: '13900000002' }]
  assert.deepStrictEqual(resolveContact(profile, recent), { name: '老王', phone: '13800000001' })
})

test('资料为空时用最近一单兜底', () => {
  const recent = [{ customer_name: '老王', customer_phone: '13900000002' }]
  assert.deepStrictEqual(resolveContact(defaultProfile, recent), { name: '老王', phone: '13900000002' })
})

test('无最近订单返回空联系人', () => {
  assert.deepStrictEqual(resolveContact(defaultProfile, []), { name: '', phone: '' })
  assert.deepStrictEqual(resolveContact(defaultProfile, null), { name: '', phone: '' })
})

test('最近订单缺字段时兜底为空', () => {
  const recent = [{ customer_name: '', customer_phone: '' }]
  assert.deepStrictEqual(resolveContact(defaultProfile, recent), { name: '', phone: '' })
})
