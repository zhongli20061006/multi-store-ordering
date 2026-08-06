const { checkActiveOrders } = require('./utils/order-watcher')

App({
  onLaunch() {
    // 全局订单状态监控：每 8 秒检查进行中订单，状态变化即弹提示（原型期替代推送）
    setInterval(() => checkActiveOrders(), 8000)
  },
})
