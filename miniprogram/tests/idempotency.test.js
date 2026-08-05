const test = require('node:test')
const assert = require('node:assert')
const { generateKey } = require('../utils/idempotency')

test('幂等键：时间戳-随机，长度≥8，每次不同', () => {
  const a = generateKey()
  const b = generateKey()
  assert.match(a, /^\d+-[a-z0-9]+$/)
  assert.ok(a.length >= 8)
  assert.notStrictEqual(a, b)
})
