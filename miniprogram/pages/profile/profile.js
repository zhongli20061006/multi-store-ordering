const profileStore = require('../../utils/profile-store')

Page({
  data: {
    nickname: '微信用户',
    phone: '',
    avatarText: '客',
  },

  onShow() {
    const p = profileStore.read()
    const avatarText = p.nickname && p.nickname !== '微信用户' ? p.nickname[0] : '客'
    this.setData({ nickname: p.nickname, phone: p.phone, avatarText })
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [field]: e.detail.value })
  },

  onSave() {
    const { nickname, phone } = this.data
    if (phone && !/^1[3-9]\d{9}$/.test(phone)) {
      wx.showToast({ title: '手机号格式不正确', icon: 'none' })
      return
    }
    const saved = profileStore.save({ nickname, phone })
    this.setData({ nickname: saved.nickname, phone: saved.phone })
    wx.showToast({ title: '已保存', icon: 'success' })
  },

  goOrders() {
    wx.setStorageSync('profile_entry', 'orders')
    wx.switchTab({ url: '/pages/my-orders/my-orders' })
  },

  goManage() {
    wx.setStorageSync('profile_entry', 'manage')
    wx.switchTab({ url: '/pages/my-orders/my-orders' })
  },

  goHistory() {
    wx.navigateTo({ url: '/pages/history/history' })
  },

  goNotify() {
    wx.navigateTo({ url: '/pages/notify/notify' })
  },
})
