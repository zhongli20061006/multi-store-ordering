Page({
  data: {
    orderNo: '',
    totalCents: 0,
    storeName: '',
  },

  onLoad(options) {
    this.setData({
      orderNo: options.order_no || '',
      totalCents: Number(options.total_cents || 0),
      storeName: decodeURIComponent(options.store_name || ''),
    })
  },

  viewOrder() {
    // pending_order_display 已由 checkout 在提交成功后写入，onShow 直接渲染
    wx.switchTab({ url: '/pages/my-orders/my-orders' })
  },

  goHome() {
    wx.switchTab({ url: '/pages/store-list/store-list' })
  },
})
