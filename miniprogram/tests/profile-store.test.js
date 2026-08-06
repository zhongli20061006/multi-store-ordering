const test = require('node:test')
const assert = require('node:assert')

const storage = new Map()
global.wx = {
  getStorageSync: (k) => storage.get(k) || '',
  setStorageSync: (k, v) => storage.set(k, v),
  removeStorageSync: (k) => storage.delete(k),
}

const profile = require('../utils/profile-store')

test.beforeEach(() => storage.clear())

test('默认昵称与空手机号', () => {
  assert.deepStrictEqual(profile.read(), { nickname: '微信用户', phone: '' })
})

test('保存昵称与手机号', () => {
  const saved = profile.save({ nickname: '小明', phone: '13800000001' })
  assert.deepStrictEqual(saved, { nickname: '小明', phone: '13800000001' })
  assert.deepStrictEqual(profile.read(), { nickname: '小明', phone: '13800000001' })
})

test('空昵称回退默认', () => {
  assert.deepStrictEqual(profile.save({ nickname: '   ', phone: '' }), { nickname: '微信用户', phone: '' })
})
