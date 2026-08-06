// 本地通知：由我的订单轮询检测状态变化写入；微信订阅消息推送属二期（B 线）。
const NOTIFY_KEY = 'notify:v1'
const MAX = 20

function statusText(status, orderNo) {
  const map = {
    accepted: '订单 ' + orderNo + ' 已接单',
    served: '订单 ' + orderNo + ' 已出单，请取餐',
    completed: '订单 ' + orderNo + ' 已完成',
    cancelled: '订单 ' + orderNo + ' 已取消',
  }
  return map[status] || ''
}

function localNow() {
  const d = new Date()
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

function read() {
  const list = wx.getStorageSync(NOTIFY_KEY)
  return Array.isArray(list) ? list : []
}

function write(list) {
  wx.setStorageSync(NOTIFY_KEY, list.slice(0, MAX))
}

function add(text) {
  const list = read()
  list.unshift({ id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`, text, time: localNow(), read: false })
  write(list)
}

function unreadCount() {
  return read().filter((n) => !n.read).length
}

function markAllRead() {
  write(read().map((n) => Object.assign({}, n, { read: true })))
}

function clear() {
  wx.removeStorageSync(NOTIFY_KEY)
}

module.exports = { add, clear, read, unreadCount, markAllRead, textForStatus: statusText }
