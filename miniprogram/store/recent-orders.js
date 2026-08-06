// 最近订单：单 key 'recent_orders:v1'，最多 5 条，新单在前；按 order_no 去重置顶。
// 原型期隐私妥协（用户 2026-08-05 确认）：记录含 customer_phone，仅本地用于静默刷新；不联网上传；上线前评估。
const RECENT_KEY = 'recent_orders:v1'
const MAX = 50

function read() {
  const list = wx.getStorageSync(RECENT_KEY)
  return Array.isArray(list) ? list : []
}

function write(list) {
  wx.setStorageSync(RECENT_KEY, list)
}

function upsert(order) {
  const list = read().filter((o) => o.order_no !== order.order_no)
  list.unshift(order)
  write(list.slice(0, MAX))
}

function remove(orderNo) {
  write(read().filter((o) => o.order_no !== orderNo))
}

function clear() {
  wx.removeStorageSync(RECENT_KEY)
}

function list() {
  return read().slice()
}

module.exports = { upsert, remove, clear, list }
