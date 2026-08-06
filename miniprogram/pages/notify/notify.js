const notifyStore = require('../../utils/notify-store')

Page({
  data: {
    list: [],
  },

  onShow() {
    notifyStore.markAllRead()
    this.setData({ list: notifyStore.read() })
  },

  onClear() {
    wx.showModal({
      title: '清空通知',
      content: '确定清空全部本地通知？',
      success: (res) => {
        if (!res.confirm) return
        notifyStore.clear()
        this.setData({ list: [] })
      },
    })
  },
})
