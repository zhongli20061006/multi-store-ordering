// 纯展示工具；金额展示分→元，时间格式化不依赖 Date 时区解析。
function centsToYuan(cents) {
  return (cents / 100).toFixed(2)
}

function formatTime(iso) {
  if (!iso) return ''
  const m = /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})/.exec(iso)
  if (!m) return iso
  return `${m[1]}-${m[2]}-${m[3]} ${m[4]}:${m[5]}`
}

module.exports = { centsToYuan, formatTime }
