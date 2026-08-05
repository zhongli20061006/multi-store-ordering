const { queryOrder, cancelOrder } = require('../../utils/api/orders')
const { getStores } = require('../../utils/api/stores')

Page({
  data: {
    order: null,
    phone: '',
    orderNo: '',
    querying: false,
    showFinder: false,
    storeNames: {},
  },

  onLoad() {
    this.loadStoreNames()
  },

  onShow() {
    // 下单成功页/确认下单页暂存的完整订单对象，直接渲染（零输入）
    const pending = wx.getStorageSync('pending_order_display')
    if (pending && pending.order_no) {
      wx.removeStorageSync('pending_order_display')
      this.applyOrder(pending)
      this.silentRefresh(pending)
    }
  },

  loadStoreNames() {
    getStores()
      .then((stores) => {
        const map = {}
        stores.forEach((s) => {
          map[s.id] = s.name
        })
        this.setData({ storeNames: map })
      })
      .catch(() => {})
  },

  storeNameOf(storeId) {
    return this.data.storeNames[storeId] || `门店 #${storeId}`
  },

  applyOrder(order) {
    this.setData({
      order: Object.assign({}, order, { storeName: this.storeNameOf(order.store_id) }),
    })
  },

  silentRefresh(order) {
    // 静默刷新最新状态；失败保持快照，不打扰用户
    queryOrder(order.customer_phone, order.order_no)
      .then((fresh) => this.applyOrder(fresh))
      .catch(() => {})
  },

  toggleFinder() {
    this.setData({ showFinder: !this.data.showFinder })
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [field]: e.detail.value })
  },

  onSearch() {
    const { phone, orderNo, querying } = this.data
    if (querying) return
    if (!/^1[3-9]\d{9}$/.test(phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }
    if (!orderNo.trim()) {
      wx.showToast({ title: '请输入订单号', icon: 'none' })
      return
    }
    this.setData({ querying: true })
    queryOrder(phone, orderNo.trim())
      .then((order) => this.applyOrder(order))
      .catch(() => {})
      .finally(() => this.setData({ querying: false }))
  },

  onCancel() {
    const { order } = this.data
    wx.showModal({
      title: '取消订单',
      content: '确定取消该订单？未制作的取消将回补限库存商品。',
      success: (res) => {
        if (!res.confirm) return
        cancelOrder(order.order_no, order.customer_phone)
          .then((fresh) => {
            wx.showToast({ title: '已取消', icon: 'success' })
            this.applyOrder(fresh)
          })
          .catch(() => {})
      },
    })
  },
})
