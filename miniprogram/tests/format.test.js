const test = require('node:test')
const assert = require('node:assert')
const { centsToYuan, formatTime } = require('../utils/format')

test('centsToYuan 分转元保留两位', () => {
  assert.strictEqual(centsToYuan(1200), '12.00')
  assert.strictEqual(centsToYuan(5), '0.05')
  assert.strictEqual(centsToYuan(0), '0.00')
})

test('formatTime 格式化 ISO 时间（不依赖时区）', () => {
  assert.strictEqual(formatTime('2026-08-05T14:30:00'), '2026-08-05 14:30')
  assert.strictEqual(formatTime(''), '')
})
