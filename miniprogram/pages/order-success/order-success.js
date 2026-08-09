const { getStore } = require('../../utils/api/stores')
const { themeStyle, themeOf, rememberTheme } = require('../../utils/theme')

Page({
  data: {
    orderNo: '',
    totalCents: 0,
    storeId: 0,
    storeName: '',
    store: null,
    themeStyle: '',
  },

  onLoad(options) {
    const storeId = Number(options.store_id || 0)
    this.setData({
      orderNo: options.order_no || '',
      totalCents: Number(options.total_cents || 0),
      storeId,
      storeName: decodeURIComponent(options.store_name || ''),
      themeStyle: themeStyle(themeOf(storeId)),
    })
    if (storeId) this.loadStore(storeId)
  },

  loadStore(storeId) {
    getStore(storeId)
      .then((store) => {
        rememberTheme(storeId, store.theme)
        this.setData({ store, themeStyle: themeStyle(store.theme) })
      })
      .catch(() => {})
  },

  viewOrder() {
    // pending_order_display 已由 checkout 在提交成功后写入，onShow 直接渲染
    wx.switchTab({ url: '/pages/my-orders/my-orders' })
  },

  goHome() {
    wx.switchTab({ url: '/pages/store-list/store-list' })
  },
})
