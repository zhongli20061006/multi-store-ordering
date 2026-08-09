const test = require('node:test')
const assert = require('node:assert')

const storage = new Map()
global.wx = {
  getStorageSync: (k) => storage.get(k) || '',
  setStorageSync: (k, v) => storage.set(k, v),
  removeStorageSync: (k) => storage.delete(k),
}

const { THEMES, themeStyle, rememberTheme, themeOf } = require('../utils/theme')

test.beforeEach(() => storage.clear())

test('四套主题 token 齐全', () => {
  for (const name of ['warm', 'white', 'green', 'berry']) {
    assert.ok(THEMES[name]['--brand-primary'])
    assert.ok(THEMES[name]['--bg-page'])
    assert.ok(THEMES[name]['--text-main'])
  }
})

test('themeStyle 输出 CSS 变量串', () => {
  const style = themeStyle('white')
  assert.ok(style.includes('--brand-primary:#8B5E3C'))
  assert.ok(style.includes('--bg-page:#FAFAF8'))
})

test('未知主题回退 warm', () => {
  assert.ok(themeStyle('rainbow').includes('--brand-primary:#F0643A'))
  assert.strictEqual(themeOf(1), 'warm')
})

test('rememberTheme/themeOf 按门店缓存', () => {
  rememberTheme(2, 'berry')
  assert.strictEqual(themeOf(2), 'berry')
  assert.strictEqual(themeOf(1), 'warm')
  rememberTheme(3, 'rainbow')
  assert.strictEqual(themeOf(3), 'warm')
})
