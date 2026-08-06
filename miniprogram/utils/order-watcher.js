// 全局订单监控：app 级每 8 秒检查进行中订单，状态变化即弹提示并写入本地通知。
const recentOrders = require('../store/recent-orders')
const notifyStore = require('./notify-store')
const { queryOrder } = require('./api/orders')

function isActiveStatus(status) {
  return status === 'pending' || status === 'accepted' || status === 'served'
}

function nextNotificationText(beforeStatus, afterStatus, orderNo) {
  if (beforeStatus === afterStatus) return ''
  return notifyStore.textForStatus(afterStatus, orderNo)
}

function checkActiveOrders() {
  recentOrders.list().forEach((order) => {
    if (!isActiveStatus(order.order_status)) return
    queryOrder(order.customer_phone, order.order_no)
      .then((fresh) => {
        const text = nextNotificationText(order.order_status, fresh.order_status, fresh.order_no)
        if (text) {
          notifyStore.add(text)
          wx.showToast({ title: text, icon: 'none' })
        }
        recentOrders.upsert(fresh)
      })
      .catch(() => {})
  })
}

module.exports = { checkActiveOrders, isActiveStatus, nextNotificationText }
