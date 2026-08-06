// 本地通知：由我的订单轮询检测状态变化写入；微信订阅消息推送属二期（B 线）。
const NOTIFY_KEY = 'notify:v1'
const MAX = 20

const STATUS_TEXT = {
  accepted: '订单已接单',
  served: '订单已出单，请取餐',
  completed: '订单已完成',
  cancelled: '订单已取消',
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
  list.unshift({ id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`, text, time: localNow() })
  write(list)
}

function clear() {
  wx.removeStorageSync(NOTIFY_KEY)
}

function textForStatus(status) {
  return STATUS_TEXT[status] || ''
}

module.exports = { add, clear, read, textForStatus }
