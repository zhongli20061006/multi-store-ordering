// 幂等键：时间戳+随机；页面层生成并持有，失败重试复用同一个键。
function generateKey() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

module.exports = { generateKey }
